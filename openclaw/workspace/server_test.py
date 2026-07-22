import requests
try:
    r = requests.get('http://127.0.0.1:18080/sse', timeout=5)
    print(f"STATUS:{r.status_code}")
except Exception as e:
    print(f"ERR:{e}")
