# Atari 2600 Fundamentals

The Atari Video Computer System (VCS), later known as the Atari 2600, is a cartridge‑based home console released in 1977.  Games are programmed directly in 6502 assembly and must run within severe hardware limits: 128 bytes of RAM, typically 4 KB of ROM (though bank‑switching allows more), and no frame buffer – the CPU must “race the beam” to draw each scanline as it is sent to the television.

## Atari 2600 Architecture Overview

The VCS architecture revolves around three chips and a cartridge port:

* **MOS 6507 CPU** – A cost‑reduced version of the 6502 with 13 address lines.  It uses an 8‑bit data bus but can only address 8 KB of memory space.  The first 4 KB ($0000–$0FFF) is reserved for RAM and I/O, while the upper 4 KB ($1000–$1FFF) maps the game cartridge.  Only the lower 8 bits of data are available; interrupts and some instructions not needed for the console were removed to reduce cost.

* **Television Interface Adaptor (TIA)** – This custom ASIC generates video and audio.  It contains horizontal position counters for two players, two missiles and a ball, a 20‑bit playfield generator, collision detection circuitry, and two 5‑bit audio shift registers.  Because there is no frame buffer, the CPU must update TIA registers in real time during each scanline.

* **RIOT (6532 RAM–I/O–Timer)** – Provides 128 bytes of scratch RAM, two 8‑bit I/O ports for joysticks and console switches, and a programmable interval timer.  The timer counts down at 1, 8, 64 or 1024 CPU‑cycle intervals and underflows into the INTIM register.

* **Game cartridge** – Plugs into the top of the console and maps directly into the CPU’s upper address space.  Standard 4 KB games occupy $F000–$FFFF (mirrored at $1000–$1FFF).  Larger games use bank‑switching to swap ROM banks.

## MOS 6507 CPU Basics (6502 Subset)

The 6507 inside the 2600 is functionally equivalent to a 6502 but with a restricted address bus and no interrupt lines.  It still executes the full 6502 instruction set, including page‑zero addressing modes that access the first 256 bytes more efficiently.  The CPU has:

* **Registers** – An 8‑bit accumulator (`A`) used for arithmetic and logic; two index registers (`X` and `Y`) often used for loop counters or offsets; a 16‑bit program counter (`PC`); an 8‑bit stack pointer (`SP`) that points into page 1 ($0100–$01FF); and a processor status register holding flags such as carry, zero, negative and overflow.

* **Zero page ($00–$FF)** – The first 256 bytes are called zero page.  Instructions that access it require fewer bytes and cycles, so most variables and pointers live here.  Page 1 ($0100–$01FF) holds the hardware stack.

* **Instruction timing** – Most instructions take 2–7 CPU cycles.  Because the CPU runs at one‑third the TIA clock, there are only 76 CPU cycles per scanline.  Precise cycle counting is essential when updating TIA registers mid‑scanline.

## TIA, RIOT, and Cartridge Hardware

### TIA overview

The TIA converts 8‑bit parallel writes from the CPU into the analog NTSC/PAL video signal.  It has dozens of write‑only registers controlling:

* **Synchronization and blanking** – `VSYNC` starts vertical sync pulses; `VBLANK` blanks the beam and disables player/missile graphics during vertical blank and overscan; `WSYNC` stalls the CPU until the next scanline begins.

* **Playfield** – The 20‑bit playfield is loaded via `PF0`, `PF1` and `PF2` registers and can be reflected or scored via `CTRLPF`.  The 2600 draws 40 low‑resolution pixels per scanline by duplicating the 20‑bit pattern across the left and right halves.

* **Sprites** – Two 8‑pixel players (`P0`, `P1`), two one‑pixel missiles and a one‑pixel ball.  Their graphics come from `GRP0`/`GRP1` and `ENAM0`/`ENAM1`/`ENABL`.  Horizontal positions are set by writing to `RESP0`/`RESP1`/`RESM0`/`RESM1`/`RESBL`.  The `NUSIZx` register selects sprite size and duplication patterns.

* **Audio** – Two independent audio channels with tone (`AUDCx`), frequency (`AUDFx`) and volume (`AUDVx`) registers.  Distortion values select pure or noise waveforms, while frequency divides a 30 kHz reference clock to set pitch.

* **Collision detection** – Fifteen one‑bit latches report collisions between any pair of objects (players, missiles, ball and playfield).  Reading `CXM0P`, `CXM1P`, `CXP0FB`, etc., returns collision bits.  Writing to `CXCLR` clears them.

### RIOT (6532) overview

The RIOT contains:

* **128 bytes of RAM** at addresses $0080–$00FF for variables and stack frame storage.
* **Two I/O ports** – `SWCHA` reads joystick directions; `SWCHB` reads console switches (Reset, Select, Color/BW, difficulty).  Corresponding control registers `SWACNT` and `SWBCNT` configure inputs as outputs.
* **Timer** – Four write‑only registers (`TIM1T`, `TIM8T`, `TIM64T`, `T1024T`) start a down counter dividing the system clock by 1, 8, 64 or 1024 cycles.  The current value is read from `INTIM`, and `INSTAT` holds the timer‑underflow flag.

### Cartridge and memory map

The 2600 memory map is heavily mirrored.  Addresses \$0000–\$003F map the 45 TIA write and 14 read registers; this 64‑byte block is mirrored across \$0040–\$007F and repeatedly up to \$00FF.  The RIOT RAM at \$0080–\$00FF is also mirrored across \$0100–\$01FF, but page 1 is reserved for the stack.  The RIOT I/O and timer registers live at \$0280–\$0297 (mirrored through \$02FF).  Cartridge ROM appears from \$F000–\$FFFF for 4 KB games; smaller 2 KB games map at \$F800–\$FFFF.  Larger games use bank‑switching to swap different 4 KB banks into this range.

## NTSC vs PAL Timing Differences

The VCS supports both NTSC (North America) and PAL (Europe) televisions.  NTSC frames consist of **262 scanlines**: 3 lines of vertical sync, ~37 lines of vertical blank, 192 visible lines and ~30 overscan lines.  Each scanline is 76 CPU cycles (228 TIA color clocks), with 68 clocks of horizontal blank and 160 visible pixels.  PAL consoles run at **50 Hz** with **312 scanlines**; they allocate 48 lines of VBLANK, 228 visible lines and 36 overscan lines.  The slower clock reduces game speed by about 17 % and shifts audio frequencies.  PAL also uses a different colour encoding, producing slightly different hues and an expanded frame; developers must account for these differences when porting games.

In summary, the Atari 2600 is a minimalist but surprisingly powerful platform.  Understanding its memory map, CPU characteristics and the interplay between the TIA and RIOT is essential before diving into game development.
