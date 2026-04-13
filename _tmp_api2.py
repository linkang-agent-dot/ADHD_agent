import requests, os

api_key = os.environ.get("DATAIN_API_KEY")
base_url = "https://datain-api.tap4fun.com/public_api"

# Try chart_id based query - chart 9 has id 66e25e77be17ff5999d52b86
# Try with POST
payload = {
    "chart_id": "66e25e77be17ff5999d52b86",
    "params": {
        "report_date": {"start": "2026-03-13", "end": "2026-04-02"},
        "control_id": "2112",
        "schema": "1,2,3,4,5,6",
        "server_id": "all"
    }
}

endpoints = ["/chart/execute", "/chart/run", "/dashboard/execute", "/query/chart"]
for ep in endpoints:
    r = requests.post(base_url + ep, params={"api_key": api_key}, json=payload, timeout=5)
    print(f"POST {ep}: {r.status_code}")

# Try public API routes
r = requests.get(base_url, params={"api_key": api_key}, timeout=5)
print(f"GET /: {r.status_code} - {r.text[:300]}")
