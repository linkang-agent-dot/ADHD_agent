const http = require('http');

function mcpRequest(method, params = {}, id = 1) {
  return new Promise((resolve, reject) => {
    const postData = JSON.stringify({
      jsonrpc: '2.0',
      id,
      method,
      params
    });

    const req = http.request({
      hostname: 'localhost',
      port: 18060,
      path: '/mcp',
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json, text/event-stream',
        'Content-Length': Buffer.byteLength(postData)
      }
    }, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        resolve({ status: res.statusCode, body: data });
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

async function main() {
  try {
    // Step 1: initialize
    const r1 = await mcpRequest('initialize', {
      protocolVersion: '2024-11-05',
      capabilities: {},
      clientInfo: { name: 'test', version: '1.0' }
    });
    console.log('Init:', r1.status, r1.body.slice(0, 300));

    // Step 2: notifications/initialized - 无id
    const r2 = await mcpRequest('notifications/initialized', {}, null);
    console.log('Notif:', r2.status, r2.body.slice(0, 200));

    // Step 3: search
    const r3 = await mcpRequest('tools/call', {
      name: 'search_notes',
      arguments: { keyword: '旅游攻略', limit: 5 }
    }, 2);
    console.log('Search:', r3.status);
    console.log('Result:', r3.body.slice(0, 3000));
  } catch (e) {
    console.error('Error:', e.message);
  }
}

main();
