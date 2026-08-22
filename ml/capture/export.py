"""Export and measure: the tooling, ready before there is a trained model to run through it.

`torch`, `onnx` and `onnxruntime` are imported lazily inside each function, not at module
load, so nothing that runs on every frame (the quality gate, `capture.process`) pays for an
import it does not use (ADR-0004).

No detector or landmark model is trained yet (OQ-011). This module is exercised in
`test_export.py` against a trivial dummy module — never presented as a cat model — so the
export and benchmarking path is built and tested before there is a real model to point it
at (task-204).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import torch


def export_onnx(model: torch.nn.Module, dummy_input: torch.Tensor, path: Path) -> Path:
    """Export `model` to ONNX at `path`, validate the result, and return `path`.

    Raises whatever `onnx.checker.check_model` raises if the exported graph is invalid, and
    does not leave a passing-looking file behind when it does.
    """
    import onnx
    import torch

    model.eval()
    with torch.no_grad():
        torch.onnx.export(
            model,
            (dummy_input,),
            str(path),
            input_names=["input"],
            output_names=["output"],
            dynamo=False,  # the legacy TorchScript exporter; avoids an onnxscript dependency
        )

    loaded = onnx.load(str(path))
    onnx.checker.check_model(loaded)
    return path


def file_size_bytes(path: Path) -> int:
    """Return the exact on-disk byte count of the file at `path`."""
    return path.stat().st_size


@dataclass(frozen=True)
class LatencyStats:
    """p50 and p95 over the timed runs, plus the cold-start cost, reported separately.

    Speed budgets are written against p95, not the mean — the mean hides the one-in-twenty
    slow frame that is exactly what makes a camera feel broken (Block 4, "Benchmark
    honestly or do not benchmark").
    """

    p50_ms: float
    p95_ms: float
    cold_start_ms: float
    n: int
    warmup: int


def benchmark(fn: Callable[[], Any], *, n: int = 200, warmup: int = 20) -> LatencyStats:
    """Time `fn` end to end: `warmup` discarded runs, then `n` measured runs, single-threaded.

    The first call (`cold_start_ms`) is timed and reported separately rather than folded
    into `warmup` or averaged into `p50`/`p95` — a user feels it once per session, so it is
    real, but it is not the steady-state number the size/speed budget is written against.
    """
    if n < 1 or warmup < 1:
        raise ValueError("n and warmup must each be at least 1")

    start = time.perf_counter()
    fn()
    cold_start_ms = (time.perf_counter() - start) * 1000.0

    for _ in range(warmup - 1):
        fn()

    samples_ms = []
    for _ in range(n):
        start = time.perf_counter()
        fn()
        samples_ms.append((time.perf_counter() - start) * 1000.0)

    samples_ms.sort()
    p50 = samples_ms[int(0.50 * (n - 1))]
    p95 = samples_ms[int(0.95 * (n - 1))]
    return LatencyStats(p50_ms=p50, p95_ms=p95, cold_start_ms=cold_start_ms, n=n, warmup=warmup)
