# iap 两页签差异（供人工核对）

**表**：`1N5T3fVLSxiypdGOZYR5CSlVYWpseAi5hBsX7XtCZOsY`
**A**（gid `1032886231`）：`iap_config_x2master`
**B**（gid `1202421075`）：`iap_config_x2master（3.31）`
**范围**：`A1:U5000`（前 7 行为 meta，之后为数据）

- A 数据行：**3415**；B 数据行：**3375**
- 仅 A 有（B 无此 Id+PkgDesc）：**10**
- 仅 B 有（A 无此 Id+PkgDesc）：**0**
- 同键同重复次数下单元格不同：**765** 处

---

## 一、仅 A 有

| Id | PkgDesc |
|------|---------|
| 2011910065 | 掉落转付费礼包 |
| 2011920001 | 自选周卡-29.99 |
| 2011920002 | 自选周卡-19.99 |
| 2011920003 | 自选周卡-9.99 |
| 2011920004 | 自选周卡-49.99 |
| 2011920005 | 节日每日礼包-1 |
| 2011920006 | 节日每日礼包-2 |
| 2011920007 | 节日每日礼包-3 |
| 2011920008 | 节日每日礼包-4 |
| 2011920009 | 节日每日礼包-5 |

---

## 二、仅 B 有

| Id | PkgDesc |
|------|---------|

---

## 三、两边都有但单元格不同

| Id | PkgDesc | 列 | A：`iap_config_x2master` | B：`iap_config_x2master（3.31）` |
|----|---------|-----|----------------|----------------|
| 2011100001 | 2020万圣节礼包 | PirceDisplay | FALSE | False |
| 2011100002 | 2020感恩节礼包 | PirceDisplay | FALSE | False |
| 2011100003 | 2020圣诞节礼包 | PirceDisplay | FALSE | False |
| 2011100004 | 2021情人节礼包 | PirceDisplay | FALSE | False |
| 2011100005 | 2021情人节礼包 36服 | PirceDisplay | FALSE | False |
| 2011100008 | 2021万圣节礼包 | PirceDisplay | FALSE | False |
| 2011100009 | 2021感恩节礼包 | PirceDisplay | FALSE | False |
| 2011100010 | 2021圣诞节礼包 | PirceDisplay | FALSE | False |
| 2011100011 | 2022情人节礼包 | PirceDisplay | FALSE | False |
| 2011100012 | 2022情人节铭牌礼包 | PirceDisplay | FALSE | False |
| 2011100013 | 2022复活节礼包 | PirceDisplay | FALSE | False |
| 2011100014 | 2022复活节铭牌礼包 | PirceDisplay | FALSE | False |
| 2011100015 | 2022幼猴节礼包 | PirceDisplay | TRUE | True |
| 2011100016 | 2022幼猴节铭牌礼包 | PirceDisplay | FALSE | False |
| 2011100017 | 2022沙滩节礼包 | PirceDisplay | FALSE | False |
| 2011100018 | 2022科技节礼包 | PirceDisplay | TRUE | True |
| 2011100019 | 2022马戏节礼包 | PirceDisplay | FALSE | False |
| 2011100020 | 2022万圣节礼包 | PirceDisplay | TRUE | True |
| 2011100021 | 2022感恩节礼包 | PirceDisplay | TRUE | True |
| 2011100022 | 2022感恩节bp礼包 | PirceDisplay | FALSE | False |
| 2011100023 | 2022圣诞节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100024 | 2022圣诞节bp礼包 | PirceDisplay | FALSE | False |
| 2011100025 | 2023春节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100026 | 2023春节bp礼包 | PirceDisplay | FALSE | False |
| 2011100027 | 2023情人节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100028 | 2023情人节bp礼包 | PirceDisplay | FALSE | False |
| 2011100029 | 2023春节锦鲤礼包-第1天 | PirceDisplay | FALSE | False |
| 2011100030 | 2023春节锦鲤礼包-第2天 | PirceDisplay | FALSE | False |
| 2011100031 | 2023春节锦鲤礼包-第3天 | PirceDisplay | FALSE | False |
| 2011100032 | 2023春节锦鲤礼包-第4天 | PirceDisplay | FALSE | False |
| 2011100033 | 2023春节锦鲤礼包-第5天 | PirceDisplay | FALSE | False |
| 2011100034 | 2023科技节bp礼包 | PirceDisplay | FALSE | False |
| 2011100035 | 2023科技节礼包 | PirceDisplay | TRUE | True |
| 2011100036 | 2023复活节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100037 | 2023复活节bp礼包 | PirceDisplay | FALSE | False |
| 2011100038 | 2023拓荒节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100039 | 2023拓荒节bp礼包 | PirceDisplay | FALSE | False |
| 2011100040 | 2023端午节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100041 | 2023端午节bp礼包 | PirceDisplay | FALSE | False |
| 2011100042 | 2023付费飞服礼包 | PirceDisplay | TRUE | True |
| 2011100043 | 2023沙滩节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100044 | 2023沙滩节bp礼包 | PirceDisplay | TRUE | True |
| 2011100045 | 2023付费飞服礼包-预告期活动 | PirceDisplay | TRUE | True |
| 2011100046 | 2023周年庆皮肤gacha礼包 | PirceDisplay | TRUE | True |
| 2011100049 | 2023周年庆锦鲤礼包-第1天 | PirceDisplay | FALSE | False |
| 2011100050 | 2023周年庆锦鲤礼包-第2天 | PirceDisplay | FALSE | False |
| 2011100051 | 2023周年庆锦鲤礼包-第3天 | PirceDisplay | FALSE | False |
| 2011100052 | 2023周年庆bp礼包 | PirceDisplay | TRUE | True |
| 2011100053 | 赛季金头一代 | PirceDisplay | FALSE | False |
| 2011100054 | 赛季金头二代 | PirceDisplay | FALSE | False |
| 2011100055 | 赛季金头三代 | PirceDisplay | FALSE | False |
| 2011100056 | 2023付费飞服礼包-预告期活动-2 | PirceDisplay | TRUE | True |
| 2011100057 | 2023登月节bp礼包 | PirceDisplay | TRUE | True |
| 2011100058 | 2023周年庆皮肤gacha礼包 | PirceDisplay | TRUE | True |
| 2011100059 | 2023万圣节bp礼包 | PirceDisplay | TRUE | True |
| 2011100060 | 2023万圣节皮肤gacha礼包 | PirceDisplay | TRUE | True |
| 2011100061 | 2023万圣节锦鲤礼包-第1天 | PirceDisplay | FALSE | False |
| 2011100062 | 2023万圣节锦鲤礼包-第2天 | PirceDisplay | FALSE | False |
| 2011100063 | 2023万圣节锦鲤礼包-第3天 | PirceDisplay | FALSE | False |
| 2011100064 | 2023感恩节黑五小额礼包-4.99 | PirceDisplay | FALSE | False |
| 2011100065 | 2023感恩节皮肤gacha礼包 | PirceDisplay | TRUE | True |
| 2011100066 | 2023感恩节大超R大额礼包-29.99 | PirceDisplay | TRUE | True |
| 2011100067 | 2023感恩节大超R大额礼包-49.99 | PirceDisplay | TRUE | True |
| 2011100068 | 2023感恩节大超R大额礼包-99.99 | PirceDisplay | TRUE | True |
| 2011100069 | 2023感恩节bp礼包 | PirceDisplay | TRUE | True |
| 2011100070 | 2023感恩节黑五小额礼包-14.99 | PirceDisplay | FALSE | False |
| 2011100071 | 2023感恩节黑五小额礼包-24.99 | PirceDisplay | FALSE | False |
| 2011100072 | 合服礼包 | PirceDisplay | TRUE | True |
| 2011100073 | 2023圣诞节bp礼包 | PirceDisplay | FALSE | False |
| 2011100074 | 2023圣诞节买三赠一 | PirceDisplay | TRUE | True |
| 2011100075 | 2023圣诞节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100076 | 装饰兑换券礼包 | PirceDisplay | TRUE | True |
| 2011100077 | 赛季金头四代 | PirceDisplay | FALSE | False |
| 2011100078 | 2024春节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100079 | 2024春节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 2011100080 | 2024春节bp礼包 | PirceDisplay | FALSE | False |
| 2011100081 | 2024情人节bp礼包 | PirceDisplay | FALSE | False |
| 2011100082 | 2024情人节-bingo活动宝箱 | PirceDisplay | TRUE | True |
| 2011100083 | 2024情人节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100084 | 情人节装饰兑换券礼包 | PirceDisplay | TRUE | True |
| 2011100085 | 2024复活节bp礼包 | PirceDisplay | FALSE | False |
| 2011100086 | 2024复活节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100087 | 2024复活节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 2011100088 | 2024科技节买三赠一 | PirceDisplay | TRUE | True |
| 2011100089 | 2024科技节bp礼包 | PirceDisplay | FALSE | False |
| 2011100090 | 2024科技节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100091 | 2024拓荒节-bingo活动宝箱 | PirceDisplay | TRUE | True |
| 2011100092 | 2024拓荒节bp礼包 | PirceDisplay | FALSE | False |
| 2011100093 | 2024拓荒节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100094 | 2024拓荒节行军表情 | PirceDisplay | FALSE | False |
| 2011100095 | 2024端午节gacha礼包 | PirceDisplay | TRUE | True |
| 2011100096 | 2024端午节bp礼包 | PirceDisplay | FALSE | False |
| 2011100097 | 2024端午节行军表情 | PirceDisplay | FALSE | False |
| 2011100098 | 2024端午节机甲礼包 | PirceDisplay | TRUE | True |
| 2011100099 | 2024沙滩节bp礼包 | PirceDisplay | FALSE | False |
| 2011100100 | 2024沙滩节折扣礼包-英雄-4.99 | PirceDisplay | TRUE | True |
| 2011100101 | 2024沙滩节折扣礼包-英雄-9.99 | PirceDisplay | TRUE | True |
| 2011100102 | 2024沙滩节折扣礼包-英雄-19.99 | PirceDisplay | TRUE | True |
| 2011100103 | 2024沙滩节折扣礼包-收藏品-4.99 | PirceDisplay | TRUE | True |
| 2011100104 | 2024沙滩节折扣礼包-收藏品-9.99 | PirceDisplay | TRUE | True |
| 2011100105 | 2024沙滩节折扣礼包-收藏品-19.99 | PirceDisplay | TRUE | True |
| 2011100106 | 2024沙滩节折扣礼包-机甲-4.99 | PirceDisplay | TRUE | True |
| 2011100107 | 2024沙滩节折扣礼包-机甲-9.99 | PirceDisplay | TRUE | True |
| 2011100108 | 2024沙滩节折扣礼包-机甲-19.99 | PirceDisplay | TRUE | True |
| 2011100109 | 2024沙滩节折扣礼包-战装-4.99 | PirceDisplay | TRUE | True |
| 2011100110 | 2024沙滩节折扣礼包-战装-9.99 | PirceDisplay | TRUE | True |
| 2011100111 | 2024沙滩节折扣礼包-战装-19.99 | PirceDisplay | TRUE | True |
| 2011100112 | 2024沙滩节折扣礼包-二代养成线-4.99-schema6 | PirceDisplay | TRUE | True |
| 2011100113 | 2024沙滩节折扣礼包-二代养成线-9.99-schema6 | PirceDisplay | TRUE | True |
| 2011100114 | 2024沙滩节折扣礼包-二代养成线-19.99-schema6 | PirceDisplay | TRUE | True |
| 2011100115 | 2024沙滩节折扣礼包-英雄-4.99-schema6 | PirceDisplay | TRUE | True |
| 2011100116 | 2024沙滩节折扣礼包-英雄-9.99-schema6 | PirceDisplay | TRUE | True |
| 2011100117 | 2024沙滩节折扣礼包-英雄-19.99-schema6 | PirceDisplay | TRUE | True |
| 2011100118 | 2024沙滩节折扣礼包-机甲-4.99-schema6 | PirceDisplay | TRUE | True |
| 2011100119 | 2024沙滩节折扣礼包-机甲-9.99-schema6 | PirceDisplay | TRUE | True |
| 2011100120 | 2024沙滩节折扣礼包-机甲-19.99-schema6 | PirceDisplay | TRUE | True |
| 2011100121 | 2024沙滩节行军表情 | PirceDisplay | FALSE | False |
| 2011100177 | 2024周年庆行军表情 | PirceDisplay | FALSE | False |
| 2011100182 | 2024周年庆锦鲤礼包-第1天 | PirceDisplay | FALSE | False |
| 2011100183 | 2024周年庆锦鲤礼包-第2天 | PirceDisplay | FALSE | False |
| 2011100184 | 2024周年庆锦鲤礼包-第3天 | PirceDisplay | FALSE | False |
| 2011100185 | 2024周年庆锦鲤礼包-第4天 | PirceDisplay | FALSE | False |
| 2011100186 | 2024周年庆锦鲤礼包-第5天 | PirceDisplay | FALSE | False |
| 2011100187 | 2024登月节买三赠一（小R）-schema3 | PirceDisplay | TRUE | True |
| 2011100188 | 2024登月节买三赠一（zhongR）-schema3 | PirceDisplay | TRUE | True |
| 2011100194 | 2024登月节买三赠一（大超R）-schema3 | PirceDisplay | TRUE | True |
| 2011100195 | 2024登月节买三赠一（小R）-schema6 | PirceDisplay | TRUE | True |
| 2011100196 | 2024登月节买三赠一（zhongR）-schema6 | PirceDisplay | TRUE | True |
| 2011100197 | 2024登月节买三赠一（大超R）-schema6 | PirceDisplay | TRUE | True |
| 2011100198 | 2024登月节行军表情 | PirceDisplay | FALSE | False |
| 2011100199 | 登月节2024新七日活动-付费礼包-第1天 | PirceDisplay | FALSE | False |
| 2011100200 | 登月节2024新七日活动-付费礼包-第2天 | PirceDisplay | FALSE | False |
| 2011100201 | 登月节2024新七日活动-付费礼包-第3天 | PirceDisplay | FALSE | False |
| 2011100202 | 登月节2024新七日活动-付费礼包-第4天 | PirceDisplay | FALSE | False |
| 2011100203 | 登月节2024新七日活动-付费礼包-第5天 | PirceDisplay | FALSE | False |
| 201110021 | 英雄达到1星（美妮） | PirceDisplay | FALSE | False |
| 201110022 | 英雄达到2星（美妮） | PirceDisplay | FALSE | False |
| 201110023 | 英雄达到3星（美妮） | PirceDisplay | FALSE | False |
| 201110024 | 英雄达到4星（美妮） | PirceDisplay | FALSE | False |
| 201110025 | 英雄达到技能2222（美妮） | PirceDisplay | FALSE | False |
| 201110026 | 英雄达到5星（美妮） | PirceDisplay | FALSE | False |
| 201110027 | 英雄达到技能3333（美妮） | PirceDisplay | FALSE | False |
| 201110028 | 英雄达到6星（美妮） | PirceDisplay | FALSE | False |
| 201110029 | 英雄达到1星（露易丝） | PirceDisplay | FALSE | False |
| 201110030 | 英雄达到2星（露易丝） | PirceDisplay | FALSE | False |
| 201110031 | 英雄达到3星（露易丝） | PirceDisplay | FALSE | False |
| 201110032 | 英雄达到4星（露易丝） | PirceDisplay | FALSE | False |
| 201110033 | 英雄达到技能2222（露易丝） | PirceDisplay | FALSE | False |
| 201110034 | 英雄达到5星（露易丝） | PirceDisplay | FALSE | False |
| 201110035 | 英雄达到技能3333（露易丝） | PirceDisplay | FALSE | False |
| 201110036 | 英雄达到6星（露易丝） | PirceDisplay | FALSE | False |
| 201110037 | 英雄达到1星（杰克） | PirceDisplay | FALSE | False |
| 201110038 | 英雄达到2星（杰克） | PirceDisplay | FALSE | False |
| 201110039 | 英雄达到3星（杰克） | PirceDisplay | FALSE | False |
| 201110040 | 英雄达到4星（杰克） | PirceDisplay | FALSE | False |
| 201110041 | 英雄达到技能2222（杰克） | PirceDisplay | FALSE | False |
| 201110042 | 英雄达到5星（杰克） | PirceDisplay | FALSE | False |
| 201110043 | 英雄达到技能3333（杰克） | PirceDisplay | FALSE | False |
| 201110044 | 英雄达到6星（杰克） | PirceDisplay | FALSE | False |
| 201110045 | 英雄达到1星（肖恩） | PirceDisplay | FALSE | False |
| 201110046 | 英雄达到2星（肖恩） | PirceDisplay | FALSE | False |
| 201110047 | 英雄达到3星（肖恩） | PirceDisplay | FALSE | False |
| 201110048 | 英雄达到4星（肖恩） | PirceDisplay | FALSE | False |
| 201110049 | 英雄达到技能2222（肖恩） | PirceDisplay | FALSE | False |
| 201110050 | 英雄达到5星（肖恩） | PirceDisplay | FALSE | False |
| 201110051 | 英雄达到技能3333（肖恩） | PirceDisplay | FALSE | False |
| 201110052 | 英雄达到6星（肖恩） | PirceDisplay | FALSE | False |
| 2011110001 | 新展览品礼包 | PirceDisplay | FALSE | False |
| 2011120001 | 月度礼包（新服） | PirceDisplay | FALSE | False |
| 2011120002 | 月度礼包（老服） | PirceDisplay | FALSE | False |
| 2011120003 | 月度礼包_schema3 | PirceDisplay | FALSE | False |
| 2011120004 | 月度礼包_schema4 | PirceDisplay | FALSE | False |
| 2011120005 | 月度礼包_schema3_new | PirceDisplay | FALSE | False |
| 2011120006 | 月度礼包_schema4,5 | PirceDisplay | FALSE | False |
| 2011120007 | 千万下载礼包 | PirceDisplay | FALSE | False |
| 2011120008 | 千万下载礼包-第22-28天版本 | PirceDisplay | FALSE | False |
| 2011120009 | 周年庆三千万下载礼包 | PirceDisplay | FALSE | False |
| 2011120010 | t6礼包 | PirceDisplay | FALSE | False |
| 2011120011 | 四千万下载礼包 | PirceDisplay | FALSE | False |
| 2011120012 | 五千万下载礼包 | PirceDisplay | FALSE | False |
| 2011120013 | 月度礼包_schema6 | PirceDisplay | FALSE | False |
| 2011120014 | 六千万下载礼包 | PirceDisplay | FALSE | False |
| 2011120015 | 七千万下载礼包_schema3-5 | PirceDisplay | FALSE | False |
| 2011120016 | 七千万下载礼包_schema6 | PirceDisplay | FALSE | False |
| 2011150019 | 新自选礼包（老服周循环-无红色收藏品） | PirceDisplay | TRUE | True |
| 2011150020 | 新自选礼包（新服20天-无军备战装） | PirceDisplay | TRUE | True |
| 2011150021 | 新自选礼包（新服27天-无军备战装） | PirceDisplay | TRUE | True |
| 2011150022 | 新自选礼包（新服34天-无战装） | PirceDisplay | TRUE | True |
| 2011150023 | 新自选礼包（新服41天-无战装） | PirceDisplay | TRUE | True |
| 2011150024 | 新自选礼包（老服周循环-无战装） | PirceDisplay | TRUE | True |
| 2011150025 | 新自选礼包（老服周循环-全线） | PirceDisplay | TRUE | True |
| 2011160001 | 美妮礼包（注册） | PirceDisplay | FALSE | False |
| 2011160002 | 罗尼贾礼包（新服9天） | PirceDisplay | FALSE | False |
| 2011160003 | 露易丝礼包（新服23天） | PirceDisplay | FALSE | False |
| 2011160004 | 美妮礼包（戴维斯转盘） | PirceDisplay | FALSE | False |
| 2011160005 | 罗尼贾礼包（菲奥娜转盘） | PirceDisplay | FALSE | False |
| 2011160006 | 露易丝礼包（克拉克转盘） | PirceDisplay | FALSE | False |
| 2011160007 | 美妮专属礼包_9.99-连锁版 | PirceDisplay | FALSE | False |
| 2011160008 | 美妮专属礼包_19.99-连锁版 | PirceDisplay | FALSE | False |
| 2011160009 | 美妮专属礼包_49.99-连锁版 | PirceDisplay | FALSE | False |
| 2011160010 | 美妮专属礼包_99.99（100片）-连锁版 | PirceDisplay | FALSE | False |
| 2011160011 | 美妮专属礼包_99.99（100片）-连锁版 | PirceDisplay | FALSE | False |
| 2011160012 | 美妮专属礼包_99.99（85片）-连锁版 | PirceDisplay | FALSE | False |
| 2011160013 | 美妮专属礼包_99.99（85片）-连锁版 | PirceDisplay | FALSE | False |
| 2011160014 | 美妮专属礼包_99.99（80片）-连锁版 | PirceDisplay | FALSE | False |
| 2011160015 | 美妮专属礼包_99.99（80片）-连锁版 | PirceDisplay | FALSE | False |
| 2011160016 | 美妮专属礼包_99.99（80片）-连锁版 | PirceDisplay | FALSE | False |
| 2011170001 | 可视化礼包 | PirceDisplay | FALSE | False |
| 2011170002 | 可视化礼包2 | PirceDisplay | FALSE | False |
| 2011170003 | 可视化礼包3 | PirceDisplay | FALSE | False |
| 2011170004 | 可视化礼包4.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170005 | 可视化礼包4.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170006 | 可视化礼包9.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170007 | 可视化礼包19.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170008 | 可视化连锁礼包2 4.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170009 | 可视化连锁礼包2 4.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170010 | 可视化连锁礼包2 9.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170011 | 可视化连锁礼包2 19.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170012 | 可视化连锁礼包3 9.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170013 | 可视化连锁礼包3 9.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170014 | 可视化连锁礼包3 19.99-连锁版 | PirceDisplay | FALSE | False |
| 2011170015 | 可视化连锁礼包3 49.99-连锁版 | PirceDisplay | FALSE | False |
| 2011180001 | 双天赋礼包（美妮） | PirceDisplay | TRUE | True |
| 2011180002 | 双天赋礼包（洛朗） | PirceDisplay | TRUE | True |
| 2011180003 | 双天赋礼包（马克西姆斯） | PirceDisplay | TRUE | True |
| 2011180004 | 双天赋礼包（露易丝·阿姆斯特朗） | PirceDisplay | TRUE | True |
| 2011180005 | 双天赋礼包（罗尼·贾） | PirceDisplay | TRUE | True |
| 2011180006 | 双天赋礼包（杰克） | PirceDisplay | TRUE | True |
| 2011180007 | 双天赋礼包（肖恩） | PirceDisplay | TRUE | True |
| 2011180008 | 双天赋礼包（彼得） | PirceDisplay | TRUE | True |
| 2011180009 | 双天赋礼包（强尼） | PirceDisplay | TRUE | True |
| 2011180010 | 双天赋礼包（戴维斯） | PirceDisplay | TRUE | True |
| 2011180011 | 双天赋礼包（蒂芙尼） | PirceDisplay | TRUE | True |
| 2011180012 | 双天赋礼包（乔伊） | PirceDisplay | TRUE | True |
| 2011180013 | 双天赋礼包（葛列格） | PirceDisplay | TRUE | True |
| 2011180014 | 双天赋礼包（拉姆斯） | PirceDisplay | TRUE | True |
| 2011180015 | 双天赋礼包（菲奥娜） | PirceDisplay | TRUE | True |
| 2011180016 | 双天赋礼包（克拉克兄弟） | PirceDisplay | TRUE | True |
| 2011180017 | 双天赋礼包（巴泽尔） | PirceDisplay | TRUE | True |
| 2011180018 | 双天赋礼包（卡瑞拉） | PirceDisplay | TRUE | True |
| 2011180019 | 双天赋礼包（肯） | PirceDisplay | TRUE | True |
| 2011180020 | 双天赋礼包（埃尔默） | PirceDisplay | TRUE | True |
| 2011180021 | 双天赋礼包（奥德里奇） | PirceDisplay | TRUE | True |
| 2011180022 | 双天赋礼包（索尔） | PirceDisplay | TRUE | True |
| 2011180023 | 双天赋礼包（德里克） | PirceDisplay | TRUE | True |
| 2011180024 | 双天赋礼包（卡尔） | PirceDisplay | TRUE | True |
| 2011180025 | 双天赋礼包（哈迪） | PirceDisplay | TRUE | True |
| 2011180026 | 双天赋礼包（比尔） | PirceDisplay | TRUE | True |
| 2011180027 | 双天赋礼包（塔西娅） | PirceDisplay | TRUE | True |
| 2011180028 | 双天赋礼包（博伊斯） | PirceDisplay | TRUE | True |
| 2011180029 | 双天赋礼包（桃乐丝） | PirceDisplay | TRUE | True |
| 2011180030 | 双天赋礼包（万斯） | PirceDisplay | TRUE | True |
| 2011180031 | 双天赋礼包（菲利克斯） | PirceDisplay | TRUE | True |
| 2011180032 | 双天赋礼包（格兰特） | PirceDisplay | TRUE | True |
| 2011180033 | 双天赋礼包（凯恩） | PirceDisplay | TRUE | True |
| 2011180034 | 双天赋礼包（古斯塔夫） | PirceDisplay | TRUE | True |
| 2011180035 | 双天赋礼包（赫尔曼） | PirceDisplay | TRUE | True |
| 2011180036 | 双天赋礼包（维罗妮卡） | PirceDisplay | TRUE | True |
| 2011180037 | 双天赋礼包（诺亚） | PirceDisplay | TRUE | True |
| 2011180038 | 双天赋礼包（维克） | PirceDisplay | TRUE | True |
| 2011180039 | 双天赋礼包（艾玛） | PirceDisplay | TRUE | True |
| 2011180040 | 双天赋礼包（萨姆） | PirceDisplay | TRUE | True |
| 2011180041 | 双天赋礼包（洪大师） | PirceDisplay | TRUE | True |
| 2011180042 | 双天赋礼包（布莱克） | PirceDisplay | TRUE | True |
| 2011180043 | 双天赋礼包（夏洛克罗西） | PirceDisplay | TRUE | True |
| 2011192001 | 回归特惠 | PirceDisplay | TRUE | True |
| 2011230108 | 每日礼包_4.99 | PirceDisplay | FALSE | False |
| 2011230206 | 挖矿小游戏-活动药水锚点礼包-4.99 | PirceDisplay | FALSE | False |
| 2011230207 | 挖矿小游戏-活动药水锚点礼包-9.99 | PirceDisplay | FALSE | False |
| 2011230208 | 挖矿小游戏-活动药水锚点礼包-19.99 | PirceDisplay | FALSE | False |
| 2011230209 | 挖矿小游戏-活动药水锚点礼包-49.99 | PirceDisplay | FALSE | False |
| 2011230210 | 挖矿小游戏-活动药水锚点礼包-99.99 | PirceDisplay | FALSE | False |
| 2011230211 | 挖矿小游戏-常规-每日礼包-4.99 | PirceDisplay | FALSE | False |
| 201130040 | 废弃展览品礼包触发 | PirceDisplay | FALSE | False |
| 201130118 | 破冰触发礼包（城建）_4.99 | PirceDisplay | FALSE | False |
| 201130119 | 破冰触发礼包（城建）_4.99 | PirceDisplay | FALSE | False |
| 201130120 | 破冰触发礼包（训练）_4.99 | PirceDisplay | FALSE | False |
| 201130121 | 破冰触发礼包（训练）_4.99 | PirceDisplay | FALSE | False |
| 201130122 | 破冰触发礼包（军备）_4.99 | PirceDisplay | FALSE | False |
| 201130123 | 破冰触发礼包（军备）_4.99 | PirceDisplay | FALSE | False |
| 201130124 | 资源耗尽触发_1.99 | PirceDisplay | TRUE | True |
| 201130125 | 资源耗尽触发_4.99 | PirceDisplay | TRUE | True |
| 201130126 | 资源耗尽触发_9.99 | PirceDisplay | TRUE | True |
| 201130127 | 资源耗尽触发_19.99 | PirceDisplay | TRUE | True |
| 201130128 | 资源耗尽触发_49.99 | PirceDisplay | TRUE | True |
| 201130129 | 17级要塞提升 | PirceDisplay | FALSE | False |
| 201130130 | 19级要塞提升 | PirceDisplay | FALSE | False |
| 201130131 | 21级要塞提升 | PirceDisplay | FALSE | False |
| 201130132 | 23级要塞提升 | PirceDisplay | FALSE | False |
| 201130133 | 25级要塞提升 | PirceDisplay | FALSE | False |
| 201130134 | 27级要塞提升 | PirceDisplay | FALSE | False |
| 201130135 | 29级要塞提升 | PirceDisplay | FALSE | False |
| 201130136 | 16级研究所提升(T3) | PirceDisplay | FALSE | False |
| 201130137 | 24级研究所提升(T4) | PirceDisplay | FALSE | False |
| 201130138 | 军事科技触发礼包_4.99 | PirceDisplay | FALSE | False |
| 201130139 | 军事科技触发礼包_4.99 | PirceDisplay | FALSE | False |
| 201130140 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130141 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130142 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130143 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130144 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130145 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130146 | 军事科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130147 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130148 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130149 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130150 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130151 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130152 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130153 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130154 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130155 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130156 | 军事科技触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130157 | 民用科技触发礼包_4.99 | PirceDisplay | FALSE | False |
| 201130158 | 民用科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130159 | 民用科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130160 | 民用科技触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130161 | 电子科研节点电池礼包_4.99 | PirceDisplay | FALSE | False |
| 201130162 | 电子科研节点电池礼包_19.99 | PirceDisplay | FALSE | False |
| 201130163 | 电子科研节点电池礼包_4.99 | PirceDisplay | FALSE | False |
| 201130164 | 电子科研节点电池礼包_19.99 | PirceDisplay | FALSE | False |
| 201130165 | 电子科研节点电池礼包_4.99 | PirceDisplay | FALSE | False |
| 201130166 | 电子科研节点电池礼包_19.99 | PirceDisplay | FALSE | False |
| 201130167 | 电子科研节点电池礼包_4.99 | PirceDisplay | FALSE | False |
| 201130168 | 电子科研节点电池礼包_19.99 | PirceDisplay | FALSE | False |
| 201130169 | T3训练部队触发礼包_4.99 | PirceDisplay | FALSE | False |
| 201130170 | T3训练部队触发礼包_9.99 | PirceDisplay | FALSE | False |
| 201130171 | T3训练部队触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130172 | T4训练部队触发礼包_9.99 | PirceDisplay | FALSE | False |
| 201130173 | T4训练部队触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130174 | T4训练部队触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130175 | T5训练部队触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130176 | T5训练部队触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130177 | T5训练部队触发礼包_99.99 | PirceDisplay | FALSE | False |
| 201130178 | 在线触发礼包_1.99 | PirceDisplay | FALSE | False |
| 201130179 | 在线触发礼包_4.99 | PirceDisplay | FALSE | False |
| 201130180 | 在线触发礼包_9.99 | PirceDisplay | FALSE | False |
| 201130181 | 在线触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130184 | 资源耗尽触发礼包_14.99 | PirceDisplay | TRUE | True |
| 201130185 | 资源耗尽触发礼包_29.99 | PirceDisplay | TRUE | True |
| 201130186 | 军备触发礼包（绿） | PirceDisplay | FALSE | False |
| 201130187 | 军备触发礼包飙车族（蓝0） | PirceDisplay | FALSE | False |
| 201130188 | 军备触发礼包打击手（蓝0） | PirceDisplay | FALSE | False |
| 201130189 | 军备触发礼包射击手（蓝0） | PirceDisplay | FALSE | False |
| 201130190 | 军备触发礼包飙车族（紫0） | PirceDisplay | FALSE | False |
| 201130191 | 军备触发礼包打击手（紫0） | PirceDisplay | FALSE | False |
| 201130192 | 军备触发礼包射击手（紫0） | PirceDisplay | FALSE | False |
| 201130193 | 军备触发礼包飙车族（紫2） | PirceDisplay | FALSE | False |
| 201130194 | 军备触发礼包打击手（紫2） | PirceDisplay | FALSE | False |
| 201130195 | 军备触发礼包射击手（紫2） | PirceDisplay | FALSE | False |
| 201130196 | 军备触发礼包飙车族（橙0） | PirceDisplay | FALSE | False |
| 201130197 | 军备触发礼包打击手（橙0） | PirceDisplay | FALSE | False |
| 201130198 | 军备触发礼包射击手（橙0） | PirceDisplay | FALSE | False |
| 201130199 | 军备触发礼包飙车族（橙2） | PirceDisplay | FALSE | False |
| 201130200 | 军备触发礼包打击手（橙2） | PirceDisplay | FALSE | False |
| 201130201 | 军备触发礼包射击手（橙2） | PirceDisplay | FALSE | False |
| 201130202 | 军备触发礼包飙车族（橙4） | PirceDisplay | FALSE | False |
| 201130203 | 军备触发礼包打击手（橙4） | PirceDisplay | FALSE | False |
| 201130204 | 军备触发礼包射击手（橙4） | PirceDisplay | FALSE | False |
| 201130205 | 占领行星枢纽LV1（kvk1) | PirceDisplay | FALSE | False |
| 201130206 | 占领行星枢纽LV2（kvk1) | PirceDisplay | FALSE | False |
| 201130207 | 占领行星枢纽LV3（kvk1) | PirceDisplay | FALSE | False |
| 201130208 | 争夺星际武器工厂（kvk1) | PirceDisplay | FALSE | False |
| 201130209 | 争夺基因宝库（kvk1) | PirceDisplay | FALSE | False |
| 201130346 | kvk3单兵种基因-骑兵克制-lv5-29.99 | PirceDisplay | FALSE | False |
| 201130347 | kvk3单兵种基因-骑兵克制-lv10-49.99 | PirceDisplay | FALSE | False |
| 201130348 | kvk3单兵种基因-骑兵克制-lv20-49.99 | PirceDisplay | FALSE | False |
| 201130349 | kvk3单兵种基因-骑兵攻击2-lv5-49.99 | PirceDisplay | FALSE | False |
| 201130350 | kvk3单兵种基因-骑兵攻击2-lv10-99.99 | PirceDisplay | FALSE | False |
| 201130351 | kvk3单兵种基因-骑兵攻击2-lv20-99.99 | PirceDisplay | FALSE | False |
| 201130352 | kvk3单兵种基因-骑兵攻击2-lv30-99.99 | PirceDisplay | FALSE | False |
| 201130353 | kvk3单兵种基因-骑兵攻击2-lv35-99.99 | PirceDisplay | FALSE | False |
| 201130354 | kvk3单兵种基因-骑兵攻击2-lv40-99.99 | PirceDisplay | FALSE | False |
| 201130355 | kvk3单兵种基因-弓兵克制-lv5-29.99 | PirceDisplay | FALSE | False |
| 201130356 | kvk3单兵种基因-弓兵克制-lv10-49.99 | PirceDisplay | FALSE | False |
| 201130357 | kvk3单兵种基因-弓兵克制-lv20-49.99 | PirceDisplay | FALSE | False |
| 201130358 | kvk3单兵种基因-弓兵攻击2-lv5-49.99 | PirceDisplay | FALSE | False |
| 201130359 | kvk3单兵种基因-弓兵攻击2-lv10-99.99 | PirceDisplay | FALSE | False |
| 201130360 | kvk3单兵种基因-弓兵攻击2-lv20-99.99 | PirceDisplay | FALSE | False |
| 201130361 | kvk3单兵种基因-弓兵攻击2-lv30-99.99 | PirceDisplay | FALSE | False |
| 201130362 | kvk3单兵种基因-骑兵攻击2-lv35-99.99 | PirceDisplay | FALSE | False |
| 201130363 | kvk3单兵种基因-弓兵攻击2-lv40-99.99 | PirceDisplay | FALSE | False |
| 201130364 | kvk3单兵种基因-步兵克制-lv5-29.99 | PirceDisplay | FALSE | False |
| 201130365 | kvk3单兵种基因-步兵克制-lv10-49.99 | PirceDisplay | FALSE | False |
| 201130366 | kvk3单兵种基因-步兵克制-lv20-49.99 | PirceDisplay | FALSE | False |
| 201130367 | kvk3单兵种基因-步兵防御2-lv5-49.99 | PirceDisplay | FALSE | False |
| 201130368 | kvk3单兵种基因-步兵防御2-lv10-99.99 | PirceDisplay | FALSE | False |
| 201130369 | kvk3单兵种基因-步兵防御2-lv20-99.99 | PirceDisplay | FALSE | False |
| 201130370 | kvk3单兵种基因-步兵防御2-lv30-99.99 | PirceDisplay | FALSE | False |
| 201130371 | kvk3单兵种基因-步兵防御2-lv35-99.99 | PirceDisplay | FALSE | False |
| 201130372 | kvk3单兵种基因-步兵防御2-lv40-99.99 | PirceDisplay | FALSE | False |
| 201130398 | bi推荐_英雄经验_4.99 | PirceDisplay | TRUE | True |
| 201130399 | bi推荐_英雄经验_9.99 | PirceDisplay | TRUE | True |
| 201130400 | bi推荐_英雄经验_14.99 | PirceDisplay | TRUE | True |
| 201130401 | bi推荐_英雄经验_19.99 | PirceDisplay | TRUE | True |
| 201130402 | bi推荐_英雄经验_24.99 | PirceDisplay | TRUE | True |
| 201130403 | bi推荐_英雄经验_29.99 | PirceDisplay | TRUE | True |
| 201130404 | bi推荐_英雄经验_49.99 | PirceDisplay | TRUE | True |
| 201130405 | bi推荐_英雄经验_99.99 | PirceDisplay | TRUE | True |
| 201130406 | bi推荐_英雄橙色升星_4.99 | PirceDisplay | TRUE | True |
| 201130407 | bi推荐_英雄橙色升星_9.99 | PirceDisplay | TRUE | True |
| 201130408 | bi推荐_英雄橙色升星_14.99 | PirceDisplay | TRUE | True |
| 201130409 | bi推荐_英雄橙色升星_19.99 | PirceDisplay | TRUE | True |
| 201130410 | bi推荐_英雄橙色升星_24.99 | PirceDisplay | TRUE | True |
| 201130411 | bi推荐_英雄橙色升星_29.99 | PirceDisplay | TRUE | True |
| 201130412 | bi推荐_英雄橙色升星_49.99 | PirceDisplay | TRUE | True |
| 201130413 | bi推荐_英雄橙色升星_99.99 | PirceDisplay | TRUE | True |
| 201130414 | bi推荐_英雄紫色升星_1.99 | PirceDisplay | FALSE | False |
| 201130415 | bi推荐_英雄紫色升星_4.99 | PirceDisplay | FALSE | False |
| 201130416 | bi推荐_英雄紫色升星_9.99 | PirceDisplay | FALSE | False |
| 201130417 | bi推荐_英雄紫色升星_14.99 | PirceDisplay | FALSE | False |
| 201130418 | bi推荐_英雄紫色升星_19.99 | PirceDisplay | FALSE | False |
| 201130419 | 橙机甲触发20级 | PirceDisplay | FALSE | False |
| 201130420 | 橙机甲触发30级 | PirceDisplay | FALSE | False |
| 201130421 | 橙机甲触发40级 | PirceDisplay | FALSE | False |
| 201130422 | 31级要塞提升 | PirceDisplay | FALSE | False |
| 201130423 | 研究所-32 | PirceDisplay | FALSE | False |
| 201130424 | 33级要塞提升 | PirceDisplay | FALSE | False |
| 201130425 | 35级要塞提升 | PirceDisplay | FALSE | False |
| 201130426 | 研究所-35 | PirceDisplay | FALSE | False |
| 201130427 | 武装科研触发_19.99_1 | PirceDisplay | FALSE | False |
| 201130428 | 武装科研触发_49.99_1 | PirceDisplay | FALSE | False |
| 201130429 | 武装科研触发_49.99_2 | PirceDisplay | FALSE | False |
| 201130430 | 武装科研触发_99.99_1 | PirceDisplay | FALSE | False |
| 201130431 | 武装科研触发_99.99_2 | PirceDisplay | FALSE | False |
| 201130432 | 武装科研触发_99.99_3 | PirceDisplay | FALSE | False |
| 201130433 | T6军备触发_A红2_29.99 | PirceDisplay | FALSE | False |
| 201130434 | T6军备触发_A红4_49.99 | PirceDisplay | FALSE | False |
| 201130435 | T6军备触发_A红5_99.99 | PirceDisplay | FALSE | False |
| 201130436 | T6军备触发_B红2_49.99 | PirceDisplay | FALSE | False |
| 201130437 | T6军备触发_B红4_99.99 | PirceDisplay | FALSE | False |
| 201130438 | T6军备触发_B红5_99.99 | PirceDisplay | FALSE | False |
| 201130439 | bi推荐_军事民用科研_4.99 | PirceDisplay | TRUE | True |
| 201130440 | bi推荐_军事民用科研_9.99 | PirceDisplay | TRUE | True |
| 201130441 | bi推荐_军事民用科研_14.99 | PirceDisplay | TRUE | True |
| 201130442 | bi推荐_军事民用科研_19.99 | PirceDisplay | TRUE | True |
| 201130443 | bi推荐_军事民用科研_24.99 | PirceDisplay | TRUE | True |
| 201130444 | bi推荐_军事民用科研_29.99 | PirceDisplay | TRUE | True |
| 201130445 | bi推荐_军事民用科研_49.99 | PirceDisplay | TRUE | True |
| 201130446 | bi推荐_军事民用科研_99.99 | PirceDisplay | TRUE | True |
| 201130447 | 战装重铸触发_紫色_3次_9.99 | PirceDisplay | FALSE | False |
| 201130448 | 战装重铸触发_紫色_10次_19.99 | PirceDisplay | FALSE | False |
| 201130449 | 战装重铸触发_橙色_3次_29.99 | PirceDisplay | FALSE | False |
| 201130450 | 战装重铸触发_橙色_10次_49.99 | PirceDisplay | FALSE | False |
| 201130451 | 战装重铸触发_紫色_循环20次_19.99 | PirceDisplay | FALSE | False |
| 201130452 | 战装重铸触发_橙色_循环20次_49.99 | PirceDisplay | FALSE | False |
| 201130453 | 一条龙触发礼包-芯片贬值应用 | PirceDisplay | TRUE | True |
| 201130454 | 锚点触发礼包_城建 | PirceDisplay | TRUE | True |
| 201130455 | 锚点触发礼包_训练 | PirceDisplay | TRUE | True |
| 201130456 | 锚点触发礼包_科研 | PirceDisplay | TRUE | True |
| 201130457 | 锚点触发礼包_收藏品 | PirceDisplay | TRUE | True |
| 201130458 | 锚点触发礼包_军备 | PirceDisplay | TRUE | True |
| 201130459 | 锚点触发礼包_战装 | PirceDisplay | TRUE | True |
| 201130460 | 资源耗尽触发礼包_99.99 | PirceDisplay | TRUE | True |
| 201130467 | 一条龙触发礼包-战装突破（国服） | PirceDisplay | TRUE | True |
| 201130467 | 一条龙触发礼包-战装突破（国际服） | PirceDisplay | TRUE | True |
| 201130468 | 锚点触发礼包_红色升星石 | PirceDisplay | TRUE | True |
| 201130469 | 一条龙触发礼包-橙色升星石贬值应用 | PirceDisplay | TRUE | True |
| 201130470 | 机甲经验耗尽礼包4.99 | PirceDisplay | FALSE | False |
| 201130471 | 机甲经验耗尽礼包9.99 | PirceDisplay | FALSE | False |
| 201130472 | 机甲经验耗尽礼包19.99 | PirceDisplay | FALSE | False |
| 201130473 | 机甲经验耗尽礼包29.99 | PirceDisplay | FALSE | False |
| 201130474 | 机甲经验耗尽礼包49.99 | PirceDisplay | FALSE | False |
| 201130475 | 机甲经验耗尽礼包99.99 | PirceDisplay | FALSE | False |
| 201130476 | bi推荐_机甲经验4.99 | PirceDisplay | TRUE | True |
| 201130477 | bi推荐_机甲经验9.99 | PirceDisplay | TRUE | True |
| 201130478 | bi推荐_机甲经验14.99 | PirceDisplay | TRUE | True |
| 201130479 | bi推荐_机甲经验19.99 | PirceDisplay | TRUE | True |
| 201130480 | bi推荐_机甲经验24.99 | PirceDisplay | TRUE | True |
| 201130481 | bi推荐_机甲经验29.99 | PirceDisplay | TRUE | True |
| 201130482 | bi推荐_机甲经验49.99 | PirceDisplay | TRUE | True |
| 201130483 | bi推荐_机甲经验99.99 | PirceDisplay | TRUE | True |
| 201130484 | 战装-红色-加工至20级（一条龙） | PirceDisplay | TRUE | True |
| 201130485 | 战装-红色-加工至23级（一条龙） | PirceDisplay | TRUE | True |
| 201130486 | 战装-红色-加工至25级（一条龙） | PirceDisplay | TRUE | True |
| 201130487 | 战装-红色-加工至27级（一条龙） | PirceDisplay | TRUE | True |
| 201130488 | 战装-红色-加工至29级（一条龙） | PirceDisplay | TRUE | True |
| 201130489 | 战装-橙色-加工至20级（一条龙） | PirceDisplay | TRUE | True |
| 201130573 | bi推荐_军备4.99 | PirceDisplay | FALSE | False |
| 201130574 | bi推荐_军备9.99 | PirceDisplay | FALSE | False |
| 201130575 | bi推荐_军备14.99 | PirceDisplay | FALSE | False |
| 201130576 | bi推荐_军备19.99 | PirceDisplay | FALSE | False |
| 201130577 | bi推荐_军备24.99 | PirceDisplay | FALSE | False |
| 201130578 | bi推荐_军备29.99 | PirceDisplay | FALSE | False |
| 201130579 | bi推荐_军备49.99 | PirceDisplay | FALSE | False |
| 201130580 | bi推荐_军备99.99 | PirceDisplay | FALSE | False |
| 201130581 | bi推荐_T6军备4.99 | PirceDisplay | FALSE | False |
| 201130582 | bi推荐_T6军备9.99 | PirceDisplay | FALSE | False |
| 201130583 | bi推荐_T6军备14.99 | PirceDisplay | FALSE | False |
| 201130584 | bi推荐_T6军备19.99 | PirceDisplay | FALSE | False |
| 201130585 | bi推荐_T6军备24.99 | PirceDisplay | FALSE | False |
| 201130586 | bi推荐_T6军备29.99 | PirceDisplay | FALSE | False |
| 201130587 | bi推荐_T6军备49.99 | PirceDisplay | FALSE | False |
| 201130588 | bi推荐_T6军备99.99 | PirceDisplay | FALSE | False |
| 201130597 | T6训练部队触发礼包_19.99 | PirceDisplay | FALSE | False |
| 201130598 | T6训练部队触发礼包_49.99 | PirceDisplay | FALSE | False |
| 201130599 | T6训练部队触发礼包_99.99 | PirceDisplay | FALSE | False |
| 201130600 | 犀牛技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130601 | 犀牛技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130602 | 犀牛技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130603 | 猎豹技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130604 | 猎豹技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130605 | 猎豹技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130606 | 猎豹技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130607 | 毒蝎技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130608 | 毒蝎技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130609 | 毒蝎技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130610 | 毒蝎技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130611 | 巨象技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130612 | 巨象技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130613 | 巨象技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130614 | 巨象技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130615 | 天鹰技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130616 | 天鹰技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130617 | 天鹰技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130618 | 天鹰技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130619 | 雄狮技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130620 | 雄狮技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130621 | 雄狮技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130622 | 雄狮技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130623 | 螳螂技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130624 | 螳螂技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130625 | 螳螂技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130626 | 螳螂技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 201130627 | 战龟技能触发礼包-3级 | PirceDisplay | FALSE | False |
| 201130628 | 战龟技能触发礼包-5级 | PirceDisplay | FALSE | False |
| 201130629 | 战龟技能触发礼包-10级 | PirceDisplay | FALSE | False |
| 201130630 | 战龟技能触发礼包-15级 | PirceDisplay | FALSE | False |
| 2011697001 | 橙色英雄成就-解锁 | SubScene | normal_research |  |
| 2011697002 | 橙色英雄成就-2星 | SubScene | normal_research |  |
| 2011697003 | 橙色英雄成就-3星 | SubScene | normal_research |  |
| 2011697004 | 橙色英雄成就-4星 | SubScene | normal_research |  |
| 2011697005 | 橙色英雄成就-卡牌技能222 | SubScene | normal_research |  |
| 2011697006 | 橙色英雄成就-SLG技能222 | SubScene | normal_research |  |
| 2011697007 | 橙色英雄成就-5星 | SubScene | normal_research |  |
| 2011697008 | 橙色英雄成就-6星 | SubScene | normal_research |  |
| 2011697009 | 橙色英雄成就-卡牌技能333 | SubScene | normal_research |  |
| 2011697010 | 橙色英雄成就-SLG技能333 | SubScene | normal_research |  |
| 2011697011 | 橙色英雄成就-7星 | SubScene | battery_research |  |
| 2011697012 | 橙色英雄成就-8星 | SubScene | battery_research |  |
| 2011697013 | 橙色英雄成就-卡牌技能444 | SubScene | battery_research |  |
| 2011697014 | 橙色英雄成就-SLG技能444 | SubScene | battery_research |  |
| 2011697015 | 橙色英雄成就-9星 | SubScene | battery_research |  |
| 2011697016 | 橙色英雄成就-10星 | SubScene | battery_research |  |
| 2011697017 | 紫色英雄成就-解锁 | SubScene | battery_research |  |
| 2011697018 | 紫色英雄成就-4星 | SubScene | battery_research |  |
| 2011820001 | 冒险家专属礼包_4.99-连锁版 | SubScene | hero_main |  |
| 2011820002 | 冒险家专属礼包_9.99-连锁版 | SubScene | hero_main |  |
| 2011820003 | 冒险家专属礼包_19.99-连锁版 | SubScene | hero_main |  |
| 2011820004 | 冒险家专属礼包_49.99-连锁版 | SubScene | hero_main |  |
| 2011820005 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820006 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820007 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820008 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820009 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820010 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820011 | 冒险家专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820012 | 精灵剑士专属礼包_4.99-连锁版 | SubScene | hero_main |  |
| 2011820013 | 精灵剑士专属礼包_9.99-连锁版 | SubScene | hero_main |  |
| 2011820014 | 精灵剑士专属礼包_19.99-连锁版 | SubScene | hero_main |  |
| 2011820015 | 精灵剑士专属礼包_49.99-连锁版 | SubScene | hero_main |  |
| 2011820016 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820017 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820018 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820019 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820020 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820021 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820022 | 精灵剑士专属礼包_99.99-连锁版 | SubScene | hero_talent |  |
| 2011820023 | 修女专属礼包_4.99-连锁版 | SubScene | hero_talent |  |
| 2011820024 | 修女专属礼包_9.99-连锁版 | SubScene | hero_talent |  |
| 2011820025 | 修女专属礼包_19.99-连锁版 | SubScene | hero_talent |  |
| 2011820026 | 修女专属礼包_49.99-连锁版 | SubScene | hero_talent |  |
| 2011820027 | 修女专属礼包_99.99-连锁版 | SubScene | hero_talent |  |
| 2011820028 | 修女专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820029 | 修女专属礼包_99.99-连锁版 | SubScene | hero_main |  |
| 2011820030 | 修女专属礼包_99.99-连锁版 | SubScene | hero_talent |  |
| 2011840001 | 科技触发礼包-原科研过程触发-test | SubScene |  | normal_research |
| 2011840002 | 精英研究T3-test | SubScene |  | normal_research |
| 2011840003 | 军事科技触发礼包_4.99 | SubScene |  | normal_research |
| 2011840004 | 军事科技触发礼包_4.99 | PirceDisplay | TRUE | True |
| 2011840004 | 军事科技触发礼包_4.99 | SubScene |  | normal_research |
| 2011840005 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840005 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840006 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840006 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840007 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840007 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840008 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840008 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840009 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840009 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840010 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840010 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840011 | 军事科技触发礼包_19.99 | PirceDisplay | TRUE | True |
| 2011840011 | 军事科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840012 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840012 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840013 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840013 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840014 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840014 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840015 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840015 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840016 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840016 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840017 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840017 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840018 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840018 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840019 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840019 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840020 | 军事科技触发礼包_49.99 | PirceDisplay | TRUE | True |
| 2011840020 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840021 | 军事科技触发礼包_49.99 | SubScene |  | normal_research |
| 2011840022 | 民用科技触发礼包_4.99 | SubScene |  | normal_research |
| 2011840023 | 民用科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840024 | 民用科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840025 | 民用科技触发礼包_19.99 | SubScene |  | normal_research |
| 2011840026 | 电子科研节点电池礼包_4.99 | SubScene |  | battery_research |
| 2011840027 | 电子科研节点电池礼包_19.99 | SubScene |  | battery_research |
| 2011840028 | 电子科研节点电池礼包_4.99 | SubScene |  | battery_research |
| 2011840029 | 电子科研节点电池礼包_19.99 | SubScene |  | battery_research |
| 2011840030 | 电子科研节点电池礼包_4.99 | SubScene |  | battery_research |
| 2011840031 | 电子科研节点电池礼包_19.99 | SubScene | normal_research | battery_research |
| 2011840032 | 电子科研节点电池礼包_4.99 | SubScene | normal_research | battery_research |
| 2011840033 | 电子科研节点电池礼包_19.99 | SubScene | normal_research | battery_research |
| 2011840034 | 英雄联动礼包-冒险家皮匠 | SubScene | normal_research |  |
| 2011850001 | 周常礼包-新 | SubScene | normal_research |  |
| 2011850002 | 金羽锚点礼包 | SubScene | normal_research |  |
| 2011850003 | 机甲耐久礼包 | SubScene | normal_research |  |
| 2011850004 | 双生符石道具礼包 | SubScene | normal_research |  |
| 2011850005 | 金色卡牌技能书礼包 | SubScene | normal_research |  |
| 2011850006 | 金色slg技能书礼包 | SubScene | normal_research |  |
| 2011850007 | 英雄特殊天赋锚点礼包 | SubScene | normal_research |  |
| 2011850008 | 宝石升级道具锚点礼包 | SubScene | normal_research |  |
| 2011850009 | 宝石洗练道具锚点礼包 | SubScene | normal_research |  |
| 2011850010 | 双倍售卖道具礼包 | SubScene | normal_research |  |
| 2011850011 | 机能核心道具锚点礼包 | SubScene | normal_research |  |
| 2011860001 | 紫色机甲升级20触发礼包9.99 | SubScene |  | mecha_main |
| 2011860002 | 紫色机甲升级30触发礼包9.99 | SubScene |  | mecha_main |
| 2011860003 | 紫色机甲升级40触发礼包19.99 | SubScene |  | mecha_main |
| 2011860004 | 紫色机甲升级50触发礼包19.99 | SubScene |  | mecha_main |
| 2011860005 | 紫色机甲升级70触发礼包49.99 | SubScene |  | mecha_main |
| 2011860006 | 紫色机甲升级90触发礼包99.99 | SubScene |  | mecha_main |
| 2011860007 | 橙机甲触发20级 | SubScene |  | mecha_main |
| 2011860008 | 橙机甲触发30级 | SubScene |  | mecha_main |
| 2011860009 | 橙机甲触发40级 | SubScene |  | mecha_main |
| 2011860010 | 机甲经验耗尽礼包4.99 | SubScene |  | mecha_main |
| 2011860011 | 机甲经验耗尽礼包9.99 | SubScene |  | mecha_main |
| 2011860012 | 机甲经验耗尽礼包19.99 | SubScene |  | mecha_main |
| 2011860013 | 机甲经验耗尽礼包29.99 | SubScene |  | mecha_main |
| 2011860014 | 机甲经验耗尽礼包49.99 | SubScene |  | mecha_main |
| 2011860015 | 机甲经验耗尽礼包99.99 | SubScene |  | mecha_main |
| 2011860016 | 蒸汽蜘蛛技能触发礼包-5级 | SubScene |  | mecha_main |
| 2011860017 | 蒸汽蜘蛛技能触发礼包-10级 | SubScene |  | mecha_main |
| 2011860018 | 蒸汽蜘蛛技能触发礼包-15级 | SubScene |  | mecha_main |
| 2011860019 | 双头狼技能触发礼包-3级 | SubScene |  | mecha_main |
| 2011860020 | 双头狼技能触发礼包-5级 | SubScene |  | mecha_main |
| 2011860021 | 双头狼技能触发礼包-10级 | SubScene |  | mecha_main |
| 2011860022 | 双头狼技能触发礼包-15级 | SubScene |  | mecha_main |
| 2011860023 | 蝎尾狮技能触发礼包-3级 | SubScene |  | mecha_main |
| 2011860024 | 蝎尾狮技能触发礼包-5级 | SubScene |  | mecha_main |
| 2011860025 | 蝎尾狮技能触发礼包-10级 | SubScene |  | mecha_main |
| 2011860026 | 蝎尾狮技能触发礼包-15级 | SubScene |  | mecha_main |
| 2011860027 | 天鹰技能触发礼包-3级 | SubScene |  | mecha_main |
| 2011860028 | 天鹰技能触发礼包-5级 | SubScene |  | mecha_main |
| 2011860029 | 天鹰技能触发礼包-10级 | SubScene |  | mecha_main |
| 2011860030 | 天鹰技能触发礼包-15级 | SubScene |  | mecha_main |
| 2011900001 | 情景礼包-橙色英雄60级 | SubScene |  | hero_main |
| 2011900002 | 情景礼包-橙色英雄80级 | SubScene |  | hero_main |
| 2011900003 | 情景礼包-橙色英雄130级 | SubScene |  | hero_main |
| 2011900004 | 情景礼包-橙色英雄180级 | SubScene |  | hero_main |
| 2011900005 | 情景礼包-橙色升星4星 | SubScene |  | hero_main |
| 2011900006 | 情景礼包-橙色升星6星 | SubScene |  | hero_main |
| 2011900007 | 情景礼包-橙色升星8星 | SubScene |  | hero_main |
| 2011900008 | 情景礼包-橙色升星10星 | SubScene |  | hero_main |
| 2011900009 | 情景礼包-橙色英雄41级 | SubScene |  | hero_main |
| 2011900010 | 情景礼包-橙色英雄61级 | SubScene |  | hero_main |
| 2011900011 | 情景礼包-橙色英雄101级 | SubScene |  | hero_main |
| 2011900012 | 情景礼包-橙色英雄151级 | SubScene |  | hero_main |
| 2011900013 | 情景礼包-橙色英雄171级 | SubScene |  | hero_main |
| 2011900014 | 情景礼包-裁缝英雄75级 | SubScene |  | hero_main |
| 2011900015 | 情景礼包-镇长英雄75级 | SubScene |  | hero_main |
| 2011900016 | 情景礼包-冒险家英雄75级 | SubScene |  | hero_main |
| 2011900017 | 情景礼包-皮匠英雄85级 | SubScene |  | hero_main |
| 2011900018 | 情景礼包-香水师英雄110级 | SubScene |  | hero_main |
| 2011900019 | 情景礼包-化学家英雄130级 | SubScene |  | hero_main |
| 2011900020 | 情景礼包-占星师英雄130级 | SubScene |  | hero_main |
| 2011900021 | 获得橙色英雄 | SubScene |  | hero_main |
| 2011900022 | 英雄天赋特殊材料-解锁英雄特殊天赋-第5页第10个节点 | SubScene |  | hero_talent |
| 2011900023 | 英雄天赋特殊材料-解锁10页 | SubScene |  | hero_talent |
| 2011900024 | 英雄天赋特殊材料-解锁20页 | SubScene |  | hero_talent |
| 2011900025 | 英雄天赋特殊材料-解锁30页 | SubScene |  | hero_talent |
| 2011900026 | 英雄天赋特殊材料-解锁40页 | SubScene |  | hero_talent |
| 2011900027 | 英雄天赋特殊材料-解锁50页 | SubScene |  | hero_talent |
| 2011900028 | 缺粉尘触发礼包-1 | SubScene |  | hero_main |
| 2011900029 | 缺粉尘触发礼包-2 | SubScene |  | hero_main |
| 2011900030 | 英雄天赋特殊材料-解锁英雄天赋功能-第1页第10个节点 | SubScene |  | hero_talent |
| 201190041 | 科技节初级通行证2023 | PirceDisplay | TRUE | True |
| 201190042 | 科技节高级通行证2023 | PirceDisplay | TRUE | True |
| 201190043 | 拓荒节初级通行证2023 | PirceDisplay | TRUE | True |
| 201190044 | 拓荒节高级通行证2023 | PirceDisplay | TRUE | True |
| 201190048 | 端午节初级通行证2023 | PirceDisplay | TRUE | True |
| 201190049 | 端午节高级通行证2023 | PirceDisplay | TRUE | True |
| 201190050 | 沙滩节初级通行证2023 | PirceDisplay | TRUE | True |
| 201190051 | 沙滩节高级通行证2023 | PirceDisplay | TRUE | True |
| 201190052 | 周年庆初级通行证2023 | PirceDisplay | TRUE | True |
| 201190053 | 周年庆高级通行证2023 | PirceDisplay | TRUE | True |
| 201190054 | 登月节初级通行证2023 | PirceDisplay | TRUE | True |
| 201190055 | 登月节高级通行证2023 | PirceDisplay | TRUE | True |
| 201190056 | 2023登月节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190057 | 2023万圣节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190058 | 万圣节初级通行证2023 | PirceDisplay | TRUE | True |
| 201190059 | 万圣节高级通行证2023 | PirceDisplay | TRUE | True |
| 201190060 | 2023感恩节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190071 | 2023圣诞节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190074 | 军备7日活动宝箱礼包 | PirceDisplay | TRUE | True |
| 201190077 | 2024复活节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190080 | 2024科技节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190089 | 2024端午节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190092 | 2024沙滩节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190093 | 沙滩节初级通行证2024 | PirceDisplay | TRUE | True |
| 201190094 | 沙滩节高级通行证2024 | PirceDisplay | TRUE | True |
| 201190095 | 周年庆初级通行证2024 | PirceDisplay | TRUE | True |
| 201190096 | 周年庆高级通行证2024 | PirceDisplay | TRUE | True |
| 201190097 | 2024周年庆-7日活动宝箱-第一周 | PirceDisplay | TRUE | True |
| 201190098 | 2024周年庆-7日活动宝箱-第四周 | PirceDisplay | TRUE | True |
| 201190099 | 登月节初级通行证2024 | PirceDisplay | TRUE | True |
| 201190100 | 登月节高级通行证2024 | PirceDisplay | TRUE | True |
| 201190104 | 万圣节初级通行证2024 | PirceDisplay | TRUE | True |
| 201190105 | 万圣节高级通行证2024 | PirceDisplay | TRUE | True |
| 201190106 | 2024万圣节-7日活动宝箱 | PirceDisplay | TRUE | True |
| 201190107 | 礼包-转盘-前期月球抽奖 | PirceDisplay | TRUE | True |
| 2011910001 | 2025夏日节bp礼包 | SubScene | mecha_main |  |
| 2011910002 | 2025夏日节初级通行证 | SubScene | mecha_main |  |
| 2011910003 | 2025夏日节高级通行证 | SubScene | mecha_main |  |
| 2011910004 | 2025夏日节gacha礼包 | SubScene | mecha_main |  |
| 2011910005 | 2025夏日节行军表情 | SubScene | mecha_main |  |
| 2011910006 | 2025夏日节gacha礼包-随机19.99 | SubScene | mecha_main |  |
| 2011910007 | 2025夏日节gacha礼包-随机19.99 | SubScene | mecha_main |  |
| 2011910008 | 2025夏日节gacha礼包-随机19.99 | SubScene | mecha_main |  |
| 2011910009 | 2025夏日节gacha礼包-随机49.99 | SubScene | mecha_main |  |
| 2011910010 | 2025夏日节gacha礼包-随机99.99 | SubScene | mecha_main |  |
| 2011910011 | 2025夏日连锁礼包_1.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910012 | 2025夏日连锁礼包_4.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910013 | 2025夏日连锁礼包_4.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910014 | 2025夏日连锁礼包_9.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910015 | 2025夏日连锁礼包_9.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910016 | 2025夏日连锁礼包_19.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910017 | 2025夏日连锁礼包_29.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910018 | 2025夏日连锁礼包_49.99_schema3-5-小中R | SubScene | mecha_main |  |
| 2011910019 | 2025夏日连锁礼包_9.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910020 | 2025夏日连锁礼包_19.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910021 | 2025夏日连锁礼包_29.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910022 | 2025夏日连锁礼包_49.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910023 | 2025夏日连锁礼包_99.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910024 | 2025夏日连锁礼包_99.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910025 | 2025夏日连锁礼包_99.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910026 | 2025夏日连锁礼包_99.99_schema3-5-大超R | SubScene | mecha_main |  |
| 2011910027 | 2025-夏日节-shop装饰礼包 | SubScene | mecha_main |  |
| 2011910028 | 2025-夏日节-七日活动连锁礼包 | SubScene | mecha_main |  |
| 2011910029 | 2025占星节bp礼包 | SubScene | mecha_main |  |
| 2011910030 | 2025占星节初级通行证 | SubScene | mecha_main |  |
| 2011910032 | 2025占星节行军表情 | PirceDisplay | FALSE | False |
| 2011910033 | 2025占星节gacha礼包 | PirceDisplay | TRUE | True |

---

## 四、说明

- 配对键为 **(Id, PkgDesc)**；同一键在 A/B 出现次数不一致时，**不会**进入第三节。
- 若需按行号对齐对比，需另写脚本。
