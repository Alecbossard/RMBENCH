# SVLR bridge for RMBench

This integration exposes RMBench/RoboTwin as an HTTP robot server controlled by
SVLR. The documented target is one physical Franka/Panda articulation, the five
SVLR benchmark tasks, and the Grounded-SAM-2 perception path.

## Matching branches

Install the two repositories on their matching branches:

```bash
git clone --branch svlr-5-tasks-complete --single-branch \
  https://github.com/Alecbossard/svlr.git ~/svlr-pr6
git clone --branch fix/reproducible-svlr-setup --single-branch \
  https://github.com/Alecbossard/RMBENCH.git ~/RMBench/RMBench
```

The RMBench fixes can use `RMBench-SVLR` instead after this branch is merged
there.

## Clean RMBench setup

Prerequisites are Git, Pixi, an NVIDIA driver compatible with the locked CUDA
environment, and the matching SVLR checkout with Conda and Ollama.

```bash
cd ~/RMBench/RMBench
pixi install --locked -e svlr
pixi run --locked -e svlr setup
pixi run --locked -e svlr validate-franka
```

The `setup` task is idempotent. It:

- downloads the RoboTwin2.0 embodiments and RMBench object assets;
- downloads only `scene_info.json`, `seed.txt`, and
  `language_annotation.json` for the five SVLR tasks;
- generates the Franka `curobo.yml`, `curobo_left.yml`, and
  `curobo_right.yml` files with paths for the current checkout;
- validates the Franka/Panda configuration and the baseline bridge assets.

CuRobo is installed from the official `v0.7.8` Git tag. No local
`envs/curobo` checkout or Git submodule is required.

The generic data downloader remains available for other RMBench workflows:

```bash
# Download every demo_clean dataset, including trajectories and videos.
pixi run --locked -e svlr python data/_download.py

# Download selected lightweight metadata only.
pixi run --locked -e svlr python data/_download.py \
  --metadata-only --tasks swap_blocks press_button
```

## Run one of the five tasks

Use the matching task launcher in two terminals. Start SVLR first.

Terminal 1:

```bash
cd ~/svlr-pr6
conda activate SVLR
bash tools/rmbench_launchers/run_swap_blocks.sh
```

Wait for the Gradio local URL, then start RMBench.

Terminal 2:

```bash
cd ~/RMBench/RMBench
bash policy/SVLR/launchers/run_swap_blocks.sh
```

Replace `swap_blocks` in both filenames with one of:

- `put_back_block`
- `rearrange_blocks`
- `press_button`
- `cover_blocks`

The paired launchers provide the task instruction, validated seed, matching
robot/Gradio ports, camera shader, homing, debug directories, and result logs.
Set `EPISODE_NUM` or `RENDER_FREQ` on the RMBench command to override their
defaults. On the SVLR side, `LLM_NAME`, `VLM_NAME`, and `CUDA_DEVICE` are
configurable.

## Panda/Franka layout and camera pose

`task_config/demo_clean_franka.yml` uses `embodiment: ["franka-panda"]`.
RMBench exposes logical left/right action slots for policy compatibility, but
they control one physical Panda articulation.

For this mode:

- `--sim_arm right` controls the supported logical slot.
- `--sim_camera_key right_camera` selects the physical wrist camera.
- `--sim_mirror_single_arm auto` mirrors the command across the logical slots.
- the pre-perception home pose is
  `[0, -0.15, 1.4, 0.5, -0.5, 0.5, 0.5, 1.0]`.
- `SIM_HOME_CONTROLLED` and the CLI configuration can still override that pose.

## SVLR Grounded-SAM-2 prerequisites

The matching SVLR environment needs:

- SAM 2.1 large at
  `~/Documents/Grounded-SAM-2/checkpoints/sam2.1_hiera_large.pt`;
- GroundingDINO SwinT-OGC at
  `~/Documents/Grounded-SAM-2/gdino_checkpoints/groundingdino_swint_ogc.pth`;
- `supervision`, `pycocotools`, `addict`, and `yapf`.

For an existing environment that intentionally uses Transformers 5.x, install
the scoped compatibility shim:

```bash
bash policy/SVLR/svlr_env/install_gdino_tf5_compat.sh
```

## Logs and troubleshooting

Evaluation logs are written under `manual_logs/<task>/<run-name>/` and are
ignored by Git. Per-instance temporary files are written under
`/tmp/svlr-rmbench/`.

`Connection refused` on `/camera/rgbd` means the matching RMBench server is not
ready yet. Wait for `[sim-server] http://0.0.0.0:<port>` before expecting SVLR
camera frames.
