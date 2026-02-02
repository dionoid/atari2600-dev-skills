# Input Handling

Interactivity on the Atari 2600 is achieved through the RIOT’s two I/O ports.  Properly reading joysticks, paddles and console switches ensures responsive controls without disrupting the video kernel.

## Joystick Input

Joysticks connect to **Port A (SWCHA)**.  Bits 7–4 correspond to player 0’s directions (right, left, down, up) and bits 3–0 correspond to player 1’s directions (left, right, down, up).  A bit is **0** when the switch is closed (direction pressed) and **1** when open.

Example code to read player 0’s left/right and up/down:

```asm
    lda SWCHA
    and #%11110000     ; isolate P0 bits
    bpl .p0Right       ; Bit7 (right) is 0 when pressed
    ; handle right movement
.p0Right:
    bmi .p0Left        ; Bit6 (left) is 0 when pressed
    ; handle left movement
.p0Left:
    and #%00100000     ; Bit5 (down)
    beq .p0Down        ; handle down
    and #%00010000     ; Bit4 (up)
    beq .p0Up          ; handle up
```

Joystick fire buttons are read via the **INPT4** and **INPT5** registers; bit 7 is **0** when the button is pressed.  Always configure `SWACNT` so these pins are inputs (set bits to 1).

## Paddles and Analog Input

Paddle controllers use potentiometers and are read through the **INPT0–INPT3** registers.  A paddle triggers an internal resistor‑capacitor circuit; the RIOT timer measures how long each input line remains low after being discharged.  To read paddles:

1. Write to `VBLANK` to allow the paddle circuit to charge.
2. Reset the RIOT timer using `TIM1T`.
3. Poll `INPTn` until bit 7 goes high; the value in `INTIM` gives the paddle position.

Because reading paddles consumes time, do it during vertical blank or overscan to avoid disrupting the kernel.

## Console Switches (Reset, Select, Color/BW)

Console switches connect to **Port B (SWCHB)**.  Bits are low when pressed:

* Bit 7 – `P1_DIFF` (player 1 difficulty); bit 6 – `P0_DIFF`.
* Bit 3 – `COLOR`/`BW` (0 = black‑and‑white, 1 = colour mode).
* Bit 1 – `GAME_SELECT`; bit 0 – `GAME_RESET`.

Example code using `BIT` and branch instructions to test the Color/BW switch without changing `A`:

```asm
    lda SWCHB
    ldx #$00
    bit SWCHB        ; test bits 7 and 6; BIT leaves bits 7/6 in N/V flags
    bvc .p0bDiff     ; branch if colour/BW bit (bit3) is 0 (black‑and‑white)
    ; handle colour mode
.p0bDiff:
```

Reading switches is best done during vertical blank or overscan so you don’t steal cycles from the kernel.

## Debouncing and Input Timing

Mechanical switches bounce, producing rapid on/off transitions when pressed or released.  You can debounce by sampling the input over several frames and only acting when the state remains consistent.  For example, maintain a two‑frame history of the joystick or button state and only accept an input when both samples are equal.  This also prevents accidental double resets when the Reset switch is flicked.

## Reading Input During VBLANK

The vertical blank and overscan periods provide around 37 + 30 = 67 scanlines of time (~5 ms) to perform non‑video tasks.  Use this time to:

* Poll `SWCHA`, `SWCHB`, `INPT0–5` and store the results in zero‑page variables.
* Debounce buttons and interpret joystick directions.
* Update game logic based on input.

Avoid reading input during the visible kernel; any branching or time spent on I/O may throw off your cycle counting and cause jitter or misaligned graphics.
