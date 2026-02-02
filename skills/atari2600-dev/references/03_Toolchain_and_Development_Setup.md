# Toolchain & Development Setup

Developing Atari 2600 software typically involves an assembler (dasm) to convert assembly into binary ROM images and an emulator for testing.  The following sections describe how to configure your environment, build projects and debug your code.

## dasm Assembler Reference

**dasm** is a cross‑assembler that supports the MOS 6502, 6507 and related processors.  On the 2600 you assemble with the directive:

```asm
    processor 6502    ; the 6507 uses the full 6502 instruction set
    include "vcs.h"   ; defines TIA/RIOT registers
    include "macro.h" ; common macros like CLEAN_START
```

dasm uses **segments** to separate code and data.  `SEG` defines a code segment, while `SEG.U` defines an uninitialised data segment (used for variables).  `ORG` sets the origin within the current segment.  For a 4 KB ROM you usually start code at `$f000` and data at `$0080`.  The assembler automatically calculates branch offsets and addresses.  The `vcs.h` include file defines equates for all TIA and RIOT registers so you don’t need to remember hexadecimal addresses.

## Project Layout and Build Scripts

A typical project directory might look like:

```
mygame/
  src/
    mygame.asm     ; main assembly source
    include/
      vcs.h        ; hardware definitions
      macro.h      ; macros like CLEAN_START, TIMER_SETUP
  build.sh         ; script to assemble and launch emulator
  assets/          ; graphics or level data
```

Your build script can call dasm and then open the resulting `.bin` in an emulator:

```sh
dasm src/mygame.asm -o mygame.bin -f3 -Isrc/include
stella mygame.bin
```

Here `-f3` produces a headerless 2600 binary.  If you’re using bank‑switching, you may need to specify additional options or include ROM signatures in your source.

## Using Stella for Debugging

**Stella** is the de facto Atari 2600 emulator.  It includes a powerful debugger that allows you to:

* **Pause and step through instructions** – You can single‑step (`Step`), step over subroutines (`Step Over`) or run to the next frame.
* **Inspect CPU registers and RAM** – The debugger shows `A`, `X`, `Y`, `SP` and `PC` as well as the 128‑byte RIOT RAM and zero‑page variables.
* **View TIA state** – Separate views display the current scanline, horizontal beam position and the contents of TIA registers.  A `TIA objects` view overlays sprites, missiles and the playfield so you can see how writes affect the screen.
* **Toggle collision display** – Pressing Ctrl‑C in the 8bitworkshop IDE toggles collision highlighting to verify that collision registers behave as expected.
* **Enable scanline count** – Ctrl‑G displays a scanline counter overlay, useful for verifying that your kernel draws exactly 192 lines.

The debugger also supports breakpoints and watchpoints.  You can set a breakpoint on a specific scanline or instruction address, or watch a memory location and halt when it changes.

## Debugging with Breakpoints and TIA Views

When debugging, break at the start of your kernel or at the vertical blank routine.  Use the TIA view to check horizontal positions and to ensure that writes to `PF0`/`PF1`/`PF2`, `GRP0` and `GRP1` occur at the intended cycle.  Breakpoints on `WSYNC` instructions help verify scanline timing.  You can also watch the `INTIM` timer or `CXM0P` collision latches to understand when collisions occur.

Interactive debugging is crucial because the 2600 has no text output.  Use Stella’s memory editor to tweak variables on the fly and test different scenarios.

## Common Assembly Macros and Patterns

The `macro.h` file distributed with the dasm examples provides many helpful macros:

* **CLEAN_START** – Clears zero page, sets the stack pointer and disables interrupts; recommended at the start of every program.
* **VERTICAL_SYNC** – Writes to `VSYNC` and holds it for three scanlines using `WSYNC`; must be called during vertical blank to begin a new frame.
* **TIMER_SETUP/TIMER_WAIT** – Configures the RIOT timer for a specified number of scanlines and waits until it underflows.  Timer values are computed from the number of scanlines using `(N * 76 + 13)/64` for the TIM64T interval.
* **SLEEP / NOP** – Delay macros to waste CPU cycles; used for fine timing inside the kernel.
* **SCORE / DRAW** – Macros from various sample code to draw digits or update sprites mid‑scanline.

Studying and re‑using these macros will save time and help you build stable kernels.
