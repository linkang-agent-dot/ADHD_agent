# iap_template：以 QA 为准同步到 master 说明

**文档表**：`2013_x2_iap_template`  

**链接**：https://docs.google.com/spreadsheets/d/1OiKK3mwKtw9seCjpVr29d9N2aFDkIbyOFInvKqMHF_E/edit

| 页签 | gid | 说明 |
|------|-----|------|
| `iap_template_x2（qa）` | 1938706798 | **为准（源）** |
| `iap_template_x2master` | 1378862323 | **待对齐（目标）** |

- QA 数据行数：**6686**；master 数据行数：**6644**
- 仅 QA 有、需整行复制到 master：**42** 行
- 两边都有但单元格不同：**14** 处

---

## 一、仅 QA 有（整行从 `iap_template_x2（qa）` 复制到 `iap_template_x2master`）

在 QA 页签中按 `Id` 搜索，选中**整行**（含所有列），复制后粘贴到 master 表数据区；勿覆盖前 7 行 meta。

| # | Id | PkgDesc（QA） |
|---|-----|---------------|
| 1 | 2013450003 | LC_IAP_packet_desc |
| 2 | 2013450004 | LC_IAP_packet_desc |
| 3 | 2013450005 | LC_IAP_packet_desc |
| 4 | 2013450006 | LC_IAP_packet_desc |
| 5 | 2013450007 | LC_IAP_packet_desc |
| 6 | 2013450008 | LC_IAP_packet_desc |
| 7 | 2013450009 | LC_IAP_packet_desc |
| 8 | 2013450010 |  |
| 9 | 2013450011 |  |
| 10 | 2013450012 |  |
| 11 | 2013450013 |  |
| 12 | 2013450014 |  |
| 13 | 2013450015 |  |
| 14 | 2013450016 |  |
| 15 | 2013450017 |  |
| 16 | 2013450018 |  |
| 17 | 2013450019 |  |
| 18 | 2013450020 |  |
| 19 | 2013450021 |  |
| 20 | 2013450022 |  |
| 21 | 2013450023 | LC_IAP_packet_desc |
| 22 | 2013500192 |  |
| 23 | 2013500193 |  |
| 24 | 2013500194 |  |
| 25 | 2013500195 |  |
| 26 | 2013500196 |  |
| 27 | 2013500197 |  |
| 28 | 2013500198 |  |
| 29 | 2013500202 |  |
| 30 | 2013500203 | LC_IAP_packet_desc |
| 31 | 2013500204 | LC_IAP_packet_desc |
| 32 | 2013500205 | LC_IAP_packet_desc |
| 33 | 2013500206 | LC_IAP_packet_desc |
| 34 | 2013500207 | LC_IAP_packet_desc |
| 35 | 2013500391 |  |
| 36 | 2013500392 |  |
| 37 | 2013500393 |  |
| 38 | 2013500394 |  |
| 39 | 2013920001 |  |
| 40 | 2013920002 |  |
| 41 | 2013920003 |  |
| 42 | 2013920004 | LC_IAP_fes_time_card_price_2 |

---

## 二、两边都有：把 master 改成与 QA 一致

| Id | PkgDesc | 列（fwcli） | master 当前（应改掉） | QA（为准，覆盖到 master） |
|----|---------|-------------|----------------------|---------------------------|
| 2013692091 |  | TempDesc | 缺粉尘触发礼包-付费1 | 解锁英雄天赋功能礼包-付费1 |
| 2013699096 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":3},"setting":{"serial_number":100, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":3},"setting":{"serial_number":100, "ishighlight": false}}] |
| 2013699097 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":5},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":2},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":5},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":2},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013699098 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":7},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":2},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":5},"setting":{"serial_number":98, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":7},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":2},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":5},"setting":{"serial_number":98, "ishighlight": false}}] |
| 2013699099 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":15},"setting":{"serial_number":100, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":15},"setting":{"serial_number":100, "ishighlight": false}}] |
| 2013699100 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":20},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":5},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":20},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":5},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013699101 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":25},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":5},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":5},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":25},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":5},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":5},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013699102 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":35},"setting":{"serial_number":100, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":35},"setting":{"serial_number":100, "ishighlight": false}}] |
| 2013699103 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":40},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":40},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":40},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":40},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013699104 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":50},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":40},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":40},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":50},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":40},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":40},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013699105 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":55},"setting":{"serial_number":100, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":55},"setting":{"serial_number":100, "ishighlight": false}}] |
| 2013699106 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":60},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":60},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":60},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":60},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013699107 | LC_IAP_packet_desc | PvpItems | [{"asset":{"typ":"item","id":11116214,"val":70},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":60},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":60},"setting":{"serial_number":99, "ishighlight": false}}] | [{"asset":{"typ":"item","id":11116243,"val":70},"setting":{"serial_number":100, "ishighlight": false}},{"asset":{"typ":"item","id":11111081,"val":60},"setting":{"serial_number":99, "ishighlight": false}},{"asset":{"typ":"item","id":11111082,"val":60},"setting":{"serial_number":99, "ishighlight": false}}] |
| 2013910013 |  | OtherItems | [{"asset":{"typ":"xp","id":11161002,"val":1250},"setting":{"serial_number":0, "ishighlight": false}},{"asset":{"typ":"item","id":11119472,"val":1},"setting":{"serial_number":999, "ishighlight": true}},{"asset":{"typ":"item","id":11119473,"val":10},"setting":{"serial_number":200, "ishighlight": true}},{"asset":{"typ":"item","id":11119453,"val":40},"setting":{"serial_number":100, "ishighlight": true}},{"asset":{"typ":"item","id":11118663,"val":2},"setting":{"serial_number":10, "ishighlight": false… | [{"asset":{"typ":"xp","id":11161002,"val":1250},"setting":{"serial_number":0, "ishighlight": false}},{"asset":{"typ":"item","id":11119472,"val":1},"setting":{"serial_number":999, "ishighlight": true}},{"asset":{"typ":"item","id":11114016,"val":2},"setting":{"serial_number":900, "ishighlight": true}},{"asset":{"typ":"item","id":11119473,"val":10},"setting":{"serial_number":200, "ishighlight": true}},{"asset":{"typ":"item","id":11119453,"val":40},"setting":{"serial_number":100, "ishighlight": true… |

---

## 三、操作检查清单

1. 完成「一」中所有行的整行复制。
2. 对「二」中每一行，在 master 打开对应 `Id`，将所列列改为 QA 单元格内容（或直接复制 QA 该格）。
3. 保存后如需落 git，再按你们 `fwcli`/导表流程导出 TSV。
