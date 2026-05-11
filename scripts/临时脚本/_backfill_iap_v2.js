#!/usr/bin/env node
const { execSync } = require('child_process');
const fs = require('fs');
const os = require('os');
const path = require('path');

const SHEET_ID = '1rPK9k75RvSb897-BS6l-9ZvrU-iAefE-e9H2-uAnCc4';
const TAB = '礼包维表-iap';

const RULES = [
  { kw: ['eqpt_achv'], matchId: true, types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-活动特惠', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['英雄装备-橙色-加工', '英雄装备-红色-加工', '英雄装备-紫色-加工', '英雄装备-紫色-高级', '英雄装备-橙色-高级', '英雄装备-橙色-普通', '英雄装备-紫色-普通', '装备触发'], types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-活动特惠', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['战装突破一条龙', '红20级_战装', '红23级_战装', '红25级_战装', '红27级_战装', '红29级_战装', '橙20级_战装', '战装重铸触发'], types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-活动特惠', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['战装新预热', '装备_尖端套装', '装备_征服者套装', '装备_精密套装'], types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-活动特惠', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['英雄装备破冰'], types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-活动特惠', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['英雄装备材料', '装备材料', '重铸矿晶', '高级重铸矿晶', '幻化刷', '装备周卡'], types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-日周月礼包', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['战装自选'], types: ['英雄装备+洗练-英雄装备', '英雄装备+洗练-英雄装备-活动特惠', '英雄装备等buff类', 'SLG', '英雄装备+洗练'] },
  { kw: ['战装大富翁'], types: ['战车-战车成长', '战车-战车成长-触发特惠', '士兵', 'SLG', '战车'] },
  { kw: ['军备触发', 'T6军备触发', '军备唤醒', '军备触发-'], types: ['军备+兵种技能-军备', '军备+兵种技能-军备-触发特惠', '英雄装备等buff类', 'SLG', '军备+兵种技能'] },
  { kw: ['兵种技能触发', '兵种技能材料锚点'], types: ['军备+兵种技能-军备', '军备+兵种技能-军备-触发特惠', '英雄装备等buff类', 'SLG', '军备+兵种技能'] },
  { kw: ['犀牛技能触发', '毒蝎技能触发', '巨象技能触发', '天鹰技能触发', '雄狮技能触发', '螳螂技能触发', '战龟技能触发'], types: ['军备+兵种技能-军备', '军备+兵种技能-军备-触发特惠', '英雄装备等buff类', 'SLG', '军备+兵种技能'] },
  { kw: ['飙车族-分支', '打击手-分支', '射击手-分支', '攻城车-分支'], types: ['军备+兵种技能-军备', '军备+兵种技能-军备-触发特惠', '英雄装备等buff类', 'SLG', '军备+兵种技能'] },
  { kw: ['超凡军备箱'], types: ['军备+兵种技能-军备', '军备+兵种技能-军备-常驻平价', '英雄装备等buff类', 'SLG', '军备+兵种技能'] },
  { kw: ['军备7日活动'], types: ['军备+兵种技能-军备', '军备+兵种技能-军备-活动特惠', '英雄装备等buff类', 'SLG', '军备+兵种技能'] },
  { kw: ['重装出击付费材料', '驾驶经验', '神经增强剂', '猩战手册', '晶体元件', '猿晶燃料'], types: ['机甲-机甲成长', '机甲-机甲成长-常驻平价', '英雄装备等buff类', 'SLG', '机甲'] },
  { kw: ['橙机师升级', '紫机师升级', '机能核心'], types: ['机甲-机甲成长', '机甲-机甲成长-触发特惠', '英雄装备等buff类', 'SLG', '机甲'] },
  { kw: ['毒尾蝎技能触发', '雷鸟技能触发'], types: ['机甲-机甲成长', '机甲-机甲成长-触发特惠', '英雄装备等buff类', 'SLG', '机甲'] },
  { kw: ['巨象破冰', '雄狮破冰', '螳螂破冰'], types: ['机甲', '机甲-成长线-破冰', '英雄装备等buff类', 'SLG', '机甲'] },
  { kw: ['展台混合锚点', '胶囊锚点', '胶囊周卡', '高分子材料锚点'], types: ['收藏品-收藏品', '收藏品-收藏品-常驻特惠', '英雄装备等buff类', 'SLG', '收藏品'] },
  { kw: ['装饰兑换券', '装饰商店随机', '行军表情'], types: ['收藏品-收藏品', '收藏品-收藏品-常驻特惠', '英雄装备等buff类', 'SLG', '收藏品'] },
  { kw: ['双天赋礼包', '双天赋_'], types: ['英雄-英雄天赋', '英雄-英雄天赋-常驻平价', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['橙色斗士', '紫色斗士', '紫将即将', '首次紫色', '英雄双天赋'], types: ['英雄-英雄成长', '英雄-英雄成长-触发特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['培养礼包', '专属礼包'], types: ['英雄-英雄成长', '英雄-英雄奖牌-触发特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['赛季金头'], types: ['英雄-英雄奖牌', '英雄-英雄奖牌-常驻特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['精英招募'], types: ['英雄-英雄成长', '英雄-英雄成长-触发特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['每日特惠（', '每日特惠_', '每日触发礼包', '每日抽奖'], types: ['英雄-英雄奖牌', '英雄-英雄奖牌-常驻特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['英雄联动'], types: ['英雄-英雄成长', '英雄-英雄成长-活动特惠', '英雄装备等buff类', 'SLG', '混合'] },
  { kw: ['金修女阶梯'], types: ['英雄-英雄奖牌', '英雄-英雄奖牌-常驻特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['英雄道具', '英雄重置'], types: ['英雄-英雄奖牌', '英雄-英雄奖牌-常驻特惠', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['宝石框架活动', '宝石纹章基金'], types: ['英雄-宝石', '英雄-宝石-常驻平价', '英雄装备等buff类', 'SLG', '英雄'] },
  { kw: ['战损礼包', '训练治疗整合版', 'T3训练', 'T4训练', 'T5训练', 'T6训练', '训练部队触发'], types: ['SLG-加速', 'SLG-加速-触发特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['科研过程', '精英研究', '研究所-', '16级研究', '24级研究', '转基因科技'], types: ['SLG-加速', 'SLG-加速-触发特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['占领氏族', '争夺太空城', '争夺补给站'], types: ['SLG-加速', 'SLG-加速-触发特惠', '士兵', 'SLG', 'SLG'] },
  { kw: ['破冰触发礼包'], types: ['SLG-加速', 'SLG-加速-触发特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['t6礼包', '每日任务礼包'], types: ['SLG-加速', 'SLG-加速-常驻平价', '科研城建', 'SLG', 'SLG'] },
  { kw: ['转基因香蕉树'], types: ['SLG-加速', 'SLG-加速-触发特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['英灵殿返还'], types: ['SLG-加速', 'SLG-加速-触发特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['氮气特卖'], types: ['SLG-加速', 'SLG-加速-常驻平价', '科研城建', 'SLG', 'SLG'] },
  { kw: ['cd银行礼包', '猿猴币', '小猪存钱罐'], types: ['SLG-CD', 'SLG-CD-常驻平价', '金币 + 节日', 'SLG', 'SLG'] },
  { kw: ['世界boss', '合服礼包'], types: ['SLG-SLG混合', 'SLG-SLG混合-活动特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['资源周卡', 'cpe进度'], types: ['SLG-SLG混合', 'SLG-SLG混合-常驻平价', '科研城建', 'SLG', 'SLG'] },
  { kw: ['付费飞服'], types: ['SLG-SLG混合', 'SLG-SLG混合-活动特惠', '科研城建', 'SLG', 'SLG'] },
  { kw: ['感恩节', '复活节', '科技节', '拓荒节', '泳池派对', '游泳圈', '沙滩节', '登月节', '圣诞', '万圣', '马戏节'], types: ['混合-节日活动', '混合-节日活动-节日特惠', '金币 + 节日', 'SLG', '节日'] },
  { kw: ['端午节', '幼猴节', '登月转盘', '科技赠礼'], types: ['混合-节日活动', '混合-节日活动-节日特惠', '金币 + 节日', 'SLG', '节日'] },
  { kw: ['千万下载', '三千万下载', '四千万下载', '五千万下载', '六千万下载', '七千万下载'], types: ['混合-节日活动', '混合-节日活动-节日特惠', '金币 + 节日', 'SLG', '节日'] },
  { kw: ['GACHA礼包', 'gacha礼包'], types: ['混合-节日活动', '混合-节日活动-节日特惠', '金币 + 节日', 'SLG', '节日'] },
  { kw: ['狙击子弹'], types: ['混合-节日活动', '混合-节日活动-节日特惠', '金币 + 节日', 'SLG', '节日'] },
  { kw: ['通行证', 'battle_pass', '订阅卡', 'subscription', '酒馆登陆bp', '回归'], types: ['混合-BP&月卡', '混合-BP&月卡-其他BP', '其他', 'SLG', '混合'] },
  { kw: ['新首充连锁'], types: ['混合-BP&月卡', '混合-BP&月卡-其他BP', '其他', 'SLG', '混合'] },
  { kw: ['战装纳米bp'], types: ['混合-BP&月卡', '混合-BP&月卡-其他BP', '其他', 'SLG', '混合'] },
  { kw: ['循环基因', '基因贬值'], types: ['混合-日常活动&礼包', '混合-日常活动&礼包-月度礼包', '科研城建', 'SLG', '混合'] },
  { kw: ['酒馆积分', '酒馆会员'], types: ['混合-日常活动&礼包', '混合-日常活动&礼包-自选礼包', '英雄装备等buff类', 'SLG', '混合'] },
  { kw: ['砍价', '欢乐币'], types: ['混合-日常活动&礼包', '混合-日常活动&礼包-自选礼包', '英雄装备等buff类', 'SLG', '混合'] },
  { kw: ['多档位转盘', '多档位翻牌'], types: ['混合-日常活动&礼包', '混合-日常活动&礼包-自选礼包', '英雄装备等buff类', 'SLG', '混合'] },
  { kw: ['转盘折扣'], types: ['混合-日常活动&礼包', '混合-日常活动&礼包-自选礼包', '英雄装备等buff类', 'SLG', '混合'] },
  { kw: ['可视化礼包', 'map_pack'], types: ['SHOP-SHOP混合', 'SHOP-SHOP混合-触发特惠', 'SHOP', 'SLG', '混合'] },
  { kw: ['建筑队列礼包', '科研队列', '额外行军', 'builder', 'research_queue', 'extra_troop'], types: ['SHOP-SHOP混合', 'SHOP-SHOP混合-触发特惠', 'SHOP', 'SLG', '混合'] },
  { kw: ['雷达增加'], types: ['SHOP-SHOP混合', 'SHOP-SHOP混合-触发特惠', 'SHOP', 'SLG', '混合'] },
];

function classify(name, id) {
  for (const rule of RULES) {
    const hit = rule.kw.some(kw => rule.matchId ? (id.includes(kw) || name.includes(kw)) : name.includes(kw));
    if (hit) return rule.types;
  }
  return null;
}

function updateRange(spreadsheetId, range, values) {
  const params = { spreadsheetId, range, valueInputOption: 'USER_ENTERED' };
  const body = { values };
  const paramsStr = JSON.stringify(params);
  const bodyStr = JSON.stringify(body);
  const tmpScript = path.join(os.tmpdir(), `gws_${Date.now()}.sh`);
  fs.writeFileSync(tmpScript, `#!/bin/bash\ngws sheets:v4 spreadsheets values update --params '${paramsStr.replace(/'/g, "'\\''")}' --json '${bodyStr.replace(/'/g, "'\\''")}'\n`);
  try {
    const result = execSync(`bash "${tmpScript}"`, { encoding: 'utf-8', maxBuffer: 10 * 1024 * 1024 });
    fs.unlinkSync(tmpScript);
    return JSON.parse(result);
  } catch (e) {
    try { fs.unlinkSync(tmpScript); } catch {}
    throw e;
  }
}

async function main() {
  console.log('=== 回填未分类礼包 ===\n');

  console.log('1. 读取主数据表...');
  const data = JSON.parse(execSync(
    `gws sheets +read --spreadsheet "${SHEET_ID}" --range "'${TAB}'!A:I"`,
    { encoding: 'utf-8', maxBuffer: 50 * 1024 * 1024 }
  ));
  const rows = data.values || [];
  console.log(`   总行数: ${rows.length - 1}`);

  console.log('2. 匹配分类...');
  const updates = []; // { rowNum, types }
  rows.slice(1).forEach((row, idx) => {
    if (row[4] !== '未分类') return;
    const types = classify(row[1] || '', row[0] || '');
    if (types) updates.push({ rowNum: idx + 2, types });
  });
  console.log(`   待更新: ${updates.length} 行`);

  // Group consecutive rows with same types into batch ranges
  // But simpler: batch N rows per update call
  const BATCH = 20;
  console.log(`\n3. 写入（每批 ${BATCH} 行）...`);
  let done = 0;

  for (let i = 0; i < updates.length; i += BATCH) {
    const batch = updates.slice(i, i + BATCH);
    // Write each row individually within a batch (they're not consecutive)
    for (const u of batch) {
      try {
        updateRange(SHEET_ID, `'${TAB}'!E${u.rowNum}:I${u.rowNum}`, [u.types]);
        done++;
      } catch (e) {
        console.error(`\n   行 ${u.rowNum} 失败:`, e.message?.slice(0, 100));
      }
    }
    process.stdout.write(`\r   进度: ${Math.min(i + BATCH, updates.length)}/${updates.length} (成功: ${done})`);
  }

  console.log(`\n\n✅ 回填完成！成功更新 ${done} / ${updates.length} 行`);
}

main().catch(console.error);
