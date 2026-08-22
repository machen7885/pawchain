"""Tests for the selection rule — task-203 acceptance criterion 5."""

from __future__ import annotations

import pytest

from ml.capture.select import select
from ml.capture.types import BBox, Point, Reject, RejectReason


def test_select_raises_on_empty_candidates() -> None:
    with pytest.raises(ValueError, match="at least one candidate"):
        select([])


def test_select_returns_the_only_candidate() -> None:
    only = BBox(x=0, y=0, width=10, height=10, confidence=0.5)
    assert select([only]) is only


def test_select_picks_the_largest_box_by_a_clear_margin() -> None:
    small = BBox(x=0, y=0, width=10, height=10, confidence=0.9)
    large = BBox(x=50, y=50, width=40, height=40, confidence=0.4)

    assert select([small, large]) is large


def test_select_is_deterministic_across_input_order() -> None:
    small = BBox(x=0, y=0, width=10, height=10, confidence=0.9)
    large = BBox(x=50, y=50, width=40, height=40, confidence=0.4)

    assert select([small, large]) is select([large, small])


def test_select_breaks_a_near_tied_area_by_centrality() -> None:
    center = Point(50.0, 50.0)
    off_center = BBox(x=0, y=0, width=20, height=20, confidence=0.5)
    near_center = BBox(x=40, y=40, width=20.5, height=20.5, confidence=0.5)

    result = select([off_center, near_center], frame_center=center)

    assert result is near_center


def test_select_reports_a_genuine_tie_as_ambiguous() -> None:
    center = Point(0.0, 0.0)
    a = BBox(x=100.0, y=100.0, width=20.0, height=20.0, confidence=0.70)
    b = BBox(x=-120.0, y=-120.0, width=20.0, height=20.0, confidence=0.705)

    result = select([a, b], frame_center=center)

    assert isinstance(result, Reject)
    assert result.reason is RejectReason.AMBIGUOUS_CANDIDATES
