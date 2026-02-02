# Timers & Game Logic

The 6532 RIOT chip provides a programmable timer that is invaluable for synchronising your code with video timing and implementing game logic.  Combined with frame counters and state machines, it allows you to build responsive games.

## RIOT Timers Explained

The RIOT has a single down counter accessed via the `INTIM` register.  To start the timer you write a value to one of four set registers: `TIM1T`, `TIM8T`, `TIM64T` or `T1024T`.  These names indicate the number of CPU cycles per tick (1, 8, 64 or 1024).  When you write a value, the timer begins counting down; when it underflows it reloads with $00 and sets bit 7 of `INSTAT`.  Reading `INTIM` returns the current counter value.

## Using Timers for Delays

Because 76 CPU cycles equal one scanline, you can use the timer to wait an exact number of lines.  For example, to delay `N` scanlines using the `TIM64T` interval, compute `((N * 76) + 13) / 64` as the timer value (13 compensates for overhead).  The `macro.h` file defines handy macros:

```asm
    TIMER_SETUP 37    ; load timer for 37 scanlines of VBLANK
    ; ...perform tasks while timer counts down...
    TIMER_WAIT        ; loop until INTIM underflows
```

These macros automatically compute the correct value for `TIM64T` and poll `INTIM` until it reaches zero.

Use `TIM1T` for very short delays (1–255 cycles) and `T1024T` for long delays (up to ~262 ms).  The timer continues counting in the background, so you can perform other work while waiting.

## Frame-Based Game Logic

Most games run their logic once per frame.  A frame counter increments every time through the main loop; you can use it to:

* Update animations every N frames (e.g., flip a sprite every 8 frames).
* Spawn enemies at regular intervals (e.g., every 120 frames).
* Alternate between players in two‑player games.

Because the frame rate is 60 Hz (NTSC) or 50 Hz (PAL), dividing the frame counter by 60 gives seconds elapsed.  Avoid placing heavy computations inside the kernel; restrict them to vertical blank and overscan.

## Game State Machines

Complex games are easier to manage with a **state machine**.  Represent each state with a label (e.g., `STATE_TITLE`, `STATE_PLAY`, `STATE_GAME_OVER`) and store the current state in a variable.  In the main loop, dispatch to the appropriate routines:

```asm
MainLoop:
    lda GameState
    cmp #STATE_TITLE
    beq RunTitle
    cmp #STATE_PLAY
    beq RunPlay
    cmp #STATE_GAME_OVER
    beq RunGameOver
    jmp MainLoop
```

Each state can have its own vertical blank and kernel routines.  Transition between states by updating `GameState` when the player presses Start or loses a life.

## Random Number Generation

Games often need random events.  One approach is to read unused bits of ROM or the stack, but a better method is to implement a **linear‑feedback shift register (LFSR)**.  A maximal‑period 8‑bit LFSR produces 255 non‑zero values before repeating.  A simple Fibonacci LFSR rotates the register and XORs bits to produce randomness:

```asm
Random:
    lda RandomByte
    asl
    bcc .noFeedback
    eor #$1d       ; feedback polynomial x^8 + x^4 + x^3 + x^2 + 1
.noFeedback:
    sta RandomByte
    rts
```

Call this routine during vertical blank to update your `RandomByte`.  To use the Galois LFSR variant, shift right and XOR on the fly; refer to the Making Games guide for code and constants.

Use random numbers for enemy movement, procedural level generation or pseudo‑randomised bonuses.  Remember that reading the collision registers or the stack pointer can also provide “noisy” data, but an LFSR is deterministic and reproducible if seeded consistently.
