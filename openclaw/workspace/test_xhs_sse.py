import requests
import json
import time

# 使用 SSE 方式保持连接
def mcp_call(session, method, params=None, msg_id=1):
    payload = {'jsonrpc':'2.0','id':msg_id,'method':method}
    if params:
        payload['params'] = params
    
    resp = session.post('http://localhost:18060/mcp', 
                        json=payload,
                        headers={'Accept': 'application/json, text/event-stream'},
                        stream=True)
    
    # 读取所有返回
    full_text = ''
    for line in resp.iter_lines():
        if line:
            line = line.decode('utf-8')
            if line.startswith('data: '):
                full_text += line[6:] + '\n'
    
    return full_text

# 创建持久session
s = requests.Session()

# 1. initialize
print("Step 1: initialize")
result1 = mcp_call(s, 'initialize', {'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'test','version':'1.0'}})
print(result1[:500])

time.sleep(0.5)

# 2. notifications/initialized
print("\nStep 2: notifications/initialized")
result2 = mcp_call(s, 'notifications/initialized')
print(result2[:200])

time.sleep(0.5)

# 3. tools/call - 搜索
print("\nStep 3: search_notes")
result3 = mcp_call(s, 'tools/call', {'name':'search_notes','arguments':{'keyword':'旅游攻略','limit':3}}, msg_id=2)
print(result3[:3000])
