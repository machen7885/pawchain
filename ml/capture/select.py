"""Stage 2: which candidate box do we mean, when a detector finds more than one.

A second cat, a poster, a cat-shaped cushion — the detector cannot tell the difference,
so the choice is a design decision, written down (facilitator guide, Idea/Block 0
"Three numbers"). The rule: largest box, then most central, then highest confidence.
"""

from __future__ import annotations

from ml.capture.types import BBox, Point, Reject, RejectReason, RejectStage

# If the two largest candidates' areas differ by less than this fraction of the largest,
# they are treated as a genuine tie and broken by centrality, then confidence, rather than
# by area alone.
AREA_TIE_MARGIN: float = 0.05

# If, after every tie-break, the two leading candidates are still this close on every
# signal, the choice is genuinely ambiguous rather than decided by a coin flip.
CONFIDENCE_TIE_MARGIN: float = 0.02


def _distance_to_center(box: BBox, frame_center: Point) -> float:
    dx = box.center.x - frame_center.x
    dy = box.center.y - frame_center.y
    return (dx * dx + dy * dy) ** 0.5


def select(candidates: list[BBox], frame_center: Point | None = None) -> BBox | Reject:
    """Pick one candidate box, or report that the choice is genuinely ambiguous.

    `candidates` must be non-empty; an empty list is a stage-1 (`detect`) concern, not a
    stage-2 one, and is rejected before `select` is ever called (see `pipeline.process`).
    `frame_center` defaults to the origin, which only matters when there is a genuine
    near-tie on area to break by centrality.
    """
    if frame_center is None:
        frame_center = Point(0.0, 0.0)
    if not candidates:
        raise ValueError("select requires at least one candidate; detect owns the empty case")
    if len(candidates) == 1:
        return candidates[0]

    by_area = sorted(candidates, key=lambda b: b.area, reverse=True)
    largest, runner_up = by_area[0], by_area[1]

    if largest.area <= 0:
        raise ValueError("candidate boxes must have positive area")

    area_gap = (largest.area - runner_up.area) / largest.area
    if area_gap >= AREA_TIE_MARGIN:
        return largest

    # Near-tie on area: break by centrality, then confidence.
    tied = [b for b in by_area if (largest.area - b.area) / largest.area < AREA_TIE_MARGIN]
    by_centrality = sorted(tied, key=lambda b: _distance_to_center(b, frame_center))
    most_central, next_most_central = by_centrality[0], by_centrality[1]

    centrality_gap = abs(
        _distance_to_center(most_central, frame_center)
        - _distance_to_center(next_most_central, frame_center)
    )
    if centrality_gap >= 1.0:
        return most_central

    by_confidence = sorted(by_centrality, key=lambda b: b.confidence, reverse=True)
    best, second = by_confidence[0], by_confidence[1]
    if best.confidence - second.confidence >= CONFIDENCE_TIE_MARGIN:
        return best

    return Reject(
        stage=RejectStage.SELECT,
        reason=RejectReason.AMBIGUOUS_CANDIDATES,
        detail=(
            f"{len(candidates)} candidates, top two tied on area, centrality and "
            f"confidence within margin"
        ),
    )
