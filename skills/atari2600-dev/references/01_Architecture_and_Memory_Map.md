# Architecture and Memory Map

## 1. Architecture Overview

The Atari Video Computer System (VCS/2600) contains three ICs and a cartridge port:

### MOS 6507 CPU

A cost-reduced 6502 with only 13 address lines (8 KB addressable space) and no IRQ/NMI pins. It executes the full 6502 instruction set. Clock speed is derived from the TIA oscillator divided by 3.

| Parameter | NTSC | PAL |
|---|---|---|
| TIA clock | 3.579545 MHz | 3.546894 MHz |
| CPU clock | 1.193182 MHz | 1.182298 MHz |
| Scanlines per frame | 262 | 312 |
| Frame rate | ~60 Hz | ~50 Hz |
| Color clocks per scanline | 228 | 228 |
| CPU cycles per scanline | 76 | 76 |
| Visible pixels per scanline | 160 | 160 |
| HBLANK clocks per scanline | 68 | 68 |

**Registers:** 8-bit accumulator (A), two 8-bit index registers (X, Y), 16-bit program counter (PC), 8-bit stack pointer (SP, points into $0100-$01FF), 8-bit processor status (P) with carry, zero, interrupt disable, decimal, break, overflow, and negative flags.

### TIA (Television Interface Adaptor)

Custom IC that generates video and audio. Contains:

- Horizontal sync counter (228 color clocks per line, automatic)
- Two 8-bit player graphics registers (P0, P1)
- Two 1-bit missile graphics (M0, M1)
- One 1-bit ball graphic (BL)
- 20-bit playfield register (PF0 + PF1 + PF2)
- Four color-luminance registers
- 15 collision detection latches
- Two independent audio channels
- Six input ports (four dumped, two latched)

The TIA has no frame buffer. The CPU must update TIA registers in real time as each scanline is drawn ("racing the beam"). All TIA write registers are latched -- values persist until overwritten.

### RIOT (6532 RAM-I/O-Timer)

Off-the-shelf MOS 6532 providing:

- 128 bytes of RAM ($0080-$00FF)
- Two 8-bit I/O ports (Port A for controllers, Port B for console switches)
- Programmable interval timer (1, 8, 64, or 1024 cycle intervals)

### Cartridge

Plugs into the upper 4 KB of address space ($1000-$1FFF). Standard games are 2 KB or 4 KB. Larger ROMs use bank-switching hardware on the cartridge PCB to swap 4 KB windows into this range.

---

## 2. VCS Memory Map

The 6507's 13-bit address bus addresses $0000-$1FFF. The full 16-bit space ($0000-$FFFF) mirrors this 8 KB block repeatedly. Address decoding uses only a few chip-select lines, producing extensive mirroring.

### Primary Address Ranges

| Address Range | Device | Function |
|---|---|---|
| $0000-$002C | TIA | Write registers (45 registers, $00-$2C) |
| $0000-$000D | TIA | Read registers (14 registers, $00-$0D) |
| $0030-$003F | TIA | Write-only mirror of $00-$0F |
| $0040-$007F | TIA | Mirror of $00-$3F |
| $0080-$00FF | RIOT | 128 bytes RAM (zero page) |
| $0100-$017F | TIA | Mirror of $00-$7F |
| $0180-$01FF | RIOT | Mirror of RAM (used as hardware stack) |
| $0200-$027F | TIA | Mirror of $00-$7F |
| $0280-$0297 | RIOT | I/O ports and timer registers |
| $0298-$02FF | RIOT | Mirrors of $0280-$0297 |
| $0300-$03FF | TIA/RIOT | Mixed mirrors |
| $1000-$1FFF | Cartridge | ROM (4 KB window) |

### Mirror Pattern Summary

**TIA ($00-$3F):** Appears at every $40-aligned block where bit 12 = 0 and bits 7+8 are not both set to the RIOT RAM pattern. Template: addresses matching $xy_z0 where x = even, z = {0, 4}.

**RIOT RAM ($80-$FF):** 128 bytes mirrored at $0080, $0180, $0480, $0580, $0880, $0980, etc. Template: $xy80 where x = even, y = {0,1,4,5,8,9,$C,$D}.

**RIOT Registers ($0280-$029F):** Mirrored at $02A0-$02FF, $0680-$06FF, $0A80-$0AFF, $0E80-$0EFF, etc. Template: $xyz0 where x = even, y = {2,3,6,7,$A,$B,$E,$F}, z = {8,$A,$C,$E}.

**ROM ($1000-$1FFF):** Mirrored at every odd $x000 block: $3000, $5000, $7000, $9000, $B000, $D000, $F000.

---

## 3. TIA Write Register Reference ($00-$2C)

Registers with no active bits are strobes -- they trigger their function on any write (data ignored). Unused bit positions are ignored by hardware.

| Addr | Name | D7 | D6 | D5 | D4 | D3 | D2 | D1 | D0 | Function |
|---|---|---|---|---|---|---|---|---|---|---|
| $00 | VSYNC | - | - | - | - | - | - | D1 | - | Vertical sync set-clear |
| $01 | VBLANK | D7 | D6 | - | - | - | - | D1 | - | Vertical blank set-clear |
| $02 | WSYNC | strobe | | | | | | | | Wait for leading edge of HBLANK |
| $03 | RSYNC | strobe | | | | | | | | Reset horizontal sync counter |
| $04 | NUSIZ0 | - | - | D5 | D4 | - | D2 | D1 | D0 | Number-size player-missile 0 |
| $05 | NUSIZ1 | - | - | D5 | D4 | - | D2 | D1 | D0 | Number-size player-missile 1 |
| $06 | COLUP0 | D7 | D6 | D5 | D4 | D3 | D2 | D1 | - | Color-luminance player 0 |
| $07 | COLUP1 | D7 | D6 | D5 | D4 | D3 | D2 | D1 | - | Color-luminance player 1 |
| $08 | COLUPF | D7 | D6 | D5 | D4 | D3 | D2 | D1 | - | Color-luminance playfield |
| $09 | COLUBK | D7 | D6 | D5 | D4 | D3 | D2 | D1 | - | Color-luminance background |
| $0A | CTRLPF | - | - | D5 | D4 | - | D2 | D1 | D0 | Control playfield/ball |
| $0B | REFP0 | - | - | - | - | D3 | - | - | - | Reflect player 0 |
| $0C | REFP1 | - | - | - | - | D3 | - | - | - | Reflect player 1 |
| $0D | PF0 | D7 | D6 | D5 | D4 | - | - | - | - | Playfield register byte 0 |
| $0E | PF1 | D7 | D6 | D5 | D4 | D3 | D2 | D1 | D0 | Playfield register byte 1 |
| $0F | PF2 | D7 | D6 | D5 | D4 | D3 | D2 | D1 | D0 | Playfield register byte 2 |
| $10 | RESP0 | strobe | | | | | | | | Reset player 0 position |
| $11 | RESP1 | strobe | | | | | | | | Reset player 1 position |
| $12 | RESM0 | strobe | | | | | | | | Reset missile 0 position |
| $13 | RESM1 | strobe | | | | | | | | Reset missile 1 position |
| $14 | RESBL | strobe | | | | | | | | Reset ball position |
| $15 | AUDC0 | - | - | - | - | D3 | D2 | D1 | D0 | Audio control 0 |
| $16 | AUDC1 | - | - | - | - | D3 | D2 | D1 | D0 | Audio control 1 |
| $17 | AUDF0 | - | - | - | D4 | D3 | D2 | D1 | D0 | Audio frequency 0 |
| $18 | AUDF1 | - | - | - | D4 | D3 | D2 | D1 | D0 | Audio frequency 1 |
| $19 | AUDV0 | - | - | - | - | D3 | D2 | D1 | D0 | Audio volume 0 |
| $1A | AUDV1 | - | - | - | - | D3 | D2 | D1 | D0 | Audio volume 1 |
| $1B | GRP0 | D7 | D6 | D5 | D4 | D3 | D2 | D1 | D0 | Graphics player 0 |
| $1C | GRP1 | D7 | D6 | D5 | D4 | D3 | D2 | D1 | D0 | Graphics player 1 |
| $1D | ENAM0 | - | - | - | - | - | - | D1 | - | Graphics (enable) missile 0 |
| $1E | ENAM1 | - | - | - | - | - | - | D1 | - | Graphics (enable) missile 1 |
| $1F | ENABL | - | - | - | - | - | - | D1 | - | Graphics (enable) ball |
| $20 | HMP0 | D7 | D6 | D5 | D4 | - | - | - | - | Horizontal motion player 0 |
| $21 | HMP1 | D7 | D6 | D5 | D4 | - | - | - | - | Horizontal motion player 1 |
| $22 | HMM0 | D7 | D6 | D5 | D4 | - | - | - | - | Horizontal motion missile 0 |
| $23 | HMM1 | D7 | D6 | D5 | D4 | - | - | - | - | Horizontal motion missile 1 |
| $24 | HMBL | D7 | D6 | D5 | D4 | - | - | - | - | Horizontal motion ball |
| $25 | VDELP0 | - | - | - | - | - | - | - | D0 | Vertical delay player 0 |
| $26 | VDELP1 | - | - | - | - | - | - | - | D0 | Vertical delay player 1 |
| $27 | VDELBL | - | - | - | - | - | - | - | D0 | Vertical delay ball |
| $28 | RESMP0 | - | - | - | - | - | - | D1 | - | Reset missile 0 to player 0 |
| $29 | RESMP1 | - | - | - | - | - | - | D1 | - | Reset missile 1 to player 1 |
| $2A | HMOVE | strobe | | | | | | | | Apply horizontal motion |
| $2B | HMCLR | strobe | | | | | | | | Clear horizontal motion registers |
| $2C | CXCLR | strobe | | | | | | | | Clear collision latches |

### Write Register Bit Field Details

**VSYNC ($00):** D1: 1 = start vertical sync, 0 = stop vertical sync.

**VBLANK ($01):** D1: 1 = enable vertical blank, 0 = disable vertical blank. D6: 1 = enable INPT4/INPT5 latches, 0 = disable (and reset) latches. D7: 1 = dump INPT0-INPT3 ports to ground, 0 = remove ground path.

**NUSIZ0/NUSIZ1 ($04/$05):**

Missile size (D5-D4):

| D5 | D4 | Missile Width |
|---|---|---|
| 0 | 0 | 1 clock |
| 0 | 1 | 2 clocks |
| 1 | 0 | 4 clocks |
| 1 | 1 | 8 clocks |

Player-missile number and player size (D2-D0):

| D2 | D1 | D0 | Description |
|---|---|---|---|
| 0 | 0 | 0 | One copy |
| 0 | 0 | 1 | Two copies - close (16 clocks apart) |
| 0 | 1 | 0 | Two copies - medium (32 clocks apart) |
| 0 | 1 | 1 | Three copies - close (16 clocks apart) |
| 1 | 0 | 0 | Two copies - wide (64 clocks apart) |
| 1 | 0 | 1 | Double size player |
| 1 | 1 | 0 | Three copies - medium (32 clocks apart) |
| 1 | 1 | 1 | Quad size player |

**COLUPx/COLUPF/COLUBK ($06-$09):** D7-D4 = color (4 bits, 16 colors), D3-D1 = luminance (3 bits, 8 levels). D0 is unused. Color-luminance pairing: P0+M0 share COLUP0, P1+M1 share COLUP1, PF+BL share COLUPF, BK uses COLUBK.

**CTRLPF ($0A):** D0 = REF (1 = reflect playfield). D1 = SCORE (1 = left PF uses COLUP0, right PF uses COLUP1). D2 = PFP (1 = playfield priority over players). D5-D4 = ball size (same encoding as missile size above).

**REFP0/REFP1 ($0B/$0C):** D3: 0 = normal (D7 first), 1 = reflect (D0 first).

**PF0 ($0D):** Only D7-D4 are used. Scanned in order D4, D5, D6, D7 (reversed bit order). Controls leftmost 4 playfield pixels.

**PF1 ($0E):** All 8 bits used. Scanned D7, D6, D5, D4, D3, D2, D1, D0 (normal order). Controls next 8 playfield pixels.

**PF2 ($0F):** All 8 bits used. Scanned D0, D1, D2, D3, D4, D5, D6, D7 (reversed bit order). Controls rightmost 8 playfield pixels of left half.

The right half is either a duplicate (REF=0) or mirror reflection (REF=1) of the left half. Each playfield bit spans 4 color clocks. See [04_Graphics_and_Playfield.md] for playfield timing details.

**RESPx/RESMx/RESBL ($10-$14):** Strobe registers. Writing any value resets the object's horizontal position counter to the current beam position. The object appears 5 clocks later (players) or 4 clocks later (missiles/ball). Resets during HBLANK position objects at the left screen edge (clock 3 for players, clock 2 for missiles/ball). See [05_Sprites_Positioning_and_Motion.md] for positioning techniques.

**HMPx/HMMx/HMBL ($20-$24):** D7-D4 contain a signed 4-bit motion value. Applied when HMOVE is strobed.

| D7 | D6 | D5 | D4 | Motion (normal HMOVE) |
|---|---|---|---|---|
| 1 | 0 | 0 | 0 | +8 right |
| 0 | 0 | 0 | 0 | No motion |
| 0 | 1 | 1 | 1 | -7 left |

Range: +8 (right) to -7 (left) with normal HMOVE timing. Do not modify motion registers for 24 CPU cycles after HMOVE.

**VDELP0/VDELP1 ($25/$26):** D0: 0 = use normal GRPx register, 1 = use shadow register (delayed until other player's GRPx is written). **VDELBL ($27):** D0: 0 = no delay, 1 = delay ball display until GRP1 is written.

**RESMP0/RESMP1 ($28/$29):** D1: 1 = lock missile to center of its player (disables missile graphics), 0 = release missile.

**HMOVE ($2A):** Must be strobed during HBLANK, typically immediately after WSYNC. Produces an 8-pixel-wide "HMOVE bar" artifact on the left edge of the line. Early HMOVE (cycle 73-74 of previous line) avoids the bar but limits motion range to left-only (0 to -15).

**GRP0/GRP1 ($1B/$1C):** Writing GRP0 also copies the current GRP1 value into GRP1's shadow register. Writing GRP1 copies GRP0 into GRP0's shadow register. This cross-copy mechanism enables the vertical delay feature. Serial output begins with D7 (unless reflected).

**ENAM0/ENAM1/ENABL ($1D-$1F):** D1: 1 = enable object, 0 = disable.

---

## 4. TIA Read Register Reference ($00-$0D)

On reads, the TIA drives only D7 and D6. Bits D5-D0 are undefined and must not be relied upon.

| Addr | Name | D7 | D6 | Function |
|---|---|---|---|---|
| $00 | CXM0P | M0-P1 | M0-P0 | Missile 0 / Player collisions |
| $01 | CXM1P | M1-P0 | M1-P1 | Missile 1 / Player collisions |
| $02 | CXP0FB | P0-PF | P0-BL | Player 0 / Playfield-Ball collisions |
| $03 | CXP1FB | P1-PF | P1-BL | Player 1 / Playfield-Ball collisions |
| $04 | CXM0FB | M0-PF | M0-BL | Missile 0 / Playfield-Ball collisions |
| $05 | CXM1FB | M1-PF | M1-BL | Missile 1 / Playfield-Ball collisions |
| $06 | CXBLPF | BL-PF | (unused) | Ball / Playfield collision |
| $07 | CXPPMM | P0-P1 | M0-M1 | Player-Player / Missile-Missile collisions |
| $08 | INPT0 | D7 | (0) | Paddle 0 input port (dumped) |
| $09 | INPT1 | D7 | (0) | Paddle 1 input port (dumped) |
| $0A | INPT2 | D7 | (0) | Paddle 2 input port (dumped) |
| $0B | INPT3 | D7 | (0) | Paddle 3 input port (dumped) |
| $0C | INPT4 | D7 | (0) | Player 0 fire button (latched) |
| $0D | INPT5 | D7 | (0) | Player 1 fire button (latched) |

A 1 in a collision bit means that collision has occurred. Collision latches are set any time two objects overlap during beam scan. All 15 collision bits are cleared simultaneously by writing to CXCLR ($2C). Reads to $0E and $0F return 0 in D7-D6.

INPT0-INPT3 (dumped ports): Used for paddle controllers. Write D7=1 to VBLANK to ground these ports (discharge capacitors), then write D7=0 and measure time until D7 reads 1 at each port.

INPT4-INPT5 (latched ports): Joystick fire buttons. D7 = 1 when button is not pressed, D7 = 0 when pressed. Latching is controlled by D6 of VBLANK.

See [06_Input_and_Collision.md] for collision handling patterns and controller reading.

---

## 5. RIOT Register Reference

### I/O Port Registers

| Addr | Name | R/W | Function |
|---|---|---|---|
| $0280 | SWCHA | R/W | Port A data: joystick directions / controller I/O |
| $0281 | SWACNT | W | Port A data direction register (0 = input, 1 = output) |
| $0282 | SWCHB | R | Port B data: console switches (active-low) |
| $0283 | SWBCNT | W | Port B DDR (hardwired as input; normally $00) |

**SWCHA ($0280) -- Joystick directions:**

| Bit | Direction | Player |
|---|---|---|
| D7 | Right | P0 (left player) |
| D6 | Left | P0 |
| D5 | Down | P0 |
| D4 | Up | P0 |
| D3 | Right | P1 (right player) |
| D2 | Left | P1 |
| D1 | Down | P1 |
| D0 | Up | P1 |

A 0 in a bit means that direction is active (switch closed). All 1s = joystick centered.

**SWCHB ($0282) -- Console switches:**

| Bit | Switch | Meaning |
|---|---|---|
| D7 | P1 Difficulty | 0 = amateur (B), 1 = pro (A) |
| D6 | P0 Difficulty | 0 = amateur (B), 1 = pro (A) |
| D5 | (not used) | |
| D4 | (not used) | |
| D3 | Color/B&W | 0 = B/W, 1 = Color |
| D2 | (not used) | |
| D1 | Game Select | 0 = switch pressed |
| D0 | Game Reset | 0 = switch pressed |

### Timer Registers

| Addr | Name | R/W | Function |
|---|---|---|---|
| $0284 | INTIM | R | Current timer value (read only) |
| $0285 | INSTAT | R | Timer interrupt status (D7 = underflow flag) |
| $0294 | TIM1T | W | Set timer: 1 clock per interval (838 ns) |
| $0295 | TIM8T | W | Set timer: 8 clocks per interval (6.7 us) |
| $0296 | TIM64T | W | Set timer: 64 clocks per interval (53.6 us) |
| $0297 | T1024T | W | Set timer: 1024 clocks per interval (858.2 us) |

Writing a value (1-255) to a timer set register starts a countdown. The value in INTIM decrements by 1 at each interval. When it reaches 0, it holds 0 for one interval, then rolls over to $FF and decrements once per clock cycle (not per interval). This allows the programmer to determine how long ago the timer expired.

See [08_Game_Logic_and_Timers.md] for timer usage patterns.

### RAM

128 bytes at $0080-$00FF. Mirrored at $0180-$01FF (page 1, used for the hardware stack). The stack pointer initializes to $FF and grows downward through page 1. Variables are conventionally allocated from $80 upward.

---

## 6. NTSC vs PAL Timing

| Parameter | NTSC | PAL |
|---|---|---|
| Frame lines | 262 | 312 |
| VSYNC lines | 3 | 3 |
| VBLANK lines | 37 | 48 |
| Visible (kernel) lines | 192 | 228 |
| Overscan lines | 30 | 36 |
| Frame rate | ~60 Hz | ~50 Hz |
| Frame time (us) | 16,686 | 20,055 |
| VBLANK time (us) | 2,548 | 3,085 |
| Kernel time (us) | 12,228 | 14,656 |
| Overscan time (us) | 1,910 | 2,314 |
| TIA clock (Hz) | 3,579,545 | 3,546,894 |
| CPU clock (Hz) | 1,193,182 | 1,182,298 |

PAL games run approximately 17% slower when game speed is tied to frame rate. PAL uses a different color encoding with more pastel hues and different color-to-value mappings. Audio frequencies drop slightly due to the slower clock.

SECAM consoles run PAL software but the color/B&W switch is hardwired to B/W. SECAM maps luminance values to fixed colors: lum 0 = black, 2 = blue, 4 = red, 6 = magenta, 8 = green, $A = cyan, $C = yellow, $E = white.

See [02_Frame_Structure_and_Timing.md] for frame timing details.

---

## 7. Cartridge Addressing and Bank-Switching

### Non-Bankswitched Cartridges

**2 KB:** ROM occupies $1800-$1FFF (mirrored at $1000-$17FF). The reset vector at $1FFC-$1FFD must point into the ROM range.

**4 KB:** ROM fills $1000-$1FFF with no switching needed.

### Common Bank-Switching Schemes

Bank switching works by placing hardware on the cartridge PCB that monitors the address bus. When the CPU accesses a specific "hotspot" address, the cartridge hardware swaps which ROM bank is visible in the $1000-$1FFF window.

| Scheme | ROM Size | Banks | Hotspot Addresses | Extra RAM |
|---|---|---|---|---|
| F8 | 8 KB | 2 x 4 KB | $1FF8 = bank 0, $1FF9 = bank 1 | None |
| F6 | 16 KB | 4 x 4 KB | $1FF6 = bank 0, $1FF7 = bank 1, $1FF8 = bank 2, $1FF9 = bank 3 | None |
| F4 | 32 KB | 8 x 4 KB | $1FF4-$1FFB = banks 0-7 | None |
| F8SC | 8 KB | 2 x 4 KB | Same as F8 | 128 bytes |
| F6SC | 16 KB | 4 x 4 KB | Same as F6 | 128 bytes |
| F4SC | 32 KB | 8 x 4 KB | Same as F4 | 128 bytes |

**SC (SuperChip) RAM:** Schemes with the SC suffix add 128 bytes of cartridge RAM. The first 128 bytes of the bank ($1000-$107F) are the write port; the next 128 bytes ($1080-$10FF) are the read port. You must write through the write addresses and read through the read addresses -- accessing the wrong port corrupts data.

**Hotspot access:** A bank switch is triggered by any access (read or write) to the hotspot address. This means even instruction fetches from a hotspot address will trigger a switch. Each bank must contain valid reset and interrupt vectors at $1FFC-$1FFF, or the startup bank must be arranged so the vectors are accessible.

See [09_Advanced_Techniques.md] for bank-switching implementation patterns.

---

## 8. Zero Page Usage Conventions

Zero page ($00-$FF) is divided between TIA registers and RIOT RAM:

| Range | Usage |
|---|---|
| $00-$2C | TIA write registers |
| $00-$0D | TIA read registers (same addresses, read vs write) |
| $2D-$3F | TIA (unused/mirrors -- can be written but no effect) |
| $40-$7F | TIA mirrors of $00-$3F |
| $80-$FF | RIOT RAM (128 bytes, the only general-purpose storage) |

### Conventions for the 128 bytes of RAM ($80-$FF)

- **$80-$9F (approx):** Kernel variables that need fast zero-page access during the display loop. Place frequently-written values here to save cycles.
- **$A0-$DF (approx):** Game state variables (positions, velocities, scores, flags).
- **$E0-$FF (approx):** Reserved for stack usage. The hardware stack at $01FF-$0180 (page 1 mirror of $FF-$80) grows downward from $FF. Deep call nesting or heavy PHA/PLA usage consumes these bytes.

Instructions addressing zero page ($00-$FF) use 2-byte, 3-cycle forms instead of 3-byte, 4-cycle absolute addressing. This saves 1 byte and 1 cycle per access, which is critical in tight kernel loops.

Variables can be reused across different frame phases (VBLANK, kernel, overscan) as long as their lifetimes do not overlap. This is a common technique for stretching the 128 bytes of available RAM.

See [02_Frame_Structure_and_Timing.md] for how frame phases relate to variable lifetimes.

---

## NTSC Color Table

| Value | NTSC Color | PAL Color |
|---|---|---|
| $0x | Grey | Grey |
| $1x | Gold | Grey |
| $2x | Orange | Gold |
| $3x | Red-Orange | Green |
| $4x | Pink | Orange |
| $5x | Purple | Green |
| $6x | Purple-Blue | Red |
| $7x | Blue | Light Green |
| $8x | Blue | Purple |
| $9x | Light Blue | Turquoise |
| $Ax | Turquoise | Purple-Blue |
| $Bx | Green-Blue | Light Blue |
| $Cx | Green | Blue-Purple |
| $Dx | Yellow-Green | Blue |
| $Ex | Orange-Green | Grey |
| $Fx | Light Orange | Grey |

The low nibble (x) sets luminance: $0 = darkest, $E = lightest. Only even values are significant for luminance (D0 is ignored). Each color value represents a combination: D7-D4 select one of 16 hues, D3-D1 select one of 8 luminance levels.

---

## Object Priority

Default priority (highest to lowest):

| Priority | Objects |
|---|---|
| 1 (highest) | P0, M0 |
| 2 | P1, M1 |
| 3 | PF, BL |
| 4 (lowest) | BK |

When CTRLPF D2 (PFP) = 1, playfield gets highest priority:

| Priority | Objects |
|---|---|
| 1 (highest) | PF, BL |
| 2 | P0, M0 |
| 3 | P1, M1 |
| 4 (lowest) | BK |

When CTRLPF D1 (SCORE) = 1, the left half of the playfield uses COLUP0 and the right half uses COLUP1.
