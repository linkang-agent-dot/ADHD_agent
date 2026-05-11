#!/usr/bin/env python3
"""通过钉钉 webhook 机器人发送消息到 QA 群"""

import sys
import json
import urllib.request

WEBHOOK_URL = "https://oapi.dingtalk.com/robot/send?access_token=9b4beb0c2903fdb7bca49eb56e7bc7efd69ee2f947b026cfd5693d1929f10334"
# 关键词: bug（消息中必须包含）


def send_markdown(title, content, at_mobiles=None):
    """发送 markdown 消息"""
    data = {
        "msgtype": "markdown",
        "markdown": {
            "title": title,
            "text": content
        }
    }
    if at_mobiles:
        data["at"] = {"atMobiles": at_mobiles, "isAtAll": False}
    
    return _send(data)


def send_text(content, at_mobiles=None):
    """发送纯文本消息"""
    data = {
        "msgtype": "text",
        "text": {"content": content}
    }
    if at_mobiles:
        data["at"] = {"atMobiles": at_mobiles, "isAtAll": False}
    
    return _send(data)


def _send(data):
    req = urllib.request.Request(
        WEBHOOK_URL,
        data=json.dumps(data).encode("utf-8"),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            result = json.loads(resp.read())
            if result.get("errcode") == 0:
                print("发送成功")
                return True
            else:
                print(f"发送失败: {result}", file=sys.stderr)
                return False
    except Exception as e:
        print(f"发送异常: {e}", file=sys.stderr)
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 send_to_qa.py <消息内容>")
        sys.exit(1)
    
    msg = " ".join(sys.argv[1:])
    send_text(msg)
