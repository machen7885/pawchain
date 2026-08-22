"""Stage 3: inside the detected head, where exactly are the eyes, the nose, the ear tips.

A landmark model is a different job from a detector — it takes a box and regresses five
coordinates, ten numbers, nothing else (facilitator guide, Idea 4). It always returns five
points, even on a photograph of a sofa, which is why the pipeline also checks its
confidence (`quality.LANDMARK_CONFIDENCE_MIN`) rather than trusting the points blindly.

No landmark model is trained yet, for the same reason `detect.py` has none: no labelled
photographs exist yet (OQ-011). `default_locate` raises rather than guessing.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

from ml.capture.types import BBox, Landmarks


class LandmarkerUnavailable(RuntimeError):
    """No trained landmark model is wired in yet."""


class Landmarker(Protocol):
    """The contract any real landmark model must satisfy: a frame and a box in, five points out."""

    def __call__(self, frame: np.ndarray, box: BBox) -> Landmarks: ...


def default_locate(frame: np.ndarray, box: BBox) -> Landmarks:
    """Raise `LandmarkerUnavailable`. See module docstring and OQ-011."""
    raise LandmarkerUnavailable(
        "No landmark model is trained yet — blocked on evals/golden/capture/manifest.json "
        "having real labelled entries (see specs/open-questions.md OQ-011, ADR-0004)."
    )
