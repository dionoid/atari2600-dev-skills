# Sprites, Positioning, and Motion

The Atari 2600 has five movable objects: two 8-pixel players (P0, P1), two 1-pixel missiles (M0, M1), and one 1-pixel ball (BL). None have built-in X or Y coordinates — positioning is accomplished through carefully timed register writes. For colour registers, see [04_Graphics_and_Playfield.md].

## 1. Player Sprites (P0 and P1)

### Graphics Registers

| Address | Register | Function |
|---------|----------|----------|
| `$1B` | `GRP0` | 8-bit graphics data for Player 0 |
| `$1C` | `GRP1` | 8-bit graphics data for Player 1 |

Each bit represents one colour clock (pixel). D7 is drawn first (leftmost) unless the player is reflected. The player colour comes from `COLUP0`/`COLUP1`.

### Reflection

| Address | Register | Bit | Function |
|---------|----------|-----|----------|
| `$0B` | `REFP0` | D3 | 1 = reflect P0 horizontally (D0 drawn first) |
| `$0C` | `REFP1` | D3 | 1 = reflect P1 horizontally |

### Vertical Positioning

There is no Y-coordinate register. To position a sprite vertically:
- Write the sprite graphics byte to `GRP0`/`GRP1` on scanlines where the sprite should appear.
- Write `#0` to `GRP0`/`GRP1` on all other scanlines.
- Use a Y counter in your kernel to determine which scanlines draw the sprite.

```asm
; Kernel loop — draw 8-line sprite at SpriteY
    ldx #KERNEL_LINES
.kernelLoop:
    sta WSYNC
    txa
    sec
    sbc SpriteY           ; A = current line - sprite Y
    cmp #SPRITE_HEIGHT    ; is it within sprite range?
    bcc .drawSprite
    lda #0                ; outside range: blank
    jmp .storeGRP
.drawSprite:
    tay
    lda SpriteData,y      ; load graphics for this line
.storeGRP:
    sta GRP0
    dex
    bne .kernelLoop
```

## 2. Missiles and Ball

### Missile Registers

| Address | Register | Function |
|---------|----------|----------|
| `$1D` | `ENAM0` | D1: 1 = enable Missile 0 |
| `$1E` | `ENAM1` | D1: 1 = enable Missile 1 |
| `$12` | `RESM0` | Strobe: reset M0 horizontal position |
| `$13` | `RESM1` | Strobe: reset M1 horizontal position |

Missiles are 1 pixel wide (expandable via NUSIZ). M0 inherits colour from `COLUP0`, M1 from `COLUP1`. Missiles have no graphics register — they are single solid pixels when enabled.

### Ball Register

| Address | Register | Function |
|---------|----------|----------|
| `$1F` | `ENABL` | D1: 1 = enable Ball |
| `$14` | `RESBL` | Strobe: reset Ball horizontal position |

The ball inherits colour from `COLUPF`. Ball width is set by CTRLPF bits D5-D4 (see [04_Graphics_and_Playfield.md]).

### Missile Lock

| Address | Register | Function |
|---------|----------|----------|
| `$28` | `RESMP0` | D1: 1 = lock M0 to centre of P0 |
| `$29` | `RESMP1` | D1: 1 = lock M1 to centre of P1 |

When locked, the missile tracks the player's position. Disable the lock before independently positioning the missile.

## 3. Size and Duplication (NUSIZ)

The `NUSIZ0` (`$04`) and `NUSIZ1` (`$05`) registers control player copies/sizing and missile width:

```
D7  D6  D5    D4    D3  D2     D1     D0
--  --  MSIZE1 MSIZE0 --  PSIZE2 PSIZE1 PSIZE0
```

### Player Size/Copy Patterns (D2-D0)

| Value | Pattern | Description |
|-------|---------|-------------|
| `%000` | `P.......` | One copy |
| `%001` | `P...P...` | Two copies, close (16 px gap) |
| `%010` | `P.......P.......` | Two copies, medium (32 px gap) |
| `%011` | `P...P...P...` | Three copies, close (16 px gap) |
| `%100` | `P...............P...............` | Two copies, wide (64 px gap) |
| `%101` | `PP..............` | One copy, double width |
| `%110` | `PP..PP..PP..` | Three copies, close, double width |
| `%111` | `PPPP............` | One copy, quad width |

### Missile Size (D5-D4)

| Value | Width |
|-------|-------|
| `%00` | 1 pixel |
| `%01` | 2 pixels |
| `%10` | 4 pixels |
| `%11` | 8 pixels |

Note: Missile duplication follows the same copy pattern as the associated player (set by D2-D0).

## 4. Horizontal Positioning

### Coarse Positioning (RESPx)

Writing to a `RESPx`/`RESMx`/`RESBL` strobe resets the object's horizontal position counter to the current beam position (approximately). The object will appear on the next scanline at that horizontal position, offset by a fixed number of colour clocks (5 for players, 4 for missiles/ball).

### Fine Positioning (HMxx and HMOVE)

The horizontal motion registers provide fine adjustment of ±8 pixels:

| Address | Register | Object |
|---------|----------|--------|
| `$20` | `HMP0` | Player 0 |
| `$21` | `HMP1` | Player 1 |
| `$22` | `HMM0` | Missile 0 |
| `$23` | `HMM1` | Missile 1 |
| `$24` | `HMBL` | Ball |

Only bits D7-D4 are used. The value is a 4-bit signed offset:

| HMxx Value | Motion (pixels) |
|------------|-----------------|
| `$80` (1000xxxx) | 8 right |
| `$90` (1001xxxx) | 7 right |
| `$A0` (1010xxxx) | 6 right |
| `$B0` (1011xxxx) | 5 right |
| `$C0` (1100xxxx) | 4 right |
| `$D0` (1101xxxx) | 3 right |
| `$E0` (1110xxxx) | 2 right |
| `$F0` (1111xxxx) | 1 right |
| `$00` (0000xxxx) | No motion |
| `$10` (0001xxxx) | 1 left |
| `$20` (0010xxxx) | 2 left |
| `$30` (0011xxxx) | 3 left |
| `$40` (0100xxxx) | 4 left |
| `$50` (0101xxxx) | 5 left |
| `$60` (0110xxxx) | 6 left |
| `$70` (0111xxxx) | 7 left |

Strobe `HMOVE` (`$2A`) to apply all pending motion values simultaneously. Strobe `HMCLR` (`$2B`) to zero all motion registers.

### The SetHorizPos Routine (REQUIRED for Smooth Movement)

**CRITICAL:** Any object that moves horizontally (spaceships, players, enemies, etc.) MUST use fine positioning for smooth movement. Coarse positioning (RESP0/RESP1 alone) moves in 15-pixel jumps, which looks extremely choppy. Fine positioning provides pixel-perfect control.

This is the canonical subroutine for positioning any object to any X coordinate (0-159). It combines coarse positioning (RESPx) and fine adjustment (HMxx) using the divide-by-15 algorithm:

```asm
;-------------------------------------------------------------------------------
; SetHorizPos - Position sprite with fine positioning (pixel-perfect)
; A = desired X coordinate (0-159)
; X = sprite number (0=P0, 1=P1, 2=M0, 3=M1, 4=BL)
;
; Algorithm: Divide X position by 15 to get coarse position and remainder.
; The coarse position is set by cycling through WSYNC + RESPx at the right time.
; The remainder (0-14) is converted to fine motion offset (-8 to +7 pixels).
;
; Must call sta HMCLR once before the first call.
; Must call sta WSYNC / sta HMOVE once after all calls to apply fine motion.
;-------------------------------------------------------------------------------
SetHorizPos:
    sec                 ; Set carry for subtraction
    sta WSYNC           ; Start on a fresh scanline
.divideLoop:
    sbc #15             ; Subtract 15 (one coarse position unit)
    bcs .divideLoop     ; Loop until negative (A now contains remainder - 15)
    ; When loop exits, we've divided position by 15:
    ; - Number of loop iterations = coarse position (set by RESP0,X timing)
    ; - A register = remainder - 15 (range: -15 to -1)
    eor #$07            ; Convert remainder to fine offset:
                        ; -15 to -1 becomes the correct HMxx value pattern
    asl                 ; Shift to upper nibble (HMxx uses bits D7-D4)
    asl
    asl
    asl
    sta HMP0,X          ; Set fine position offset
    sta RESP0,X         ; Strobe coarse position (timing from divideLoop)
    rts
```

**Usage pattern:**

```asm
    sta HMCLR            ; clear all motion registers first
    lda PlayerXPos
    ldx #0               ; X=0 for P0
    jsr SetHorizPos
    lda MissileXPos
    ldx #2               ; X=2 for M0
    jsr SetHorizPos
    sta WSYNC
    sta HMOVE            ; apply all fine positions
```

**Important**: `sta HMOVE` must be the first instruction after `sta WSYNC` (executed during HBLANK). Executing it later produces HMOVE bar artifacts.

## 5. Vertical Delay (VDELP0, VDELP1, VDELBL)

| Address | Register | Function |
|---------|----------|----------|
| `$25` | `VDELP0` | D0: 1 = delay P0 graphics by one scanline |
| `$26` | `VDELP1` | D0: 1 = delay P1 graphics by one scanline |
| `$27` | `VDELBL` | D0: 1 = delay Ball enable by one scanline |

When vertical delay is enabled, writes to `GRP0` go into a buffer rather than being displayed immediately. The buffered value is transferred to the display when the *other* player's graphics register is written:

- Writing `GRP0` → value goes to GRP0 buffer; GRP1 buffer → GRP1 display
- Writing `GRP1` → value goes to GRP1 buffer; GRP0 buffer → GRP0 display

This cross-copy mechanism is essential for:
- **48-pixel sprites**: allows loading 6 graphics slices with only 3 CPU registers (see [09_Advanced_Techniques.md])
- **Tight kernel timing**: gives extra cycles to update graphics data

## 6. HMOVE Bar Artifact

When `HMOVE` is strobed, the TIA extends the horizontal blank by 8 colour clocks, producing a visible black bar at the left edge of the scanline. This is called the **HMOVE bar** or **HMOVE comb**.

### How to Minimise HMOVE Bars

- Execute `sta HMOVE` immediately after `sta WSYNC` (cycle 0-3) so the extension occurs during normal HBLANK.
- Do not write to HMxx registers within 24 cycles after HMOVE.
- Perform all positioning during VBLANK or overscan when possible (HMOVE bars are invisible when the beam is blanked).
- Some games hide HMOVE bars by setting `COLUBK` to black for the leftmost pixels.

## 7. Common Positioning Patterns

### CRITICAL: Always Use Fine Positioning for Moving Objects

**RULE:** Any sprite that moves horizontally during gameplay (player ships, enemies, projectiles, etc.) MUST be positioned using `SetHorizPos` or equivalent fine positioning code. Using only coarse positioning (writing to RESP0/RESP1 directly without HMOVE) results in movement that jumps by 15 pixels at a time, which looks terrible.

**Why this matters:**
- Coarse positioning alone: Object jumps in 15-pixel increments (very choppy)
- Fine positioning (SetHorizPos): Object moves smoothly pixel-by-pixel
- Players immediately notice choppy movement and it makes games feel broken

**Examples:**
- ✅ Good: `lda shipX; ldx #0; jsr SetHorizPos` → smooth movement
- ❌ Bad: `lda #shipX; sta RESP0` → jumps by 15 pixels

### Smooth Movement

To move a sprite by 1 pixel per frame:
```asm
; During VBLANK
    lda SWCHA
    and #%10000000    ; P0 right
    bne .notRight
    inc PlayerX
.notRight:
    lda SWCHA
    and #%01000000    ; P0 left
    bne .notLeft
    dec PlayerX
.notLeft:
    ; Clamp to 0-159
    lda PlayerX
    bpl .notNeg
    lda #0
    sta PlayerX
.notNeg:
    cmp #160
    bcc .inRange
    lda #159
    sta PlayerX
.inRange:
```

### Sub-Pixel Movement

For slower speeds, use a fractional position:
```asm
    lda PlayerXFrac
    clc
    adc #$40          ; add 0.25 pixels per frame
    sta PlayerXFrac
    bcc .noCarry
    inc PlayerX       ; carry = moved 1 pixel
.noCarry:
```

### Page-Crossing Pitfalls

If a `LDA table,Y` instruction crosses a `$100` page boundary, it costs an extra cycle. This can break kernel timing. Align sprite data tables on page boundaries:

```asm
    align 256
SpriteData:
    .byte %00111100
    .byte %01111110
    ; ...
```

See [02_Frame_Structure_and_Timing.md] for kernel timing fundamentals and [09_Advanced_Techniques.md] for 48-pixel sprite and multiplexing techniques.
