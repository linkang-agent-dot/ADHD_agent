#!/usr/bin/env node
const path = require('path');
const fs = require('fs');
const { RouteTable } = require('../src/route-table');

const AUTH_FILE = path.join(process.env.HOME || process.env.USERPROFILE, '.igame-auth.json');
const ROUTES_FILE = path.resolve(__dirname, '../igame-routes.json');
const API_HOST = 'https://webgw-cn.tap4fun.com';

function loadAuth() {
  if (!fs.existsSync(AUTH_FILE)) {
    console.error('ERROR: 认证文件不存在。请先运行 setup-auth.sh 配置认证信息。');
    console.error('  文件路径: ' + AUTH_FILE);
    console.error('  或手动创建，格式: {"token":"...","clientId":"...","gameId":"1041","regionId":"201"}');
    process.exit(1);
  }
  return JSON.parse(fs.readFileSync(AUTH_FILE, 'utf-8'));
}

function buildUrl(templatePath, params) {
  let url = templatePath;
  const usedParams = new Set();
  url = url.replace(/\{(\w+)\}/g, (_, key) => {
    for (const [k, v] of Object.entries(params)) {
      if (k === key || k.toLowerCase().includes(key.toLowerCase())) {
        usedParams.add(k);
        return encodeURIComponent(v);
      }
    }
    return `{${key}}`;
  });
  const remaining = {};
  for (const [k, v] of Object.entries(params)) {
    if (!usedParams.has(k)) remaining[k] = v;
  }
  return { url, remaining };
}

async function callApi(apiPath, method, params, auth) {
  // 数组 body（如 activity/submit）：原样作为 body，不经过 buildUrl 的占位符替换，
  // 否则 Object.entries(array) 会把 ["0", {...}] 当键值对处理，产出 {"0":{...}} 这种错误结构。
  const isArrayBody = Array.isArray(params);
  let fullUrl;
  let remaining = {};
  if (isArrayBody) {
    fullUrl = new URL('/ark' + apiPath, API_HOST);
  } else {
    const built = buildUrl(apiPath, params);
    remaining = built.remaining;
    fullUrl = new URL('/ark' + built.url, API_HOST);
  }

  const fetchOptions = {
    method,
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${auth.token}`,
      'clientid': auth.clientId,
      'gameid': auth.gameId || '1041',
      'regionid': auth.regionId || '201',
      'origin': 'https://igame.tap4fun.com',
      'referer': 'https://igame.tap4fun.com/',
    },
  };

  if (method === 'GET') {
    for (const [k, v] of Object.entries(remaining)) {
      fullUrl.searchParams.set(k, String(v));
    }
  } else {
    // 数组 body 原样序列化；对象 body 使用 buildUrl 剥出 URL 占位后的剩余字段
    fetchOptions.body = isArrayBody ? JSON.stringify(params) : JSON.stringify(remaining);
  }

  const resp = await fetch(fullUrl.toString(), fetchOptions);
  return resp.json();
}

async function main() {
  const [,, command, routePath, paramsJson] = process.argv;

  if (!command) {
    console.log('iGame CLI\n');
    console.log('用法:');
    console.log('  igame-query.js ls [path]                    列出模块/接口');
    console.log('  igame-query.js describe <path>              查看接口详情');
    console.log('  igame-query.js read <path> [params_json]    调用 GET 接口');
    console.log('  igame-query.js write <path> [params_json]   调用写接口');
    console.log('\n示例:');
    console.log('  igame-query.js ls ""');
    console.log('  igame-query.js ls "serverMgr"');
    console.log('  igame-query.js describe "serverMgr/serverList/getServerList"');
    console.log('  igame-query.js read "serverMgr/serverList/getServerList" \'{"pageIndex":1,"pageSize":5}\'');
    process.exit(0);
  }

  const rt = new RouteTable(ROUTES_FILE);

  if (command === 'ls') {
    const result = rt.resolve(routePath || '');
    if (result.type === 'not_found') {
      console.log('路径不存在:', routePath);
      process.exit(1);
    }
    if (result.type === 'root') {
      console.log('iGame 模块列表:\n');
      for (const m of result.data) {
        console.log(`  ${m.name.padEnd(28)} ${String(m.totalApis).padStart(4)} 个接口  (${m.subModules} 个子模块)`);
      }
      console.log(`\n共 ${result.data.length} 个模块`);
    } else if (result.type === 'module') {
      console.log(`${result.module} 模块:\n`);
      for (const sub of result.data) {
        console.log(`  ${sub.name} (${sub.apis.length} 个接口)`);
        for (const api of sub.apis) {
          const desc = api.description ? ` — ${api.description}` : '';
          console.log(`      ${api.method.padEnd(7)} ${api.name}${desc}`);
        }
      }
    } else if (result.type === 'submodule') {
      console.log(`${result.module}/${result.sub}:\n`);
      for (const api of result.data) {
        const desc = api.description ? ` — ${api.description}` : '';
        console.log(`  ${api.method.padEnd(7)} ${api.name.padEnd(30)} ${api.path}${desc}`);
      }
    } else if (result.type === 'api') {
      const a = result.data;
      console.log(`${a.name}: ${a.method} ${a.path} (${a.params.join(', ')}) ${a.description || ''}`);
    }
    return;
  }

  if (command === 'describe') {
    if (!routePath) { console.log('请提供接口路径'); process.exit(1); }
    const desc = rt.describeApi(routePath);
    if (!desc) { console.log('接口不存在:', routePath); process.exit(1); }
    console.log(`名称: ${desc.name}`);
    console.log(`模块: ${desc.module}/${desc.sub}`);
    console.log(`方法: ${desc.method}`);
    console.log(`路径: /ark${desc.path}`);
    console.log(`参数: ${desc.params.length > 0 ? desc.params.join(', ') : '无'}`);
    console.log(`描述: ${desc.description || '无'}`);
    return;
  }

  if (command === 'read' || command === 'write') {
    if (!routePath) { console.log('请提供接口路径'); process.exit(1); }
    const api = rt.describeApi(routePath);
    if (!api) { console.log('接口不存在:', routePath); process.exit(1); }

    if (command === 'read' && api.method !== 'GET') {
      console.log(`接口 ${api.name} 是 ${api.method} 方法，请使用 write 命令`);
      process.exit(1);
    }
    if (command === 'write' && api.method === 'GET') {
      console.log(`接口 ${api.name} 是 GET 方法，请使用 read 命令`);
      process.exit(1);
    }

    const auth = loadAuth();
    let params = {};
    if (paramsJson) {
      try {
        params = JSON.parse(paramsJson);
      } catch (e) {
        // PowerShell strips quotes, try to fix: {key:value} -> {"key":value}
        const fixed = paramsJson.replace(/(\{|,)\s*(\w+)\s*:/g, '$1"$2":');
        params = JSON.parse(fixed);
      }
    }
    const result = await callApi(api.path, api.method, params, auth);
    console.log(JSON.stringify(result, null, 2));
    return;
  }

  console.log('未知命令:', command);
  process.exit(1);
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
