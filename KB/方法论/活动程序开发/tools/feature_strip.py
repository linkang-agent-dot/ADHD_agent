# -*- coding: utf-8 -*-
"""feature_strip.py —— 从「共享注册文件 / 生成代码」里结构化摘除某个功能的全部痕迹。

用途：整体撤除一个 X3 功能（活动/模块）时，绝大部分文件可以直接 `git apply -R` 补丁回退，
但下面这几类会打不上补丁，必须按结构摘块：
  - 生成的 protobuf C#（Protos/activity.cs、CSSharedHotfix/Common/Protos/activity.cs）
  - activity.proto / msgid.def
  - 各种「追加式注册表」（ActivityConst / MetaConst / ErrCode / SysOpReason / TEventType）
原因：合并 dev 后往往跑过一次 proto/DK 重生成（如 x3-project 328ef08170f），
      文件被重排/让号，补丁的上下文全对不上。

用法：
    python feature_strip.py --token FlashSale --file <文件路径> [--kind csharp|proto|lines] ...

  --kind csharp  按 C# 结构摘：顶层 `public sealed partial class <Token>*` 整块（含 /// 注释与 [特性]）、
                 `public <Token>Data <token>Data { get; set; }` 属性、Encode 的 if 块、Decode 的 case 块、
                 复位行、ProtoBuf.PType.RegisterType 行
  --kind proto   按 proto 结构摘：`message <Token>*{...}` 整块 + 引用该类型的字段行
  --kind lines   纯按行删（msgid.def / 各种常量表），带 --eat-blank 时连带吃掉前面的空行

自带三道校验：删完必须(1)零残留 token (2)大括号增删配平 (3)输出 .new 供 diff 复核（纯删除、零新增）。
校验不过 → 退出码 1，不要盲信结果。

沉淀来源：2026-07-28 X3 马戏节限时抢购推倒重做（清除提交 973997a92ce）。
配套手法见同目录 `X3_功能整体撤除手法_代码prefab全清.md`。
"""
import re
import os
import sys
import argparse


def brace_end(lines, i):
    """i = 块起始(声明行)；找其后第一个 '{'，配平到闭合行，返回闭合行下标。"""
    j = i
    while "{" not in lines[j]:
        j += 1
        if j - i > 6:
            raise RuntimeError(f"找不到起始花括号 @ 行{i+1}: {lines[i][:80]}")
    depth = 0
    while j < len(lines):
        depth += lines[j].count("{") - lines[j].count("}")
        if depth == 0:
            return j
        j += 1
    raise RuntimeError(f"花括号未配平 @ 行{i+1}")


def back_over(lines, i, prefixes):
    while i > 0 and any(lines[i - 1].strip().startswith(p) for p in prefixes):
        i -= 1
    return i


def eat_blank_before(lines, i):
    return i - 1 if i > 0 and lines[i - 1].strip() == "" else i


def eat_blank_after(lines, k):
    return k + 1 if k + 1 < len(lines) and lines[k + 1].strip() == "" else k


def cuts_csharp(lines, token):
    """token 例: 'FlashSale' -> 类名 FlashSale*/ActivityFlashSaleData, 字段 flashSaleData"""
    field = token[0].lower() + token[1:] + "Data"          # flashSaleData
    data_cls = "Activity" + token + "Data"                  # ActivityFlashSaleData
    cuts = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        # 顶层消息类整块
        if re.match(rf"^public sealed partial class \w*{token}\w*\b", s):
            a = eat_blank_before(lines, back_over(lines, i, ("///", "[")))
            cuts.append((a, eat_blank_after(lines, brace_end(lines, i))))
        # 宿主消息里的字段属性（含 /// 注释）
        elif re.match(rf"^public {data_cls} {field} \{{ get; set; \}}$", s):
            cuts.append((eat_blank_before(lines, back_over(lines, i, ("///",))), i))
        # Encode 的 if 块（取最外层：前一行是空行）
        elif s == f"if ({field} != null)" and i > 0 and lines[i - 1].strip() == "":
            cuts.append((i - 1, eat_blank_after(lines, brace_end(lines, i))))
        # Decode 的 case 块
        elif s == f"{field} = new cspb.{data_cls}();":
            a = i
            while not re.match(r"^case \d+:$", lines[a].strip()):
                a -= 1
                if i - a > 4:
                    raise RuntimeError(f"找不到 case 头 @ 行{i+1}")
            b = brace_end(lines, a)
            if lines[b + 1].strip() == "break;":
                b += 1
            cuts.append((a, b))
        # 复位行
        elif s == f"{field} = null;":
            cuts.append((eat_blank_before(lines, i), i))
        # 类型注册行
        elif s.startswith('ProtoBuf.PType.RegisterType("cspb.') and token.lower() in s.lower():
            cuts.append((i, i))
    return cuts


def cuts_proto(lines, token):
    data_cls = "Activity" + token + "Data"
    cuts = []
    for i, ln in enumerate(lines):
        s = ln.strip()
        if re.match(rf"^message \w*{token}\w*\s*\{{", s):
            cuts.append((eat_blank_before(lines, back_over(lines, i, ("//",))),
                         brace_end(lines, i)))
        elif re.match(rf"^{data_cls} \w+ = \d+;", s):
            cuts.append((i, i))
    return cuts


def cuts_lines(lines, pattern, eat_blank):
    return [(eat_blank_before(lines, i) if eat_blank else i, i)
            for i, ln in enumerate(lines) if re.search(pattern, ln)]


def apply_cuts(lines, cuts):
    merged = []
    for a, b in sorted(cuts):
        if merged and a <= merged[-1][1] + 1:
            merged[-1] = (merged[-1][0], max(merged[-1][1], b))
        else:
            merged.append((a, b))
    out, removed = list(lines), 0
    for a, b in reversed(merged):
        removed += b - a + 1
        del out[a:b + 1]
    return out, removed, merged


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--token", required=True, help="功能标识，如 FlashSale")
    ap.add_argument("--file", action="append", required=True,
                    help="文件路径，格式 <kind>:<path>，kind ∈ csharp|proto|lines")
    ap.add_argument("--pattern", default=None, help="kind=lines 时的匹配正则，默认用 token")
    ap.add_argument("--eat-blank", action="store_true", help="kind=lines 时连带删前置空行")
    ap.add_argument("--inplace", action="store_true", help="直接改源文件（默认只写 .new）")
    args = ap.parse_args()

    tok_re = re.compile(re.escape(args.token), re.I)
    pattern = args.pattern or args.token
    ok = True

    for spec in args.file:
        kind, _, path = spec.partition(":")
        if not path:
            kind, path = "lines", spec
        raw = open(path, "rb").read()
        text = raw.decode("utf-8", "surrogateescape")
        lines = text.split("\n")
        ob, cb = text.count("{"), text.count("}")

        if kind == "csharp":
            cuts = cuts_csharp(lines, args.token)
        elif kind == "proto":
            cuts = cuts_proto(lines, args.token)
        else:
            cuts = cuts_lines(lines, pattern, args.eat_blank)

        out, removed, merged = apply_cuts(lines, cuts)
        new = "\n".join(out)
        nob, ncb = new.count("{"), new.count("}")
        left = [l for l in out if tok_re.search(l)]

        status = "OK"
        if left:
            status = f"!! 仍残留 {len(left)} 行"
            ok = False
        if (ob - nob) != (cb - ncb):
            status += f" !! 花括号不配平(删了 {ob-nob} 个 '{{' / {cb-ncb} 个 '}}')"
            ok = False

        dest = path if args.inplace else path + ".new"
        open(dest, "wb").write(new.encode("utf-8", "surrogateescape"))
        print(f"{os.path.basename(path):26s} 删 {removed:5d} 行 / {len(merged):2d} 块  "
              f"{{{ob}->{nob}  }}{cb}->{ncb}  {status}  -> {os.path.basename(dest)}")
        for l in left[:5]:
            print("     残留:", l.strip()[:100])

    if not ok:
        print("\n校验未通过，不要直接用结果。")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
