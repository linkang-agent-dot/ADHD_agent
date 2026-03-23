import asyncio
import sys
from mcp_server_weibo.weibo import WeiboCrawler

async def main():
    c = WeiboCrawler()
    result = await c.get_trendings(3)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
