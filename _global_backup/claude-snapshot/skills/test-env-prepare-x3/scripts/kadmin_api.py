#!/usr/bin/env python3
"""X3 Kadmin API client. Independent from P2 — uses X3's own base URL and access key."""

from __future__ import annotations

import json
import ssl
import urllib.request

BASE_URL = "https://api-kadmin-beta.tap4fun.com"
ACCESS_KEY = "5df3d84a-6960-11f1-ac6a-0242ac130002"

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE


def _post(path: str, body: dict) -> dict:
    body.setdefault("accessKey", ACCESS_KEY)
    data = json.dumps(body, ensure_ascii=False).encode()
    req = urllib.request.Request(f"{BASE_URL}{path}", data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Accept", "application/json")
    with urllib.request.urlopen(req, timeout=30, context=_SSL_CTX) as resp:
        return json.loads(resp.read())


def query_app(**kwargs) -> dict:
    return _post("/api/application-key/query-application-info", kwargs)


def deploy_app(name: list[str], tag: str, grace: int = 10) -> dict:
    return _post("/api/application-key/deploy", {"name": name, "tag": tag, "gracePeriodSeconds": grace})


def offline_app(name: list[str], grace: int = 10) -> dict:
    return _post("/api/application-key/offline", {"name": name, "gracePeriodSeconds": grace})


def restart_app(name: list[str], grace: int = 10) -> dict:
    return _post("/api/application-key/restart", {"name": name, "gracePeriodSeconds": grace})


def app_history(ids: list[int]) -> dict:
    return _post("/api/application-key/history", {"applicationExecuteHistoryIds": ids})


def execute_workflow(id: int = None, name: str = None) -> dict:
    """执行 workflow。注意：API 只认 name 字段，id 会被静默忽略。"""
    if name:
        return _post("/api/workflow-key/execute", {"name": [name]})
    elif id:
        # id 需先查 name 再执行
        result = query_workflow(page=1, limit=100)
        for w in result.get("info", {}).get("list", []):
            if w.get("id") == id:
                return _post("/api/workflow-key/execute", {"name": [w["name"]]})
        raise ValueError(f"workflow id={id} not found")


def query_workflow(**kwargs) -> dict:
    return _post("/api/workflow-key/query", kwargs)


def workflow_history(workflow_id: int = None, ids: list[int] = None, page: int = 1, limit: int = 5) -> dict:
    body: dict = {"page": page, "limit": limit}
    if workflow_id:
        body["workflowId"] = workflow_id
    if ids:
        body["workflowExecuteHistoryIds"] = ids
    return _post("/api/workflow-key/history", body)
