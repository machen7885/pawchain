"""The capture pipeline: `capture.process(frame)` — see `pipeline.py` and task-203."""

from __future__ import annotations

from ml.capture.pipeline import process
from ml.capture.types import (
    AlignedCrop,
    BBox,
    CaptureResult,
    Landmarks,
    Point,
    Reject,
    RejectReason,
    RejectStage,
)

__all__ = [
    "AlignedCrop",
    "BBox",
    "CaptureResult",
    "Landmarks",
    "Point",
    "Reject",
    "RejectReason",
    "RejectStage",
    "process",
]
