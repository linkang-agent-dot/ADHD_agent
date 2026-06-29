# -*- coding: utf-8 -*-
"""多语言邮件内容 csv 生成器 —— iGame「[模版]导入多语言邮件内容.csv」转置格式。
任何补偿/发奖邮件要出可直接导入 iGame 的多语言文案,统一用本模块(别再各自手拼)。

格式(实测自模板,2026-06-29):
  - 语言做【列】,字段做【行】(转置);UTF-8 无 BOM。
  - 第1行=表头: 空格 + 20种语言列名(英语-en/简体中文-cn/繁体中文-zh/法语-fr/...);
  - 第2行=标题, 第3行=内容, 第4行=超链接文本内容, 第5行=超链接地址。
  - 某语言没填=该列留空(iGame 会回退默认语言)。

用法:
  import sys; sys.path.insert(0, r"C:\\Users\\linkang\\.claude\\skills\\bulk-mail-reissue")
  from multilang_mail import write_multilang_mail
  write_multilang_mail("out.csv", {"cn":("标题","正文"),"en":("Title","Body"), ...})
  # 可选 link_text/link_url 给超链接行
mail dict 的 key 用 LANG_CODES 里的码(en/cn/zh/fr/de/ru/jp/kr/sp/id/th/ar/ro/nl/tr/po/it/vi/fa/pls)。
"""
import csv, io

LANG_HDR = ["", "英语-en", "简体中文-cn", "繁体中文-zh", "法语-fr", "德语-de", "俄语-ru",
            "日语-jp", "韩语-kr", "西班牙语-sp", "印度尼西亚语-id", "泰语-th", "阿拉伯语-ar",
            "罗马尼亚语-ro", "荷兰语-nl", "土耳其语-tr", "葡萄牙语-po", "意大利语-it",
            "越南语-vi", "波斯语-fa", "波兰语-pls"]
LANG_CODES = ["en", "cn", "zh", "fr", "de", "ru", "jp", "kr", "sp", "id", "th", "ar",
              "ro", "nl", "tr", "po", "it", "vi", "fa", "pls"]

def write_multilang_mail(path, mail, link_text="", link_url=""):
    """mail = {lang_code: (title, content)};未给的语言列留空。link_* 选填(同文案各语言通用)。"""
    title = ["标题"] + [mail.get(c, ("", ""))[0] for c in LANG_CODES]
    body  = ["内容"] + [mail.get(c, ("", ""))[1] for c in LANG_CODES]
    lt    = ["超链接文本内容"] + [(link_text if link_text else "")] * len(LANG_CODES)
    lu    = ["超链接地址"]     + [(link_url  if link_url  else "")] * len(LANG_CODES)
    # 用 StringIO 写后去掉尾部 CRLF —— 必须无结尾空行,否则 iGame 导入把尾部空行当多一行而失败(2026-06-29实测)
    buf = io.StringIO()
    csv.writer(buf).writerows([LANG_HDR, title, body, lt, lu])
    data = buf.getvalue()
    if data.endswith("\r\n"): data = data[:-2]
    elif data.endswith("\n"): data = data[:-1]
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(data)
    return path
