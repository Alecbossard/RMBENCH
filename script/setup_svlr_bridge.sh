#!/usr/bin/env bash
set -euo pipefail

# One-shot setup helper for the RMBench side of the SVLR bridge.
# It prepares the pixi env, downloads required assets, patches generated
# CuRobo asset paths, and validates the bridge files.

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

if ! command -v pixi >/dev/null 2>&1; then
  echo "[RMBench setup] ERROR: pixi is not installed or not on PATH."
  echo "Install pixi first: https://pixi.sh/latest/installation/"
  exit 1
fi

echo "[RMBench setup] installing/updating pixi svlr environment"
pixi install -e svlr

echo "[RMBench setup] preparing assets"
pixi run -e svlr python script/setup_svlr_assets.py

echo "[RMBench setup] validating bridge Python files"
pixi run -e svlr python -m py_compile \
  script/eval_svlr.py \
  policy/SVLR/deploy_policy.py \
  envs/swap_blocks.py

cat <<EOF

[RMBench setup] done.

Start SVLR in terminal 1:
  cd ~/svlr-pr6
  SVLR_SEGMENTATION_USE_VLM_IMAGE=1 SVLR_DEBUG_BBOX=1 bash run_svlr_rmbench.sh

Then run RMBench in terminal 2:
  cd "$ROOT_DIR"
  bash policy/SVLR/run_demo.sh
EOF
