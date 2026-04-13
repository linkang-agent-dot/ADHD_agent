import requests, os, json

api_key = os.environ.get("DATAIN_API_KEY")
base_url = "https://datain-api.tap4fun.com/public_api"

# Try to find a chart/dashboard query endpoint
# Chart 9 id: 66e25e77be17ff5999d52b86
endpoints_to_try = [
    "/chart/query",
    "/dashboard/chart/query", 
    "/trino/query",
    "/sql/execute",
    "/chart/data",
]

for ep in endpoints_to_try:
    try:
        r = requests.get(base_url + ep, params={"api_key": api_key}, timeout=5)
        print(f"{ep}: status={r.status_code}")
        if r.status_code != 404:
            print(f"  response: {r.text[:200]}")
    except Exception as e:
        print(f"{ep}: error={e}")
