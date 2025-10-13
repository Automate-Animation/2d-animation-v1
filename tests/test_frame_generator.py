import builtins
import csv
import importlib.util
import io
import sys
from pathlib import Path


class DummyImage:
    def __init__(self):
        self.saved_paths = []

    def save(self, path):
        self.saved_paths.append(path)


class DummyManager:
    def __init__(self):
        self.calls = []

    def get_character(self, **kwargs):
        self.calls.append(kwargs)
        return DummyImage(), {}


def load_frame_generator(monkeypatch):
    core_dir = Path(__file__).resolve().parents[1] / "core"
    monkeypatch.chdir(core_dir)
    monkeypatch.syspath_prepend(str(core_dir))

    module_name = "frame_generator"
    if module_name in sys.modules:
        del sys.modules[module_name]

    spec = importlib.util.spec_from_file_location(module_name, core_dir / "frame_generator.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_save_frames_from_csv_uses_false_for_falsey_blink(tmp_path, monkeypatch):
    module = load_frame_generator(monkeypatch)

    csv_path = tmp_path / "frames.csv"
    fieldnames = [
        "Character",
        "Emotion",
        "Body",
        "Head_Direction",
        "Eyes_Direction",
        "Background",
        "Mouth_Emotion",
        "Mouth_Name",
        "Zoom",
        "Blink",
    ]
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerow(
            {
                "Character": "character_1",
                "Emotion": "happy",
                "Body": "default",
                "Head_Direction": "M",
                "Eyes_Direction": "M",
                "Background": "bg",
                "Mouth_Emotion": "smile",
                "Mouth_Name": "default",
                "Zoom": "1",
                "Blink": "False",
            }
        )

    dummy_manager = DummyManager()
    monkeypatch.setattr(module, "manager", dummy_manager)
    monkeypatch.setattr(module, "frame_data", {"key_counter": {}, "frame_key": {}})
    monkeypatch.setattr(module.os.path, "exists", lambda path: False)

    real_open = builtins.open

    def fake_open(path, mode="r", *args, **kwargs):
        if path == "frameCreationInfo.json" and "w" in mode:
            return io.StringIO()
        return real_open(path, mode, *args, **kwargs)

    monkeypatch.setattr(module, "open", fake_open, raising=False)

    module.save_frames_from_csv(str(csv_path))

    assert dummy_manager.calls, "Manager should have been invoked"
    assert dummy_manager.calls[0]["blink"] is False

    frame_key = module.frame_data["frame_key"][0]
    assert frame_key.endswith("False")


def test_parse_blink_value_truthy_inputs(monkeypatch):
    module = load_frame_generator(monkeypatch)

    assert module.parse_blink_value("true") is True
    assert module.parse_blink_value("TRUE") is True
    assert module.parse_blink_value("1") is True
    assert module.parse_blink_value(1) is True
    assert module.parse_blink_value("anything else") is False
