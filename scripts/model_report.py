#!/usr/bin/env python3
"""Report AchiticLM parameter counts and rough training memory budgets."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from achitic.model import AchiticLM, Config


DTYPE_BYTES = {
    "fp32": 4,
    "float32": 4,
    "bf16": 2,
    "bfloat16": 2,
    "fp16": 2,
    "float16": 2,
}


@dataclass(frozen=True)
class MemoryEstimate:
    parameter_bytes: int
    gradient_bytes: int
    optimizer_bytes: int
    activation_bytes: int
    overhead_bytes: int
    total_bytes: int


@dataclass(frozen=True)
class ModelReport:
    config: str
    role: str
    params: int
    verified_params: int | None
    label_status: str
    warning: str
    vocab_size: int
    layers: int
    dim: int
    heads: int
    kv_heads: int
    ffn_dim: int
    context: int
    dtype: str
    batch: int
    accum: int
    tokens_per_update: int
    memory: MemoryEstimate
    recommended_start: str


def load_config(path: Path) -> Config:
    return Config(**json.loads(path.read_text()))


def validate_config(cfg: Config) -> None:
    if cfg.dim % cfg.heads != 0:
        raise ValueError("dim must be divisible by heads")
    if cfg.heads % cfg.kv_heads != 0:
        raise ValueError("heads must be divisible by kv_heads")


def formula_parameter_count(cfg: Config) -> int:
    """Exact parameter formula for current AchiticLM with tied output head."""
    validate_config(cfg)
    head_dim = cfg.dim // cfg.heads
    kv_dim = cfg.kv_heads * head_dim

    embedding = cfg.vocab_size * cfg.dim
    attention = (cfg.dim * cfg.dim) + (2 * cfg.dim * kv_dim) + (cfg.dim * cfg.dim)
    feed_forward = 3 * cfg.dim * cfg.ffn_dim
    block_norms = 2 * cfg.dim
    block = attention + feed_forward + block_norms
    final_norm = cfg.dim
    return embedding + cfg.layers * block + final_norm


def instantiated_parameter_count(cfg: Config) -> int:
    model = AchiticLM(cfg)
    return sum(p.numel() for p in model.parameters())


def role_from_path(path: Path) -> str:
    stem = path.stem.lower()
    if stem == "nano":
        return "Nano"
    if stem == "tiny":
        return "Tiny"
    return stem.upper()


def label_target(path: Path) -> tuple[str, int | None, tuple[int, int] | None]:
    stem = path.stem.lower()
    if stem == "nano":
        return "Nano 5-10M", None, (5_000_000, 10_000_000)
    if stem == "tiny":
        return "Tiny 20-30M", None, (20_000_000, 30_000_000)
    match = re.fullmatch(r"(\d+)(m|b)", stem)
    if not match:
        return "unlabeled", None, None
    value = int(match.group(1))
    target = value * (1_000_000 if match.group(2) == "m" else 1_000_000_000)
    return f"{value}{match.group(2).upper()} label", target, None


def label_status(path: Path, params: int, tolerance: float = 0.10) -> tuple[str, str]:
    label, target, band = label_target(path)
    if band is not None:
        lower, upper = band
        slack = math.ceil((upper - lower) * tolerance)
        if lower - slack <= params <= upper + slack:
            return "OK", ""
        return "WARN", f"{label} expects {lower:,}-{upper:,} params; got {params:,}"
    if target is not None:
        delta = (params - target) / target
        if abs(delta) <= tolerance:
            return "OK", ""
        return "WARN", f"{label} target is {target:,}; got {params:,} ({delta:+.1%})"
    return "OK", ""


def estimate_memory(
    cfg: Config,
    params: int,
    *,
    batch: int,
    dtype: str,
    activation_multiplier: float,
    overhead_ratio: float,
) -> MemoryEstimate:
    if batch < 1:
        raise ValueError("batch must be >= 1")
    if dtype not in DTYPE_BYTES:
        raise ValueError(f"unsupported dtype {dtype!r}")
    if activation_multiplier <= 0:
        raise ValueError("activation_multiplier must be > 0")
    if overhead_ratio < 1.0:
        raise ValueError("overhead_ratio must be >= 1.0")

    dtype_bytes = DTYPE_BYTES[dtype]
    parameter_bytes = params * dtype_bytes
    gradient_bytes = params * dtype_bytes
    optimizer_bytes = params * 8  # AdamW first and second moments, conservatively fp32.
    activation_bytes = int(batch * cfg.context * cfg.dim * cfg.layers * dtype_bytes * activation_multiplier)
    subtotal = parameter_bytes + gradient_bytes + optimizer_bytes + activation_bytes
    overhead_bytes = int(subtotal * (overhead_ratio - 1.0))
    return MemoryEstimate(
        parameter_bytes=parameter_bytes,
        gradient_bytes=gradient_bytes,
        optimizer_bytes=optimizer_bytes,
        activation_bytes=activation_bytes,
        overhead_bytes=overhead_bytes,
        total_bytes=subtotal + overhead_bytes,
    )


def recommend_start(estimate: MemoryEstimate, *, budget_gb: float, context: int) -> str:
    total_gb = estimate.total_bytes / (1024**3)
    if total_gb <= min(2.0, budget_gb):
        return f"batch=1, accum={max(1, math.ceil(2048 / context))}"
    if total_gb <= budget_gb:
        return f"batch=1, accum={max(4, math.ceil(4096 / context))}"
    return "batch=1, accum>=8; reduce context/model or add memory before long runs"


def build_report(
    path: Path,
    *,
    batch: int = 1,
    accum: int = 4,
    dtype: str = "fp32",
    activation_multiplier: float = 12.0,
    overhead_ratio: float = 1.20,
    budget_gb: float = 4.0,
    verify_threshold: int = 50_000_000,
) -> ModelReport:
    cfg = load_config(path)
    params = formula_parameter_count(cfg)
    verified = instantiated_parameter_count(cfg) if params <= verify_threshold else None
    status, warning = label_status(path, params)
    if verified is not None and verified != params:
        status = "WARN"
        warning = f"formula params {params:,} != instantiated params {verified:,}"
    memory = estimate_memory(
        cfg,
        params,
        batch=batch,
        dtype=dtype,
        activation_multiplier=activation_multiplier,
        overhead_ratio=overhead_ratio,
    )
    return ModelReport(
        config=str(path),
        role=role_from_path(path),
        params=params,
        verified_params=verified,
        label_status=status,
        warning=warning,
        vocab_size=cfg.vocab_size,
        layers=cfg.layers,
        dim=cfg.dim,
        heads=cfg.heads,
        kv_heads=cfg.kv_heads,
        ffn_dim=cfg.ffn_dim,
        context=cfg.context,
        dtype=dtype,
        batch=batch,
        accum=accum,
        tokens_per_update=batch * cfg.context * accum,
        memory=memory,
        recommended_start=recommend_start(memory, budget_gb=budget_gb, context=cfg.context),
    )


def bytes_to_mib(value: int) -> float:
    return value / (1024**2)


def bytes_to_gib(value: int) -> float:
    return value / (1024**3)


def format_markdown(reports: Iterable[ModelReport]) -> str:
    rows = list(reports)
    lines = [
        "| Config | Role | Params | Verified | Status | Context | Train RAM GiB | Recommended start |",
        "| --- | --- | ---: | --- | --- | ---: | ---: | --- |",
    ]
    for report in rows:
        verified = "yes" if report.verified_params == report.params else ("skipped" if report.verified_params is None else "mismatch")
        lines.append(
            "| {config} | {role} | {params:,} | {verified} | {status} | {context} | {ram:.2f} | `{rec}` |".format(
                config=report.config,
                role=report.role,
                params=report.params,
                verified=verified,
                status=report.label_status,
                context=report.context,
                ram=bytes_to_gib(report.memory.total_bytes),
                rec=report.recommended_start,
            )
        )
    warnings = [report.warning for report in rows if report.warning]
    if warnings:
        lines.append("")
        lines.append("Warnings:")
        lines.extend(f"- {warning}" for warning in warnings)
    lines.append("")
    lines.append("Memory model: params + grads + AdamW moments + activation estimate + overhead.")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--configs", nargs="+", type=Path, required=True)
    parser.add_argument("--batch", type=int, default=1)
    parser.add_argument("--accum", type=int, default=4)
    parser.add_argument("--dtype", choices=sorted(DTYPE_BYTES), default="fp32")
    parser.add_argument("--activation-multiplier", type=float, default=12.0)
    parser.add_argument("--overhead-ratio", type=float, default=1.20)
    parser.add_argument("--budget-gb", type=float, default=4.0)
    parser.add_argument("--verify-threshold", type=int, default=50_000_000)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reports = [
        build_report(
            path,
            batch=args.batch,
            accum=args.accum,
            dtype=args.dtype,
            activation_multiplier=args.activation_multiplier,
            overhead_ratio=args.overhead_ratio,
            budget_gb=args.budget_gb,
            verify_threshold=args.verify_threshold,
        )
        for path in args.configs
    ]
    if args.json:
        print(json.dumps([asdict(report) for report in reports], indent=2))
    else:
        print(format_markdown(reports))


if __name__ == "__main__":
    main()
