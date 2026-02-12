# Atari 2600 Development Skill for Claude Code

Expert 6502 assembly programming skill for creating Atari 2600 games with Claude Code. This skill provides comprehensive knowledge of the TIA chip, memory constraints, cycle-accurate timing, and classic game programming techniques.

## Features

- **Complete 6502 Assembly Code Generation**: Create working Atari 2600 games from natural language descriptions
- **Hardware Expertise**: Deep knowledge of TIA registers, RIOT timers, memory mapping, and NTSC/PAL timing
- **Build Automation**: Python scripts for compiling with dasm and validating in headless Stella
- **Project Templates**: Pre-configured project structure with vcs.h and macro.h includes
- **Reference Documentation**: Complete guides for registers, timing, memory layout, and code patterns
- **Cycle-Accurate Code**: Ensures proper 262 scanline NTSC timing and 76 cycles/scanline limits

## Prerequisites

This project is designed to run inside a **dev container**. The dev container includes all required tools pre-installed:

- **dasm** assembler
- Headless(!) **Stella** emulator (with logexec patch) running via `xvfb-run`
- **Python 3** for build/validation scripts

For local dev containers you need [Docker Desktop](https://www.docker.com/products/docker-desktop/) (or a compatible runtime like Rancher Desktop or Podman) installed and running. GitHub Codespaces runs in the cloud and doesn't require Docker locally.

### Opening in a Dev Container

**VS Code:**
1. Install the [Dev Containers](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers) extension
2. Open this repository
3. When prompted, click "Reopen in Container" (or use the command palette: `Dev Containers: Reopen in Container`)

**PyCharm Professional:**
1. Open the repository
2. PyCharm will detect the `.devcontainer/devcontainer.json` and offer to open in a dev container
3. Alternatively, go to **File > Remote Development > Dev Containers**

**GitHub Codespaces:**
1. Click the green "Code" button on the repository
2. Select "Codespaces" and create a new codespace

No manual installation of dasm, Stella, or other dependencies is required.

## Skill Setup

No registration/setup needed, because the dev container automatically creates a symlink on first start via `postCreateCommand`:

```
.claude/skills/atari2600-dev -> ../../skills/atari2600-dev
```

Claude Code picks it up automatically from `.claude/skills/`.

## Quick Start

After installation, the skill automatically activates when you mention Atari 2600 development:

```
> Generate an Atari 2600 rainbow color demo
```

```
> Create a simple Atari 2600 game with a spaceship at the bottom of the screen, which you can move left and right with your joystick. Asteroids come falling from above towards your spaceship and should be avoided by the player.
```

The skill will:
1. Generate complete 6502 assembly code
2. Create proper project structure
3. Build the ROM and validate scanline timing in headless Stella
4. Ensure correct timings for NTSC (262 scanlines) or PAL (312 scanlines)

## Project Structure

When using the skill's `create_project.py` script, you get:

```
your-game/
├── src/
│   └── main.asm          # Main source file
├── include/
│   ├── vcs.h             # TIA/RIOT register definitions
│   ├── macro.h           # Helpful macros (CLEAN_START, VERTICAL_SYNC, etc.)
│   └── tv_modes.h        # NTSC/PAL timing constants
└── build/                # Output directory
    ├── main.a26          # ROM file
    ├── main.lst          # Assembly listing with cycle counts
    ├── main.sym          # Symbol table
    └── main.script       # Stella debug script for validation
```

## Scripts

The skill includes automation scripts:

**Build and Validate:**
```bash
python3 skills/atari2600-dev/scripts/build_and_run.py src/main.asm
```
- Assembles with dasm (`-f3` format)
- Creates or uses a debug script named `<romname>.script` in the build directory
- Runs the ROM in headless Stella with the command:
  ```bash
  xvfb-run -a stella -userdir <build-dir> -debug <rom>.a26 -dbg.logexec 1
  ```
- **IMPORTANT:** The `-dbg.logexec 1` flag is always required for automated testing
- Validates scanline count from `<romname>.script.output.txt` (expects 262 for NTSC)
- Reports pass/fail with scanline count and RAM state

**Create New Project:**
```bash
python3 skills/atari2600-dev/scripts/create_project.py my-game
```
- Creates complete project structure
- Includes template code with proper frame structure
- Ready to compile immediately

## Documentation

The skill includes comprehensive reference documentation in the [references/](skills/atari2600-dev/references/) directory:

### Core Topics
- **01 - Architecture and Memory Map**: 6507 CPU, TIA, RIOT, memory map, register addresses
- **02 - Frame Structure and Timing**: VSYNC/VBLANK/kernel/overscan, cycle budgets, NTSC vs PAL
- **03 - Toolchain and Stella Debugger**: dasm assembler, Stella debugger commands, .script format

### Graphics & Display
- **04 - Graphics and Playfield**: Colour system, PF registers, playfield timing, asymmetric PF
- **05 - Sprites, Positioning and Motion**: Players, missiles, ball, NUSIZ, SetHorizPos, HMOVE, VDEL

### Input & Game Logic
- **06 - Input and Collision**: Joysticks, fire buttons, console switches, collision registers
- **07 - Sound and Music**: AUDC/AUDF/AUDV, distortion types, frequency tables, music
- **08 - Game Logic and Timers**: RIOT timer, frame counters, state machines, RNG, BCD scoring

### Advanced Topics
- **09 - Advanced Techniques**: 48-pixel sprites, score displays, multiplexing, bank switching
- **10 - Common Patterns and Gotchas**: Kernel stability, common bugs, debugging workflow
- **11 - Complete Examples**: Full working programs: rainbow, sprite, maze, sound demo
- **12 - Reference and Cheat Sheets**: Register tables, 6502 instructions, colour chart, memory map

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with real examples
5. Submit a pull request

## Credits

Created for use with [Claude Code](https://claude.com/claude-code) by Anthropic.

## Version History

### v1.0.0 (2026-01-30)
- Initial release
- Complete 6502 assembly generation
- Build automation scripts
- Comprehensive reference documentation
- Rainbow color demo example
- NTSC and PAL timing validation
