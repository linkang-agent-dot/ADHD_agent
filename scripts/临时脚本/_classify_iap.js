#!/usr/bin/env node
const { execSync } = require('child_process');

const data = JSON.parse(execSync(
  'gws sheets +read --spreadsheet "1rPK9k75RvSb897-BS6l-9ZvrU-iAefE-e9H2-uAnCc4" --range "\'礼包维表-iap\'!A:I"',
  { encoding: 'utf-8', maxBuffer: 50 * 1024 * 1024 }
));

const rows = data.values || [];
const unclassified = rows.slice(1).filter(r => r[4] === '未分类');

const RULES = [
  // ======= 英雄装备+洗练 =======
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-成长线-成就', kw: ['eqpt_achv'], matchId: true, t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-触发特惠', kw: ['英雄装备-橙色-加工', '英雄装备-红色-加工', '英雄装备-紫色-加工', '英雄装备-紫色-高级', '英雄装备-橙色-高级', '英雄装备-橙色-普通', '英雄装备-紫色-普通', '装备触发'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-触发特惠', kw: ['战装突破一条龙', '红20级_战装', '红23级_战装', '红25级_战装', '红27级_战装', '红29级_战装', '橙20级_战装'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-触发特惠', kw: ['战装重铸触发'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-常驻平价', kw: ['英雄装备材料', '装备材料', '重铸矿晶', '高级重铸矿晶', '幻化刷'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-常驻平价', kw: ['装备周卡'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-成长线-破冰', kw: ['英雄装备破冰'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄装备+洗练', sub: '英雄装备+洗练-英雄装备-活动特惠', kw: ['装备_尖端套装', '装备_征服者套装', '装备_精密套装', '装备_战神套装'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= 战车 =======
  { cat: '战车-战车成长', sub: '战车-战车成长-活动特惠', kw: ['战装大富翁'], t3: '士兵', t4: 'SLG' },

  // ======= 军备+兵种技能 =======
  { cat: '军备+兵种技能', sub: '军备+兵种技能-军备-触发特惠', kw: ['军备触发', 'T6军备触发', '军备唤醒'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '军备+兵种技能', sub: '军备+兵种技能-军备-触发特惠', kw: ['兵种技能触发', '兵种技能材料锚点'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '军备+兵种技能', sub: '军备+兵种技能-军备-触发特惠', kw: ['犀牛技能触发', '毒蝎技能触发', '巨象技能触发', '天鹰技能触发', '雄狮技能触发', '螳螂技能触发', '战龟技能触发'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '军备+兵种技能', sub: '军备+兵种技能-军备-常驻平价', kw: ['超凡军备箱'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '军备+兵种技能', sub: '军备+兵种技能-军备-触发特惠', kw: ['飙车族-分支', '打击手-分支', '射击手-分支', '攻城车-分支'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '军备+兵种技能', sub: '军备+兵种技能-军备-活动特惠', kw: ['军备7日活动'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= 机甲 =======
  { cat: '机甲', sub: '机甲-机甲成长-常驻平价', kw: ['重装出击付费材料', '驾驶经验', '神经增强剂', '猩战手册', '晶体元件', '猿晶燃料'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '机甲', sub: '机甲-机甲成长-触发特惠', kw: ['橙机师升级', '紫机师升级', '机能核心'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '机甲', sub: '机甲-机甲成长-成长线-破冰', kw: ['巨象破冰', '雄狮破冰', '螳螂破冰'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '机甲', sub: '机甲-机甲成长-触发特惠', kw: ['毒尾蝎技能触发', '雷鸟技能触发'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= 收藏品 =======
  { cat: '收藏品', sub: '收藏品-收藏品-常驻特惠', kw: ['展台混合锚点', '胶囊锚点', '胶囊周卡', '高分子材料锚点'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '收藏品', sub: '收藏品-收藏品-常驻特惠', kw: ['装饰兑换券', '装饰商店随机', '行军表情'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= 英雄-英雄天赋 =======
  { cat: '英雄-英雄天赋', sub: '英雄-英雄天赋-常驻平价', kw: ['双天赋礼包', '双天赋_'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= 英雄-英雄成长 =======
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-触发特惠', kw: ['橙色斗士', '紫色斗士', '紫将即将', '首次紫色', '英雄双天赋'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-触发特惠', kw: ['培养礼包'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-常驻特惠', kw: ['赛季金头', '英雄道具', '英雄重置', '精英招募'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-触发特惠', kw: ['专属礼包'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-常驻特惠', kw: ['每日特惠（', '每日特惠_', '每日触发礼包', '每日抽奖'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-活动特惠', kw: ['英雄联动'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '英雄-英雄成长', sub: '英雄-英雄成长-常驻特惠', kw: ['金修女阶梯'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= 英雄-宝石 =======
  { cat: '英雄-宝石', sub: '英雄-宝石-常驻平价', kw: ['宝石框架活动', '宝石纹章基金'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= SLG-加速 =======
  { cat: 'SLG-加速', sub: 'SLG-加速-触发特惠', kw: ['战损礼包', '训练治疗整合版', 'T3训练', 'T4训练', 'T5训练', 'T6训练', '训练部队触发'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-触发特惠', kw: ['科研过程', '精英研究', '研究所-', '16级研究', '24级研究', '转基因科技'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-触发特惠', kw: ['占领氏族', '争夺太空城', '争夺补给站'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-触发特惠', kw: ['破冰触发礼包（城建', '破冰触发礼包（训练'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-常驻平价', kw: ['t6礼包', '每日任务礼包'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-触发特惠', kw: ['转基因香蕉树'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-活动特惠', kw: ['英灵殿返还'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-加速', sub: 'SLG-加速-常驻平价', kw: ['氮气特卖'], t3: '科研城建', t4: 'SLG' },

  // ======= SLG-CD =======
  { cat: 'SLG-CD', sub: 'SLG-CD-常驻平价', kw: ['cd银行礼包', '猿猴币', '小猪存钱罐'], t3: '金币 + 节日', t4: 'SLG' },

  // ======= SLG-SLG混合 =======
  { cat: 'SLG-SLG混合', sub: 'SLG-SLG混合-活动特惠', kw: ['世界boss', '合服礼包'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-SLG混合', sub: 'SLG-SLG混合-常驻平价', kw: ['资源周卡', 'cpe进度'], t3: '科研城建', t4: 'SLG' },
  { cat: 'SLG-SLG混合', sub: 'SLG-SLG混合-活动特惠', kw: ['付费飞服'], t3: '科研城建', t4: 'SLG' },

  // ======= 混合-节日活动 =======
  { cat: '混合-节日活动', sub: '混合-节日活动-节日特惠', kw: ['感恩节', '复活节连锁', '科技节', '拓荒节', '泳池派对', '游泳圈', '沙滩节', '登月节', '圣诞', '万圣', '马戏节'], t3: '金币 + 节日', t4: 'SLG' },
  { cat: '混合-节日活动', sub: '混合-节日活动-节日特惠', kw: ['端午节', '幼猴节', '登月转盘', '科技赠礼'], t3: '金币 + 节日', t4: 'SLG' },
  { cat: '混合-节日活动', sub: '混合-节日活动-节日特惠', kw: ['千万下载', '三千万下载', '四千万下载', '五千万下载', '六千万下载', '七千万下载'], t3: '金币 + 节日', t4: 'SLG' },
  { cat: '混合-节日活动', sub: '混合-节日活动-节日特惠', kw: ['GACHA礼包', 'gacha礼包'], t3: '金币 + 节日', t4: 'SLG' },
  { cat: '混合-节日活动', sub: '混合-节日活动-节日特惠', kw: ['狙击子弹'], t3: '金币 + 节日', t4: 'SLG' },

  // ======= 混合-BP&月卡 =======
  { cat: '混合-BP&月卡', sub: '混合-BP&月卡-其他BP', kw: ['通行证', 'battle_pass', '订阅卡', 'subscription', '酒馆登陆bp', '回归'], t3: '其他', t4: 'SLG' },
  { cat: '混合-BP&月卡', sub: '混合-BP&月卡-其他BP', kw: ['新首充连锁'], t3: '其他', t4: 'SLG' },

  // ======= 混合-日常活动&礼包 =======
  { cat: '混合-日常活动&礼包', sub: '混合-日常活动&礼包-月度礼包', kw: ['循环基因', '基因贬值'], t3: '科研城建', t4: 'SLG' },
  { cat: '混合-日常活动&礼包', sub: '混合-日常活动&礼包-自选礼包', kw: ['酒馆积分', '酒馆会员'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '混合-日常活动&礼包', sub: '混合-日常活动&礼包-自选礼包', kw: ['砍价', '欢乐币'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '混合-日常活动&礼包', sub: '混合-日常活动&礼包-自选礼包', kw: ['多档位转盘', '多档位翻牌'], t3: '英雄装备等buff类', t4: 'SLG' },
  { cat: '混合-日常活动&礼包', sub: '混合-日常活动&礼包-自选礼包', kw: ['转盘折扣'], t3: '英雄装备等buff类', t4: 'SLG' },

  // ======= SHOP =======
  { cat: 'SHOP-SHOP混合', sub: 'SHOP-SHOP混合-触发特惠', kw: ['可视化礼包', 'map_pack'], t3: 'SHOP', t4: 'SHOP' },
  { cat: 'SHOP-SHOP混合', sub: 'SHOP-SHOP混合-触发特惠', kw: ['建筑队列礼包', '科研队列', '额外行军', 'builder', 'research_queue', 'extra_troop'], t3: 'SHOP', t4: 'SHOP' },
  { cat: 'SHOP-SHOP混合', sub: 'SHOP-SHOP混合-触发特惠', kw: ['雷达增加'], t3: 'SHOP', t4: 'SHOP' },
];

// Match
const results = {};
const stillUnmatched = [];

unclassified.forEach(r => {
  const name = r[1] || '';
  const id = r[0] || '';
  let matched = false;
  for (const rule of RULES) {
    const hit = rule.kw.some(kw => {
      if (rule.matchId) return id.includes(kw) || name.includes(kw);
      return name.includes(kw);
    });
    if (hit) {
      const key = rule.cat + '|' + rule.sub + '|' + rule.t3 + '|' + rule.t4;
      if (!results[key]) results[key] = [];
      results[key].push({ id, name, price: r[3] || '0' });
      matched = true;
      break;
    }
  }
  if (!matched) stillUnmatched.push({ id, name, price: r[3] || '0' });
});

// Output
const catOrder = ['英雄装备+洗练', '战车', '军备+兵种技能', '机甲', '收藏品', '英雄-英雄天赋', '英雄-英雄成长', '英雄-宝石', 'SLG-加速', 'SLG-CD', 'SLG-SLG混合', '混合-节日活动', '混合-BP&月卡', '混合-日常活动&礼包', 'SHOP'];

let totalMatched = 0;
const sortedEntries = Object.entries(results).sort((a, b) => {
  const ca = catOrder.findIndex(c => a[0].split('|')[0].startsWith(c));
  const cb = catOrder.findIndex(c => b[0].split('|')[0].startsWith(c));
  return (ca === -1 ? 99 : ca) - (cb === -1 ? 99 : cb);
});

for (const [key, items] of sortedEntries) {
  totalMatched += items.length;
  const [cat, sub, t3, t4] = key.split('|');
  console.log('');
  console.log('## ' + cat + ' → ' + sub + ' (' + items.length + '条)');
  console.log('   [iap_type=' + cat + ', iap_type2=' + sub + ', iap_type3=' + t3 + ', iap_type4=' + t4 + ']');
  items.forEach(i => {
    console.log('   ' + i.name + ' | $' + i.price + ' | ' + i.id);
  });
}

console.log('');
console.log('========================================');
console.log('总未分类: ' + unclassified.length);
console.log('已预分类: ' + totalMatched);
console.log('仍未分类: ' + stillUnmatched.length);
if (stillUnmatched.length > 0) {
  console.log('');
  console.log('## 仍未分类 (' + stillUnmatched.length + '条)');
  stillUnmatched.forEach(i => {
    console.log('   ' + i.name + ' | $' + i.price + ' | ' + i.id);
  });
}
