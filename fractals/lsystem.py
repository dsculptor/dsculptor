"""L-system rewriting + turtle drawing.

Two presets ship: the Koch snowflake and a recursive tree. An L-system
expands a string by replacing characters according to fixed rules; a
small turtle then walks the expanded string and emits line segments.
The whole pipeline fits on a postcard.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
from PIL import Image, ImageDraw

# ------------------------------------------------------------------------------
# rewriting
# ------------------------------------------------------------------------------


@dataclass(frozen=True)
class LSystem:
    """An L-system: axiom + production rules + turtle turn angle (degrees)."""

    axiom: str
    rules: dict[str, str]
    angle: float


KOCH = LSystem(
    axiom="F--F--F",
    rules={"F": "F+F--F+F"},
    angle=60.0,
)

TREE = LSystem(
    axiom="F",
    rules={"F": "FF+[+F-F-F]-[-F+F+F]"},
    angle=22.5,
)


def expand(system: LSystem, depth: int) -> str:
    """Apply the rewriting rules `depth` times to the axiom."""
    s = system.axiom
    for _ in range(depth):
        s = "".join(system.rules.get(ch, ch) for ch in s)
    return s


# ------------------------------------------------------------------------------
# turtle walk
# ------------------------------------------------------------------------------

Segment = tuple[float, float, float, float]


def walk(s: str, angle_deg: float) -> list[Segment]:
    """Walk an expanded L-system string. Returns line segments [(x0,y0,x1,y1)]."""
    angle = math.radians(angle_deg)
    x, y, theta = 0.0, 0.0, math.pi / 2
    stack: list[tuple[float, float, float]] = []
    segs: list[Segment] = []
    for ch in s:
        if ch in "Ff":
            nx, ny = x + math.cos(theta), y + math.sin(theta)
            if ch == "F":
                segs.append((x, y, nx, ny))
            x, y = nx, ny
        elif ch == "+":
            theta += angle
        elif ch == "-":
            theta -= angle
        elif ch == "[":
            stack.append((x, y, theta))
        elif ch == "]":
            x, y, theta = stack.pop()
    return segs


# ------------------------------------------------------------------------------
# rasterize
# ------------------------------------------------------------------------------


def _fit(
    segs: list[Segment], width: int, height: int, padding: int
) -> tuple[float, float, float]:
    arr = np.array(segs)
    x0, x1 = float(arr[:, [0, 2]].min()), float(arr[:, [0, 2]].max())
    y0, y1 = float(arr[:, [1, 3]].min()), float(arr[:, [1, 3]].max())
    sx = (width - 2 * padding) / max(x1 - x0, 1e-9)
    sy = (height - 2 * padding) / max(y1 - y0, 1e-9)
    return x0, y0, min(sx, sy)


def render_lsystem(
    system: LSystem,
    depth: int,
    *,
    width: int = 1024,
    height: int = 1024,
    padding: int = 32,
    fg: tuple[int, int, int] = (220, 230, 255),
    bg: tuple[int, int, int] = (8, 10, 16),
) -> NDArray[np.uint8]:
    """Expand, walk, and rasterize an L-system to an RGB array."""
    segs = walk(expand(system, depth), system.angle)
    if not segs:
        return np.zeros((height, width, 3), dtype=np.uint8)
    x0, y0, s = _fit(segs, width, height, padding)
    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    for a, b, c, d in segs:
        draw.line(
            (
                padding + (a - x0) * s,
                height - padding - (b - y0) * s,
                padding + (c - x0) * s,
                height - padding - (d - y0) * s,
            ),
            fill=fg,
            width=1,
        )
    return np.array(img)
