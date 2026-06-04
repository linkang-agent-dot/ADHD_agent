import argparse
import json
import ssl
import subprocess
import urllib.request
import requests

deploy_api = "/api/application-key/deploy"
query_api = "/api/application-key/query-application-info"

# kadmin access_key
access_keys = {
    "dev": "74823c8f-f61e-11ee-b5d7-0242ac1f0003",
    "beta": "915224d9-f61e-11ee-b6a9-0242ac130002"
}
# kadmin 地址
apis = {
    "dev": "https://api-kadmin-inner.tap4fun.com",
    "beta": "https://api-kadmin-beta.tap4fun.com",
}


def do_deploy(env, branch, name):
    """发起部署请求，返回响应 dict"""
    deploy_url = apis[env] + deploy_api
    params = {
        "accessKey": access_keys[env],
        "name": [name],
        "tag": branch,
        "gracePeriodSeconds": -1,
    }
    headers = {"content-type": "application/json"}
    response = requests.post(deploy_url, data=json.dumps(params), headers=headers)
    return response.json()


def fuzzy_find(env, keyword):
    """模糊搜索包含 keyword 的服务器名，返回名称列表"""
    url = apis[env] + query_api
    data = {
        "accessKey": access_keys[env],
        "name": [keyword],
        "limit": 10000,
    }
    resp = requests.post(url, headers={"Content-Type": "application/json"}, data=json.dumps(data))
    result = resp.json()
    names = []
    if result.get("success") and result.get("info"):
        for s in result["info"].get("list", []):
            names.append(s["Name"])
    return names


def deploy(env, branch, server_id):
    if env not in apis:
        print(f"env {env} err")
        return
    branch = branch.strip() if isinstance(branch, str) else ""
    if not branch:
        branch = "master_bugfix"
        print("未指定分支，默认使用: master_bugfix")

    # 1. 先用 default_game_ 前缀尝试
    prefixed = "default_game_" + server_id
    print(f"尝试部署: {prefixed}")
    result = do_deploy(env, branch, prefixed)

    if result.get("success"):
        print(f"[OK] 部署成功: {prefixed} -> {branch}")
        print(json.dumps(result))
        return

    if result.get("error") != "record not found":
        print(f"[FAIL] 部署失败: {json.dumps(result)}")
        return

    # 2. 前缀找不到，模糊搜索完整名称
    print(f"未找到 {prefixed}，尝试模糊搜索: {server_id}")
    matches = fuzzy_find(env, server_id)

    if not matches:
        print(f"✗ 模糊搜索也未找到包含 '{server_id}' 的服务器，请检查服务器 ID 或登录 Kadmin 后台确认。")
        return

    if len(matches) == 1:
        target = matches[0]
        print(f"找到匹配服务器: {target}，直接部署")
        result2 = do_deploy(env, branch, target)
        if result2.get("success"):
            print(f"[OK] 部署成功: {target} -> {branch}")
        else:
            print(f"[FAIL] 部署失败: {json.dumps(result2)}")
        return

    # 3. 多条匹配，列出让用户确认
    print(f"找到多个匹配服务器，请确认目标后重新指定完整名称：")
    for name in matches:
        print(f"  - {name}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", default="dev")
    parser.add_argument("-b", "--branch", default="master_bugfix")
    parser.add_argument("-s", "--server")
    args = parser.parse_args()
    deploy(args.env, args.branch, args.server)
