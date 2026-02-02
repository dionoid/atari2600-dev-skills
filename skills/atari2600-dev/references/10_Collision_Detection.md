# Collision Detection

The TIA hardware automatically detects when any of the six objects (players, missiles, ball and playfield) overlap.  It sets one‑bit latches that you can read during vertical blank to determine collisions.

## Collision Registers Overview

Collision status is reported in eight read‑only registers:

| Register | Bits 7–6 | Meaning |
|---|---|---|
| `CXM0P` | **D7** | Missile 0 hits player 1 |
|         | **D6** | Missile 0 hits player 0 |
| `CXM1P` | **D7** | Missile 1 hits player 0 |
|         | **D6** | Missile 1 hits player 1 |
| `CXP0FB` | **D7** | Player 0 hits ball |
|         | **D6** | Player 0 hits playfield |
| `CXP1FB` | **D7** | Player 1 hits ball |
|         | **D6** | Player 1 hits playfield |
| `CXM0FB` | **D7** | Missile 0 hits ball |
|         | **D6** | Missile 0 hits playfield |
| `CXM1FB` | **D7** | Missile 1 hits ball |
|         | **D6** | Missile 1 hits playfield |
| `CXBLPF` | **D7** | Ball hits playfield |
|         | **D6** | (unused) |
| `CXPPMM` | **D7** | Player 1 hits player 0 |
|         | **D6** | Missile 1 hits missile 0 |

Bits 5–0 are undefined and should be ignored.  Each latch remains set until cleared.

## Player-to-Player Collisions

When two players overlap, bit 7 of `CXPPMM` is set.  Because players can be duplicated via `NUSIZx`, a collision may occur between any copy of the sprites.  To handle this, read the register during vertical blank and then clear all collision latches.  For example:

```asm
    lda CXPPMM
    bmi .playersCollided  ; bit7 is negative flag
    ; ...
.playersCollided:
    ; handle player collision
    lda #0
    sta CXCLR             ; clear all collisions
```

## Player-to-Playfield Collisions

Bits in `CXP0FB` and `CXP1FB` report collisions between each player and the playfield.  Bit 6 indicates a player–playfield hit; bit 7 indicates a player–ball hit.  Use these to detect when a character hits a wall or lands on a platform.  Clear the latches with `CXCLR` after processing.

## Missile and Ball Collisions

Missiles share the collision registers `CXM0P`, `CXM1P`, `CXM0FB` and `CXM1FB`.  Each register’s bits indicate missile collisions with players, playfield or ball respectively.  The `CXBLPF` register reports ball–playfield collisions.  As with players, the latches are set whenever any copy of the missile collides; treat them as “any hit” indicators.

## Collision Clearing and Timing

Collision latches persist until cleared.  You should:

* Read collision registers during **vertical blank** or **overscan**, not during the kernel.  This ensures that collisions from the previous frame have all been latched and that reading them doesn’t steal cycles from your drawing routine.
* Clear latches by writing any value to `CXCLR` after processing collisions.  If you forget to clear them, old collisions will remain set and trigger false positives.

Be aware that objects disabled via `VBLANK` or with their graphics set to zero will not generate collisions.  Therefore, collisions only occur in the visible kernel.
