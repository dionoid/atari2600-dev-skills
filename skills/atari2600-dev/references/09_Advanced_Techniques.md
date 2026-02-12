# Advanced Techniques

This document covers advanced programming techniques that push the Atari 2600 hardware beyond its apparent limits: 48-pixel sprites, score displays, sprite multiplexing, mid-scanline tricks, bank switching, and ROM optimisation.

## 1. 48-Pixel Sprites

By exploiting NUSIZ duplication and vertical delay (VDEL), you can display a continuous 48-pixel-wide image — six 8-pixel segments alternating between P0 and P1.

### Setup

1. Set `NUSIZ0` and `NUSIZ1` to `$03` (three close copies, 16-pixel gap).
2. Position P1 exactly 8 pixels to the right of P0 (use SetHorizPos from [05_Sprites_Positioning_and_Motion.md]).
3. Enable `VDELP0` and `VDELP1` (write `#1` to both).

### How VDEL Makes It Work

With VDEL enabled, writes to `GRP0` go to a buffer. The buffer contents transfer to the display register only when `GRP1` is written (and vice versa). This gives you an extra "register" for the tight timing window.

The six segments are drawn left-to-right:

| Segment | Player | Register | Cycle Window (centred image) |
|---------|--------|----------|------|
| G0 | P0 | GRP0 display | Before cycle 41 |
| G1 | P1 | GRP1 display | Before cycle 43 |
| G2 | P0 | GRP0 display | Cycles 44-46 |
| G3 | P1 | GRP1 display | Cycles 47-49 |
| G4 | P0 | GRP0 display | Cycles 49-51 |
| G5 | P1 | GRP1 display | Cycles 52-54 |

### Image Data Format

Store data in 6 page-aligned tables (one per segment). Each table has one byte per scanline. Use the page-boundary check to prevent timing-breaking page crossings:

```asm
    if >. != >[.+IMG_HEIGHT]
        align 256
    endif
ImageSeg0:
    .byte %01000010
    .byte %11100111
    ; ... IMG_HEIGHT bytes total
```

### 48-Pixel Kernel

```asm
    ldy #(IMG_HEIGHT-1)
BigSpriteLoop:
    sta WSYNC           ; 3     (0)
    lda ImageSeg0,y     ; 4     (4)
    sta GRP0            ; 3     (7)   seg0->[GRP0]
    lda ImageSeg1,y     ; 4     (11)
    sta GRP1            ; 3     (14)  seg1->[GRP1], seg0->GRP0 displayed
    lda ImageSeg2,y     ; 4     (18)
    sta GRP0            ; 3     (21)  seg2->[GRP0], seg1->GRP1 displayed
    lda ImageSeg3,y     ; 4     (25)
    tax                 ; 2     (27)  seg3 saved in X
    lda ImageSeg4,y     ; 4     (31)
    sta Temp            ; 3     (34)  seg4 saved in Temp (zero-page)
    lda ImageSeg5,y     ; 4     (38)  seg5 in A
    ldy Temp            ; 3     (41)  seg4 in Y
    stx GRP1            ; 3     (44)  seg3->[GRP1], seg2->GRP0 displayed
    sty GRP0            ; 3     (47)  seg4->[GRP0], seg3->GRP1 displayed
    sta GRP1            ; 3     (50)  seg5->[GRP1], seg4->GRP0 displayed
    sta GRP0            ; 3     (53)  flush: seg5->GRP1 displayed
    ldy ImageHeight     ; 3     (56)  restore Y counter
    dey                 ; 2     (58)
    sty ImageHeight     ; 3     (61)
    bne BigSpriteLoop   ; 2/3   (63/64)
```

**Critical timing notes:**
- The `stx GRP1` at cycle 44 triggers seg2 to display in GRP0 — this must happen before the beam reaches the G2 segment.
- All 6 image data tables must be page-aligned to guarantee consistent 4-cycle `LDA abs,Y` timing.
- The `sta GRP0` at cycle 53 is a dummy write that flushes seg5 from GRP1's buffer to display.

## 2. Score Displays

### Playfield Score Mode

Set `CTRLPF` D1 (SCORE) to make the left playfield use `COLUP0` and the right use `COLUP1`. Combined with asymmetric playfield writes, this creates a two-colour scoreboard.

### 6-Digit Score Using 48-Pixel Sprites

The most common approach uses the 48-pixel technique with digit bitmaps:

1. Store 0-9 digit glyphs as 5-byte tables (3x5 or 4x5 pixels).
2. During VBLANK, look up the current score's BCD digits and copy the corresponding glyph rows into the 6 image segment tables.
3. Draw using the 48-pixel kernel above.

```asm
; Digit lookup — 5 rows per digit, 4 pixels wide
DigitGfx:
    ; Digit 0
    .byte %01100000
    .byte %10010000
    .byte %10010000
    .byte %10010000
    .byte %01100000
    ; Digit 1
    .byte %01100000
    .byte %00100000
    .byte %00100000
    .byte %00100000
    .byte %01110000
    ; ... digits 2-9
```

## 3. Sprite Multiplexing

The 2600 has only 2 players and 2 missiles, but you can reuse them at different vertical positions within the same frame.

### Basic Multiplexing Pattern

1. During VBLANK, sort objects by Y position.
2. In the kernel, maintain a scanline counter.
3. When the counter matches an object's Y position, reposition the player horizontally and load new graphics.

```asm
; Simple 2-object multiplex using P0
; Objects sorted: Obj0.Y < Obj1.Y
    ldx #KERNEL_LINES
.kernelLoop:
    sta WSYNC
    cpx Obj0Y
    bne .notObj0
    lda Obj0Gfx
    sta GRP0
    ; Position was set during VBLANK
.notObj0:
    cpx Obj1Y
    bne .notObj1
    ; Need to reposition P0 for second object
    lda Obj1HMval
    sta HMP0
    sta HMOVE         ; apply motion (creates HMOVE bar)
    lda Obj1Gfx
    sta GRP0
.notObj1:
    dex
    bne .kernelLoop
```

Practical limit: 2-4 reuses per player per frame, depending on kernel complexity and vertical separation.

## 4. Mid-Scanline Register Changes

### Multicolour Sprites

Change `COLUPx` between scanlines (or mid-scanline) to give sprites different colours per row:

```asm
; Draw a multicolour 8-line sprite
    ldy #7
.spriteLoop:
    sta WSYNC
    lda SpriteColors,y
    sta COLUP0           ; colour for this row
    lda SpriteData,y
    sta GRP0             ; graphics for this row
    dey
    bpl .spriteLoop
```

### Mid-Scanline Colour Split

To change a sprite's colour partway through a scanline (e.g., different hat colour):

```asm
    sta WSYNC
    lda SpriteData,y
    sta GRP0
    lda #$28             ; hat colour
    sta COLUP0
    ; Wait N cycles for beam to reach colour change point
    SLEEP 20
    lda #$86             ; body colour
    sta COLUP0
```

Count cycles carefully from `sta WSYNC` to ensure the colour change happens at the right pixel.

## 5. Text Rendering

### Playfield Text

Use PF1/PF2 with asymmetric writes to display narrow (3-4 pixel) characters:

1. Store a 3x5 or 4x5 font as byte tables.
2. For each text row, compose PF1/PF2 values from the character bitmaps.
3. Write PF registers for left half, wait, write again for right half.

### Player-Based Text

Use the 48-pixel technique with a character set. Each character is 6-8 pixels wide; you can display 6-8 characters per line. Useful for title screens and game-over messages.

## 6. Bank Switching

### Overview

The 6507 CPU addresses only 4 KB of cartridge ROM at a time (`$F000`-`$FFFF`). Bank switching allows cartridges to contain more ROM by swapping 4 KB banks in and out of this window.

### Common Bank-Switching Schemes

| Scheme | ROM Size | Banks | Hotspot Addresses |
|--------|----------|-------|-------------------|
| 2K | 2 KB | 1 | None (maps to `$F800`-`$FFFF`) |
| 4K | 4 KB | 1 | None (maps to `$F000`-`$FFFF`) |
| F8 | 8 KB | 2 | `$1FF8` = bank 0, `$1FF9` = bank 1 |
| F6 | 16 KB | 4 | `$1FF6`-`$1FF9` = banks 0-3 |
| F4 | 32 KB | 8 | `$1FF4`-`$1FFB` = banks 0-7 |
| F8SC | 8 KB + 128B RAM | 2 | `$1FF8`-`$1FF9`; RAM: write `$1000`-`$107F`, read `$1080`-`$10FF` |
| F6SC | 16 KB + 128B RAM | 4 | Same pattern with SC RAM |
| F4SC | 32 KB + 128B RAM | 8 | Same pattern with SC RAM |
| 3F | up to 512 KB | Many | Write bank number to `$003F` |
| E0 | 8 KB | 8x1KB | Segments in `$1FE0`-`$1FF7` |

### Bank Switch Code Pattern

```asm
; Switch to bank 1 (F8 scheme)
SwitchToBank1:
    lda $1FF9            ; reading the hotspot switches the bank
    ; Execution continues in bank 1 at the same address
    ; So this code must exist at the same address in both banks!
```

**Important**: Place a small trampoline routine at the same address in every bank:

```asm
; In bank 0 at $FFF0:
    lda $1FF9            ; switch to bank 1
    jmp Bank1Entry

; In bank 1 at $FFF0:
    lda $1FF8            ; switch to bank 0
    jmp Bank0Entry
```

### SC (SuperChip) RAM

SC variants add 128 bytes of extra RAM to the cartridge:
- **Write port**: `$1000`-`$107F` (write-only)
- **Read port**: `$1080`-`$10FF` (read-only)

You must use the correct port — reading from the write port or writing to the read port produces undefined behaviour.

### Emulator Detection Signatures

Include signature bytes in your ROM to help emulators auto-detect the scheme:
- F8SC/F6SC/F4SC: First 256 bytes of each bank are identical, plus bytes `$53, $43` ("SC") at `$1FFA`.
- BF: Include `$42, $46, $42, $46` ("BFBF") anywhere in ROM.

## 7. ROM Optimisation

### Page-Aligned Data Tables

Indexed addressing (`LDA table,X`) takes an extra cycle when crossing a `$100` page boundary. Align lookup tables to prevent this:

```asm
    align 256
SinTable:
    .byte 0, 3, 6, 9, 12, ...
```

### Code Reuse vs Unrolling

- **Subroutines** save ROM but cost 12 cycles per call (6 for `JSR` + 6 for `RTS`).
- **Unrolling** saves cycles but costs ROM. Use it in time-critical kernel code.
- **Macros** expand inline (no call overhead) but duplicate code. Good for short repeated patterns.

### Illegal Opcodes

Some undocumented 6502 instructions save cycles by combining operations:

| Opcode | Name | Function | Cycles (ZP) |
|--------|------|----------|-------------|
| `$87` | SAX | Store A AND X to memory | 3 |
| `$A7` | LAX | Load A and X from memory | 3 |
| `$C7` | DCP | Decrement memory, compare with A | 5 |
| `$E7` | ISB | Increment memory, subtract from A | 5 |
| `$04` | NOP (zp) | 2-byte NOP, 3 cycles | 3 |

Use with caution — wrap in macros and note that not all assemblers support these mnemonics. dasm supports them when using the `-f3` format flag.

See [05_Sprites_Positioning_and_Motion.md] for the SetHorizPos routine, [04_Graphics_and_Playfield.md] for playfield score mode, and [12_Reference_and_Cheat_Sheets.md] for instruction timing tables.
