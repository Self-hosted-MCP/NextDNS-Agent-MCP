# SPDX-License-Identifier: Apache-2.0
"""Simple PNG charts drawn with Pillow: lines over time, or bars. No fonts or files needed from elsewhere."""

from __future__ import annotations

import io

from PIL import Image, ImageDraw, ImageFont

W, H = 1000, 560
PAD_L, PAD_R, PAD_T, PAD_B = 90, 30, 70, 90
BG, INK, SOFT, GRID = (255, 255, 255), (22, 20, 42), (100, 96, 128), (230, 228, 241)
# Colors that stay apart for most color vision; blocked is always the red one.
COLORS = [(29, 78, 216), (240, 140, 30), (20, 150, 110), (200, 60, 140), (60, 140, 220), (120, 120, 120)]
BLOCKED = (214, 40, 40)


def font(size: int):
    try:
        return ImageFont.load_default(size=size)
    except TypeError:   # an old Pillow: one small built-in size
        return ImageFont.load_default()


def short(n: float) -> str:
    n = float(n)
    for size, mark in ((1e9, "B"), (1e6, "M"), (1e3, "k")):
        if abs(n) >= size:
            return f"{n / size:.1f}".rstrip("0").rstrip(".") + mark
    return f"{n:g}"


def nice_max(v: float) -> float:
    if v <= 0:
        return 1
    import math
    step = 10 ** math.floor(math.log10(v))
    for m in (1, 2, 2.5, 5, 10):
        if v <= m * step:
            return m * step
    return 10 * step


def png(img: Image.Image) -> bytes:
    out = io.BytesIO()
    img.save(out, "PNG", optimize=True)
    return out.getvalue()


def color_for(label: str, i: int):
    """Blocked is always red; the others take the palette in order."""
    return BLOCKED if label.lower().startswith("blocked") else COLORS[i % len(COLORS)]


def lines(title: str, times: list[str], series: list[tuple[str, list[float]]]) -> bytes:
    """series: (label, values per time window), at most 6."""
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((PAD_L, 22), title, fill=INK, font=font(24))
    series = series[:6]
    top = nice_max(max([v for _l, vals in series for v in vals] or [0]))
    x0, x1, y0, y1 = PAD_L, W - PAD_R, H - PAD_B, PAD_T
    for k in range(5):
        y = y0 - (y0 - y1) * k / 4
        d.line([(x0, y), (x1, y)], fill=GRID, width=1)
        d.text((x0 - 12, y), short(top * k / 4), fill=SOFT, font=font(15), anchor="rm")
    n = max(len(times), 1)
    xs = [x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0.5) for i in range(n)]
    for i in sorted({0, n // 3, 2 * n // 3, n - 1}):
        if 0 <= i < len(times):
            anchor = "lt" if i == 0 and n > 1 else "rt" if i == n - 1 and n > 1 else "mt"
            d.text((xs[i], y0 + 14), times[i][5:16].replace("T", " "), fill=SOFT, font=font(14), anchor=anchor)
    for i, (label, vals) in enumerate(series):
        pts = [(xs[j], y0 - (y0 - y1) * (v / top)) for j, v in enumerate(vals[:n])]
        c = color_for(label, i)
        if len(pts) > 1:
            d.line(pts, fill=c, width=3, joint="curve")
        for p in pts if len(pts) <= 40 else []:
            d.ellipse([p[0] - 3, p[1] - 3, p[0] + 3, p[1] + 3], fill=c)
    lx = x0
    for i, (label, vals) in enumerate(series):   # legend, under the chart
        c = color_for(label, i)
        d.rectangle([lx, H - 34, lx + 14, H - 20], fill=c)
        text = f"{label} ({short(sum(vals))})"
        d.text((lx + 20, H - 27), text, fill=INK, font=font(15), anchor="lm")
        lx += 40 + d.textlength(text, font=font(15))
    return png(img)


def bars(title: str, rows: list[tuple[str, float]]) -> bytes:
    """rows: (label, count), drawn as horizontal bars, at most 20."""
    rows = rows[:20]
    h = max(220, PAD_T + 34 * len(rows) + 40)
    img = Image.new("RGB", (W, h), BG)
    d = ImageDraw.Draw(img)
    d.text((30, 22), title, fill=INK, font=font(24))
    label_w = min(420, max([d.textlength(l[:48], font=font(16)) for l, _v in rows] or [0]) + 20)
    x0, x1 = 30 + label_w, W - 90
    top = max([v for _l, v in rows] or [1]) or 1
    for i, (label, v) in enumerate(rows):
        y = PAD_T + 34 * i
        d.text((x0 - 12, y + 12), label[:48], fill=INK, font=font(16), anchor="rm")
        d.rectangle([x0, y + 2, x0 + max(2, (x1 - x0) * v / top), y + 24], fill=color_for(label, 0))
        d.text((x0 + (x1 - x0) * v / top + 8, y + 12), short(v), fill=SOFT, font=font(15), anchor="lm")
    return png(img)
