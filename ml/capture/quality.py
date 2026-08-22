"""The quality gate: three cheap, model-free checks on the aligned crop.

All three are arithmetic on pixels, none needs a model, and all three run in well under a
millisecond — which is why they belong on the phone, before the frame is ever sent anywhere
(facilitator guide, Idea 7).

Every threshold here is provisional. See ADR-0005 for why, and for the exact sweep
procedure that replaces each one once `evals/golden/capture/manifest.json` has real,
labelled entries.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

# Laplacian variance floor on the aligned 112x112 crop (REQ-001). Written in Week 1 before
# any photograph existed — a placeholder wearing the costume of a decision (ADR-0005). This
# is the single named constant for this number; nowhere else in ml/ repeats it as a literal
# (task-203 #3, enforced by test_quality.py::test_blur_threshold_is_a_single_named_constant).
BLUR_THRESHOLD: float = 120.0

# How far the aligned landmarks may sit from CANONICAL_TEMPLATE, in pixels, before the pose
# is judged too extreme to have aligned correctly. Provisional (ADR-0005).
POSE_RESIDUAL_MAX: float = 6.0

# Fraction of pixels clipped to pure black (0) or pure white (255) before a crop is judged
# blown out or too dark to use. Provisional (ADR-0005).
ILLUMINATION_CLIP_MAX: float = 0.15

# Landmark model confidence floor. A landmark model always returns five points, even on
# nothing (facilitator guide, Idea 4) — this is what lets stage 3 refuse when it should.
LANDMARK_CONFIDENCE_MIN: float = 0.5

_LAPLACIAN_KERNEL_CENTER = -4.0


@dataclass(frozen=True)
class QualityThresholds:
    """The operating point for every quality signal, bundled so a sweep can vary them."""

    blur_min: float = BLUR_THRESHOLD
    pose_residual_max: float = POSE_RESIDUAL_MAX
    illumination_clip_max: float = ILLUMINATION_CLIP_MAX
    landmark_confidence_min: float = LANDMARK_CONFIDENCE_MIN


DEFAULT_THRESHOLDS = QualityThresholds()


def _to_grayscale(crop: np.ndarray) -> np.ndarray:
    if crop.ndim == 2:
        return crop.astype(np.float64)
    if crop.ndim == 3 and crop.shape[2] == 3:
        return crop.astype(np.float64).mean(axis=2)
    raise ValueError(f"crop must be (H, W) or (H, W, 3); got {crop.shape}")


def laplacian_variance(crop: np.ndarray) -> float:
    """Return the Laplacian variance of `crop`: sharp is high, blurry is low.

    Blurring mixes each pixel with its neighbours; neighbouring pixels in a blurry image
    are similar, so the Laplacian — how different each pixel is from its four neighbours —
    is small and its variance across the image is small (facilitator guide, Idea 7).

    Raises `ValueError` on a crop smaller than 3x3 in either dimension, or with a shape
    that is neither `(H, W)` nor `(H, W, 3)`.
    """
    gray = _to_grayscale(crop)
    if gray.shape[0] < 3 or gray.shape[1] < 3:
        raise ValueError(f"crop must be at least 3x3; got {gray.shape}")

    padded = np.pad(gray, 1, mode="edge")
    laplacian = (
        padded[0:-2, 1:-1]
        + padded[2:, 1:-1]
        + padded[1:-1, 0:-2]
        + padded[1:-1, 2:]
        + _LAPLACIAN_KERNEL_CENTER * padded[1:-1, 1:-1]
    )
    return float(laplacian.var())


def illumination_stats(crop: np.ndarray) -> tuple[float, float]:
    """Return `(clipped_fraction, mean_luminance)` for `crop`.

    `clipped_fraction` is the share of pixels sitting at pure black (0) or pure white (255)
    — the signature of a dark room or blown-out fur (facilitator guide, Idea 7).
    """
    gray = _to_grayscale(crop)
    clipped = float(np.mean((gray <= 1.0) | (gray >= 254.0)))
    mean_luminance = float(gray.mean())
    return clipped, mean_luminance
