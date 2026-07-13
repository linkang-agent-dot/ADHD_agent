import requests, json, threading, queue, time

results = queue.Queue()
stop_event = threading.Event()

def read_sse(url):
    try:
        r = requests.get(url, stream=True, timeout=60)
        for line in r.iter_lines():
            if stop_event.is_set():
                break
            line = line.decode()
            if line.startswith('data:'):
                results.put(('data', line[5:].strip()))
            elif line.startswith('event:'):
                results.put(('event', line[6:].strip()))
    except Exception as e:
        results.put(('error', str(e)))
    finally:
        r.close()

sse_url = 'http://127.0.0.1:18080/sse'
t = threading.Thread(target=read_sse, args=(sse_url,), daemon=True)
t.start()

# Get endpoint
endpoint = None
for _ in range(10):
    try:
        item = results.get(timeout=5)
        if item[0] == 'data' and 'session_id' in item[1]:
            import re
            m = re.search(r'session_id=([a-z0-9]+)', item[1])
            if m:
                endpoint = f'/messages/?session_id={m.group(1)}'
                break
    except:
        pass

if not endpoint:
    print('FAILED: could not get SSE endpoint')
    exit(1)

print(f'Endpoint: {endpoint}')
msg_url = f'http://127.0.0.1:18080{endpoint}'

# Initialize
requests.post(msg_url, json={
    'jsonrpc':'2.0','id':1,'method':'initialize',
    'params':{'protocolVersion':'2024-11-05','capabilities':{},'clientInfo':{'name':'openclaw','version':'1.0'}}
}, timeout=10)
init_resp = results.get(timeout=10)
print(f'Init: {init_resp[:200] if init_resp else "NONE"}')

# Send initialized notification
requests.post(msg_url, json={'jsonrpc':'2.0','method':'notifications/initialized'}, timeout=5)

# Submit search
print('Submitting search...')
requests.post(msg_url, json={
    'jsonrpc':'2.0','id':2,'method':'tools/call',
    'params':{'name':'crawl_search','arguments':{'platform':'xhs','store_type':'json','keywords':'旅游攻略'}}
}, timeout=10)

# Wait for result
print('Waiting for results...')
start = time.time()
found_result = False
while time.time() - start < 90:
    try:
        item = results.get(timeout=3)
        print(f'RECV [{time.time()-start:.1f}s]: {item[1][:300]}')
        found_result = True
    except:
        if found_result:
            break

stop_event.set()
print('Done')
