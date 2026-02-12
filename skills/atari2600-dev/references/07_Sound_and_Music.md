# Sound and Music

The TIA contains two identical, independent audio channels. Each channel generates sound using shift registers of various lengths, controlled by three 4-5 bit registers. Despite the simple hardware, careful programming can produce music, sound effects, and even 4-bit sample playback.

## 1. Audio Registers

Each channel has three write-only registers:

| Address | Register | Bits | Function |
|---------|----------|------|----------|
| `$15` | `AUDC0` | D3-D0 (4-bit) | Channel 0 distortion/waveform |
| `$16` | `AUDC1` | D3-D0 (4-bit) | Channel 1 distortion/waveform |
| `$17` | `AUDF0` | D4-D0 (5-bit) | Channel 0 frequency divider (0-31) |
| `$18` | `AUDF1` | D4-D0 (5-bit) | Channel 1 frequency divider (0-31) |
| `$19` | `AUDV0` | D3-D0 (4-bit) | Channel 0 volume (0-15) |
| `$1A` | `AUDV1` | D3-D0 (4-bit) | Channel 1 volume (0-15) |

All registers are latched — values persist until overwritten. Writing 0 to `AUDVx` silences the channel. Changes to `AUDCx` and `AUDFx` take effect immediately.

## 2. Clock Speed and Output Rate

The TIA generates audio by shifting registers at one of two speeds:

| Clock Source | NTSC Rate | PAL Rate |
|-------------|-----------|----------|
| Pixel clock / 114 | 31,440 Hz | 31,200 Hz |
| CPU clock / 114 | 10,480 Hz | 10,400 Hz |

The `AUDCx` distortion value selects which clock is used. A pitch value of `n` in `AUDFx` causes `n` shift opportunities to be skipped, lowering the frequency by a factor of `(n+1)`.

## 3. Distortion/Waveform Reference (AUDCx)

| AUDC | Waveform | Clock | Description |
|------|----------|-------|-------------|
| 0 | Always high | Pixel/114 | Silent (use for 4-bit PCM via volume modulation) |
| 1 | 15-bit pattern | Pixel/114 | Buzzy tone |
| 2 | 465-bit pattern | Pixel/114 | Low rumble |
| 3 | 465-bit pattern | Pixel/114 | Low rumble (variant) |
| **4** | **01 (square)** | **Pixel/114** | **Pure tone — best for melody** |
| **5** | **01 (square)** | **Pixel/114** | **Pure tone (same as 4)** |
| 6 | 31-bit pattern | Pixel/114 | Buzzy square wave |
| 7 | 31-bit pattern | Pixel/114 | Saw-like tone |
| 8 | 511-bit noise | Pixel/114 | White noise (explosions, wind) |
| 9 | 31-bit pattern | Pixel/114 | Saw-like tone (same as 7) |
| 10 | 31-bit pattern | Pixel/114 | Buzzy square wave (same as 6) |
| 11 | Always high | Pixel/114 | Silent (same as 0) |
| **12** | **10 (square)** | **CPU/114** | **Pure tone, lower octave — best for bass** |
| **13** | **10 (square)** | **CPU/114** | **Pure tone, lower octave (same as 12)** |
| 14 | 31-bit pattern | CPU/114 | Buzzy/saw, lower octave |
| 15 | 31-bit pattern | CPU/114 | Saw-like, lower octave |

**For music**: Use AUDC 4 or 5 for melody and AUDC 12 or 13 for bass lines. These produce the cleanest square waves with the most recognisable pitch.

## 4. Frequency Tables for Musical Distortions

### AUDC 4/5 (Pure Tone — Pixel Clock)

| Pitch | NTSC Hz | Note | Cents Off | PAL Hz | Note | Cents Off |
|-------|---------|------|-----------|--------|------|-----------|
| 0 | 15720 | (silent) | | 15600 | (silent) | |
| 1 | 7860 | B8 | -9 | 7800 | B8 | -23 |
| 2 | 5240 | E8 | -11 | 5200 | E8 | -25 |
| 3 | 3930 | B7 | -10 | 3900 | B7 | -23 |
| 4 | 3144 | G7 | +4 | 3120 | G7 | -9 |
| 5 | 2620 | E7 | -11 | 2600 | E7 | -25 |
| 6 | 2245.7 | C#7 | +21 | 2228.6 | C#7 | +8 |
| 7 | 1965 | B6 | -9 | 1950 | B6 | -23 |
| 8 | 1746.7 | A6 | -13 | 1733.3 | A6 | -27 |
| 9 | 1572 | G6 | +4 | 1560 | G6 | -9 |
| 10 | 1429.1 | F6 | +39 | 1418.2 | F6 | +25 |
| 11 | 1310 | E6 | -11 | 1300 | E6 | -25 |
| 12 | 1209.2 | D6 | +49 | 1200 | D6 | +36 |
| 13 | 1122.9 | C#6 | +22 | 1114.3 | C#6 | +8 |
| 14 | 1048 | C6 | +2 | 1040 | C6 | -11 |
| 15 | 982.5 | B5 | -10 | 975 | B5 | -23 |
| 16 | 924.7 | A#5 | -15 | 917.6 | A#5 | -28 |
| 17 | 873.3 | A5 | -14 | 866.7 | A5 | -27 |
| 18 | 827.4 | G#5 | -7 | 821.1 | G#5 | -20 |
| 19 | 786 | G5 | +4 | 780 | G5 | -9 |
| 20 | 748.6 | F#5 | +20 | 742.9 | F#5 | +7 |
| 21 | 714.5 | F5 | +39 | 709.1 | F5 | +26 |
| 22 | 683.5 | F5 | -38 | 678.3 | E5 | +48 |
| 23 | 655 | E5 | -12 | 650 | E5 | -25 |
| 24 | 628.8 | D#5 | +18 | 624 | D#5 | +5 |
| 25 | 604.6 | D5 | +49 | 600 | D5 | +36 |
| 26 | 582.2 | D5 | -16 | 577.8 | D5 | -29 |
| 27 | 561.4 | C#5 | +21 | 557.1 | C#5 | +8 |
| 28 | 542.1 | C#5 | -40 | 537.9 | C5 | +47 |
| 29 | 524 | C5 | +2 | 520 | C5 | -11 |
| 30 | 507.1 | B4 | +45 | 503.2 | B4 | +32 |
| 31 | 491.3 | B4 | -9 | 487.5 | B4 | -23 |

### AUDC 12/13 (Pure Tone — CPU Clock, Lower Octave)

| Pitch | NTSC Hz | Note | Cents Off | PAL Hz | Note | Cents Off |
|-------|---------|------|-----------|--------|------|-----------|
| 0 | 5240 | E8 | -11 | 5200 | E8 | -25 |
| 1 | 2620 | E7 | -11 | 2600 | E7 | -25 |
| 2 | 1746.6 | A6 | -14 | 1733.3 | A6 | -27 |
| 3 | 1310 | E6 | -11 | 1300 | E6 | -25 |
| 4 | 1048 | C6 | +2 | 1040 | C6 | -11 |
| 5 | 873.3 | A5 | -14 | 866.7 | A5 | -27 |
| 6 | 748.6 | F#5 | +20 | 742.9 | F#5 | +7 |
| 7 | 655 | E5 | -12 | 650 | E5 | -25 |
| 8 | 582.2 | D5 | -16 | 577.8 | D5 | -29 |
| 9 | 524 | C5 | +2 | 520 | C5 | -11 |
| 10 | 476.4 | A#4 | +39 | 472.7 | A#4 | +23 |
| 11 | 436.7 | A4 | -13 | 433.3 | A4 | -27 |
| 12 | 403.1 | G4 | +48 | 400 | G4 | +34 |
| 13 | 374.3 | F#4 | +20 | 371.4 | F#4 | +6 |
| 14 | 349.3 | F4 | 0 | 346.7 | F4 | -13 |
| 15 | 327.5 | E4 | -11 | 325 | E4 | -25 |
| 16 | 308.2 | D#4 | -17 | 305.9 | D#4 | -30 |
| 17 | 291.1 | D4 | -16 | 288.9 | D4 | -29 |
| 18 | 275.8 | C#4 | -9 | 273.7 | C#4 | -22 |
| 19 | 262 | C4 | +3 | 260 | C4 | -11 |
| 20 | 249.5 | B3 | +18 | 247.6 | B3 | +5 |
| 21 | 238.2 | A#3 | +37 | 236.4 | A#3 | +24 |
| 22 | 227.8 | A#3 | -40 | 226.1 | A3 | +47 |
| 23 | 218.3 | A3 | -14 | 216.7 | A3 | -27 |
| 24 | 209.6 | G#3 | +15 | 208 | G#3 | +2 |
| 25 | 201.5 | G3 | +47 | 200 | G3 | +34 |
| 26 | 194.1 | G3 | -17 | 192.6 | G3 | -31 |
| 27 | 187.1 | F#3 | +19 | 185.7 | F#3 | +6 |
| 28 | 180.7 | F#3 | -41 | 179.3 | F3 | +45 |
| 29 | 174.7 | F3 | +1 | 173.3 | F3 | -13 |
| 30 | 169 | E3 | +43 | 167.7 | E3 | +30 |
| 31 | 163.8 | E3 | -11 | 162.5 | E3 | -25 |

**Cents**: Positive = sharp, negative = flat. Values within ±10 cents sound in-tune. Choose AUDF values where cents are close to 0.

## 5. White Noise (AUDC 8)

AUDC 8 produces a 511-bit noise pattern, useful for:
- Explosions: Start at high AUDF (0-3), sweep down over frames
- Wind/rain: Mid-range AUDF (8-15) with low volume
- Static: Random AUDF changes each frame

| Pitch | NTSC Hz | Description |
|-------|---------|-------------|
| 0 | 61.5 | Very low rumble |
| 1 | 30.8 | Low rumble |
| 2 | 20.5 | Bass noise |
| 3-31 | 15.4-1.9 | Sub-bass (below audible for higher values) |

## 6. Common Sound Effect Patterns

### Laser/Blaster

```asm
; Play a laser sound on channel 0
; Call during VBLANK, update SoundTimer each frame
PlayLaser:
    lda SoundTimer
    beq .silent
    ; Buzzy square wave, sweep pitch down
    lda #6              ; AUDC: buzzy square
    sta AUDC0
    lda SoundTimer      ; use timer as frequency (sweeps down)
    sta AUDF0
    lda SoundTimer
    sta AUDV0           ; volume fades with pitch
    dec SoundTimer
    rts
.silent:
    lda #0
    sta AUDV0
    rts

; To trigger: lda #15 / sta SoundTimer
```

### Explosion

```asm
; White noise that fades over 15 frames
PlayExplosion:
    lda SoundTimer
    beq .silent
    lda #8              ; AUDC: white noise
    sta AUDC0
    lda #2              ; low frequency = deep boom
    sta AUDF0
    lda SoundTimer
    sta AUDV0
    dec SoundTimer
    rts
.silent:
    lda #0
    sta AUDV0
    rts
```

### Jump Arc

```asm
; Pure tone that sweeps up then down
; JumpPhase: 0=not playing, 1-8=up, 9-16=down
PlayJump:
    lda JumpPhase
    beq .silent
    lda #4              ; AUDC: pure tone
    sta AUDC0
    lda #10
    sta AUDV0
    lda JumpPhase
    cmp #9
    bcs .descending
    ; Ascending: pitch goes up (AUDF decreases)
    eor #$FF            ; invert
    clc
    adc #20             ; base pitch
    jmp .setFreq
.descending:
    sec
    sbc #8              ; offset back to 1-8
    clc
    adc #12             ; start from mid-pitch going down
.setFreq:
    sta AUDF0
    inc JumpPhase
    lda JumpPhase
    cmp #17
    bcc .done
    lda #0
    sta JumpPhase
.silent:
    lda #0
    sta AUDV0
.done:
    rts
```

### Pickup/Coin

```asm
; Short high-pitched chirp, 4 frames
PlayPickup:
    lda SoundTimer
    beq .silent
    lda #4              ; pure tone
    sta AUDC0
    lda #3              ; high pitch
    sta AUDF0
    lda #12
    sta AUDV0
    dec SoundTimer
    rts
.silent:
    lda #0
    sta AUDV0
    rts

; To trigger: lda #4 / sta SoundTimer
```

## 7. Music Implementation

The TIA has no hardware sequencer. Implement music in software using note tables:

```asm
; Note table: pairs of (AUDF value, duration in frames)
; Use $FF as end-of-track marker
MelodyTrack:
    .byte 29, 15       ; C5, quarter note at ~120 BPM
    .byte 23, 15       ; E5
    .byte 19, 15       ; G5
    .byte 14, 30       ; C6, half note
    .byte $FF          ; end marker

; Music player — call once per frame during VBLANK
UpdateMusic:
    lda NoteDuration
    bne .playing
    ; Load next note
    ldx NoteIndex
    lda MelodyTrack,x
    cmp #$FF
    beq .trackDone
    sta AUDF0
    lda #4             ; pure tone
    sta AUDC0
    lda #10
    sta AUDV0
    inx
    lda MelodyTrack,x
    sta NoteDuration
    inx
    stx NoteIndex
    rts
.playing:
    dec NoteDuration
    rts
.trackDone:
    lda #0
    sta NoteIndex      ; loop track
    sta AUDV0
    rts
```

### Tempo Calculation

At 60 Hz (NTSC), frame durations map to musical timing at 120 BPM:
- Whole note = 120 frames
- Half note = 60 frames
- Quarter note = 30 frames
- Eighth note = 15 frames
- Sixteenth note = ~8 frames

For PAL (50 Hz), multiply durations by 5/6 to maintain the same tempo.

### Two-Channel Harmony

Use channel 0 for melody (AUDC 4/5) and channel 1 for bass (AUDC 12/13). Update both channels from separate note tables in your music routine.

## 8. 4-Bit PCM Sample Playback

AUDC values 0 and 11 produce a constant high output. By rapidly changing `AUDVx` (volume) each scanline, you can play back 4-bit PCM audio samples. This requires dedicating CPU time during the kernel to volume updates, so it is typically used only for short samples (title screens, jingles).

See [08_Game_Logic_and_Timers.md] for frame-based timing and [12_Reference_and_Cheat_Sheets.md] for the complete register table.
