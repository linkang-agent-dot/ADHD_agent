# -*- coding: utf-8 -*-
"""Path_*.asset keys/values 平行字典重对齐修复器（2026-07-17 马戏节DK错位血案）。
背景：Path_*.asset 的 paths 字段=keys(光杆名单)+values(key+objPath成对)按下标配对的序列化字典。
往 keys 单边插行 => 全部 DK 从插入点起下标错位（游戏内图标全乱）。
本脚本：按 values 顺序重建 keys；keys 里多出的光杆(孤儿)按 key->objPath 映射补成对到两侧末尾。
兼容 YAML plain scalar 折行（含空格文件名，空格连接续行）。
用法：填好 M 映射（孤儿key -> objPath）后跑；无孤儿时=纯自检（keys/values 数量断言）。
"""
# 完整可跑版本见会话记录；核心断言：len(keys)==len(values)、无重复key、孤儿必有映射。
