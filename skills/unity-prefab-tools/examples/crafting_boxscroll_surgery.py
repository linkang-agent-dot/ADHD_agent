# -*- coding: utf-8 -*-
r"""
开箱(UIActvCrafting) 阶段奖励条加横滑 —— 把大富翁(UIActvVoyage) 07-27 那次改造原样搬过来。

背景/根因：
  两个界面的 OtherReward 块本来同源（Detailed/BoxGroup/Slider/Item 四个 RT 的 fileID 完全相同），
  大富翁在 b396fca6f1e 做了「套 TFWScrollRect + Slider 挪进 BoxGroup + content 按项数定宽」，
  开箱没跟 → 11 档被 HorizontalLayoutGroup(ForceExpandWidth=1) 平分进固定 920px，挤成一团且无法滚动。

本脚本只做 prefab 侧；配套还需改两个 .cs（见文件末尾 TODO 打印）。

⚠️ 必须在 Unity 里打开 prefab 复验后才能信 —— 脚本只保证 YAML 结构自洽。
"""
import io, os, re, shutil, sys

CRAFT = r'C:\x3-project\client\Assets\Res\UI\Prefab\Activity\UIActvCrafting.prefab'
VOY   = r'C:\x3-project\client\Assets\Res\UI\Prefab\ActvVoyage\UIActvVoyage.prefab'

# 两 prefab 共有的 fileID（同源拷贝）
RT_DETAILED = '2318320025297968609'
RT_BOXGROUP = '5338486777929857815'
RT_SLIDER   = '4754917410839098701'
RT_ITEM     = '5150322922942693672'

# 大富翁 BoxScroll 的 6 个 doc（源）
VOY_BS = ['81720260728000001', '81720260728000002', '81720260728000003',
          '81720260728000004', '81720260728000006', '81720260728000007', '81720260728000008']
# 开箱侧新 fileID：同样的可读方案，日期换 20260729
IDMAP = {v: v.replace('20260728', '20260729') for v in VOY_BS}
BS_GO = IDMAP['81720260728000001']
BS_RT = IDMAP['81720260728000002']


def split_docs(text):
    parts = re.split(r'(^--- !u!\d+ &\d+\n)', text, flags=re.M)
    head = parts[0]
    docs = []
    for i in range(1, len(parts), 2):
        m = re.match(r'--- !u!(\d+) &(\d+)\n', parts[i])
        docs.append([int(m.group(1)), m.group(2), parts[i], parts[i + 1]])
    return head, docs


def find(docs, fid):
    for d in docs:
        if d[1] == fid:
            return d
    raise SystemExit(f'!! 找不到 doc &{fid}')


def set_field(body, key, value):
    """替换 `  key: {...}` 或 `  key: xxx` 这一行的值"""
    pat = re.compile(r'^(\s*' + re.escape(key) + r': )(.*)$', re.M)
    if not pat.search(body):
        raise SystemExit(f'!! 字段 {key} 不存在')
    return pat.sub(lambda m: m.group(1) + value, body, count=1)


def set_children(body, fids):
    """重写 m_Children 列表"""
    lines = '\n'.join(f'  - {{fileID: {f}}}' for f in fids)
    new = 'm_Children:\n' + lines + '\n  m_Father:' if fids else 'm_Children: []\n  m_Father:'
    return re.sub(r'm_Children:[\s\S]*?\n  m_Father:', new, body, count=1)


def main(dry):
    craft = io.open(CRAFT, encoding='utf-8').read()
    voy   = io.open(VOY,   encoding='utf-8').read()
    if 'BoxScroll' in craft:
        raise SystemExit('!! 开箱 prefab 里已有 BoxScroll，脚本已跑过？中止')
    nl = '\r\n' if '\r\n' in craft[:2000] else '\n'
    craft_n = craft.replace('\r\n', '\n')
    voy_n   = voy.replace('\r\n', '\n')

    head, docs = split_docs(craft_n)
    _, vdocs   = split_docs(voy_n)

    # ---------- 1. 克隆 BoxScroll 六件套 ----------
    new_docs = []
    for src in VOY_BS:
        cls, _, hdr, body = find(vdocs, src)
        for old, new in IDMAP.items():           # 内部互指的 fileID 一并重映射
            body = body.replace(old, new)
            hdr  = hdr.replace(old, new)
        # ScrollRect 的 content / RectTransform 的 father 用开箱侧真实 ID（本来就同号，稳妥起见显式设）
        new_docs.append([cls, IDMAP[src], hdr, body])
    print(f'[1/5] 克隆 BoxScroll 六件套 -> 新 fileID {BS_GO}..')

    # BoxScroll 的 RectTransform：父=Detailed，子=[BoxGroup]
    bs_rt = [d for d in new_docs if d[1] == BS_RT][0]
    bs_rt[3] = set_children(bs_rt[3], [RT_BOXGROUP])
    bs_rt[3] = set_field(bs_rt[3], 'm_Father', '{fileID: %s}' % RT_DETAILED)

    # ---------- 2. Detailed：子列表 [Slider, BoxGroup] -> [BoxScroll] ----------
    d = find(docs, RT_DETAILED)
    before = re.findall(r'\{fileID: (\d+)\}', d[3].split('m_Children:')[1].split('m_Father:')[0])
    d[3] = set_children(d[3], [BS_RT])
    print(f'[2/5] Detailed 子物体 {before} -> [{BS_RT}]')

    # ---------- 3. BoxGroup：父改 BoxScroll，子=[Slider, Item]，锚点改不拉伸 ----------
    d = find(docs, RT_BOXGROUP)
    d[3] = set_field(d[3], 'm_Father', '{fileID: %s}' % BS_RT)
    d[3] = set_children(d[3], [RT_SLIDER, RT_ITEM])
    d[3] = set_field(d[3], 'm_AnchorMin', '{x: 0, y: 0.5}')
    d[3] = set_field(d[3], 'm_AnchorMax', '{x: 0, y: 0.5}')       # 不拉伸 -> 宽度由代码设
    d[3] = set_field(d[3], 'm_AnchoredPosition', '{x: 0, y: -44}')
    d[3] = set_field(d[3], 'm_SizeDelta', '{x: 0, y: 52}')
    # 🔴 pivot.x 必须 0：pivot 0.5 时 sizeDelta=count*120 会以锚点为中心向左右两边撑开，
    #    左半边跑到视口左边界外被裁 → 前一半档位直接看不见。横滑列表的 content 一律左对齐 pivot。
    d[3] = set_field(d[3], 'm_Pivot', '{x: 0, y: 0.5}')
    # HLG 参数对齐大富翁：ForceExpandWidth=1 会把子物体平分容器宽(项被压扁)；Alignment 也要跟着左对齐
    d[3] = set_field(d[3], 'm_ChildForceExpandWidth', '0') if 'm_ChildForceExpandWidth' in d[3] else d[3]
    print('[3/5] BoxGroup 移入 BoxScroll，锚点改不拉伸 + pivot.x=0（宽度交给代码）')

    # ---------- 4. Slider：从 Detailed 移入 BoxGroup ----------
    d = find(docs, RT_SLIDER)
    d[3] = set_field(d[3], 'm_Father', '{fileID: %s}' % RT_BOXGROUP)
    d[3] = set_field(d[3], 'm_AnchoredPosition', '{x: 0, y: 0}')
    d[3] = set_field(d[3], 'm_SizeDelta', '{x: 0, y: 52}')
    print('[4/5] Slider 移入 BoxGroup（否则条滚了进度轨不滚会脱节）')
    print('      ⚠️ Slider 还必须补 LayoutElement(m_IgnoreLayout=1)，否则会被 HLG 当成第一个布局项排进去，'
          '进度条整条消失（07-29 实测）。BoxGroup 的 HLG 另需 ForceExpandWidth=0 / ChildAlignment=3。')

    # ---------- 5. Item：宽度 0 -> 120（与大富翁一致，代码按此定 content 宽）----------
    d = find(docs, RT_ITEM)
    d[3] = set_field(d[3], 'm_SizeDelta', '{x: 120, y: 52}')
    d[3] = set_field(d[3], 'm_AnchoredPosition', '{x: 60, y: -26}')
    d[3] = set_field(d[3], 'm_AnchorMin', '{x: 0, y: 1}')
    d[3] = set_field(d[3], 'm_AnchorMax', '{x: 0, y: 1}')
    print('[5/5] Item 宽度 0 -> 120（原来靠 ForceExpandWidth 平分，是挤在一起的根因）')

    out = head + ''.join(h + b for _, _, h, b in docs) + ''.join(h + b for _, _, h, b in new_docs)
    if dry:
        print('\n[dry-run] 未写盘')
        return
    io.open(CRAFT, 'w', encoding='utf-8', newline=nl).write(out)
    print('\n✅ prefab 已改写')
    print('\n' + '=' * 60)
    print('TODO 配套代码改动（本脚本不做）：')
    print('  A. Auto_UIActvCrafting.cs 三条路径插入 BoxScroll/：')
    print('     mGoItem                        .../Detailed/BoxScroll/BoxGroup/Item')
    print('     mSliderSlider                  .../Detailed/BoxScroll/BoxGroup/Slider')
    print('     mChildGroupControllerBoxGroup   -> 删除（改用 UIWidgetList）')
    print('  B. UIActvCrafting.cs 照 UIActvVoyage.cs 改：')
    print('     - ChildGroupController -> WidgetContainer.AddList<UIActvCraftingBoxSlotItem>')
    print('       (Slider 进了 BoxGroup 会被 ChildGroupController 当成一项)')
    print('     - ShowBoxItemInfos() 末尾补 boxContent.sizeDelta = count * 120f')
    print('=' * 60)


if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    main('--dry-run' in sys.argv)
