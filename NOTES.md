# Meme Sprint — "AI Agents Ship Games" entry

## Concept

A fresh twist on the classic "works on my machine" developer joke, made
specific to AI agents shipping software:

- **Top caption:** THE GAME CRASHES FOR EVERY HUMAN
- **Scene:** a smug robot agent — sunglasses, smirk, thumbs up — standing
  beside a big monitor running a broken platformer: the hero is falling
  through a gap in the floor, a red ERROR! popup is up, glitch bars tear
  across the screen, and the score reads -1. A speech bubble from the
  robot says: SHIP IT!
- **Bottom caption (punchline):** RAN PERFECTLY IN MY CONTEXT WINDOW

The joke lands in one reading: the agent tested the game only inside its
own context window, where it "ran perfectly", and shipped it anyway.

## Build approach

`main.py` is Python 3, standard library only, fully self-contained:

- Own PNG encoder (zlib, filter-0 scanlines, CRC chunks).
- Own hand-authored 5×7 bitmap font (A–Z, 0–9, basic punctuation),
  rendered bold with a double strike.
- Own rasterizer on a supersampled framebuffer (2×, box downsample):
  rectangles, rounded rectangles, circles, thick lines, scanline
  polygons, and a clip rectangle so the in-game hills stay inside the
  monitor screen.
- The program resolves its output directory first
  (`MAKEFUN_OUTPUT_DIR` if set, else `/output`), creates it, and writes
  `entry.png` only there — it never writes to the working directory,
  which the grader mounts read-only.
- Fully deterministic: no clock, no randomness, no network, no input.

## Verification

- Normal run: `entry.png` = 1024×1024 px, 16,683 bytes (limit 1 MiB).
- Visually inspected two renders; fixed in revision: hills overflowing
  the monitor bezel (now clipped to the screen), added the glitch bars
  and the SHIP IT! speech bubble.
- Simulated server conditions — read-only working directory, empty
  environment (`env -i`), no `MAKEFUN_OUTPUT_DIR`, writable `/output`:
  exit 0 on both runs, `entry.png` produced in `/output`, nothing
  written to the cwd, and both runs byte-identical.
- sha256 (all runs, normal and server-condition):
  `1fd3fe5ed1e01d8e06d6a8bc4c7c904270aa835a3fbd75e0ce9353094e2c8342`
