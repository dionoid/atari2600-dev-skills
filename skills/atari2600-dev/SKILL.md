---
name: atari2600-dev
description: "Expert 6502 assembly programming for Atari 2600 game development. Use when creating, modifying, or debugging Atari 2600 games, writing 6502 assembly code for the TIA chip, working with .asm files, building .a26 ROM files with dasm, or running games in Stella emulator. Triggers on Atari 2600, 6502 assembly, TIA, dasm, Stella, .a26 ROM, or requests to create retro games."
---

# Atari 2600 Development

Expert system for creating 6502 assembly code for Atari 2600 games, compiling with dasm, and testing in Stella emulator.

## Core Workflow

### 1. Understand the Request

Determine what type of Atari 2600 work is needed:
- **New game/demo**: Start with project setup, then implement core game loop
- **Modify existing code**: Read code first, understand structure, make targeted changes
- **Debug/fix issue**: Analyze code, identify timing or logic problems, apply fixes
- **Add feature**: Integrate into existing frame structure without breaking timing

### 2. Create or Modify Code

Generate 6502 assembly code following these principles:

**Hardware Constraints:**
- Only 128 bytes RAM ($80-$FF)
- No video RAM - race the beam every frame
- **76 CPU cycles per scanline** - CRITICAL timing constraint
- **NTSC: EXACTLY 262 scanlines per frame** (3 + 37 + 192 + 30)
- PAL: 312 scanlines per frame (3 + 45 + 228 + 36)
- 60 Hz (NTSC) / 50 Hz (PAL)

**Frame Structure (NTSC - must total 262 scanlines):**
```asm
MainLoop:
    ; 1. Vertical Sync (3 scanlines)
    VERTICAL_SYNC

    ; 2. Vertical Blank (37 scanlines) - game logic time
    ; Pre-calculate colors, positions, lookup tables here
    ; You have ~2,800 cycles for complex calculations

    ; 3. Visible Screen (192 scanlines) - display kernel
    ; CRITICAL: Each loop iteration must be EXACTLY 1 scanline
    ; Keep kernel simple - max 76 cycles per scanline
    ; Update TIA registers for graphics each scanline

    ; 4. Overscan (30 scanlines) - more game logic time
    ; Additional time for calculations

    jmp MainLoop
```

**Code Quality Standards:**
- **CRITICAL**: Use WSYNC to synchronize with scanlines
- **CRITICAL**: Keep visible kernel under 76 cycles/scanline - if doing complex calculations, each loop iteration may span multiple scanlines, breaking timing
- Pre-calculate data during VBLANK, not during visible screen
- Use lookup tables for complex math in kernels
- Clear TIA registers at startup
- Include comments explaining TIA interactions and cycle counts
- Follow DASM syntax (labels with `:`, `.` for local labels)
- Structure: processor directive, includes, variables, code, vectors

### 3. Build and Test

Use provided scripts for rapid iteration:

**scripts/build_and_run.py**: Compile and launch in one command
```bash
python scripts/build_and_run.py game.asm
```

Automatically:
- Assembles with dasm (-f3 format for .a26 ROMs)
- Generates listing and symbol files
- Launches Stella emulator

**scripts/create_project.py**: Generate new project structure
```bash
python scripts/create_project.py my-game
```

Creates:
- src/main.asm with working template
- include/vcs.h, macro.h, tia_constants.h and tv_modes.h
- build/ directory for outputs

## Hardware Reference

**When to consult references:** Load these files when you need detailed information:

- [01_Atari_2600_Fundamentals.md](references/01_Atari_2600_Fundamentals.md) - Architecture overview, 6507 CPU, TIA/RIOT basics, NTSC vs PAL timing
- [02_Memory_and_Hardware_Maps.md](references/02_Memory_and_Hardware_Maps.md) - Complete memory map, TIA/RIOT register addresses, zero-page conventions
- [03_Toolchain_and_Development_Setup.md](references/03_Toolchain_and_Development_Setup.md) - dasm assembler usage, project layout, Stella debugger, macros
- [04_Frame_Structure_and_Timing.md](references/04_Frame_Structure_and_Timing.md) - Frame sections (VSYNC/VBLANK/kernel/overscan), cycle counting, timing
- [05_Graphics_Basics.md](references/05_Graphics_Basics.md) - Color system, luminance values, basic TIA graphics concepts
- [06_Playfield_Graphics.md](references/06_Playfield_Graphics.md) - PF0/PF1/PF2 registers, reflection, score mode, asymmetric playfields
- [07_Players_Missiles_and_Ball.md](references/07_Players_Missiles_and_Ball.md) - Sprite objects (P0/P1/M0/M1/BL), NUSIZ, graphics registers
- [08_Positioning_and_Motion.md](references/08_Positioning_and_Motion.md) - RESP0/1, horizontal motion (HMP0/1, HMOVE), fine positioning
- [09_Input_Handling.md](references/09_Input_Handling.md) - Reading joysticks (SWCHA), fire buttons (INPT4/5), console switches
- [10_Collision_Detection.md](references/10_Collision_Detection.md) - Collision registers (CXM0P, CXP0FB, etc.), CXCLR, collision patterns
- [11_Sound_and_Music.md](references/11_Sound_and_Music.md) - Audio channels, AUDC/AUDF/AUDV registers, waveforms, music patterns
- [12_Timers_and_Game_Logic.md](references/12_Timers_and_Game_Logic.md) - RIOT timer (TIM64T), INTIM, game state management
- [13_Advanced_Graphics_Techniques.md](references/13_Advanced_Graphics_Techniques.md) - Multi-sprite kernels, flicker, 2-line kernels, 6-digit scores
- [14_Cartridge_and_ROM_Techniques.md](references/14_Cartridge_and_ROM_Techniques.md) - Bank switching (F8/F6/F4), ROM layout, cartridge formats
- [15_Common_Patterns_and_Gotchas.md](references/15_Common_Patterns_and_Gotchas.md) - Best practices, common mistakes, optimization tips
- [16_Complete_Examples.md](references/16_Complete_Examples.md) - Full working code samples demonstrating various techniques
- [17_Reference_and_Cheat_Sheets.md](references/17_Reference_and_Cheat_Sheets.md) - Quick reference tables for registers, cycles, and common values

**Quick reference:**

Memory:
- $00-$2C: TIA write registers
- $80-$FF: RAM (128 bytes)
- $0280-$0297: RIOT (I/O, timers)
- $F000-$FFFF: ROM (4KB)

Key TIA registers:
- VSYNC ($00), VBLANK ($01), WSYNC ($02)
- COLUBK ($09): Background color
- COLUPF ($08): Playfield color
- COLUP0/1 ($06/$07): Player colors
- GRP0/1 ($1B/$1C): Player graphics
- PF0/1/2 ($0D/$0E/$0F): Playfield graphics
- RESP0/1 ($10/$11): Reset player position
- HMP0/1 ($20/$21): Horizontal motion
- HMOVE ($2A): Apply motion
- CXCLR ($2C): Clear collisions

Key RIOT registers:
- SWCHA ($0280): Joystick input
- INPT4/5 ($0C/$0D): Fire buttons
- TIM64T ($0296): 64-cycle timer (most common)
- INTIM ($0284): Read timer

## Development Patterns

### Starting from Scratch

1. Create project: `python scripts/create_project.py game-name`
2. Edit src/main.asm:
   - Define variables at $80
   - Implement game logic in VBLANK
   - Create display kernel for visible screen
   - Handle input, collisions, scoring
3. Build and test: `python scripts/build_and_run.py src/main.asm`
4. Iterate: Modify code, rebuild, test

### Modifying Existing Code

1. Read the .asm file completely
2. Identify frame structure and kernel
3. Make targeted changes preserving timing
4. Test immediately to catch timing issues

### Common Tasks

**Add sprite movement:**
- Read joystick in VBLANK: `lda SWCHA`
- Update position variables
- Position sprite with RESP0/1 and horizontal motion
- See [08_Positioning_and_Motion.md](references/08_Positioning_and_Motion.md) for detailed positioning techniques

**Add collision detection:**
- Read collision registers: `lda CXP0FB` (player-playfield)
- Check bit 7 for collision
- Clear with `sta CXCLR`
- See [10_Collision_Detection.md](references/10_Collision_Detection.md) for collision register details

**Add sound:**
- Set AUDC (waveform), AUDF (frequency), AUDV (volume)
- Update each frame for effects
- See [11_Sound_and_Music.md](references/11_Sound_and_Music.md) for audio channels and waveforms

**Add score display:**
- Use BCD for scoring: `sed` mode, `adc #1`
- Display with playfield or sprites
- See [13_Advanced_Graphics_Techniques.md](references/13_Advanced_Graphics_Techniques.md) for 6-digit score displays

## Best Practices

**Performance:**
- **CRITICAL**: Pre-calculate in VBLANK, not during visible screen - complex math in kernel will cause multi-scanline iterations
- Build lookup tables in RAM during VBLANK for kernel to use
- Use zero-page RAM ($80-$FF) for speed (4 cycles vs 3 cycles)
- Unroll loops in tight kernels when possible
- Count cycles in critical sections - kernel must stay under 76 cycles per scanline

**Debugging:**
- Check .lst file for cycle counts
- Use .sym file to verify addresses
- Color COLUBK different per frame section to visualize timing
- Simplify kernel if graphics glitch (timing issue)

**Code Organization:**
- Separate game logic (VBLANK/overscan) from display (kernel)
- Use macros from macro.h (CLEAN_START, VERTICAL_SYNC, etc.)
- Comment cycle-critical sections
- Keep kernels simple - prefer 2-line kernels for complex graphics

## Common Issues

**Wrong total scanlines (not 262 for NTSC):** Most common cause is kernel doing too much work per iteration. If each loop iteration takes >76 cycles, it spans multiple scanlines. Solution: Pre-calculate data during VBLANK and use lookup tables in kernel. Check .lst file for cycle counts.

**Graphics flickering:** Timing issue in kernel, missing WSYNC, or too many cycles per scanline

**Sprites not appearing:** Check RESP0/1 timing, verify GRP0/1 updates, ensure colors set

**Collision not working:** Forgot CXCLR, reading wrong register, or objects don't overlap

**ROM won't assemble:** Missing includes, org directive wrong, or exceeds 4KB (need bank switching)

**Kernel too slow:** If doing math/logic in visible kernel (lsr/asl/adc chains, multiple branches), move to VBLANK. Use lookup tables stored in RAM for kernel efficiency.

## Output Format

Always generate complete, working .asm files that:
- Start with `processor 6502`
- Include vcs.h, macro.h, tia_constants.h and color.h
- Define variables at $80
- Implement full frame structure (VSYNC, VBLANK, kernel, overscan)
- Include interrupt vectors at $FFFC
- Are ready to compile with dasm and run in Stella

For modifications, preserve existing structure and timing while implementing requested changes.
