import importlib
import sys
from pathlib import Path

import pytest


def test_update_assets_resolves_relative_paths(tmp_path, monkeypatch):
    repo_root = Path(__file__).resolve().parents[1]
    core_path = repo_root / "core"
    sys.path.insert(0, str(core_path))

    monkeypatch.chdir(tmp_path)

    module_name = "utils.update_character_asset_name"
    if module_name in sys.modules:
        del sys.modules[module_name]

    module = importlib.import_module(module_name)

    sample_data = {
        "words": [
            {
                "intensity": 1,
                "emotion": 1,
                "character": 1,
                "screen_mode": 1,
                "body_action": 1,
                "phonemes_frame": [{"name": "AA0", "frames": [1, 2, 3]}],
            }
        ]
    }

    updated_data = module.update_assets(sample_data)

    phoneme_details = updated_data["words"][0]["phonemes_frame_details"][0]
    assert phoneme_details["phoneme"] == "AA0"
    assert phoneme_details["mouth_name"] == module.response_json["AA0"]["happy"]


@pytest.fixture(autouse=True)
def _cleanup_sys_path():
    original_sys_path = list(sys.path)
    yield
    sys.path[:] = original_sys_path
