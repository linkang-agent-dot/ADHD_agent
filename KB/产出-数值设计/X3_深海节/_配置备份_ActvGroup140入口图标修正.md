# 深海节 ActvGroup 140 入口图标修正（✅ 已应用）

**状态**：✅ **已应用并提交+推送**（2026-06-23·**dev_festival** commit `6716183`·用户改口"就在dev_festival干不切feature"）。下方为留底，无需再重应用。

## 改动内容
- **表**：`tsv/ActvOnline__ActvGroup.tsv`
- **行**：ID=140（深海节入口组）
- **字段**：c4 = `MainEntranceIcon`（DK_入口图标）
- **before**：`DK_img_Activity_icon_Monopoly_deepsea`（错：大富翁图标）
- **after**：`DK_img_Activity_deepsea_hud_icon`（对：深海节潜艇入口图）

## 为什么
深海节整个入口组的图标被错配成大富翁(Monopoly)的图。潜艇图 `deepsea_hud_icon` 才是节日入口图标（对齐参考：尼罗组 c4=`Egypt_icon_7`、夏日组 c4=`VD_icon_2`，都是各自节日入口图）。用户确认潜艇图归 ActvGroup。

## 重应用命令（另一个 agent 推完后跑）
```bash
cd /c/x3/gdconfig && python -c "
import io
p='tsv/ActvOnline__ActvGroup.tsv'
with io.open(p,'r',encoding='utf-8',newline='') as f: lines=f.readlines()
for i,l in enumerate(lines):
    c=l.rstrip('\r\n').split('\t')
    if c[0]=='140':
        c[3]='DK_img_Activity_deepsea_hud_icon'
        nl='\r\n' if l.endswith('\r\n') else '\n'
        lines[i]='\t'.join(c)+nl; break
with io.open(p,'w',encoding='utf-8',newline='') as f: f.writelines(lines)
print('reapplied ActvGroup140 c4')
"
```

## 同批待办（深海图片尺寸 + 邀请函）
- 邀请函道具：ActvVisitPack 5606 c5=1137「婚礼邀请函」→ 应建深海专属邀请函（参尼罗1132）
- 活动 ActvImg 尺寸核对（见下方对比结论，与本备份同批改）
