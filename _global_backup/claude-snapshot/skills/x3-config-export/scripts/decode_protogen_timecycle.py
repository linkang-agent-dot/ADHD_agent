#!/usr/bin/env python3
"""
decode_protogen_timecycle.py — 不启动 Unity，直接解码客户端/服务端 ProtoGen TimeCycle.bytes，
读出指定 TimeCycle ID 的运行时字段（TriggerType/StartTime/Duration/CycleType/ReOpenTime...）。

用来验证 gdconfig 改了 TimeCycle 表后，导表产物(.bytes)里的运行时值对不对
（导表会把 "26d 00:00:01" / "7 2 00:00:01" 这类人读值转成毫秒，需回换核对）。

CTimeCycleCfg proto 字段号（2026-07-15 实测，见 client/Assets/Res/Config/Proto/TimeCycle.proto）：
  1 ID / 3 TriggerType / 4 StartTime(string) / 5 DurationType / 6 Duration(string)
  7 CycleType / 8 ReOpenTime(string) / 9 EndTimeType / 10 EndTime(string) / 11 NeedCycle(bool)
外层 CTimeCycle.Configs = map<int,CTimeCycleCfg> at field2；每个 cfg 以 0x08+varint(ID) 开头。

毫秒回换速查：26d00:00:01=2246401000 / 5d23h59m59s=518399000 / 48h=172800000 / 21d=1814400000。
TT=6 "第N周周M" 导表按 (N-1)*7+M 天线性转毫秒(仅为占位)，真实开窗由运行时按开服周历重算到真正的周M。

用法：
  python decode_protogen_timecycle.py <TimeCycle.bytes 路径> <ID> [<ID> ...]
例：
  python decode_protogen_timecycle.py client/Assets/Res/Config/ProtoGen/TimeCycle.bytes 1207 1208 1209 10301
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


def rd(buf: bytes, p: int):
    r = 0
    s = 0
    while True:
        c = buf[p]
        p += 1
        r |= (c & 0x7F) << s
        s += 7
        if not c & 0x80:
            return r, p


def parse_cfg(data: bytes, p: int) -> dict:
    """从 CTimeCycleCfg 起点(指向 0x08)顺序解字段，遇未知 tag 停。"""
    f = {}
    STR = {0x22: "StartTime", 0x32: "Duration", 0x42: "ReOpenTime", 0x52: "EndTime"}
    INT = {0x08: "ID", 0x18: "TriggerType", 0x28: "DurationType",
           0x38: "CycleType", 0x48: "EndTimeType", 0x58: "NeedCycle"}
    while p < len(data):
        tag = data[p]
        if tag in INT:
            v, p = rd(data, p + 1)
            f[INT[tag]] = v
        elif tag in STR:
            ln, p = rd(data, p + 1)
            f[STR[tag]] = data[p:p + ln].decode("utf8", "replace")
            p += ln
        else:
            break
    return f


def find_cfg(data: bytes, tid: int):
    pat = b"\x08" + enc_varint(tid)
    for m in re.finditer(re.escape(pat), data):
        f = parse_cfg(data, m.start())
        if f.get("ID") == tid and "TriggerType" in f and "Duration" in f:
            return f
    return None


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    path = sys.argv[1]
    data = open(path, "rb").read()
    print(f"file={path} size={len(data)}")
    for tid in (int(x) for x in sys.argv[2:]):
        print(f"{tid} -> {find_cfg(data, tid)}")


if __name__ == "__main__":
    main()
