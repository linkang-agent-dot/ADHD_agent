# 视频资源命名规范

参考 X2 项目 Unity 命名规范。

## 目录结构

```
Assets/x2/Video/Other/
├── Skill/              # 技能特效视频
├── Cutscene/           # 过场动画
├── UI/                 # UI 动画
├── Effect/             # 通用特效
├── Character/          # 角色相关
├── Activity/           # 活动相关
├── UnionBoss/          # 联盟 Boss
├── Adventure/          # 冒险/远征
├── Gacha/              # 抽卡/召唤
├── AgeSailing/         # 大航海
└── CreateCharacter/    # 创建角色
```

## 文件夹命名

| 规则 | 说明 |
|------|------|
| 大小写 | **PascalCase** |
| 内容 | 简洁描述该模块用途 |
| 禁止 | 空格、中文、全小写、连字符 |

## 文件命名

| 规则 | 说明 |
|------|------|
| 大小写 | **PascalCase** |
| 分隔符 | 可用下划线 `_` 分隔单词 |
| 禁止 | 空格、中文、全小写、连字符 |
| 注意 | 文件名不重复模块名前缀 |

## 示例

```
# ✅ 正确
Skill/FireBlast.mp4
Cutscene/Intro.mp4
Character/GoblinLaugh.webm

# ❌ 错误
Skill/SkillFireBlast.mp4    # 不要重复模块前缀
character/goblin laugh.mp4  # 不要小写和空格
```

## 完整保存路径

```
{project_path}/Assets/x2/Video/Other/{功能模块}/{文件名}.{扩展名}
```

扩展名：抠背景后 `.webm`（带透明通道），原始视频 `.mp4`。
