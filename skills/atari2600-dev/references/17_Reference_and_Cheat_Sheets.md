# Reference & Cheat Sheets

This section collects quick‑reference tables and definitions to keep handy while coding.

## TIA Register Cheat Sheet

| Address | Register | Description |
|---|---|---|
| **$00** | `VSYNC` | Start vertical sync (set bit 1) for exactly 3 scanlines. |
| **$01** | `VBLANK` | Control vertical blank and disable graphics during VBLANK/overscan. |
| **$02** | `WSYNC` | Wait for next scanline; halts CPU until horizontal blank ends. |
| **$03** | `RSYNC` | Reset horizontal sync counter (rarely used). |
| **$04–$05** | `NUSIZ0`, `NUSIZ1` | Sprite size and duplication settings for players/missiles. |
| **$06–$07** | `COLUP0`, `COLUP1` | Colours for players and missiles. |
| **$08** | `COLUPF` | Colour for playfield and ball. |
| **$09** | `COLUBK` | Background colour. |
| **$0A** | `CTRLPF` | Playfield reflect/score mode and priority bits. |
| **$0B–$0F** | `REFP0`, `REFP1`, `PF0`, `PF1`, `PF2` | Reflect players and load playfield bits. |
| **$10–$1A** | `RESP0`–`RESBL`, `AUDC0`–`AUDV1` | Reset positions and sound registers. |
| **$1B–$1C** | `GRP0`, `GRP1` | Player graphics bytes. |
| **$1D–$1F** | `ENAM0`, `ENAM1`, `ENABL` | Enable missiles and ball. |
| **$20–$2B** | `HMP0`–`HMCLR` | Horizontal motion registers and control. |
| **$2C–$2D** | `VDELP0`, `VDELP1` | Vertical delay bits for players and ball. |
| **$2E–$2F** | `VDELBL`, `RESMP0/1` | Vertical delay for ball; missile reset. |
| **$30–$3A** | `HMOVE`, `HMCLR`, `CXCLR` | Apply horizontal motion; clear motion registers; clear collision latches. |

Read‑only registers at the same addresses return collision flags (`CXM0P` etc.), input pins (`INPT0`–`INPT5`) and position counters.  See the TIA chapter for details.

## Cycle Count Reference

Most 6502 instructions on the 6507 take 2–7 cycles.  Important timings include:

| Instruction | Addressing Mode | Cycles | Notes |
|---|---|---|---|
| `LDA` | immediate | 2 | Load accumulator with constant. |
| `LDA` | zero page | 3 | Add 1 cycle if crossing page boundary with indexed addressing. |
| `STA` | zero page | 3 | Store accumulator. |
| `ADC/SBC` | immediate | 2 | Add/subtract with carry. |
| `JMP` | absolute | 3 | Jump to address. |
| `JSR` | absolute | 6 | Jump to subroutine (push return address). |
| `RTS` | 6 | Return from subroutine. |
| `INC/DEC` | zero page | 5 | Increment/decrement memory. |
| `BIT` | zero page | 3 | Test bits; sets N and V flags from operand. |

Branch instructions (`BEQ`, `BMI`, etc.) take 2 cycles if the branch is not taken and 3 cycles if it is; add 1 extra cycle if the destination crosses a page boundary.  Use this table when budgeting cycles in your kernel.

## Color Reference Tables

Each colour register uses bits `%CCCLLLL`, where `CCC` is luminance (0–7) and `LLLL` is hue (0–15).  Here are a few commonly used hues with their hexadecimal values:

| Hue (`LLLL`) | Colour | Example Value (with luminance 4) |
|---|---|---|
| `$0` | Black/Grey | `$40` – dark grey |
| `$2` | Orange | `$42` – dim orange |
| `$4` | Yellow | `$44` – dim yellow |
| `$6` | Green | `$46` – dim green |
| `$8` | Aqua | `$48` – dim cyan |
| `$A` | Blue | `$4A` – dim blue |
| `$C` | Purple | `$4C` – dim purple |
| `$E` | Red | `$4E` – dim red |

Increase luminance (`CCC`) for brighter shades.  On PAL systems colours shift slightly due to different phase encoding.

## Instruction Timing (6507)

Although the 6507 omits interrupts, its instruction timings match the 6502.  A few handy points:

* **Page crossing** – Indexed addressing modes add 1 cycle if crossing a page boundary (e.g., `LDA $00FF,X` with `X=1`).
* **Write operations** – `STA`, `STX`, `STY` always take 3 cycles in zero page and 4 cycles absolute.
* **Stack operations** – `PHA`, `PLA`, `PHP`, `PLP` each take 3–4 cycles; avoid them inside the kernel.
* **Illegal opcodes** – Some combine operations (see below) and often take 4–6 cycles.

Use these timings along with the cycle budget (76 cycles per scanline) to plan your code.

## Illegal Opcodes (SAX, LAX, DCP)

The 6502 family has undocumented instructions that perform multiple operations in one instruction.  While not officially supported, they work on the 6507 and can save cycles:

* **`SAX`** – Stores `A & X` to memory; useful for clearing bits.  Takes 3 cycles on zero page.
* **`LAX`** – Loads memory into both `A` and `X` simultaneously; available in several addressing modes.  Takes 3–4 cycles.
* **`DCP`** – Decrements memory and compares with `A` in one step; used in advanced kernels.  Takes 5–6 cycles.

Before using illegal opcodes, ensure your assembler supports them and be aware that future hardware or emulators may not.

## Glossary of Atari 2600 Terms

* **Kernel** – The part of your program that draws the visible portion of the screen.
* **Overscan** – The scanlines after the visible image where you can perform work while the beam retraces to the top.
* **Zero page** – The first 256 bytes of RAM, accessed more quickly than other addresses.
* **VBLANK** – Vertical blanking interval; the period when the beam moves from bottom to top.
* **HMOVE** – TIA register that applies horizontal motion values to sprites.
* **LFSR** – Linear‑feedback shift register; used for pseudorandom numbers.
* **Bank‑switching** – Technique to swap different 4 KB ROM banks into the address space.

Keep this cheat sheet nearby when writing code to recall addresses, timing and definitions quickly.
