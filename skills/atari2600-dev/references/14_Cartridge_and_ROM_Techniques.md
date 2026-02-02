# Cartridge & ROM Techniques

The original VCS hardware expects a 4 KB ROM image.  Modern development tools allow much larger games using bank‑switching, but you must still organise your code and data carefully to stay within the available space.

## ROM Size Constraints

The 6507 can address only 4 KB of cartridge space at once.  This means:

* **2 KB games** map to $F800–$FFFF.  Early cartridges used this format and had very simple graphics and sound.
* **4 KB games** map to $F000–$FFFF and remain the most common size.  Many classic titles fit within this limit.
* Anything larger requires bank‑switching.  Each bank is 4 KB; you switch banks by writing to addresses that the cartridge decodes.

Design your data structures (fonts, graphics, levels) to fit within one or more 4 KB banks.  Avoid large lookup tables unless absolutely necessary.

## 4 K ROMs

In a standard 4 KB ROM, code usually starts at `$F000` and the reset/interrupt vectors reside at `$FFFC`–`$FFFF`.  Here’s a typical memory map:

```
$F000-$F7FF : Code and data segment 0
$F800-$FFFB : Code and data segment 1
$FFFC-$FFFD : Reset vector (points to your start routine)
$FFFE-$FFFF : BRK/IRQ vector (unused on the 2600, often duplicates reset)
```

You must ensure that your program counter never reads beyond $FFFF; the ROM is mirrored, so addresses wrap around.

## Bank Switching (F8, F6, F4, etc.)

To exceed 4 KB, cartridges implement bank‑switching by decoding writes to specific addresses.  Common schemes include:

* **F8 (8 KB)** – Two 4 KB banks.  Writing to `$1FF8` selects bank 0 and writing to `$1FF9` selects bank 1.  Code must place a small stub in each bank at the same addresses to handle switching.
* **F6 (16 KB)** – Four banks.  Writes to `$1FF6`–`$1FF9` select banks 0–3.
* **F4 (32 KB)** – Eight banks selected via `$1FF4`–`$1FF9`.
* **F8SC/F4SC** – Similar to F8 and F4 but include 128 bytes of RAM.  Writing to `$1FFB` enables the RAM bank.
* **E0, FE and others** – Provide different combinations of banks and RAM.  Consult the Harmony/Melody documentation for details.

To bank‑switch in code:

```asm
    lda #<bank_number>   ; not used; write to address selects bank
    sta $1FF8            ; switch to bank 0, for example
    jmp NewBankRoutine   ; continue execution in new bank
```

When designing multi‑bank games, place common routines (e.g., kernel code) in one bank and call them from others.  Use macros to encapsulate bank switches.

## Data Tables in ROM

Large tables for fonts, bitmaps or level data can consume significant space.  Tips:

* **Align tables on page boundaries** – Avoid crossing a $0100 boundary to prevent extra cycles during indexed addressing.
* **Place tables in separate banks** – Data used only in certain levels can reside in its own bank; switch banks when needed.
* **Compress data** – Use run‑length encoding or procedural generation to reduce size.  For example, Pitfall! uses an LFSR to generate the entire jungle world.
* **Use `SEG.U`** – In dasm, the `SEG.U` segment defines uninitialised data in zero page or RAM; use it for variables rather than storing them in ROM.

## Optimizing for Size and Speed

With limited ROM, optimising code matters:

* **Reuse code** – Factor out common routines (e.g., drawing digits) and call them with parameters.
* **Unroll loops selectively** – Unrolling reduces branch overhead but increases ROM usage.  Use it in the kernel where cycle timing is critical.
* **Use illegal opcodes cautiously** – Some developers use undocumented instructions (e.g., LAX, DCP) that combine operations in fewer cycles.  While powerful, they may not be supported on all assemblers and should be isolated behind macros.
* **Place rarely used code at the end of banks** – Put setup or title screen routines near $F800 so the start of the bank contains your time‑critical kernel.

Balancing size and speed is an art.  Profile your game to find bottlenecks and move code or data accordingly.
