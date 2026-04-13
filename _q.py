import requests, os, json

api_key = os.environ.get("DATAIN_API_KEY")
base = "https://datain-api.tap4fun.com/public_api"

r = requests.get(f"{base}/basic/dimensions", params={"api_key": api_key, "pageId": "GAME_DATA"}, timeout=10)
data = r.json()

# Find iap related
all_text = json.dumps(data, ensure_ascii=False)
# Search for iap or gift pack related
import re
matches = re.findall(r'"name"\s*:\s*"([^"]*(?:iap|礼包|品类|道具|活动|节日|充值|购买)[^"]*)"', all_text, re.IGNORECASE)
print("iap/gift related dimensions:", matches[:30])
print("\nTotal items:", len(data) if isinstance(data, list) else "dict")
print("Keys:", list(data.keys()) if isinstance(data, dict) else "list")
