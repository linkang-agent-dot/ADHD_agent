#!/usr/bin/env python3
"""Initialize, validate, and price an ecommerce video-reskin project."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = SKILL_ROOT / "assets" / "project-template"
VALID_ACTIONS = {"reuse", "reskin", "rebuild"}
VALID_ROUTES = {"ORIGINAL", "T", "F", "SS", "SE", "MK"}
VALID_STATUSES = {"planned", "generated", "accepted", "frozen", "rejected", "reuse"}
FINAL_STATUSES = {"accepted", "frozen", "reuse"}


def load_manifest(root: Path) -> dict:
    path = root / "project.json"
    if not path.is_file():
        raise ValueError(f"Missing manifest: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def cmd_init(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    manifest_path = root / "project.json"
    if manifest_path.exists():
        print(f"Refusing to overwrite existing project: {manifest_path}", file=sys.stderr)
        return 2

    root.mkdir(parents=True, exist_ok=True)
    for relative in (
        "input",
        "references/source-clips",
        "references/product",
        "references/keyframes",
        "prompts",
        "modules",
        "output/raw",
        "output/final",
        "qc",
    ):
        (root / relative).mkdir(parents=True, exist_ok=True)

    for template in TEMPLATE_ROOT.iterdir():
        if template.is_file():
            shutil.copy2(template, root / template.name)

    manifest = load_manifest(root)
    manifest["project"]["name"] = args.name
    manifest["project"]["source_video"] = args.source
    manifest["project"]["target_product"] = args.target_product
    manifest_path.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Initialized: {root}")
    print("Next: replace the sample module in project.json, then run validate --stage plan")
    return 0


def path_ok(root: Path, value: str) -> bool:
    if not value:
        return False
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    return path.is_file()


def validate_manifest(root: Path, data: dict, stage: str) -> list[str]:
    errors: list[str] = []
    project = data.get("project", {})
    if not project.get("name"):
        errors.append("project.name is required")
    if not project.get("source_video"):
        errors.append("project.source_video is required")
    if not project.get("target_product"):
        errors.append("project.target_product is required")

    modules = data.get("modules")
    if not isinstance(modules, list) or not modules:
        errors.append("modules must be a non-empty list")
        return errors

    ids: set[str] = set()
    previous_end = -1.0
    for index, module in enumerate(modules):
        prefix = f"modules[{index}]"
        module_id = str(module.get("id", "")).strip()
        if not module_id:
            errors.append(f"{prefix}.id is required")
        elif module_id in ids:
            errors.append(f"duplicate module id: {module_id}")
        ids.add(module_id)

        start = module.get("start_sec")
        end = module.get("end_sec")
        if not isinstance(start, (int, float)) or not isinstance(end, (int, float)) or end <= start:
            errors.append(f"{prefix} requires numeric end_sec > start_sec")
        elif start < previous_end:
            errors.append(f"{prefix} overlaps or is out of timeline order")
        if isinstance(end, (int, float)):
            previous_end = float(end)

        action = module.get("action")
        route = module.get("route")
        status = module.get("status")
        if action not in VALID_ACTIONS:
            errors.append(f"{prefix}.action must be one of {sorted(VALID_ACTIONS)}")
        if route not in VALID_ROUTES:
            errors.append(f"{prefix}.route must be one of {sorted(VALID_ROUTES)}")
        if status not in VALID_STATUSES:
            errors.append(f"{prefix}.status must be one of {sorted(VALID_STATUSES)}")
        if action == "reuse" and route != "ORIGINAL":
            errors.append(f"{prefix}: reuse modules must use ORIGINAL")
        if action != "reuse" and route == "ORIGINAL":
            errors.append(f"{prefix}: changed modules need a generated route")

        if stage in {"generate", "final"} and action != "reuse":
            if not path_ok(root, str(module.get("reference_video", ""))):
                errors.append(f"{prefix}.reference_video is missing")
            refs = module.get("product_refs")
            if not isinstance(refs, list) or not refs:
                errors.append(f"{prefix}.product_refs must list single-view product truth")
            elif any(not path_ok(root, str(item)) for item in refs):
                errors.append(f"{prefix}.product_refs contains a missing file")
            if not path_ok(root, str(module.get("prompt_path", ""))):
                errors.append(f"{prefix}.prompt_path is missing")
            if module.get("keyframe_required") and module.get("keyframe_status") != "accepted":
                errors.append(f"{prefix}: required keyframe is not accepted")

        if stage == "final":
            if status not in FINAL_STATUSES:
                errors.append(f"{prefix}.status is not final: {status}")
            if action != "reuse" and not path_ok(root, str(module.get("output_path", ""))):
                errors.append(f"{prefix}.output_path is missing")

    cost_entries = data.get("cost_entries", [])
    if not isinstance(cost_entries, list):
        errors.append("cost_entries must be a list")
    else:
        for index, entry in enumerate(cost_entries):
            prefix = f"cost_entries[{index}]"
            if entry.get("module_id") not in ids:
                errors.append(f"{prefix}.module_id does not match a module")
            if entry.get("bucket") not in {"production", "r_and_d", "historical_reuse"}:
                errors.append(f"{prefix}.bucket is invalid")
            points = entry.get("points")
            if not isinstance(points, (int, float)) or points < 0:
                errors.append(f"{prefix}.points must be a non-negative number")

    if stage == "final" and not path_ok(root, str(project.get("output_file", ""))):
        errors.append("project.output_file is missing")
    return errors


def cmd_validate(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        data = load_manifest(root)
        errors = validate_manifest(root, data, args.stage)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Validation failed: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"FAIL: {len(errors)} issue(s)")
        return 1
    print(f"PASS: {args.stage} gate")
    return 0


def cmd_cost(args: argparse.Namespace) -> int:
    root = Path(args.root).resolve()
    try:
        data = load_manifest(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Cost failed: {exc}", file=sys.stderr)
        return 2
    pricing = data.get("pricing", {})
    monthly_points = float(pricing.get("monthly_points", 0) or 0)
    subscription_cny = float(pricing.get("subscription_cny", 0) or 0)
    cny_per_point = subscription_cny / monthly_points if monthly_points else 0.0
    totals = {"production": 0.0, "r_and_d": 0.0, "historical_reuse": 0.0}
    for entry in data.get("cost_entries", []):
        if entry.get("paid", True):
            bucket = entry.get("bucket")
            if bucket in totals:
                totals[bucket] += float(entry.get("points", 0) or 0)

    result = {
        "plan": pricing.get("plan", "unknown"),
        "pricing_verified_at": pricing.get("verified_at", "unknown"),
        "cny_per_point": round(cny_per_point, 6),
        "production_points": round(totals["production"], 2),
        "production_cny": round(totals["production"] * cny_per_point, 2),
        "r_and_d_points": round(totals["r_and_d"], 2),
        "r_and_d_cny": round(totals["r_and_d"] * cny_per_point, 2),
        "historical_reuse_points": round(totals["historical_reuse"], 2),
        "historical_reuse_cny": round(totals["historical_reuse"] * cny_per_point, 2),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    init = sub.add_parser("init", help="create a non-destructive project scaffold")
    init.add_argument("--root", required=True)
    init.add_argument("--name", required=True)
    init.add_argument("--source", required=True)
    init.add_argument("--target-product", required=True)
    init.set_defaults(func=cmd_init)

    validate = sub.add_parser("validate", help="validate project gates")
    validate.add_argument("--root", required=True)
    validate.add_argument("--stage", choices=("plan", "generate", "final"), default="plan")
    validate.set_defaults(func=cmd_validate)

    cost = sub.add_parser("cost", help="summarize production and R&D cost separately")
    cost.add_argument("--root", required=True)
    cost.set_defaults(func=cmd_cost)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
