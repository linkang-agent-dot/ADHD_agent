# 配置表上传工具

## 功能描述
根据用户提供的截图或表名，自动识别配置表编号并批量上传到 gdconfig 仓库。

## 触发条件
当用户提到以下关键词时使用：
- "上传配置表"、"上传表"、"upload config"、"传表"
- "下载配置表"、"拉表"、"拉配置"
- 用户发送包含 `fo\config\*.tsv` 文件列表的截图

## Token 优化指南（重要！）

为减少 token 消耗，执行时遵循以下原则：

1. **git 操作静默化**：使用 `-q` 参数抑制输出
2. **不读取下载工具完整输出**：只读取最后 5 行确认结果
3. **多分支批量操作**：尽量合并命令，减少轮次

## 使用流程

### 1. 识别配置表
从用户提供的截图或文字中识别表名/编号。用户可能直接给编号（如 1111）或表名（如 item）。

### 2. 常用配置表编号速查

| 编号 | 表名 | 说明 |
|------|------|------|
| 1011 | i18n | 客户端本地化 |
| 1111 | item | 道具表 |
| 1118 | building | 建筑表 |
| 1120 | drop | 掉落表 |
| 1211 | buff | buff表 |
| 1387 | city_effect | 城内特效 |
| 1392 | city_effect_extent | 城内范围特效 |
| 1920 | hero_data | 英雄表 |
| 2011 | iap_config | 内购配置总表 |
| 2111 | activity_calendar | 活动日历配置表 |
| 2112 | activity_config | 活动配置表 |
| 2118 | activity_rank_rewards | 活动排名奖励 |
| 2119 | activity_ui_template | 活动UI模板 |
| 2120 | activity_ui_module | 活动UI模块 |
| 2122 | activity_rank_rule | 活动排名模板 |
| 2136 | activity_cycle_period | 活动周期配置 |
| 2138 | activity_proto_module | 活动类型和客户端协议模块 |
| 2141 | activity_without_gacha_pool | 活动非放回抽奖池 |
| 2142 | activity_without_gacha_reward | 活动非放回抽奖奖励 |
| 2160 | activity_metro_grade | 挖矿评级 |
| 2169 | activity_hud_entry_style | 活动HUD入口样式 |

### 3. 切换分支（静默模式）

使用 `-q` 参数减少输出：

```powershell
git -C C:\gdconfig checkout -q <分支名>; git -C C:\gdconfig pull -q
```

**常用分支：** `hotfix`、`bugfix`、`dev`、`qa`

### 4. 执行下载命令

```powershell
echo "1`n<编号列表>`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

**示例：**
```powershell
echo "1`n1011 1111`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

### 5. 验证结果（只读最后几行！）

**关键优化**：命令输出会很长（1500+行），但只需读取输出文件的**最后 5 行**来确认结果：

```
Read 工具使用 offset: -5 参数
```

查找关键信息：`成功: X, 失败: 0` 即可确认下载成功。

### 6. 多分支操作模板

如果用户要传多个分支（如 bugfix + hotfix），按顺序执行：

```powershell
# 分支1
git -C C:\gdconfig checkout -q bugfix; git -C C:\gdconfig pull -q
echo "1`n<编号>`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"

# 分支2  
git -C C:\gdconfig checkout -q hotfix; git -C C:\gdconfig pull -q
echo "1`n<编号>`nn" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

### 7. 回复模板（简洁）

```
✅ <分支名>: <编号列表> 下载成功，请手动检查后提交。
```

多分支示例：
```
✅ bugfix: 1011 1111 下载成功
✅ hotfix: 1011 1111 下载成功
请手动检查后提交。
```

## 完整编号查询
```powershell
echo "1`n9999" | & "C:\gdconfig\scripts\GSheetDownloader.exe"
```

## 注意事项
1. 工具路径：`C:\gdconfig\scripts\GSheetDownloader.exe`
2. 表编号用空格分隔
3. PowerShell 用 `;` 连接命令（不是 `&&`）
