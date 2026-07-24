import importlib.util
import os
from pathlib import Path
import unittest
from unittest import mock


DEPLOY_POLICY = Path(__file__).resolve().parents[1] / "policy" / "SVLR" / "deploy_policy.py"
SPEC = importlib.util.spec_from_file_location("svlr_deploy_policy", DEPLOY_POLICY)
deploy_policy = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(deploy_policy)


class CameraShaderEnvironmentTests(unittest.TestCase):
    def test_source_shader_inherits_requested_vlm_shader(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            source, vlm = deploy_policy._configure_camera_shader_environment(
                {"sim_vlm_camera_shader_dir": "minimal"}
            )

            self.assertEqual(source, "minimal")
            self.assertEqual(vlm, "minimal")
            self.assertEqual(os.environ["RMBENCH_CAMERA_SHADER_DIR"], "minimal")
            self.assertEqual(
                os.environ["RMBENCH_VLM_CAMERA_SHADER_DIR"], "minimal"
            )

    def test_explicit_source_shader_override_is_preserved(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            source, vlm = deploy_policy._configure_camera_shader_environment(
                {
                    "sim_camera_shader_dir": "rt",
                    "sim_vlm_camera_shader_dir": "minimal",
                }
            )

            self.assertEqual(source, "rt")
            self.assertEqual(vlm, "minimal")
            self.assertEqual(os.environ["RMBENCH_CAMERA_SHADER_DIR"], "rt")

    def test_empty_configuration_clears_inherited_camera_shader_state(self):
        with mock.patch.dict(
            os.environ,
            {
                "RMBENCH_CAMERA_SHADER_DIR": "",
                "RMBENCH_VLM_CAMERA_SHADER_DIR": "stale",
            },
            clear=True,
        ):
            source, vlm = deploy_policy._configure_camera_shader_environment({})

            self.assertEqual(source, "")
            self.assertEqual(vlm, "")
            self.assertNotIn("RMBENCH_CAMERA_SHADER_DIR", os.environ)
            self.assertNotIn("RMBENCH_VLM_CAMERA_SHADER_DIR", os.environ)


if __name__ == "__main__":
    unittest.main()
