# Toolchain and Stella Debugger

This reference covers the complete development toolchain for Atari 2600 programming: the dasm assembler for building ROMs, headless Stella for automated testing, the debug script format, and all available debugger commands.

---

## 1. dasm Assembler

**dasm** is the standard cross-assembler for Atari 2600 development. It targets the MOS 6502 processor (the 6507 in the 2600 uses the same instruction set with a reduced address bus).

### Command Line

The standard invocation for assembling an Atari 2600 ROM:

```
dasm source.asm -osource.a26 -f3 -v0 -lsource.lst -ssource.sym
```

### Flags

| Flag | Purpose |
|---|---|
| `-f3` | Output format 3: raw binary with no header. Required for Atari 2600 ROMs. |
| `-v0` | Verbosity level 0: only show errors. Keeps build output clean. |
| `-l<file>` | Write assembly listing to file. Shows addresses, opcodes, and source for each line. |
| `-s<file>` | Write symbol table to file. Lists all labels and their resolved addresses. |
| `-o<file>` | Output file path for the assembled ROM binary. |
| `-I<path>` | Add include search path for header files. |

### Directives

| Directive | Purpose | Example |
|---|---|---|
| `processor 6502` | Declare target CPU. Must be the first directive. | `processor 6502` |
| `SEG` | Begin an initialized (code/data) segment. | `SEG Code` |
| `SEG.U` | Begin an uninitialized segment (variables in RAM). | `SEG.U Variables` |
| `ORG` | Set the origin address within the current segment. | `ORG $F000` |
| `include` | Include another source file. | `include "vcs.h"` |
| `.byte` | Define one or more literal bytes. | `.byte $FF, $00, $42` |
| `.word` | Define a 16-bit word (little-endian). | `.word Reset` |
| `ds` | Define storage: reserve N bytes (uninitialized). | `ds 1` |
| `dc` | Define constant: reserve and initialize bytes. | `dc.b 10` |
| `align` | Align to a boundary (e.g., 256 for page). | `align 256` |
| `ECHO` | Print a message during assembly. | `ECHO "ROM size:", *` |
| `ERR` | Force an assembly error. | `ERR` |
| `IF / ELSE / ENDIF` | Conditional assembly. | `IF TV_MODE == NTSC` |
| `REPEAT / REPEND` | Repeat a block of code N times. | `REPEAT 10` |
| `MAC / ENDM` | Define a macro. | `MAC MY_MACRO` |

### Labels

- **Global labels** end with a colon: `Reset:`, `MainLoop:`, `DrawKernel:`
- **Local labels** start with a dot: `.loop`, `.done`, `.skip` -- they are scoped to the nearest preceding global label
- **Macros** are defined with `MAC name` ... `ENDM` and invoked by name. Arguments are referenced as `{1}`, `{2}`, etc.

### Standard Include Files

| File | Contents |
|---|---|
| `vcs.h` | Equates for all TIA and RIOT register addresses (VSYNC, VBLANK, WSYNC, COLUBK, GRP0, PF0, SWCHA, INTIM, etc.) |
| `macro.h` | Standard macros: CLEAN_START, VERTICAL_SYNC, SLEEP, SET_POINTER, TIMER_SETUP, TIMER_WAIT, ALIGN_PAGE, CHECK_PAGE, BYTE_COUNT |
| `tv_modes.h` | TV mode constants (NTSC/PAL/PAL60), scanline counts (VBLANK_LINES, KERNEL_LINES, OVERSCAN_LINES), and color definitions per mode |

### Typical Source Structure

```asm
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tv_modes.h"

TV_MODE = NTSC

; --- Variables in zero-page RAM ---
    SEG.U Variables
    ORG $80

frameCounter    ds 1
playerX         ds 1

; --- ROM code ---
    SEG Code
    ORG $F000       ; $F000 for 4K ROM, $F800 for 2K ROM

Reset:
    CLEAN_START
    ; ... game code ...

; --- Interrupt vectors ---
    ORG $FFFC
    .word Reset     ; Reset vector
    .word Reset     ; BRK/IRQ vector
```

---

## 2. Headless Stella

Stella is the standard Atari 2600 emulator and includes a built-in debugger. For automated testing without a display, Stella runs headlessly under xvfb (X Virtual Framebuffer).

### Full Command

```
xvfb-run -a -s "-screen 0 1280x720x24" stella -userdir <dir> -debug <rom>.a26 -dbg.logexec 1
```

### Flags Breakdown

| Part | Purpose |
|---|---|
| `xvfb-run -a` | Run under a virtual framebuffer; `-a` auto-selects a free display number |
| `-s "-screen 0 1280x720x24"` | Configure virtual screen resolution and color depth |
| `stella` | The Stella emulator binary |
| `-userdir <dir>` | Directory where Stella looks for `<romname>.script` and writes output files |
| `-debug` | Start Stella in debugger mode immediately |
| `<rom>.a26` | Path to the ROM file to load |
| `-dbg.logexec 1` | Enable script output logging -- writes debugger output to a file instead of only displaying in the UI |

### How -userdir Works

The `-userdir` flag tells Stella which directory to use as its user configuration directory. When Stella loads a ROM in debug mode, it looks for a file named `<romname>.script` in the `-userdir` directory. For example, if you load `main.a26` with `-userdir /path/to/build`, Stella will look for `/path/to/build/main.script` and automatically execute the commands in that file.

### How -dbg.logexec 1 Works

When `-dbg.logexec 1` is enabled, Stella writes all debugger output (command echoes and results) to a file named `<romname>.script.output.txt` in the same directory as the ROM. This is what makes headless validation possible -- the build script can parse this output file to check scanline counts, RAM state, and other validation criteria.

### Example Output Format

After running a debug script, the output file (`main.script.output.txt`) contains a log of every command executed and its result. Lines beginning with `> ` are echoed commands. Comment lines (starting with `;`) produce "No such command" errors that are safely ignored:

```
> frame #60
advanced 60 frame(s)
> print _scanEnd
CXBLPF|$100(R) / COLUP0|$100(W): $0106 %0000000100000110 #262
> exitRom
```

The `print _scanEnd` line is the key validation output. The value after `#` is the decimal scanline count. For a correct NTSC ROM this should be `#262`; for PAL it should be `#312`.

---

## 3. Debug Script Format

Debug scripts automate Stella's debugger. They allow you to run a ROM for a specified number of frames, inspect state, take screenshots, and exit -- all without user interaction.

### Script File Location and Naming

- Scripts must be named `<romname>.script` where `<romname>` matches the ROM filename without extension
- Scripts must be placed in the directory specified by the `-userdir` flag
- Example: ROM is `main.a26`, script must be `main.script` in the `-userdir` directory

### Script Syntax

- One debugger command per line
- Lines starting with `;` are treated as comments (Stella will report "No such command" but they are harmless)
- Blank lines are ignored
- Commands are exactly the same as those typed in the interactive Stella debugger

### Example: Basic Validation Script

```
frame #60
print _scanEnd
exitRom
```

This script:
1. Advances emulation by 60 frames (gives the ROM time to initialize and settle)
2. Prints `_scanEnd` to check the scanline count of the last completed frame
3. Exits the ROM and closes Stella

### Example: Gameplay Simulation Script

```
; let the game boot up
frame #60

; press fire to start
joy0Fire 1
joy0Fire 0

; play for a second
frame #60

; validate scanlines
print _scanEnd

; capture snapshot of screen to a png file
saveSnap

; show the RAM bytes
ram

exitRom
```

---

## 4. Stella Debugger Commands

This is a comprehensive reference of all debugger commands available in Stella's built-in debugger and in debug scripts.

### Execution Control

| Command | Description |
|---|---|
| `step` | Execute one CPU instruction and stop |
| `trace` | Step over subroutines (execute a JSR and all its code, then stop at the next instruction) |
| `scanLine [n]` | Advance by n scanlines (default 1) |
| `frame [n]` | Advance by n frames (default 1). Use `frame #60` for 60 frames. |
| `run` | Resume emulation at full speed (until a breakpoint is hit) |
| `exitRom` | Exit the ROM and close Stella. Essential as the last command in any debug script. |

### Breakpoints

| Command | Description |
|---|---|
| `break [addr]` | Set or clear a breakpoint at the given address. With no argument, lists breakpoints. |
| `breakIf {expression}` | Set a conditional breakpoint that triggers when the expression is true |
| `listBreaks` | Show all currently set breakpoints |
| `clearBreaks` | Remove all breakpoints |

Conditional breakpoint examples:

```
breakIf { _scanEnd != 262 }
breakIf { _scan > 262 }
breakIf { *SWCHA & $80 == 0 }
```

### Memory Inspection

| Command | Description |
|---|---|
| `ram` | Show a hex dump of all 128 bytes of zero-page RAM ($80-$FF) |
| `rom [addr] [value]` | Read or patch ROM bytes at the given address |
| `dump [addr]` | Display memory contents at the given address |
| `print {expression}` | Evaluate an expression and display the result in hex, binary, and decimal |

The `print` command output format shows the address mapping, then the value in three formats:
```
> print _scanEnd
CXBLPF|$100(R) / COLUP0|$100(W): $0106 %0000000100000110 #262
```
The value after `#` is the decimal result (the most useful for validation).

### Input Simulation

These commands simulate joystick input. Pass `1` to press or `0` to release.

| Command | Description |
|---|---|
| `joy0Up [0\|1]` | Player 0 joystick up |
| `joy0Down [0\|1]` | Player 0 joystick down |
| `joy0Left [0\|1]` | Player 0 joystick left |
| `joy0Right [0\|1]` | Player 0 joystick right |
| `joy0Fire [0\|1]` | Player 0 fire button |
| `joy1Up [0\|1]` | Player 1 joystick up |
| `joy1Down [0\|1]` | Player 1 joystick down |
| `joy1Left [0\|1]` | Player 1 joystick left |
| `joy1Right [0\|1]` | Player 1 joystick right |
| `joy1Fire [0\|1]` | Player 1 fire button |

### Snapshots and Session Logging

| Command | Description |
|---|---|
| `saveSnap` | Save a screenshot of the current frame as a PNG file in the ROM directory |
| `saveSes` | Log the current debugger session state to a text file |

### Traps (Memory Access Watches)

Traps halt execution when a specific memory address is accessed.

| Command | Description |
|---|---|
| `trap [addr]` | Catch any read or write access to the given address |
| `trapRead [addr]` | Halt on read access only |
| `trapWrite [addr]` | Halt on write access only |
| `listTraps` | Show all currently set traps |
| `clearTraps` | Remove all traps |

---

## 5. Pseudo-Registers (Built-in Variables)

Stella provides pseudo-registers that expose internal emulator state. These can be used in `print` commands and `breakIf` expressions.

| Variable | Description |
|---|---|
| `_scan` | Current scanline count (within the frame being drawn) |
| `_scanEnd` | Scanline count at the end of the last completed frame. **This is the primary validation metric.** NTSC should be 262, PAL should be 312. |
| `_fCount` | Frame count since emulation started |
| `_fCycles` | CPU cycles consumed in the current frame so far |
| `_sCycles` | CPU cycles consumed in the current scanline so far |
| `_cClocks` | Color clocks on the current scanline (3 color clocks per CPU cycle) |
| `_vBlank` | Vertical blank status: 1 if in VBLANK, 0 otherwise |
| `_vSync` | Vertical sync status: 1 if in VSYNC, 0 otherwise |
| `_bank` | Currently selected ROM bank (for bankswitched cartridges) |
| `_iCycles` | Number of CPU cycles consumed by the last executed instruction |
| `_inTim` | Current value of the RIOT timer (INTIM register) |
| `_timInt` | Timer interrupt flag (set when timer underflows) |
| `_cyclesLo` | Total cycle count since emulation started (lower 32 bits) |
| `_cyclesHi` | Total cycle count since emulation started (upper 32 bits) |

---

## 6. Expression Operators

Expressions can be used with `print` and `breakIf` commands. They are enclosed in curly braces: `{ expression }`.

### Arithmetic Operators

| Operator | Description |
|---|---|
| `+` | Addition |
| `-` | Subtraction |
| `*` | Multiplication |
| `/` | Division |
| `%` | Modulo |

### Bitwise Operators

| Operator | Description |
|---|---|
| `&` | Bitwise AND |
| `\|` | Bitwise OR |
| `^` | Bitwise XOR |
| `~` | Bitwise NOT |
| `<<` | Left shift |
| `>>` | Right shift |

### Comparison Operators

| Operator | Description |
|---|---|
| `==` | Equal to |
| `!=` | Not equal to |
| `<` | Less than |
| `>` | Greater than |
| `<=` | Less than or equal to |
| `>=` | Greater than or equal to |

### Number Prefixes

| Prefix | Base | Example |
|---|---|---|
| `$` | Hexadecimal | `$FF`, `$F000` |
| `#` | Decimal | `#262`, `#60` |
| `\` | Binary | `\10101010` |

---

## 7. Common Validation Patterns

### Checking Scanline Count

The most important validation for any Atari 2600 ROM is that it produces the correct number of scanlines per frame.

```
frame #60
print _scanEnd
```

In the output, look for `#262` (NTSC) or `#312` (PAL). Any other value means the frame timing is wrong and the ROM will roll or flicker on real hardware.

### Conditional Break on Bad Scanlines

Useful for finding exactly where timing goes wrong:

```
breakIf { _scanEnd != 262 }
run
```

Stella will halt as soon as a frame completes with the wrong scanline count.

### Simulating Gameplay

Test that a game handles input correctly:

```
; press and release fire button
joy0Fire 1
frame #5
joy0Fire 0

; move joystick right for half a second
joy0Right 1
frame #30
joy0Right 0

; check state after input
frame #1
print _scanEnd
ram
```

### Dumping RAM State for Analysis

The `ram` command shows all 128 bytes of zero-page RAM ($80-$FF). Cross-reference with your symbol file (.sym) to identify which variables hold which values:

```
frame #120
ram
```

The symbol file maps labels to addresses, so if your .sym shows `frameCounter = $0080`, you can find the frame counter value in the first byte of the RAM dump.

### Checking Specific Variables

Use `print` with memory addresses to inspect individual values:

```
print *$80
print *$81
```

The `*` dereferences the address, showing the value stored at that location.

---

## 8. Build Scripts

The development environment includes two Python scripts that automate the build and validation workflow.

### build_and_run.py

**Location:** `skills/atari2600-dev/scripts/build_and_run.py`

**Usage:**
```
python3 build_and_run.py <source.asm> [output.a26]
```

**What it does:**
1. Assembles the source file with dasm using standard flags (`-f3 -v0 -l -s`)
2. Looks for an existing `<romname>.script` file next to the output ROM, or creates a default one
3. Runs the ROM in headless Stella with `xvfb-run` and `-dbg.logexec 1`
4. Parses the script output file to extract the `_scanEnd` value and RAM dump
5. Reports whether validation passed (correct scanline count) or failed

**Default debug script** (created automatically if no .script file exists):
```
frame #60
print _scanEnd
exitRom
```

**Output directory logic:**
- If a `build/` directory exists alongside the source, output goes there
- Otherwise, output goes next to the source file
- The output filename matches the source filename with a `.a26` extension

### create_project.py

**Location:** `skills/atari2600-dev/scripts/create_project.py`

**Usage:**
```
python3 create_project.py <project-name>
```

**What it does:**
1. Creates the project directory structure:
   ```
   project-name/
   ├── src/
   │   └── main.asm          # Working template with proper frame structure
   ├── include/
   │   ├── vcs.h             # TIA/RIOT register definitions
   │   ├── macro.h           # Standard macros
   │   └── tv_modes.h        # TV mode constants and colors
   ├── build/
   │   └── main.script       # Default debug script for validation
   └── .gitignore            # Ignores build artifacts
   ```
2. Copies the standard include files (vcs.h, macro.h, tv_modes.h) from the assets directory
3. Generates a `main.asm` template with a complete, working frame structure (VSYNC, VBLANK, kernel, overscan) that assembles and validates cleanly out of the box
4. Creates a default `main.script` in the build directory for headless validation

**After creating a project, build and test it with:**
```
python3 build_and_run.py project-name/src/main.asm
```
