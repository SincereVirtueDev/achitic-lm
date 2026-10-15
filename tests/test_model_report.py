import importlib.util
import sys
from pathlib import Path

from achitic.model import AchiticLM, Config


def load_model_report():
    path = Path("scripts/model_report.py")
    spec = importlib.util.spec_from_file_location("model_report", path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_formula_parameter_count_matches_instantiated_model():
    report = load_model_report()
    cfg = Config(vocab_size=128, dim=64, layers=2, heads=4, kv_heads=2, ffn_dim=160, context=32)

    expected = sum(p.numel() for p in AchiticLM(cfg).parameters())

    assert report.formula_parameter_count(cfg) == expected


def test_legacy_50m_label_warns_when_actual_params_diverge():
    report = load_model_report()

    result = report.build_report(Path("configs/50m.json"), verify_threshold=0)

    assert result.params == 30_745_088
    assert result.label_status == "WARN"
    assert "50M label" in result.warning


def test_memory_estimate_scales_with_micro_batch_activation_cost():
    report = load_model_report()
    cfg = Config(vocab_size=128, dim=64, layers=2, heads=4, kv_heads=2, ffn_dim=160, context=32)
    params = report.formula_parameter_count(cfg)

    batch_1 = report.estimate_memory(
        cfg,
        params,
        batch=1,
        dtype="fp32",
        activation_multiplier=12.0,
        overhead_ratio=1.0,
    )
    batch_2 = report.estimate_memory(
        cfg,
        params,
        batch=2,
        dtype="fp32",
        activation_multiplier=12.0,
        overhead_ratio=1.0,
    )

    assert batch_2.activation_bytes == batch_1.activation_bytes * 2
    assert batch_2.total_bytes > batch_1.total_bytes
