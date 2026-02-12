# Frame Structure and Timing

The Atari 2600 has no frame buffer. The CPU must generate every scanline of video in real time as the television's electron beam sweeps across the screen. Understanding TV signal timing is therefore not optional -- it is the foundation of all 2600 programming.

> See [01_Architecture_and_Memory_Map.md] for the overall architecture and register addresses.

---

## 1. TV Signal Basics

A television builds an image by sweeping an electron beam across a phosphor-coated screen, one horizontal line at a time. As the beam sweeps left to right, the signal controls its intensity (and color), producing a single **scanline**. When the beam reaches the right edge, it turns off briefly and returns to the left side -- this is **horizontal blank** (HBLANK). When all scanlines for a frame have been drawn, the beam turns off and returns to the top-left corner -- this is **vertical blank** (VBLANK).

The Atari 2600 does not use interlacing. It sends a single non-interlaced field per frame, which means every frame stands alone:

| Property | NTSC | PAL |
| --- | --- | --- |
| Frame rate | 60 Hz | 50 Hz |
| Total scanlines per frame | 262 | 312 |
| Color clock frequency | 3.58 MHz | 3.55 MHz |
| CPU clock (color clocks / 3) | ~1.19 MHz | ~1.18 MHz |

The 2600's TIA chip handles horizontal timing automatically. Vertical timing, however, is entirely the programmer's responsibility. If you send the wrong number of scanlines, the picture will roll, judder, or display in black and white (PAL requires even scanline counts).

---

## 2. Frame Structure

Each frame is divided into four sections. Every scanline in every section takes exactly the same time: 228 color clocks = 76 CPU cycles.

### NTSC Frame: 262 Scanlines

```
 Section          Scanlines   CPU Cycles Available
 ─────────────────────────────────────────────────
 VSYNC                  3        228  (3 x 76)
 VBLANK                37      2,812  (37 x 76)
 Visible Kernel       192     14,592  (192 x 76)
 Overscan              30      2,280  (30 x 76)
 ─────────────────────────────────────────────────
 TOTAL                262     19,912  (262 x 76)
```

### PAL Frame: 312 Scanlines

```
 Section          Scanlines   CPU Cycles Available
 ─────────────────────────────────────────────────
 VSYNC                  3        228  (3 x 76)
 VBLANK                45      3,420  (45 x 76)
 Visible Kernel       228     17,328  (228 x 76)
 Overscan              36      2,736  (36 x 76)
 ─────────────────────────────────────────────────
 TOTAL                312     23,712  (312 x 76)
```

### Frame Diagram (NTSC)

```
     68 color clocks          160 color clocks
    ┌─ HBLANK ──┐┌──────── Visible ────────┐
    │           ││                          │
    ├───────────┤├──────────────────────────┤ ─┐
    │           ││  (beam off - VSYNC)      │  │ 3 lines   VSYNC
    ├───────────┤├──────────────────────────┤ ─┤
    │           ││  (beam off - blanked)    │  │ 37 lines  VBLANK
    │  CPU can  ││                          │  │  (game logic time)
    │  execute  ││                          │  │
    ├───────────┤├──────────────────────────┤ ─┤
    │  ~22 CPU  ││  ~53 CPU cycles of      │  │
    │  cycles   ││  visible pixels         │  │ 192 lines KERNEL
    │  (setup)  ││  (drawing only!)        │  │  (drawing time)
    │           ││                          │  │
    ├───────────┤├──────────────────────────┤ ─┤
    │           ││  (beam off - blanked)    │  │ 30 lines  OVERSCAN
    │  CPU can  ││                          │  │  (more logic time)
    │  execute  ││                          │  │
    └───────────┘└──────────────────────────┘ ─┘
```

---

## 3. Scanline Timing

Every scanline -- whether in VBLANK, the visible kernel, or overscan -- consists of exactly **228 color clocks**. The CPU clock runs at 1/3 the color clock rate, giving **76 CPU cycles per scanline**.

```
  One Scanline = 228 color clocks = 76 CPU cycles

  ┌── 68 color clocks ──┬──── 160 color clocks ────┐
  │   Horizontal Blank   │   Visible Pixels          │
  │   (~22.7 CPU cycles) │   (~53.3 CPU cycles)      │
  └──────────────────────┴───────────────────────────┘
```

Because 68 and 160 do not divide evenly by 3, a CPU instruction can straddle the HBLANK/visible boundary. In practice:

- **Horizontal blank:** 68 color clocks = 22 full CPU cycles + 2 leftover color clocks. This is your setup window -- load TIA registers here before the beam reaches visible pixels.
- **Visible region:** 160 color clocks = 53 full CPU cycles + 1 leftover color clock. During the kernel, TIA register writes in this region change what appears on screen mid-scanline.
- **Total per line:** 76 CPU cycles exactly (228 / 3 = 76).

### WSYNC -- Synchronizing to Scanlines

Writing any value to `WSYNC` ($02) halts the CPU until the next horizontal blank begins. This is how you align your code to scanline boundaries:

```asm
    sta WSYNC       ; CPU halts here, resumes at start of next HBLANK
    ; Now at cycle 0 of the new scanline (start of 68-clock HBLANK)
    stx COLUBK      ; 3 cycles -- changes background color for this line
```

WSYNC is essential for kernel timing. Without it, small variations in branch timing cause your code to drift across scanline boundaries.

---

## 4. Initialization and System Reset

At power-on or reset, the 6507 reads a 16-bit address from the **reset vector** at `$FFFC`-`$FFFD` and begins execution there. Your ROM must place the entry point address at this location:

```asm
    ORG $FFFC
    .word Reset     ; Reset vector -- execution starts here
    .word Reset     ; BRK/IRQ vector (unused on 2600, but must be present)
```

The first thing your code should do is call the `CLEAN_START` macro, which:

1. Disables interrupts (`sei`) and clears decimal mode (`cld`).
2. Sets the stack pointer to `$FF`.
3. Zeroes all of zero-page RAM ($00-$FF), which clears both TIA registers ($00-$7F) and RAM ($80-$FF).

```asm
Reset:
    CLEAN_START     ; Clear TIA, RAM, set stack to $FF
```

After `CLEAN_START`, the accumulator, X, and Y registers are all zero. You then initialize your game variables and jump into the main loop.

---

## 5. VBLANK Section -- Game Logic Goes Here

After the 3-line VSYNC, the beam is off and traveling back to the top of the screen. You have **37 scanlines** (NTSC) or **45 scanlines** (PAL) of VBLANK time. This is **2,812 CPU cycles** (NTSC) or **3,420 CPU cycles** (PAL) -- your primary window for game logic.

### What to do during VBLANK

- Read joystick input (`SWCHA`, `INPT4`/`INPT5`)
- Update player positions, velocities, and game state
- Process collisions (read collision registers, then `sta CXCLR` to clear them)
- Calculate score
- Set up horizontal positions for sprites (`RESP0`, `RESP1`, fine-tune with `HMxx`/`HMOVE`)
- Pre-calculate graphics pointers, colors, and any data the kernel will need

### VBLANK register

The `VBLANK` register ($01) controls whether the screen output is blanked:

- **Bit 1 (D1):** Set to 1 to blank the screen (output is black regardless of TIA state). Set to 0 to allow visible output.
- **Bit 6 (D6):** Controls input port latches (for trigger buttons).
- **Bit 7 (D7):** Controls paddle discharge (for paddle controllers).

Typical usage:

```asm
;---------------------------------------
; VSYNC (3 scanlines)
;---------------------------------------
    VERTICAL_SYNC           ; Macro: sets VSYNC for 3 lines

;---------------------------------------
; VBLANK (37 scanlines for NTSC)
;---------------------------------------
    TIMER_SETUP 37          ; Start RIOT timer for 37 scanlines
    lda #%01000010
    sta VBLANK              ; Turn on blanking (D1=1), enable latches (D6=1)

    ; === ALL GAME LOGIC GOES HERE ===
    ; Read input, update positions, check collisions, calculate score,
    ; set up sprite positions, pre-calculate kernel data...

    TIMER_WAIT              ; Wait for timer to expire

    lda #0
    sta VBLANK              ; Turn off blanking -- visible output begins
```

### Timer setup for VBLANK

The `TIMER_SETUP` macro writes to the RIOT's `TIM64T` register ($0296), which decrements a counter once every 64 CPU cycles. The formula used internally is:

```
timer_value = ((scanlines * 76) - 13) / 64
```

The 13-cycle offset accounts for the overhead of the macro itself and the `TIMER_WAIT` loop. After `TIMER_WAIT` returns and you execute a `sta WSYNC`, you are synchronized to the exact scanline boundary where the visible kernel should begin.

---

## 6. Visible Kernel -- Drawing ONLY

The kernel is the heart of your program. It runs for exactly **192 scanlines** (NTSC) or **228 scanlines** (PAL) and produces the visible picture. You have **76 CPU cycles per scanline** -- and that is all.

### The 76-cycle budget

Every visible scanline, you must:

1. Write to `WSYNC` to synchronize to the scanline start.
2. During the 68-clock HBLANK (~22 CPU cycles), set up TIA registers for this line.
3. During the 160-clock visible region (~53 CPU cycles), the TIA draws pixels. You can still write TIA registers to change colors or graphics mid-line, but every cycle counts.
4. Loop back for the next scanline.

### A minimal kernel loop

```asm
DisplayKernel:
    ldx #192                ; NTSC: 192 visible scanlines
.kernelLoop:
    sta WSYNC               ; Wait for start of scanline       [0]
    ; -- HBLANK begins (68 color clocks / ~22 CPU cycles) --
    stx COLUBK              ; Set background color              [3]
    ; -- visible pixels begin at color clock 68 --
    dex                     ;                                   [2]
    bne .kernelLoop         ;                                   [2/3]
```

This simple loop uses only ~10 cycles per scanline, leaving the rest unused. A real game kernel will be much tighter, updating `GRP0`, `GRP1`, `PF0`-`PF2`, `COLUP0`, `COLUP1`, `COLUBK`, and more on every line.

### WSYNC usage pattern

The standard kernel pattern is:

```asm
.line:
    sta WSYNC           ; Sync to start of scanline
    ; ... write TIA registers (must complete within 76 cycles) ...
    dey
    bne .line           ; Loop for all visible lines
```

Always place `sta WSYNC` at the **top** of the loop. This ensures you start each iteration at a known cycle position (the beginning of HBLANK).

---

## 7. Overscan -- More Game Logic Time

After the visible kernel, you enter the **overscan** period: **30 scanlines** (NTSC) or **36 scanlines** (PAL). This gives you another **2,280 CPU cycles** (NTSC) or **2,736 CPU cycles** (PAL) for game logic.

```asm
Overscan:
    lda #%01000010
    sta VBLANK              ; Turn on blanking (screen goes black)

    TIMER_SETUP 30          ; Start timer for 30 scanlines (NTSC)

    ; === MORE GAME LOGIC HERE ===
    ; Sound effects, state transitions, additional calculations,
    ; anything that did not fit in VBLANK...

    TIMER_WAIT              ; Wait for overscan period to end

    jmp MainLoop            ; Back to top of frame (VSYNC)
```

Between VBLANK and overscan, you have a combined **5,092 CPU cycles** (NTSC) or **6,156 CPU cycles** (PAL) per frame for all game logic. Budget your work across both periods as needed.

---

## 8. CRITICAL: What Goes in Each Section

```
 ╔═══════════════════════════════════════════════════════════════════╗
 ║  VBLANK (37 lines)  =  ALL GAME LOGIC                          ║
 ║    - Input reading (joystick, paddles, fire buttons)            ║
 ║    - Position updates, velocity, movement                      ║
 ║    - Collision detection and response                          ║
 ║    - Score calculation                                          ║
 ║    - Sprite horizontal positioning (SetHorizPos / HMOVE)       ║
 ║    - Pre-calculating colors, graphics pointers, kernel data    ║
 ║    - Any math, branching, or complex calculations              ║
 ╠═══════════════════════════════════════════════════════════════════╣
 ║  KERNEL (192 lines) =  DRAWING ONLY                            ║
 ║    - Writing pre-calculated values to TIA registers            ║
 ║    - GRP0, GRP1, PF0, PF1, PF2, COLUP0, COLUP1, COLUBK       ║
 ║    - ENAM0, ENAM1, ENABL for missiles and ball                 ║
 ║    - Simple scanline counter (dex / dey / bne)                 ║
 ║    - NO: collision checks, input reading, position math,       ║
 ║      complex branching, subroutine calls with variable timing  ║
 ╠═══════════════════════════════════════════════════════════════════╣
 ║  OVERSCAN (30 lines) =  MORE GAME LOGIC                       ║
 ║    - Sound effect updates (AUDCx, AUDFx, AUDVx)               ║
 ║    - State transitions (game over, level changes)              ║
 ║    - Additional calculations that did not fit in VBLANK        ║
 ╚═══════════════════════════════════════════════════════════════════╝
```

---

## 9. The MOST CRITICAL Mistake: Game Logic in the Kernel

**DO NOT put game logic in the visible kernel.**

This is the single most common mistake in 2600 programming and the hardest to debug. Here is why it is catastrophic:

### The problem

Each visible scanline gives you exactly **76 CPU cycles**. A simple `sta WSYNC` / load / store / decrement / branch loop uses about 10-15 cycles. That leaves some room for reading pre-calculated data and writing it to TIA registers.

But game logic -- reading joystick input, comparing positions, updating variables, branching on game state -- easily takes **50-200+ cycles**. If any iteration of your kernel loop exceeds 76 cycles, the CPU misses the next WSYNC and the TIA keeps drawing. The result:

- Your kernel takes more than 192 scanlines to complete.
- The total frame exceeds 262 scanlines.
- The picture rolls, tears, or judders.
- On PAL, odd scanline counts cause the display to lose color entirely.

### Example of the mistake

```asm
; BAD -- DO NOT DO THIS
.kernelLoop:
    sta WSYNC
    lda SWCHA           ; Read joystick -- WHY IS THIS HERE?!
    and #$F0
    cmp #$E0
    beq .noMove
    inc playerY          ; Updating game state in the kernel!
.noMove:
    lda (spritePtr),Y    ; Draw sprite
    sta GRP0
    dey
    bne .kernelLoop
```

The joystick reading and position update add variable-length branches inside the kernel. On some iterations this exceeds 76 cycles and the frame breaks.

### The fix

Move ALL logic to VBLANK or overscan. The kernel should only read pre-calculated values and write them to TIA:

```asm
; GOOD -- kernel only draws
.kernelLoop:
    sta WSYNC
    lda (spritePtr),Y    ; Read pre-calculated sprite data
    sta GRP0             ; Write to TIA
    lda (colorPtr),Y     ; Read pre-calculated color
    sta COLUP0           ; Write to TIA
    dey
    bne .kernelLoop
```

All the joystick reading and `playerY` updates happen in VBLANK, before the kernel starts.

---

## 10. Stable Kernels and 262 Scanlines

A "stable kernel" produces exactly the same number of scanlines every frame -- 262 for NTSC, 312 for PAL. This is essential for a rock-solid picture.

### Common sources of instability

- Game logic in the kernel (variable-length code paths)
- Forgetting to count the VSYNC scanlines (they are part of the 262)
- Off-by-one errors in loop counters
- Timer miscalculation (wrong value written to `TIM64T`)
- Conditional branches that skip `sta WSYNC` calls

### Verifying with `_scanEnd`

The Stella emulator provides the pseudo-register `_scanEnd`, which reports the total number of scanlines in the most recently completed frame. Use it in a Stella debug script to automatically validate your frame timing:

```
; debug.script -- run with headless Stella
frame #10
print _scanEnd
exitRom
```

If the output is not `262` (NTSC) or `312` (PAL), your frame timing is wrong. The build-and-run script in this project's toolchain automatically checks `_scanEnd` after assembling and running your ROM.

You can also press **Ctrl+G** in interactive Stella to see a real-time scanline count overlay.

### Counting scanlines manually

Without timers, you can verify your frame by adding up all the scanlines your code produces:

```
VSYNC:    3 lines  (VERTICAL_SYNC macro)
VBLANK:  37 lines  (counted by TIMER_SETUP 37 + TIMER_WAIT)
Kernel: 192 lines  (your loop counter)
Overscan: 30 lines (counted by TIMER_SETUP 30 + TIMER_WAIT)
                    ───
Total:  262 lines
```

Note that `tv_modes.h` defines `VBLANK_LINES = 40` for NTSC, which includes the 3 VSYNC lines in the count. The `TIMER_SETUP` macro is called with this value, and the `VERTICAL_SYNC` macro consumes 3 of those lines. The remaining 37 are the actual VBLANK scanlines timed by the RIOT timer.

---

## 11. Using TIMER_SETUP/TIMER_WAIT vs. Manual Scanline Counting

There are two approaches to timing the VBLANK and overscan periods:

### Approach 1: Manual WSYNC counting (simple but rigid)

```asm
    ; 37 lines of VBLANK, one WSYNC per line
    ldx #37
.vblankLoop:
    sta WSYNC
    dex
    bne .vblankLoop
```

Pros: Simple, exact, easy to understand.
Cons: No time for game logic -- the CPU spends every cycle in the wait loop.

### Approach 2: RIOT timer with TIMER_SETUP/TIMER_WAIT (recommended)

```asm
    TIMER_SETUP 37          ; Set RIOT timer for 37 scanlines
    ; ... do game logic here (up to ~2800 cycles) ...
    TIMER_WAIT              ; Wait for remaining time to elapse
```

The `TIMER_SETUP` macro writes to `TIM64T` ($0296), which decrements a counter once every 64 CPU cycles. The macro calculates the correct initial value:

```
timer_value = ((scanlines * 76) - 13) / 64
```

The `TIMER_WAIT` macro polls `INTIM` ($0284) in a tight loop until it reaches zero, then executes a final `WSYNC` to align to the scanline boundary.

**The RIOT timer is the standard approach for all real games.** It frees the CPU to execute variable-length game logic during VBLANK and overscan without worrying about exact cycle counts -- as long as the logic finishes before the timer expires.

### Manual timer setup (without macros)

If you need to understand what the macros do internally, here is the equivalent manual code:

```asm
    ; Timer setup for 37 scanlines of VBLANK
    ; (37 * 76 - 13) / 64 = 2799 / 64 = 43
    sta WSYNC
    lda #43
    sta TIM64T              ; Start countdown: 43 * 64 = 2752 cycles

    ; ... game logic ...

    ; Timer wait
.waitTimer:
    lda INTIM               ; Read current timer value
    bne .waitTimer           ; Loop until timer reaches 0
    sta WSYNC               ; Align to next scanline boundary
```

After `TIMER_WAIT`, when the timer reaches zero, it holds zero for one interval and then flips to $FF and begins decrementing once per CPU cycle (not per interval). This means if you are slightly late reading the timer, `INTIM` will read $FF, $FE, $FD, etc. -- you can determine how many cycles you overshot.

---

## 12. Complete Rainbow ROM -- Timing Demo

This is a complete, working program that assembles with dasm and produces a stable 262-scanline NTSC frame. It draws a rainbow effect by incrementing the background color on every visible scanline.

```asm
; rainbow.asm -- Frame timing demonstration
; Assembles with: dasm rainbow.asm -f3 -oout.bin
;
; Demonstrates:
;   - CLEAN_START initialization
;   - VERTICAL_SYNC for 3-line VSYNC
;   - TIMER_SETUP / TIMER_WAIT for VBLANK and overscan
;   - A 192-scanline visible kernel
;   - Stable 262-scanline NTSC frame

    processor 6502
    include "vcs.h"
    include "macro.h"

;===============================================================================
; Constants
;===============================================================================
VBLANK_LINES    = 37        ; Scanlines of VBLANK (after 3-line VSYNC)
KERNEL_LINES    = 192       ; Visible scanlines
OVERSCAN_LINES  = 30        ; Scanlines of overscan
                            ; Total: 3 + 37 + 192 + 30 = 262

;===============================================================================
; Variables
;===============================================================================
    SEG.U Variables
    ORG $80

frameCounter    ds 1        ; Increments every frame, drives color cycling

;===============================================================================
; ROM
;===============================================================================
    SEG Code
    ORG $F000

;-------------------------------------------------------------------------------
; Reset -- entry point from $FFFC vector
;-------------------------------------------------------------------------------
Reset:
    CLEAN_START             ; Zero RAM, clear TIA, stack to $FF, A=X=Y=0

;-------------------------------------------------------------------------------
; Main Loop -- one iteration = one complete frame
;-------------------------------------------------------------------------------
MainLoop:
    inc frameCounter        ; Advance color offset each frame

;---------------------------------------
; VSYNC (3 scanlines)
;---------------------------------------
    VERTICAL_SYNC           ; Sets VSYNC for exactly 3 scanlines

;---------------------------------------
; VBLANK (37 scanlines)
;---------------------------------------
    TIMER_SETUP VBLANK_LINES ; Start RIOT timer for 37 scanlines
    lda #%01000010
    sta VBLANK              ; Enable blanking (D1=1) and input latches (D6=1)

    ; ── Game logic goes here ──
    ; (In this demo there is nothing to do, but a real game would
    ;  read input, update positions, check collisions, and prepare
    ;  kernel data during this time.)

    TIMER_WAIT              ; Spin until timer expires, then WSYNC

    lda #0
    sta VBLANK              ; Disable blanking -- visible output starts now

;---------------------------------------
; Visible Kernel (192 scanlines)
; DRAWING ONLY -- no game logic here!
;---------------------------------------
    ldx frameCounter        ; Start color from current frame offset
    ldy #KERNEL_LINES       ; Loop counter = 192
.kernelLoop:
    sta WSYNC               ; Sync to start of scanline
    stx COLUBK              ; Set background color for this line
    inx                     ; Next color
    dey                     ; Decrement scanline counter
    bne .kernelLoop         ; Repeat for all 192 lines

;---------------------------------------
; Overscan (30 scanlines)
;---------------------------------------
    lda #%01000010
    sta VBLANK              ; Enable blanking

    TIMER_SETUP OVERSCAN_LINES ; Start timer for 30 scanlines

    ; ── More game logic could go here ──
    ; (Sound updates, state transitions, etc.)

    TIMER_WAIT              ; Spin until overscan period ends

    jmp MainLoop            ; Back to top -- start next frame

;===============================================================================
; Interrupt Vectors
;===============================================================================
    ORG $FFFC
    .word Reset             ; Reset vector
    .word Reset             ; BRK/IRQ vector
```

### What this program does

1. `CLEAN_START` initializes all hardware and RAM to zero.
2. Each frame increments `frameCounter`, which offsets the starting color.
3. `VERTICAL_SYNC` generates the 3-scanline VSYNC signal.
4. `TIMER_SETUP 37` / `TIMER_WAIT` consume exactly 37 VBLANK scanlines (with time for game logic in between).
5. The kernel loops 192 times, writing a new `COLUBK` color each line. The `inx` produces a cycling rainbow.
6. `TIMER_SETUP 30` / `TIMER_WAIT` consume exactly 30 overscan scanlines.
7. Total: 3 + 37 + 192 + 30 = **262 scanlines** -- a stable NTSC frame.

When run in Stella, the `_scanEnd` pseudo-register will report `262`. The display shows vertical rainbow stripes that shift downward each frame, creating a smooth animation.

---

## Quick Reference: Key Numbers

| Item | NTSC | PAL |
| --- | --- | --- |
| VSYNC lines | 3 | 3 |
| VBLANK lines | 37 | 45 |
| Visible kernel lines | 192 | 228 |
| Overscan lines | 30 | 36 |
| **Total scanlines** | **262** | **312** |
| Color clocks per scanline | 228 | 228 |
| HBLANK color clocks | 68 | 68 |
| Visible color clocks | 160 | 160 |
| CPU cycles per scanline | 76 | 76 |
| HBLANK CPU cycles | ~22 | ~22 |
| Visible CPU cycles | ~53 | ~53 |
| CPU cycles for VBLANK+overscan logic | 5,092 | 6,156 |
| Frame rate | 60 Hz | 50 Hz |
| CPU clock speed | ~1.19 MHz | ~1.18 MHz |
