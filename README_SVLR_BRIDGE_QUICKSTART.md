# RMBench + SVLR Bridge Quickstart

This document explains how to run RMBench with SVLR as the policy for the
current `swap_blocks` bridge setup.

## Matching Branches

Use these two branches together:

```bash
cd ~/svlr-pr6
git checkout svlr-rmbench-complete

cd ~/RMBench/RMBench
git checkout svlr-bridge-complete
```

## Start SVLR

Terminal 1:

```bash
cd ~/svlr-pr6
conda activate SVLR
SVLR_SEGMENTATION_USE_VLM_IMAGE=1 SVLR_DEBUG_BBOX=1 bash run_svlr_rmbench.sh
```

The default SVLR launcher expects:

- Ollama running locally.
- `qwen3-vl:8b` for VLM perception.
- `qwen3.5:4b` for LLM planning.
- Grounded-SAM-2 at `~/Documents/Grounded-SAM-2`.

Override Grounded-SAM-2 paths with environment variables:

```bash
SVLR_GROUNDED_SAM2_REPO=/path/to/Grounded-SAM-2
SVLR_SAM2_CHECKPOINT=/path/to/sam2.1_hiera_large.pt
SVLR_GROUNDING_DINO_CHECKPOINT=/path/to/groundingdino_swint_ogc.pth
```

## Run RMBench

Terminal 2:

```bash
cd ~/RMBench/RMBench
RMBENCH_SWAP_DEBUG_SUCCESS=1 pixi run -e svlr python script/eval_svlr.py \
  --config policy/SVLR/deploy_policy.yml \
  --overrides \
  --task_name swap_blocks \
  --task_config demo_clean_franka \
  --policy_name SVLR \
  --ckpt_setting svlr_swap_debug \
  --seed 0 \
  --instruction_type unseen \
  --episode_num 1 \
  --global_task "Swap the positions of the two blocks and after press the button." \
  --sim_camera_key right_camera \
  --sim_vlm_camera_shader_dir minimal \
  --sim_save_debug_images true \
  --sim_drive true \
  --sim_home true \
  --sim_arm right \
  --sim_mirror_single_arm auto \
  --sim_keep_alive_after_actions false \
  --render_freq 1
```

## What Should Happen

RMBench should:

1. create the simulator;
2. connect to SVLR at `http://127.0.0.1:7860`;
3. send the right wrist camera RGB-D observation;
4. receive queued SVLR low-level actions;
5. swap the two cubes;
6. press the button.

For `swap_blocks`, the reward debug should eventually show:

```text
block2->basket1: all True
block1->basket2: all True
gripper_close=True
press_cnt=1
press_flag=True
```

The bridge accepts a closed gripper during button press because the Franka press
primitive closes the gripper to press the button. Expert seed checking remains
compatible because the reward checks whether either gripper is closed.

## Useful Flags

- `RMBENCH_SWAP_DEBUG_SUCCESS=1`: print detailed reward checks.
- `--sim_vlm_camera_shader_dir minimal`: use a cleaner RGB image for VLM input.
- `--sim_save_debug_images true`: save bridge camera images.
- `--sim_keep_alive_after_actions true`: keep the simulator open after actions.
- `--render_freq 1`: render every step for visual inspection.

## Common Issues

### Camera clone messages repeat forever

This means RMBench is failing the expert seed check before the real SVLR episode.
Check `envs/swap_blocks.py`: the reward condition should require
`self.is_left_gripper_close() or self.is_right_gripper_close()`.

### SVLR connects but the robot does not move

Check the SVLR terminal for VLM/LLM errors. Also confirm the expected object list
is detected:

```json
["breadbasket", "breadbasket", "breadbasket", "red cube", "red cube", "red button"]
```

### Button is pressed but reward stays zero

Enable `RMBENCH_SWAP_DEBUG_SUCCESS=1` and verify that `gripper_close`,
`press_cnt`, and `press_flag` are true in the same debug block.

## Validation

```bash
cd ~/RMBench/RMBench
pixi run -e svlr python -m py_compile \
  script/eval_svlr.py \
  policy/SVLR/deploy_policy.py \
  envs/swap_blocks.py
```

