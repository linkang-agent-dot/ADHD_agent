"""全面体检所有 DisplayKey 注册文件（Path_* / Display_*）。

检查项：
1. 冲突标记残留（会让 Unity YAML 解析整个文件失败 → 该文件所有 DK 失效）
2. keys / values / objPath 三段条目数一致（不一致=有条目残缺）
3. YAML 头部结构完整（%YAML / MonoBehaviour / m_Script）
4. 文件大小异常（0 字节或极小）
"""
import os, re, sys, glob

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

DIRS = [
    r'C:\x3-project\client\Assets\Res\Config\DisplayKey',
    r'C:\x3-project\client\Assets\Editor\Config\DisplayKey',
]

bad = []
total = 0
for d in DIRS:
    for f in sorted(glob.glob(os.path.join(d, '*.asset'))):
        total += 1
        name = os.path.basename(f)
        size = os.path.getsize(f)
        try:
            s = open(f, encoding='utf-8').read()
        except Exception as e:
            bad.append((name, f'读取失败: {e}'))
            continue

        issues = []
        # 1 冲突标记
        marks = len(re.findall(r'^(<<<<<<< |>>>>>>> |=======)$', s, re.M))
        if marks:
            issues.append(f'冲突标记 {marks} 处')
        # 2 结构
        if not s.startswith('%YAML'):
            issues.append('缺 YAML 头')
        if 'm_Script:' not in s:
            issues.append('缺 m_Script')
        # 3 条目一致性（仅 Path_*）
        if name.startswith('Path_'):
            k = len(re.findall(r'\n    - DK_', s))
            v = len(re.findall(r'\n    - key: ', s))
            o = len(re.findall(r'\n      objPath: ', s))
            if not (k == v == o):
                issues.append(f'条目不一致 keys={k}/values={v}/objPath={o}')
        else:
            k = len(re.findall(r'\n  - key: ', s))
            g = len(re.findall(r'\n    guid: ', s))
            if k != g:
                issues.append(f'条目不一致 key={k}/guid={g}')
        # 4 大小
        if size < 200:
            issues.append(f'文件过小 {size}B')

        if issues:
            bad.append((name, '; '.join(issues)))

print(f'扫描 {total} 个 DK 注册文件')
if bad:
    print(f'\n🔴 发现 {len(bad)} 个有问题：')
    for n, i in bad:
        print(f'  {n:42s} {i}')
else:
    print('\n✅ 全部正常（无冲突标记、结构完整、条目数一致）')
