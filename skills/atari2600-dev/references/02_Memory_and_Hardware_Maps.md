# Memory & Hardware Maps

Developing for the Atari 2600 requires an intimate knowledge of its tiny address space.  The following sections outline the memory map, key hardware registers and conventions for organising data.

## VCS Memory Map

The 6507’s 13‑bit address bus can only address 8 KB.  This space is heavily mirrored:

| Address range | Purpose | Notes |
| --- | --- | --- |
| **$0000–$003F** | **TIA write registers** | 45 write‑only registers controlling sync, playfield, sprites, colour, audio and horizontal motion.  This 64‑byte block repeats every $40 bytes through $00FF. |
| **$0000–$003F (read)** | **TIA read registers** | 14 registers return collision flags, input latches and horizontal motion counters. |
| **$0080–$00FF** | **RIOT RAM** | 128 bytes of scratch RAM, mirrored across $0180–$01FF but page 1 is used for the stack. |
| **$0280–$0297** | **RIOT I/O ports and timers** | `SWCHA`, `SWCHB`, `SWACNT`, `SWBCNT`, `INTIM`, `INSTAT` and timer set registers `TIM1T`/`TIM8T`/`TIM64T`/`T1024T`.  Mirrored through $02FF. |
| **$F000–$FFFF** | **Cartridge ROM** | Standard 4 KB games occupy this space.  2 KB games map to $F800–$FFFF.  Larger ROMs use bank‑switching to swap 4 KB windows here. |

Because the TIA and RIOT areas mirror every $100 and $80 bytes respectively, you can refer to registers using multiple addresses.  It is common to define equates for the lowest mirror and use it consistently.

## TIA Register Reference

The TIA exposes dozens of registers grouped by function:

* **Synchronization and blanking** – `VSYNC` ($00) starts vertical sync pulses; `VBLANK` ($01) blanks the beam and optionally disables sprite drawing; `WSYNC` ($02) halts the CPU until the next scanline begins.
* **Horizontal motion and size** – `HMOVE` ($2A) applies horizontal motion values (`HMP0`/`HMP1`/`HMM0`/`HMM1`/`HMBL`) to sprites; `HMCLR` ($2B) resets motion registers; `NUSIZ0`/`NUSIZ1` select sprite width and duplication patterns.
* **Playfield** – `PF0` ($0D), `PF1` ($0E) and `PF2` ($0F) hold the 20‑bit playfield bitmap; `CTRLPF` ($0A) configures reflection, score mode and priority; `COLUPF` sets the playfield colour and luminance.
* **Players** – `GRP0`/`GRP1` ($1B/$1C) load 8‑bit graphics for players 0/1.  `ENAM0`/`ENAM1` enable missiles and `ENABL` enables the ball.  Reset registers (`RESP0`/`RESP1`/`RESM0`/`RESM1`/`RESBL`) set horizontal positions.  `VDELP0`/`VDELP1` and `VDELBL` buffer graphics for fine‑timed updates.
* **Audio** – `AUDC0`/`AUDC1` select waveform distortions; `AUDF0`/`AUDF1` select pitch; `AUDV0`/`AUDV1` set volume.
* **Collision registers (read‑only)** – `CXM0P`, `CXM1P`, `CXP0FB`, `CXP1FB`, `CXM0FB`, `CXM1FB`, `CXBLPF` and `CXPPMM` report collisions between pairs of objects.  Each register contains two one‑bit latches.
* **Input ports (read‑only)** – `INPT0`–`INPT5` return paddle triggers and joystick button states.  Bits are 1 when open and 0 when pressed.

A complete list of register addresses and bit fields is provided in the TIA data sheet and the Woodgrain Wizard reference.

## RIOT Registers and RAM

The RIOT chip provides two 8‑bit I/O ports and a timer.  Important registers include:

* **SWCHA ($0280)** – Port A for joysticks.  Bits 7–4 report player 0’s right, left, down, up directions; bits 3–0 report player 1’s left, right, down, up.
* **SWACNT ($0281)** – Control register for Port A; bits set to 1 configure corresponding bits in SWCHA as inputs.
* **SWCHB ($0282)** – Port B for console switches.  Bit 7 is `P1_DIFF` (player 1 difficulty), bit 6 `P0_DIFF`, bit 3 `COLOR/BW`, bit 1 `GAME_SELECT`, bit 0 `GAME_RESET`.  Bits are low when switches are pressed.
* **SWBCNT ($0283)** – Control register for Port B.
* **INTIM ($0284)** – Timer output latch; counts down when a timer is active.
* **INSTAT ($0285)** – Timer status; bit 7 indicates the timer underflow flag.
* **TIM1T/TIM8T/TIM64T/T1024T ($0294–$0297)** – Timer set registers.  Writing a value to one of these starts a down counter at 1, 8, 64 or 1024 cycles per tick.

Use of the RIOT timer is covered in the Timers & Game Logic section.

## Cartridge Addressing and Banking Basics

Because the 6507 only addresses 4 KB of cartridge space at once, larger games must bank‑switch.  Common schemes include:

* **2 KB/4 KB games** – The simplest cartridges map 2 KB at $F800–$FFFF or 4 KB at $F000–$FFFF with no switching.  Execution wraps around because the address space is mirrored.
* **F8 (8 KB)** – Two 4 KB banks.  Writing to $1FF8 selects bank 0 and writing to $1FF9 selects bank 1.
* **F6 (16 KB)** – Four banks; writes to $1FF6–$1FF9 select banks 0–3.
* **F4/F4SC (32 KB)** – Eight banks; F4SC adds 128 bytes of RAM.
* **FA/F8SC** – Provide additional RAM or special features such as display kernels.

When using a bankswitching scheme, your code must reside in one bank but you may define vectors in each bank so the system can jump into the correct code when switching.  The bank‑switching mechanism is selected by hardware signatures in the cartridge.

## Zero Page Usage and Conventions

Zero page ($00–$7F) is precious because instructions addressing it take one cycle less and one byte less than absolute addressing.  Typical conventions are:

* Reserve a few bytes for frequently accessed variables such as frame counters, pointers and temporary registers.
* Use page 0 addresses $00–$1F for kernel variables that must be accessed during the display; this minimises page crossing delays.
* Avoid using page 1 ($0100–$01FF) except via the stack pointer.  The 6507 stack grows downward from $01FF.

Because there are only 128 bytes of RAM, efficient zero‑page allocation and re‑use of variables in different parts of the frame (e.g., using the same byte for both vertical blank logic and overscan) is a common optimisation.
