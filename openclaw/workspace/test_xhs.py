import requests
import json

session = requests.Session()

# Initialize
init_resp = session.post('http://localhost:18060/mcp', 
    json={'jsonrpc': '2.0', 'id': 1, 'method': 'initialize', 'params': 
          {'protocolVersion': '2024-11-05', 'capabilities': {}, 
           'clientInfo': {'name': 'test', 'version': '1.0'}, 'processId': 1}},
    headers={'Accept': 'application/json, text/event-stream'})
print('Init:', init_resp.status_code, init_resp.text[:200])

# Search
search_resp = session.post('http://localhost:18060/mcp', 
    json={'jsonrpc': '2.0', 'id': 2, 'method': 'tools/call', 'params': 
          {'name': 'search_notes', 'arguments': {'keyword': '旅游攻略', 'limit': 10}}},
    headers={'Accept': 'application/json, text/event-stream'})
print('Search:', search_resp.status_code)
print(search_resp.text[:3000])
