"""Alignment: rotate, scale and shift a photo until five points land in fixed positions.

No stretching or bending — a similarity transform only (facilitator guide, Idea 5). The
canonical template below is a chosen number, not a discovered one (OQ-012 tracks whether
Week 3's embedding accuracy argues for a different one).
"""

from __future__ import annotations

import numpy as np

from ml.capture.types import LANDMARK_NAMES

CROP_SIZE: int = 112

# Target positions for (left_eye, right_eye, nose, left_ear, right_ear) in a CROP_SIZE
# square, x right, y down. Eyes sit low-centre, nose below them, ears at the upper corners
# — the cat-face analogue of the standard human five-point alignment template. Chosen once;
# everything ever stored downstream depends on this choice (facilitator guide, "Canonical
# template").
CANONICAL_TEMPLATE: np.ndarray = np.array(
    [
        [38.0, 58.0],  # left_eye
        [74.0, 58.0],  # right_eye
        [56.0, 78.0],  # nose
        [18.0, 18.0],  # left_ear
        [94.0, 18.0],  # right_ear
    ],
    dtype=np.float64,
)

assert CANONICAL_TEMPLATE.shape == (len(LANDMARK_NAMES), 2)


def similarity_transform(src: np.ndarray, dst: np.ndarray) -> tuple[np.ndarray, float]:
    """Solve for the rotation, uniform scale and translation mapping `src` onto `dst`.

    Both are `(N, 2)` point arrays, `N >= 2`. Returns a `(2, 3)` affine matrix `[R*s | t]`
    and the residual: the mean per-point distance still remaining after the best-possible
    transform is applied (facilitator guide, "Residual" — free information about how
    implausible the pose was).
    """
    if src.shape != dst.shape or src.ndim != 2 or src.shape[1] != 2:
        raise ValueError(f"src and dst must both be (N, 2); got {src.shape} and {dst.shape}")
    if src.shape[0] < 2:
        raise ValueError("similarity_transform needs at least 2 point correspondences")

    n = src.shape[0]
    src_mean = src.mean(axis=0)
    dst_mean = dst.mean(axis=0)
    src_c = src - src_mean
    dst_c = dst - dst_mean

    covariance = (dst_c.T @ src_c) / n
    u, s, vt = np.linalg.svd(covariance)

    d = np.ones(2)
    if np.linalg.det(u) * np.linalg.det(vt) < 0:
        d[-1] = -1
    rotation = u @ np.diag(d) @ vt

    src_var = (src_c**2).sum() / n
    scale = float((s * d).sum() / src_var) if src_var > 1e-12 else 0.0

    translation = dst_mean - scale * (rotation @ src_mean)

    matrix = np.zeros((2, 3), dtype=np.float64)
    matrix[:, :2] = scale * rotation
    matrix[:, 2] = translation

    mapped = (matrix[:, :2] @ src.T).T + translation
    residual = float(np.sqrt(((mapped - dst) ** 2).sum(axis=1)).mean())
    return matrix, residual


def warp_affine(
    frame: np.ndarray, matrix: np.ndarray, output_size: int = CROP_SIZE
) -> np.ndarray:
    """Apply a forward `(2, 3)` affine matrix to `frame`, producing an `output_size` square.

    Pure numpy, bilinear-sampled, no OpenCV dependency. Pixels that map outside `frame` come
    back black (`0`) rather than wrapping or extrapolating.
    """
    if frame.ndim != 3 or frame.shape[2] != 3:
        raise ValueError(f"frame must be (H, W, 3); got {frame.shape}")

    linear = matrix[:, :2]
    translation = matrix[:, 2]
    linear_inv = np.linalg.inv(linear)

    ys, xs = np.mgrid[0:output_size, 0:output_size]
    dst_coords = np.stack([xs.ravel(), ys.ravel()], axis=1).astype(np.float64)
    src_coords = (dst_coords - translation) @ linear_inv.T

    src_h, src_w = frame.shape[:2]
    sx, sy = src_coords[:, 0], src_coords[:, 1]

    x0 = np.floor(sx).astype(np.int64)
    y0 = np.floor(sy).astype(np.int64)
    x1, y1 = x0 + 1, y0 + 1
    fx, fy = sx - x0, sy - y0

    in_bounds = (x0 >= 0) & (x1 < src_w) & (y0 >= 0) & (y1 < src_h)
    x0c, x1c = np.clip(x0, 0, src_w - 1), np.clip(x1, 0, src_w - 1)
    y0c, y1c = np.clip(y0, 0, src_h - 1), np.clip(y1, 0, src_h - 1)

    frame_f = frame.astype(np.float64)
    top = (
        frame_f[y0c, x0c] * (1 - fx)[:, None] + frame_f[y0c, x1c] * fx[:, None]
    )
    bottom = (
        frame_f[y1c, x0c] * (1 - fx)[:, None] + frame_f[y1c, x1c] * fx[:, None]
    )
    sampled = top * (1 - fy)[:, None] + bottom * fy[:, None]
    sampled[~in_bounds] = 0.0

    result = sampled.reshape(output_size, output_size, 3)
    return np.clip(result, 0, 255).astype(np.uint8)
