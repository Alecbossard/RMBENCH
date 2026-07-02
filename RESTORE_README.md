# RMBench SVLR restore bundle

This bundle contains the latest RMBench-side SVLR bridge files recovered from the patch artifacts in this chat:
- policy/SVLR/deploy_policy.py: one-shot action bridge, gripper-only safe handling, init/work orientation logic from the latest patch chain.
- script/eval_svlr.py: render_freq override / SVLR driver updates.
- script/run_eval_svlr.sh and policy/SVLR/deploy_policy.yml from the good-init patch chain.

Apply from the root of RMBench:

```bash
unzip -o rmbench_svlr_restore_latest_bundle.zip -d ~/RMBench/RMBench
cd ~/RMBench/RMBench
find . -type d -name "__pycache__" -prune -exec rm -rf {} +
find . -name "*.pyc" -delete
rm -f svlr_bridge_*.png

git add policy/SVLR/deploy_policy.py policy/SVLR/deploy_policy.yml policy/SVLR/README_SVLR_BRIDGE.md policy/SVLR/README_SVLR_SIM_CALIBRATION.md script/eval_svlr.py script/run_eval_svlr.sh README_RENDER_VIEWER_PATCH.md RMBENCH_SVLR_ONE_SHOT_ACTION_README.md RESTORE_README.md
git commit -m "Restore RMBench SVLR bridge updates"
git push -u origin main
```
