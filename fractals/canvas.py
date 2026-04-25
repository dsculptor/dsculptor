"""Image I/O helper — saves an (H, W, 3) uint8 array as a PNG."""

from __future__ import annotations

from pathlib import Path

import numpy as np
from numpy.typing import NDArray
from PIL import Image


def save_rgb(pixels: NDArray[np.uint8], out: Path) -> Path:
    """Write an (H, W, 3) uint8 array to `out` as PNG. Creates parent dirs."""
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(pixels, mode="RGB").save(out)
    return out
