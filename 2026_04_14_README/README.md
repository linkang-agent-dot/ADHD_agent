# X3 线上问题排查工具 - 使用说明

## 这是什么

收到玩家反馈或线上问题后，自动查 X3 master 配置表（161个xlsx），判断是配置问题还是代码 bug，结论发到钉钉客服群。

## 你需要改什么

只改一个地方：

打开 `scripts/config_lookup.py`，第 14 行：

```python
CONFIG_DIR = Path("/Users/zouhanling/Desktop/X3/design/data_master")
```

改成你自己电脑上 SVN checkout 的 X3 **data_master** 路径，比如：

```python
CONFIG_DIR = Path("/Users/你的用户名/Desktop/X3/design/data_master")
```

其他都不用改。webhook 机器人是共用的，指向「X3-客服问题反馈专用」群。

## 前置条件

1. 本地装了 Python 3
2. 安装 openpyxl：`pip install openpyxl`
3. SVN 上的 X3 配置表已 checkout 到本地（确保 data_master 是最新的）

## 怎么用

把问题发给 Nomi（私聊），说"帮查一下：xxx问题"，Nomi 会：

1. 分析问题涉及哪个系统（活动/礼包/英雄/...）
2. 自动读取对应的 master 配置表验证
3. 输出排查结论到钉钉客服群
4. 等策划确认后给出最终反馈

## 文件说明

```
x3-issue-checker/
├── SKILL.md              ← Nomi 的流程指引（不用管）
├── README.md             ← 你正在看的这个
├── scripts/
│   ├── config_lookup.py  ← 配置表查询工具（改路径在这里）
│   └── send_to_qa.py     ← 发消息到客服群（不用改）
└── references/
    └── config-index.md   ← 161个配置文件的完整索引
```
