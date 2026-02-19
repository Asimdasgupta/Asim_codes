import argparse
import json
from pathlib import Path

from .compressor import load_catalog, compress_catalog, compress_progress
from .planner import plan_path


def main():
    parser = argparse.ArgumentParser(description="Educational Agent: compress catalog and progress to generate a personalized learning path.")
    parser.add_argument("--catalog", type=str, required=True, help="Path to catalog JSON")
    parser.add_argument("--progress", type=str, required=True, help="Path to learner progress JSON")
    parser.add_argument("--targets", type=str, required=False, help="Optional path to targets JSON")
    parser.add_argument("--max-hours", type=float, required=False, help="Optional hours budget for this plan")
    args = parser.parse_args()

    catalog_raw = json.loads(Path(args.catalog).read_text(encoding="utf-8"))
    progress_raw = json.loads(Path(args.progress).read_text(encoding="utf-8"))
    targets_raw = None
    if args.targets:
        targets_raw = json.loads(Path(args.targets).read_text(encoding="utf-8"))

    catalog = load_catalog(catalog_raw)
    cc = compress_catalog(catalog)
    progress = compress_progress(progress_raw, cc)

    target_topics = None
    if targets_raw:
        target_topics = targets_raw.get("target_topics") or targets_raw.get("desired_outcomes")
    result = plan_path(cc, progress, target_topics=target_topics, max_hours=args.max_hours)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

