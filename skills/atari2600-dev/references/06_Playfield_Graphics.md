# Playfield Graphics

The playfield is the Atari 2600’s background.  It consists of 40 low‑resolution pixels per scanline and is drawn by repeating a 20‑bit pattern across the left and right halves of the screen.  Although simple, the playfield can produce walls, platforms, mazes and scoreboards.

## Playfield Registers (PF0, PF1, PF2)

The 20‑bit playfield pattern is split across three registers:

* **`PF0`** – Holds the **leftmost 4 bits**, but bits are reversed (bit 7 is the leftmost pixel).
* **`PF1`** – Holds the **next 8 bits** (bits 7–0).
* **`PF2`** – Holds the **rightmost 8 bits** (bits 7–0).

The TIA copies these 20 bits to the left half of the screen starting at colour clock 68 and again to the right half at clock 148.  If you do nothing, the right half is a mirror of the left.  To create asymmetric playfields you must rewrite `PF0`/`PF1`/`PF2` after the left half has been drawn but before the right half starts (see below).

The playfield colour comes from `COLUPF` unless **score mode** is enabled, in which case the left half uses `COLUP0` and the right half uses `COLUP1`.

## Playfield Reflection and Symmetry

The `CTRLPF` register controls how the playfield pattern is used.  Bit 0 (`REFLECT`) selects reflection: 0 means copy the 20‑bit pattern to both halves (mirror), 1 means reflect the pattern about the centre, producing bilateral symmetry.  Bit 1 (`SCORE`) enables score mode, changing colours on each half.  Bit 2 (`PRIOR`) changes sprite priority so players can appear behind the playfield.

Using reflection reduces the amount of data you need to store.  Many games store half of a maze or shield and rely on reflection to mirror it on the right.

## Scrolling and Animated Playfields

Because there is no hardware scrolling, you must implement it manually by shifting the playfield registers and updating them each scanline:

```asm
; scroll playfield right by one pixel (3 colour clocks)
    lsr PF2          ; shift rightmost byte
    ror PF1
    ror PF0
    lda NewPFByte
    sta PF0          ; insert new bits at left
```

By performing such shifts during vertical blank or overscan you can scroll the background smoothly.  To animate bricks or platforms, change the playfield pattern every few frames.  Remember that each shift operation costs cycles, so plan your kernel accordingly.

## Asymmetric Playfields

In many games you need a different image on the right half of the screen (e.g., scoreboards, bricks).  To achieve this, write new values to `PF0`, `PF1` and `PF2` between **colour clocks 68 and 148**.  According to the VCS timing, the left half of the playfield is drawn starting at TIA clock 68 and the right half at clock 148.  Therefore, after writing the initial values at the beginning of the scanline, insert a timed delay (using `NOP` or a custom SLEEP macro) and then write the second set of values:

```asm
    lda LeftPF0
    sta PF0
    lda LeftPF1
    sta PF1
    lda LeftPF2
    sta PF2
    ; wait ~22 CPU cycles (equivalent to 68 TIA clocks)
    .repeat 22 : nop : .endr
    lda RightPF0
    sta PF0
    lda RightPF1
    sta PF1
    lda RightPF2
    sta PF2
```

This technique, often called **asymmetric playfield**, is used in Breakout‑style brick displays and scoreboards.  Align your playfield data on page boundaries to avoid crossing a page and incurring extra cycle penalties.

## Playfield Collision Detection

The TIA detects collisions between players/missiles/ball and the playfield.  When a player pixel overlaps a playfield pixel, a latch in the **`CXP0FB`** or **`CXP1FB`** register is set; `CXBLPF` reports ball–playfield collisions; `CXM0FB`/`CXM1FB` report missile collisions.  Bits 7 and 6 correspond to the two possible collision pairs, while bits 5–0 are undefined.  Read these registers during vertical blank and clear them with `CXCLR`.  Note that the playfield is only active during the visible kernel; objects that collide during VBLANK or overscan will not set these flags.
