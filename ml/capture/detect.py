"""Stage 1: is there a cat in this photo, and where.

A detector answers "the head is roughly in this box," with a confidence — nothing more. It
does not know whose cat it is (facilitator guide, Idea 4).

No detector is trained yet. Training one needs labelled photographs, and none exist yet
(`EVIDENCE.md`, Week 2; `specs/open-questions.md` OQ-011). `default_detect` says so loudly
rather than returning a heuristic dressed up as a model — the same refusal
`evals/run.py::run_unimplemented_suite` already uses for a suite that has not landed,
applied here at the pipeline stage.
"""

from __future__ import annotations

from typing import Protocol

import numpy as np

from ml.capture.types import BBox


class DetectorUnavailable(RuntimeError):
    """No trained detector is wired in yet."""


class Detector(Protocol):
    """The contract any real detector must satisfy: a frame in, candidate boxes out."""

    def __call__(self, frame: np.ndarray) -> list[BBox]: ...


def default_detect(frame: np.ndarray) -> list[BBox]:
    """Raise `DetectorUnavailable`. See module docstring and OQ-011."""
    raise DetectorUnavailable(
        "No detector is trained yet — blocked on evals/golden/capture/manifest.json "
        "having real labelled entries (see specs/open-questions.md OQ-011, ADR-0004)."
    )
