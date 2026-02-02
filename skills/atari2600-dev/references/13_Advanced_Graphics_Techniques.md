# Advanced Graphics Techniques

Once you’re comfortable with basic playfield and sprite programming, you can push the hardware further using mid‑scanline changes and object multiplexing.  These techniques enable detailed 48‑pixel sprites, scoreboards and on‑screen text.

## 48‑Pixel (Big) Sprites

By default each player is only 8 pixels wide.  However, you can create a **48‑pixel** graphic by exploiting `NUSIZx` duplication and mid‑scanline writes.  The Woodgrain Wizard method works as follows:

1. Set `NUSIZ0` and `NUSIZ1` to **three close copies** (pattern `%011`), which draws each player three times separated by 16 pixels.
2. Position `P1` eight pixels to the right of `P0`.
3. Use `VDELP0` and `VDELP1` so writes to `GRP0` and `GRP1` take effect one scanline later.
4. During each scanline, load three bytes of graphic data and perform four quick stores:

```asm
    lda (ptr0),y   ; load next 8‑pixel slice for P0
    ldx (ptr1),y   ; load P1 slice
    sta GRP0
    stx GRP1
    sta GRP0       ; second copy for the right-hand halves
    stx GRP1
```

Because the players are offset, these writes interleave to form a continuous 48‑pixel line.  Repeat this every scanline to draw large sprites or six‑digit scoreboards.  When not drawing, set `GRPx` to 0 to hide duplicates.

## Multiplexing Sprites

The 2600 has only two players and two missiles, but you can reuse them multiple times per frame by repositioning them vertically.  This technique, called **multiplexing**, involves:

* During vertical blank, load a table of Y positions and pointers to sprite graphics.
* In the kernel, keep a scanline counter.  When it matches the next Y position, update `RESPx` and `HMPx` to set the horizontal position and then load the sprite graphics into `GRPx`.
* Use `VDELPx` to buffer the graphics so that writes can occur a scanline earlier.

Because repositioning a player consumes cycles, you may only have time to reuse each object 2–4 times per frame, but this is sufficient for games like *Centipede* or *Kaboom*.

## Mid‑Scanline Register Changes

The TIA latches graphics and colour registers at specific cycles within a scanline.  By rewriting registers between these latches you can create multi‑colour objects and complex playfields:

* **Playfield** – Write `PF0`/`PF1`/`PF2` once for the left half and again for the right half (as described in the Asymmetric Playfield section).
* **Sprite colour** – Change `COLUPx` mid‑scanline to give a sprite two colours (e.g., a character with a different coloured hat).
* **Sprite graphics** – Update `GRPx` after a delay to change the lower portion of the sprite (e.g., multi‑colour missiles).

To time these changes, count CPU cycles from `WSYNC` or use a custom delay macro.  Always ensure you complete writes before the corresponding object’s pixels are drawn; otherwise you’ll see tearing.

## Score Displays

The 2600 provides a special **score mode** in `CTRLPF` where the playfield’s left half uses `COLUP0` and the right half uses `COLUP1`.  Combined with asymmetric playfields, you can draw a six‑digit scoreboard.  A common method stores digits as **3×5** bitmaps and packs two digits into a single byte.  During the kernel:

1. Use a lookup routine (`GetBCDBitmap`) to fetch two digits’ bitmaps and store them in a buffer.
2. Write the left digit’s pattern to `PF1`, wait for 28 cycles (using `SLEEP`) and then write the right digit’s pattern.
3. Set `CTRLPF` to score mode and write `COLUP0`/`COLUP1` to set the digits’ colours.

This produces crisp numbers with minimal code.  For more digits, combine this with the 48‑pixel sprite technique.

## Text Rendering Techniques

Since each player sprite is 8 pixels wide, displaying text requires creativity:

* **4×5 or 3×5 fonts** – Use the playfield to draw narrow characters.  Each letter is a 4‑pixel wide bitmap stored in a table; you write `PF1` or `PF2` twice per line to draw the left and right halves.
* **Tiny font with players** – Use the 48‑pixel sprite technique and design a 6×7 character set; you can display six characters on one line.
* **Scrolling text** – Scroll the playfield data horizontally to make a ticker or credits sequence.  Use a timer to change the playfield every few frames.

Use overscan to compute which letters to draw next frame and update pointers accordingly.

## Sprite Reuse Patterns

To maximise the limited number of sprites:

* **Use missiles as extra players** – Missiles can act as bullets, paddles or vertical lines.  Align them with their players or reposition them independently.
* **Turn off objects when not needed** – Write zero to `GRPx`/`ENAMx`/`ENABL` so they don’t waste cycles drawing invisible pixels.
* **Double‑buffer graphics** – Store two copies of sprite graphics and swap pointers every frame; while one copy is on screen, you can update the other.

Combining these patterns allows you to display more objects than the hardware appears to support and is key to creating professional‑looking games.
