# -*- coding: utf-8 -*-
"""
Google Workspace CLI 配置测试脚本
运行此脚本验证 gws 是否配置正确
"""

import subprocess
import json
import os
import sys

# 设置输出编码
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')

def test_gws():
    """测试 gws 配置"""
    
    print("=" * 50)
    print("Google Workspace CLI 配置测试")
    print("=" * 50)
    print()
    
    # 获取 gws 路径
    gws_cmd = os.path.join(os.environ.get('APPDATA', ''), 'npm', 'gws.cmd')
    if not os.path.exists(gws_cmd):
        import shutil
        gws_cmd = shutil.which('gws') or 'gws'
    
    # 测试 1: 检查 gws 版本
    print("[1/4] 检查 gws CLI...")
    try:
        result = subprocess.run([gws_cmd, '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"  ✓ gws CLI: {result.stdout.strip().split(chr(10))[0]}")
        else:
            print(f"  ✗ gws CLI 未安装或无法运行")
            return False
    except FileNotFoundError:
        print(f"  ✗ 找不到 gws 命令")
        return False
    
    # 测试 2: 检查环境变量
    print()
    print("[2/4] 检查环境变量...")
    project_id = os.environ.get('GOOGLE_WORKSPACE_PROJECT_ID')
    if project_id:
        print(f"  ✓ GOOGLE_WORKSPACE_PROJECT_ID: {project_id}")
    else:
        print(f"  ✗ GOOGLE_WORKSPACE_PROJECT_ID 未设置")
        print(f"    请运行: $env:GOOGLE_WORKSPACE_PROJECT_ID = '你的项目ID'")
        return False
    
    # 测试 3: 检查认证状态
    print()
    print("[3/4] 检查认证状态...")
    result = subprocess.run([gws_cmd, 'auth', 'status'], capture_output=True, text=True, encoding='utf-8')
    try:
        status = json.loads(result.stdout)
        if status.get('token_valid'):
            print(f"  ✓ 认证有效")
            print(f"    用户: {status.get('user', 'N/A')}")
            print(f"    Scopes: {len(status.get('scopes', []))} 个")
        else:
            print(f"  ✗ 认证无效或已过期")
            print(f"    请运行: gws auth login")
            return False
    except json.JSONDecodeError:
        print(f"  ✗ 无法获取认证状态")
        print(f"    请运行: gws auth login")
        return False
    
    # 测试 4: 测试 API 调用
    print()
    print("[4/4] 测试 API 调用...")
    result = subprocess.run(
        [gws_cmd, 'drive', 'files', 'list'],
        capture_output=True, text=True, encoding='utf-8',
        env={**os.environ, 'GOOGLE_WORKSPACE_PROJECT_ID': project_id}
    )
    
    try:
        data = json.loads(result.stdout)
        if 'files' in data:
            print(f"  ✓ Drive API 正常")
            print(f"    找到 {len(data['files'])} 个文件")
        elif 'error' in data:
            print(f"  ✗ API 错误: {data['error'].get('message', 'Unknown error')}")
            return False
    except json.JSONDecodeError:
        print(f"  ✗ API 调用失败")
        print(f"    输出: {result.stdout[:200]}")
        return False
    
    # 全部通过
    print()
    print("=" * 50)
    print("✓ 所有测试通过！gws 已正确配置")
    print("=" * 50)
    print()
    print("可用命令示例:")
    print("  gws drive files list                    # 列出文件")
    print("  python gws_helper.py list-files         # 列出文件(友好格式)")
    print("  python gws_helper.py sheet-info <ID>    # 获取表格信息")
    print("  python gws_helper.py summarize-sheet <ID> <标题>  # 总结表格")
    
    return True


if __name__ == '__main__':
    success = test_gws()
    sys.exit(0 if success else 1)
