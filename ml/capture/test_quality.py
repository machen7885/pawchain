"""Tests for the quality gate — task-203 acceptance criteria 1, 2, 3."""

from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pytest

from ml.capture.quality import BLUR_THRESHOLD, illumination_stats, laplacian_variance

ML_DIR = Path(__file__).resolve().parent.parent


def _sharp_checkerboard(size: int = 112) -> np.ndarray:
    xs, ys = np.meshgrid(np.arange(size), np.arange(size))
    pattern = (((xs // 4) + (ys // 4)) % 2) * 255
    return np.stack([pattern, pattern, pattern], axis=2).astype(np.uint8)


def _box_blur(image: np.ndarray, passes: int = 6) -> np.ndarray:
    blurred = image.astype(np.float64)
    for _ in range(passes):
        padded = np.pad(blurred, ((1, 1), (1, 1), (0, 0)), mode="edge")
        up, down = padded[0:-2, 1:-1], padded[2:, 1:-1]
        left, right, center = padded[1:-1, 0:-2], padded[1:-1, 2:], padded[1:-1, 1:-1]
        blurred = (up + down + left + right + center) / 5.0
    return blurred.astype(np.uint8)


def test_laplacian_variance_returns_a_float_for_a_valid_crop() -> None:
    crop = _sharp_checkerboard()
    result = laplacian_variance(crop)
    assert isinstance(result, float)


def test_laplacian_variance_raises_on_a_too_small_crop() -> None:
    with pytest.raises(ValueError, match="at least 3x3"):
        laplacian_variance(np.zeros((2, 2, 3), dtype=np.uint8))


def test_laplacian_variance_raises_on_a_wrongly_shaped_crop() -> None:
    with pytest.raises(ValueError, match="must be"):
        laplacian_variance(np.zeros((10, 10, 4), dtype=np.uint8))


def test_sharp_image_scores_higher_than_a_blurred_version_of_the_same_image() -> None:
    sharp = _sharp_checkerboard()
    blurry = _box_blur(sharp)

    assert laplacian_variance(sharp) > laplacian_variance(blurry)


def test_blur_threshold_decision_matches_the_sharp_and_blurry_fixtures() -> None:
    sharp = _sharp_checkerboard()
    blurry = _box_blur(sharp, passes=10)

    assert laplacian_variance(sharp) >= BLUR_THRESHOLD
    assert laplacian_variance(blurry) < BLUR_THRESHOLD


def test_blur_threshold_is_a_single_named_constant() -> None:
    """Task-203 #3: 120 appears nowhere in ml/ except the BLUR_THRESHOLD definition."""
    pattern = re.compile(r"(?<![\w.])120(?![\w.])")
    offending: list[str] = []
    for path in ML_DIR.rglob("*.py"):
        if path.name.startswith("test_"):
            continue
        for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if "BLUR_THRESHOLD" in line:
                continue
            if pattern.search(line):
                offending.append(f"{path}:{lineno}: {line.strip()}")
    assert not offending, f"literal 120 found outside BLUR_THRESHOLD: {offending}"


def test_illumination_stats_flags_a_blown_out_crop() -> None:
    blown_out = np.full((112, 112, 3), 255, dtype=np.uint8)
    clipped, luminance = illumination_stats(blown_out)
    assert clipped == pytest.approx(1.0)
    assert luminance == pytest.approx(255.0)


def test_illumination_stats_on_a_mid_gray_crop_reports_no_clipping() -> None:
    mid_gray = np.full((112, 112, 3), 128, dtype=np.uint8)
    clipped, luminance = illumination_stats(mid_gray)
    assert clipped == 0.0
    assert luminance == pytest.approx(128.0)
