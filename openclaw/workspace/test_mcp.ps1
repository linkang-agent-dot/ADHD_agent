$body = '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
Invoke-RestMethod -Uri 'http://localhost:18060/mcp' -Method POST -Body $body -ContentType 'application/json'
