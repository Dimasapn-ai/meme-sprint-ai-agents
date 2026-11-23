#!/usr/bin/env python3
"""Meme Sprint entry: "AI Agents Ship Games".

Draws a 1024x1024 meme with a hand-rolled rasterizer (Python stdlib only):
own PNG encoder (zlib), own 5x7 bitmap font, shapes rendered at 2x
supersampling and box-downsampled for smooth edges.

Top caption:    THE GAME CRASHES FOR EVERY HUMAN
Scene:          a smug robot agent (sunglasses, thumbs up) beside a monitor
                running a broken platformer - hero falling through a gap in
                the floor, an ERROR! popup, glitch bars, SCORE: -1.
Bottom caption: RAN PERFECTLY IN MY / CONTEXT WINDOW

Output: entry.png in $MAKEFUN_OUTPUT_DIR if set, else /output.
The output directory is resolved first and is the only place written to;
the program never writes to the (read-only) working directory.
"""

import os
import sys
import zlib

W = 1024
H = 1024
SS = 2  # supersampling factor
SW = W * SS
SH = H * SS

# --------------------------------------------------------------------------
# 5x7 bitmap font. Each glyph is 7 strings of 5 characters.
# --------------------------------------------------------------------------
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "B": ("11110", "10001", "10001", "11110", "10001", "10001", "11110"),
    "C": ("01110", "10001", "10000", "10000", "10000", "10001", "01110"),
    "D": ("11100", "10010", "10001", "10001", "10001", "10010", "11100"),
    "E": ("11111", "10000", "10000", "11110", "10000", "10000", "11111"),
    "F": ("11111", "10000", "10000", "11110", "10000", "10000", "10000"),
    "G": ("01110", "10001", "10000", "10111", "10001", "10001", "01111"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "I": ("01110", "00100", "00100", "00100", "00100", "00100", "01110"),
    "J": ("00111", "00010", "00010", "00010", "00010", "10010", "01100"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "L": ("10000", "10000", "10000", "10000", "10000", "10000", "11111"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "10001", "11001", "10101", "10011", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "Q": ("01110", "10001", "10001", "10001", "10101", "10010", "01101"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "V": ("10001", "10001", "10001", "10001", "10001", "01010", "00100"),
    "W": ("10001", "10001", "10001", "10101", "10101", "10101", "01010"),
    "X": ("10001", "01010", "00100", "00100", "00100", "01010", "10001"),
    "Y": ("10001", "10001", "01010", "00100", "00100", "00100", "00100"),
    "Z": ("11111", "00001", "00010", "00100", "01000", "10000", "11111"),
    "0": ("01110", "10001", "10011", "10101", "11001", "10001", "01110"),
    "1": ("00100", "01100", "00100", "00100", "00100", "00100", "01110"),
    "2": ("01110", "10001", "00001", "00110", "01000", "10000", "11111"),
    "3": ("11111", "00010", "00100", "00010", "00001", "10001", "01110"),
    "4": ("00010", "00110", "01010", "10010", "11111", "00010", "00010"),
    "5": ("11111", "10000", "11110", "00001", "00001", "10001", "01110"),
    "6": ("00110", "01000", "10000", "11110", "10001", "10001", "01110"),
    "7": ("11111", "00001", "00010", "00100", "01000", "01000", "01000"),
    "8": ("01110", "10001", "10001", "01110", "10001", "10001", "01110"),
    "9": ("01110", "10001", "10001", "01111", "00001", "00010", "01100"),
    "!": ("00100", "00100", "00100", "00100", "00100", "00000", "00100"),
    ":": ("00000", "00100", "00000", "00000", "00000", "00100", "00000"),
    "-": ("00000", "00000", "00000", "01110", "00000", "00000", "00000"),
    ".": ("00000", "00000", "00000", "00000", "00000", "00110", "00110"),
    "'": ("00100", "00100", "01000", "00000", "00000", "00000", "00000"),
    "?": ("01110", "10001", "00001", "00110", "00100", "00000", "00100"),
    " ": ("00000", "00000", "00000", "00000", "00000", "00000", "00000"),
}

# Colours (R, G, B)
BLACK = (8, 8, 10)
WHITE = (245, 245, 245)
WALL = (37, 43, 57)
WALL_PANEL = (44, 51, 66)
FLOOR = (22, 24, 30)
DESK = (96, 66, 42)
DESK_FRONT = (74, 50, 32)
BEZEL = (16, 16, 20)
SKY = (94, 172, 238)
SKY_LIGHT = (140, 198, 246)
HILL = (88, 160, 92)
GRASS = (70, 168, 74)
DIRT = (122, 86, 66)
PIT = (26, 20, 18)
GOLD = (250, 200, 40)
HERO_SKIN = (242, 200, 158)
HERO_RED = (214, 40, 40)
HERO_BLUE = (40, 84, 200)
POPUP_RED = (200, 30, 30)
POPUP_SHADOW = (10, 10, 12)
METAL = (156, 166, 180)
METAL_DARK = (104, 114, 128)
METAL_LINE = (84, 94, 108)
GLASSES = (10, 10, 14)
SHINE = (150, 155, 165)
ANTENNA_RED = (224, 48, 48)
CHEST_LIGHT = (120, 224, 255)
MOTION = (210, 215, 220)


class FB:
    """Supersampled RGB framebuffer. All drawing coords are in final-image
    pixels (floats allowed); they are scaled by SS internally."""

    def __init__(self):
        self.buf = bytearray(SW * SH * 3)
        self.clip = None

    def _span(self, x0, x1, y, color):
        if y < 0 or y >= SH or x1 <= 0 or x0 >= SW:
            return
        if self.clip is not None:
            cx0, cy0, cx1, cy1 = self.clip
            if y < cy0 or y >= cy1:
                return
            x0 = max(x0, cx0)
            x1 = min(x1, cx1)
        x0 = max(0, x0)
        x1 = min(SW, x1)
        if x1 <= x0:
            return
        row = (y * SW + x0) * 3
        self.buf[row:row + (x1 - x0) * 3] = bytes(color) * (x1 - x0)

    def set_clip(self, x, y, w, h):
        self.clip = (int(x * SS), int(y * SS),
                     int((x + w) * SS), int((y + h) * SS))

    def clear_clip(self):
        self.clip = None

    def rect(self, x, y, w, h, color):
        x0 = int(round(x * SS))
        x1 = int(round((x + w) * SS))
        y0 = int(round(y * SS))
        y1 = int(round((y + h) * SS))
        for yy in range(max(0, y0), min(SH, y1)):
            self._span(x0, x1, yy, color)

    def circle(self, cx, cy, r, color):
        cx_s = cx * SS
        cy_s = cy * SS
        r_s = r * SS
        y0 = int(cy_s - r_s)
        y1 = int(cy_s + r_s)
        r2 = r_s * r_s
        for yy in range(max(0, y0), min(SH - 1, y1) + 1):
            dy = yy - cy_s
            dx2 = r2 - dy * dy
            if dx2 < 0:
                continue
            dx = int(dx2 ** 0.5)
            self._span(int(cx_s - dx), int(cx_s + dx) + 1, yy, color)

    def rrect(self, x, y, w, h, r, color):
        self.rect(x + r, y, w - 2 * r, h, color)
        self.rect(x, y + r, w, h - 2 * r, color)
        self.circle(x + r, y + r, r, color)
        self.circle(x + w - r, y + r, r, color)
        self.circle(x + r, y + h - r, r, color)
        self.circle(x + w - r, y + h - r, r, color)

    def line(self, x1, y1, x2, y2, wdt, color):
        steps = max(abs(x2 - x1), abs(y2 - y1), 1) * SS
        steps = int(steps)
        for i in range(steps + 1):
            t = i / steps
            self.circle(x1 + (x2 - x1) * t, y1 + (y2 - y1) * t,
                        wdt / 2.0, color)

    def poly(self, pts, color):
        """Scanline even-odd polygon fill; pts are (x, y) in final pixels."""
        pts_s = [(px * SS, py * SS) for px, py in pts]
        ys = [p[1] for p in pts_s]
        y0 = max(0, int(min(ys)))
        y1 = min(SH - 1, int(max(ys)))
        n = len(pts_s)
        for yy in range(y0, y1 + 1):
            yc = yy + 0.5
            xs = []
            for i in range(n):
                xa, ya = pts_s[i]
                xb, yb = pts_s[(i + 1) % n]
                if (ya <= yc < yb) or (yb <= yc < ya):
                    xs.append(xa + (yc - ya) * (xb - xa) / (yb - ya))
            xs.sort()
            for i in range(0, len(xs) - 1, 2):
                self._span(int(xs[i]), int(xs[i + 1]) + 1, yy, color)


def text_width(text, px):
    return len(text) * 6 * px


def draw_text(fb, cx, y, text, px, color, bold=True):
    """Draw text centred at cx, top edge at y. px = size of one font pixel
    in final-image pixels (multiples of 0.5 keep SS arithmetic exact)."""
    x0 = cx - text_width(text, px) / 2.0
    passes = (0.0, 1.0) if bold else (0.0,)
    for off in passes:
        for i, ch in enumerate(text):
            glyph = FONT.get(ch, FONT[" "])
            gx = x0 + i * 6 * px + off
            for row in range(7):
                bits = glyph[row]
                for col in range(5):
                    if bits[col] == "1":
                        fb.rect(gx + col * px, y + row * px, px, px, color)


def draw_text_left(fb, x, y, text, px, color, bold=True):
    draw_text(fb, x + text_width(text, px) / 2.0, y, text, px, color, bold)


# --------------------------------------------------------------------------
# Scene
# --------------------------------------------------------------------------

def draw_screen(fb):
    """The broken platformer inside the monitor."""
    # sky
    fb.rect(70, 250, 550, 400, SKY)
    fb.rect(70, 250, 550, 90, SKY_LIGHT)
    # clouds
    for cx, cy in ((168, 306), (486, 292)):
        fb.circle(cx, cy, 17, WHITE)
        fb.circle(cx + 20, cy + 3, 13, WHITE)
        fb.circle(cx - 20, cy + 4, 12, WHITE)
    # hills behind the ground
    fb.circle(180, 668, 150, HILL)
    fb.circle(520, 678, 170, HILL)
    # ground with a pit gap at x 300-384
    fb.rect(70, 560, 550, 90, DIRT)
    fb.rect(70, 560, 550, 16, GRASS)
    fb.rect(300, 560, 84, 90, PIT)
    # floating platform + coins
    fb.rect(105, 438, 130, 18, DIRT)
    fb.rect(105, 438, 130, 7, GRASS)
    fb.circle(140, 408, 8, GOLD)
    fb.circle(176, 408, 8, GOLD)
    fb.circle(528, 474, 8, GOLD)
    # hero falling through the pit, arms up
    fb.line(322, 566, 322, 588, 3, MOTION)
    fb.line(342, 556, 342, 580, 3, MOTION)
    fb.line(362, 566, 362, 588, 3, MOTION)
    fb.line(333, 622, 319, 607, 5, HERO_BLUE)
    fb.line(351, 622, 365, 607, 5, HERO_BLUE)
    fb.rect(333, 614, 18, 24, HERO_BLUE)
    fb.circle(342, 602, 11, HERO_SKIN)
    fb.rect(330, 591, 24, 8, HERO_RED)
    fb.rect(327, 597, 30, 5, HERO_RED)
    fb.line(336, 638, 330, 652, 5, HERO_BLUE)
    fb.line(348, 638, 354, 652, 5, HERO_BLUE)
    # score, top-left of the screen
    draw_text_left(fb, 90, 268, "SCORE: -1", 3, BLACK, bold=False)
    draw_text_left(fb, 88, 266, "SCORE: -1", 3, WHITE, bold=False)
    # ERROR! popup
    fb.rrect(408, 298, 204, 86, 8, POPUP_SHADOW)
    fb.rrect(396, 286, 212, 94, 10, WHITE)
    fb.rrect(400, 290, 204, 86, 8, POPUP_RED)
    draw_text(fb, 502, 317, "ERROR!", 4.5, WHITE)


def draw_robot(fb):
    """The smug agent: sunglasses, smirk, thumbs up."""
    # torso (bottom hidden behind the desk, drawn later)
    fb.rrect(748, 545, 140, 175, 14, METAL)
    fb.rect(748, 600, 140, 4, METAL_LINE)
    fb.circle(818, 636, 15, METAL_DARK)
    fb.circle(818, 636, 9, CHEST_LIGHT)
    # neck + head
    fb.rect(793, 532, 50, 22, METAL_DARK)
    fb.rrect(728, 375, 180, 165, 22, METAL)
    fb.rect(712, 440, 16, 60, METAL_DARK)
    fb.rect(908, 440, 16, 60, METAL_DARK)
    # antenna
    fb.line(818, 375, 818, 324, 5, METAL_DARK)
    fb.circle(818, 313, 11, ANTENNA_RED)
    fb.circle(814, 309, 4, WHITE)
    # sunglasses
    fb.rrect(743, 432, 150, 46, 12, GLASSES)
    fb.rect(760, 440, 26, 8, SHINE)
    fb.rect(838, 440, 26, 8, SHINE)
    # smirk
    fb.line(788, 512, 818, 521, 5, METAL_LINE)
    fb.line(818, 521, 848, 509, 5, METAL_LINE)
    # resting arm (viewer right)
    fb.rect(892, 560, 28, 112, METAL)
    fb.circle(906, 676, 16, METAL)
    # raised arm with thumbs up (viewer left), drawn over the head edge
    fb.rect(698, 468, 30, 112, METAL)
    fb.rrect(680, 406, 66, 58, 14, METAL_DARK)
    fb.rrect(683, 409, 60, 52, 12, METAL)
    fb.rrect(697, 360, 30, 54, 12, METAL_DARK)
    fb.rrect(700, 363, 24, 48, 10, METAL)
    fb.rect(690, 428, 46, 4, METAL_LINE)
    fb.rect(690, 442, 46, 4, METAL_LINE)


def draw_scene(fb):
    # caption bars
    fb.rect(0, 0, W, H, BLACK)
    # room
    fb.rect(0, 140, W, 690, WALL)
    fb.rect(60, 180, 200, 300, WALL_PANEL)
    fb.rect(790, 180, 180, 300, WALL_PANEL)
    fb.rect(0, 745, W, 85, FLOOR)
    # monitor
    fb.rrect(50, 230, 590, 450, 14, BEZEL)
    fb.set_clip(70, 250, 550, 400)
    draw_screen(fb)
    fb.clear_clip()
    fb.rect(325, 680, 60, 22, BEZEL)
    fb.rect(285, 698, 140, 10, BEZEL)
    # robot, then the desk in front of both
    draw_robot(fb)
    fb.rect(30, 706, 964, 22, DESK)
    fb.rect(30, 728, 964, 56, DESK_FRONT)
    fb.rect(170, 714, 230, 10, BEZEL)
    # captions
    draw_text(fb, W / 2, 52, "THE GAME CRASHES FOR EVERY HUMAN", 5, WHITE)
    draw_text(fb, W / 2, 872, "RAN PERFECTLY IN MY", 7, WHITE)
    draw_text(fb, W / 2, 936, "CONTEXT WINDOW", 7, WHITE)
    # glitch bars tearing across the game screen
    fb.rect(70, 428, 300, 10, (206, 62, 160))
    fb.rect(392, 522, 228, 8, (70, 205, 220))
    fb.rect(70, 612, 190, 8, (206, 62, 160))
    fb.rect(120, 442, 180, 5, (70, 205, 220))
    # speech bubble from the robot: tail first, then the bubble
    fb.poly([(622, 236), (678, 238), (750, 356)], WHITE)
    fb.rrect(392, 150, 300, 86, 18, WHITE)
    draw_text(fb, 542, 176, "SHIP IT!", 5, BLACK)


def render():
    fb = FB()
    draw_scene(fb)
    # box downsample SS x SS
    out = bytearray(W * H * 3)
    buf = fb.buf
    for yy in range(H):
        for xx in range(W):
            r = g = b = 0
            base = ((yy * SS) * SW + xx * SS) * 3
            for dy in range(SS):
                row = base + dy * SW * 3
                for dx in range(SS):
                    i = row + dx * 3
                    r += buf[i]
                    g += buf[i + 1]
                    b += buf[i + 2]
            o = (yy * W + xx) * 3
            n = SS * SS
            out[o] = r // n
            out[o + 1] = g // n
            out[o + 2] = b // n
    return bytes(out)


def png_bytes(w, h, rgb):
    def chunk(tag, data):
        c = zlib.crc32(tag)
        c = zlib.crc32(data, c)
        return (len(data).to_bytes(4, "big") + tag + data
                + (c & 0xFFFFFFFF).to_bytes(4, "big"))

    raw = bytearray()
    stride = w * 3
    for yy in range(h):
        raw.append(0)
        raw += rgb[yy * stride:(yy + 1) * stride]
    ihdr = (w.to_bytes(4, "big") + h.to_bytes(4, "big")
            + bytes((8, 2, 0, 0, 0)))
    return (b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", ihdr)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b""))


def main():
    outdir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(outdir, exist_ok=True)
    data = png_bytes(W, H, render())
    path = os.path.join(outdir, "entry.png")
    with open(path, "wb") as fh:
        fh.write(data)
    print("wrote %s (%d bytes)" % (path, len(data)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
