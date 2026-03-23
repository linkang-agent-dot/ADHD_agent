"""
微博热搜工具
"""
import asyncio
import sys
from mcp_server_weibo.weibo import WeiboCrawler

async def get_trendings(limit=5):
    c = WeiboCrawler()
    r = await c.get_trendings(limit)
    return r

async def search_users(keyword, limit=5):
    c = WeiboCrawler()
    r = await c.search_users(keyword, limit)
    return r

async def get_profile(uid):
    c = WeiboCrawler()
    r = await c.get_profile(uid)
    return r

async def search_content(keyword, limit=5):
    c = WeiboCrawler()
    r = await c.search_content(keyword, limit)
    return r

if __name__ == "__main__":
    import json
    
    if len(sys.argv) < 2:
        print("用法: python weibo_tools.py <command> [args]")
        print("命令: trendings [数量], search <关键词> [数量], profile <uid>, content <关键词> [数量]")
        sys.exit(1)
    
    cmd = sys.argv[1]
    
    if cmd == "trendings":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        r = asyncio.run(get_trendings(limit))
        for i, item in enumerate(r, 1):
            print(f"{i}. {item.description} (热度: {item.trending})")
    elif cmd == "search":
        keyword = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        r = asyncio.run(search_users(keyword, limit))
        for u in r:
            print(f"- {u.screen_name}: {u.description}")
    elif cmd == "profile":
        uid = int(sys.argv[2])
        r = asyncio.run(get_profile(uid))
        print(f"昵称: {r.screen_name}")
        print(f"简介: {r.description}")
        print(f"粉丝: {r.followers_count}")
        print(f"关注: {r.follow_count}")
    elif cmd == "content":
        keyword = sys.argv[2]
        limit = int(sys.argv[3]) if len(sys.argv) > 3 else 5
        r = asyncio.run(search_content(keyword, limit))
        for i, item in enumerate(r, 1):
            print(f"{i}. {item.text[:100]}...")
    else:
        print(f"未知命令: {cmd}")
