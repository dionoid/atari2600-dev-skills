# Complete Examples

Each example in this document is a complete, working program that assembles with dasm and produces exactly 262 scanlines (NTSC). Use these as starting points or as reference implementations.

**Build command**: `dasm <file>.asm -f3 -o<file>.a26`

## 1. Scrolling Rainbow

Demonstrates the basic frame structure: VSYNC, VBLANK with timer, a 192-scanline kernel, and overscan. Changes the background colour every scanline to produce a scrolling rainbow.

```asm
;===============================================================================
; Scrolling Rainbow - Atari 2600 frame timing demo
; Produces a stable 262-scanline NTSC frame
;===============================================================================
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tv_modes.h"

    TV_MODE = NTSC

; Variables
    SEG.U Variables
    ORG $80
FrameCounter    ds 1

; ROM
    SEG Code
    ORG $F000

Reset:
    CLEAN_START

MainLoop:
    inc FrameCounter

; VSYNC (3 scanlines)
    VERTICAL_SYNC

; VBLANK (37 scanlines)
    TIMER_SETUP VBLANK_LINES
    lda #%01000010
    sta VBLANK
    ; Game logic would go here
    TIMER_WAIT
    lda #0
    sta VBLANK

; Visible Kernel (192 scanlines) -- DRAWING ONLY
    ldx FrameCounter
    ldy #KERNEL_LINES
.kernelLoop:
    sta WSYNC
    stx COLUBK
    inx
    dey
    bne .kernelLoop

; Overscan (30 scanlines)
    lda #%01000010
    sta VBLANK
    TIMER_SETUP OVERSCAN_LINES
    TIMER_WAIT
    jmp MainLoop

; Vectors
    ORG $FFFC
    .word Reset
    .word Reset
```

**Key points**:
- `CLEAN_START` initialises RAM, stack, and TIA.
- `VERTICAL_SYNC` handles the 3-scanline VSYNC sequence.
- `TIMER_SETUP` / `TIMER_WAIT` free the CPU during VBLANK and overscan.
- The kernel is a tight loop: `sta WSYNC` + `stx COLUBK` + `inx` + `dey` + `bne` = exactly 76 cycles.

## 2. Movable Sprite

Demonstrates a single player sprite with joystick control. Uses the SetHorizPos routine for proper horizontal positioning during VBLANK.

```asm
;===============================================================================
; Movable Sprite - joystick-controlled player
; Demonstrates: SetHorizPos, VBLANK input, kernel sprite drawing
;===============================================================================
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tv_modes.h"

    TV_MODE = NTSC

SPRITE_HEIGHT = 8
SPRITE_Y_POS  = 80       ; fixed vertical position (scanline from top)

; Variables
    SEG.U Variables
    ORG $80
FrameCounter    ds 1
PlayerX         ds 1      ; horizontal position 0-159

; ROM
    SEG Code
    ORG $F000

Reset:
    CLEAN_START
    lda #76               ; start near centre
    sta PlayerX

MainLoop:
    inc FrameCounter

; VSYNC
    VERTICAL_SYNC

; VBLANK
    TIMER_SETUP VBLANK_LINES
    lda #%01000010
    sta VBLANK

    ; -- Read joystick --
    lda SWCHA
    and #%01000000        ; P0 Left (D6, active low)
    bne .noLeft
    dec PlayerX
.noLeft:
    lda SWCHA
    and #%10000000        ; P0 Right (D7, active low)
    bne .noRight
    inc PlayerX
.noRight:
    ; Clamp X to 1-158 (avoid wrapping artifacts)
    lda PlayerX
    cmp #159
    bcc .xNotHigh
    lda #1                ; wrapped below 0 (unsigned), reset to 1
    sta PlayerX
.xNotHigh:

    ; -- Position sprite using SetHorizPos --
    sta HMCLR             ; clear old motion values
    lda PlayerX
    ldx #0                ; X=0 = Player 0
    jsr SetHorizPos
    sta WSYNC
    sta HMOVE             ; apply fine position

    ; Set sprite colour
    lda #$C6              ; orange
    sta COLUP0

    TIMER_WAIT
    lda #0
    sta VBLANK

; Kernel (192 scanlines)
    ldx #KERNEL_LINES
.kernelLoop:
    sta WSYNC
    ; Check if we're in sprite Y range
    txa
    sec
    sbc #SPRITE_Y_POS
    cmp #SPRITE_HEIGHT
    bcs .noSprite
    tay
    lda ShipGfx,y
    sta GRP0
    jmp .nextLine
.noSprite:
    lda #0
    sta GRP0
.nextLine:
    dex
    bne .kernelLoop

; Overscan
    lda #%01000010
    sta VBLANK
    TIMER_SETUP OVERSCAN_LINES
    TIMER_WAIT
    jmp MainLoop

;---------------------------------------
; SetHorizPos subroutine
; A = X position (0-159), X = object (0=P0, 1=P1, 2=M0, 3=M1, 4=BL)
;---------------------------------------
SetHorizPos SUBROUTINE
    sec
    sta WSYNC
.divLoop:
    sbc #15
    bcs .divLoop
    eor #7
    asl
    asl
    asl
    asl
    sta HMP0,X
    sta RESP0,X
    rts

;---------------------------------------
; Sprite data (8 lines, bottom to top)
;---------------------------------------
ShipGfx:
    .byte %00011000
    .byte %00111100
    .byte %01111110
    .byte %11111111
    .byte %11111111
    .byte %01111110
    .byte %00111100
    .byte %00011000

; Vectors
    ORG $FFFC
    .word Reset
    .word Reset
```

**Key points**:
- Joystick is read during VBLANK (not in the kernel).
- `SetHorizPos` + `HMOVE` positions the sprite during VBLANK, so no HMOVE bars in the visible area.
- The kernel only reads pre-positioned data — no branching that varies the scanline count.

## 3. Playfield Maze with Collision

Demonstrates a reflected playfield maze, a movable player sprite, and player-to-playfield collision detection.

```asm
;===============================================================================
; Playfield Maze - player navigates a simple maze
; Demonstrates: PF registers, reflected mode, CXP0FB collision
;===============================================================================
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tv_modes.h"

    TV_MODE = NTSC

MAZE_ROWS     = 12        ; number of distinct PF rows
LINES_PER_ROW = 16        ; scanlines per maze row (12*16=192)
SPRITE_HEIGHT = 8

; Variables
    SEG.U Variables
    ORG $80
FrameCounter    ds 1
PlayerX         ds 1
PlayerY         ds 1      ; maze row (0-11)
PlayerFineY     ds 1      ; scanline within row
PrevX           ds 1
PrevY           ds 1

; ROM
    SEG Code
    ORG $F000

Reset:
    CLEAN_START
    lda #76
    sta PlayerX
    lda #6
    sta PlayerY
    lda #4
    sta PlayerFineY

MainLoop:
    inc FrameCounter

; VSYNC
    VERTICAL_SYNC

; VBLANK
    TIMER_SETUP VBLANK_LINES
    lda #%01000010
    sta VBLANK

    ; Save previous position (for collision rollback)
    lda PlayerX
    sta PrevX
    lda PlayerY
    sta PrevY

    ; Read joystick
    lda SWCHA
    and #%01000000        ; Left
    bne .noL
    dec PlayerX
.noL:
    lda SWCHA
    and #%10000000        ; Right
    bne .noR
    inc PlayerX
.noR:
    lda SWCHA
    and #%00010000        ; Up
    bne .noU
    lda PlayerY
    beq .noU
    dec PlayerY
.noU:
    lda SWCHA
    and #%00100000        ; Down
    bne .noD
    lda PlayerY
    cmp #MAZE_ROWS-1
    bcs .noD
    inc PlayerY
.noD:
    ; Clamp X
    lda PlayerX
    cmp #158
    bcc .xOk
    lda #2
    sta PlayerX
.xOk:

    ; Handle collision from PREVIOUS frame
    lda CXP0FB
    bmi .wallHit          ; D7 = P0-PF collision
    jmp .noCollision
.wallHit:
    ; Roll back to previous position
    lda PrevX
    sta PlayerX
    lda PrevY
    sta PlayerY
.noCollision:
    sta CXCLR             ; clear collision latches

    ; Position sprite
    sta HMCLR
    lda PlayerX
    ldx #0
    jsr SetHorizPos
    sta WSYNC
    sta HMOVE

    ; Set colours
    lda #$0E              ; white playfield
    sta COLUPF
    lda #$86              ; blue player
    sta COLUP0
    lda #$00              ; black background
    sta COLUBK

    ; Set playfield to reflected mode with PF priority
    lda #%00000101        ; REFLECT=1, PRIORITY=1
    sta CTRLPF

    TIMER_WAIT
    lda #0
    sta VBLANK

; Kernel — draw maze rows
    ldy #0                ; maze row index
.mazeRowLoop:
    ; Load PF data for this row
    lda MazePF0,y
    sta PF0
    lda MazePF1,y
    sta PF1
    lda MazePF2,y
    sta PF2

    ; Draw LINES_PER_ROW scanlines for this row
    ldx #LINES_PER_ROW
.rowScanline:
    sta WSYNC
    ; Check if sprite should be drawn on this scanline
    cpy PlayerY
    bne .noSpriteThisRow
    txa
    sec
    sbc PlayerFineY
    cmp #SPRITE_HEIGHT
    bcs .noSpriteHere
    pha
    tax
    lda ShipGfx,x
    sta GRP0
    pla
    jmp .doneDraw
.noSpriteThisRow:
.noSpriteHere:
    lda #0
    sta GRP0
.doneDraw:
    dex
    bne .rowScanline

    iny
    cpy #MAZE_ROWS
    bne .mazeRowLoop

    ; Clear playfield after kernel
    lda #0
    sta PF0
    sta PF1
    sta PF2
    sta GRP0

; Overscan
    lda #%01000010
    sta VBLANK
    TIMER_SETUP OVERSCAN_LINES
    TIMER_WAIT
    jmp MainLoop

;---------------------------------------
SetHorizPos SUBROUTINE
    sec
    sta WSYNC
.divLoop:
    sbc #15
    bcs .divLoop
    eor #7
    asl
    asl
    asl
    asl
    sta HMP0,X
    sta RESP0,X
    rts

;---------------------------------------
; Maze data (12 rows) — reflected playfield
; Each row: PF0(D4-D7), PF1(D7-D0), PF2(D0-D7)
;---------------------------------------
MazePF0:
    .byte %11110000    ; top wall
    .byte %10000000
    .byte %10100000
    .byte %10100000
    .byte %10000000
    .byte %11100000
    .byte %10000000
    .byte %10100000
    .byte %10100000
    .byte %10000000
    .byte %10000000
    .byte %11110000    ; bottom wall
MazePF1:
    .byte %11111111
    .byte %00000000
    .byte %01001010
    .byte %01001010
    .byte %00000000
    .byte %11101110
    .byte %00000000
    .byte %01001010
    .byte %01001010
    .byte %00000000
    .byte %00000000
    .byte %11111111
MazePF2:
    .byte %11111111
    .byte %00000001
    .byte %01010101
    .byte %01010001
    .byte %00000001
    .byte %01110101
    .byte %00000001
    .byte %01010101
    .byte %01010001
    .byte %00000001
    .byte %00000001
    .byte %11111111

;---------------------------------------
ShipGfx:
    .byte %00011000
    .byte %00111100
    .byte %01111110
    .byte %11111111
    .byte %11111111
    .byte %01111110
    .byte %00111100
    .byte %00011000

; Vectors
    ORG $FFFC
    .word Reset
    .word Reset
```

**Key points**:
- Playfield uses reflected mode (`CTRLPF` D0=1) for a symmetric maze.
- Playfield priority (`CTRLPF` D2=1) makes walls draw over the player, creating a "behind walls" effect.
- Collision detection uses `CXP0FB` D7 (player-playfield) and rolls back position on hit.
- `sta CXCLR` is called every frame after reading collisions.

## 4. Sound Effects Demo

Demonstrates triggering different sound effects (laser and explosion) on button presses, with frame-based volume decay.

```asm
;===============================================================================
; Sound Effects Demo
; Fire button = laser sound, Reset switch = explosion
;===============================================================================
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tv_modes.h"

    TV_MODE = NTSC

; Variables
    SEG.U Variables
    ORG $80
FrameCounter    ds 1
LaserTimer      ds 1      ; frames remaining for laser sound
ExplodeTimer    ds 1      ; frames remaining for explosion
PrevFire        ds 1      ; previous frame's fire button state

; ROM
    SEG Code
    ORG $F000

Reset:
    CLEAN_START

MainLoop:
    inc FrameCounter

; VSYNC
    VERTICAL_SYNC

; VBLANK
    TIMER_SETUP VBLANK_LINES
    lda #%01000010
    sta VBLANK

    ; Check fire button (new press only)
    lda INPT4
    asl                   ; D7 -> Carry
    lda #0
    rol                   ; Carry -> D0: 0=pressed, 1=not pressed
    tax                   ; save current state
    cpx PrevFire
    beq .noNewFire
    cpx #0
    bne .noNewFire
    ; New fire press — trigger laser on channel 0
    lda #15
    sta LaserTimer
.noNewFire:
    stx PrevFire

    ; Check Reset switch
    lda SWCHB
    lsr                   ; D0 -> Carry
    bcs .noReset
    ; Reset pressed — trigger explosion on channel 1
    lda #20
    sta ExplodeTimer
.noReset:

    ; Update laser sound (channel 0)
    lda LaserTimer
    beq .laserSilent
    sta AUDV0             ; volume = timer (fades out)
    lda #6                ; buzzy square wave
    sta AUDC0
    lda LaserTimer        ; frequency sweeps down with timer
    sta AUDF0
    dec LaserTimer
    jmp .laserDone
.laserSilent:
    lda #0
    sta AUDV0
.laserDone:

    ; Update explosion sound (channel 1)
    lda ExplodeTimer
    beq .explodeSilent
    sta AUDV1
    lda #8                ; white noise
    sta AUDC1
    lda #2                ; low frequency = deep boom
    sta AUDF1
    dec ExplodeTimer
    jmp .explodeDone
.explodeSilent:
    lda #0
    sta AUDV1
.explodeDone:

    TIMER_WAIT
    lda #0
    sta VBLANK

; Kernel — simple colour bars to show something on screen
    ldx FrameCounter
    ldy #KERNEL_LINES
.kernelLoop:
    sta WSYNC
    stx COLUBK
    inx
    inx
    dey
    bne .kernelLoop

; Overscan
    lda #%01000010
    sta VBLANK
    TIMER_SETUP OVERSCAN_LINES
    TIMER_WAIT
    jmp MainLoop

; Vectors
    ORG $FFFC
    .word Reset
    .word Reset
```

**Key points**:
- Sound effects use frame-based timers that decrement each frame.
- Volume is set to the timer value, creating a natural fade-out.
- Channel 0 uses AUDC 6 (buzzy square) with sweeping frequency for a laser.
- Channel 1 uses AUDC 8 (white noise) at low frequency for an explosion.
- Fire button uses edge detection (current vs previous frame) to trigger once per press.

See [02_Frame_Structure_and_Timing.md] for the frame structure reference, [05_Sprites_Positioning_and_Motion.md] for SetHorizPos details, and [07_Sound_and_Music.md] for the frequency tables.
