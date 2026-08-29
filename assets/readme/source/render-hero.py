from __future__ import annotations

import math
import random
from pathlib import Path
from xml.sax.saxutils import escape

from PIL import Image, ImageDraw, ImageFont


WIDTH = 1200
HEIGHT = 360
FRAME_MS = 80
PHRASES = ("Hey,I'm Celyn", "Welcome to my world!")
OUTPUT_DIR = Path(__file__).resolve().parent.parent


def build_network() -> tuple[list[tuple[int, int]], list[tuple[int, int]]]:
    rng = random.Random(27)
    points = []
    for _ in range(28):
        points.append((rng.randint(18, WIDTH - 18), rng.randint(16, 132)))
    for _ in range(18):
        points.append((rng.randint(18, WIDTH - 18), rng.randint(238, HEIGHT - 16)))
    points.extend([(22, 178), (1178, 176), (92, 201), (1108, 211)])

    edges: set[tuple[int, int]] = set()
    for index, (x1, y1) in enumerate(points):
        distances = []
        for other, (x2, y2) in enumerate(points):
            if index == other:
                continue
            distance = math.hypot(x2 - x1, y2 - y1)
            if distance < 245:
                distances.append((distance, other))
        for _, other in sorted(distances)[:3]:
            edges.add(tuple(sorted((index, other))))
    return points, sorted(edges)


def load_font(size: int) -> ImageFont.FreeTypeFont:
    candidates = (
        Path("C:/Windows/Fonts/segoeuib.ttf"),
        Path("C:/Windows/Fonts/arialbd.ttf"),
    )
    for candidate in candidates:
        if candidate.exists():
            return ImageFont.truetype(str(candidate), size)
    return ImageFont.load_default(size=size)


def draw_background(
    points: list[tuple[int, int]], edges: list[tuple[int, int]]
) -> Image.Image:
    image = Image.new("L", (WIDTH, HEIGHT), 255)
    draw = ImageDraw.Draw(image)
    for start, end in edges:
        draw.line((*points[start], *points[end]), fill=224, width=1)
    for x, y in points:
        draw.ellipse((x - 2, y - 2, x + 2, y + 2), fill=92)
    return image


def draw_frame(background: Image.Image, text: str, cursor: bool) -> Image.Image:
    frame = background.copy()
    draw = ImageDraw.Draw(frame)
    font = load_font(62)
    box = draw.textbbox((0, 0), text, font=font)
    text_width = box[2] - box[0]
    text_height = box[3] - box[1]
    x = (WIDTH - text_width) // 2
    y = (HEIGHT - text_height) // 2 - box[1]
    draw.text((x, y), text, font=font, fill=8)
    if cursor:
        cursor_x = x + text_width + 7
        draw.rectangle((cursor_x, 143, cursor_x + 4, 217), fill=8)
    return frame


def make_gif(points: list[tuple[int, int]], edges: list[tuple[int, int]]) -> None:
    background = draw_background(points, edges)
    frames: list[Image.Image] = []
    durations: list[int] = []

    def add(text: str, duration: int = FRAME_MS, cursor: bool = True) -> None:
        frames.append(draw_frame(background, text, cursor))
        durations.append(duration)

    add("", 400)
    for phrase in PHRASES:
        for length in range(1, len(phrase) + 1):
            add(phrase[:length], 95)
        for blink in range(12):
            add(phrase, FRAME_MS, cursor=blink % 4 < 2)
        for length in range(len(phrase) - 1, -1, -1):
            add(phrase[:length], 48)
        add("", 260)
    add("", 400)

    frames[0].save(
        OUTPUT_DIR / "hero.gif",
        save_all=True,
        append_images=frames[1:],
        duration=durations,
        loop=0,
        optimize=True,
        disposal=1,
    )


def make_svg(points: list[tuple[int, int]], edges: list[tuple[int, int]]) -> None:
    lines = "\n".join(
        f'    <line x1="{points[a][0]}" y1="{points[a][1]}" '
        f'x2="{points[b][0]}" y2="{points[b][1]}" />'
        for a, b in edges
    )
    nodes = "\n".join(
        f'    <circle cx="{x}" cy="{y}" r="2.4" />' for x, y in points
    )
    title = escape(PHRASES[0])
    subtitle = escape(PHRASES[1])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="360" viewBox="0 0 1200 360" role="img" aria-labelledby="title desc">
  <title id="title">Celyn profile welcome</title>
  <desc id="desc">A monochrome network banner welcoming visitors to Celyn's world.</desc>
  <rect width="1200" height="360" fill="#ffffff" />
  <g stroke="#d8dadd" stroke-width="1" fill="none">
{lines}
  </g>
  <g fill="#5c6166">
{nodes}
  </g>
  <g text-anchor="middle" font-family="Segoe UI, Arial, sans-serif" fill="#080808">
    <text x="600" y="178" font-size="62" font-weight="700">{title}</text>
    <text x="600" y="226" font-size="24" font-weight="400" fill="#666a70">{subtitle}</text>
  </g>
</svg>
'''
    (OUTPUT_DIR / "hero.svg").write_text(svg, encoding="utf-8")


if __name__ == "__main__":
    network_points, network_edges = build_network()
    make_svg(network_points, network_edges)
    make_gif(network_points, network_edges)
