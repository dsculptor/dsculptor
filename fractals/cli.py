"""Typer CLI: `uv run fractals <subcommand> [...]`."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import numpy as np
import typer
from numpy.typing import NDArray

from . import canvas, escape, palette
from . import newton as _newton
from .ifs import FERN, SIERPINSKI, chaos_game, rasterize
from .lsystem import KOCH, TREE, render_lsystem

app = typer.Typer(
    add_completion=False,
    help="Render the classic fractals — escape-time, Newton, IFS, L-systems.",
    no_args_is_help=True,
)

# ------------------------------------------------------------------------------
# shared option types
# ------------------------------------------------------------------------------

WidthOpt = Annotated[int, typer.Option("--width", "-w", help="Image width in px.")]
HeightOpt = Annotated[int, typer.Option("--height", "-H", help="Image height in px.")]
IterOpt = Annotated[int, typer.Option("--iters", "-i", help="Max iterations.")]
OutOpt = Annotated[Path, typer.Option("--out", "-o", help="Output PNG path.")]
PointsOpt = Annotated[
    int, typer.Option("--points", "-n", help="Chaos game point count.")
]
DepthOpt = Annotated[int, typer.Option("--depth", "-d", help="L-system rewrite depth.")]


def _save(pixels: NDArray[np.uint8], out: Path) -> None:
    saved = canvas.save_rgb(pixels, out)
    typer.echo(f"wrote {saved}")


# ------------------------------------------------------------------------------
# escape-time family
# ------------------------------------------------------------------------------


@app.command()
def mandelbrot(
    width: WidthOpt = 1600,
    height: HeightOpt = 1200,
    iters: IterOpt = 256,
    out: OutOpt = Path("gallery/mandelbrot.png"),
) -> None:
    """The Mandelbrot set."""
    arr = escape.render_escape(
        width=width,
        height=height,
        bbox=escape.MANDELBROT_BBOX,
        max_iter=iters,
        kernel=escape.mandel_kernel,
    )
    _save(palette.colorize_escape(arr, iters), out)


JuliaSeedOpt = Annotated[
    str, typer.Option("--c", "-c", help="Seed, e.g. -0.7+0.27015j.")
]


@app.command()
def julia(
    c: JuliaSeedOpt = "-0.7+0.27015j",
    width: WidthOpt = 1600,
    height: HeightOpt = 1200,
    iters: IterOpt = 256,
    out: OutOpt = Path("gallery/julia.png"),
) -> None:
    """A Julia set for the given complex seed."""
    seed = complex(c)
    arr = escape.render_escape(
        width=width,
        height=height,
        bbox=escape.JULIA_BBOX,
        max_iter=iters,
        kernel=escape.mandel_kernel,
        c0=seed,
    )
    _save(palette.colorize_escape(arr, iters, hue_shift=180.0), out)


@app.command(name="burning-ship")
def burning_ship(
    width: WidthOpt = 1600,
    height: HeightOpt = 1200,
    iters: IterOpt = 256,
    out: OutOpt = Path("gallery/burning_ship.png"),
) -> None:
    """The Burning Ship — Mandelbrot with absolute values."""
    arr = escape.render_escape(
        width=width,
        height=height,
        bbox=escape.BURNING_BBOX,
        max_iter=iters,
        kernel=escape.burning_kernel,
    )
    _save(palette.colorize_escape(arr, iters, hue_shift=30.0), out)


# ------------------------------------------------------------------------------
# newton family
# ------------------------------------------------------------------------------


@app.command()
def newton(
    width: WidthOpt = 1200,
    height: HeightOpt = 1200,
    iters: IterOpt = 60,
    out: OutOpt = Path("gallery/newton.png"),
) -> None:
    """Newton fractal for z³ − 1."""
    root_id, it = _newton.render_newton(width=width, height=height, max_iter=iters)
    _save(_newton.colorize_newton(root_id, it, max_iter=iters), out)


# ------------------------------------------------------------------------------
# ifs family (chaos game)
# ------------------------------------------------------------------------------


@app.command()
def sierpinski(
    width: WidthOpt = 1024,
    height: HeightOpt = 1024,
    points: PointsOpt = 300_000,
    out: OutOpt = Path("gallery/sierpinski.png"),
) -> None:
    """Sierpinski triangle via the chaos game."""
    pts = chaos_game(SIERPINSKI, points)
    _save(rasterize(pts, width, height, color=(180, 200, 255)), out)


@app.command()
def fern(
    width: WidthOpt = 800,
    height: HeightOpt = 1200,
    points: PointsOpt = 500_000,
    out: OutOpt = Path("gallery/fern.png"),
) -> None:
    """Barnsley fern via the chaos game."""
    pts = chaos_game(FERN, points)
    _save(rasterize(pts, width, height, color=(120, 220, 90)), out)


# ------------------------------------------------------------------------------
# l-system family
# ------------------------------------------------------------------------------


@app.command()
def koch(
    depth: DepthOpt = 5,
    width: WidthOpt = 1600,
    height: HeightOpt = 1600,
    out: OutOpt = Path("gallery/koch.png"),
) -> None:
    """Koch snowflake via L-system."""
    img = render_lsystem(KOCH, depth, width=width, height=height)
    _save(img, out)


@app.command()
def tree(
    depth: DepthOpt = 5,
    width: WidthOpt = 1200,
    height: HeightOpt = 1600,
    out: OutOpt = Path("gallery/tree.png"),
) -> None:
    """Recursive fractal tree via L-system."""
    img = render_lsystem(TREE, depth, width=width, height=height)
    _save(img, out)


# ------------------------------------------------------------------------------
# render-everything
# ------------------------------------------------------------------------------


def _render_gallery(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    mandelbrot(out=out_dir / "mandelbrot.png")
    julia(out=out_dir / "julia.png")
    burning_ship(out=out_dir / "burning_ship.png")
    newton(out=out_dir / "newton.png")
    sierpinski(out=out_dir / "sierpinski.png")
    fern(out=out_dir / "fern.png")
    koch(out=out_dir / "koch.png")
    tree(out=out_dir / "tree.png")


@app.command(name="all")
def render_all(
    out_dir: Annotated[
        Path, typer.Option("--out-dir", "-o", help="Gallery directory.")
    ] = Path("gallery"),
) -> None:
    """Render every fractal at default settings into a gallery directory."""
    _render_gallery(out_dir)


def build_all() -> None:
    """`uv run build-all` — render the canonical gallery into ./gallery/."""
    _render_gallery(Path("gallery"))
