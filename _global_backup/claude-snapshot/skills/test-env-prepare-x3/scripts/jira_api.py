#!/usr/bin/env python3
"""Jira API — 查询 issue、添加评论。"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

JIRA_URL = "https://jira.tap4fun.com"


def load_token(auth_file: str = "~/.jira-credentials.json") -> str:
    path = Path(auth_file).expanduser()
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data["token"].strip()


def _headers(token: str) -> dict:
    return {
        "Authorization": f"Bearer {token}",
        "Accept": "application/json",
        "Content-Type": "application/json",
    }


def query_issue(token: str, issue_id: str) -> dict:
    r = requests.get(f"{JIRA_URL}/rest/api/2/issue/{issue_id}", headers=_headers(token), timeout=15)
    r.raise_for_status()
    return r.json()


def print_issue(data: dict):
    f = data.get("fields", {})
    print(f"Summary: {f.get('summary', '')}")
    print(f"Status: {f.get('status', {}).get('name', '')}")
    print(f"Type: {f.get('issuetype', {}).get('name', '')}")
    print(f"Priority: {f.get('priority', {}).get('name', '')}")
    print(f"Reporter: {f.get('reporter', {}).get('displayName', '')}")
    print(f"Assignee: {(f.get('assignee') or {}).get('displayName', '')}")
    print()
    print("Description:")
    print(f.get("description", "") or "(empty)")
    att = f.get("attachment", [])
    if att:
        print(f"\nAttachments ({len(att)}):")
        for a in att:
            print(f"  - {a['filename']}: {a['content']}")
    comments = f.get("comment", {}).get("comments", [])
    if comments:
        print(f"\nComments ({len(comments)}):")
        for c in comments[-5:]:
            author = c.get("author", {}).get("displayName", "")
            body = c.get("body", "")[:300]
            print(f"  [{author}]: {body}")


def add_comment(token: str, issue_id: str, body: str) -> dict:
    r = requests.post(
        f"{JIRA_URL}/rest/api/2/issue/{issue_id}/comment",
        headers=_headers(token),
        json={"body": body},
        timeout=15,
    )
    r.raise_for_status()
    return r.json()


def main() -> int:
    parser = argparse.ArgumentParser(description="Jira API")
    sub = parser.add_subparsers(dest="cmd")

    q = sub.add_parser("query", help="查询 issue")
    q.add_argument("issue", help="Issue ID (如 X3NEW-1518)")
    q.add_argument("--auth-file", default="~/.jira-credentials.json")

    c = sub.add_parser("comment", help="添加评论")
    c.add_argument("issue", help="Issue ID")
    c.add_argument("text", help="评论内容")
    c.add_argument("--auth-file", default="~/.jira-credentials.json")

    args = parser.parse_args()
    if not args.cmd:
        parser.print_help()
        return 0

    token = load_token(args.auth_file)

    if args.cmd == "query":
        data = query_issue(token, args.issue)
        print_issue(data)
    elif args.cmd == "comment":
        result = add_comment(token, args.issue, args.text)
        print(f"评论已添加: {JIRA_URL}/browse/{args.issue}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
