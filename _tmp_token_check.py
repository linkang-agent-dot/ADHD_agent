import json

# 尝试不同编码
for enc in ['gbk', 'latin-1', 'cp1252']:
    try:
        with open(r'C:\Users\linkang\.config\gws\token_cache.json', encoding=enc) as f:
            d = json.load(f)
        print(f"成功用 {enc} 解码")
        print("keys:", list(d.keys())[:5])
        # 找 access_token
        def find_token(obj, depth=0):
            if depth > 4:
                return
            if isinstance(obj, dict):
                if 'access_token' in obj:
                    print("  access_token:", obj['access_token'][:40] + '...')
                    print("  token_type:", obj.get('token_type',''))
                    print("  expiry:", obj.get('expiry', obj.get('expires_at','')))
                    return True
                for v in obj.values():
                    if find_token(v, depth+1):
                        return True
            elif isinstance(obj, list):
                for item in obj:
                    if find_token(item, depth+1):
                        return True
        find_token(d)
        break
    except Exception as e:
        print(f"{enc} 失败: {e}")
