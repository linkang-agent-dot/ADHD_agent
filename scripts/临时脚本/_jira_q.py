import json, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding="utf-8")
with open("C:/Users/linkang/_jira_current.json", encoding="utf-8") as f:
    issues = json.load(f)
for i in issues:
    key = i["key"]; summary = i["fields"]["summary"]
    priority = i["fields"]["priority"]["name"]
    attachments = i["fields"].get("attachment", [])
    desc = (i["fields"].get("description", "") or "")[:200]
    att_list = [(a["id"], a["filename"]) for a in attachments]
    print(f"{key} [{priority}]")
    print(f"  {summary}")
    if desc: print(f"  desc: {desc}")
    for aid, aname in att_list: print(f"  att: {aid} | {aname}")
    print()
