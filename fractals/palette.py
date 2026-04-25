"""Color helpers: vectorized HSV→RGB and the escape-time colorizer."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

# ------------------------------------------------------------------------------
# hsv → rgb
# ------------------------------------------------------------------------------


def hsv_to_rgb(
    h: NDArray[np.floating],
    s: NDArray[np.floating],
    v: NDArray[np.floating],
) -> NDArray[np.floating]:
    """Vectorized HSV→RGB. h in [0, 360), s and v in [0, 1]. Returns (..., 3)."""
    c = v * s
    h6 = (h / 60.0) % 6.0
    x = c * (1.0 - np.abs(h6 % 2.0 - 1.0))
    zero = np.zeros_like(c)
    sector = h6.astype(np.int32) % 6
    r = np.choose(sector, [c, x, zero, zero, x, c])
    g = np.choose(sector, [x, c, c, x, zero, zero])
    b = np.choose(sector, [zero, zero, x, c, c, x])
    m = v - c
    return np.stack([r + m, g + m, b + m], axis=-1)


# ------------------------------------------------------------------------------
# escape-time colorizer
# ------------------------------------------------------------------------------


def colorize_escape(
    iters: NDArray[np.floating],
    max_iter: int,
    *,
    hue_shift: float = 0.0,
) -> NDArray[np.uint8]:
    """Map smooth escape-time values to an RGB image. Interior pixels go black.

    Quick-escape pixels (away from the boundary) are saturated and bright; the
    hue rotates with iteration count so detail near the boundary stays visible.
    `hue_shift` rotates the whole palette to differentiate variants.
    """
    interior = iters >= max_iter - 0.5
    norm = np.clip(iters / max_iter, 0.0, 1.0).astype(np.float32)
    hue = (np.sqrt(norm) * 360.0 + hue_shift) % 360.0
    sat = np.where(interior, 0.0, 0.85).astype(np.float32)
    val = np.where(interior, 0.0, 0.55 + 0.45 * np.sqrt(norm)).astype(np.float32)
    rgb = hsv_to_rgb(hue, sat, val)
    out: NDArray[np.uint8] = (np.clip(rgb, 0.0, 1.0) * 255.0).astype(np.uint8)
    return out
