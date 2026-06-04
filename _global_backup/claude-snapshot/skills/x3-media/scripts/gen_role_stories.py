"""
从 i18n cn.bytes 解析角色背景故事，写到 asset_library/roles/Role_F_N.story.md

设计：见 docs/plans/2026-05-29-card-gallery-role-driven-design.md (P8)
        以及 _quick/asset_library/roles/_HOW_TO_GENERATE_story.md

用法（单角色模式，DesignDeck 调用）：
  python gen_role_stories.py \
    --cn-bytes "E:\x3git\x3-project\client\Assets\Res\Config\ProtoGen\i18n\cn.bytes" \
    --roles-dir "E:\AIProgram\A-X3Gxd\_quick\asset_library\roles" \
    --single-role Role_F_23

用法（批量模式，刷新所有有立绘的角色）：
  python gen_role_stories.py \
    --cn-bytes "..." \
    --roles-dir "..."

输出格式（stdout 每行一段 JSON，便于主进程解析进度）：
  {"stage": "read_bytes", "msg": "读取 cn.bytes (3.5MB)..."}
  {"stage": "extract", "msg": "提取 77 个 hero 文本", "count": 77}
  {"stage": "write", "msg": "写 Role_F_23.story.md", "role_id": "Role_F_23"}
  {"stage": "sweep", "msg": "sweep \\n 字面 12 处", "count": 12}
  {"stage": "done", "msg": "完成", "written": ["Role_F_23"]}
  {"stage": "error", "msg": "...原因..."}
"""
import argparse
import glob
import json
import os
import re
import sys
from pathlib import Path


def log(stage: str, msg: str, **extra):
    """发一行 JSON 到 stdout，主进程逐行解析做进度条。"""
    payload = {"stage": stage, "msg": msg}
    payload.update(extra)
    print(json.dumps(payload, ensure_ascii=False), flush=True)


def read_varint(b: bytes, p: int):
    """protobuf varint 读法（值, 下一位）"""
    n, shift = 0, 0
    while p < len(b):
        x = b[p]
        n |= (x & 0x7F) << shift
        p += 1
        if x < 0x80:
            return n, p
        shift += 7
    return n, p


def extract_heroes(cn_bytes_path: str) -> dict:
    """从 cn.bytes 提取所有 hero 文本，按 hid → {field → str} 返回。"""
    data = open(cn_bytes_path, "rb").read()
    log("read_bytes", f"读取 cn.bytes ({len(data) // 1024} KB)", size=len(data))

    # protobuf map entry 结构：tag(0x0a) <len> key  tag(0x12) <varint len> utf8 value
    pat = re.compile(rb"TXT_Hero_(Name|Title|Story|Story2|Story3|Words)_(\d+)")

    hero_data: dict = {}
    for m in pat.finditer(data):
        field, hid = m.group(1).decode(), int(m.group(2))
        pos = m.end()
        if pos < len(data) and data[pos] == 0x12:  # value tag = field 2 string
            ln, p2 = read_varint(data, pos + 1)
            try:
                s = data[p2 : p2 + ln].decode("utf-8")
                # 含中文才接受
                if any("一" <= c <= "鿿" for c in s):
                    hero_data.setdefault(hid, {})[field] = s
            except UnicodeDecodeError:
                pass

    log("extract", f"提取 {len(hero_data)} 个 hero 文本", count=len(hero_data))
    return hero_data


def build_story_md(hid: int, n: int, d: dict) -> str:
    """组装 Role_F_N.story.md 内容。"""
    name = d.get("Name", "?")
    title = d.get("Title", "?")
    lines = [
        f"# Role_F_{n} · {name} · {title}",
        "",
        f"**Hero ID**：`{hid}` (本地化 key: TXT_Hero_Story_{hid})",
        "",
        "## 背景故事",
        "",
        d["Story"],
    ]
    if d.get("Story2"):
        lines += ["", "## 背景故事 2（好感解锁）", "", d["Story2"]]
    if d.get("Story3"):
        lines += ["", "## 背景故事 3（好感解锁）", "", d["Story3"]]
    if d.get("Words"):
        lines += ["", "## 角色台词", "", d["Words"]]
    return "\n".join(lines)


def sweep_backslash_n(roles_dir: str, only_files: list | None = None) -> int:
    """字节级 sweep：把 `\\n` 字面（0x5C 0x6E）转成真换行 0x0A。"""
    total = 0
    if only_files is not None:
        targets = only_files
    else:
        targets = glob.glob(str(Path(roles_dir) / "Role_F_*.story.md"))
    for f in targets:
        try:
            raw = open(f, "rb").read()
            c = raw.count(b"\x5c\x6e")
            if c:
                open(f, "wb").write(raw.replace(b"\x5c\x6e", b"\x0a"))
                total += c
        except Exception:
            pass
    return total


def existing_role_ns(roles_dir: str) -> set:
    """扫 roles 目录现有 Role_F_N (主立绘 N 的集合)。"""
    out = set()
    p = Path(roles_dir)
    if not p.is_dir():
        return out
    for f in p.iterdir():
        m = re.match(r"Role_F_(\d+)(_|\.)", f.name)
        if m:
            out.add(int(m.group(1)))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cn-bytes", required=True, help="cn.bytes 文件绝对路径")
    ap.add_argument("--roles-dir", required=True, help="角色资源目录")
    ap.add_argument(
        "--single-role",
        default=None,
        help="只生成单个 Role_F_N（DesignDeck 按角色调用时用）",
    )
    args = ap.parse_args()

    cn_bytes_path = args.cn_bytes
    roles_dir = args.roles_dir

    # 路径校验
    if not os.path.isfile(cn_bytes_path):
        log("error", f"cn.bytes 不存在: {cn_bytes_path}")
        sys.exit(1)
    if not os.path.isdir(roles_dir):
        log("error", f"roles 目录不存在: {roles_dir}")
        sys.exit(1)

    # 解析 cn.bytes
    try:
        hero_data = extract_heroes(cn_bytes_path)
    except Exception as e:
        log("error", f"解析 cn.bytes 失败: {e}")
        sys.exit(2)

    # 只取主英雄段（hid 1001-1999），转换 hid → N = hid - 1000
    candidate = {hid - 1000: d for hid, d in hero_data.items() if 1001 <= hid <= 1999 and d.get("Story")}

    # 单角色模式
    if args.single_role:
        m = re.match(r"^Role_F_(\d+)$", args.single_role)
        if not m:
            log("error", f"非法 single-role: {args.single_role}")
            sys.exit(3)
        n = int(m.group(1))
        if n not in candidate:
            log(
                "error",
                f"cn.bytes 没有 Role_F_{n}（hid={n + 1000}）的 Story 文本，"
                "需等 i18n 补齐才能自动生成 — 也可手写",
            )
            sys.exit(4)
        out_path = Path(roles_dir) / f"Role_F_{n}.story.md"
        log("write", f"写 Role_F_{n}.story.md", role_id=f"Role_F_{n}", path=str(out_path))
        out_path.write_text(
            build_story_md(n + 1000, n, candidate[n]),
            encoding="utf-8",
        )
        # sweep \n 字面 — 只对这一个文件
        swept = sweep_backslash_n(roles_dir, only_files=[str(out_path)])
        log("sweep", f"sweep \\n 字面 {swept} 处", count=swept)
        log("done", "完成", written=[f"Role_F_{n}"])
        return

    # 批量模式：交集（仅为有资源的角色写）
    have_role = existing_role_ns(roles_dir)
    written = []
    for n in sorted(candidate.keys()):
        if n not in have_role:
            continue
        role_id = f"Role_F_{n}"
        out_path = Path(roles_dir) / f"{role_id}.story.md"
        log("write", f"写 {role_id}.story.md", role_id=role_id)
        out_path.write_text(
            build_story_md(n + 1000, n, candidate[n]),
            encoding="utf-8",
        )
        written.append(role_id)

    swept = sweep_backslash_n(roles_dir)
    log("sweep", f"sweep \\n 字面 {swept} 处", count=swept)
    log("done", f"完成，写入 {len(written)} 个", written=written)


if __name__ == "__main__":
    main()
