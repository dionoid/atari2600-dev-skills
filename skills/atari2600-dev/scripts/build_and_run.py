#!/usr/bin/env python3
"""
Build and run Atari 2600 assembly code with dasm and Stella emulator.

Usage:
    python build_and_run.py <source.asm> [output.a26]

Requirements:
    - dasm assembler (install via: brew install dasm or apt-get install dasm)
    - Stella emulator (install via: brew install --cask stella or download from stella-emu.github.io)
"""

import sys
import subprocess
import os
from pathlib import Path

def find_stella():
    """Find Stella emulator executable."""
    # Common Stella locations
    locations = [
        "/Applications/Stella.app/Contents/MacOS/Stella",  # macOS
        "/usr/bin/stella",  # Linux
        "/usr/local/bin/stella",  # Linux/macOS homebrew
        "stella",  # In PATH
    ]

    for loc in locations:
        if os.path.exists(loc) or subprocess.run(["which", loc], capture_output=True).returncode == 0:
            return loc

    return None

def build_and_run(source_file, output_file=None):
    """Build assembly file with dasm and run in Stella."""
    source_path = Path(source_file).resolve()

    if not source_path.exists():
        print(f"Error: Source file '{source_file}' not found")
        return False

    # Determine output filename
    if output_file is None:
        # Output to build/ directory if it exists, otherwise same as source
        build_dir = source_path.parent.parent / 'build'
        if build_dir.exists():
            output_file = build_dir / source_path.with_suffix('.a26').name
        else:
            output_file = source_path.with_suffix('.a26')
    else:
        output_file = Path(output_file).resolve()

    # Build with dasm (run from source file's directory to handle relative includes)
    print(f"🔨 Assembling {source_path.name} with dasm...")

    dasm_cmd = [
        "dasm",
        source_path.name,
        f"-o{output_file}",
        "-f3",  # Output format (3 = raw binary)
        "-v0",  # Verbosity (0 = errors only)
        f"-l{output_file.with_suffix('.lst')}",  # Generate listing file
        f"-s{output_file.with_suffix('.sym')}"   # Generate symbol file
    ]

    try:
        # Run dasm from the source file's directory
        result = subprocess.run(dasm_cmd, capture_output=True, text=True, cwd=source_path.parent)

        if result.returncode != 0:
            print(f"❌ Assembly failed:")
            print(result.stderr)
            print(result.stdout)
            return False

        print(f"✅ Assembly successful: {output_file}")

        # Show any warnings
        if result.stdout:
            print(result.stdout)

    except FileNotFoundError:
        print("❌ Error: dasm assembler not found")
        print("Install with: brew install dasm (macOS) or apt-get install dasm (Linux)")
        return False

    # Run in Stella
    stella_path = find_stella()

    if stella_path is None:
        print("⚠️  Stella emulator not found. ROM built successfully but cannot launch.")
        print("Install with: brew install --cask stella (macOS)")
        print(f"Or manually run: stella {output_file}")
        return True

    print(f"🎮 Launching {output_file.name} in Stella...")

    try:
        # Launch Stella in background
        subprocess.Popen([stella_path, str(output_file)],
                        stdout=subprocess.DEVNULL,
                        stderr=subprocess.DEVNULL)
        print("✅ Stella launched successfully")
        return True

    except Exception as e:
        print(f"❌ Error launching Stella: {e}")
        print(f"Try manually: {stella_path} {output_file}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python build_and_run.py <source.asm> [output.a26]")
        sys.exit(1)

    source = sys.argv[1]
    output = sys.argv[2] if len(sys.argv) > 2 else None

    success = build_and_run(source, output)
    sys.exit(0 if success else 1)
