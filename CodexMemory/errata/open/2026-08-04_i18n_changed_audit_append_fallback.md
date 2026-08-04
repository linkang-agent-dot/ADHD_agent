# i18n changed 审计对纯追加改动回退为全表噪音

- 日期：2026-08-04
- 场景：X3 马戏节新增 101831，向 `Text__Text.tsv` 纯追加 3 个完整复刻文本键。
- 现象：执行 `i18n_leak_audit.py --changed` 时，因为新旧 TSV 行数不同，工具无法按行定位 changed scope，回退为全表审计，报出 360 条历史问题（EN_LEAK/CJK_LEAK/EMPTY），exit 1。
- 根因：`--changed` 的差异定位假设新旧文件行数一致，不适用于 append-only 新增行。
- 绕行：对新增 key 做精确审计：逐键确认唯一性、16 语言非空，并核对除 key 外全部字段与复刻源逐字节一致；全表回退结果不作为本次新增行失败证据。
- 后续规则：X3 i18n 纯追加行验证，先做 exact-key audit；若再跑 `--changed`，必须区分“目标行问题”和“因行数变化触发的全表历史噪音”。
