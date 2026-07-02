# SVLR bridge for RMBench

This folder exposes RMBench/RoboTwin as an HTTP robot server that SVLR can control without changing SVLR's core architecture.

## What this patch fixes

- Uses `head_camera` by default for SVLR perception, with fallback to wrist cameras.
- Runs SVLR perception before language planning: `/process_vlm` then `/process_llm_command`.
- Waits indefinitely for SVLR actions by design, so benchmark failures are not hidden by an artificial timeout. Use `/stop` or Ctrl-C to end a stuck debug run.
- Converts PANDA-style gripper widths (`0.08` open, `0.0` close) to RoboTwin normalized gripper commands (`1.0` open, `0.0` close).
- Removes unconditional `output_step*.png` debug image spam; enable it with `--sim_save_debug_images true`.
- Respects `--episode_num` instead of hardcoding 100 episodes.
- Allows `--global_task` to override generated RMBench instructions for smoke tests.

## Recommended first smoke test

Terminal 1, in the SVLR repo:

```bash
python main.py \
  --robot_name PANDA \
  --http_server 127.0.0.1 \
  --port 65500 \
  --llm_provider Ollama \
  --llm_name qwen3.5:2b \
  --vlm_provider Ollama \
  --vlm_name granite3.2-vision \
  --disable-startup-init-pose
```

Terminal 2, in the RMBench repo:

```bash
bash script/run_eval_svlr.sh
```

## Useful overrides

```bash
--task_name press_button              # safest first task
--task_name observe_and_pickup        # next simple pick task
--episode_num 1                       # debug single episode
--global_task "press the button"      # force deterministic instruction
--sim_camera_key head_camera          # best for VLM scene view
--sim_camera_key right_camera         # fallback/debug wrist camera
--sim_save_debug_images true          # save bridge camera snapshots
```

## Important limitation

This bridge still lets SVLR use its normal RGB-D/VLM object position pipeline. That is faithful to SVLR, but the Panda real-camera calibration may not perfectly match RMBench's simulated camera coordinates. For a strict reasoning-only benchmark, the next clean step would be a separate ground-truth-entity adapter, not a perception rewrite.
