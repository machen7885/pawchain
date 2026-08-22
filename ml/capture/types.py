"""The shapes that flow through the capture pipeline.

`capture.process(frame)` returns exactly one of `AlignedCrop` or `Reject` — see
`specs/tasks/task-203.md`. Every reject carries the exact measured value for the internal
log (`detail`) and a short, vague-but-actionable message for the person holding the phone
(`user_message`) — the two audiences from the facilitator guide's Idea on the reject
message: tell the user what to do, never tell them what you measured.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np


@dataclass(frozen=True)
class Point:
    """A single pixel coordinate."""

    x: float
    y: float

    def as_tuple(self) -> tuple[float, float]:
        """Return `(x, y)`."""
        return (self.x, self.y)


@dataclass(frozen=True)
class BBox:
    """A detector's answer: roughly where the head is, and how sure it is."""

    x: float
    y: float
    width: float
    height: float
    confidence: float

    @property
    def area(self) -> float:
        """Box area in pixels."""
        return self.width * self.height

    @property
    def center(self) -> Point:
        """The box's centre point."""
        return Point(self.x + self.width / 2, self.y + self.height / 2)


# The five landmark names, in the fixed order every array conversion uses.
LANDMARK_NAMES: tuple[str, ...] = ("left_eye", "right_eye", "nose", "left_ear", "right_ear")


@dataclass(frozen=True)
class Landmarks:
    """Five points inside a detected head, plus the model's confidence in them.

    A landmark model always returns five points, even on a photo of a sofa — it has no way
    to say "there is nothing here" (facilitator guide, Idea 4). `confidence` is what lets
    the pipeline refuse when it should have.
    """

    left_eye: Point
    right_eye: Point
    nose: Point
    left_ear: Point
    right_ear: Point
    confidence: float

    def as_array(self) -> np.ndarray:
        """Return the five points as an `(5, 2)` array, in `LANDMARK_NAMES` order."""
        points = (self.left_eye, self.right_eye, self.nose, self.left_ear, self.right_ear)
        return np.array([p.as_tuple() for p in points], dtype=np.float64)


@dataclass(frozen=True)
class AlignedCrop:
    """The one non-reject outcome of `capture.process`: a standardised face crop.

    `pixels` is `(112, 112, 3)`, `uint8`, RGB. `residual` is the leftover alignment error in
    pixels (Idea 5, facilitator guide) — a pose and plausibility signal that costs nothing
    extra to compute, already used by the quality gate, and worth keeping on the result for
    downstream diagnostics.
    """

    pixels: np.ndarray
    residual: float
    source_box: BBox
    landmarks: Landmarks


class RejectStage(StrEnum):
    """Which of the five stages produced the reject."""

    DETECT = "detect"
    SELECT = "select"
    LANDMARK = "landmark"
    ALIGN = "align"
    QUALITY = "quality"


class RejectReason(StrEnum):
    """Every named cause a stage may reject for. Never a free-form string (task-203)."""

    INVALID_INPUT = "invalid_input"
    NO_CAT_FOUND = "no_cat_found"
    DETECTOR_NOT_TRAINED = "detector_not_trained"
    AMBIGUOUS_CANDIDATES = "ambiguous_candidates"
    LANDMARK_MODEL_NOT_TRAINED = "landmark_model_not_trained"
    LOW_LANDMARK_CONFIDENCE = "low_landmark_confidence"
    POSE_TOO_EXTREME = "pose_too_extreme"
    BLUR = "blur"
    ILLUMINATION = "illumination"


# Under eight words, no digits (Block 3, Exercise 3: "too specific" teaches the attacker
# what to aim for; "too vague" makes the household give up). Tested in test_types.py.
REJECT_MESSAGES: dict[RejectReason, str] = {
    RejectReason.INVALID_INPUT: "Capture unavailable. Try again.",
    RejectReason.NO_CAT_FOUND: "Bring the cat into frame.",
    RejectReason.DETECTOR_NOT_TRAINED: "Capture unavailable. Try again shortly.",
    RejectReason.AMBIGUOUS_CANDIDATES: "Only one cat in frame, please.",
    RejectReason.LANDMARK_MODEL_NOT_TRAINED: "Capture unavailable. Try again shortly.",
    RejectReason.LOW_LANDMARK_CONFIDENCE: "Face unclear. Face the camera.",
    RejectReason.POSE_TOO_EXTREME: "Turn your cat to face the camera.",
    RejectReason.BLUR: "Hold the phone steady.",
    RejectReason.ILLUMINATION: "Move to better light.",
}


@dataclass(frozen=True)
class Reject:
    """A refusal, with the reason attached."""

    stage: RejectStage
    reason: RejectReason
    detail: str

    @property
    def user_message(self) -> str:
        """The short, vague-but-actionable message shown to the person holding the phone."""
        return REJECT_MESSAGES[self.reason]


CaptureResult = AlignedCrop | Reject
