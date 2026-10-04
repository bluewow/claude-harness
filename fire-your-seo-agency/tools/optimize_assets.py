#!/usr/bin/env python3
"""Recompress the raster assets in this repository without changing a pixel.

    python3 tools/optimize_assets.py           # rewrite the assets in place
    python3 tools/optimize_assets.py --check   # report only; fail on recoverable slack
    python3 tools/optimize_assets.py some.png  # limit to specific files

Lossless only: a file is rewritten only when the candidate encoding decodes to the
identical RGBA pixel grid. Needs Pillow (``python3 -m pip install pillow``).
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path

DEFAULT_TARGETS = ("assets/social-preview.png",)
CHECK_THRESHOLD = 0.02
ENCODERS = {".png": "PNG", ".jpg": "JPEG", ".jpeg": "JPEG", ".webp": "WEBP"}


def load_pillow():
    try:
        from PIL import Image
    except ImportError as exc:
        raise SystemExit("Pillow is required: python3 -m pip install pillow") from exc
    return Image


def decode_pixels(image_module, payload: bytes) -> bytes:
    with image_module.open(io.BytesIO(payload)) as handle:
        handle.load()
        return handle.convert("RGBA").tobytes()


def encode(image_module, payload: bytes, fmt: str) -> bytes:
    buffer = io.BytesIO()
    with image_module.open(io.BytesIO(payload)) as handle:
        handle.load()
        if fmt == "PNG":
            handle.save(buffer, format="PNG", optimize=True, compress_level=9)
        elif fmt == "JPEG":
            handle.convert("RGB").save(buffer, format="JPEG", quality=95, optimize=True, progressive=True)
        else:
            handle.save(buffer, format="WEBP", lossless=True, quality=100, method=6)
    return buffer.getvalue()


def optimize(path: Path, image_module, apply: bool) -> tuple:
    """Return (error, before_bytes, after_bytes)."""
    fmt = ENCODERS[path.suffix.lower()]
    original = path.read_bytes()
    candidate = encode(image_module, original, fmt)
    if decode_pixels(image_module, original) != decode_pixels(image_module, candidate):
        return "refused: recompression would change pixels", len(original), len(original)
    if len(candidate) < len(original) and apply:
        temporary = path.with_name(path.name + ".optimized")
        temporary.write_bytes(candidate)
        temporary.replace(path)
    return None, len(original), len(candidate)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Losslessly recompress repository assets.")
    parser.add_argument("paths", nargs="*", help="files to process (default: the committed raster assets)")
    parser.add_argument("--check", action="store_true", help="do not write; fail when savings exceed the threshold")
    parser.add_argument("--root", default=str(Path(__file__).resolve().parent.parent))
    args = parser.parse_args(argv)
    root = Path(args.root).resolve()
    targets = args.paths or list(DEFAULT_TARGETS)
    image_module = load_pillow()
    failing = False
    for name in targets:
        path = Path(name)
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            print("SKIP  %s (missing)" % name)
            continue
        if path.suffix.lower() not in ENCODERS:
            print("SKIP  %s (unsupported image format)" % name)
            continue
        error, before, after = optimize(path, image_module, apply=not args.check)
        if error:
            print("FAIL  %s: %s" % (path.name, error))
            failing = True
            continue
        savings = 100.0 * (before - after) / before if before else 0.0
        if args.check:
            print("CHECK %-26s %9d -> %9d bytes (%+.2f%%)" % (path.name, before, after, savings))
            if savings / 100.0 > CHECK_THRESHOLD:
                failing = True
        elif after < before:
            print("WROTE %-26s %9d -> %9d bytes (%+.2f%%)" % (path.name, before, after, savings))
        else:
            print("OK    %-26s %9d bytes (already optimal)" % (path.name, before))
    return 1 if failing else 0


if __name__ == "__main__":
    raise SystemExit(main())
