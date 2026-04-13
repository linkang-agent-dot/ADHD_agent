import subprocess, json, os, requests

os.environ['GOOGLE_WORKSPACE_PROJECT_ID'] = 'calm-repeater-489707-n1'
gws = r'C:\Users\linkang\AppData\Roaming\npm\gws.cmd'

creds_raw = subprocess.run([gws, 'auth', 'export'],
    capture_output=True, text=True, encoding='utf-8', errors='replace').stdout
creds = json.loads(creds_raw)
print("creds keys:", list(creds.keys()))

token_resp = requests.post('https://oauth2.googleapis.com/token', data={
    'client_id':     creds['client_id'],
    'client_secret': creds['client_secret'],
    'refresh_token': creds['refresh_token'],
    'grant_type':    'refresh_token',
})
print("status:", token_resp.status_code)
resp = token_resp.json()
print("resp keys:", list(resp.keys()))
if 'error' in resp:
    print("error:", resp)
else:
    print("access_token len:", len(resp.get('access_token','')))
