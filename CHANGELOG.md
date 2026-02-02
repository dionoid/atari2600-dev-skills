# Changelog

All notable changes to the Atari 2600 Development Skill will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-01-30

### Added
- Initial release of Atari 2600 development skill
- Complete 6502 assembly code generation with TIA chip knowledge
- Build automation scripts:
  - `build_and_run.py` - Compile with dasm and launch in Stella
  - `create_project.py` - Generate new project structure
- Comprehensive reference documentation.

### Technical Details
- Ensures proper frame structure (3 + 37 + 192 + 30 scanlines)
- Hardware constraint awareness (128 bytes RAM, 76 cycles/scanline)

[1.0.0]: https://github.com/dionoid/atari2600-skills/releases/tag/v1.0.0
