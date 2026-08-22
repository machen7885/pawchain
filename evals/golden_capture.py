"""The golden capture manifest: schema, loading, hash verification, relabelling, and the
threshold sweep that turns 150 labelled crops into a defended number (task-201, task-202).

Nothing in this module ever writes to `evals/golden/capture/manifest.json` — it is loaded,
verified, and measured against. A relabel produces a *new* manifest object for the caller
to write and commit themselves, in a change that touches nothing else (`evals/golden/README.md`
rule 1; `record_relabel` below).
"""

from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, replace
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
from PIL import Image

from ml.capture import process
from ml.capture.align import CANONICAL_TEMPLATE, similarity_transform, warp_affine
from ml.capture.quality import laplacian_variance
from ml.capture.types import LANDMARK_NAMES, Landmarks, Point, Reject, RejectStage

REQUIRED_IMAGE_FIELDS = frozenset({"id", "relative_path", "sha256", "label"})
VALID_LABELS = frozenset({"usable", "not_usable"})
VALID_REASONS = frozenset({"no_cat", "wrong_crop", "blur", "pose", "illumination", "other"})

STAGE_ORDER: tuple[RejectStage, ...] = (
    RejectStage.DETECT,
    RejectStage.SELECT,
    RejectStage.LANDMARK,
    RejectStage.ALIGN,
    RejectStage.QUALITY,
)

DEFAULT_GOLDEN_IMAGES_ENV = "PAWCHAIN_GOLDEN_IMAGES"
DEFAULT_GOLDEN_IMAGES_DIR = "data/golden/capture"


@dataclass(frozen=True)
class GoldenImage:
    """One labelled entry in the golden capture manifest. See task-201's schema table."""

    id: str
    relative_path: str
    sha256: str
    label: str
    reason: str | None = None
    landmarks: Landmarks | None = None


@dataclass(frozen=True)
class Relabel:
    """One recorded change of a `GoldenImage`'s label — never a silent edit."""

    image_id: str
    old_label: str
    new_label: str
    note: str
    at: str


@dataclass(frozen=True)
class GoldenManifest:
    """A frozen collection of labelled crops. See `evals/golden/README.md`."""

    version: int
    images: tuple[GoldenImage, ...]
    relabels: tuple[Relabel, ...] = ()


def default_image_root() -> Path:
    """The local, gitignored directory the manifest's `relative_path`s resolve against.

    Defaults to `data/golden/capture/`, overridable with `PAWCHAIN_GOLDEN_IMAGES`
    (ADR-0006). Never a path inside git.
    """
    return Path(os.environ.get(DEFAULT_GOLDEN_IMAGES_ENV, DEFAULT_GOLDEN_IMAGES_DIR))


def _landmarks_from_dict(raw: dict[str, list[float]]) -> Landmarks:
    missing = set(LANDMARK_NAMES) - raw.keys()
    if missing:
        raise ValueError(f"landmarks entry missing points: {sorted(missing)}")
    points = {name: Point(x=float(raw[name][0]), y=float(raw[name][1])) for name in LANDMARK_NAMES}
    return Landmarks(confidence=1.0, **points)


def _landmarks_to_dict(landmarks: Landmarks) -> dict[str, list[float]]:
    return {name: list(getattr(landmarks, name).as_tuple()) for name in LANDMARK_NAMES}


def load_manifest(path: Path) -> GoldenManifest:
    """Load and validate a golden manifest. Raises on any structurally invalid entry."""
    if not path.is_file():
        raise FileNotFoundError(path)

    raw = json.loads(path.read_text(encoding="utf-8"))
    images: list[GoldenImage] = []
    for entry in raw.get("images", []):
        missing = REQUIRED_IMAGE_FIELDS - entry.keys()
        if missing:
            raise ValueError(f"golden image entry missing fields {sorted(missing)}: {entry}")
        if entry["label"] not in VALID_LABELS:
            raise ValueError(f"invalid label {entry['label']!r} for {entry['id']}")
        reason = entry.get("reason")
        if entry["label"] == "not_usable" and not reason:
            raise ValueError(f"not_usable entry {entry['id']!r} is missing a reason")
        if reason is not None and reason not in VALID_REASONS:
            raise ValueError(f"invalid reason {reason!r} for {entry['id']}")
        landmarks = _landmarks_from_dict(entry["landmarks"]) if entry.get("landmarks") else None
        images.append(
            GoldenImage(
                id=entry["id"],
                relative_path=entry["relative_path"],
                sha256=entry["sha256"],
                label=entry["label"],
                reason=reason,
                landmarks=landmarks,
            )
        )

    relabels = tuple(Relabel(**r) for r in raw.get("relabels", []))
    return GoldenManifest(version=raw.get("version", 1), images=tuple(images), relabels=relabels)


def dump_manifest(manifest: GoldenManifest) -> str:
    """Serialise `manifest` back to the JSON text `load_manifest` can read."""
    payload = {
        "version": manifest.version,
        "images": [
            {
                "id": image.id,
                "relative_path": image.relative_path,
                "sha256": image.sha256,
                "label": image.label,
                "reason": image.reason,
                "landmarks": _landmarks_to_dict(image.landmarks) if image.landmarks else None,
            }
            for image in manifest.images
        ],
        "relabels": [asdict(r) for r in manifest.relabels],
    }
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"


def verify_hashes(manifest: GoldenManifest, image_root: Path) -> list[str]:
    """Return the ids of every image whose file is missing or does not match its sha256."""
    mismatches: list[str] = []
    for image in manifest.images:
        file_path = image_root / image.relative_path
        if not file_path.is_file():
            mismatches.append(image.id)
            continue
        digest = hashlib.sha256(file_path.read_bytes()).hexdigest()
        if digest != image.sha256:
            mismatches.append(image.id)
    return mismatches


def record_relabel(
    manifest: GoldenManifest, image_id: str, new_label: str, new_reason: str | None, note: str
) -> GoldenManifest:
    """Return a *new* manifest with one image's label changed and the change logged.

    Never mutates `manifest`. Raises `KeyError` if `image_id` is not present.
    """
    if new_label not in VALID_LABELS:
        raise ValueError(f"invalid label {new_label!r}")

    updated_images: list[GoldenImage] = []
    old_label: str | None = None
    for image in manifest.images:
        if image.id == image_id:
            old_label = image.label
            image = replace(image, label=new_label, reason=new_reason)
        updated_images.append(image)

    if old_label is None:
        raise KeyError(image_id)

    relabel = Relabel(
        image_id=image_id,
        old_label=old_label,
        new_label=new_label,
        note=note,
        at=datetime.now(UTC).isoformat(timespec="seconds"),
    )
    return replace(manifest, images=tuple(updated_images), relabels=manifest.relabels + (relabel,))


def load_image(path: Path) -> np.ndarray:
    """Decode a JPEG/PNG file into an `(H, W, 3)` `uint8` RGB array. See ADR-0004."""
    with Image.open(path) as img:
        return np.array(img.convert("RGB"))


def stage_yield(
    manifest: GoldenManifest, image_root: Path
) -> dict[str, float | None]:
    """Run every image through `capture.process` and report per-stage conditional yield.

    Each value is the fraction of images that *reached* that stage which then *passed* it —
    a stage with no trained model behind it (`DETECTOR_NOT_TRAINED`, `LANDMARK_MODEL_NOT_TRAINED`)
    rejects every image it reaches, exactly as the deck's Block 4 requires: not implemented
    counts as reject, never as pass. `end_to_end` is the product of all five — REQ-001's
    `accept_rate`.
    """
    total = len(manifest.images)
    if total == 0:
        empty: dict[str, float | None] = {stage.value: None for stage in STAGE_ORDER}
        empty["end_to_end"] = None
        return empty

    reject_counts = dict.fromkeys(STAGE_ORDER, 0)
    passed = 0
    for image in manifest.images:
        frame = load_image(image_root / image.relative_path)
        result = process(frame)
        if isinstance(result, Reject):
            reject_counts[result.stage] += 1
        else:
            passed += 1

    rates: dict[str, float | None] = {}
    reached = total
    for stage in STAGE_ORDER:
        rejected_here = reject_counts[stage]
        rates[stage.value] = (reached - rejected_here) / reached if reached else None
        reached -= rejected_here
    rates["end_to_end"] = passed / total
    return rates


def _ground_truth_blur_score(frame: np.ndarray, landmarks: Landmarks) -> float:
    """Blur score on the crop aligned from *human-labelled* landmark points.

    Bypasses the untrained detector/landmarker on purpose (task-202) — this is what lets
    the blur/pose/illumination sweep run before those two models exist.
    """
    matrix, _residual = similarity_transform(landmarks.as_array(), CANONICAL_TEMPLATE)
    crop = warp_affine(frame, matrix)
    return laplacian_variance(crop)


@dataclass(frozen=True)
class SweepPoint:
    """One candidate threshold's cost, from a labelled sweep. See ADR-0005."""

    threshold: float
    bad_admitted: float
    good_rejected: float


def sweep_thresholds(
    manifest: GoldenManifest, image_root: Path, candidate_thresholds: list[float]
) -> list[SweepPoint]:
    """Sweep candidate blur thresholds against the ground-truth-landmarked subset.

    For every candidate cutoff: `bad_admitted` is the fraction of the `not_usable` pile
    that would still score at or above it, and `good_rejected` is the fraction of the
    `usable` pile that would score below it. Neither trends the wrong way as the threshold
    rises — that is `test_golden_capture.py`'s monotonicity check.
    """
    labelled = [image for image in manifest.images if image.landmarks is not None]
    if not labelled:
        return []

    usable_scores: list[float] = []
    not_usable_scores: list[float] = []
    for image in labelled:
        frame = load_image(image_root / image.relative_path)
        score = _ground_truth_blur_score(frame, image.landmarks)  # type: ignore[arg-type]
        (usable_scores if image.label == "usable" else not_usable_scores).append(score)

    points: list[SweepPoint] = []
    for threshold in candidate_thresholds:
        bad_admitted = (
            sum(1 for s in not_usable_scores if s >= threshold) / len(not_usable_scores)
            if not_usable_scores
            else 0.0
        )
        good_rejected = (
            sum(1 for s in usable_scores if s < threshold) / len(usable_scores)
            if usable_scores
            else 0.0
        )
        points.append(
            SweepPoint(threshold=threshold, bad_admitted=bad_admitted, good_rejected=good_rejected)
        )
    return points
