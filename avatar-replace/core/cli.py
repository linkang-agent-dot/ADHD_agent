"""命令行入口：annotate → confirm → run → status。

python -m core.cli annotate <video>              建任务+打轴
python -m core.cli confirm <job_id> --all        全确认（或 --spans 0,2 选择性）
python -m core.cli run <job_id> --avatar <名>    切段+替换+拼回
python -m core.cli status <job_id>               查看状态
"""
import argparse
import json
import sys
from pathlib import Path

from core.config import load_config
from core.pipeline import Job

ROOT = Path(__file__).resolve().parent.parent
JOBS = ROOT / "jobs"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="avatar-replace")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("annotate", help="建任务+打轴")
    a.add_argument("video")
    c = sub.add_parser("confirm", help="确认待替换时段")
    c.add_argument("job_id")
    c.add_argument("--all", action="store_true", help="确认全部时段")
    c.add_argument("--spans", default="", help="逗号分隔的时段序号，如 0,2")
    r = sub.add_parser("run", help="切段+替换+拼回")
    r.add_argument("job_id")
    r.add_argument("--avatar", required=True, help="avatars/ 下的形象目录名")
    s = sub.add_parser("status", help="查看任务状态")
    s.add_argument("job_id")
    return p


def _provider(cfg):
    from core.providers.volc import VolcProvider
    return VolcProvider(cfg.ark)


def _load_job(job_id: str, cfg) -> Job:
    jdir = JOBS / job_id
    if not (jdir / "job.json").exists():
        sys.exit(f"job {job_id} 不存在（jobs/ 下无此目录）")
    return Job.load(jdir, cfg)


def main(argv=None):
    # Windows 控制台可能是 GBK，中文 JSON 直接 print 会 UnicodeEncodeError
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    args = build_parser().parse_args(argv)
    cfg_path = ROOT / "config.yaml"
    if not cfg_path.exists():
        sys.exit("缺少 config.yaml：先 cp config.example.yaml config.yaml 并填写模型 ID")
    cfg = load_config(cfg_path,
                      require_key=(args.cmd in ("annotate", "run")))
    if args.cmd == "annotate":
        job = Job.create(Path(args.video), JOBS, cfg)
        job.annotate(_provider(cfg))
        print(f"job: {job.dir.name}")
        print(json.dumps(job.timeline, ensure_ascii=False, indent=2))
    elif args.cmd == "confirm":
        job = _load_job(args.job_id, cfg)
        try:
            picks = set(range(len(job.timeline))) if args.all else \
                    {int(i) for i in args.spans.split(",") if i.strip()}
        except ValueError:
            sys.exit(f"--spans 需为逗号分隔整数，收到: {args.spans}")
        for i, t in enumerate(job.timeline):
            t["confirmed"] = i in picks
        try:
            job.confirm()
        except ValueError as e:
            sys.exit(str(e))
        print(f"confirmed: {sorted(picks)}")
    elif args.cmd == "run":
        job = _load_job(args.job_id, cfg)
        avatar_dir = ROOT / "avatars" / args.avatar
        refs = sorted(avatar_dir.glob("*.png")) + sorted(avatar_dir.glob("*.jpg"))
        if not refs:
            sys.exit(f"形象 {args.avatar} 无参考图（avatars/{args.avatar}/*.png|jpg）")
        try:
            job.run(_provider(cfg), avatar_refs=refs)
        except ValueError as e:
            sys.exit(str(e))
        print(f"done: {job._meta['final']}")
    elif args.cmd == "status":
        job = _load_job(args.job_id, cfg)
        print(json.dumps(
            {k: job._meta[k] for k in ("id", "state")} |
            {"segments": [(s["mode"], s["status"]) for s in job._meta["segments"]]},
            ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
