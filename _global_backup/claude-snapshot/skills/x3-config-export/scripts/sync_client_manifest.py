#!/usr/bin/env python
"""本地导表→热更本地服时,把 temp_dev 导出的新 MD5 选择性同步进 client manifest。

为什么需要:ReloadGameServer 靠 client 的 AllTableDataMd5.txt 清单 diff 决定重载哪些表。
只 cp 新 .bytes 不更新 manifest → 清单没变 → `0 tables reloaded`(改动不生效)。
本脚本只更新「你实际 cp 过去的那几张表」的 MD5 行,不整份覆盖
(整份覆盖会把没 cp 的表也标成已变,ReloadGameServer 拿 client 旧 bytes reload→MD5 mismatch)。

坑:temp_dev manifest 用反斜杠 `i18n\\zh.bytes`,client manifest 用正斜杠 `i18n/zh.bytes`
   → 归一化 key 比对,保留 client 原行格式只换 md5。

用法:
  python sync_client_manifest.py i18n ActvOnline.bytes Pack.bytes
    参数 = 要同步的表(basename 或前缀)。`i18n` = 全部 i18n/*.bytes;
    `ActvOnline.bytes` = 精确匹配;末尾不带 .bytes 当前缀。
可选环境变量覆盖默认路径:
  SRC_MANIFEST(默认 C:\\x3\\gdconfig\\temp_dev\\ProtoGen\\AllTableDataMd5.txt)
  DST_MANIFEST(默认 C:\\x3-project\\client\\Assets\\Res\\Config\\ProtoGen\\AllTableDataMd5.txt)
"""
import os, sys

BS = chr(92)
SRC = os.environ.get("SRC_MANIFEST", r"C:\x3\gdconfig\temp_dev\ProtoGen\AllTableDataMd5.txt")
DST = os.environ.get("DST_MANIFEST", r"C:\x3-project\client\Assets\Res\Config\ProtoGen\AllTableDataMd5.txt")


def norm(k):
    return k.strip().replace(BS, "/")


def main(patterns):
    if not patterns:
        print("用法: python sync_client_manifest.py <表名/前缀> [...]  (如 i18n ActvOnline.bytes)")
        return 2
    newmd5 = {}
    for ln in open(SRC, encoding="utf-8"):
        if ":" not in ln:
            continue
        k, v = ln.rsplit(":", 1)
        newmd5[norm(k)] = v.strip()

    def is_target(k):
        for p in patterns:
            if k == p or k.startswith(p if p.endswith("/") else p + "/") or (not p.endswith(".bytes") and k.startswith(p)):
                return True
        return False

    out, changed = [], []
    for ln in open(DST, encoding="utf-8"):
        if ":" in ln:
            k, v = ln.rsplit(":", 1)
            kk = norm(k)
            if is_target(kk) and kk in newmd5 and v.strip() != newmd5[kk]:
                out.append("%s : %s\n" % (k.rstrip(), newmd5[kk]))
                changed.append(kk)
                continue
        out.append(ln)
    open(DST, "w", encoding="utf-8", newline="").writelines(out)
    print("manifest 更新行数:", len(changed))
    for c in changed:
        print("  ", c)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
