const fs = require('fs');
const path = require('path');

const AUTH_FILE = path.join(process.env.USERPROFILE, '.igame-auth.json');
const CSV_FILE = 'C:\\Users\\linkang\\Downloads\\asset_11112765_80_full.csv';
const API_HOST = 'https://webgw-cn.tap4fun.com';

async function main() {
  // 读取认证
  const auth = JSON.parse(fs.readFileSync(AUTH_FILE, 'utf-8'));

  // 读取 CSV
  const csv = fs.readFileSync(CSV_FILE, 'utf-8');
  const lines = csv.split('\n').slice(1).filter(l => l.trim());

  // 构造 to 数组 - 完全匹配网页格式
  const toArray = lines.map(line => {
    const [playerId, serverId, itemId, amount] = line.split(',');
    return {
      playerId: playerId.trim(),
      serverId: serverId.trim(),
      assets: [{
        id: itemId.trim(),
        amount: parseInt(amount.trim()),
        assetType: 'PROP'
      }]
    };
  });

  console.log(`Total players: ${toArray.length}`);

  // 构造邮件内容 - 匹配网页格式
  const content = {
    cn: {
      title: '奖励补偿发放',
      body: '亲爱的指挥官：\n\n由于游戏内数据异常，导致您在单笔充值活动中没有收到对应的奖励，我们已经修复了这个问题，因此给您带来的不便我们深感歉意，在此将奖励补发给您，请注意查收：\n\n感谢您对Age of Apes的理解与支持，祝愿火箭发射顺利！\n\n罗杰副官',
      collectionId: -1
    },
    en: {
      title: 'Reward Re-Send',
      body: 'Dear Captain,\n\nDue to data abnormalities, you did not receive the corresponding rewards for the Single Recharge event. We have fixed this issue and have included the appropriate rewards here. Please claim them below.\n\nThank you for your understanding and support of Age of Apes. May the bananas be with you and see you around the Tavern!\n\nDeputy Roger',
      collectionId: -1
    }
  };

  // 构造请求 - 完全匹配网页格式
  const params = {
    content: content,
    to: toArray,
    remark: '单笔充值活动奖励补发',
    mailCategoryId: 5
  };

  console.log('Sending request to /ark/mails ...');
  console.log('First player:', JSON.stringify(toArray[0]));

  // 发送请求
  const resp = await fetch(`${API_HOST}/ark/mails`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${auth.token}`,
      'clientid': auth.clientId,
      'gameid': auth.gameId || '1041',
      'regionid': auth.regionId || '201',
      'origin': 'https://igame.tap4fun.com',
      'referer': 'https://igame.tap4fun.com/',
    },
    body: JSON.stringify(params)
  });

  const result = await resp.json();
  console.log('Response:', JSON.stringify(result, null, 2));

  if (result.success) {
    console.log('\n✓ 邮件提交成功！');
  } else {
    console.log('\n✗ 提交失败:', result.message);
  }
}

main().catch(err => {
  console.error('Error:', err.message);
  process.exit(1);
});
