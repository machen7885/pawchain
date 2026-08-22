"""Tests for `capture.process` — task-203 acceptance criteria 6, 7."""

from __future__ import annotations

import numpy as np

from ml.capture import process
from ml.capture.align import CANONICAL_TEMPLATE
from ml.capture.quality import QualityThresholds
from ml.capture.types import BBox, Landmarks, Point, Reject, RejectReason, RejectStage


def _frame(size: int = 200) -> np.ndarray:
    return np.random.default_rng(0).integers(0, 256, size=(size, size, 3), dtype=np.uint8)


def _landmarks_at(template: np.ndarray, confidence: float = 0.95) -> Landmarks:
    names = ("left_eye", "right_eye", "nose", "left_ear", "right_ear")
    points = {name: Point(*template[i]) for i, name in enumerate(names)}
    return Landmarks(confidence=confidence, **points)


def test_default_pipeline_always_rejects_at_detect_stage_not_trained() -> None:
    result = process(_frame())

    assert isinstance(result, Reject)
    assert result.stage is RejectStage.DETECT
    assert result.reason is RejectReason.DETECTOR_NOT_TRAINED


def test_pipeline_rejects_invalid_input_shape() -> None:
    result = process(np.zeros((10, 10)))

    assert isinstance(result, Reject)
    assert result.stage is RejectStage.DETECT
    assert result.reason is RejectReason.INVALID_INPUT


def test_pipeline_rejects_no_cat_found_when_detector_returns_nothing() -> None:
    result = process(_frame(), detect=lambda frame: [])

    assert isinstance(result, Reject)
    assert result.reason is RejectReason.NO_CAT_FOUND


def test_pipeline_happy_path_reaches_an_aligned_crop_with_injected_stages() -> None:
    box = BBox(x=40.0, y=40.0, width=120.0, height=120.0, confidence=0.99)
    landmarks = _landmarks_at(CANONICAL_TEMPLATE + np.array([40.0, 40.0]))

    result = process(
        _frame(),
        detect=lambda frame: [box],
        locate=lambda frame, box: landmarks,
    )

    assert not isinstance(result, Reject), result
    assert result.pixels.shape == (112, 112, 3)
    assert result.residual < 1.0


def test_pipeline_rejects_low_landmark_confidence() -> None:
    box = BBox(x=40.0, y=40.0, width=120.0, height=120.0, confidence=0.99)
    landmarks = _landmarks_at(CANONICAL_TEMPLATE + np.array([40.0, 40.0]), confidence=0.1)

    result = process(_frame(), detect=lambda frame: [box], locate=lambda frame, box: landmarks)

    assert isinstance(result, Reject)
    assert result.stage is RejectStage.LANDMARK
    assert result.reason is RejectReason.LOW_LANDMARK_CONFIDENCE


def test_pipeline_rejects_pose_too_extreme_on_a_large_residual() -> None:
    box = BBox(x=40.0, y=40.0, width=120.0, height=120.0, confidence=0.99)
    scrambled = CANONICAL_TEMPLATE.copy()
    scrambled[[0, 1, 2, 3, 4]] = scrambled[[2, 3, 4, 0, 1]]
    landmarks = _landmarks_at(scrambled + np.array([40.0, 40.0]))

    result = process(_frame(), detect=lambda frame: [box], locate=lambda frame, box: landmarks)

    assert isinstance(result, Reject)
    assert result.stage is RejectStage.ALIGN
    assert result.reason is RejectReason.POSE_TOO_EXTREME


def test_pipeline_rejects_blur_on_a_flat_frame() -> None:
    flat_frame = np.full((200, 200, 3), 128, dtype=np.uint8)
    box = BBox(x=40.0, y=40.0, width=120.0, height=120.0, confidence=0.99)
    landmarks = _landmarks_at(CANONICAL_TEMPLATE + np.array([40.0, 40.0]))

    result = process(flat_frame, detect=lambda frame: [box], locate=lambda frame, box: landmarks)

    assert isinstance(result, Reject)
    assert result.stage is RejectStage.QUALITY
    assert result.reason is RejectReason.BLUR


def test_pipeline_rejects_illumination_on_a_blown_out_frame() -> None:
    bright_frame = np.full((200, 200, 3), 255, dtype=np.uint8)
    box = BBox(x=40.0, y=40.0, width=120.0, height=120.0, confidence=0.99)
    landmarks = _landmarks_at(CANONICAL_TEMPLATE + np.array([40.0, 40.0]))
    # A blur threshold of 0 isolates the illumination check from the (also-failing) blur one.
    thresholds = QualityThresholds(blur_min=0.0)

    result = process(
        bright_frame,
        detect=lambda frame: [box],
        locate=lambda frame, box: landmarks,
        thresholds=thresholds,
    )

    assert isinstance(result, Reject)
    assert result.stage is RejectStage.QUALITY
    assert result.reason is RejectReason.ILLUMINATION
