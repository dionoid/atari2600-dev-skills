# Atari 2600 Development Skill for Claude Code

Expert 6502 assembly programming skill for creating Atari 2600 games with Claude Code. This skill provides comprehensive knowledge of the TIA chip, memory constraints, cycle-accurate timing, and classic game programming techniques.

## Features

- **Complete 6502 Assembly Code Generation**: Create working Atari 2600 games from natural language descriptions
- **Hardware Expertise**: Deep knowledge of TIA registers, RIOT timers, memory mapping, and NTSC/PAL timing
- **Build Automation**: Python scripts for compiling with dasm and launching in Stella emulator
- **Project Templates**: Pre-configured project structure with vcs.h and macro.h includes
- **Reference Documentation**: Complete guides for registers, timing, memory layout, and code patterns
- **Cycle-Accurate Code**: Ensures proper 262 scanline NTSC timing and 76 cycles/scanline limits

## Installation

### Prerequisites

Install the required tools:

**macOS:**
```bash
brew install dasm
brew install --cask stella
```

**Linux:**
```bash
sudo apt-get install dasm stella
# or
sudo pacman -S dasm stella
```

**Windows:**
- Download dasm from [dasm-assembler.github.io](http://dasm-assembler.github.io/)
- Download Stella from [stella-emu.github.io](https://stella-emu.github.io/)

### Install the Skill

**Option 1: Install from .skill file (Recommended)**

```bash
# Download the latest release
curl -L https://github.com/dionoid/atari2600-dev-skills/releases/latest/download/atari2600-dev.skill -o atari2600-dev.skill

# Install in Claude Code
/plugin install atari2600-dev.skill
```

**Option 2: Project-local installation**

Copy the skill to your project's `.claude/skills/` directory:

```bash
# Clone this repository
git clone https://github.com/dionoid/atari2600-dev-skills.git

# Copy to your project
mkdir -p .claude/skills
cp -r atari2600-dev-skills/skills/atari2600-dev .claude/skills/
```

**Option 3: Global installation**

For use across all projects:

```bash
# Clone this repository
git clone https://github.com/dionoid/atari2600-dev-skills.git

# Install globally
mkdir -p ~/.claude/skills
cp -r atari2600-dev-skills/skills/atari2600-dev ~/.claude/skills/
```

## Quick Start

After installation, the skill automatically activates when you mention Atari 2600 development:

```
> Create a simple Atari 2600 game with a bouncing ball
```

```
> Build a Pong clone for Atari 2600
```

```
> Generate an Atari 2600 rainbow color demo
```

The skill will:
1. Generate complete 6502 assembly code
2. Create proper project structure
3. Provide build commands
4. Ensure correct NTSC timing (262 scanlines)

## Project Structure

When using the skill's `create_project.py` script, you get:

```
your-game/
├── src/
│   └── main.asm          # Main source file
├── include/
│   ├── vcs.h             # TIA/RIOT register definitions
│   └── macro.h           # Helpful macros (CLEAN_START, VERTICAL_SYNC, etc.)
└── build/                # Output directory
    ├── game.a26          # ROM file
    ├── game.lst          # Assembly listing with cycle counts
    └── game.sym          # Symbol table
```

## Scripts

The skill includes automation scripts:

**Build and Run:**
```bash
python skills/atari2600-dev/scripts/build_and_run.py src/main.asm
```
- Assembles with dasm
- Generates .a26 ROM file
- Launches in Stella automatically

**Create New Project:**
```bash
python skills/atari2600-dev/scripts/create_project.py my-game
```
- Creates complete project structure
- Includes template code with proper frame structure
- Ready to compile immediately

## Documentation

The skill includes comprehensive reference documentation.

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly with real examples
5. Submit a pull request

## Resources

- [AtariAge Forums](https://atariage.com/forums/)
- [Atari 2600 Programming Guide](https://www.randomterrain.com/atari-2600-memories.html)

## Credits

Created for use with [Claude Code](https://claude.com/claude-code) by Anthropic.

Skill framework based on [Agent Skills standard](https://agentskills.io/).

## Version History

### v1.0.0 (2026-01-30)
- Initial release
- Complete 6502 assembly generation
- Build automation scripts
- Comprehensive reference documentation
- Rainbow color demo example
- NTSC timing validation
