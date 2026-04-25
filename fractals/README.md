# fractals — usage & internals

A `uv`-managed Python renderer for eight classic fractals across three
algorithmic families. All images in the profile README are produced here.

## Quick start

```bash
git clone git@github.com:dsculptor/dsculptor.git
cd dsculptor
uv sync                                  # creates .venv, installs deps
uv run build-all                         # render all 8 fractals → gallery/
uv run fractals --help                   # full CLI
```

## Commands

```bash
uv run fractals mandelbrot               # Mandelbrot set (default 1600×1200)
uv run fractals julia -c "-0.8+0.156j"  # Julia set with custom seed
uv run fractals burning-ship             # Burning Ship
uv run fractals newton                   # Newton fractal for z³−1
uv run fractals sierpinski               # Sierpinski triangle (chaos game)
uv run fractals fern                     # Barnsley fern (chaos game)
uv run fractals koch --depth 6           # Koch snowflake (L-system)
uv run fractals tree --depth 7           # Recursive tree (L-system)
uv run fractals all --out-dir my-dir/    # render all into a custom directory
uv run build-all                         # same as `all`, fixed to gallery/
```

Common options accepted by every command:

| Flag | Default | Description |
|------|---------|-------------|
| `--width / -w` | varies | Image width in pixels |
| `--height / -H` | varies | Image height in pixels |
| `--iters / -i` | 256 | Max iterations (escape-time only) |
| `--out / -o` | `gallery/<name>.png` | Output path |

## Package layout

| Module | What it does |
|--------|-------------|
| `escape.py` | Escape-time engine — one kernel abstraction, three fractals |
| `newton.py` | Newton iteration on z³−1, colored by convergence basin |
| `ifs.py` | Chaos game — Sierpinski triangle & Barnsley fern |
| `lsystem.py` | L-system string rewriting + turtle rasterizer |
| `palette.py` | Vectorized HSV→RGB, smooth escape-time coloring |
| `canvas.py` | Save an (H,W,3) uint8 array as PNG |
| `cli.py` | Typer app wiring all of the above |

## Stack

Python 3.12 · `uv` · `numpy` · `Pillow` · `typer`

Type-checked with `mypy --strict`, linted with `ruff`.
See [`pyproject.toml`](../pyproject.toml) for the full configuration.

## Adding a new fractal

1. Implement the renderer in a new module (≤ 50 lines per function).
2. Add a `@app.command()` in `cli.py` + a call inside `_render_gallery()`.
3. Add a smoke test in `tests/test_smoke.py` asserting the output shape.
4. Run `uv run build-all` and commit the new PNG under `gallery/`.
