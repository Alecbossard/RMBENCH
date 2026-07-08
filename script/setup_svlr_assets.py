#!/usr/bin/env python3
"""Prepare RMBench assets required by the SVLR bridge.

The bridge should be usable from a fresh clone without committing large assets.
This script downloads the standard RMBench objects and embodiments, falls back
to the RoboTwin2.0 embodiments zip for Franka assets, and rewrites generated
CuRobo YAML files with the absolute local asset path.
"""

from __future__ import annotations

import argparse
import contextlib
import shutil
import sys
import zipfile
from pathlib import Path


REQUIRED_PATHS = [
    Path("assets/objects/002_breadbasket/model_data0.json"),
    Path("assets/objects/005_button/10124/mobility.urdf"),
    Path("assets/embodiments/franka-panda/panda.urdf"),
    Path("assets/embodiments/franka-panda/panda.srdf"),
    Path("assets/embodiments/franka-panda/curobo_tmp.yml"),
]


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def missing_required(root: Path) -> list[Path]:
    return [path for path in REQUIRED_PATHS if not (root / path).exists()]


def snapshot_download_assets(root: Path) -> None:
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit(
            "huggingface-hub is required. Run `pixi install -e svlr` first."
        ) from exc

    print("[assets] downloading RMBench objects/embodiments from Hugging Face")
    snapshot_download(
        repo_id="TianxingChen/RMBench",
        allow_patterns=["embodiments/**", "objects/**"],
        local_dir=str(root / "assets"),
        repo_type="dataset",
        resume_download=True,
    )


def download_robotwin_embodiments_zip(root: Path) -> None:
    try:
        from huggingface_hub import hf_hub_download
    except ImportError as exc:
        raise SystemExit(
            "huggingface-hub is required. Run `pixi install -e svlr` first."
        ) from exc

    cache_dir = root / "assets" / ".cache"
    cache_dir.mkdir(parents=True, exist_ok=True)
    print("[assets] downloading RoboTwin2.0 embodiments.zip fallback")
    zip_path = Path(
        hf_hub_download(
            repo_id="TianxingChen/RoboTwin2.0",
            filename="embodiments.zip",
            repo_type="dataset",
            local_dir=str(cache_dir),
        )
    )
    print(f"[assets] extracting {zip_path}")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(root / "assets")

    nested = root / "assets" / "embodiments" / "embodiments"
    if nested.exists():
        for child in nested.iterdir():
            target = root / "assets" / "embodiments" / child.name
            if target.exists():
                continue
            shutil.move(str(child), str(target))
        with contextlib.suppress(OSError):
            nested.rmdir()


def rewrite_curobo_paths(root: Path) -> None:
    embodiments_root = root / "assets" / "embodiments"
    tmp_files = sorted(embodiments_root.glob("**/*_tmp.yml"))
    if not tmp_files:
        print("[assets] no *_tmp.yml files found under assets/embodiments")
        return

    asset_root = str(root)
    for tmp_file in tmp_files:
        target = tmp_file.with_name(tmp_file.name.replace("_tmp.yml", ".yml"))
        content = tmp_file.read_text(encoding="utf-8")
        content = content.replace("${ASSETS_PATH}", asset_root).replace(
            "$ASSETS_PATH", asset_root
        )
        target.write_text(content, encoding="utf-8")
        print(f"[assets] wrote {target.relative_to(root)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--skip-download",
        action="store_true",
        help="Only validate and rewrite local asset paths.",
    )
    args = parser.parse_args()

    root = repo_root()
    before = missing_required(root)
    if before and not args.skip_download:
        print("[assets] missing required files:")
        for path in before:
            print(f"  - {path}")
        snapshot_download_assets(root)

    after_snapshot = missing_required(root)
    franka_missing = any("franka-panda" in str(path) for path in after_snapshot)
    if franka_missing and not args.skip_download:
        download_robotwin_embodiments_zip(root)

    rewrite_curobo_paths(root)

    missing = missing_required(root)
    if missing:
        print("[assets] ERROR: missing required files after setup:")
        for path in missing:
            print(f"  - {path}")
        return 1

    print("[assets] all required SVLR/RMBench assets are present")
    return 0


if __name__ == "__main__":
    sys.exit(main())
