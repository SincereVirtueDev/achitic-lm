import importlib.util
import sys
from pathlib import Path


EXPECTED_CONFIGS = {
    "nano.json": {"params": 4_999_424, "label_status": "OK"},
    "tiny.json": {"params": 23_058_944, "label_status": "OK"},
    "50m.json": {"params": 30_745_088, "label_status": "WARN"},
    "150m.json": {"params": 92_769_024, "label_status": "WARN"},
    "350m.json": {"params": 258_253_824, "label_status": "WARN"},
    "1b.json": {"params": 668_345_856, "label_status": "WARN"},
}


def load_model_report():
    path = Path("scripts/model_report.py")
    spec = importlib.util.spec_from_file_location("model_report", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_every_config_has_measured_parameter_count_recorded_in_ladder_docs():
    report = load_model_report()
    ladder = Path("docs/pipeline/00_MODEL_LADDER.md").read_text(encoding="utf8")
    config_paths = sorted(Path("configs").glob("*.json"))

    assert {path.name for path in config_paths} == set(EXPECTED_CONFIGS)

    for path in config_paths:
        expected = EXPECTED_CONFIGS[path.name]
        result = report.build_report(path, verify_threshold=0)

        assert result.params == expected["params"]
        assert result.label_status == expected["label_status"]
        assert f"`configs/{path.name}`" in ladder
        assert f"{result.params:,}" in ladder


def test_current_cpu_targets_and_legacy_alias_policy_are_explicit():
    report = load_model_report()
    ladder = Path("docs/pipeline/00_MODEL_LADDER.md").read_text(encoding="utf8")

    nano = report.build_report(Path("configs/nano.json"), verify_threshold=0)
    tiny = report.build_report(Path("configs/tiny.json"), verify_threshold=0)
    assert abs(nano.params - 5_000_000) <= 1_000
    assert 20_000_000 <= tiny.params <= 30_000_000

    for legacy_name in ["50m.json", "150m.json", "350m.json", "1b.json"]:
        legacy = report.build_report(Path("configs") / legacy_name, verify_threshold=0)
        assert legacy.label_status == "WARN"

    assert "Legacy alias policy" in ladder
    for legacy_name in ["50m.json", "150m.json", "350m.json", "1b.json"]:
        assert f"`configs/{legacy_name}`" in ladder
    assert "alias" in ladder.lower()
    assert "deprecated" in ladder.lower()


def test_architecture_documents_quant_friendly_shape_policy():
    architecture = Path("docs/ARCHITECTURE.md").read_text(encoding="utf8")
    normalized = architecture.lower()

    assert "quant-friendly shape policy" in normalized
    assert "ffn_dim" in architecture
    assert "dim" in architecture
    assert "32" in architecture
    assert "llama.cpp" in architecture
    assert "load-and-generate" in normalized
