"""Tests for the pipeline's shared types — task-203 acceptance criterion 8."""

from __future__ import annotations

from ml.capture.types import REJECT_MESSAGES, BBox, Point, RejectReason


def test_bbox_area_and_center() -> None:
    box = BBox(x=10.0, y=20.0, width=30.0, height=40.0, confidence=0.9)
    assert box.area == 1200.0
    assert box.center == Point(25.0, 40.0)


def test_every_reject_reason_has_a_message() -> None:
    for reason in RejectReason:
        assert reason in REJECT_MESSAGES, f"{reason} has no user-facing message"


def test_reject_messages_are_short_and_have_no_numbers() -> None:
    for reason, message in REJECT_MESSAGES.items():
        word_count = len(message.split())
        assert word_count <= 8, f"{reason}: {message!r} is {word_count} words"
        assert not any(char.isdigit() for char in message), (
            f"{reason}: {message!r} leaks a measured value to the user"
        )
