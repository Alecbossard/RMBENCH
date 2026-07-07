#!/usr/bin/env bash
set -euo pipefail

# Run from RMBENCH repo root or from policy/SVLR.
# Start SVLR first in another terminal:
#   cd <svlr_repo> && bash run_svlr_rmbench.sh
#
# Default command mirrors the manual command used for the SVLR/RMBench demo:
#   press_button + demo_clean_franka + global instruction "press the button"
#
# Usage:
#   bash policy/SVLR/run_demo.sh
#   bash policy/SVLR/run_demo.sh press_button demo_clean_franka svlr_debug 0 "press the button"

cd "$(dirname "$0")/../.."

TASK_NAME="${1:-press_button}"
TASK_CONFIG="${2:-demo_clean_franka}"
CKPT_SETTING="${3:-svlr_debug}"
SEED="${4:-0}"
GLOBAL_TASK="${5:-press the button}"
SIM_CAMERA_KEY="${SIM_CAMERA_KEY:-right_camera}"
SIM_SAVE_DEBUG_IMAGES="${SIM_SAVE_DEBUG_IMAGES:-true}"
SIM_DRIVE="${SIM_DRIVE:-true}"
SIM_HOME="${SIM_HOME:-false}"
SIM_MIRROR_SINGLE_ARM="${SIM_MIRROR_SINGLE_ARM:-auto}"
SIM_KEEP_ALIVE_AFTER_ACTIONS="${SIM_KEEP_ALIVE_AFTER_ACTIONS:-false}"
RENDER_FREQ="${RENDER_FREQ:-30}"
INSTRUCTION_TYPE="${INSTRUCTION_TYPE:-unseen}"
EPISODE_NUM="${EPISODE_NUM:-1}"

fuser -k -9 65500/tcp || true
rm -f svlr_bridge_*.png

pixi run -e svlr python script/eval_svlr.py --config policy/SVLR/deploy_policy.yml --overrides \
  --task_name "${TASK_NAME}" \
  --task_config "${TASK_CONFIG}" \
  --policy_name SVLR \
  --ckpt_setting "${CKPT_SETTING}" \
  --seed "${SEED}" \
  --instruction_type "${INSTRUCTION_TYPE}" \
  --episode_num "${EPISODE_NUM}" \
  --global_task "${GLOBAL_TASK}" \
  --sim_camera_key "${SIM_CAMERA_KEY}" \
  --sim_save_debug_images "${SIM_SAVE_DEBUG_IMAGES}" \
  --sim_drive "${SIM_DRIVE}" \
  --sim_home "${SIM_HOME}" \
  --sim_mirror_single_arm "${SIM_MIRROR_SINGLE_ARM}" \
  --sim_keep_alive_after_actions "${SIM_KEEP_ALIVE_AFTER_ACTIONS}" \
  --render_freq "${RENDER_FREQ}"
