# -*- coding: utf-8 -*-
import requests
import json
import sys
sys.stdout.reconfigure(encoding='utf-8')

s = requests.Session()
s.timeout = 60
hdrs = {'Accept': 'application/json, text/event-stream'}

# 1. initialize
r1 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':1,'method':'initialize',
          'params':{'protocolVersion':'2024-11-05','capabilities':{},
                    'clientInfo':{'name':'openclaw','version':'1.0'}}},
    headers=hdrs)
print('Init:', r1.status_code)

session_id = r1.headers.get('Mcp-Session-Id')
hdrs['Mcp-Session-Id'] = session_id

# 2. 检查登录状态
r_check = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':2,'method':'tools/call',
          'params':{'name':'check_login_status','arguments':{}}},
    headers=hdrs)
print('Login status:', r_check.status_code, r_check.text[:500])

# 3. initialized
s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','method':'notifications/initialized'},
    headers=hdrs)

# 4. 搜索
r3 = s.post('http://localhost:18060/mcp', 
    json={'jsonrpc':'2.0','id':3,'method':'tools/call',
          'params':{'name':'search_feeds','arguments':{'keyword':'旅游攻略'}}},
    headers=hdrs)
print('Search:', r3.status_code)
print(r3.text[:3000])
