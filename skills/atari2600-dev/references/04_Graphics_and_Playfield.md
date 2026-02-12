# Graphics and Playfield

The TIA generates all video output on the Atari 2600. This document covers the colour system, playfield registers, playfield timing, and display priorities. For sprite graphics, see [05_Sprites_Positioning_and_Motion.md].

## 1. Colour System

### Colour Registers

Four TIA registers control the colour of all on-screen objects:

| Address | Register | Controls |
|---------|----------|----------|
| `$06` | `COLUP0` | Player 0, Missile 0 |
| `$07` | `COLUP1` | Player 1, Missile 1 |
| `$08` | `COLUPF` | Playfield, Ball |
| `$09` | `COLUBK` | Background |

### Colour Encoding (NTSC)

Each colour register uses the format `%HHHHLLLL`:

```
D7  D6  D5  D4  D3  D2  D1  D0
COL3 COL2 COL1 COL0 LUM2 LUM1 LUM0  (unused)
|---- hue ----|  |-- luminance --|
```

- **D7-D4 (hue)**: 16 values selecting the colour. Hue `$0x` = grey (no colour).
- **D3-D1 (luminance)**: 8 levels from dark (0) to bright (7).
- **D0**: Ignored by hardware. Values `$34` and `$35` produce the same colour.
- **Total unique colours**: 128 (16 hues x 8 luminance levels).

### NTSC Hue Reference

| Hue (D7-D4) | Hex Range | Colour |
|-------------|-----------|--------|
| `$0x` | `$00`-`$0E` | Grey |
| `$1x` | `$10`-`$1E` | Gold/Yellow |
| `$2x` | `$20`-`$2E` | Orange |
| `$3x` | `$30`-`$3E` | Red-Orange |
| `$4x` | `$40`-`$4E` | Pink/Red |
| `$5x` | `$50`-`$5E` | Purple |
| `$6x` | `$60`-`$6E` | Blue-Purple |
| `$7x` | `$70`-`$7E` | Blue |
| `$8x` | `$80`-`$8E` | Blue |
| `$9x` | `$90`-`$9E` | Cyan |
| `$Ax` | `$A0`-`$AE` | Cyan-Green |
| `$Bx` | `$B0`-`$BE` | Green |
| `$Cx` | `$C0`-`$CE` | Green-Yellow |
| `$Dx` | `$D0`-`$DE` | Yellow-Green |
| `$Ex` | `$E0`-`$EE` | Yellow |
| `$Fx` | `$F0`-`$FE` | Yellow-Orange |

Increase D3-D1 for brighter shades. Example: `$1E` = bright gold, `$12` = dim gold.

### PAL Colour Differences

PAL has only 104 unique colours (vs 128 on NTSC) because the TIA's phase-shift mechanism maps to only 12 hues on PAL (instead of 15 effective NTSC hues). The colours are also interleaved rather than sequential. When targeting both systems, test colour values on each or use the `tv_modes.h` colour constants.

### Mid-Scanline Colour Changes

Colour registers are latched by the TIA each colour clock. You can change `COLUBK`, `COLUPF`, or `COLUPx` mid-scanline to produce horizontal colour bands or multicolour sprites. Time your writes by counting cycles from `sta WSYNC`.

## 2. Playfield Registers

The playfield occupies the full screen width (160 pixels) using three registers that define a 20-bit pattern for the left half. The right half is either a duplicate or a mirror of the left half.

### Register Layout

| Address | Register | Active Bits | Scan Order |
|---------|----------|-------------|------------|
| `$0D` | `PF0` | D7-D4 (4 bits) | D4, D5, D6, D7 (reversed) |
| `$0E` | `PF1` | D7-D0 (8 bits) | D7, D6, D5, D4, D3, D2, D1, D0 (normal) |
| `$0F` | `PF2` | D7-D0 (8 bits) | D0, D1, D2, D3, D4, D5, D6, D7 (reversed) |

**Total**: 4 + 8 + 8 = 20 bits representing the left half of the screen. Each playfield bit controls a 4-colour-clock (4 pixel) wide block.

### Bit Scan Order Detail

The TIA scans playfield bits in this order across the left half:

```
Screen position (left to right):
PF0: D4  D5  D6  D7
PF1: D7  D6  D5  D4  D3  D2  D1  D0
PF2: D0  D1  D2  D3  D4  D5  D6  D7
```

Note that PF0 and PF2 are scanned in reversed bit order (LSB toward screen centre), while PF1 is scanned MSB-first. This asymmetry is a common source of confusion.

### Example: Drawing a Simple Wall

```asm
    ; Draw walls on left and right edges
    lda #%11110000   ; PF0: all 4 bits set = left wall
    sta PF0
    lda #%00000000   ; PF1: empty
    sta PF1
    lda #%00000001   ; PF2: D0 set = rightmost pixel of left half
    sta PF2
```

## 3. CTRLPF Register

The `CTRLPF` register (`$0A`) controls playfield behaviour and ball size:

```
D7  D6  D5    D4    D3  D2      D1     D0
--  --  BSIZE1 BSIZE0 --  PRIORITY SCORE  REFLECT
```

| Bit(s) | Name | Function |
|--------|------|----------|
| D0 | REFLECT | 0 = right half duplicates left; 1 = right half mirrors left |
| D1 | SCORE | 0 = PF uses COLUPF; 1 = left PF uses COLUP0, right PF uses COLUP1 |
| D2 | PRIORITY | 0 = players draw over PF; 1 = PF draws over players |
| D5-D4 | BSIZE | Ball width: 00=1, 01=2, 10=4, 11=8 colour clocks |

### Reflected vs Repeated Playfield

- **Repeated** (D0=0): Right half = PF0-PF1-PF2 (same order as left). Useful for horizontally scrolling backgrounds.
- **Reflected** (D0=1): Right half = PF2-PF1-PF0 (mirror of left). Useful for symmetric mazes and borders. The reflected mode reverses the order of the registers AND the scan direction within each register for the right half.

### Score Mode

When SCORE (D1) is set, the playfield's left half uses the colour from `COLUP0` and the right half uses `COLUP1`. This allows a two-colour scoreboard. The ball still uses `COLUPF`.

## 4. Playfield Timing

The playfield is drawn continuously by the TIA as the beam sweeps across the scanline. The CPU can update PF0/PF1/PF2 mid-scanline to display different patterns on the left and right halves (asymmetric playfield).

### Latest Write Cycles (Compact Reference)

The following table shows the **latest CPU cycle** at which you can write to a playfield register and have the new value fully displayed. Cycle numbers are measured from the start of the scanline (cycle 0 = start of HBLANK).

**Repeated Playfield** (REFLECT=0):

| Register | Left Copy (Latest) | Right Copy (Latest) |
|----------|-------------------|---------------------|
| PF0 | Cycle 22 | Cycle 48 |
| PF1 | Cycle 27 | Cycle 54 |
| PF2 | Cycle 38 | Cycle 64 |

**Reflected Playfield** (REFLECT=1):

| Register | Left Copy (Latest) | Right Copy |
|----------|-------------------|------------|
| PF0 | Cycle 22 | R.PF0 latest = Cycle 70 |
| PF1 | Cycle 27 | R.PF1 latest = Cycle 59 |
| PF2 | Cycle 38 | R.PF2 latest = Cycle 48 |

Note: For reflected playfields, the right-half register order is reversed: PF2 is drawn first on the right, then PF1, then PF0.

### Asymmetric Playfield Write Windows

For asymmetric playfields, you write PF registers once for the left half and again for the right half. Here are the earliest and latest cycles for each copy:

**Repeated graphics** (PF0-PF1-PF2-PF0-PF1-PF2):

| Register | Earliest Write | Latest Write |
|----------|---------------|-------------|
| Left PF0 | Cycle 53 (prev line) | Cycle 21 |
| Left PF1 | Cycle 64 (prev line) | Cycle 27 |
| Left PF2 | Cycle 75 (prev line) | Cycle 37 |
| Right PF0 | Cycle 27 | Cycle 48 |
| Right PF1 | Cycle 37 | Cycle 53 |
| Right PF2 | Cycle 48 | Cycle 64 |

**Reflected graphics** (PF0-PF1-PF2-PF2-PF1-PF0):

| Register | Earliest Write | Latest Write |
|----------|---------------|-------------|
| Left PF0 | Cycle 75 (prev line) | Cycle 21 |
| Left PF1 | Cycle 69 (prev line) | Cycle 27 |
| Left PF2 | Cycle 59 (prev line) | Cycle 37 |
| Right PF2 | Cycle 48 | Cycle 48 |
| Right PF1 | Cycle 37 | Cycle 59 |
| Right PF0 | Cycle 27 | Cycle 69 |

**Critical**: For a reflected asymmetric playfield, the right copy of PF2 *must* be written at exactly cycle 48 — there is zero leeway.

### Asymmetric Playfield Example

```asm
; Asymmetric playfield kernel (reflected mode)
; Left and right halves show different patterns
    sta WSYNC
    ; -- Write left-half PF data (before cycle 22/27/38) --
    lda LeftPF0Data
    sta PF0              ; 3 cycles
    lda LeftPF1Data
    sta PF1              ; 3 cycles
    lda LeftPF2Data
    sta PF2              ; 3 cycles
    ; -- Wait for beam to pass left half --
    SLEEP 20             ; burn cycles until right-half window
    ; -- Write right-half PF data --
    lda RightPF0Data
    sta PF0
    lda RightPF1Data
    sta PF1
    lda RightPF2Data
    sta PF2
```

Timing varies with positioning; always count cycles from `sta WSYNC`. See [02_Frame_Structure_and_Timing.md] for cycle-counting fundamentals.

## 5. Object Priority

The TIA composites objects in a specific priority order. When multiple objects overlap at the same pixel, the higher-priority object's colour is displayed.

### Default Priority (PRIORITY=0)

| Priority | Object(s) |
|----------|-----------|
| Highest | P0, M0 |
| | P1, M1 |
| | PF, BL |
| Lowest | BK (background) |

Players always draw over the playfield.

### Playfield Priority (PRIORITY=1, CTRLPF D2 set)

| Priority | Object(s) |
|----------|-----------|
| Highest | PF, BL |
| | P0, M0 |
| | P1, M1 |
| Lowest | BK (background) |

The playfield draws over players, useful for foreground scenery or platforms.

### Colour When Objects Overlap

When P0 and P1 overlap, the displayed colour is determined by priority (P0 wins by default). When a player and its missile overlap, they share the same colour so no difference is visible. The `SCORE` mode in CTRLPF affects only the playfield colour source — it does not change priority.

See [01_Architecture_and_Memory_Map.md] for the complete register reference and memory map.
