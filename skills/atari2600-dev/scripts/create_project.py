#!/usr/bin/env python3
"""
Create a new Atari 2600 project with proper structure and includes.

Usage:
    python create_project.py <project-name>

IMPORTANT: Run this script from your workspace root directory.
The project will be created in the current directory.

Creates:
    project-name/
    ├── src/
    │   └── main.asm          # Main source file
    ├── include/
    │   ├── vcs.h             # TIA/RIOT register definitions
    │   ├── macro.h           # Helpful macros
    │   └── tv_modes.h        # TV mode constants
    └── build/                # Output directory for ROMs
"""

import sys
import os
import shutil
from pathlib import Path

MAIN_ASM = """    
    processor 6502
    include "../include/vcs.h"
    include "../include/macro.h"
    include "../include/tv_modes.h"

TV_MODE = NTSC

;===============================================================================
; Variables
;===============================================================================
    SEG.U Variables
    ORG $80

; Add your variables here (you have 128 bytes total)
frameCounter    ds 1    ; Frame counter


;===============================================================================
; ROM Code
;===============================================================================
    SEG Code
    ORG $f000 ; use $f800 for a 2K ROM and $f000 for 4K

;-------------------------------------------------------------------------------
; Startup
;-------------------------------------------------------------------------------
Reset:
    CLEAN_START         ; Initialize system

    ; Initialize variables
    lda #0
    sta frameCounter

;-------------------------------------------------------------------------------
; Main Loop
;-------------------------------------------------------------------------------
MainLoop:
    ; Increment frame counter
    inc frameCounter

;---------------------------------------
; Vertical Sync and Blank
;---------------------------------------
    TIMER_SETUP VBLANK_LINES
    VERTICAL_SYNC
    
    ; Game logic goes here
    ; You have time during VBLANK for calculations

    TIMER_WAIT
    
    lda #%00000000
    sta VBLANK ; Turn off VBLANK

;---------------------------------------
; Visible Screen
;---------------------------------------
    ; Set background color
    lda frameCounter    ; Cycle through colors
    sta COLUBK

    ; Draw kernel scanlines
    ldx #KERNEL_LINES
.kernel:
    sta WSYNC           ; Wait for horizontal blank
    dex
    bne .kernel

;---------------------------------------
; Overscan
;---------------------------------------
    lda #%01000010
    sta VBLANK          ; Turn on VBLANK

    TIMER_SETUP OVERSCAN_LINES

    ; Handle controls, score, sound here

    TIMER_WAIT

    ; Jump back to main loop
    jmp MainLoop

;-------------------------------------------------------------------------------
; Interrupt Vectors
;-------------------------------------------------------------------------------
    org $FFFC
    .word Reset         ; Reset vector
    .word Reset         ; BRK vector
"""

def create_project(project_name):
    """Create a new Atari 2600 project directory structure."""
    project_path = Path(project_name)

    # Get the assets directory relative to this script
    script_dir = Path(__file__).parent
    assets_dir = script_dir.parent / "assets"

    # Check if project already exists
    if project_path.exists():
        print(f"Error: Directory '{project_name}' already exists")
        return False

    try:
        # Create directory structure
        project_path.mkdir()
        (project_path / "src").mkdir()
        (project_path / "include").mkdir()
        (project_path / "build").mkdir()

        # Copy include files from assets
        shutil.copy(assets_dir / "vcs.h", project_path / "include" / "vcs.h")
        shutil.copy(assets_dir / "macro.h", project_path / "include" / "macro.h")
        shutil.copy(assets_dir / "tv_modes.h", project_path / "include" / "tv_modes.h")
        
        # Create main.asm file
        (project_path / "src" / "main.asm").write_text(MAIN_ASM)

        # Create .gitignore
        gitignore = """# Build outputs
build/
*.a26
*.bin
*.lst
*.sym

# Editor files
.vscode/
.idea/
*.swp
*~
"""
        (project_path / ".gitignore").write_text(gitignore)

        print(f"✅ Project '{project_name}' created successfully!")
        print(f"\nProject structure:")
        print(f"  {project_name}/")
        print(f"  ├── src/")
        print(f"  │   └── main.asm          # Your code here")
        print(f"  ├── include/")
        print(f"  │   ├── vcs.h             # TIA/RIOT registers")
        print(f"  │   └── macro.h           # Helpful macros")
        print(f"  └── build/                # Build output")
        print(f"\nNext steps:")
        print(f"  cd {project_name}")
        print(f"  dasm src/main.asm -f3 -obuild/game.a26")
        print(f"  stella build/game.a26")

        return True

    except Exception as e:
        print(f"Error creating project: {e}")
        return False

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python create_project.py <project-name>")
        sys.exit(1)

    project_name = sys.argv[1]
    success = create_project(project_name)
    sys.exit(0 if success else 1)
