#!/usr/bin/env python3
"""Download RMBench demo_clean evaluation data from Hugging Face.

The generic mode keeps the historical full demo_clean download. The SVLR setup
uses ``--metadata-only`` for its five supported tasks because the live simulator
and ``--global_task`` do not require trajectories, videos, or HDF5 episodes.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from huggingface_hub import snapshot_download

REPO_ID = "TianxingChen/RMBench"
SVLR_TASKS = (
    "swap_blocks",
    "put_back_block",
    "rearrange_blocks",
    "press_button",
    "cover_blocks",
)
METADATA_FILES = (
    "language_annotation.json",
    "scene_info.json",
    "seed.txt",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--tasks",
        nargs="+",
        default=["all"],
        help=(
            "Task names to download, or 'all' for every demo_clean task. "
            f"SVLR tasks: {', '.join(SVLR_TASKS)}."
        ),
    )
    parser.add_argument(
        "--metadata-only",
        action="store_true",
        help="Download only scene_info.json, seed.txt, and language_annotation.json.",
    )
    return parser.parse_args()


def allow_patterns(tasks: list[str], metadata_only: bool) -> list[str]:
    if "all" in tasks and len(tasks) != 1:
        raise SystemExit("'all' cannot be combined with explicit task names")

    task_patterns = ["*"] if tasks == ["all"] else tasks
    if metadata_only:
        return [
            f"data/{task}/demo_clean/{filename}"
            for task in task_patterns
            for filename in METADATA_FILES
        ]
    return [f"data/{task}/demo_clean/**" for task in task_patterns]


def main() -> None:
    args = parse_args()
    patterns = allow_patterns(args.tasks, args.metadata_only)
    data_root = Path(__file__).resolve().parent
    print(f"[data] downloading dataset {REPO_ID} patterns={patterns}")
    snapshot_download(
        repo_id=REPO_ID,
        repo_type="dataset",
        local_dir=data_root,
        allow_patterns=patterns,
    )
    print(f"[data] download complete: {data_root / 'data'}")


if __name__ == "__main__":
    main()
