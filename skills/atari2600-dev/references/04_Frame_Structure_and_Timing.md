# Frame Structure & Timing

Unlike modern consoles, the Atari 2600 does not have a frame buffer.  Instead the CPU must generate each scanline of video in real time as the electron beam sweeps across the screen.  A reliable game therefore divides each 262‑line NTSC frame (or 312‑line PAL frame) into well‑timed sections.

## Initialization and System Reset

At power‑on or reset, the 6507’s program counter jumps to the address stored at $FFFC.  Your code should start with a **CLEAN_START** macro that:

1. Clears zero‑page RAM and sets the stack pointer to $FF.
2. Disables interrupts and resets the decimal flag.
3. Initializes TIA registers such as `COLUBK` (background colour) and disables audio.

Next you typically jump into a perpetual game loop containing the vertical blank, kernel and overscan routines.

## Vertical Blank (VBLANK) Explained

When the electron beam reaches the bottom of the screen, it returns to the top.  During this retrace the TIA does not display graphics; this period is called **vertical blank**.  In NTSC the standard frame allocates **37 lines** of VBLANK after the three lines of vertical sync; PAL uses **48 lines**.  Developers control VBLANK by writing to the `VBLANK` register:

```asm
    lda #%01000010
    sta VBLANK     ; blank the screen and disable player/missile graphics
    ; ...perform game logic here...
    lda #0
    sta VBLANK     ; end blanking before entering the visible kernel
```

The vertical blank is the best time to:

* Update game state, move objects and respond to input.
* Clear collision registers (`CXCLR`) and read `INTIM` to set up timers.
* Prepare graphics data for the upcoming kernel.

## Kernel vs Overscan

The **kernel** is your visible drawing routine.  It typically iterates exactly **192 scanlines** for NTSC or **228 scanlines** for PAL, using `WSYNC` to wait for the start of each line and updating TIA registers at precise cycles.  Because each scanline has only 76 CPU cycles, you must carefully budget your instructions to finish before the beam reaches the next line.

After drawing, the 2600 enters **overscan**, another blanking period at the bottom of the frame.  Overscan lasts about **30 lines** for NTSC or **36 lines** for PAL.  Developers often use overscan to:

* Read joystick and console switch inputs (using `SWCHA` and `SWCHB`).
* Compute audio values and update `AUDVx`, `AUDCx` and `AUDFx`.
* Draw status bars or decompress graphics for the next frame.

Overscan uses the same `VBLANK` register to blank the beam and disable objects.

## Frame Timing and Scanline Budgeting

With 76 CPU cycles per scanline, you must plan how many cycles you spend on each operation.  For example:

* **Setting `PF0`/`PF1`/`PF2` and `COLUBK`** early in the scanline (during the 68‑cycle horizontal blank) leaves roughly 22 cycles to update player graphics before the visible pixels begin.
* **Using `WSYNC`** after writing to TIA registers ensures the CPU waits until the next scanline.  This is essential to align your kernel loop.
* **Counting scanlines** – Many kernels use a loop counter (`Y`) initialised with the number of visible lines and decrement it each `WSYNC`.  When `Y` reaches zero, the kernel ends.

The RIOT timer can also track scanlines.  Writing a value to `TIM64T` and polling `INTIM` until it underflows allows you to wait a fixed number of lines without explicit loop counters.

## Stable Kernels and 262 Scanlines

To achieve a stable picture, your kernel must output exactly the same number of scanlines every frame.  A typical NTSC frame sequence is:

1. **Vertical sync** – Set `VSYNC` for 3 scanlines (`VERTICAL_SYNC` macro).
2. **Vertical blank** – Blank the beam and run game logic for 37 scanlines using the timer (`TIMER_SETUP`/`TIMER_WAIT` macros).
3. **Visible kernel** – Draw the playfield and sprites for 192 scanlines.
4. **Overscan** – Blank the beam again and handle input/sound for 30 scanlines before looping back to the top.

You can verify stability by counting scanlines in Stella (Ctrl‑G).  A drifting picture indicates that your kernel is too short or too long; adjust timing loops or add `NOP` instructions to pad cycles.

## A Simple Rainbow ROM (Timing Demo)

A classic timing demonstration is the *rainbow* program that changes the background colour every scanline.  The kernel increments a frame counter and uses it to select a colour:

```asm
InitSystem:
    CLEAN_START
GameLoop:
    inc FrameCounter

VerticalBlank:
    TIMER_SETUP #37         ; wait 37 VBLANK lines
    VERTICAL_SYNC
    TIMER_WAIT
    lda #0
    sta VBLANK

DisplayKernel:
    ldx FrameCounter
    ldy #192
.kernel_loop:
    inx
    stx COLUBK              ; change background colour each line
    sta WSYNC               ; wait for next scanline
    dey
    bne .kernel_loop

Overscan:
    lda #%01000010
    sta VBLANK
    TIMER_SETUP #30
    ; read controls or play sound here
    TIMER_WAIT
    jmp GameLoop
```

When assembled and run, this program produces vertical stripes cycling through all 128 colours, demonstrating how to synchronise code with scanlines and use the RIOT timer.
