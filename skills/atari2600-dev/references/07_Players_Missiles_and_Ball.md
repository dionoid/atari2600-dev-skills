# Players, Missiles, and Ball

The Atari 2600 features five movable objects: two players (P0 and P1), two missiles (M0 and M1), and a ball.  All objects are drawn by the TIA hardware but controlled by the CPU via registers.

## Player Sprites (P0 and P1)

Players are **8‑pixel-wide**, 1‑bit monochrome sprites.  Their graphics data is loaded into `GRP0` or `GRP1`.  Each bit corresponds to one TIA colour clock (one pixel), and the colour comes from `COLUP0` or `COLUP1`.  Players have no built‑in X or Y coordinates.  To position them:

1. **Horizontal position** – Write to `RESP0` or `RESP1` to reset the horizontal counter to the current beam position.  Because the TIA counts horizontally at 1 colour clock per system cycle, the object will appear 37 (or 39) pixels later; you must time this write precisely within the scanline.
2. **Size and duplication** – The `NUSIZ0` and `NUSIZ1` registers control the number and spacing of copies (1, 2 or 3) and whether the sprite is doubled or quadrupled in width.
3. **Vertical positioning** – There is no Y coordinate; the sprite appears on every scanline until you disable it.  To move vertically, enable and disable graphics at specific scanlines by writing zero to `GRP0`/`GRP1` when you don’t want it drawn and reloading graphics when you do.

## Missiles and the Ball

Missiles (`M0`, `M1`) are single‑pixel wide objects aligned with their respective players.  They can be enabled/disabled via `ENAM0` and `ENAM1`.  Their size and copies are also controlled by `NUSIZ0`/`NUSIZ1`.  Horizontal positioning uses `RESM0` and `RESM1`; vertical positioning is controlled by when you write to `ENAMx` and update `HMMx` (horizontal motion).  Missiles inherit their colour from the associated player.

The ball (`BL`) is another single‑pixel wide object with its own enable (`ENABL`) and horizontal reset (`RESBL`).  Its size is selected via the lower bits of `CTRLPF`.  The ball shares colour with the playfield (`COLUPF`).

## Sprite Size and Duplication

`NUSIZ0` and `NUSIZ1` are 3‑bit registers with multiple functions:

* Bits 0–2 select duplication pattern: `000` = one copy, `001` = two copies close together, `010` = two copies medium, `011` = three copies close, `100` = two copies wide, `101` = single copy double size, `110` = triple copy double size, `111` = quad width.
* For missiles, bit patterns affect missile size (1, 2, 4 or 8 pixels wide).

Choosing the right pattern allows you to draw multiple enemies or 48‑pixel sprites by combining duplicates (see Advanced Graphics Techniques).

## Sprite Graphics Data Formats

Because each player byte is only 8 bits, complex images must be drawn over multiple scanlines.  A common approach is to store sprite images as a sequence of bytes in ROM, with one byte per scanline:

```asm
PlayerShip:
    .byte %00111100
    .byte %01111110
    .byte %11111111
    .byte %11111111
    .byte %01111110
    .byte %00111100
```

During the kernel you load these bytes into `GRP0`/`GRP1` on the appropriate scanlines.  Use the `VDELPx` registers to buffer graphics: when `VDELP0` is set, writes to `GRP0` take effect one scanline later, giving you extra time to update the register mid‑scanline.

## Sprite Animation Techniques

To animate sprites you can:

* **Cycle through multiple graphics frames** stored in ROM.  Update the pointer during vertical blank and read the next byte in the kernel.
* **Use vertical delay (VDELPx)** to buffer `GRPx` writes, allowing you to load a new byte while the previous one is still on the screen.  This is essential for 48‑pixel sprites or for changing colours mid‑scanline.
* **Alter duplication patterns** via `NUSIZx` between frames to grow or shrink sprites (e.g., for explosions).
* **Combine players and missiles** – Use missiles for extra bullets or to extend the width of a sprite.  Missiles can be repositioned independently and may be used for lasers, bats or paddles.

Animation on the 2600 is a balancing act between CPU time and memory.  Plan your kernels so that graphic updates occur during the horizontal blank and vertical blank periods to avoid jitter.
