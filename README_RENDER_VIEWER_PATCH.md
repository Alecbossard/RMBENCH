# RMBench SVLR render_freq override patch

This patch fixes `script/eval_svlr.py` so task-level command-line overrides such as `--render_freq 1` are applied after the task YAML is loaded. Without this, RMBench keeps `render_freq: 0` from the YAML and the SAPIEN 3D viewer is never created.

Usage:

```bash
cd ~/RMBench/RMBench
unzip -o ~/Downloads/rmbench_svlr_renderfreq_override_patch.zip
```

Then run with:

```bash
pixi run -e svlr python script/eval_svlr.py --config policy/SVLR/deploy_policy.yml --overrides \
  --task_name press_button \
  --task_config demo_clean_franka \
  --policy_name SVLR \
  --ckpt_setting svlr_debug \
  --seed 0 \
  --instruction_type unseen \
  --episode_num 1 \
  --global_task "press the button" \
  --sim_camera_key right_camera \
  --sim_save_debug_images true \
  --sim_drive false \
  --sim_home false \
  --render_freq 1
```
