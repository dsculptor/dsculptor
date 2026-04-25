"""Newton fractal for z³ − 1 = 0.

Each pixel is colored by which root the iteration converges to, with
brightness modulated by how fast it got there. Three basins, each with a
fractal boundary — proof that even a 'simple' polynomial hides chaos.
"""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from .escape import BBox, _grid
from .palette import hsv_to_rgb

NEWTON_BBOX = BBox(-1.5, 1.5, -1.5, 1.5)
ROOTS = np.array(
    [1.0 + 0.0j, np.exp(2j * np.pi / 3), np.exp(-2j * np.pi / 3)],
    dtype=np.complex128,
)


def render_newton(
    *,
    width: int,
    height: int,
    bbox: BBox = NEWTON_BBOX,
    max_iter: int = 60,
    tol: float = 1e-6,
) -> tuple[NDArray[np.int8], NDArray[np.float32]]:
    """Run Newton's method on z³−1 over a grid. Returns (root_id, iters)."""
    z = _grid(width, height, bbox)
    root_id = np.full(z.shape, -1, dtype=np.int8)
    iters = np.zeros(z.shape, dtype=np.float32)
    for i in range(max_iter):
        z = z - (z**3 - 1.0) / (3.0 * z**2 + 1e-30)
        for k in range(3):
            close = (root_id == -1) & (np.abs(z - ROOTS[k]) < tol)
            root_id[close] = k
            iters[close] = i
        if (root_id >= 0).all():
            break
    return root_id, iters


def colorize_newton(
    root_id: NDArray[np.int8],
    iters: NDArray[np.float32],
    max_iter: int = 60,
) -> NDArray[np.uint8]:
    """One hue per root family, brightness fades with iteration count."""
    hues = np.array([0.0, 120.0, 240.0], dtype=np.float32)
    safe_idx = np.clip(root_id, 0, 2).astype(np.int32)
    h = np.where(root_id >= 0, hues[safe_idx], 0.0).astype(np.float32)
    s = np.where(root_id >= 0, 0.85, 0.0).astype(np.float32)
    v = np.clip(1.0 - iters / max_iter, 0.1, 1.0).astype(np.float32)
    rgb = hsv_to_rgb(h, s, v)
    out: NDArray[np.uint8] = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    return out
