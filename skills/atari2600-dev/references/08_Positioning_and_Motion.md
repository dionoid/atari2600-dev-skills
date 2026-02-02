# Positioning & Motion

Because the Atari 2600 lacks built‑in X and Y coordinates, positioning objects requires carefully timed writes to TIA registers.  Understanding horizontal and vertical motion is crucial for smooth gameplay.

## Horizontal Positioning Basics

Each sprite’s horizontal position is tracked by an internal counter that wraps every 160 visible pixels.  To move a sprite, you **reset** its counter to the current beam position using `RESP0`, `RESP1`, `RESM0`, `RESM1` or `RESBL`.  The object appears some pixels later because the TIA’s counters are offset.

To change the horizontal position each frame, write to the appropriate `RESx` during the vertical blank or overscan so you don’t disturb the kernel.

## RESPx and HMOVE Explained

While coarse positioning resets the counter, **fine positioning** uses the horizontal motion registers:

* `HMP0`, `HMP1`, `HMM0`, `HMM1`, `HMBL` – 4‑bit registers containing values from `0000` to `1111`, representing a shift of 0–15 pixels to the left.
* `HMOVE` – When written, the TIA reads the `HMPx` values and injects extra clock pulses into the position counters, shifting objects left by the specified number of pixels.

After an HMOVE, you should wait at least **24 CPU cycles** before writing to motion registers again; modifying them too soon can create the infamous **HMOVE bar** – a comb‑like artifact at the left edge of the screen.

## Fine vs Coarse Movement

Use coarse positioning (`RESPx`) for large movements (e.g., when repositioning a sprite after it leaves the screen) and fine positioning (`HMOVE`) for per‑frame movement (1–8 pixels).  A typical horizontal movement routine:

```asm
; SetHorizPos routine
; A = X coordinate
; RESP0+X = register to strobe for coarse positioning
SetHorizPos SUBROUTINE
            cpx #2 ; carry flag will be set for balls and missiles
            adc #0 ; (adding 1 to account for different timings)
            sec
            sta WSYNC
.loop       sbc #15
            bcs .loop
            eor #7
            asl
            asl
            asl
            asl
            sta.a HMP0,X  ; force absolute addressing for timing!
            sta RESP0,X
            rts
```

Note that *before* calling the SetHorizPos subroutine for the set of objects you want to position horizontally, you must (once) do `sta HMCLR` to reset any old horizontal fine position offsets. And after calling the SetHorizPos subroutine for the objects, you must (once) do: 
```asm
            sta WSYNC
            sta HMOVE ; apply horizontal fine position offset
```

Because HMOVE only shifts left, you must calculate the two’s complement of rightward motion (e.g., to move right by 3 pixels write value `-3 & $0F` to `HMPx`).

## Vertical Positioning

There is no vertical position register.  Instead you control **when** graphics are drawn:

* **Enable or disable drawing** – Write your graphics byte (`GRP0`/`GRP1`) on the scanlines where the object should appear and write `0` on other scanlines.
* **Use vertical delay** – Setting `VDELP0`, `VDELP1` or `VDELBL` causes writes to `GRPx` or `ENABL` to take effect one scanline later.  This allows you to update graphics during the visible portion of the previous line without affecting the current line.
* **Kernel loops** – Many games maintain a Y counter to determine which sprites appear on each scanline.  If `Y` equals the sprite’s vertical coordinate, the kernel loads the appropriate graphics byte; otherwise it writes zero.

## Common Positioning Pitfalls

* **Page‑crossing delays** – If a `LDA` or `STA` crosses a page boundary, it consumes an extra cycle, throwing off your timing.  Align sprite data on page boundaries to avoid this.
* **HMOVE bar** – Writing `HMOVE` too late or modifying `HMPx` within 24 cycles produces a black comb at the left edge.  Perform all motion writes at the start of the kernel or during vertical blank.
* **MISSILE resets** – Missiles inherit horizontal motion from their players when first reset.  If you move a player using HMOVE but forget to update the missile, it may drift.

## Stable Object Positioning Patterns

To achieve smooth movement:

* Reset your objects during vertical blank or overscan using `RESPx` and `HMOVE`.
* Use a frame counter to update fine motion every N frames (e.g., move 1 pixel every other frame for slower speeds).
* When updating multiple objects, write all `HMPx` values, then write a single `HMOVE` to apply them simultaneously.  This reduces the risk of HMOVE bars.

The combination of coarse resets and fine HMOVE shifts provides sub‑pixel motion resolution and allows you to implement inertia, gravity and collision responses on a system without hardware coordinates.
