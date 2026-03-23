const http = require('http');

function callMCP(method, params = {}) {
  return new Promise((resolve, reject) => {
    const data = JSON.stringify({
      jsonrpc: '2.0',
      id: 1,
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
        'Accept': 'application/json'
      }
    }, res => {
      let body = '';
      res.on('data', c => body += c);
      res.on('end', () => {
        try {
          // Extract JSON from SSE format
          const lines = body.split('\n');
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const jsonStr = line.slice(6);
              if (jsonStr.trim()) {
                const result = JSON.parse(jsonStr);
                if (result.error) {
                  reject(new Error(result.error.message));
                  return;
                }
                resolve(result.result);
                return;
              }
            }
          }
          // Try parsing whole body as JSON
          const result = JSON.parse(body);
          if (result.error) {
            reject(new Error(result.error.message));
          } else {
            resolve(result.result);
          }
        } catch (e) {
          reject(e);
        }
      });
    });

    req.on('error', reject);
    req.write(data);
    req.end();
  });
}

async function main() {
  // First initialize
  await callMCP('initialize', {
    protocolVersion: '2024-11-05',
    capabilities: {},
    clientInfo: { name: 'test', version: '1.0' },
    processId: process.pid
  });

  // Now call the tool
  const result = await callMCP('tools/call', {
    name: 'get_feed_detail',
    arguments: {
      click_more_replies: false,
      feed_id: '697cb886000000000a033a78',
      limit: 20,
      load_all_comments: false,
      xsec_token: 'ABGy6XETk7WudfAgQHnRcXn5PPmSjocn-52VN9FnyrpJQ='
    }
  });

  console.log(JSON.stringify(result, null, 2));
}

main().catch(console.error);
