# Complete Examples

This section provides fully working code samples demonstrating techniques discussed throughout the guide.  Each example uses the macros from `macro.h` and the definitions in `vcs.h`.

## Scrolling Rainbow Screen Example

The following program displays a vertical rainbow that scrolls through all 128 NTSC colours.  It demonstrates how to structure a frame with vertical sync, vertical blank, a kernel loop that changes the background colour every line, and overscan:

```asm
;===============================================================================
; Scrolling Rainbow - basic example ROM for the Atari 2600
;===============================================================================
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tia_constants.h"
    include "../include/tv_modes.h"

    TV_MODE = NTSC

; Variables
    SEG.U Variables
    ORG $80
FrameCounter    ds 1

; ROM code (4 KB)
    SEG Code
    ORG $f000

InitSystem:
    CLEAN_START       ; zero RAM, set stack, disable interrupts
GameLoop:
    inc FrameCounter  ; increment each frame
VerticalBlank:
    TIMER_SETUP VBLANK_LINES
    VERTICAL_SYNC     ; hold VSYNC for 3 scanlines
    ; game logic could go here
    TIMER_WAIT        ; wait for end of VBLANK
    lda #STOP_VBLANK
    sta VBLANK
DisplayKernel:
    ldx FrameCounter
    ldy #KERNEL_LINES
.kernel_loop:
    inx               ; change colour every line
    stx COLUBK        ; update background colour
    sta WSYNC         ; wait for next scanline
    dey
    bne .kernel_loop
Overscan:
    lda #(ENABLE_LATCHES | START_VBLANK)
    sta VBLANK        ; blank screen during overscan
    TIMER_SETUP OVERSCAN_LINES
    ; handle input or sound here
    TIMER_WAIT
    jmp GameLoop

    ORG $fffc         ; interrupt vectors
    .word InitSystem  ; RESET vector
    .word InitSystem  ; IRQ/BRK vector (unused)
```

When assembled, this program produces coloured stripes across the screen and scrolls them by incrementing the frame counter each frame.

## Single‑Sprite Demo

This example draws a single 8‑pixel sprite (a player ship) and moves it left or right in response to the joystick.  It illustrates sprite positioning, reading joystick input and implementing simple motion.

```asm
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tia_constants.h"
    include "../include/tv_modes.h"

    SEG.U Variables
    ORG $80
PlayerX     ds 1    ; coarse X position (0–159)
Motion      ds 1    ; fine motion (0–15)

    SEG Code
    ORG $f000
InitSystem:
    CLEAN_START
    lda #37          ; initial coarse position (approx middle)
    sta PlayerX
    lda #0
    sta Motion
MainLoop:
    TIMER_SETUP VBLANK_LINES
    VERTICAL_SYNC
    ; Read joystick left/right
    lda SWCHA
    and #%01000000   ; bit6 = P0 left (0 when pressed)
    beq .moveLeft
    lda SWCHA
    and #%10000000   ; bit7 = P0 right
    beq .moveRight
    jmp .noMove
.moveLeft:
    dec PlayerX
    jmp .noMove
.moveRight:
    inc PlayerX
.noMove:
    TIMER_WAIT
    lda #STOP_VBLANK
    sta VBLANK
    ; Kernel – draw sprite on 10 scanlines
    ldy #10
.draw_loop:
    lda ShipGraphic,y
    sta GRP0         ; load sprite byte
    ; set colour
    lda #$C6         ; orange colour
    sta COLUP0
    ; position sprite using RESP0 and HMOVE
    lda PlayerX
    sta RESP0        ; coarse position
    lda Motion
    sta HMP0
    sta HMOVE
    sta WSYNC
    dey
    bpl .draw_loop
    ; overscan
    lda #(ENABLE_LATCHES | START_VBLANK)
    sta VBLANK
    TIMER_SETUP OVERSCAN_LINES
    TIMER_WAIT
    jmp MainLoop

ShipGraphic:
    .byte %00111100
    .byte %01111110
    .byte %11111111
    .byte %11111111
    .byte %01111110
    .byte %00111100
    .byte %00111100
    .byte %01100110
    .byte %11000011
    .byte %00000000

    ORG $fffc
    .word InitSystem
    .word InitSystem
```

## Two‑Player Game Skeleton

A basic two‑player game needs to manage two sets of sprites, missiles and input.  The following skeleton sets up two player ships, reads both joysticks and updates positions accordingly.  You can extend this to create Pong, Combat or other two‑player games:

```asm
; definitions omitted for brevity; see Single-Sprite Demo for setup
P0X    ds 1
P1X    ds 1
GameState ds 1
; ...init code...
MainLoop:
    ; read player 0 joystick
    lda SWCHA
    and #%01000000
    beq .p0Left
    lda SWCHA
    and #%10000000
    beq .p0Right
    ; read player 1 joystick (bits0–3)
    ; update P0X/P1X accordingly
    ; draw both players in the kernel, similar to Single-Sprite Demo
```

Fill in the logic to move `P0X` and `P1X` and to draw both sprites on their respective scanlines.  Use `NUSIZx` to choose sizes and duplication patterns and `COLUPx` to assign different colours to each player.

## Scoreboard Example

This example shows how to draw a numeric scoreboard using playfield score mode.  Each digit is a 3×5 bitmap; two digits are packed into one byte and displayed on one scanline.

```asm
; Scoreboard variables
ScoreP0  ds 1
ScoreP1  ds 1
; ...init code...
Kernel:
    ldy #5                ; five rows high
.rowLoop:
    lda ScoreP0
    jsr DrawDigitPair     ; draws a pair of digits from ScoreP0 and ScoreP1
    sta WSYNC
    dey
    bne .rowLoop
    ; continue with game graphics

DrawDigitPair:
    ; A contains digit pairs packed in nibbles
    lsr a
    ; lookup bitmaps and write PF1 twice with delay
    ; set CTRLPF to score mode and COLUP0/COLUP1 for different colours
    rts
```

See the Score Displays section for details on packing bitmaps and timing writes.

## Sound Effects Demo

Finally, here’s a small routine to play a laser blast sound on channel 0:

```asm
PlayLaser:
    lda #$0F      ; volume 15
    sta AUDV0
    lda #$06      ; square wave
    sta AUDC0
    lda #$0C      ; frequency (adjust to taste)
    sta AUDF0
    ; decay volume
    ldx #15
.decay:
    stx AUDV0
    jsr WaitFrame ; waits one frame using timer or counter
    dex
    bpl .decay
    lda #0
    sta AUDV0     ; silence
    rts
```

Call `PlayLaser` during vertical blank when the player fires.  The volume envelope decreases each frame, creating a fading effect.
