# Input and Collision

The RIOT chip provides I/O ports for reading controllers and console switches. The TIA provides hardware collision detection between all six on-screen objects. Both should be read during VBLANK or overscan to avoid stealing cycles from the kernel.

## 1. Joystick Input (SWCHA)

Port A of the RIOT (`SWCHA`, read at `$0280`) carries joystick direction signals for both players. Bits are **active-low**: 0 = pressed, 1 = released.

### SWCHA Bit Layout

| Bit | Player | Direction |
|-----|--------|-----------|
| D7 | P0 | Right |
| D6 | P0 | Left |
| D5 | P0 | Down |
| D4 | P0 | Up |
| D3 | P1 | Right |
| D2 | P1 | Left |
| D1 | P1 | Down |
| D0 | P1 | Up |

### Reading Joystick Example

```asm
; Read P0 joystick during VBLANK
    lda SWCHA
    and #%00010000    ; test P0 Up (D4)
    beq .p0Up         ; branch if pressed (bit=0)
    lda SWCHA
    and #%00100000    ; test P0 Down (D5)
    beq .p0Down
    lda SWCHA
    and #%01000000    ; test P0 Left (D6)
    beq .p0Left
    lda SWCHA
    and #%10000000    ; test P0 Right (D7)
    beq .p0Right
```

**Efficient pattern** — read once, test multiple bits:

```asm
    lda SWCHA
    asl               ; D7 (P0 Right) -> Carry
    bcc .p0Right
    asl               ; D6 (P0 Left) -> Carry
    bcc .p0Left
    asl               ; D5 (P0 Down) -> Carry
    bcc .p0Down
    asl               ; D4 (P0 Up) -> Carry
    bcc .p0Up
```

### Data Direction Register

`SWACNT` (`$0281`) configures Port A pin directions. For standard joysticks, leave it at `$00` (all inputs). Only change this for driving-controller or keyboard-controller hardware that requires output pins.

## 2. Fire Buttons (INPT4, INPT5)

Fire buttons are read through TIA input ports, not the RIOT:

| Address | Register | Player |
|---------|----------|--------|
| `$0C` | `INPT4` | P0 fire button |
| `$0D` | `INPT5` | P1 fire button |

- **D7 = 1**: Button NOT pressed
- **D7 = 0**: Button pressed

```asm
    lda INPT4
    bmi .notFiring    ; D7=1 means not pressed (N flag clear after BMI)
    ; button is pressed — fire!
.notFiring:
```

### Latching Mode

`VBLANK` bit D6 controls input latching:
- D6=0 (default): Inputs are read in real-time.
- D6=1: Once a button press sets D7=0, it stays latched until `VBLANK` D6 is written back to 0.

Latching is useful for detecting button presses that happen during the kernel when you cannot poll inputs.

## 3. Console Switches (SWCHB)

Port B of the RIOT (`SWCHB`, read at `$0282`) provides console switch state. These are active-low where 0 = pressed/active:

| Bit | Name | Function |
|-----|------|----------|
| D7 | P1 Difficulty | 0 = Expert (A), 1 = Novice (B) |
| D6 | P0 Difficulty | 0 = Expert (A), 1 = Novice (B) |
| D3 | Color/BW | 0 = B&W mode, 1 = Colour mode |
| D1 | Select | 0 = Select pressed |
| D0 | Reset | 0 = Reset pressed |

Bits D5, D4, D2 are unused.

```asm
; Check for Reset switch
    lda SWCHB
    lsr               ; D0 (Reset) -> Carry
    bcc .resetPressed ; carry clear = bit was 0 = pressed

; Check for Select switch
    lda SWCHB
    and #%00000010    ; D1 = Select
    beq .selectPressed

; Check P0 difficulty
    lda SWCHB
    and #%01000000    ; D6 = P0 Difficulty
    beq .expertMode   ; 0 = Expert (A position)
```

`SWBCNT` (`$0283`) is the data direction register for Port B. Leave it at `$00` (hardwired as inputs on the console).

## 4. Paddle Controllers

Paddles use analog inputs read through dumped ports INPT0–INPT3:

| Address | Register | Paddle |
|---------|----------|--------|
| `$08` | `INPT0` | Paddle 0 (P0 left) |
| `$09` | `INPT1` | Paddle 1 (P0 right) |
| `$0A` | `INPT2` | Paddle 2 (P1 left) |
| `$0B` | `INPT3` | Paddle 3 (P1 right) |

### Reading Paddles

1. Set `VBLANK` D7=1 to dump (ground) the capacitors.
2. Wait a few scanlines for discharge.
3. Set `VBLANK` D7=0 to begin charging.
4. Poll `INPTn` D7 each scanline — it reads 0 while charging, flips to 1 when charged.
5. The number of scanlines until D7=1 gives the paddle position.

Because this process spans many scanlines, perform it across the VBLANK/kernel boundary or dedicate a frame to reading paddles.

## 5. Debouncing

Mechanical switches produce rapid on/off transitions (bounce) when pressed. Debounce by tracking a two-frame history:

```asm
; Debounce pattern for fire button
    lda INPT4
    asl               ; D7 -> Carry
    rol FireCurrent   ; shift current state into bit 0
    lda FireCurrent
    and #%00000011    ; look at last 2 frames
    cmp #%00000001    ; was 1 (not pressed), now 0 (pressed)?
    bne .noNewPress
    ; New press detected!
.noNewPress:
```

This prevents repeated triggers from switch bounce and ensures a single press is processed once.

## 6. Collision Detection Hardware

The TIA automatically detects pixel-level overlap between any two of the six objects (P0, P1, M0, M1, BL, PF) during the visible kernel. Collision results are stored in 8 read-only registers containing 15 collision latches.

### Collision Registers

| Address | Register | D7 | D6 |
|---------|----------|----|----|
| `$00` | `CXM0P` | M0 ↔ P1 | M0 ↔ P0 |
| `$01` | `CXM1P` | M1 ↔ P0 | M1 ↔ P1 |
| `$02` | `CXP0FB` | P0 ↔ PF | P0 ↔ BL |
| `$03` | `CXP1FB` | P1 ↔ PF | P1 ↔ BL |
| `$04` | `CXM0FB` | M0 ↔ PF | M0 ↔ BL |
| `$05` | `CXM1FB` | M1 ↔ PF | M1 ↔ BL |
| `$06` | `CXBLPF` | BL ↔ PF | (always 0) |
| `$07` | `CXPPMM` | P0 ↔ P1 | M0 ↔ M1 |

**Bits D5-D0 are indeterminate** and must not be used. Only test D7 and D6.

### Collision Matrix Quick Reference

To find the register and bit for any pair of objects:

|  | P0 | P1 | M0 | M1 | PF | BL |
|---|---|---|---|---|---|---|
| **P0** | — | CXPPMM D7 | CXM0P D6 | CXM1P D6 | CXP0FB D7 | CXP0FB D6 |
| **P1** | CXPPMM D7 | — | CXM0P D7 | CXM1P D7 | CXP1FB D7 | CXP1FB D6 |
| **M0** | CXM0P D6 | CXM0P D7 | — | CXPPMM D6 | CXM0FB D7 | CXM0FB D6 |
| **M1** | CXM1P D6 | CXM1P D7 | CXPPMM D6 | — | CXM1FB D7 | CXM1FB D6 |
| **PF** | CXP0FB D7 | CXP1FB D7 | CXM0FB D7 | CXM1FB D7 | — | CXBLPF D7 |
| **BL** | CXP0FB D6 | CXP1FB D6 | CXM0FB D6 | CXM1FB D6 | CXBLPF D7 | — |

### Reading and Clearing Collisions

- Collision latches are **set** when objects overlap during the visible kernel. Objects that are disabled (GRP=0, ENAM=0) or blanked via VBLANK do not generate collisions.
- Latches **persist** until explicitly cleared. A latch set on frame N will still read as set on frame N+1 if not cleared.
- **Clear** all latches by writing any value to `CXCLR` (`$2C`).

### Standard Collision Handling Pattern

```asm
; During VBLANK or overscan — after the kernel has drawn the frame
    ; Check player-to-playfield collision
    lda CXP0FB
    bmi .playerHitWall    ; D7 = P0-PF collision

    ; Check player-to-player collision
    lda CXPPMM
    bmi .playersCollided  ; D7 = P0-P1 collision

    ; Check missile-to-player collision (bullet hit)
    lda CXM0P
    bmi .m0HitP1          ; D7 = M0-P1
    asl                   ; shift D6 into D7
    bmi .m0HitP0          ; (now testing original D6)

    jmp .noCollision

.playerHitWall:
    ; Handle wall collision (stop movement, bounce, etc.)
    jmp .doneCollisions

.playersCollided:
    ; Handle player-player collision
    jmp .doneCollisions

.m0HitP1:
    ; Handle missile 0 hitting player 1
    lda #0
    sta ENAM0             ; disable missile after hit
    jmp .doneCollisions

.m0HitP0:
    ; Missile 0 hit its own player (usually ignored)

.noCollision:
.doneCollisions:
    sta CXCLR             ; ALWAYS clear collision latches after reading
```

**Critical**: Always write `sta CXCLR` after processing collisions. Forgetting this is one of the most common bugs — old collision flags persist and cause false positives on subsequent frames.

See [01_Architecture_and_Memory_Map.md] for the complete register map and [05_Sprites_Positioning_and_Motion.md] for sprite positioning.
