# Common Patterns & Gotchas

Developing for the 2600 is rewarding but challenging.  Here are common patterns to follow and pitfalls to avoid.

## Cycle Counting and Timing Errors

Because there are only 76 CPU cycles per scanline, it’s easy to overshoot and disrupt the picture.  Common mistakes include:

* **Incorrect branch timing** – Conditional branches consume either 2 or 3 cycles depending on whether they cross a page boundary.  Misjudging this can make your kernel too long.
* **Page crossing in indexed addressing** – When `LDA table,X` crosses a $0100 boundary, it costs an extra cycle.  Align tables so the highest index doesn’t cross a page.
* **Forgotten `WSYNC`** – Failing to wait for the next scanline can cause your code to “drift” into the visible portion, producing jitter.

Use cycle counting comments or a tool like 8bitworkshop’s cycle counter to verify each scanline.  If your picture rolls or shakes, your kernel likely has too few or too many cycles.

## HMOVE Bars and How to Avoid Them

Executing `HMOVE` extends the horizontal blank by 8 colour clocks and sends extra pulses to the position counters.  If you write to `HMPx` registers during this extension or too close to the left edge of the screen, the TIA draws a comb‑like bar known as an **HMOVE bar**.  To avoid it:

* Write `HMPx` values **no later than 24 CPU cycles** after the previous `HMOVE`.
* Execute `HMOVE` early in the scanline, ideally immediately after `WSYNC`.
* Perform all horizontal motion writes during vertical blank or overscan instead of the visible kernel.

Some games hide HMOVE bars by changing `COLUBK` to black for a few pixels at the left edge.

## Kernel Stability Checklist

To produce a stable picture:

* Hold `VSYNC` high for exactly 3 scanlines using `WSYNC`.
* Blank the beam with `VBLANK` for 37 (NTSC) or 48 (PAL) lines before drawing.
* Draw exactly 192 (NTSC) or 228 (PAL) visible scanlines using `WSYNC`.
* Blank again for 30 (NTSC) or 36 (PAL) overscan lines.
* Set up the RIOT timer and use `TIMER_WAIT` to enforce these counts.
* Avoid extra cycles at the end of your kernel; pad with `NOP` or `STA WSYNC` to align the loop.

If your game causes vertical jitter or horizontal misalignment, revisit this checklist.

## Common Beginner Bugs

* **Uninitialised memory** – Forgetting to clear variables can cause random behaviour.  Use `CLEAN_START` to zero the stack and RAM.
* **Forgetting to clear collisions** – If you don’t write to `CXCLR`, old collision flags persist and may trigger false hits.
* **Not disabling unused objects** – Players, missiles or the ball remain on screen until you write 0 to their graphics or enable registers.  Leaving them enabled produces phantom pixels.
* **Bank‑switching mistakes** – Jumping across bank boundaries or forgetting to place stubs in each bank can crash your game.

Carefully initialise all registers and test each feature in isolation before integrating them.

## Performance Optimization Tips

* **Use zero page** – Accessing addresses $00–$7F is one cycle faster than absolute addresses.  Store frequently used variables here.
* **Leverage illegal opcodes** – Undocumented instructions like `LAX` (load A and X simultaneously) and `DCP` (decrement and compare) save cycles but should be wrapped in macros for portability.
* **Unroll critical loops** – In the kernel, unroll loops to avoid branch overhead.  For example, manually write six `STA PF1` instructions instead of looping with `DEX/BNE`.
* **Precompute values** – Calculate positions, offsets and bit patterns during vertical blank rather than in the kernel.
* **Use the RIOT timer** – Offload delays to the timer instead of busy‑waiting.

Optimising for both speed and size requires practice; always profile your game and adjust as needed.
