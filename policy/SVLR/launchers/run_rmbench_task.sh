#!/usr/bin/env bash
set -euo pipefail

if [[ $# -ne 1 ]]; then
  echo "Usage: $0 {swap_blocks|put_back_block|rearrange_blocks|press_button|cover_blocks}" >&2
  exit 2
fi

TASK_NAME="$1"

case "$TASK_NAME" in
  swap_blocks)
    SIM_PORT=65500
    GRADIO_PORT=7860
    BASE_SEED=4177
    GLOBAL_TASK="Swap the positions of the two blocks and after press the button."
    ;;
  put_back_block)
    SIM_PORT=65501
    GRADIO_PORT=7861
    BASE_SEED=7882
    GLOBAL_TASK="Put the block on the center of the 4 blue cube, press the button, then put the block back to its initial position."
    ;;
  rearrange_blocks)
    SIM_PORT=65502
    GRADIO_PORT=7862
    BASE_SEED=7133
    GLOBAL_TASK="Move the block between the two mats onto the empty mat, press the button, then move the other block (the one that started on a mat) to the space between the two mats."
    ;;
  press_button)
    SIM_PORT=65503
    GRADIO_PORT=7863
    BASE_SEED=1762
    GLOBAL_TASK="Observe the two numbers on the table. Press the left button the number of times corresponding to the number on the left, and press the middle button the number of times corresponding to the number on the right. Then press the right button once to confirm."
    ;;
  cover_blocks)
    SIM_PORT=65504
    GRADIO_PORT=7864
    BASE_SEED=4982
    GLOBAL_TASK="On the table, red, green, and blue blocks are arranged randomly along with three lids. From the current viewpoint, cover the blocks from left to right using the lids, and then uncover them again in the sequence red, green, and blue."
    ;;
  *)
    echo "Unknown RMBench task: $TASK_NAME" >&2
    exit 2
    ;;
esac

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
RMBENCH_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"
EPISODE_NUM="${EPISODE_NUM:-1}"
RENDER_FREQ="${RENDER_FREQ:-1}"
RUN_STAMP="$(date +%Y%m%dT%H%M%S)"
RUN_NAME="${TASK_NAME}_${EPISODE_NUM}ep_${RUN_STAMP}"
RUN_DIR="$RMBENCH_ROOT/manual_logs/$TASK_NAME/$RUN_NAME"
TMP_DIR="/tmp/svlr-rmbench/$TASK_NAME/rmbench/$RUN_NAME/tmp"

mkdir -p "$RUN_DIR/debug_images" "$RUN_DIR/eval_result" "$TMP_DIR"
cd "$RMBENCH_ROOT"

echo "Starting RMBench task=$TASK_NAME episodes=$EPISODE_NUM render_freq=$RENDER_FREQ"
echo "Run directory: $RUN_DIR"

env -u CUDA_VISIBLE_DEVICES \
  PYTHONUNBUFFERED=1 \
  TMPDIR="$TMP_DIR" \
  pixi run --locked -e svlr python script/eval_svlr.py \
    --config policy/SVLR/deploy_policy.yml \
    --overrides \
    --task_name "$TASK_NAME" \
    --task_config demo_clean_franka \
    --policy_name SVLR \
    --ckpt_setting "$RUN_NAME" \
    --seed "$BASE_SEED" \
    --instruction_type unseen \
    --episode_num "$EPISODE_NUM" \
    --global_task "$GLOBAL_TASK" \
    --sim_port "$SIM_PORT" \
    --svlr_url "http://127.0.0.1:$GRADIO_PORT" \
    --sim_debug_dir "$RUN_DIR/debug_images" \
    --eval_output_dir "$RUN_DIR/eval_result" \
    --sim_camera_key right_camera \
    --sim_vlm_camera_shader_dir minimal \
    --sim_save_debug_images true \
    --sim_drive true \
    --sim_home true \
    --sim_arm right \
    --sim_mirror_single_arm auto \
    --sim_keep_alive_after_actions false \
    --render_freq "$RENDER_FREQ" \
    --skip_expert_check true \
  2>&1 | tee "$RUN_DIR/rmbench.log"
