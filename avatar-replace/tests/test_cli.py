from core.cli import build_parser


def test_parser_routes():
    p = build_parser()
    a = p.parse_args(["annotate", "v.mp4"])
    assert a.cmd == "annotate" and a.video == "v.mp4"
    a = p.parse_args(["confirm", "jid", "--all"])
    assert a.cmd == "confirm" and a.all
    a = p.parse_args(["confirm", "jid", "--spans", "0,2"])
    assert a.spans == "0,2"
    a = p.parse_args(["run", "jid", "--avatar", "girl_a"])
    assert a.avatar == "girl_a"
    a = p.parse_args(["status", "jid"])
    assert a.cmd == "status"
