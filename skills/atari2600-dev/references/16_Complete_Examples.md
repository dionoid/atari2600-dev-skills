# Complete Examples

## Scrolling Rainbow Screen Example

```
;===============================================================================
; Scrolling Raindbow - basic example ROM for the Atari 2600
;===============================================================================
    processor 6502

    include "include/vcs.h"
    include "include/macro.h"
    include "include/tv_modes.h"
    include "include/tia_constants.h"

TV_MODE = NTSC

;===============================================================================
; Variables
;===============================================================================
    SEG.U Variables
    ORG $80
    ;-------------------------------
    ; Your variables here (max 128!)
    ;-------------------------------
FrameCounter    ds 1

    ECHO "###", [128 - (* - $0080)]d, "bytes of unused RAM"

;===============================================================================
; ROM code (2K/4K ROM)
;===============================================================================
    SEG Code
    ORG $f000 ; use $f800 for a 2K ROM and $f000 for 4K

;===============================================================================
; Init
;===============================================================================
InitSystem:
    CLEAN_START ; initialize zero page and stack

;===============================================================================
; GameLoop - runs VerticalBlank, DisplayKernel and OverScan in a loop
;===============================================================================
GameLoop:
    inc FrameCounter

;--------------------------------------------------------------------------------
; VerticalBlank - perform game logic and prepare for display
;-------------------------------------------------------------------------------
VerticalBlank:
    ; vertical syncing and blanking...
    TIMER_SETUP VBLANK_LINES
    VERTICAL_SYNC
    
    ;------------------------
    ; Your game logic here
    ;------------------------

    TIMER_WAIT
    
    lda #STOP_VBLANK
    sta VBLANK ; stop blanking

;-------------------------------------------------------------------------------
; DisplayKernel - display visible screen
;-------------------------------------------------------------------------------
DisplayKernel:
    ; scanlines for drawing visible screen
    ldx FrameCounter
    ldy #KERNEL_LINES
.kernel_loop:
    inx
    stx COLUBK
    sta WSYNC
    dey
    bne .kernel_loop

;-------------------------------------------------------------------------------
; Overscan - handle controls, score and sound
;-------------------------------------------------------------------------------
OverScan:

    ; end of screen - enter blanking
    lda #(ENABLE_LATCHES | START_VBLANK)
    sta VBLANK

    ; scanlines of overscan...
    TIMER_SETUP OVERSCAN_LINES

    ;-------------------------------------
    ; Handle joystick input and sound here
    ;-------------------------------------

    TIMER_WAIT

    ; back to game loop
    jmp GameLoop

    ; show free space check before end of ROM
    echo "###", [$fffc - *]d, "bytes free before end of ROM"

    ORG $fffc ; interrupt vectors
    .word InitSystem          ; RESET
    .word InitSystem          ; IRQ/BRK
```

## Single-Sprite Demo

## Two-Player Game Skeleton

## Scoreboard Example

## Sound Effects Demo
