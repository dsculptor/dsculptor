"""Escape-time fractals: Mandelbrot, Julia, Burning Ship.

All three share the same iteration scaffolding; only the per-step kernel
differs. Smooth coloring (the standard log-log normalization) removes the
visible iteration banding without any extra cost.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

Complex = NDArray[np.complexfloating]
Real = NDArray[np.floating]
Kernel = Callable[[Complex, Complex], Complex]


# ------------------------------------------------------------------------------
# bbox + grid
# ------------------------------------------------------------------------------


@dataclass(frozen=True)
class BBox:
    """Axis-aligned viewing window in the complex plane."""

    x_min: float
    x_max: float
    y_min: float
    y_max: float


def _grid(width: int, height: int, bbox: BBox) -> Complex:
    x = np.linspace(bbox.x_min, bbox.x_max, width)
    y = np.linspace(bbox.y_min, bbox.y_max, height)
    return (x[None, :] + 1j * y[:, None]).astype(np.complex128)


# ------------------------------------------------------------------------------
# generic engine
# ------------------------------------------------------------------------------


def render_escape(
    *,
    width: int,
    height: int,
    bbox: BBox,
    max_iter: int,
    kernel: Kernel,
    c0: complex | None = None,
) -> Real:
    """Run an escape-time iteration. Returns smooth iteration counts (H, W).

    `c0=None` → Mandelbrot-style (c=grid, z₀=0).
    `c0` set → Julia-style (c is fixed, z₀=grid).
    """
    grid = _grid(width, height, bbox)
    if c0 is None:
        z = np.zeros_like(grid)
        c: Complex = grid
    else:
        z = grid.copy()
        c = np.full_like(grid, c0)
    iters = np.full(grid.shape, float(max_iter), dtype=np.float32)
    active = np.ones(grid.shape, dtype=bool)
    log2 = np.log(2.0)
    for i in range(max_iter):
        z[active] = kernel(z[active], c[active])
        escaped = active & (np.abs(z) > 2.0)
        if escaped.any():
            zr = np.abs(z[escaped])
            iters[escaped] = i + 1 - np.log(np.log(zr)) / log2
        active &= ~escaped
        if not active.any():
            break
    return iters


# ------------------------------------------------------------------------------
# kernels + bboxes
# ------------------------------------------------------------------------------


def mandel_kernel(z: Complex, c: Complex) -> Complex:
    """Standard Mandelbrot/Julia step: z ↦ z² + c."""
    return z * z + c


def burning_kernel(z: Complex, c: Complex) -> Complex:
    """Burning Ship step: z ↦ (|Re z| + i|Im z|)² + c."""
    return (np.abs(z.real) + 1j * np.abs(z.imag)) ** 2 + c


MANDELBROT_BBOX = BBox(-2.2, 1.0, -1.3, 1.3)
JULIA_BBOX = BBox(-1.6, 1.6, -1.2, 1.2)
BURNING_BBOX = BBox(-2.0, 1.5, -2.0, 1.0)
