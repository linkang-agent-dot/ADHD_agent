# -*- coding: utf-8 -*-
import sys
import io
import locale
from deploy import *
import argparse
from datetime import datetime

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


def get_workflow_list(env, names, page=1, limit=50):
    """使用 accessKey 查询工作流列表"""
    url = apis[env] + "/api/workflow-key/query"
    params = {
        "accessKey": access_keys[env],
        "page": page,
        "limit": limit,
    }
    if names:
        params["names"] = names
    
    headers = {
        "content-type": "application/json; charset=utf-8"
    }
    data = json.dumps(params, ensure_ascii=False)
    resp = requests.post(url, data=data.encode('utf-8'), headers=headers)
    return resp.text


def get_workflow_history(env, workflow_name, page=1, limit=50):
    """使用 accessKey 查询工作流执行记录状态"""
    url = apis[env] + "/api/workflow-key/history"
    params = {
        "accessKey": access_keys[env],
        "page": page,
        "limit": limit,
    }
    if workflow_name:
        params["workflowName"] = workflow_name
    
    headers = {
        "content-type": "application/json; charset=utf-8"
    }
    data = json.dumps(params, ensure_ascii=False)
    resp = requests.post(url, data=data.encode('utf-8'), headers=headers)
    return resp.text


def build_workflow_names(module, server_id, operation):
    """根据模块类型构建工作流名称列表"""
    if module == "all":
        # 查询全部工作流：不传 names 参数
        return None
    elif module == "build":
        # 构建模块：固定名称
        return ["x2gs_构建_game"]
    elif module == "config":
        # 导配置模块：需要 server_id 和 operation
        if not server_id:
            raise ValueError("导配置模块需要指定 server_id")
        if not operation:
            raise ValueError("导配置模块需要指定 operation (clear_db/hot_reload/restart)")
        
        operation_map = {
            "clear_db": f"x2gs_{server_id}_清库",
            "hot_reload": f"x2gs_{server_id}_导配置_热更",
            "restart": f"x2gs_{server_id}_导配置_重启"
        }
        if operation not in operation_map:
            raise ValueError(f"operation 必须是: clear_db/hot_reload/restart")
        return [operation_map[operation]]
    elif module == "deploy":
        # 部署模块：需要 server_id
        if not server_id:
            raise ValueError("部署模块需要指定 server_id")
        return [f"default_game_{server_id}"]
    else:
        raise ValueError(f"未知的模块类型: {module}")


def format_timestamp(timestamp):
    """将时间戳格式化为字符串"""
    if timestamp <= 0:
        return "未执行"
    try:
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return "时间格式错误"


def format_workflow_list(result_json):
    """格式化工作流列表结果"""
    try:
        data = json.loads(result_json)
        if not data.get("success"):
            return result_json
        
        workflows = data.get("info", {}).get("list", [])
        if not workflows:
            return result_json
        
        # 格式化时间戳
        for workflow in workflows:
            if "createTime" in workflow:
                workflow["createTime"] = format_timestamp(workflow["createTime"])
            if "lastExecuteTime" in workflow:
                workflow["lastExecuteTime"] = format_timestamp(workflow["lastExecuteTime"])
        
        # 返回格式化后的 JSON
        return json.dumps(data, ensure_ascii=False, indent=2)
    except:
        return result_json


def format_workflow_history(result_json):
    """格式化工作流执行历史结果"""
    try:
        data = json.loads(result_json)
        if not data.get("success"):
            return result_json
        
        records = data.get("info", {}).get("list", [])
        if not records:
            return result_json
        
        # 格式化时间戳
        for record in records:
            if "createTime" in record:
                record["createTime"] = format_timestamp(record["createTime"])
            if "startTime" in record:
                record["startTime"] = format_timestamp(record["startTime"])
            if "endTime" in record:
                record["endTime"] = format_timestamp(record["endTime"])
        
        # 返回格式化后的 JSON
        return json.dumps(data, ensure_ascii=False, indent=2)
    except:
        return result_json


def query_workflow(env, module, query_type, server_id, operation, page, limit):
    """查询工作流"""
    # 构建工作流名称
    workflow_names = build_workflow_names(module, server_id, operation)
    
    if query_type == "list":
        if workflow_names is None:
            safe_print(f"工作流列表查询 - 模块: {module} (全部工作流)")
        else:
            safe_print(f"工作流列表查询 - 模块: {module}, 名称: {workflow_names}")
        result = get_workflow_list(env, workflow_names, page, limit)
        return format_workflow_list(result)
    elif query_type == "history":
        if module == "all":
            raise ValueError("查询全部工作流时不支持 history 模式，请使用 list 模式")
        # history 只查询单个工作流
        workflow_name = workflow_names[0]
        safe_print(f"工作流执行历史查询 - 模块: {module}, 名称: {workflow_name}")
        result = get_workflow_history(env, workflow_name, page, limit)
        return format_workflow_history(result)


def main():
    parser = argparse.ArgumentParser(
        description="查询工作流列表或执行历史记录",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 查询全部工作流列表
  python3 scripts/workflow_select.py -e dev -m all

  # 查询全部工作流列表（第2页，每页100条）
  python3 scripts/workflow_select.py -e dev -m all -p 2 -l 100

  # 查询构建工作流列表
  python3 scripts/workflow_select.py -e dev -m build

  # 查询构建工作流执行历史
  python3 scripts/workflow_select.py -e dev -m build -t history

  # 查询清库工作流
  python3 scripts/workflow_select.py -e dev -m config -s 1001 -o clear_db

  # 查询导配置热更工作流历史
  python3 scripts/workflow_select.py -e dev -m config -s 1001 -o hot_reload -t history

  # 查询导配置重启工作流
  python3 scripts/workflow_select.py -e dev -m config -s 1001 -o restart

  # 查询部署工作流
  python3 workflow_select.py -e dev -m deploy -s 25

  # 查询部署工作流历史（第2页）
  python3 scripts/workflow_select.py -e beta -m deploy -s 1001 -t history -p 2
        """
    )
    parser.add_argument("-e", "--env", default="dev", help="环境: dev/beta")
    parser.add_argument("-m", "--module", required=True, choices=["all", "build", "config", "deploy"],
                        help="模块类型: all(全部) / build(构建) / config(导配置) / deploy(部署)")
    parser.add_argument("-s", "--server_id", default="", help="服务器ID (config和deploy模块必需)")
    parser.add_argument("-o", "--operation", default="", choices=["", "clear_db", "hot_reload", "restart"],
                        help="操作类型 (仅config模块): clear_db(清库) / hot_reload(热更) / restart(重启)")
    parser.add_argument("-t", "--type", default="list", choices=["list", "history"], 
                        help="查询类型: list(工作流列表) / history(执行历史)")
    parser.add_argument("-p", "--page", type=int, default=1, help="页码，默认第1页")
    parser.add_argument("-l", "--limit", type=int, default=50, help="每页数量，默认50条")
    args = parser.parse_args()

    try:
        result = query_workflow(
            args.env, 
            args.module, 
            args.type, 
            args.server_id, 
            args.operation,
            args.page, 
            args.limit
        )
        safe_print(result)
    except ValueError as e:
        safe_print(f"参数错误: {e}")
        parser.print_help()
        exit(1)


if __name__ == "__main__":
    main()
