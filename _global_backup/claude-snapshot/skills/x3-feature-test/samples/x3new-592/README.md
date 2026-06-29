# X3NEW-592 验证报告 · 样例（限时招募池 174天+ 断档修复）

`scripts/make_html_report.py` 的实战样例 + 本次验证产物归档。

## 文件
- `spec.json` —— 报告内容（验收横幅 / 5 个服龄实测表 / 配置生效 / 已知项）。**新任务照抄改字段即可。**
- `recruit_175d_lingshuang.png` —— 核心证据截图：服龄 175 天，酒館招募，凌霜·異國功夫·异国美酒(7002)。
- `popup_state_175d.png` —— 测试过程截图：GM 跳服龄触发的登录弹窗（关弹窗坑位）。
- `report_X3NEW-592.html` —— 生成产物（截图已 base64 内联，单文件可直接浏览器打开 / 发 Artifact）。

## 重新生成
```
python ../../scripts/make_html_report.py spec.json report_X3NEW-592.html
```
（spec 里截图用相对路径，脚本按 spec 所在目录解析。）

## 结论
🟢 通过：5 个服龄点（175/180/210/250/300）代码证据 + 175 天干净截图，证明 7002 限时池 173 天后不断档、每 84 天永久循环。完整方法见 `references/recipes.md` 配方 2/3。
