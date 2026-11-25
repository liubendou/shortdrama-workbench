"""命令行入口：python -m workbench <子命令> ..."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import PROJECT_ROOT, load_config
from .cost import summarize


def _root(p: str) -> Path:
    q = Path(p)
    return q if q.is_absolute() else (PROJECT_ROOT / q)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="workbench", description="短剧剪辑工作台")
    sub = ap.add_subparsers(dest="cmd", required=True)

    run = sub.add_parser("run", help="端到端：分析 → 三模式脚本 → 渲染 → 报告")
    run.add_argument("--episodes", required=True, help="剧集目录（epNN.mp4 + epNN.srt）")
    run.add_argument("--out", required=True)
    run.add_argument("--modes", default="hook,highlight,narration")
    run.add_argument("--limit", type=int, default=0)
    run.add_argument("--chars", type=int, default=120, help="解说每集总字数上限")
    run.add_argument("--no-cache", action="store_true")

    cost = sub.add_parser("cost", help="汇总某次运行的云成本")
    cost.add_argument("--out", required=True)

    args = ap.parse_args(argv)
    if args.cmd == "run":
        from .pipeline import ALL_MODES, run_pipeline

        modes = tuple(m.strip() for m in args.modes.split(",") if m.strip())
        bad = [m for m in modes if m not in ALL_MODES]
        if bad:
            ap.error(f"未知模式：{bad}")
        cfg = load_config()
        report = run_pipeline(_root(args.episodes), _root(args.out), cfg, modes=modes, limit=args.limit,
                              chars_per_episode=args.chars, use_cache=not args.no_cache)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    if args.cmd == "cost":
        print(json.dumps(summarize(_root(args.out) / "cost.jsonl"), ensure_ascii=False, indent=2))
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
