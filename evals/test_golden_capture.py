"""Tests for the golden capture manifest and sweep — task-201, task-202."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from evals import golden_capture
from ml.capture.align import CANONICAL_TEMPLATE
from ml.capture.types import LANDMARK_NAMES, Landmarks, Point


def _write_manifest(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")


def _write_image(path: Path, array: np.ndarray) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(array).save(path)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _landmarks_dict(offset: tuple[float, float]) -> dict[str, list[float]]:
    points = CANONICAL_TEMPLATE + np.array(offset)
    return {name: list(points[i]) for i, name in enumerate(LANDMARK_NAMES)}


def _landmarks(offset: tuple[float, float]) -> Landmarks:
    points = CANONICAL_TEMPLATE + np.array(offset)
    kwargs = {name: Point(*points[i]) for i, name in enumerate(LANDMARK_NAMES)}
    return Landmarks(confidence=1.0, **kwargs)


def _single_image_manifest(
    image_id: str, relative_path: str, sha256: str, label: str = "usable"
) -> golden_capture.GoldenManifest:
    image = golden_capture.GoldenImage(
        id=image_id, relative_path=relative_path, sha256=sha256, label=label
    )
    return golden_capture.GoldenManifest(version=1, images=(image,))


def _sharp_checkerboard(size: int = 200) -> np.ndarray:
    xs, ys = np.meshgrid(np.arange(size), np.arange(size))
    pattern = (((xs // 4) + (ys // 4)) % 2) * 255
    return np.stack([pattern, pattern, pattern], axis=2).astype(np.uint8)


def _flat_frame(size: int = 200, value: int = 128) -> np.ndarray:
    return np.full((size, size, 3), value, dtype=np.uint8)


def _box_blur(image: np.ndarray, passes: int = 4) -> np.ndarray:
    blurred = image.astype(np.float64)
    for _ in range(passes):
        padded = np.pad(blurred, ((1, 1), (1, 1), (0, 0)), mode="edge")
        up, down = padded[0:-2, 1:-1], padded[2:, 1:-1]
        left, right, center = padded[1:-1, 0:-2], padded[1:-1, 2:], padded[1:-1, 1:-1]
        blurred = (up + down + left + right + center) / 5.0
    return blurred.astype(np.uint8)


# ---------------------------------------------------------------------------
# load_manifest / schema
# ---------------------------------------------------------------------------


def test_load_manifest_empty_images_list(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(manifest_path, {"version": 1, "images": []})

    manifest = golden_capture.load_manifest(manifest_path)

    assert manifest.version == 1
    assert manifest.images == ()


def test_load_manifest_missing_file_raises() -> None:
    with pytest.raises(FileNotFoundError):
        golden_capture.load_manifest(Path("/nonexistent/manifest.json"))


def test_load_manifest_rejects_entry_missing_required_field(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        {"version": 1, "images": [{"id": "a", "relative_path": "a.jpg", "label": "usable"}]},
    )

    with pytest.raises(ValueError, match="missing fields"):
        golden_capture.load_manifest(manifest_path)


def test_load_manifest_rejects_not_usable_without_a_reason(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        {
            "version": 1,
            "images": [
                {"id": "a", "relative_path": "a.jpg", "sha256": "x" * 64, "label": "not_usable"}
            ],
        },
    )

    with pytest.raises(ValueError, match="missing a reason"):
        golden_capture.load_manifest(manifest_path)


def test_load_manifest_round_trips_through_dump_manifest(tmp_path: Path) -> None:
    manifest_path = tmp_path / "manifest.json"
    _write_manifest(
        manifest_path,
        {
            "version": 1,
            "images": [
                {
                    "id": "a",
                    "relative_path": "a.jpg",
                    "sha256": "x" * 64,
                    "label": "usable",
                    "landmarks": _landmarks_dict((0.0, 0.0)),
                }
            ],
        },
    )

    manifest = golden_capture.load_manifest(manifest_path)
    round_tripped_path = tmp_path / "round_tripped.json"
    round_tripped_path.write_text(golden_capture.dump_manifest(manifest), encoding="utf-8")

    assert golden_capture.load_manifest(round_tripped_path) == manifest


# ---------------------------------------------------------------------------
# verify_hashes
# ---------------------------------------------------------------------------


def test_verify_hashes_passes_when_bytes_match(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    digest = _write_image(image_root / "a.jpg", _flat_frame())
    manifest = _single_image_manifest("a", "a.jpg", digest)

    assert golden_capture.verify_hashes(manifest, image_root) == []


def test_verify_hashes_flags_a_tampered_file(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    digest = _write_image(image_root / "a.jpg", _flat_frame())
    (image_root / "a.jpg").write_bytes(b"tampered bytes, not the original image")
    manifest = _single_image_manifest("a", "a.jpg", digest)

    assert golden_capture.verify_hashes(manifest, image_root) == ["a"]


def test_verify_hashes_flags_a_missing_file(tmp_path: Path) -> None:
    manifest = _single_image_manifest("a", "missing.jpg", "x" * 64)

    assert golden_capture.verify_hashes(manifest, tmp_path) == ["a"]


# ---------------------------------------------------------------------------
# record_relabel
# ---------------------------------------------------------------------------


def test_record_relabel_does_not_mutate_the_original_and_appends_one_entry() -> None:
    original = _single_image_manifest("a", "a.jpg", "x" * 64)
    note = "mislabelled on first pass"

    updated = golden_capture.record_relabel(original, "a", "not_usable", "blur", note)

    assert original.images[0].label == "usable"
    assert original.relabels == ()
    assert updated.images[0].label == "not_usable"
    assert updated.images[0].reason == "blur"
    assert len(updated.relabels) == 1
    assert updated.relabels[0].old_label == "usable"
    assert updated.relabels[0].new_label == "not_usable"


def test_record_relabel_raises_on_an_unknown_id() -> None:
    manifest = golden_capture.GoldenManifest(version=1, images=())

    with pytest.raises(KeyError):
        golden_capture.record_relabel(manifest, "missing", "usable", None, "note")


# ---------------------------------------------------------------------------
# stage_yield
# ---------------------------------------------------------------------------


def test_stage_yield_on_empty_manifest_is_all_none() -> None:
    manifest = golden_capture.GoldenManifest(version=1, images=())

    rates = golden_capture.stage_yield(manifest, Path("."))

    assert rates["end_to_end"] is None
    assert all(value is None for value in rates.values())


def test_stage_yield_with_untrained_detector_rejects_every_image_at_detect(
    tmp_path: Path,
) -> None:
    image_root = tmp_path / "images"
    digest = _write_image(image_root / "a.jpg", _sharp_checkerboard())
    manifest = _single_image_manifest("a", "a.jpg", digest)

    rates = golden_capture.stage_yield(manifest, image_root)

    assert rates["detect"] == 0.0
    assert rates["select"] is None
    assert rates["end_to_end"] == 0.0


# ---------------------------------------------------------------------------
# sweep_thresholds
# ---------------------------------------------------------------------------


def test_sweep_thresholds_is_empty_without_ground_truth_landmarks() -> None:
    manifest = _single_image_manifest("a", "a.jpg", "x" * 64)

    assert golden_capture.sweep_thresholds(manifest, Path("."), [100.0]) == []


def test_sweep_thresholds_curves_are_monotonic(tmp_path: Path) -> None:
    image_root = tmp_path / "images"
    sharp = _sharp_checkerboard()
    sharp_digest = _write_image(image_root / "sharp.jpg", sharp)
    blurry_digest = _write_image(image_root / "blurry.jpg", _box_blur(sharp))
    landmarks = _landmarks((44.0, 44.0))

    sharp_image = golden_capture.GoldenImage(
        id="sharp",
        relative_path="sharp.jpg",
        sha256=sharp_digest,
        label="usable",
        landmarks=landmarks,
    )
    blurry_image = golden_capture.GoldenImage(
        id="blurry",
        relative_path="blurry.jpg",
        sha256=blurry_digest,
        label="not_usable",
        reason="blur",
        landmarks=landmarks,
    )
    manifest = golden_capture.GoldenManifest(version=1, images=(sharp_image, blurry_image))

    thresholds = [500.0, 5000.0, 50000.0, 150000.0]
    points = golden_capture.sweep_thresholds(manifest, image_root, thresholds)

    bad_admitted = [p.bad_admitted for p in points]
    good_rejected = [p.good_rejected for p in points]
    assert bad_admitted == sorted(bad_admitted, reverse=True)
    assert good_rejected == sorted(good_rejected)
    # At the lowest threshold the blurry image still gets admitted; at the highest, the
    # sharp one gets wrongly rejected. Both curves actually move, not just stay flat.
    assert points[0].bad_admitted == 1.0
    assert points[-1].good_rejected == 1.0
