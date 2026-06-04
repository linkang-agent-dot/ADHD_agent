# -*- coding: utf-8 -*-
from deploy import *
import getopt
import sys
import io
import locale

# 设置标准输出编码（解决 Windows 控制台编码问题）
def setup_console_encoding():
    """配置控制台编码以正确显示中文"""
    if sys.platform == 'win32':
        try:
            # 尝试设置控制台代码页为 UTF-8 (65001)
            import os
            os.system('chcp 65001 > nul')
            # 重新包装 stdout 和 stderr 为 UTF-8
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except Exception:
            # 如果失败，使用系统默认编码
            try:
                encoding = locale.getpreferredencoding()
                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding=encoding, errors='replace')
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding=encoding, errors='replace')
            except Exception:
                pass  # 保持默认设置

setup_console_encoding()

keyword = ""  # 关键词: clear_db/hot_reload_config/restart_with_config
server_id = ""  # 服务器ID
env = ""  # 环境: dev/beta
src_type = ""  # 部署源类型(branch, tag, commit)
src_target = ""  # 镜像tag
execute_params = ""  # 工作流参数(JSON字符串)
config_branch = ""  # 配置分支(导配置重启使用)

# 英文关键词到中文的映射
KEYWORD_MAP = {
    "clear_db": "清库",
    "hot_reload_config": "配置热更",
    "restart_with_config": "导配置重启"
}


def safe_print(*args, **kwargs):
    """安全的打印函数，处理编码错误"""
    try:
        print(*args, **kwargs)
    except UnicodeEncodeError:
        # 如果出现编码错误，尝试使用 ASCII 兼容的方式输出
        try:
            message = ' '.join(str(arg) for arg in args)
            print(message.encode('utf-8', errors='replace').decode('utf-8', errors='replace'), **kwargs)
        except Exception:
            # 最后的备选方案：只输出 ASCII 字符
            message = ' '.join(str(arg) for arg in args)
            print(message.encode('ascii', errors='replace').decode('ascii'), **kwargs)


class KaPostData:
    def __init__(self, access_key, names, src_type, src_target, execute_params, execute_images):
        self.accessKey = access_key
        self.name = names
        self.srcType = src_type
        self.srcTarget = src_target
        self.executeParams = execute_params
        self.executeImages = execute_images

    def to_dict(self):
        return {
            'accessKey': self.accessKey,
            'name': self.name,
            'srcType': self.srcType,
            'srcTarget': self.srcTarget,
            'executeParams': self.executeParams,
            'executeImages': self.executeImages
        }


def send_to_ka(name, src_type, src_target, execute_params, execute_images, success_str):
    access_key = access_keys[env]
    data = KaPostData(access_key, name, src_type, src_target, execute_params, execute_images)
    ka_url = apis[env]
    url = ka_url + "/api/workflow-key/execute"
    params = json.dumps(data.to_dict(), ensure_ascii=False)
    headers = {
        "content-type": "application/json; charset=utf-8"
    }
    response = requests.post(url, headers=headers, data=params.encode('utf-8'))
    safe_print(str(response.text))


def usage():
    safe_print("workflow_execute.py : workflow\n"
               "args:\n"
               " keyword:         关键词(clear_db/hot_reload_config/restart_with_config)\n"
               " server_id:       服务器ID\n"
               " env:             环境(dev/beta)\n"
               " src_type:        部署源类型(branch, tag, commit)\n"
               " src_target:      镜像tag\n"
               " execute_params:  工作流参数(JSON字符串)\n"
               " config_branch:   配置分支(restart_with_config/hot_reload_config需要)\n"
               " eg1:             python3 scripts/workflow_execute.py --keyword clear_db --server_id 1001 --env dev\n"
               " eg2:             python3 scripts/workflow_execute.py --keyword hot_reload_config --server_id 1001 --env beta --config_branch dev\n"
               " eg3:             python3 scripts/workflow_execute.py --keyword restart_with_config --server_id 1001 --env dev "
               "--src_type branch --src_target v1.2.3.4 --config_branch dev\n")


def get_option():
    try:
        options, args = getopt.getopt(
            sys.argv[1:],
            "",
            [
                "keyword=",
                "server_id=",
                "env=",
                "src_type=",
                "src_target=",
                "execute_params=",
                "config_branch=",
                "help",
            ],
        )
        for name, value in options:
            safe_print(name, value)
            if name == "--keyword":
                global keyword
                keyword = value
            if name == "--server_id":
                global server_id
                server_id = value
            if name == "--env":
                global env
                env = value
            if name == "--src_type":
                global src_type
                src_type = value
            if name == "--src_target":
                global src_target
                src_target = value
            if name == "--execute_params":
                global execute_params
                execute_params = value
            if name == "--config_branch":
                global config_branch
                config_branch = value
            if name == '--help':
                usage()
                return False
        return True
    except Exception as e:
        safe_print("options error", e)
        usage()
        return False


def check_option():
    global keyword
    global server_id
    global env
    global src_type
    global src_target
    global config_branch

    if keyword == "" or server_id == "" or env == "":
        safe_print("keyword、server_id 和 env 不能为空")
        return False
    if env not in ["dev", "beta"]:
        safe_print("env 只支持: dev / beta")
        return False
    if keyword not in KEYWORD_MAP:
        safe_print(f"keyword 只支持: {' / '.join(KEYWORD_MAP.keys())}")
        return False
    if src_type != "" and src_type not in ["branch", "tag", "commit"]:
        safe_print("src_type 只支持: branch / tag / commit")
        return False
    if keyword == "restart_with_config":
        if src_type == "" or src_target == "":
            safe_print("restart_with_config 需要指定 src_type 和 src_target")
            return False
        if config_branch == "":
            safe_print("restart_with_config 需要指定 config_branch")
            return False
    if keyword == "hot_reload_config":
        if config_branch == "":
            safe_print("hot_reload_config 需要指定 config_branch")
            return False
    return True


def build_workflow_name():
    keyword_cn = KEYWORD_MAP[keyword]
    if keyword == "clear_db":
        return "x2gs_" + server_id + "_清库"
    if keyword == "hot_reload_config":
        return "x2gs_" + server_id + "_导配置_热更"
    return "x2gs_" + server_id + "_导配置_重启"


def build_execute_images():
    if keyword == "clear_db":
        return [
            {"taskName": "清库", "imageType": 0},
        ]
    if keyword == "hot_reload_config":
        return [
            {"taskName": "导配置", "imageType": 1, "privateImageTag": config_branch},
            {"taskName": "热更", "imageType": 0},
        ]
    return [
        {"taskName": server_id + "服导库", "imageType": 1, "privateImageTag": config_branch},
    ]


def main():
    if get_option() == False or check_option() == False:
        return
    workflow_name = build_workflow_name()
    execute_images = build_execute_images()
    names = [workflow_name]
    execute_images_json = json.dumps(execute_images, ensure_ascii=False)

    safe_print("工作流名称:", workflow_name)
    if keyword == "restart_with_config":
        safe_print("src_type:", src_type, " src_target:", src_target)
    success_str = "执行工作流 " + workflow_name + " success"
    send_to_ka(names, src_type, src_target, execute_params, execute_images_json, success_str)


if __name__ == '__main__':
    main()
