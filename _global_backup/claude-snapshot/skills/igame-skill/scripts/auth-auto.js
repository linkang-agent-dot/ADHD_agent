// iGame 一键认证：启动 Chrome(专属profile) -> CDP 注入提取 token/clientId -> 写 ~/.igame-auth.json
// Node 18+ (自带 WebSocket)。用法: node auth-auto.js [gameId]
const fs = require('fs');
const os = require('os');
const path = require('path');
const { spawn } = require('child_process');

const GAME_ID = process.argv[2] || '1090';      // 默认 X3
const REGION_ID = '201';
const PORT = 9222;
const URL = 'https://igame.tap4fun.com';
const PROFILE = path.join(os.homedir(), '.igame-chrome-profile');
const AUTH_FILE = path.join(os.homedir(), '.igame-auth.json');
const EXTRACT = fs.readFileSync(path.join(__dirname, 'extract-auth.js'), 'utf8');

const CHROMES = [
  'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe',
  'C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe',
];
const sleep = ms => new Promise(r => setTimeout(r, ms));

async function httpJson(p) {
  const res = await fetch(`http://127.0.0.1:${PORT}${p}`);
  return res.json();
}

// 在指定 target 上执行 EXTRACT，返回 {token, clientId} 或 null
async function evalOnTarget(wsUrl) {
  return new Promise((resolve) => {
    let done = false;
    const ws = new WebSocket(wsUrl);
    const finish = v => { if (!done) { done = true; try { ws.close(); } catch {} resolve(v); } };
    const timer = setTimeout(() => finish(null), 8000);
    ws.onopen = () => ws.send(JSON.stringify({ id: 1, method: 'Runtime.evaluate',
      params: { expression: EXTRACT, returnByValue: true } }));
    ws.onmessage = (ev) => {
      try {
        const msg = JSON.parse(ev.data);
        if (msg.id === 1) {
          clearTimeout(timer);
          const val = msg.result && msg.result.result && msg.result.result.value;
          finish(val ? JSON.parse(val) : null);
        }
      } catch { }
    };
    ws.onerror = () => { clearTimeout(timer); finish(null); };
  });
}

(async () => {
  const chrome = CHROMES.find(p => fs.existsSync(p));
  if (!chrome) { console.error('未找到 Chrome/Edge'); process.exit(1); }
  console.log('启动浏览器(专属 igame 配置)...');
  const child = spawn(chrome, [
    `--remote-debugging-port=${PORT}`,
    `--user-data-dir=${PROFILE}`,
    '--no-first-run', '--no-default-browser-check',
    URL,
  ], { detached: true, stdio: 'ignore' });
  child.unref();

  console.log('等待浏览器就绪 + 你在打开的窗口里登录(企业微信扫码)...');
  console.log('（登录过一次后，下次直接自动认证，无需再扫码）\n');

  const deadline = Date.now() + 5 * 60 * 1000; // 最多等 5 分钟
  let lastMsg = 0;
  while (Date.now() < deadline) {
    try {
      const list = await httpJson('/json');
      const page = list.find(t => t.type === 'page' && /igame\.tap4fun\.com/.test(t.url) && t.webSocketDebuggerUrl);
      if (page) {
        const r = await evalOnTarget(page.webSocketDebuggerUrl);
        if (r && r.token && !r.error) {
          fs.writeFileSync(AUTH_FILE, JSON.stringify({
            token: r.token, clientId: r.clientId, gameId: GAME_ID, regionId: REGION_ID,
          }, null, 2), 'utf8');
          console.log('\n✅ 认证成功！已写入 ' + AUTH_FILE);
          console.log('   gameId=' + GAME_ID + '  token=' + r.token.slice(0, 12) + '...');
          console.log('\n可以关掉浏览器了。回到对话继续查询。');
          process.exit(0);
        }
      }
    } catch (e) { /* 调试端口还没起来 */ }
    if (Date.now() - lastMsg > 15000) { console.log('  ...仍在等待登录/就绪'); lastMsg = Date.now(); }
    await sleep(2500);
  }
  console.error('\n❌ 超时(5分钟)未拿到 token。请确认已在浏览器登录后重试。');
  process.exit(1);
})();
