---
name: x3-config-export
description: >
  X3 配置修改 + 导表一条龙（2026-05-29 起导表读 tsv 缓存，直接改 tsv 不改 xlsx）。
  覆盖：定位字段 → 安全改 tsv → 提交 → 触发 Jenkins 导表 → 自动验证构建结果。
  触发词：改X3配置、屏蔽礼包/下架礼包、改timecycle、改X3数值、改tsv、导X3配置、导表(X3)、
  X3配置生效、夏日/尼罗礼包屏蔽、ActvOnline改、Pack改。
  不含 i18n 翻译扫描（那走 x3-translation-automatic）。
---

# X3 配置修改 + 导表一条龙

## 背景（必读）

2026-05-29 X3 导表迁移：**Jenkins「X3导配置」读仓库里提交的 tsv 缓存，不再从 xlsx 现导**。
- **所有非翻译配置改动 → 直接改 `C:\x3\gdconfig\tsv\` 下的 tsv**，不碰 xlsx。
- ⚠️ **绝不对已 tsv-直接改过的表跑 `xlsx_to_tsv.py` 重生成**——xlsx 还是旧的，重生成会把 tsv 改动覆盖回去（尼罗/夏日屏蔽就只在 tsv）。
- xlsx 下周删除，目前仅作备份。
- 详见 memory `reference_x3_tsv_export_migration.md`。

tsv 命名：`tsv/{data下相对目录}/{xlsx文件名}__{Sheet名}.tsv`（顶层 data/ 无子目录前缀）。

## 步骤0：主目录 or worktree（开工第一件事，必跑）

多窗口/多 agent 同机改 X3 配置会踩同一工作区。开工先判**当前分支是否被别人占着没收尾**：
> 注：全局 `PreToolUse` hook（`scripts/x3_config_isolation_gate.py`）会**强制兜底**这步——主仓脏时改主仓配置会被 exit 2 拦下。机制/绕过见 memory `workflow_x3_multiagent_worktree`。

```powershell
cd C:\x3\gdconfig ; git status -sb
```
读首行 + 文件行，按下表决策：

| 工作区状态 | 含义 | 怎么干 |
|---|---|---|
| 干净（无文件行）**且** 无 `[ahead N]` | 没人在改、本地没攒未推送提交 | **直接在主目录 `C:\x3\gdconfig` 干**，走下面 5 步 |
| 有未提交改动 **或** 显示 `[ahead N]` | 已有人/别的窗口在改且没收尾 | **开 worktree 隔离**，本功能改完不碰主目录 |

开 worktree 时（机制/坑/prompt 模板见 memory `workflow_x3_multiagent_worktree.md`）：
```powershell
git worktree add ../gdconfig-<短名> -b feature/<短名> dev_festival
```
**铁律**：之后 `tsv_edit.py` 每条带 `--repo C:\x3\gdconfig-<短名>`；commit/push 都 `cd` 进该 worktree；不碰主目录。漏了 `--repo` 会按默认值静默写回主目录，worktree 白开。
⚠️ `--repo` 是**全局参数，必须放在子命令之前**：`tsv_edit.py --repo C:\x3\gdconfig-<短名> show --file ...`；放在 show/set 之后会报 unrecognized arguments（2026-07-02 实测）。

## 工作流（5 步）

```powershell
# 0. 确认分支（X3 仓库分支敏感）
cd C:\x3\gdconfig ; git branch --show-current

# 1. 定位：打印目标行全字段+索引，确认要改的列号
python <skill>\scripts\tsv_edit.py show --file tsv/Pack__ChainPack.tsv --id 647

# 2. 安全改 tsv（断言旧值，命中数校验，保 LF，dry-run 先看）
python <skill>\scripts\tsv_edit.py set --file tsv/Pack__ChainPack.tsv --id 647 --col 2 --old 1 --new 0 --dry-run
python <skill>\scripts\tsv_edit.py set --file tsv/Pack__ChainPack.tsv --id 647 --col 2 --old 1 --new 0

# 3. 看 diff 确认只动了该动的（行级 diff = LF 没坏）
git diff

# 4. 提交（commit msg 用 X3NEW-/X3- 前缀）+ push
git add tsv/<改过的文件...> ; git commit -m "X3NEW-xxx ..." ; git push origin <branch>

# 5. 触发导表 + 自动验证（替代裸 jolt_export.py）
python <skill>\scripts\jolt_verify.py <branch>
```

`<skill>` = `C:\Users\linkang\.claude\skills\x3-config-export`

## 换皮档案（批量 / 多活动换皮时必建，换人不丢信息）

多活动 / 整轮换皮开工前，复制模板 `C:\ADHD_agent\KB\换皮档案\_模板_换皮档案.md` 到
`C:\ADHD_agent\KB\换皮档案\X3\{日期}.md`，按活动模块分节。三步铁律：

1. **开工先读** — 接手 / 新会话第一件事读本轮档案：进度到哪、已知坑、改了哪些 tsv、列号定位。
2. **随手回写** — 定位的列号、改动、状态、踩到 BUG（如 depend_checks 失败），立刻写回档案。
3. **收工更新** — 更新各模块进度 + BUG 解决情况。

**索引 + 改BUG 背景**：开工时在 `C:\ADHD_agent\KB\换皮档案\索引.md` 登记本轮（状态 🔄进行中），收工改 ✅已完结。中途单独派改 BUG 的 agent，**必须把本轮档案路径给它当背景**；BUG 修完回写本档案。

> 单条改动（如屏蔽单个礼包）不必建；多活动 / 整轮换皮才建。
> 发现通用规律 → 同时回写对应 memory（本档案只留本轮特有信息）。

## 工具

### tsv_edit.py — 安全改 tsv
- `show  --file <tsv> --id <行ID> [--max 32]` 打印字段+索引，定位列号
- `set   --file <tsv> --id <ID或逗号列表> --col <N> --old <旧> --new <新> [--dry-run]`
  改前断言每行该列==旧值，命中ID数必须等于传入数，否则不写盘
- `remove --file <tsv> --id <行ID> --cols 49,50 --ids 210917,210918,210919 [--dry-run]`
  从管道列表 `a|b|c` 里移除若干ID，每列实删数必须等于ID数
- `add    --file <tsv> --id <行ID> --cols 49,50 --ids 210917,210918,210919 --after 210921 [--dry-run]`
  往管道列表锚点ID后插入（`remove` 逆操作，解屏蔽/恢复用）；断言锚点存在、ID未重复
- 默认 repo `C:\x3\gdconfig`；--file 相对该目录；写盘保 LF（不被 Windows 翻 CRLF）

### jolt_verify.py — 触发导表 + 验证
- `python jolt_verify.py <branch>`：jolt 触发 → 轮询队列拿 build 号 → 轮询构建 → 报 SUCCESS/FAILURE + 分支 + 结尾行
- 退出码 0=SUCCESS / 2=FAILURE / 3=超时或已有构建在跑 / 1=异常
- 输出 `触发失败: 任务已在/正在执行` 时退回查 lastBuild（不算错误，已有构建会带上你的提交）
- 「已加入队列排队+`等待 build 号超时`」退 exit 3 ≠ 失败也≠必然会跑：**队列项不保证成活**（2026-07-02 实测：77286 排上队后始终没变成 build，疑被 dedup/取消）。确认法=直查 Jenkins API `job/X3%E5%AF%BC%E9%85%8D%E7%BD%AE/api/json?tree=builds[number,result,building,actions[parameters[name,value]]]` 看该分支有没有**晚于你 push 时间**的 build；没有就再触发一次。构建取的是**build 启动时刻**的分支 tip（多笔连推只需最后一轮覆盖验证）

## 列位置速查表（本会话已验证）

### 屏蔽 / 下架礼包（启用标志 1→0 + 从累充活动移除）
| 表 | 行 | 列 | 改动 |
|----|----|----|----|
| `Pack__ChainPack.tsv` | 阶梯礼包链ID（如647夏日/648尼罗） | field[2] | `1`→`0` |
| `Pack__Pack.tsv` | 各档礼包ID（如210917/918/919） | field[12] | `1`→`0` |
| `Pack__PackTypeInfo.tsv` | 代表礼包ID（首档，如210917） | field[1] | `1`→`0` |
| `ActvOnline__ActvOnline.tsv` | 累充活动ID（如100595夏日/100594尼罗） | field[49]=Pack列；若 field[50] 也含则一并 | 移除礼包ID |

- field[49] 是表头定义的 `Pack`(int[]) 列；field[50] 无表头名但同为礼包ID列表，**有的活动两列都含礼包、有的只 field[49]**——先 `show` 看哪几列含目标ID再 remove。
- ActvOnline 行名可能是历史复用名（如夏日累充行名叫"26情人节-累充"），**按 TimeCycle 值/含的礼包ID判断，不认名字**（见 memory `feedback_x3_timecycle_name_legacy`）。

### 解屏蔽 / 上架礼包（屏蔽的逆操作，对称反转）
1. ChainPack/Pack/PackTypeInfo 启用标志 `0→1`（`set` 同上，old/new 反过来）
2. ActvOnline 累充把礼包ID **加回原位**：`tsv_edit.py add ... --after <原前一个ID>`（先 `show` 看屏蔽前的邻居ID确定锚点）

### ⚠️ depend_checks 依赖规则（导表会强校验）
**ActvOnline 活动引用的 ChainPack 必须是启用状态**，否则导表报：
`Exception: data_name: ChainPack, depend_keys: {647} not existed`。
- 推论：屏蔽某 ChainPack 时，**任何引用它的 ActvOnline 活动行也必须一并删/停**，否则导表失败。
- 反之解屏蔽时只要把 ChainPack 启用回来，依赖即成立。
- 2026-05-29 踩坑：port 了引用 ChainPack 647 的 ActvOnline 106101，但 647 仍屏蔽 → 导表 FAILURE(#352)；解开 647 后 #353 SUCCESS。

### 其他表
列位置因表而异，**一律先 `tsv_edit.py show` 确认列号再 set**，别凭记忆。常用表参见 memory `reference_x3_score_activity` / `reference_config_library`。

### 新增整行（2026-06-12 世界杯竞猜实操沉淀）
- tsv_edit.py 无 append 子命令——写小脚本追加：**列数 pad 到表头行宽度**、LF 写盘、写前断言 ID 不存在；先全表预查新 ID 占用。
- **Pack.Price 列(field[7])填 PackPrice 档位 id**（105=$4.99/107=$9.99/111=$19.99/116=$49.99），不是美元数；field[6]=美元备注列；Content(field[13])=Reward 组 id。
- **免费包无先例**：全表无 GemPrice=0 行；UseGem 不在任何 tsv（导表推导字段）——免费领取型先配 GemPrice=1 钻占位，零价支持找程序确认。
- **pre-commit gate 实操**：只改 tsv 直接 commit 会被本地 gate 拦。流程=①工作区无关 unstaged 改动先 `git stash push -- <文件>`（否则拒 auto-sync）②`python scripts/sync_xlsx_tsv.py --from-tsv --files tsv/<改过的>.tsv` 补 xlsx ③tsv+xlsx 一起 commit，gate 逐格 identical 即过（一次过，不会 rc=24 二次触发）。
- TimeCycle 活动行模板：TriggerType=5(部署起算)+StartTime=00:00:00+DurationType=1+Duration=29d23h59m59s。
  - ★**TriggerType=5 仅限「触发式玩家活动」**(2026-06-16 世界杯累充/BP/签到踩坑)：导表 PostProcessData.py:1737-1751=若 TC.TriggerType==5,则活动**必须**是触发式玩家活动(item.TriggerType≠0 且在 PlayerActivityIds),否则报 `ActvOnline配置错误...TriggerType不能是0`。竞猜(进度礼包ActvType,GIFT_TRIGGER_ACTIVITY_TYPES={29})本是触发式所以能用 5;**普通节日活动(累充5/BP22/签到14/开箱15 等)克隆配 TC 要套复用源同类 TriggerType(1绝对/2开服相对/3注册相对),别套竞猜的5**。TimeCycle 列:idx4=TriggerType / idx5=StartTime(绝对要完整 `YYYY-MM-DD HH:MM:SS`) / idx7=Duration(`Nd23h59m59s`,签到 ActvType14 还要求 Duration≥签到天数)。
- ActvPack.FinalReward 别填 0/空（依赖校验风险），指向低价值真实 Reward 组兜底。

### 整套活动换皮 + 节日入口 ActvGroup + sync坑（2026-06-16 世界杯累充/BP/签到）
- **节日「单独入口」= `ActvOnline__ActvGroup` 表新建一行**（非普通活动列表/非酒馆）：col1=ID col3=TXT入口名(自动key `TXT_ActvGroup_MainEntranceName_{id}`) col4=DK入口图标(HUD主按钮) col5=排序(节日97/想靠前用98) col6-11=顶/底边框·退出钮·亮/暗页签·mask。**无专属chrome就克隆组101(通用cm套:DK_img_cm_bg_1/2 + cm_anniu_return + gift_btn_1/2 + Activity_bg)**。节日组ID排到138,新世界杯=139。
- **活动归入口=纯靠 ActvOnline.col38(=ActvGroup ID)**；ActvGroupSchedule 只给航海/入侵/KVK主子活动用,节日累充/BP/签到不需要。改 col38 即把活动从普通列表移进该入口。
- **复用源精确列**：[4]短ID [5]ActvType [7]**TimeCycle** [17]MailID [21]ActvIcon(HUD) [22]ActvImg(背景) [33]展示道具 [38]ActvGroup [49]RechargePointPackWhitelist(累充白名单)。
- **三模块联动表**：累充(type5)=ActvTask(TT=902,CID/P1=短ID,阈值)+Reward(同号RewardID,换item即换道具)+[49]白名单；签到(type14)=ActvLogin(col1=CID,col2=day,col7=实际奖励RewardID,col8=补签钻石);BP(type22)=ActvBattlePassScore.BattlePassScore([5]→等级组)+BattlePassScoreReward(组内每级「积分需求」列=改积分处,免/高/至尊三轨各指一个RewardID)。**BP走BattlePassScore不是ActvScore→天然不进酒馆**。
- ★**BP/积分活动「奖励组跨节日共享RewardID」坑**(2026-06-16世界杯BP实操):克隆某节日BP的等级组后,新组的免/高/至尊轨仍指向**原节日的同一批RewardID**(如世界杯组140克隆元旦组132,两组都指4028xxx)→**直接改这些Reward行=连原节日BP一起改!** 改奖励必须先**克隆出专属Reward块**(新RewardID,如+71000到空闲段4099xxx),按需换道具/其余照抄,再把新等级组的轨道指针(BattlePassScoreReward idx4/5/6)指到新块,原节日组不动。同理任何"克隆复用源后要改其引用的子表"都先确认该子表ID是否被复用源共享。
- ★**ActvBattlePassScore.xlsx 同步坑（openpyxl写崩）**：BattlePassScore sheet 是 16384列(XFD)病态宽表，且 Excel Table `table1` 的 ref 被写坏成 `6:42`(缺列字母)→ `sync_xlsx_tsv.py --from-tsv`(openpyxl full-load写路径) 报 `Value does not match pattern`(read_only能读、写不行)。**修=zip里改 table1 ref `6:42`→`A6:G42`**(table只是样式元数据不影响导表)，之后 openpyxl 正常 sync。脚本见换皮档案 `KB\换皮档案\X3\20260616_世界杯累充BP签到.md`。
- ★克隆超宽行(16384列)按**源行精确字段数**写,别 pad 到猜测宽;gate 比对会 trim 尾部空列(16384 vs 实际7列能匹配)。

### ★新增「列」（2026-06-15 ActvOnline 加 DKVideo 视频列血泪沉淀，比加行难得多）
给定长表加列三重坑，**每条都卡过导表**，按序解：
1. **DK 资源列靠「注释行(row5)含 DK_」判定 isRes（2026-06-16 实证纠正，比"列名DK_"更准）**：导表 `FieldDef.py:60` = `self.isRes = comment.find("DK_")>=0`——某列是否当 DisplayKey 资源字段，**看它的注释行(xlsx row5/字段名行的上一行)有没有 "DK_" 文本**(如 col48 MainEffect 注释="DK_界面特效")。若某列单元格值以 `DK_` 开头但该列注释漏写 DK_(isRes=False)→`RowObjTransform.py:66-68` 报 `key: <字段名去下划线> not startswith DK_` FAILURE(**报错文案误导**:真意=值是DK_资源但列没被声明为资源字段,不是"值不以DK_开头")。**修=给该列注释行补含 DK_ 的中文注释**(如"DK_视频")。⚠️注意区分:**注释行(row5)** 决定 isRes ≠ 字段名行(field name 仍建议 DK_ 前缀,codegen 去下划线→C#属性如 DKVideo 对上 cfg.DKVideo)。两者都要对。
2. **xlsx 模板列宽 ≠ tsv 列数 → gate 死结**：很多老表的 .xlsx **物理列宽远超 tsv 有效列**（如 ActvOnline.xlsx 有 101 列、tsv 仅 51）。append 新列(第52)→`sync --from-tsv` 反复把 xlsx 撑回 101 列→gate 在首个空列(col53)`tsv "" vs xlsx null` 永远 mismatch=1，删了又弹回，死循环；本地/Jenkins gate(rc=21) 都拒。**解法=别 append，占用「字段名行无名、row1(cs)/row2(类型)标记也空 的冗余尾列」**(proto 不读它)→全表列数不变→gate mismatch=0 直接过。先 `awk 'NR==1/2/99{print 末列}'` 确认该尾列在 cs/类型行确实无标记=proto 不生效，再覆盖。
3. **proto 字段要客户端补**：tsv 加了列、客户端代码引用 `cfg.NewField` ≠ proto 已生成该字段。proto 类(如 ActvOnline.cs)字段是**按列位置生成**的——加列后客户端须在 proto/schema 定义里把**对应位置**的字段补上并重跑生成器，否则 `cfg.NewField` 编译/运行读不到。这步配置侧做不了，必须客户端同步。
- ⚠️**判某尾列是不是"冗余可覆盖"**：看 row1(cs标记行)/row2(类型行)在该列**是否有标记**——空=proto 不读=可覆盖；有标记(如位50 RechargePointPackWhitelist 的 cs/int[])=有效字段**绝不能动**（位50 是累充白名单，覆盖=线上事故）。数据行某列有值≠该列有效（可能是历史脏数据/数组溢出残留）。
- **★配置表文本列机制（2026-06-13 实证）**：文本列（Pack.Name/Desc、ActvOnline.ActvName/ActvDesc 等"TXT_"注释列）**单元格内容不进客户端**——proto 运行时写死拼 `TXT_{表}_{字段}_{行ID}`（如 TXT_Pack_Name_891101，见 CfgProtoTextEx.cs）去 i18n bytes 查。所以：①单元格填中文原文（仅供翻译扫描器用）②**新行文本要显示=把自动 key 直接写进 Text 表**（tsv/i18n/Text__Text.tsv，27列，key|AI|key|cn|en|...10语种，行尾 pad 空到27列）③别把自定义 key 填进单元格（白填，运行时根本不读）。代码里 LocalizationMgr.Get 直引的自定义 key 才需要自定义命名。EN 客户端文本空白=该自动 key 的 en 列没值。

## ★openpyxl 重存 xlsx 污染公式/列结构 → mismatch 阻塞导表（2026-06-16 世界杯兑换+纪念卡踩坑）
- **现象**：`ExportTable.py` 启动即 `RuntimeError: XLSX/TSV are not synchronized; abort export`（它有 `verify_xlsx_tsv_before_export` 预检，mismatch≠0 直接 abort）；`sync_xlsx_tsv.py --check` 报 mismatch=N。**数据没错(tsv 都对)，是 xlsx 二进制被 openpyxl 重写后跟 tsv 对不齐**。
- **根因**：gate/`--check` 读的是 xlsx 单元格的**公式串**(非 data_only)。① **含公式的表**(如 MemorialCard.xlsx 有 1232 公式,Id列=`Group*1000+Level`)：正常 xlsx 存的是**静态值**(=tsv 值),被 openpyxl(sync_xlsx_tsv / 别的脚本)重存后**公式缓存丢失/变回公式串** → 公式串 ≠ tsv 值 → mismatch。② **无公式表**：openpyxl 重存改尾列空 cell 表示(`''` vs `None`/列宽)→结构 mismatch。
- **修**(不能再用 openpyxl sync 硬怼,越修越乱)：
  - 含公式表：让公式列变回**静态值**=tsv 值 → ⓐ Excel 打开→选公式列→复制→选择性粘贴「仅值」→存；或 ⓑ `scripts/tsv_to_xlsx.py`(XML 手术,不经 openpyxl,不碰其他公式)从 tsv 写值；或 ⓒ `sync_xlsx_tsv.py --from-tsv --files <该xlsx全部子页签tsv>`(写值,**子页签必须带齐**否则漏的页被清空)。
  - 列结构乱：从 HEAD `git checkout -- data/X.xlsx` 还原干净 xlsx,再用 tsv_to_xlsx 只塞改动行(别用 openpyxl 全表重存)。
- **预防**：改含公式的表(MemorialCard/带计算列的)优先 `tsv_to_xlsx.py`(XML手术) 或直接 Excel,**避免 openpyxl 全表重存**。多 agent 同一工作区时,别人重存过的 xlsx 也可能带进这种污染。

## ActvOnline 导表按 ActvType 的硬校验（2026-06-16 大富翁踩坑，校验代码在 `Tools/table_exporter/PostProcessData.py:deal_actv_online_data` + `def/actvonline_def.py`）
新建/换皮活动导表报 `ActvOnline配置错误：活动ID:X ...` 多半是这几条按 ActvType 的硬规则没满足：
- **MailID 必须=101109**（部分 ActvType，如 28 航海/大富翁）：`actvonline_def.py:248` GENERAL_MAIL_ID=101109，到期补领邮件硬绑。报 `邮件ID必须为101109`→ 改 col17(idx17 MailID)=101109。
- **TimeController(idx7) 不能为 0**（PostProcessData.py:~1765）：除非 ActvType 在 `SKIP_TIMECYCLE_CHECK_ACTIVITY_TYPE`(集合在 ~1643) 或 id 在 kvkSeason/ScheduleActvIDS。报 `时间控制器ID:0 不能是0`→ 要么绑个 TC，要么把该 ActvType 加进 SKIP 集（如大富翁 ActvType_VOYAGE=28 成就礼包版靠成就触发无需 TC，2026-06-16 加入）。
  - ⚠️**ActvType=64 世界杯竞猜（76个）**：故意 `TimeCycle=0`（走 iGame/外部控时），但 dev_festival 的 SKIP 集**没含 64** → 本地导表和 Jenkins 都报 `活动ID:102911 时间控制器ID:0 不能是0`（commit 4291166 作者只验了 FK/depend，漏了这条 PostProcess 校验）。修法=给 SKIP 集加 `ACTV_TYPE_WORLD_CUP_GUESS = 64`（2026-06-18 实测，应正式补进导表工具）。
- **TC.TriggerType=5 → 活动必须是触发式玩家活动**(item.TriggerType≠0)；非触发式节日活动(累充/BP/签到/开箱)别套竞猜的 TriggerType=5（见上「TriggerType=5 仅限触发式玩家活动」）。
- 校验是**纯本地可复现**：`cd Tools/table_exporter && python ExportTable.py`（bat 有 pause 卡非交互，直接跑 py），全跑通=尾部 `protoc 成功 + generate localization bytes success + MD5`，零 Exception。改配置/排导表错先本地跑这个，比等 Jenkins 快。

## ★本地导表 → 导入本地服（不走 jolt/Jenkins，2026-06-18 实测）
- **纯校验/转换**：`python ExportTable.py`（上条）→ 产出 `gdconfig/temp_dev/ProtoGen/*.bytes`。**仅 Python，不要 .NET**。
- **连带生成客户端 C# proto**：`python GenCSharp.py`（=`export_table_and_cp_to_client.bat`）调 `protogen-csharp/win/TableProtoGen.exe`，其 `runtimeconfig.json` 写死 **net6.0**。机器只有 .NET 8 会报「找不到 6.0 运行时」→ `winget install Microsoft.DotNet.SDK.6`（含 6.0.x 运行时）。另需 `table_exporter/local.json`（从 `local.json.temp` 复制改 `client_path`）。
- **导入运行中的本地服**（temp_dev 本地服不读它，本地服读 `client/Assets/Res/Config/ProtoGen`，由 `server/Resource/.../ProtoGen` 软链）：① `cp -r temp_dev/ProtoGen/* C:/x3-project/client/Assets/Res/Config/ProtoGen/` ② `python ~/x3_gm.py "!gm ReloadGameServer"`（热更，不掉玩家）。验证日志 `ReloadTable finished, N tables reloaded` + `[Notify]reload[N] success` 且无 `InvalidProtocolBufferException`（有=schema 变了须停服重编 Hotfix）。详见 `reference_x3_tsv_export_migration` + `workflow_x3_local_server_gm_telnet`。

## i18n 翻译例外

翻译文本（`tsv/i18n/Text__Text.tsv`）涉及扫描/翻译工具链，仍可走 xlsx：改 `data/i18n/Text.xlsx` → `python C:\x3\gdconfig\scripts\xlsx_to_tsv.py --files data/i18n/Text.xlsx` 重生成 → 提交 tsv。或直接改 tsv 的语言列（状态列改 `AI`）。详见 `reference_x3_i18n_workflow`。

## 安全红线
1. **不碰 xlsx**（非翻译场景）；**不对已 tsv-改过的表重生成 tsv**。
2. 改前 `git branch --show-current` 确认分支。
3. `set` 用断言、`remove` 用计数校验；先 `--dry-run`。
4. push 可能被拒（多人并行）→ `git fetch` 比对，若与远端 blob 逐字节相同直接 `git reset --hard origin/<branch>` 丢重复提交。
5. 改完必须 `jolt_verify.py` 确认 SUCCESS，别只触发不看结果。
