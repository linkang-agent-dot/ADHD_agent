import sys, json

for line in sys.stdin:
    try:
        d = json.loads(line.strip())
        ch = d.get('channel', '?')
        subs = d.get('channel_follower_count', '?')
        title = d.get('title', '?')
        date = d.get('upload_date', '?')
        views = d.get('view_count', '?')
        vid = d.get('id', '')
        print(f"频道: {ch} | 订阅: {subs} | 播放: {views} | 发布: {date} | 标题: {title} | URL: https://youtu.be/{vid}")
    except:
        pass
