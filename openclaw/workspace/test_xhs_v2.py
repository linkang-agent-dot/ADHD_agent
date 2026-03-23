import requests
import time

time.sleep(2)

# 每次用新session
def call_mcp(method, params):
    s = requests.Session()
    r = s.post('http://localhost:18060/mcp', 
               json={'jsonrpc':'2.0','id':1,'method':method,'params':params},
               headers={'Accept': 'application/json, text/event-stream'})
    return r

# 1. initialize
r1 = call_mcp('initialize', {'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}})
print('Init:', r1.status_code, r1.text[:300])

# 2. 等待一下再发
time.sleep(1)

# 3. 搜索 - 用新session
r3 = call_mcp('tools/call', {'name':'search_notes','arguments':{'keyword':'旅游攻略','limit':5}})
print('Search:', r3.status_code)
print(r3.text[:2000])
