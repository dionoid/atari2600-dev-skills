# Game Logic and Timers

The 6532 RIOT chip provides a programmable down-counter timer essential for synchronising code with video timing. Combined with frame counters, state machines, and random number generation, it forms the foundation for game logic on the Atari 2600.

## 1. RIOT Timer

The RIOT timer is a single 8-bit down-counter that can be configured with four different tick intervals.

### Timer Set Registers (Write)

| Address | Register | Interval Per Tick | Max Duration |
|---------|----------|-------------------|--------------|
| `$0294` | `TIM1T` | 1 CPU cycle (0.84 µs) | 214 µs |
| `$0295` | `TIM8T` | 8 CPU cycles (6.7 µs) | 1.7 ms |
| `$0296` | `TIM64T` | 64 CPU cycles (53.6 µs) | 13.7 ms |
| `$0297` | `T1024T` | 1024 CPU cycles (858 µs) | 219 ms |

### Timer Read Registers

| Address | Register | Function |
|---------|----------|----------|
| `$0284` | `INTIM` | Current counter value (read-only) |
| `$0285` | `INSTAT` | D7: 1 = timer has underflowed (read-only) |

### Timer Behaviour

1. Write a value N to one of the set registers. The counter loads N and begins counting down.
2. Each tick (at the configured interval), the counter decrements by 1.
3. When the counter reaches 0, it holds 0 for one tick interval.
4. After that tick, it rolls over to `$FF` and begins counting down once per **CPU cycle** (regardless of the original interval).
5. Bit D7 of `INSTAT` is set to 1 after the underflow.

### TIM64T — The Standard Choice

`TIM64T` is the most commonly used timer for VBLANK and overscan timing. The formula to compute the timer value for N scanlines:

```
timer_value = ((N * 76) - 13) / 64
```

The `- 13` compensates for setup overhead. Examples:
- 37 scanlines (NTSC VBLANK): `((37 * 76) - 13) / 64 = 43` → write 43 to TIM64T
- 30 scanlines (NTSC overscan): `((30 * 76) - 13) / 64 = 35` → write 35 to TIM64T

### Polling the Timer

```asm
; Wait for timer to expire
.waitTimer:
    lda INTIM
    bne .waitTimer    ; loop while counter > 0
    sta WSYNC         ; final alignment to scanline boundary
```

## 2. TIMER_SETUP and TIMER_WAIT Macros

The `macro.h` file provides two macros that automate timer usage:

### TIMER_SETUP

```asm
    TIMER_SETUP 37    ; set timer for 37 scanlines
```

This macro:
1. Computes the correct TIM64T value for the requested number of scanlines.
2. Writes the value to `TIM64T`.
3. Adjusts for its own cycle overhead.

### TIMER_WAIT

```asm
    TIMER_WAIT        ; wait for timer to expire
```

This macro:
1. Polls `INTIM` until the counter underflows.
2. Executes a final `sta WSYNC` to align with the next scanline boundary.

### Usage in Frame Structure

```asm
GameLoop:
    VERTICAL_SYNC         ; 3 scanlines of VSYNC
    TIMER_SETUP VBLANK_LINES  ; start VBLANK timer (37 NTSC / 45 PAL)

    ; === GAME LOGIC GOES HERE ===
    ; Read input, update positions, process collisions
    ; You have ~2800 cycles (NTSC) to work with

    TIMER_WAIT            ; wait for VBLANK to finish
    lda #0
    sta VBLANK            ; turn off blanking, start visible frame

    ; === KERNEL (drawing) ===

    lda #%01000010
    sta VBLANK            ; turn on blanking for overscan
    TIMER_SETUP OVERSCAN_LINES  ; start overscan timer (30 NTSC / 36 PAL)

    ; === MORE GAME LOGIC ===
    ; Sound updates, animation counters, etc.
    ; You have ~2280 cycles (NTSC) to work with

    TIMER_WAIT            ; wait for overscan to finish
    jmp GameLoop
```

### Manual Timer Usage (Without Macros)

```asm
    lda #43               ; 37 scanlines worth of TIM64T ticks
    sta TIM64T
    ; ... do work ...
.wait:
    lda INTIM
    bne .wait
    sta WSYNC
```

## 3. Frame-Based Game Logic

### Frame Counter

Increment a counter each frame to drive time-based events:

```asm
; In VBLANK
    inc FrameCounter

; Animation every 8 frames
    lda FrameCounter
    and #%00000111        ; mask lower 3 bits (0-7)
    bne .noAnimation
    ; Update animation frame
    inc AnimFrame
.noAnimation:
```

### NTSC/PAL Timing

| Event | NTSC (60 Hz) | PAL (50 Hz) |
|-------|-------------|-------------|
| 1 second | 60 frames | 50 frames |
| 1/4 second | 15 frames | ~13 frames |
| 2 seconds | 120 frames | 100 frames |

Use `tv_modes.h` constants (`NTSC`, `PAL`) to adjust timing for both systems.

### Splitting Work Across VBLANK and Overscan

VBLANK provides ~37 scanlines (2,812 cycles) and overscan provides ~30 scanlines (2,280 cycles) on NTSC. Split game logic to fit:

- **VBLANK**: Input reading, position updates, collision processing, score updates
- **Overscan**: Sound updates, animation counters, AI routines, random number generation

## 4. Game State Machines

Use a state variable to manage game flow:

```asm
STATE_TITLE     = 0
STATE_PLAY      = 1
STATE_GAME_OVER = 2

; In the main loop, dispatch based on state
    lda GameState
    cmp #STATE_TITLE
    beq .doTitle
    cmp #STATE_PLAY
    beq .doPlay
    cmp #STATE_GAME_OVER
    beq .doGameOver
    jmp GameLoop         ; fallback

.doTitle:
    jsr TitleScreen_VBLANK
    jsr TitleScreen_Kernel
    jsr TitleScreen_Overscan
    jmp GameLoop

.doPlay:
    jsr Game_VBLANK
    jsr Game_Kernel
    jsr Game_Overscan
    jmp GameLoop

.doGameOver:
    jsr GameOver_VBLANK
    jsr GameOver_Kernel
    jsr GameOver_Overscan
    jmp GameLoop
```

Each state can have its own VBLANK logic, kernel, and overscan routines. Transition between states by writing to `GameState`:

```asm
; When player presses Reset on title screen
    lda SWCHB
    lsr
    bcc .startGame
    ; ...
.startGame:
    lda #STATE_PLAY
    sta GameState
```

## 5. Random Number Generation

### 8-Bit LFSR (Linear Feedback Shift Register)

A maximal-period 8-bit Galois LFSR produces 255 unique non-zero values:

```asm
; Call once per frame during VBLANK
GetRandom:
    lda Random
    lsr               ; shift right, bit 0 -> carry
    bcc .noFeedback
    eor #$B4          ; feedback polynomial (taps at bits 7,5,4,2)
.noFeedback:
    sta Random
    rts
```

Alternative Fibonacci LFSR (from the Atari community):

```asm
GetRandom:
    lda Random
    asl
    bcc .noFeedback
    eor #$1D          ; polynomial x^8 + x^4 + x^3 + x^2 + 1
.noFeedback:
    sta Random
    rts
```

**Important**: Seed `Random` with a non-zero value at startup. Zero produces a stuck state. A common trick: seed with the frame count when the player first presses fire.

### Using Random Numbers

```asm
    jsr GetRandom
    and #%00000111    ; mask to 0-7
    ; Use as enemy speed, spawn position, etc.
```

## 6. BCD Scoring

The 6502's decimal mode (`SED`) enables Binary-Coded Decimal arithmetic, where each nibble represents a digit 0-9:

```asm
; Increment score by 10 points
    sed               ; enable decimal mode
    lda Score
    clc
    adc #$10          ; add 10 in BCD ($10 = 10 decimal)
    sta Score
    lda Score+1       ; carry into high byte
    adc #0
    sta Score+1
    cld               ; ALWAYS disable decimal mode when done

; Score is now stored as BCD:
; Score+1 = high digits, Score = low digits
; e.g., $01 $50 = 150 points
```

**Critical**: Always `CLD` after BCD operations. Leaving decimal mode active corrupts all subsequent arithmetic (including address calculations in the kernel). The `CLEAN_START` macro clears the decimal flag at boot, but accidental `SED` without `CLD` is a common bug.

### Displaying BCD Scores

To display a BCD score, extract individual digits and use them as indices into a font table:

```asm
    lda Score
    and #$0F          ; low digit
    tax
    lda DigitBitmaps,x  ; lookup glyph

    lda Score
    lsr
    lsr
    lsr
    lsr               ; high digit
    tax
    lda DigitBitmaps,x
```

See [09_Advanced_Techniques.md] for 6-digit score display using 48-pixel sprites and [02_Frame_Structure_and_Timing.md] for frame structure details.
