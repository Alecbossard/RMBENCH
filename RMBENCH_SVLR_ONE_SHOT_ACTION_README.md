# RMBench SVLR one-shot action execution patch

This patch changes `policy/SVLR/deploy_policy.py` so the RMBench bridge executes exactly one RMBench dense action per SVLR low-level `/send_action`.

Previous behavior:

- One SVLR action could be re-issued up to `MAX_SUBSTEPS_PER_ACTION` times.
- The bridge waited for measured EE error to fall below a threshold.
- Near contact, for example button pressing, the same target could be replayed many times and the arm appeared to correct/replan in a loop.

New behavior:

- One SVLR `/send_action` maps to one `env.take_action(..., action_type="ee")` call.
- RMBench itself plans and executes the dense trajectory internally.
- `/end_action` is acknowledged after that dense execution returns.
- EE error is printed only for debugging; it does not cause re-execution.

Apply from the RMBench repo root:

```bash
cd ~/RMBench/RMBench
unzip -o ~/Downloads/rmbench_svlr_one_shot_action_patch.zip
```

Run with UI + SVLR:

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
  --sim_drive true \
  --sim_home false \
  --render_freq 1
```

Expected log lines:

```text
[sim-server] one-shot position action complete: ee_error=...m (debug only)
[sim-server] take_action complete: ... (ran 1 substeps)
```

`ran 1 substeps` now means one RMBench dense action, not one physics step.
