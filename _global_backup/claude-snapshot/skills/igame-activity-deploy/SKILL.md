---
name: igame-activity-deploy
description: Deploy iGame DEV activities to specific servers via activity submit API. Use when the user asks to deploy/submit/open an activity, set activity start/end time, choose server IDs, or mentions 活动部署 in X3/dev.
---

# iGame Activity Deploy

## Scope

- This skill is only for activity deployment/submit in iGame DEV gateway.
- It does not manage unrelated modules (player ban, mail, flow rate, etc.).

## Default behavior

- If user does not specify environment, use DEV activity gateway.
- Use single-server deployment by default unless user explicitly asks for multiple servers.

## Required inputs

- `activityConfigId` (example: `211110560`)
- Activity `name`
- Target `server` (example: `403`)
- Start and end time (or start date + duration in days)
- Valid auth: `token` and `clientId`
  - Stored in `C:/Users/linkang/.igame-auth.json` as `{"token": "...", "clientId": "..."}`
  - Load with: `auth = json.load(open('C:/Users/linkang/.igame-auth.json'))`
  - If token is expired (401), ask user to paste new token + clientId, then update the file.

## Time conversion rule

- **All activity times are treated as UTC directly.** Do NOT apply any timezone offset.
- When user says "2026-04-29", use `2026-04-29 00:00:00 UTC` as the epoch milliseconds.
- Duration "N days" means `endTime = startTime + N * 86400 * 1000`.
- Compute with `calendar.timegm((YYYY, MM, DD, 0, 0, 0)) * 1000` (Python).
- **Never** convert Beijing time (CST/UTC+8) to UTC for these timestamps.

## Execution steps

1. Confirm deployment target (server and time range).
2. **Resolve `activityConfigId`** if not provided by user:
   - Call `GET https://ms-inner-gateway-dev.tap4fun.com/ark/activity/query?refresh=true`
   - Headers: `authorization: Bearer <token>`, `clientid`, `gameid: 1090`, `regionid: 201`, `origin/referer: https://igame-dev.tap4fun.com`
   - Response is a list of `{"id": "...", "cn": "...", "en": "..."}` — match by `cn` keyword search.
   - This endpoint returns **all ~878 configured activities**, so nothing will be missed.
3. Build payload as a JSON array with one object:
   - `activityConfigId`, `name`, `servers`, `startTime`, `endTime`
   - plus `previewTime`, `endShowTime`, `acrossServer`, `acrossServerRank`
4. Execute submit call via helper script:
  - `python C:/Users/linkang/.claude/skills/igame-activity-deploy/scripts/submit_activity.py ...`
5. Return API result (`success`, `code`, `message`, `data`) to user.
6. If permission/login error is returned, ask user for latest browser cURL from DevTools and retry with updated token.

## Standard payload shape

```json
[
  {
    "activityConfigId": "211110560",
    "previewTime": 0,
    "startTime": 1809792000000,
    "endTime": 1810396800000,
    "endShowTime": 0,
    "acrossServerRank": 1,
    "acrossServer": 0,
    "name": "联盟IPO-生命周期2",
    "servers": [["403"]]
  }
]
```

## Command template

```bash
python C:/Users/linkang/.claude/skills/igame-activity-deploy/scripts/submit_activity.py --token "<token>" --clientid "<clientId>" --activity-config-id "211110560" --name "联盟IPO-生命周期2" --server "403" --start-ms 1809792000000 --end-ms 1810396800000
```

## Multi-server deployment

Run the script once per server. Example for 402 and 403:

```python
import json, subprocess, sys
auth = json.load(open('C:/Users/linkang/.igame-auth.json'))
base = [sys.executable, r'C:/Users/linkang/.claude/skills/igame-activity-deploy/scripts/submit_activity.py',
        '--token', auth['token'], '--clientid', auth['clientId'],
        '--activity-config-id', '211110560', '--name', '联盟IPO-生命周期2',
        '--start-ms', '1809792000000', '--end-ms', '1810396800000']
for srv in ['402', '403']:
    r = subprocess.run(base + ['--server', srv], capture_output=True)
    print(srv, r.stdout.decode('utf-8', errors='replace'))
```

## Additional resource

- See [reference.md](reference.md) for endpoint and troubleshooting.
