"""Tests for the similarity transform and the warp — task-203 acceptance criteria 4, 9."""

from __future__ import annotations

import numpy as np
import pytest

from ml.capture.align import CROP_SIZE, similarity_transform, warp_affine


def _rotation_matrix(degrees: float) -> np.ndarray:
    theta = np.radians(degrees)
    return np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])


def test_similarity_transform_recovers_a_known_rotation_scale_and_shift() -> None:
    src = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [5.0, 5.0]])
    true_rotation = _rotation_matrix(30.0)
    true_scale = 2.0
    true_translation = np.array([7.0, -3.0])
    dst = (true_scale * (true_rotation @ src.T).T) + true_translation

    matrix, residual = similarity_transform(src, dst)

    assert residual < 1e-8
    recovered_linear = matrix[:, :2]
    expected_linear = true_scale * true_rotation
    assert np.allclose(recovered_linear, expected_linear, atol=1e-6)
    assert np.allclose(matrix[:, 2], true_translation, atol=1e-6)


def test_similarity_transform_reports_nonzero_residual_for_an_implausible_pose() -> None:
    src = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [5.0, 12.0]])
    dst = np.array([[0.0, 0.0], [10.0, 0.0], [10.0, 10.0], [0.0, 10.0], [5.0, 5.0]])

    _matrix, residual = similarity_transform(src, dst)

    assert residual > 0.5


def test_similarity_transform_rejects_mismatched_shapes() -> None:
    with pytest.raises(ValueError, match="src and dst"):
        similarity_transform(np.zeros((3, 2)), np.zeros((4, 2)))


def test_warp_affine_under_identity_reproduces_the_source_region_exactly() -> None:
    frame = np.random.default_rng(0).integers(0, 256, size=(200, 200, 3), dtype=np.uint8)
    identity = np.array([[1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])

    crop = warp_affine(frame, identity, output_size=CROP_SIZE)

    assert crop.shape == (CROP_SIZE, CROP_SIZE, 3)
    assert np.array_equal(crop, frame[:CROP_SIZE, :CROP_SIZE])


def test_warp_affine_out_of_bounds_pixels_come_back_black() -> None:
    frame = np.full((50, 50, 3), 255, dtype=np.uint8)
    # Shift far enough that most of the output samples outside the source frame.
    shifted = np.array([[1.0, 0.0, 1000.0], [0.0, 1.0, 1000.0]])

    crop = warp_affine(frame, shifted, output_size=CROP_SIZE)

    assert np.all(crop == 0)


def test_warp_affine_rejects_a_non_hwc_frame() -> None:
    with pytest.raises(ValueError, match="frame must be"):
        warp_affine(np.zeros((10, 10)), np.eye(2, 3))
