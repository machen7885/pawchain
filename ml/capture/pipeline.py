"""`capture.process(frame)` — phone frame in, aligned crop or labelled reject out.

Five stages, five chances to say no, wired into one function
(`specs/tasks/task-203.md`; facilitator guide, Idea 1 and Idea 3): detect, select,
landmark, align, quality. There is no third outcome — everything downstream (Week 3's
embedder, Week 5's mini-program capture flow) can assume that whatever it receives from
here is already good.
"""

from __future__ import annotations

import numpy as np

from ml.capture.align import CANONICAL_TEMPLATE, similarity_transform, warp_affine
from ml.capture.detect import Detector, DetectorUnavailable, default_detect
from ml.capture.landmark import Landmarker, LandmarkerUnavailable, default_locate
from ml.capture.quality import (
    DEFAULT_THRESHOLDS,
    QualityThresholds,
    illumination_stats,
    laplacian_variance,
)
from ml.capture.select import select
from ml.capture.types import (
    AlignedCrop,
    BBox,
    Point,
    Reject,
    RejectReason,
    RejectStage,
)


def process(
    frame: np.ndarray,
    *,
    detect: Detector = default_detect,
    locate: Landmarker = default_locate,
    thresholds: QualityThresholds = DEFAULT_THRESHOLDS,
) -> AlignedCrop | Reject:
    """Run the five-stage capture pipeline on one frame.

    `detect` and `locate` are injectable so the pipeline's wiring can be tested without a
    trained model (`ml/capture/test_pipeline.py`); production callers use the defaults,
    which honestly refuse (`DetectorUnavailable`, `LandmarkerUnavailable`) until real
    models exist (OQ-011).
    """
    if frame.ndim != 3 or frame.shape[2] != 3:
        return Reject(
            stage=RejectStage.DETECT,
            reason=RejectReason.INVALID_INPUT,
            detail=f"frame must be (H, W, 3); got {frame.shape}",
        )

    try:
        candidates: list[BBox] = detect(frame)
    except DetectorUnavailable as exc:
        return Reject(
            stage=RejectStage.DETECT, reason=RejectReason.DETECTOR_NOT_TRAINED, detail=str(exc)
        )

    if not candidates:
        return Reject(
            stage=RejectStage.DETECT, reason=RejectReason.NO_CAT_FOUND, detail="0 candidates"
        )

    frame_h, frame_w = frame.shape[:2]
    selection = select(candidates, frame_center=Point(frame_w / 2, frame_h / 2))
    if isinstance(selection, Reject):
        return selection
    box = selection

    try:
        landmarks = locate(frame, box)
    except LandmarkerUnavailable as exc:
        return Reject(
            stage=RejectStage.LANDMARK,
            reason=RejectReason.LANDMARK_MODEL_NOT_TRAINED,
            detail=str(exc),
        )

    if landmarks.confidence < thresholds.landmark_confidence_min:
        return Reject(
            stage=RejectStage.LANDMARK,
            reason=RejectReason.LOW_LANDMARK_CONFIDENCE,
            detail=f"confidence={landmarks.confidence:.3f}",
        )

    matrix, residual = similarity_transform(landmarks.as_array(), CANONICAL_TEMPLATE)
    if residual > thresholds.pose_residual_max:
        return Reject(
            stage=RejectStage.ALIGN,
            reason=RejectReason.POSE_TOO_EXTREME,
            detail=f"residual={residual:.2f}px",
        )

    crop = warp_affine(frame, matrix)

    blur = laplacian_variance(crop)
    if blur < thresholds.blur_min:
        return Reject(
            stage=RejectStage.QUALITY,
            reason=RejectReason.BLUR,
            detail=f"laplacian_variance={blur:.1f}",
        )

    clipped_fraction, _mean_luminance = illumination_stats(crop)
    if clipped_fraction > thresholds.illumination_clip_max:
        return Reject(
            stage=RejectStage.QUALITY,
            reason=RejectReason.ILLUMINATION,
            detail=f"clipped_fraction={clipped_fraction:.3f}",
        )

    return AlignedCrop(pixels=crop, residual=residual, source_box=box, landmarks=landmarks)
