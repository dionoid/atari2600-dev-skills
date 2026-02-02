# Graphics Basics

The Atari 2600 has no frame buffer; instead it streams pixels directly to the television.  Understanding how pixels and colours work is essential before drawing anything.

## Color Clock and Pixel Resolution

Each scanline consists of **228 TIA colour clocks**, of which **68 clocks** occur during the horizontal blank and **160 clocks** are visible.  The 6507 runs at one‑third the TIA clock, so **one CPU cycle equals three TIA pixels**.  The leftmost pixel of the visible area appears around CPU cycle 20, giving you approximately 22 cycles after `WSYNC` to set up TIA registers before drawing begins.  In practice the Atari’s horizontal resolution is 160 pixels across 192 (NTSC) or 228 (PAL) scanlines.

## NTSC Color System

NTSC encodes colour by altering the phase (hue) and amplitude (luminance) of a chroma signal.  The TIA uses **4 bits for hue** and **3 bits for luminance**, yielding **128 colour values**.  Colour register bits are arranged as `%CCCLLLL` where `CCC` selects one of eight luminance levels (0 = darkest, 7 = brightest) and `LLLL` selects one of 16 hues around the colour wheel.  PAL uses the same encoding but produces slightly different hues due to phase differences; SECAM only supports eight colours because it encodes colour differently.

## Color Registers and Luminance

The TIA provides four colour registers:

* **`COLUBK`** – Background colour; fills areas where no other graphics are drawn.
* **`COLUPF`** – Colour and luminance for the playfield and ball.
* **`COLUP0` / `COLUP1`** – Colours for player 0/missile 0 and player 1/missile 1 respectively.

Each register is 8 bits using the `%CCCLLLL` layout described above.  Changing a colour register takes effect immediately on the current scanline, so you can create horizontal colour bands by rewriting `COLUBK` or `COLUPF` mid‑scanline.

## Background and Playfield Colors

Because the playfield and background share a register (`COLUPF`/`COLUBK`), you must choose colours carefully.  The `CTRLPF` register’s **score mode** bit splits the playfield into left and right halves using `COLUP0` and `COLUP1` for each side.  This allows you to draw scoreboards with two independent colours.  Another bit in `CTRLPF` selects priority: setting it allows sprites to appear behind the playfield, useful for tunnels or objects hiding behind walls.

## Sprite Color Tricks

Sprites (players, missiles and the ball) each have their own colour register (`COLUP0` or `COLUP1`).  Here are a few tricks:

* **Multi‑colour sprites** – By rewriting `COLUPx` at different cycles within the same scanline you can change a sprite’s colour on the fly, creating horizontal stripes or gradient effects.
* **Score mode** – Use `CTRLPF`’s score bit to split the playfield colour.  Combine this with multi‑colour sprites to create eye‑catching scoreboards.
* **Colour cycling** – Increment the colour registers each frame to animate rainbows or flashing objects.  The sample rainbow ROM demonstrates this technique.

Remember that altering colour registers mid‑scanline consumes CPU cycles; plan such effects carefully within the 76‑cycle budget.
