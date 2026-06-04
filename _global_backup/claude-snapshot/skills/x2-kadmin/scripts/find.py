from deploy import *

plugin_types_dict = {
    "games": ["game", "kvk", "kvk2", "kvk3", "kvk4", "kvk5", "kvk43"],
}

def print_red(text):
    print(f"\033[91m{text}\033[0m\n")

def get_server_detail_by_kadmin(host, data):
    try:
        url = "{}/api/application-key/query-application-info".format(host)
        header = {"Content-Type": "application/json"}
        #print(data)
        resp = requests.post(
            url=url,
            headers=header,
            data=json.dumps(data)
        )
        output = resp.json()
        # print(output)
        return output
    except Exception as e:
        raise Exception("Error querying service by kadmin: {}".format(e))

def get_kadmin_run_names(result):
    tags = {}
    filter_names = []
    for s in result["info"]["list"]:
        dTag = s["LastDeployTag"]
        name = s["Name"]
        if dTag == "":
            print_red(f"没有找到部署的tag: {name}")
            continue
        if s["Status"] != "Run":
            filter_names.append(name)
            continue
        tags[name] = dTag
    if len(filter_names) > 0:
        print_red(f"查询到以下服务器: {filter_names}")
    return tags

def get_kadmin_detail_data_byserver(env, server_ids):
    host, access_key = apis[env], access_keys[env]
    serverid_arr = []
    for serverid in server_ids.split(","):
        serverid_arr.append(serverid.strip())
    # print("查询服务器ID:", serverid_arr)
    data = {
        "accessKey": access_key,
        "name": serverid_arr,
        # "lastDeployTag": self.v_tag,
        "limit": 10000,
    }
    result = get_server_detail_by_kadmin(host, data)
    return get_kadmin_run_names(result)


def get_kadmin_detail_data_bytag(env, tags):
    host, access_key = apis[env], access_keys[env]
    result_tags = {}
    for tag in tags.split(","):
        data = {"accessKey": access_key, "lastDeployTag": tag, "limit": 10000}
        result = get_server_detail_by_kadmin(host, data)
        run_names = get_kadmin_run_names(result)
        for name, dTag in run_names.items():
            result_tags[name] = dTag
    return result_tags


def get_kadmin_detail_data_byall(env):
    host, access_key = apis[env], access_keys[env]
    server_types = []
    for key, value in plugin_types_dict.items():
        for plugin_type in value:
            server_type = "default_" + plugin_type + "_"
            server_types.append(server_type)
    data = {"accessKey": access_key, "name": server_types, "limit": 10000}
    result = get_server_detail_by_kadmin(host, data)
    return get_kadmin_run_names(result)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--env", default="dev")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-q", "--query", help="分支或tag名称")
    group.add_argument("--all", action="store_true", help="查询全部")
    args = parser.parse_args()

    if args.all:
        print("查询全部服务器")
        result = get_kadmin_detail_data_byall(args.env)
        if len(result) == 0:
            print_red("没有查到结果")
            return
        for name, tag in result.items():
            print(f"{name}\t{tag}")
        return

    query = args.query.strip()
    print(f"按tag查询: {query}")
    result = get_kadmin_detail_data_bytag(args.env, query)
    result.update(get_kadmin_detail_data_byserver(args.env, query))
    if len(result) == 0:
        print_red("没有查到结果")
        return
    for name, tag in result.items():
        print(f"{name}\t{tag}")


if __name__ == "__main__":
    main()
