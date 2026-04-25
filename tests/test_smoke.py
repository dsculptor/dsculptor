"""Smoke tests — every renderer produces a small image of the expected shape."""

from __future__ import annotations

from fractals import escape, ifs, lsystem, newton, palette


def test_mandelbrot_shape() -> None:
    arr = escape.render_escape(
        width=64,
        height=48,
        bbox=escape.MANDELBROT_BBOX,
        max_iter=32,
        kernel=escape.mandel_kernel,
    )
    img = palette.colorize_escape(arr, 32)
    assert img.shape == (48, 64, 3)
    assert img.dtype.name == "uint8"


def test_julia_shape() -> None:
    arr = escape.render_escape(
        width=64,
        height=48,
        bbox=escape.JULIA_BBOX,
        max_iter=32,
        kernel=escape.mandel_kernel,
        c0=complex(-0.7, 0.27),
    )
    img = palette.colorize_escape(arr, 32)
    assert img.shape == (48, 64, 3)


def test_burning_ship_shape() -> None:
    arr = escape.render_escape(
        width=64,
        height=48,
        bbox=escape.BURNING_BBOX,
        max_iter=32,
        kernel=escape.burning_kernel,
    )
    img = palette.colorize_escape(arr, 32)
    assert img.shape == (48, 64, 3)


def test_newton_shape() -> None:
    root_id, it = newton.render_newton(width=64, height=64, max_iter=20)
    img = newton.colorize_newton(root_id, it, max_iter=20)
    assert img.shape == (64, 64, 3)


def test_sierpinski_shape() -> None:
    pts = ifs.chaos_game(ifs.SIERPINSKI, 1_000)
    img = ifs.rasterize(pts, 64, 64)
    assert img.shape == (64, 64, 3)


def test_fern_shape() -> None:
    pts = ifs.chaos_game(ifs.FERN, 1_000)
    img = ifs.rasterize(pts, 64, 96)
    assert img.shape == (96, 64, 3)


def test_koch_shape() -> None:
    img = lsystem.render_lsystem(lsystem.KOCH, 2, width=64, height=64)
    assert img.shape == (64, 64, 3)


def test_tree_shape() -> None:
    img = lsystem.render_lsystem(lsystem.TREE, 3, width=64, height=96)
    assert img.shape == (96, 64, 3)
