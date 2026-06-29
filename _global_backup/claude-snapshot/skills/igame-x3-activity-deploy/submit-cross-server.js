#!/usr/bin/env node
// X3 跨服活动批量部署 - 单文件无依赖
// 用法: node submit-cross-server.js --env prod|dev --file <payloads.json> [--dry-run] [--offline]
const fs=require('fs'),path=require('path');

// ── env ──
const HOME=process.env.USERPROFILE||process.env.HOME;
const ENV_CFG={
  prod:{host:'https://webgw-cn.tap4fun.com',ui:'https://igame.tap4fun.com',auth:'.igame-auth.json'},
  beta:{host:'https://ms-inner-gateway-qa.tap4fun.com',ui:'https://igame-qa.tap4fun.com',auth:'.igame-credentials.json'},
  dev: {host:'https://ms-inner-gateway-dev.tap4fun.com',ui:'https://igame-dev.tap4fun.com',auth:'.igame-auth-dev.json'},
};

// ── args ──
const args=process.argv.slice(2);
function arg(k,def){const i=args.indexOf(k);return i<0?def:args[i+1];}
const flag=k=>args.includes(k);

const env=arg('--env','prod');
const file=arg('--file');
const dry=flag('--dry-run');
const off=flag('--offline');
const idsArg=arg('--ids');
const help=flag('--help')||flag('-h');
const noAgg=flag('--no-aggregate');   // 默认开聚合, 加这个反向关闭
const force=flag('--force');           // 跳过部署前查重/B状态拦截

if(help||!ENV_CFG[env]||(!file&&!off)){
  console.log(`
X3 跨服活动批量部署/下线

用法:
  node submit-cross-server.js --env <prod|dev> --file <payloads.json>       # 批量上线
  node submit-cross-server.js --env <prod|dev> --file <payloads.json> --dry-run  # 仅预览
  node submit-cross-server.js --env <prod|dev> --offline --ids 13713,13714      # 批量下线

参数:
  --env prod|dev    选环境 (默认 prod)
  --file PATH       payload JSON 文件路径 (上线必填)
  --dry-run         只打印不发送
  --offline         下线模式
  --ids ID,ID,...   下线时的活动 id 列表 (逗号分隔)
  --no-aggregate    关闭自动聚合 (默认开)
                    聚合规则: 同 cfg+startTime+endTime 合并到 1 个活动 ID
                    跨服: servers 多组保留, 单服: 所有服合 1 大组
                    可节省大量活动 ID (实测 17 条 → 8 条)

auth 文件位置:
  ${HOME}\\.igame-auth.json       (prod)
  ${HOME}\\.igame-auth-dev.json   (dev)

payload JSON 格式 (数组, 每个元素 1 组活动):
  [
    {
      "activityConfigId":"102001",
      "previewTime":0,
      "startTime":1782691200000,        ⚠ 必须 UTC 时间戳 (Date.UTC)
      "endTime":1783295999000,
      "endShowTime":0,
      "acrossServerRank":1,
      "acrossServer":1,
      "name":"风暴逐鹿OpenServer_1870,1880,1890",
      "servers":[["1870","1880","1890"]]
    }
  ]
`);
  process.exit(help?0:1);
}

const cfg=ENV_CFG[env];
const authPath=path.join(HOME,cfg.auth);
if(!fs.existsSync(authPath)){console.error(`❌ auth 文件不存在: ${authPath}`);process.exit(1);}
const auth=JSON.parse(fs.readFileSync(authPath,'utf-8'));
const HDRS={'Content-Type':'application/json','Authorization':`Bearer ${auth.token}`,'clientid':auth.clientId,'gameid':auth.gameId,'regionid':auth.regionId,'origin':cfg.ui,'referer':cfg.ui+'/'};
const ENV_TAG=env==='prod'?'🔴 PROD':'🟢 DEV';

(async()=>{
  // ── 下线模式 ──
  if(off){
    if(!idsArg){console.error('❌ --offline 必须配 --ids');process.exit(1);}
    const ids=idsArg.split(',').map(x=>parseInt(x.trim())).filter(Boolean);
    console.log(`${ENV_TAG}  下线模式  ids=${ids.join(',')}`);
    if(dry){console.log('[DRY] 仅预览, 不发送');process.exit(0);}
    const results=[];
    for(const id of ids){
      process.stdout.write(`  ↓ offline ${id} ... `);
      try{
        const r=await fetch(cfg.host+'/ark/activity/batch_offline',{method:'POST',headers:HDRS,body:JSON.stringify({ids:id,reason:'1'})});
        const j=await r.json();
        if(r.status===200&&j.success){console.log('✓');results.push({id,ok:true});}
        else{console.log(`✗ ${j.message||j.code}`);results.push({id,ok:false,err:j.message||j.code});}
      }catch(e){console.log('✗',e.message.split('\n')[0]);results.push({id,ok:false,err:e.message});}
      await new Promise(r=>setTimeout(r,200));
    }
    console.log(`\n汇总: 成功 ${results.filter(r=>r.ok).length}/${ids.length}`);
    process.exit(0);
  }

  // ── 上线模式 ──
  if(!fs.existsSync(file)){console.error(`❌ payload 文件不存在: ${file}`);process.exit(1);}
  let payloads=JSON.parse(fs.readFileSync(file,'utf-8'));
  if(!Array.isArray(payloads)){console.error('❌ JSON 必须是数组');process.exit(1);}
  const original_n=payloads.length;

  // ── 自动聚合: 同 cfg + 同 startTime + 同 endTime 合并到 1 个 payload ──
  if(!noAgg){
    const buckets=new Map();
    for(const p of payloads){
      const key=`${p.activityConfigId}|${p.startTime}|${p.endTime}|${p.acrossServer}|${p.acrossServerRank}`;
      if(!buckets.has(key)){
        // 深拷贝, servers 重置
        buckets.set(key,{...p,servers:[],_serverGroups:0});
      }
      const m=buckets.get(key);
      // 跨服: 保留多组; 单服: 把所有内层服全部拍平到 1 大组
      if(p.acrossServer===1){
        for(const g of (p.servers||[])) m.servers.push(g);
      }else{
        // 单服合 1 大组
        for(const g of (p.servers||[])) for(const s of g) {
          if(!m.servers[0]) m.servers[0]=[];
          if(!m.servers[0].includes(s)) m.servers[0].push(s);
        }
      }
      m._serverGroups++;
    }
    const aggregated=[...buckets.values()].map(m=>{const {_serverGroups,...rest}=m;return rest;});
    if(aggregated.length<original_n){
      console.log(`📦 自动聚合: ${original_n} 条 → ${aggregated.length} 条 (节省 ${original_n-aggregated.length} 个活动 ID)`);
      console.log('   (按 cfg+startTime+endTime 合并; 跨服保留多组, 单服合 1 大组; --no-aggregate 关闭)');
    }
    payloads=aggregated;
  }

  console.log(`${ENV_TAG}  上线模式  host=${cfg.host}  共 ${payloads.length} 条 payload${dry?'  [DRY-RUN]':''}\n`);

  // ── 部署前 double-check(通用): ①重复=同cfg+同server+时间重叠+对方status2/5 ②B状态=同cfg+同server有status8卡单 ──
  {
    let existing=null;
    try{
      const lr=await fetch(cfg.host+'/ark/activity/list?pageIndex=1&pageSize=300',{headers:HDRS});
      const lj=await lr.json(); existing=lj.data||lj||[];
    }catch(e){ console.error('⚠️ 查重拉取 activity/list 失败,跳过检查:',(e.message||'').split('\n')[0]); }
    if(Array.isArray(existing)){
      const ov=(s1,e1,s2,e2)=>s1<e2&&s2<e1;   // 时间窗重叠
      const dup=[], bstate=[];
      for(const p of payloads){
        const c=String(p.activityConfigId);
        const psrv=new Set((p.servers||[]).flat().map(String));
        for(const a of existing){
          if(String(a.activityConfigId)!==c) continue;
          const inter=(a.servers||[]).flat().map(String).filter(s=>psrv.has(s));
          if(!inter.length) continue;                       // server 不重叠 → 跳过
          if((a.status===2||a.status===5)&&ov(p.startTime,p.endTime,a.startTime,a.endTime))
            dup.push({cfg:c,id:a.id,st:a.status,n:inter.length,sv:inter});
          else if(a.status===8||a.status===11||a.status===14)
            bstate.push({cfg:c,id:a.id,st:a.status,n:inter.length});
        }
      }
      if(dup.length){
        console.log('❌ 查重: 同 cfg+server+时间重叠的活跃实例(真重复):');
        for(const d of dup) console.log(`   cfg=${d.cfg} 已有id=${d.id}(status${d.st}) 重叠${d.n}服[${d.sv.slice(0,8).join(',')}${d.sv.length>8?'...':''}]`);
      }
      if(bstate.length){
        console.log('⚠️ B状态: 同 cfg+server 有 status8 卡单(下线申请待审批·API清不了·需UI审批):');
        for(const b of bstate) console.log(`   cfg=${b.cfg} 卡单id=${b.id}(status${b.st}) ${b.n}服`);
      }
      if(dup.length||bstate.length){
        if(!dry&&!force){ console.error('\n❌ 已拦截不发送。先清理上述重复/卡单(status8走iGame UI审批),或加 --force 强制部署。'); process.exit(3); }
        else console.log(`   (${dry?'DRY-RUN仅提示':'--force 强制'}, 继续)`);
      } else console.log('✅ 部署前查重通过: 无 cfg+server+时间重叠重复, 无 status8 卡单。');
    }
  }


  // 预览所有 payload 时间换算
  console.log('=== payload 预览 ===');
  for(let i=0;i<payloads.length;i++){
    const p=payloads[i];
    const stUtc=new Date(p.startTime).toISOString().replace('T',' ').slice(0,19);
    const enUtc=new Date(p.endTime).toISOString().replace('T',' ').slice(0,19);
    const dur=((p.endTime-p.startTime)/3600000).toFixed(1);
    const xs=p.acrossServer===1?'跨服':'单服';
    const ng=p.servers.length, nserver=p.servers.reduce((s,g)=>s+g.length,0);
    const srvDesc=ng>1?`${ng}组共${nserver}服 ${JSON.stringify(p.servers).slice(0,80)}${JSON.stringify(p.servers).length>80?'...':''}`:`${nserver}服 [${p.servers[0].join(',')}]`;
    console.log(`[${(i+1).toString().padStart(2)}/${payloads.length}] cfg=${p.activityConfigId} ${xs} ${stUtc}~${enUtc} UTC (${dur}h) ${srvDesc}`);
  }
  if(dry){console.log('\n[DRY-RUN] 仅预览, 不发送');process.exit(0);}

  console.log('\n=== 开始批量 submit ===');
  const results=[];
  for(let i=0;i<payloads.length;i++){
    const p=payloads[i];
    process.stdout.write(`[${(i+1).toString().padStart(2)}/${payloads.length}] cfg=${p.activityConfigId} 服=[${p.servers[0].join(',')}] ... `);
    try{
      const r=await fetch(cfg.host+'/ark/activity/submit',{method:'POST',headers:HDRS,body:JSON.stringify([p])});
      const j=await r.json();
      if(r.status===200&&j.success){
        const id=(j.data||['?'])[0];
        console.log(`✓ id=${id}`);
        results.push({idx:i+1,name:p.name,id,ok:true});
      }else{
        console.log(`✗ HTTP ${r.status} ${j.message||j.code||''}`);
        results.push({idx:i+1,name:p.name,id:null,ok:false,err:j.message||j.code});
      }
    }catch(e){console.log('✗ ERR',e.message.split('\n')[0]);results.push({idx:i+1,name:p.name,id:null,ok:false,err:e.message});}
    await new Promise(r=>setTimeout(r,200));
  }
  const ok=results.filter(r=>r.ok),fail=results.filter(r=>!r.ok);
  console.log(`\n=== 汇总: 成功 ${ok.length}/${payloads.length}  失败 ${fail.length}/${payloads.length} ===`);
  console.log('\n成功 ids (逗号分隔, 可直接喂 --offline --ids):');
  console.log('  '+ok.map(r=>r.id).join(','));
  if(fail.length){
    console.log('\n失败列表:');
    for(const r of fail)console.log(`  [${r.idx}] ${r.name}  err=${r.err}`);
  }
  // 写结果备查
  const outPath=path.join(path.dirname(file),`${path.basename(file,'.json')}-results-${Date.now()}.json`);
  fs.writeFileSync(outPath,JSON.stringify({env,when:new Date().toISOString(),results},null,2));
  console.log(`\n结果已存: ${outPath}`);
})();
