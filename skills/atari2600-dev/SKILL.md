---
name: atari2600-dev
description: "Expert 6502 assembly programming for Atari 2600 game development. Use when creating, modifying, or debugging Atari 2600 games, writing 6502 assembly code for the TIA chip, working with .asm files, building .a26 ROM files with dasm, or running games in Stella emulator. Triggers on Atari 2600, 6502 assembly, TIA, dasm, Stella, .a26 ROM, or requests to create retro games."
---

# Atari 2600 Development

Expert system for creating 6502 assembly code for Atari 2600 games, compiling with dasm, and validating in headless Stella.

## Important: Skill Directory Paths

**This skill provides a base directory path when it loads.** All scripts are located relative to that base directory:
- `<skill-base-dir>/scripts/create_project.py`
- `<skill-base-dir>/scripts/build_and_run.py`

**Usage Pattern:**
1. When this skill loads, note the "Base directory for this skill" path from the system message
2. Use that full path when calling the scripts, e.g.: `python3 /path/to/skill/scripts/build_and_run.py <source.asm>`

## Core Workflow

### 1. Understand the Request

- **New game/demo**: Create project, implement core game loop
- **Modify existing code**: Read code first, understand structure, make targeted changes
- **Debug/fix issue**: Analyze code, identify timing or logic problems, apply fixes
- **Add feature**: Integrate into existing frame structure without breaking timing

### 2. Create or Modify Code

Generate 6502 assembly following these constraints:

- **128 bytes RAM** ($80-$FF) — that's all you get
- **76 CPU cycles per scanline** — the hard timing limit
- **NTSC: exactly 262 scanlines per frame** (3 VSYNC + 37 VBLANK + 192 kernel + 30 overscan)
- No video RAM — race the beam every frame
- Keep all game logic in VBLANK/overscan, never in the visible kernel
- Use DASM syntax: `processor 6502`, includes, `SEG.U`/`SEG`, labels with `:`, `.` for locals
- See [01_Architecture_and_Memory_Map.md](references/01_Architecture_and_Memory_Map.md) for full hardware details

### 3. Build and Validate

Use the build script:

```bash
python3 <skill-base-dir>/scripts/build_and_run.py <source.asm>
```

This script:
1. **Assembles** with dasm (`-f3` format, generates `.lst` and `.sym` files)
2. **Creates or uses** a debug script named `<romname>.script` in the build directory
3. **Runs** the ROM in headless Stella with the command:
   ```bash
   xvfb-run -a -s "-screen 0 1280x720x24" stella -userdir <build-dir> -debug <rom>.a26 -dbg.logexec 1
   ```
   **IMPORTANT:** The `-dbg.logexec 1` flag is ALWAYS required for automated validation
4. **Validates** by reading `_scanEnd` from `<romname>.script.output.txt` — expects 262 (NTSC) or 312 (PAL)
5. **Reports** pass/fail with scanline count, RAM state, and any saved snapshots

Output tells you exactly what happened:
- `Assembly OK` / `Assembly FAILED` — did dasm succeed?
- `Scanlines: 262 (NTSC OK)` — is the frame timing correct?
- `Build and validation PASSED` / `validation FAILED` — overall result

**How Stella Debug Scripts Work:**
- Script must be named `<romname>.script` (e.g., `main.script` for `main.a26`)
- Script must be in the directory specified by `-userdir`
- Stella automatically loads and executes the script when started with `-debug`
- Output is written to `<romname>.script.output.txt` when `-dbg.logexec 1` is used

### 4. Iterate

If validation fails:
- **Wrong scanline count**: Most likely game logic leaked into the kernel. Move calculations to VBLANK/overscan. Check `.lst` file for cycle counts in the kernel loop.
- **Assembly errors**: Check dasm output for missing includes, undefined labels, or exceeding 4KB.
- **Visual bugs**: Check the saved `.png` snapshot. Use the `.script` file to advance more frames or save multiple snapshots.

Rebuild after every change — the build-validate cycle catches timing bugs early.

## Creating a New Project

Use the project creation script:

```bash
python3 <skill-base-dir>/scripts/create_project.py my-game
```

Creates in the current directory:
```
my-game/
├── src/main.asm             # Working template (assembles to 262 scanlines)
├── include/
│   ├── vcs.h                # TIA/RIOT register definitions
│   ├── macro.h              # CLEAN_START, VERTICAL_SYNC, TIMER_SETUP, etc.
│   └── tv_modes.h           # NTSC/PAL constants (VBLANK_LINES, KERNEL_LINES, etc.)
└── build/
    └── main.script          # Default debug script for validation
```

Build immediately to verify:
```bash
python3 <skill-base-dir>/scripts/build_and_run.py my-game/src/main.asm
```

## Debug Scripts

**How Debug Scripts Work:**
- Stella automatically loads `<romname>.script` from the `-userdir` directory
- The script runs debugger commands automatically when Stella starts with `-debug`
- If no `.script` file exists, `build_and_run.py` creates a default one
- **DO NOT** use `-exitlauncher` (not a valid Stella flag)
- **DO NOT** pipe scripts with `< script.txt` (Stella uses naming convention, not stdin)

### Script Format

One command per line. Comments with `//`. Example:

```
frame #60
print _scanEnd
exitRom
```

### Key Commands

| Command | What It Does |
|---|---|
| `frame #N` | Advance N frames |
| `print <expr>` | Print a value (register, pseudo-register, or address) |
| `exitRom` | Quit Stella |

### Pseudo-Registers

These are read-only values computed by Stella — use them with `print`:

| Register | Meaning |
|---|---|
| `_scanEnd` | Total scanlines in the last completed frame (should be 262 for NTSC) |
| `_scan` | Current scanline number |
| `_fCount` | Frame count since ROM start |
| `_cClocks` | Color clocks within current scanline |

### Input Simulation

Simulate joystick/button input in scripts:

| Command | Effect |
|---|---|
| `joy0Up 1` / `joy0Up 0` | Press/release P0 joystick up |
| `joy0Down`, `joy0Left`, `joy0Right` | Other P0 directions |
| `joy0Fire 1` / `joy0Fire 0` | Press/release P0 fire button |
| `joy1Up`, `joy1Fire`, etc. | P1 equivalents |

Example — test what happens when fire is pressed:
```
joy0Fire 1
frame #10
saveSnap
joy0Fire 0
frame #10
saveSnap
exitRom
```

See [03_Toolchain_and_Stella_Debugger.md](references/03_Toolchain_and_Stella_Debugger.md) for the complete debugger command reference.

## Frame Structure

This is the most important concept. Every frame must follow this structure:

```asm
MainLoop:
    ; 1. VSYNC (3 scanlines)
    VERTICAL_SYNC

    ; 2. VBLANK (37 scanlines) — ALL game logic here
    TIMER_SETUP VBLANK_LINES
    ;   Read input (SWCHA, INPT4/5)
    ;   Update positions, process collisions
    ;   Pre-calculate kernel data (colours, graphics pointers)
    ;   Position sprites (SetHorizPos)
    TIMER_WAIT
    lda #0
    sta VBLANK              ; turn off blanking

    ; 3. Visible Kernel (192 scanlines) — ONLY drawing
    ;   sta WSYNC, update GRP0/1, PF0/1/2, COLUPx
    ;   NO game logic, NO collision checks, NO input reading

    ; 4. Overscan (30 scanlines) — more game logic time
    lda #%01000010
    sta VBLANK              ; turn on blanking
    TIMER_SETUP OVERSCAN_LINES
    ;   Sound updates, animation counters, AI
    TIMER_WAIT

    jmp MainLoop
```

**MOST CRITICAL MISTAKE**: Putting game logic (collision detection, input reading, score updates, movement calculations) inside the visible kernel. This exceeds 76 cycles per scanline, produces wrong scanline counts, and fails validation. The kernel must ONLY write to graphics registers using pre-calculated values.

See [02_Frame_Structure_and_Timing.md](references/02_Frame_Structure_and_Timing.md) for cycle budgets, timing diagrams, and kernel patterns.

## Common Tasks

| Task | Key Approach | Reference |
|---|---|---|
| Sprite movement | Read SWCHA in VBLANK, update position, use SetHorizPos | [05_Sprites_Positioning_and_Motion.md](references/05_Sprites_Positioning_and_Motion.md) |
| Collision detection | Read CXP0FB/CXM0P etc. in VBLANK, clear with CXCLR | [06_Input_and_Collision.md](references/06_Input_and_Collision.md) |
| Sound effects | Set AUDC/AUDF/AUDV, update each frame | [07_Sound_and_Music.md](references/07_Sound_and_Music.md) |
| Score display | BCD arithmetic (SED/CLD), 48-pixel sprite technique | [09_Advanced_Techniques.md](references/09_Advanced_Techniques.md) |
| Playfield graphics | PF0/PF1/PF2 with CTRLPF for reflect/score mode | [04_Graphics_and_Playfield.md](references/04_Graphics_and_Playfield.md) |
| Asymmetric playfield | Timed writes to PF registers mid-scanline | [04_Graphics_and_Playfield.md](references/04_Graphics_and_Playfield.md) |
| Multi-sprite kernel | Sprite multiplexing, reposition between zones | [09_Advanced_Techniques.md](references/09_Advanced_Techniques.md) |
| Timers | TIM64T for VBLANK/overscan, TIMER_SETUP/TIMER_WAIT macros | [08_Game_Logic_and_Timers.md](references/08_Game_Logic_and_Timers.md) |
| Debugging | Stella .script files, _scanEnd validation, cycle counting | [03_Toolchain_and_Stella_Debugger.md](references/03_Toolchain_and_Stella_Debugger.md) |
| Common bugs | Kernel timing, HMOVE bars, uninitialised RAM, CXCLR | [10_Common_Patterns_and_Gotchas.md](references/10_Common_Patterns_and_Gotchas.md) |
| Complete examples | Working code for rainbow, sprite, maze, sound | [11_Complete_Examples.md](references/11_Complete_Examples.md) |

## Reference Index

| File | Contents |
|---|---|
| [01_Architecture_and_Memory_Map.md](references/01_Architecture_and_Memory_Map.md) | 6507 CPU, TIA, RIOT, memory map, register addresses |
| [02_Frame_Structure_and_Timing.md](references/02_Frame_Structure_and_Timing.md) | VSYNC/VBLANK/kernel/overscan, cycle budgets, NTSC vs PAL |
| [03_Toolchain_and_Stella_Debugger.md](references/03_Toolchain_and_Stella_Debugger.md) | dasm assembler, Stella debugger commands, .script format |
| [04_Graphics_and_Playfield.md](references/04_Graphics_and_Playfield.md) | Colour system, PF registers, playfield timing, asymmetric PF |
| [05_Sprites_Positioning_and_Motion.md](references/05_Sprites_Positioning_and_Motion.md) | Players, missiles, ball, NUSIZ, SetHorizPos, HMOVE, VDEL |
| [06_Input_and_Collision.md](references/06_Input_and_Collision.md) | Joysticks, fire buttons, console switches, collision registers |
| [07_Sound_and_Music.md](references/07_Sound_and_Music.md) | AUDC/AUDF/AUDV, distortion types, frequency tables, music |
| [08_Game_Logic_and_Timers.md](references/08_Game_Logic_and_Timers.md) | RIOT timer, frame counters, state machines, RNG, BCD scoring |
| [09_Advanced_Techniques.md](references/09_Advanced_Techniques.md) | 48-pixel sprites, score displays, multiplexing, bank switching |
| [10_Common_Patterns_and_Gotchas.md](references/10_Common_Patterns_and_Gotchas.md) | Kernel stability, common bugs, debugging workflow |
| [11_Complete_Examples.md](references/11_Complete_Examples.md) | Full working programs: rainbow, sprite, maze, sound demo |
| [12_Reference_and_Cheat_Sheets.md](references/12_Reference_and_Cheat_Sheets.md) | Register tables, 6502 instructions, colour chart, memory map |
