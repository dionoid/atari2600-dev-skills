# Reference and Cheat Sheets

Quick-reference tables for TIA registers, RIOT registers, 6502 instructions, colour values, timing budgets, and common macros.

## 1. TIA Write Registers

| Addr | Name | Active Bits | Function |
|------|------|-------------|----------|
| `$00` | VSYNC | D1 | Vertical sync (set D1=1 for 3 scanlines) |
| `$01` | VBLANK | D7,D6,D1 | D7=dump ports, D6=latch inputs, D1=blank |
| `$02` | WSYNC | strobe | Halt CPU until end of scanline |
| `$03` | RSYNC | strobe | Reset horizontal sync counter |
| `$04` | NUSIZ0 | D5-D4,D2-D0 | P0/M0 size and copies |
| `$05` | NUSIZ1 | D5-D4,D2-D0 | P1/M1 size and copies |
| `$06` | COLUP0 | D7-D1 | Colour for P0 and M0 |
| `$07` | COLUP1 | D7-D1 | Colour for P1 and M1 |
| `$08` | COLUPF | D7-D1 | Colour for playfield and ball |
| `$09` | COLUBK | D7-D1 | Background colour |
| `$0A` | CTRLPF | D5-D4,D2-D0 | PF reflect, score mode, priority, ball size |
| `$0B` | REFP0 | D3 | Reflect P0 |
| `$0C` | REFP1 | D3 | Reflect P1 |
| `$0D` | PF0 | D7-D4 | Playfield bits (scanned D4-D7) |
| `$0E` | PF1 | D7-D0 | Playfield bits (scanned D7-D0) |
| `$0F` | PF2 | D7-D0 | Playfield bits (scanned D0-D7) |
| `$10` | RESP0 | strobe | Reset P0 horizontal position |
| `$11` | RESP1 | strobe | Reset P1 horizontal position |
| `$12` | RESM0 | strobe | Reset M0 horizontal position |
| `$13` | RESM1 | strobe | Reset M1 horizontal position |
| `$14` | RESBL | strobe | Reset Ball horizontal position |
| `$15` | AUDC0 | D3-D0 | Audio channel 0 distortion |
| `$16` | AUDC1 | D3-D0 | Audio channel 1 distortion |
| `$17` | AUDF0 | D4-D0 | Audio channel 0 frequency (0-31) |
| `$18` | AUDF1 | D4-D0 | Audio channel 1 frequency (0-31) |
| `$19` | AUDV0 | D3-D0 | Audio channel 0 volume (0-15) |
| `$1A` | AUDV1 | D3-D0 | Audio channel 1 volume (0-15) |
| `$1B` | GRP0 | D7-D0 | Player 0 graphics |
| `$1C` | GRP1 | D7-D0 | Player 1 graphics |
| `$1D` | ENAM0 | D1 | Enable missile 0 |
| `$1E` | ENAM1 | D1 | Enable missile 1 |
| `$1F` | ENABL | D1 | Enable ball |
| `$20` | HMP0 | D7-D4 | P0 horizontal motion (-8 to +7) |
| `$21` | HMP1 | D7-D4 | P1 horizontal motion |
| `$22` | HMM0 | D7-D4 | M0 horizontal motion |
| `$23` | HMM1 | D7-D4 | M1 horizontal motion |
| `$24` | HMBL | D7-D4 | Ball horizontal motion |
| `$25` | VDELP0 | D0 | Vertical delay P0 |
| `$26` | VDELP1 | D0 | Vertical delay P1 |
| `$27` | VDELBL | D0 | Vertical delay ball |
| `$28` | RESMP0 | D1 | Lock M0 to P0 centre |
| `$29` | RESMP1 | D1 | Lock M1 to P1 centre |
| `$2A` | HMOVE | strobe | Apply horizontal motion |
| `$2B` | HMCLR | strobe | Clear all HMxx registers |
| `$2C` | CXCLR | strobe | Clear all collision latches |

## 2. TIA Read Registers

| Addr | Name | D7 | D6 |
|------|------|----|----|
| `$00` | CXM0P | M0-P1 | M0-P0 |
| `$01` | CXM1P | M1-P0 | M1-P1 |
| `$02` | CXP0FB | P0-PF | P0-BL |
| `$03` | CXP1FB | P1-PF | P1-BL |
| `$04` | CXM0FB | M0-PF | M0-BL |
| `$05` | CXM1FB | M1-PF | M1-BL |
| `$06` | CXBLPF | BL-PF | (0) |
| `$07` | CXPPMM | P0-P1 | M0-M1 |
| `$08` | INPT0 | Paddle 0 | — |
| `$09` | INPT1 | Paddle 1 | — |
| `$0A` | INPT2 | Paddle 2 | — |
| `$0B` | INPT3 | Paddle 3 | — |
| `$0C` | INPT4 | P0 fire | — |
| `$0D` | INPT5 | P1 fire | — |

D5-D0 are indeterminate on all TIA read registers.

## 3. RIOT Registers

| Addr | Name | R/W | Function |
|------|------|-----|----------|
| `$0280` | SWCHA | R/W | Port A: joystick directions |
| `$0281` | SWACNT | R/W | Port A data direction |
| `$0282` | SWCHB | R | Port B: console switches |
| `$0283` | SWBCNT | R/W | Port B data direction |
| `$0284` | INTIM | R | Timer current value |
| `$0285` | INSTAT | R | Timer status (D7=underflow) |
| `$0294` | TIM1T | W | Set timer: 1 cycle/tick |
| `$0295` | TIM8T | W | Set timer: 8 cycles/tick |
| `$0296` | TIM64T | W | Set timer: 64 cycles/tick |
| `$0297` | T1024T | W | Set timer: 1024 cycles/tick |

## 4. Memory Map

| Range | Size | Contents |
|-------|------|----------|
| `$00`-`$2C` | 45 bytes | TIA registers (write) |
| `$00`-`$0D` | 14 bytes | TIA registers (read) |
| `$80`-`$FF` | 128 bytes | RAM (zero page) |
| `$0280`-`$0297` | 24 bytes | RIOT registers |
| `$F000`-`$FFFF` | 4096 bytes | ROM (4K cartridge) |
| `$F800`-`$FFFF` | 2048 bytes | ROM (2K cartridge) |
| `$FFFC`-`$FFFD` | 2 bytes | Reset vector |
| `$FFFE`-`$FFFF` | 2 bytes | IRQ/BRK vector |

## 5. Scanline Budget

### NTSC (262 scanlines, 60 Hz)

| Section | Lines | Cycles | Purpose |
|---------|-------|--------|---------|
| VSYNC | 3 | 228 | Signal vertical sync |
| VBLANK | 37 | 2,812 | Game logic, input |
| Kernel | 192 | 14,592 | Drawing ONLY |
| Overscan | 30 | 2,280 | Sound, AI, misc logic |
| **Total** | **262** | **19,912** | |

### PAL (312 scanlines, 50 Hz)

| Section | Lines | Cycles |
|---------|-------|--------|
| VSYNC | 3 | 228 |
| VBLANK | 45 | 3,420 |
| Kernel | 228 | 17,328 |
| Overscan | 36 | 2,736 |
| **Total** | **312** | **23,712** |

**Per scanline**: 76 CPU cycles = 228 colour clocks. 68 colour clocks = HBLANK, 160 = visible.

## 6. 6502 Instruction Set Summary

### Load / Store

| Mnemonic | Function | Flags | ZP | ABS | Imm |
|----------|----------|-------|----|-----|-----|
| LDA | Load A | N,Z | 3 | 4 | 2 |
| LDX | Load X | N,Z | 3 | 4 | 2 |
| LDY | Load Y | N,Z | 3 | 4 | 2 |
| STA | Store A | — | 3 | 4 | — |
| STX | Store X | — | 3 | 4 | — |
| STY | Store Y | — | 3 | 4 | — |

### Arithmetic

| Mnemonic | Function | Flags | ZP | ABS | Imm |
|----------|----------|-------|----|-----|-----|
| ADC | Add with carry | N,V,Z,C | 3 | 4 | 2 |
| SBC | Subtract with carry | N,V,Z,C | 3 | 4 | 2 |
| INC | Increment memory | N,Z | 5 | 6 | — |
| DEC | Decrement memory | N,Z | 5 | 6 | — |
| INX | Increment X | N,Z | 2 | — | — |
| INY | Increment Y | N,Z | 2 | — | — |
| DEX | Decrement X | N,Z | 2 | — | — |
| DEY | Decrement Y | N,Z | 2 | — | — |

### Logical

| Mnemonic | Function | Flags | ZP | ABS | Imm |
|----------|----------|-------|----|-----|-----|
| AND | Bitwise AND | N,Z | 3 | 4 | 2 |
| ORA | Bitwise OR | N,Z | 3 | 4 | 2 |
| EOR | Bitwise XOR | N,Z | 3 | 4 | 2 |
| BIT | Test bits | N,V,Z | 3 | 4 | — |

### Shift / Rotate

| Mnemonic | Function | Flags | A | ZP | ABS |
|----------|----------|-------|---|----|----|
| ASL | Shift left | N,Z,C | 2 | 5 | 6 |
| LSR | Shift right | N,Z,C | 2 | 5 | 6 |
| ROL | Rotate left | N,Z,C | 2 | 5 | 6 |
| ROR | Rotate right | N,Z,C | 2 | 5 | 6 |

### Compare

| Mnemonic | Function | Flags | ZP | ABS | Imm |
|----------|----------|-------|----|-----|-----|
| CMP | Compare A | N,Z,C | 3 | 4 | 2 |
| CPX | Compare X | N,Z,C | 3 | 4 | 2 |
| CPY | Compare Y | N,Z,C | 3 | 4 | 2 |

### Branch (all: 2 cycles not taken, 3 taken, +1 page cross)

| Mnemonic | Condition |
|----------|-----------|
| BEQ | Z=1 (equal) |
| BNE | Z=0 (not equal) |
| BCS | C=1 (carry set) |
| BCC | C=0 (carry clear) |
| BMI | N=1 (negative) |
| BPL | N=0 (positive) |
| BVS | V=1 (overflow) |
| BVC | V=0 (no overflow) |

### Jump / Call

| Mnemonic | Function | Cycles |
|----------|----------|--------|
| JMP abs | Jump to address | 3 |
| JMP (ind) | Jump indirect | 5 |
| JSR | Jump to subroutine | 6 |
| RTS | Return from subroutine | 6 |
| RTI | Return from interrupt | 6 |
| BRK | Software interrupt | 7 |

### Stack

| Mnemonic | Function | Cycles |
|----------|----------|--------|
| PHA | Push A | 3 |
| PLA | Pull A | 4 |
| PHP | Push status | 3 |
| PLP | Pull status | 4 |
| TXS | X -> Stack pointer | 2 |
| TSX | Stack pointer -> X | 2 |

### Transfer

| Mnemonic | Function | Cycles |
|----------|----------|--------|
| TAX | A -> X | 2 |
| TAY | A -> Y | 2 |
| TXA | X -> A | 2 |
| TYA | Y -> A | 2 |

### Flag

| Mnemonic | Function | Cycles |
|----------|----------|--------|
| CLC | Clear carry | 2 |
| SEC | Set carry | 2 |
| CLD | Clear decimal | 2 |
| SED | Set decimal | 2 |
| CLI | Clear interrupt | 2 |
| SEI | Set interrupt | 2 |
| CLV | Clear overflow | 2 |
| NOP | No operation | 2 |

## 7. Addressing Modes

| Mode | Syntax | Bytes | Base Cycles | Example |
|------|--------|-------|-------------|---------|
| Immediate | `#val` | 2 | 2 | `LDA #$0F` |
| Zero Page | `zp` | 2 | 3 | `LDA $80` |
| Zero Page,X | `zp,X` | 2 | 4 | `LDA $80,X` |
| Zero Page,Y | `zp,Y` | 2 | 4 | `LDX $80,Y` |
| Absolute | `abs` | 3 | 4 | `LDA $F000` |
| Absolute,X | `abs,X` | 3 | 4+1* | `LDA $F000,X` |
| Absolute,Y | `abs,Y` | 3 | 4+1* | `LDA $F000,Y` |
| Indirect | `(abs)` | 3 | 5 | `JMP ($FFFC)` |
| (Indirect,X) | `(zp,X)` | 2 | 6 | `LDA ($80,X)` |
| (Indirect),Y | `(zp),Y` | 2 | 5+1* | `LDA ($80),Y` |
| Accumulator | `A` | 1 | 2 | `ASL` |
| Implied | — | 1 | 2 | `INX` |
| Relative | `rel` | 2 | 2/3+1* | `BEQ label` |

\* +1 cycle if indexing crosses a page boundary. Store instructions (STA, STX, STY) always take the +1 cycle for indexed modes.

## 8. NTSC Colour Quick Reference

| Hex | Colour | | Hex | Colour |
|-----|--------|-|-----|--------|
| `$0x` | Grey | | `$8x` | Blue |
| `$1x` | Gold | | `$9x` | Cyan |
| `$2x` | Orange | | `$Ax` | Cyan-Green |
| `$3x` | Red-Orange | | `$Bx` | Green |
| `$4x` | Pink/Red | | `$Cx` | Green-Yellow |
| `$5x` | Purple | | `$Dx` | Yellow-Green |
| `$6x` | Blue-Purple | | `$Ex` | Yellow |
| `$7x` | Blue | | `$Fx` | Yellow-Orange |

Replace `x` with luminance: `0`=darkest, `E`=brightest (D0 ignored). Example: `$1E` = bright gold, `$84` = dim blue.

## 9. Common Macro Reference (from macro.h)

| Macro | Function |
|-------|----------|
| `CLEAN_START` | Zero RAM, reset stack, clear TIA, A=X=Y=0 |
| `VERTICAL_SYNC` | Generate 3-scanline VSYNC signal |
| `TIMER_SETUP n` | Load TIM64T for n scanlines |
| `TIMER_WAIT` | Poll INTIM until expired, then WSYNC |
| `SLEEP n` | Burn exactly n CPU cycles (uses NOPs/illegal opcodes) |
| `SET_POINTER ptr, addr` | Load 16-bit address into zero-page pointer |
| `BOUNDARY n` | Pad to n-byte boundary |
| `ALIGN_PAGE` | Align to next 256-byte page |
| `CHECK_PAGE` | Verify no page crossing since last ALIGN_PAGE |

## 10. Illegal Opcodes

| Hex | Name | Function | ZP Cycles |
|-----|------|----------|-----------|
| `$87` | SAX | Store A AND X | 3 |
| `$A7` | LAX | Load A and X | 3 |
| `$C7` | DCP | Decrement, then compare A | 5 |
| `$E7` | ISB | Increment, then subtract from A | 5 |
| `$04` | DOP | Double-byte NOP | 3 |

Use with caution. dasm supports these with `-f3` format.

## 11. Glossary

| Term | Definition |
|------|-----------|
| **Kernel** | The code that draws the visible portion of the screen (192 lines NTSC) |
| **VBLANK** | Vertical blank: time after VSYNC when beam returns to top; used for game logic |
| **Overscan** | Time after the visible frame; used for additional game logic |
| **WSYNC** | Wait for Sync: halts CPU until horizontal blank |
| **HMOVE** | Strobe that applies horizontal motion values to all objects |
| **LFSR** | Linear Feedback Shift Register: hardware-efficient pseudo-random generator |
| **Bank switching** | Swapping 4 KB ROM banks to access more than 4 KB total |
| **Zero page** | First 256 bytes ($00-$FF); faster access than absolute addressing |
| **Colour clock** | One TIA pixel; 3 colour clocks = 1 CPU cycle |
| **Scanline** | One horizontal line: 228 colour clocks (68 HBLANK + 160 visible) |
| **BCD** | Binary-Coded Decimal: each nibble stores a digit 0-9 |
| **VDEL** | Vertical Delay: buffers GRPx writes until the other player register is written |
