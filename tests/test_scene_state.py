import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scene_state.py"


def run_script(*args, input_text=None):
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        input=input_text,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        cwd=ROOT,
        check=False,
    )


def make_state(tmp_path, slug="test-tideclock"):
    state_path = tmp_path / "scene-state.json"
    result = run_script(
        "init",
        "--out",
        str(state_path),
        "--slug",
        slug,
        "--mode",
        "object",
        "--platform",
        "portable",
        "--view",
        "front-left-three-quarter",
        "--subject",
        "Tideclock",
        "--force",
    )
    assert result.returncode == 0, result.stderr + result.stdout

    state = json.loads(state_path.read_text(encoding="utf-8"))
    state["world_id"] = slug
    state["visual_thesis"] = "A weathered scientific heirloom in warm lamplight."
    state["entities"][0]["name"] = "Tideclock"
    state["entities"][0]["geometry"] = (
        "Upright drum-shaped instrument with a glass front dome and conical base."
    )
    state["entities"][0]["dimensions"] = "~0.8 m tall, ~0.5 m wide"
    state["entities"][0]["materials"] = ["oxidized brass", "smoked glass"]
    state["entities"][0]["features"] = [
        {
            "id": "f1",
            "name": "front glass dome",
            "surface": "front",
            "description": "smoked glass disc in a brass bezel",
            "origin": "stated",
        },
        {
            "id": "f2",
            "name": "rear winding key",
            "surface": "back",
            "description": "iron key projecting from the rear case",
            "origin": "stated",
        },
    ]
    state["visibility"] = [
        {
            "entity_id": "e1",
            "feature_id": "f1",
            "surface": "front",
            "state": "visible",
            "cue": "direct",
            "prompt_action": "describe",
            "note": "facing camera",
        },
        {
            "entity_id": "e1",
            "feature_id": "f2",
            "surface": "back",
            "state": "hidden",
            "cue": "none",
            "prompt_action": "negative",
            "note": "rear faces away",
        },
    ]
    state["camera"].update(
        {
            "view_id": "front-left-three-quarter",
            "height": "1.3 m",
            "distance": "2.2 m",
            "azimuth_deg": -35,
            "elevation_deg": 8,
            "lens": "50mm",
            "shot_scale": "full instrument with table edge",
            "framing": "subject centered, two-thirds of frame height",
            "focus": "front glass dome",
            "depth_of_field": "f/2.8, shallow",
            "aspect_ratio": "3:2",
        }
    )
    state_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    return state_path, state


GOOD_PROMPT = (
    "Photoreal cinematic still life, 50mm lens at chest height, three-quarter front-left "
    "view, subject centered and filling two-thirds of the frame. A tideclock in oxidized "
    "brass with a smoked-glass front dome, warm oil-lamp key light from the upper right, "
    "soft contact shadow, muted brass and smoke gray palette, fine film grain. "
    "Negative: no readable text, no rear winding key."
)

BAD_PROMPT = (
    "Photoreal still life of a tideclock, 50mm lens, warm light, centered composition. "
    "The rear winding key projects from the back of the case. Negative: no text."
)


class SceneStateTests(unittest.TestCase):
    def test_init_creates_valid_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "scene-state.json"
            result = run_script(
                "init",
                "--out",
                str(state_path),
                "--slug",
                "new-object",
                "--mode",
                "object",
                "--force",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(state_path.exists())

            validate = run_script("validate", str(state_path))
            self.assertEqual(validate.returncode, 0, validate.stderr + validate.stdout)

    def test_init_refuses_overwrite_without_force(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path = Path(temp_dir) / "scene-state.json"
            first = run_script("init", "--out", str(state_path), "--slug", "new-object")
            self.assertEqual(first.returncode, 0, first.stderr)
            second = run_script("init", "--out", str(state_path), "--slug", "new-object")
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("already exists", second.stderr + second.stdout)

    def test_validate_rejects_missing_visibility_reference(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, state = make_state(Path(temp_dir))
            state["visibility"][0]["feature_id"] = "missing"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = run_script("validate", str(state_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("references missing feature", result.stdout)

    def test_validate_rejects_hidden_feature_marked_describe(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, state = make_state(Path(temp_dir))
            state["visibility"][1]["prompt_action"] = "describe"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = run_script("validate", str(state_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("cannot use prompt_action 'describe'", result.stdout)

    def test_brief_renders_camera_and_visibility(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            result = run_script("brief", str(state_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Camera", result.stdout)
            self.assertIn("front-left-three-quarter", result.stdout)
            self.assertIn("front glass dome", result.stdout)
            self.assertIn("Hidden: f2 (rear winding key)", result.stdout)

    def test_brief_refuses_invalid_state(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, state = make_state(Path(temp_dir))
            state["visibility"][1]["prompt_action"] = "describe"
            state_path.write_text(json.dumps(state), encoding="utf-8")

            result = run_script("brief", str(state_path))
            self.assertEqual(result.returncode, 1)
            self.assertIn("validation error", result.stderr)

    def test_diff_reports_camera_and_material_changes(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            old_path, old_state = make_state(Path(temp_dir))
            new_path = Path(temp_dir) / "scene-state-v2.json"
            new_state = json.loads(json.dumps(old_state))
            new_state["entities"][0]["materials"] = ["oxidized copper", "smoked glass"]
            new_state["camera"]["elevation_deg"] = 20
            new_path.write_text(json.dumps(new_state), encoding="utf-8")

            result = run_script("diff", str(old_path), str(new_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Camera", result.stdout)
            self.assertIn("elevation_deg: 8 -> 20", result.stdout)
            self.assertIn("oxidized brass, smoked glass -> oxidized copper, smoked glass", result.stdout)

    def test_check_passes_visible_prompt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            result = run_script(
                "check",
                "--state",
                str(state_path),
                "--text",
                GOOD_PROMPT,
                "--platform",
                "portable",
            )
            self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
            self.assertIn("Result: PASS", result.stdout)

    def test_check_flags_hidden_feature_in_visible_prompt(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            result = run_script(
                "check",
                "--state",
                str(state_path),
                "--text",
                BAD_PROMPT,
                "--platform",
                "portable",
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("appears in the visible prompt", result.stdout)

    def test_check_allows_negated_hidden_feature(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            prompt = (
                "Photoreal still life, 50mm lens, warm light, centered composition. "
                "The case has no rear winding key."
            )
            result = run_script(
                "check",
                "--state",
                str(state_path),
                "--text",
                prompt,
                "--platform",
                "portable",
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Result: PASS", result.stdout)

    def test_check_json_report(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            result = run_script(
                "check",
                "--state",
                str(state_path),
                "--text",
                BAD_PROMPT,
                "--json",
            )
            self.assertEqual(result.returncode, 1)
            report = json.loads(result.stdout)
            self.assertEqual(report["result"], "fail")
            self.assertEqual(report["hidden_features_checked"], 1)
            self.assertTrue(any("rear winding key" in item for item in report["errors"]))

    def test_check_handles_negative_prompt_block(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            prompt = (
                "Photoreal still life, 50mm lens, warm light, centered composition, "
                "brass and glass. Positive: tideclock with a smoked-glass dome. "
                "Negative Prompt: no rear winding key, no text."
            )
            result = run_script(
                "check",
                "--state",
                str(state_path),
                "--text",
                prompt,
                "--platform",
                "stable-diffusion",
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Result: PASS", result.stdout)

    def test_check_warns_about_stable_diffusion_blocks(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            state_path, _ = make_state(Path(temp_dir))
            prompt = (
                "Photoreal still life, 50mm lens, warm light, centered composition, "
                "brass and glass."
            )
            result = run_script(
                "check",
                "--state",
                str(state_path),
                "--text",
                prompt,
                "--platform",
                "stable-diffusion",
            )
            self.assertEqual(result.returncode, 0, result.stdout)
            self.assertIn("Positive: and Negative: blocks", result.stdout)


if __name__ == "__main__":
    unittest.main()
