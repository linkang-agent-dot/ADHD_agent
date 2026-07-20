#!/usr/bin/env python3
"""
decode_protogen_reward.py — 不启动 Unity，直接解码客户端 ProtoGen Reward.bytes，
读出指定 RewardID 的 (ItemID, count) 列表，用来验证配置改动是否真的到达客户端 build。

背景：X3 客户端礼包/奖励四格「展示」由客户端本机 ProtoGen 字节驱动（不是服务端）。
改了 gdconfig 的 Reward 表后，客户端要看到新内容，必须导表把新 Reward.bytes 提交进 x3-project
并被客户端拉取+Unity 重导入。本脚本直接读二进制确认，避免靠"感觉/时间戳"猜。

Reward.bytes 每行记录字段（protobuf，经 2026-07-15 实测）：
  field1(0x08)=行ID(A列)  field2(0x10)=RewardID  field4(0x20)=ItemID  count 在 field9(0x4a,len前缀)
一个 RewardID 通常对应多行（=四格里的每一格一行）。

用法：
  python decode_protogen_reward.py <Reward.bytes 路径> <RewardID> [<RewardID> ...]
例：
  python decode_protogen_reward.py client/Assets/Res/Config/ProtoGen/Reward.bytes 15900502 15900503 15900504

同理可改字段号解其它 ProtoGen 表；核心是「varint 编码目标ID + 正则找co-occurrence + 顺序解字段」。
"""
import re
import sys


def enc_varint(n: int) -> bytes:
    b = bytearray()
    while True:
        x = n & 0x7F
        n >>= 7
        if n:
            b.append(x | 0x80)
        else:
            b.append(x)
            break
    return bytes(b)


def read_varint(buf: bytes):
    r = 0
    s = 0
    for i, c in enumerate(buf):
        r |= (c & 0x7F) << s
        s += 7
        if not c & 0x80:
            return r, i + 1
    return r, len(buf)


def decode_reward(data: bytes, reward_id: int):
    """返回该 RewardID 去重后的 [(itemID, count_or_None), ...]"""
    rv = enc_varint(reward_id)
    seen = set()
    rows = []
    for m in re.finditer(re.escape(b"\x10" + rv), data):  # field2 = RewardID
        i = m.start()
        k = i + 1 + len(rv)
        items = []
        while k < i + 48 and k < len(data):
            tag = data[k]
            if tag == 0x20:                      # field4 = ItemID (varint)
                val, ln = read_varint(data[k + 1:k + 6]); items.append(("item", val)); k += 1 + ln
            elif tag in (0x18, 0x28):            # 其它 varint 字段跳过
                _, ln = read_varint(data[k + 1:k + 6]); k += 1 + ln
            elif tag == 0x4a:                    # count (length-delimited, 常见1字节)
                ln = data[k + 1]
                cnt = data[k + 2] if ln == 1 else read_varint(data[k + 2:k + 2 + ln])[0]
                items.append(("count", cnt)); k += 2 + ln
            else:
                break
        key = tuple(items)
        if key not in seen:
            seen.add(key)
            rows.append(items)
    return rows


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    ids = [int(x) for x in sys.argv[2:]]
    data = open(path, "rb").read()
    print(f"file={path} size={len(data)}")
    for rid in ids:
        rows = decode_reward(data, rid)
        print(f"\n=== RewardID {rid} ===")
        if not rows:
            print("  (未找到该 RewardID)")
        for r in rows:
            print("  ", r)


if __name__ == "__main__":
    main()
