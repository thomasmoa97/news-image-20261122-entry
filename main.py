#!/usr/bin/env python3
"""World News, 22 November 2026 — a one-page newspaper infographic, 1024x1024.

Draws the day's world news with Pillow only. Fully deterministic: no clock,
no randomness, no network, no file reads beyond the bundled fonts. The program
writes entry.png into MAKEFUN_OUTPUT_DIR (default /output).

Layout, top to bottom: masthead with the date, a hero panel on the Gulf
escalation, a 2x3 grid of the day's other big stories, and a news ticker.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

CANVAS = 1024
MARGIN = 28
CONTENT_W = CANVAS - 2 * MARGIN

PALETTE = {
    "paper": (250, 247, 238),
    "ink": (26, 25, 22),
    "soft_ink": (74, 70, 62),
    "red": (172, 32, 28),
    "navy": (14, 32, 62),
    "deep_navy": (9, 22, 44),
    "steel": (70, 104, 142),
    "pale": (214, 226, 238),
    "gold": (198, 158, 38),
    "teal": (16, 108, 102),
    "moss": (74, 116, 62),
    "slate": (88, 94, 102),
    "cream": (238, 231, 214),
    "white": (255, 255, 255),
    "amber": (224, 148, 32),
}

FONT_DIR = "/usr/share/fonts/truetype/dejavu"
_FONT_CACHE = {}


def load_font(kind, size):
    """Load a DejaVu font by role; cache so every call is cheap."""
    key = (kind, size)
    if key in _FONT_CACHE:
        return _FONT_CACHE[key]
    names = {
        "serif": "DejaVuSerif-Bold.ttf",
        "serif_plain": "DejaVuSerif.ttf",
        "sans": "DejaVuSans.ttf",
        "sans_bold": "DejaVuSans-Bold.ttf",
    }
    path = os.path.join(FONT_DIR, names[kind])
    try:
        font = ImageFont.truetype(path, size)
    except OSError:
        font = ImageFont.load_default()
    _FONT_CACHE[key] = font
    return font


def wrap_lines(draw, text, font, max_width):
    """Greedy word wrap; returns a list of lines that fit max_width."""
    lines = []
    for paragraph in text.split("\n"):
        words = paragraph.split()
        if not words:
            lines.append("")
            continue
        current = words[0]
        for word in words[1:]:
            trial = current + " " + word
            if draw.textlength(trial, font=font) <= max_width:
                current = trial
            else:
                lines.append(current)
                current = word
        lines.append(current)
    return lines


def draw_lines(draw, x, y, lines, font, fill, leading):
    """Draw stacked lines; returns the y just below the last line."""
    for line in lines:
        draw.text((x, y), line, font=font, fill=fill)
        y += leading
    return y


def draw_rule(draw, x0, x1, y, fill, width=2):
    draw.line([(x0, y), (x1, y)], fill=fill, width=width)


def draw_chip(draw, x, y, label, bg, fg):
    """A small filled tag with white text, e.g. a story kicker."""
    font = load_font("sans_bold", 15)
    pad_x, pad_y = 10, 5
    text_w = draw.textlength(label, font=font)
    box = [x, y, x + text_w + 2 * pad_x, y + 26]
    draw.rounded_rectangle(box, radius=3, fill=bg)
    draw.text((x + pad_x, y + pad_y), label, font=font, fill=fg)
    return box[2]


def burst_motif(draw, cx, cy, radius, color, spokes=12):
    """Starburst: short rays out of a centre dot."""
    for i in range(spokes):
        angle = 2 * math.pi * i / spokes
        x1 = cx + radius * 0.35 * math.cos(angle)
        y1 = cy + radius * 0.35 * math.sin(angle)
        x2 = cx + radius * math.cos(angle)
        y2 = cy + radius * math.sin(angle)
        draw.line([(x1, y1), (x2, y2)], fill=color, width=3)
    draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=color)


def star_motif(draw, cx, cy, outer, color):
    """Five-point star, for the capture story."""
    points = []
    for i in range(10):
        r = outer if i % 2 == 0 else outer * 0.42
        angle = -math.pi / 2 + i * math.pi / 5
        points.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    draw.polygon(points, fill=color)


def rings_motif(draw, cx, cy, radius, color_a, color_b):
    """Two interlocked rings, for the trade-deal story."""
    draw.ellipse([cx - radius, cy - radius // 2, cx, cy + radius // 2],
                 outline=color_a, width=5)
    draw.ellipse([cx, cy - radius // 2, cx + radius, cy + radius // 2],
                 outline=color_b, width=5)


def gauge_motif(draw, cx, cy, radius, color):
    """A half-dial with a needle, for the climate-deadlock story."""
    draw.arc([cx - radius, cy - radius, cx + radius, cy + radius],
             start=180, end=360, fill=color, width=5)
    tip_x = cx + radius * 0.8 * math.cos(-math.pi * 0.22)
    tip_y = cy + radius * 0.8 * math.sin(-math.pi * 0.22)
    draw.line([(cx, cy), (tip_x, tip_y)], fill=color, width=4)
    draw.ellipse([cx - 5, cy - 5, cx + 5, cy + 5], fill=color)
    draw.line([(cx - radius, cy), (cx + radius, cy)], fill=color, width=2)


def lens_motif(draw, cx, cy, radius, color):
    """A magnifier, for the FBI-probe story."""
    draw.ellipse([cx - radius, cy - radius, cx + radius, cy + radius],
                 outline=color, width=5)
    draw.line([(cx + radius * 0.7, cy + radius * 0.7),
               (cx + radius * 1.35, cy + radius * 1.35)], fill=color, width=5)


def ballot_motif(draw, cx, cy, size, color):
    """A ballot box with a check mark, for the Hong Kong vote."""
    draw.rectangle([cx - size, cy - size * 0.7, cx + size, cy + size * 0.7],
                   outline=color, width=4)
    draw.line([(cx - size * 0.6, cy), (cx - size * 0.15, cy + size * 0.45)],
              fill=color, width=5)
    draw.line([(cx - size * 0.15, cy + size * 0.45),
               (cx + size * 0.7, cy - size * 0.5)], fill=color, width=5)


def arc_arrow(draw, start, end, lift, color, width=4):
    """A curved missile path from start to end, arcing upward by lift."""
    steps = 24
    pts = []
    for i in range(steps + 1):
        t = i / steps
        x = start[0] + (end[0] - start[0]) * t
        y = start[1] + (end[1] - start[1]) * t - lift * 4 * t * (1 - t)
        pts.append((x, y))
    draw.line(pts, fill=color, width=width, joint="curve")
    dx = pts[-1][0] - pts[-2][0]
    dy = pts[-1][1] - pts[-2][1]
    norm = math.hypot(dx, dy) or 1
    ux, uy = dx / norm, dy / norm
    tip = pts[-1]
    base = (tip[0] - ux * 16, tip[1] - uy * 16)
    left = (base[0] - uy * 7, base[1] + ux * 7)
    right = (base[0] + uy * 7, base[1] - ux * 7)
    draw.polygon([tip, left, right], fill=color)


def map_pin(draw, x, y, color, label, label_side="right"):
    """A ringed dot with a place label, for the hero map panel."""
    draw.ellipse([x - 12, y - 12, x + 12, y + 12], outline=color, width=3)
    draw.ellipse([x - 5, y - 5, x + 5, y + 5], fill=color)
    font = load_font("sans_bold", 17)
    if label_side == "right":
        draw.text((x + 26, y - 9), label, font=font, fill=PALETTE["white"])
    else:
        w = draw.textlength(label, font=font)
        draw.text((x - 26 - w, y - 9), label, font=font, fill=PALETTE["white"])


def render_masthead(draw):
    """Newspaper nameplate: title, date line, double rule."""
    title = "THE WORLD TODAY"
    font = load_font("serif", 60)
    tw = draw.textlength(title, font=font)
    draw.text(((CANVAS - tw) / 2, 22), title, font=font, fill=PALETTE["ink"])
    dateline = "SUNDAY, 22 NOVEMBER 2026  •  WORLD NEWS IN ONE IMAGE"
    dfont = load_font("sans_bold", 19)
    dw = draw.textlength(dateline, font=dfont)
    draw.text(((CANVAS - dw) / 2, 96), dateline, font=dfont, fill=PALETTE["red"])
    draw_rule(draw, MARGIN, CANVAS - MARGIN, 128, PALETTE["ink"], 3)
    draw_rule(draw, MARGIN, CANVAS - MARGIN, 133, PALETTE["ink"], 1)


def render_hero(draw):
    """The day's lead story: Gulf map art on the left, headline on the right."""
    top, bottom = 148, 498
    art_x0, art_x1 = MARGIN, 492
    # --- map panel ---
    draw.rectangle([art_x0, top, art_x1, bottom], fill=PALETTE["deep_navy"])
    draw.rectangle([art_x0, top, art_x1, bottom], outline=PALETTE["ink"], width=2)
    # faint latitude/longitude grid
    for gx in range(art_x0 + 52, art_x1, 52):
        draw.line([(gx, top), (gx, bottom)], fill=(24, 48, 80), width=1)
    for gy in range(top + 52, bottom, 52):
        draw.line([(art_x0, gy), (art_x1, gy)], fill=(24, 48, 80), width=1)
    # missile arcs converging on the two pins
    arc_arrow(draw, (art_x0 + 30, bottom - 34), (300, 250), 70,
              PALETTE["amber"], 4)
    arc_arrow(draw, (art_x0 + 120, bottom - 20), (382, 330), 55,
              PALETTE["amber"], 4)
    arc_arrow(draw, (art_x0 + 210, bottom - 30), (300, 250), 46,
              PALETTE["red"], 4)
    # bursts first so they never paint over the place labels
    burst_motif(draw, 300, 250, 22, PALETTE["amber"], spokes=8)
    burst_motif(draw, 382, 330, 22, PALETTE["red"], spokes=8)
    # pins
    map_pin(draw, 300, 250, PALETTE["amber"], "KUWAIT")
    map_pin(draw, 382, 330, PALETTE["red"], "BAHRAIN")
    caption = "THE PERSIAN GULF — U.S. BASES UNDER FIRE"
    cfont = load_font("sans_bold", 15)
    cw = draw.textlength(caption, font=cfont)
    draw.text(((art_x0 + art_x1 - cw) / 2, bottom - 34), caption,
              font=cfont, fill=PALETTE["pale"])
    # --- headline block ---
    tx = 516
    draw_chip(draw, tx, 152, "GULF ESCALATION", PALETTE["red"], PALETTE["white"])
    head_font = load_font("sans_bold", 54)
    y = 192
    for line in ["IRAN STRIKES", "U.S. BASES", "IN THE GULF"]:
        draw.text((tx, y), line, font=head_font, fill=PALETTE["ink"])
        y += 58
    deck = ("Iran fires missiles and drones at Ali Al Salem air base in "
            "Kuwait and Patriot radar sites in Bahrain. U.S. Central "
            "Command says defences held — no casualties.")
    dfont = load_font("sans", 21)
    lines = wrap_lines(draw, deck, dfont, CANVAS - MARGIN - tx)
    draw_lines(draw, tx, y + 8, lines, dfont, PALETTE["soft_ink"], 28)


STORIES = [
    {
        "tag": "UKRAINE", "tag_bg": (172, 32, 28),
        "headline": "Russia strikes Lviv; missiles kill 2, wound 10",
        "body": "Ballistic attack also hits Kryvyi Rih, Zelensky's home city.",
        "art": "burst", "art_bg": (58, 28, 24),
    },
    {
        "tag": "MEXICO", "tag_bg": (14, 32, 62),
        "headline": "\u2018El Chapo Isidro\u2019 captured in Sinaloa raid",
        "body": "FBI most-wanted boss seized; 11 killed in clashes after the raid.",
        "art": "star", "art_bg": (14, 32, 62),
    },
    {
        "tag": "TRADE", "tag_bg": (16, 108, 102),
        "headline": "EU and Indonesia sign landmark trade deal",
        "body": "Ten years of talks end: 98.5% of tariffs between Brussels and Jakarta to go.",
        "art": "rings", "art_bg": (16, 108, 102),
    },
    {
        "tag": "CLIMATE", "tag_bg": (74, 116, 62),
        "headline": "COP31 talks deadlocked over fossil fuels",
        "body": "The fight over the future of fossil fuels stalls the climate summit in overtime.",
        "art": "gauge", "art_bg": (74, 116, 62),
    },
    {
        "tag": "AMERICA", "tag_bg": (88, 94, 102),
        "headline": "FBI probes apparent hack of its database",
        "body": "Investigators look into a breach of the bureau's criminal database.",
        "art": "lens", "art_bg": (88, 94, 102),
    },
    {
        "tag": "ASIA", "tag_bg": (120, 84, 24),
        "headline": "Hong Kong votes; Estonia to shut Russia border",
        "body": "Election Committee polls open in Hong Kong as Estonia moves to close its border.",
        "art": "ballot", "art_bg": (120, 84, 24),
    },
]


def draw_story_art(draw, kind, box, bg):
    """Paint one story's small geometric illustration inside box."""
    draw.rectangle(box, fill=bg)
    x0, y0, x1, y1 = box
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    white = PALETTE["white"]
    if kind == "burst":
        burst_motif(draw, cx, cy, 34, PALETTE["amber"])
    elif kind == "star":
        star_motif(draw, cx, cy, 34, PALETTE["gold"])
    elif kind == "rings":
        rings_motif(draw, cx, cy, 26, white, PALETTE["gold"])
    elif kind == "gauge":
        gauge_motif(draw, cx, cy, 30, white)
    elif kind == "lens":
        lens_motif(draw, cx, cy, 24, white)
    elif kind == "ballot":
        ballot_motif(draw, cx, cy, 26, white)


def render_story_grid(draw):
    """2 columns x 3 rows of story cards under the hero."""
    grid_top = 514
    gap = 14
    card_w = (CONTENT_W - gap) // 2
    card_h = 133
    for index, story in enumerate(STORIES):
        row, col = divmod(index, 2)
        x0 = MARGIN + col * (card_w + gap)
        y0 = grid_top + row * (card_h + gap)
        draw.rectangle([x0, y0, x0 + card_w, y0 + card_h],
                       fill=PALETTE["white"], outline=(206, 200, 186), width=1)
        # art square
        art_box = [x0 + 12, y0 + 14, x0 + 108, y0 + 110]
        draw_story_art(draw, story["art"], art_box, story["art_bg"])
        # text column
        tx = x0 + 122
        text_w = x0 + card_w - 14 - tx
        kicker_font = load_font("sans_bold", 14)
        draw.text((tx, y0 + 12), story["tag"], font=kicker_font,
                  fill=story["tag_bg"])
        head_font = load_font("sans_bold", 21)
        head_lines = wrap_lines(draw, story["headline"], head_font, text_w)
        y = draw_lines(draw, tx, y0 + 34, head_lines[:2], head_font,
                       PALETTE["ink"], 26)
        body_font = load_font("sans", 16)
        body_lines = wrap_lines(draw, story["body"], body_font, text_w)
        draw_lines(draw, tx, y + 2, body_lines[:2], body_font,
                   PALETTE["soft_ink"], 21)


def render_ticker(draw):
    """Bottom news ticker bar."""
    top = 956
    draw.rectangle([MARGIN, top, CANVAS - MARGIN, top + 40],
                   fill=PALETTE["navy"])
    ticker = ("ESTONIA TO SHUT RUSSIA BORDER   •   ZELENSKY: KERCH STRIKES "
              "A \u2018FAIR RESPONSE\u2019   •   TECH SHARES SLIDE")
    # shrink the ticker font until the line fits the bar, so nothing clips
    size = 17
    font = load_font("sans_bold", size)
    while draw.textlength(ticker, font=font) > CONTENT_W - 16 and size > 11:
        size -= 1
        font = load_font("sans_bold", size)
    tw = draw.textlength(ticker, font=font)
    draw.text(((CANVAS - tw) / 2, top + 11), ticker, font=font,
              fill=PALETTE["white"])


def build_image():
    """Compose the whole front page and return the Pillow image."""
    canvas = Image.new("RGB", (CANVAS, CANVAS), PALETTE["paper"])
    draw = ImageDraw.Draw(canvas)
    render_masthead(draw)
    render_hero(draw)
    render_story_grid(draw)
    render_ticker(draw)
    return canvas


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    image = build_image()
    image.save(os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
