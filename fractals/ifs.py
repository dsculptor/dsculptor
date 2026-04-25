"""Iterated Function Systems via the chaos game.

Sierpinski triangle and the Barnsley fern: pick an affine map at random
(weighted), apply it to the current point, plot the result. After ~10⁵–10⁶
points the attractor emerges. The simplest beautiful idea in fractals.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass(frozen=True)
class Affine:
    """2D affine transform: (x, y) → (a x + b y + e, c x + d y + f)."""

    a: float
    b: float
    c: float
    d: float
    e: float
    f: float


# ------------------------------------------------------------------------------
# preset systems
# ------------------------------------------------------------------------------

SIERPINSKI: tuple[tuple[Affine, float], ...] = (
    (Affine(0.5, 0.0, 0.0, 0.5, 0.00, 0.0), 1 / 3),
    (Affine(0.5, 0.0, 0.0, 0.5, 0.50, 0.0), 1 / 3),
    (Affine(0.5, 0.0, 0.0, 0.5, 0.25, 0.5), 1 / 3),
)

# Barnsley's classic stochastic fern (Fractals Everywhere, 1988).
FERN: tuple[tuple[Affine, float], ...] = (
    (Affine(0.00, 0.00, 0.00, 0.16, 0.00, 0.00), 0.01),
    (Affine(0.85, 0.04, -0.04, 0.85, 0.00, 1.60), 0.85),
    (Affine(0.20, -0.26, 0.23, 0.22, 0.00, 1.60), 0.07),
    (Affine(-0.15, 0.28, 0.26, 0.24, 0.00, 0.44), 0.07),
)


# ------------------------------------------------------------------------------
# chaos game + rasterizer
# ------------------------------------------------------------------------------


def chaos_game(
    system: tuple[tuple[Affine, float], ...],
    n_points: int,
    *,
    seed: int = 0,
) -> NDArray[np.float64]:
    """Run the chaos game and return an (n_points, 2) array of points."""
    rng = np.random.default_rng(seed)
    affines = np.array([(t.a, t.b, t.c, t.d, t.e, t.f) for t, _ in system])
    weights = np.array([w for _, w in system], dtype=np.float64)
    weights /= weights.sum()
    choices = rng.choice(len(system), size=n_points, p=weights)
    pts = np.empty((n_points, 2), dtype=np.float64)
    x, y = 0.0, 0.0
    for i in range(n_points):
        a, b, c, d, e, f = affines[choices[i]]
        x, y = a * x + b * y + e, c * x + d * y + f
        pts[i] = (x, y)
    return pts


def rasterize(
    pts: NDArray[np.float64],
    width: int,
    height: int,
    *,
    padding: float = 0.05,
    color: tuple[int, int, int] = (120, 220, 90),
) -> NDArray[np.uint8]:
    """Rasterize point cloud to image, log-scale density for nice contrast."""
    x, y = pts[:, 0], pts[:, 1]
    x0, x1, y0, y1 = x.min(), x.max(), y.min(), y.max()
    pad_x = (x1 - x0) * padding
    pad_y = (y1 - y0) * padding
    px = ((x - x0 + pad_x) / (x1 - x0 + 2 * pad_x) * (width - 1)).astype(np.int32)
    py = ((y1 + pad_y - y) / (y1 - y0 + 2 * pad_y) * (height - 1)).astype(np.int32)
    density = np.zeros((height, width), dtype=np.int32)
    np.add.at(density, (py, px), 1)
    norm = np.log1p(density.astype(np.float32))
    norm /= max(float(norm.max()), 1e-9)
    img = np.zeros((height, width, 3), dtype=np.uint8)
    for ch in range(3):
        img[..., ch] = (norm * color[ch]).astype(np.uint8)
    return img
