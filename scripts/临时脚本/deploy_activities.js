const { execSync } = require('child_process');

const IGAME_QUERY = 'C:/Users/linkang/.claude/skills/igame-skill/scripts/igame-query.js';

const activities = [
  { name: '主城特效累充bingo', configId: '21115750' },
  { name: '主城特效累充-服务器版', configId: '21115749' },
  { name: '异族大富翁-第二期-皮肤抽奖', configId: '21115686' },
  { name: '机甲累充', configId: '21115767' },
  { name: '每日异族大富翁礼包', configId: '21115693' },
  { name: '赛车本体活动', configId: '21115759' },
  { name: '赛车活动-组队', configId: '21115763' },
  { name: '节日BP', configId: '21115659' },
  { name: '强消耗扭蛋', configId: '21115386' },
  { name: '节日BP-2', configId: '21115677' },
  { name: '大富翁-节日装饰', configId: '21115631' },
  { name: '大富翁-团队合作子活动', configId: '21115745' },
  { name: '周卡', configId: '21115667' },
  { name: '节日押镖', configId: '21115519' },
  { name: '节日押镖-子任务', configId: '21115520' },
  { name: '挖孔优化', configId: '21115735' },
  { name: '挖矿', configId: '21115396' },
  { name: '挖矿-累计活动', configId: '21115748' },
  { name: '节日交换活动', configId: '21115766' },
  { name: '掉落转付费', configId: '21115708' },
  { name: '7日', configId: '21115622' },
  { name: 'bingo', configId: '21127035' },
  { name: '联动礼包', configId: '21115754' },
  { name: '行军特效-付费率', configId: '21115753' },
  { name: '行军表情-付费率', configId: '21115755' },
  { name: '预购连锁礼包', configId: '21115681' },
  { name: '贬值商店', configId: '21115571' },
  { name: '抢购礼包', configId: '21115751' },
  { name: '挂机BP', configId: '21115607' },
  { name: '巨猿', configId: '21115756' },
  { name: '签到', configId: '21115757' },
  { name: '节日卡包三合一', configId: '21115743' },
  { name: '节日卡包BP', configId: '21115744' },
  { name: '新7日活动', configId: '21115758' },
];

// UTC 时间: 2026-04-08 00:00 UTC ~ 2026-04-11 00:00 UTC
const startTime = 1775606400000; // 2026-04-08T00:00:00.000Z
const endTime = 1775865600000;   // 2026-04-11T00:00:00.000Z
const serverId = 2000302;

console.log(`部署 ${activities.length} 个活动到服务器 ${serverId}`);
console.log('时间: 2026-04-08 00:00 UTC ~ 2026-04-11 00:00 UTC\n');

let success = 0, failed = 0;

for (const act of activities) {
  const payload = [{
    activityConfigId: act.configId,
    name: act.name,
    startTime,
    endTime,
    previewTime: 0,
    endShowTime: 0,
    acrossServer: 0,
    acrossServerRank: 0,
    servers: [[serverId]]
  }];

  try {
    const payloadStr = JSON.stringify(JSON.stringify(payload));
    const cmd = `node "${IGAME_QUERY}" write "activity/add_activity/submitActivity" ${payloadStr}`;
    const result = execSync(cmd, { encoding: 'utf8', timeout: 30000 });
    const json = JSON.parse(result);
    if (json.success && json.data) {
      const id = Array.isArray(json.data) ? json.data[0] : json.data;
      console.log(`✓ ${act.name} (id=${id})`);
      success++;
    } else {
      console.log(`✗ ${act.name}: ${json.message || 'unknown error'}`);
      failed++;
    }
  } catch (e) {
    console.log(`✗ ${act.name}: ${e.message.split('\n')[0]}`);
    failed++;
  }
}

console.log(`\n完成: 成功 ${success}, 失败 ${failed}`);
