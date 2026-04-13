import sys, json, os
from datetime import datetime
sys.stdout.reconfigure(encoding='utf-8')

outbox = r"C:\ADHD_agent\openclaw\workspace\cursor_outbox"
results = [
    {
        "task_id": "task_20260331_221847_722903",
        "title": "X2合并：列出所有差异分支",
        "status": "done",
        "result": "差异分析完成：hotfix vs master_bugfix 共53个文件差异。分类：fo/config/21个、fo/i18n/17个、fo/json/10个、fo/s2c/3个、新增2个。根因：hotfix积累142个commit(活动配置/i18n/json等)未同步到master_bugfix，master_bugfix只有1个独有commit(军事发展科研改为随slg解锁,只改test1文件)。无冲突，已执行合并并创建merge commit，等待用户确认push。",
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "task_id": "task_20260331_215204_b150a5",
        "title": "X2 config合并：hotfix → master_bugfix",
        "status": "done",
        "result": "合并完成。策略：ort（无冲突）。52个文件变更，新增activity_flash_sale_raffle.tsv和activity_flash_sale_virtual.tsv。校验：无编码问题，无新增字段错误（monopoly_gacha_map第20行字段不一致为hotfix预存旧问题）。merge commit已创建(05c0c810c)，本地master_bugfix领先origin 158个commit。等待用户确认执行 git push origin master_bugfix。",
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    },
    {
        "task_id": "task_20260331_213427_d770a8",
        "title": "补充：buff对比数据是卡包相关的道具",
        "status": "done",
        "result": "已确认：buff_result.txt中的5条buff均为「来源装饰/来源装饰粉刷」类型(ID:12117002/12117010/12117011/12117020/121140935)，对应骑兵防御/全局部队生命/防御/对射手伤害/全局部队攻击等装饰加成buff，确为卡包(装饰道具)相关。result_19893734.md显示玩家19893734共82次卡包，总增益36736，最大单次3000，最小10，New终值52549-Old起始31004=净增21545。这是正常的卡包装饰buff累积数据。",
        "completed_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
]

for r in results:
    path = os.path.join(outbox, f"{r['task_id']}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(r, f, ensure_ascii=False, indent=2)
    print(f"写入: {r['task_id']}")
print("完成")
