"""Tests for the export/benchmark tooling — task-204.

`model` here is a trivial dummy `torch.nn.Module`, never presented as a cat model — see
`ml/capture/export.py`'s module docstring and `specs/tasks/task-204.md`.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import pytest

torch = pytest.importorskip("torch")
onnx = pytest.importorskip("onnx")

from ml.capture.export import benchmark, export_onnx, file_size_bytes  # noqa: E402


class _DummyModule(torch.nn.Module):
    """A trivial linear layer. Infra validation only — not a detector or a landmarker."""

    def __init__(self) -> None:
        super().__init__()
        self.linear = torch.nn.Linear(4, 2)

    def forward(self, x: Any) -> Any:
        return self.linear(x)


def test_export_onnx_produces_a_file_a_checker_accepts(tmp_path: Path) -> None:
    model = _DummyModule()
    dummy_input = torch.zeros(1, 4)
    path = tmp_path / "dummy.onnx"

    result = export_onnx(model, dummy_input, path)

    assert result == path
    assert path.is_file()
    onnx.checker.check_model(onnx.load(str(path)))


def test_export_onnx_raises_and_leaves_no_valid_file_on_a_broken_model(tmp_path: Path) -> None:
    class _Broken(torch.nn.Module):
        def forward(self, x: Any) -> Any:
            raise RuntimeError("forward is intentionally broken for this test")

    path = tmp_path / "broken.onnx"

    with pytest.raises(Exception):  # noqa: B017 - torch.onnx.export's own export error type
        export_onnx(_Broken(), torch.zeros(1, 4), path)


def test_file_size_bytes_matches_the_real_file_on_disk(tmp_path: Path) -> None:
    path = tmp_path / "sized.bin"
    path.write_bytes(b"0" * 4096)

    assert file_size_bytes(path) == 4096


def test_benchmark_orders_p50_at_or_below_p95() -> None:
    stats = benchmark(lambda: sum(range(1000)), n=50, warmup=5)

    assert stats.p50_ms <= stats.p95_ms
    assert stats.n == 50
    assert stats.warmup == 5


def test_benchmark_reports_cold_start_separately_from_the_measured_samples() -> None:
    calls = {"count": 0}

    def fn() -> None:
        calls["count"] += 1
        if calls["count"] == 1:
            time.sleep(0.02)

    stats = benchmark(fn, n=20, warmup=5)

    assert stats.cold_start_ms > stats.p95_ms
    assert calls["count"] == 1 + 4 + 20
