; TV modes
NTSC = 0
PAL = 1
PAL60 = 2

    IFNCONST TV_MODE
TV_MODE = NTSC
    ENDIF

; Scanline counts per TV mode
    IF TV_MODE == NTSC || TV_MODE == PAL60
VBLANK_LINES    = 40
KERNEL_LINES    = 192
OVERSCAN_LINES  = 30
    ELSE ; PAL
VBLANK_LINES    = 48
KERNEL_LINES    = 228
OVERSCAN_LINES  = 36
    ENDIF

; Color definitions per TV mode
    IF TV_MODE == NTSC
GREY           = $00
YELLOW         = $10
ORANGE         = $20
BROWN          = $20
RED_ORANGE     = $30
RED            = $40
PURPLE         = $50
VIOLET         = $60
INDIGO         = $70
BLUE           = $80
BLUE2          = $90
TURQUOISE      = $A0
CYAN           = $B0
GREEN          = $C0
YELLOW_GREEN   = $D0
OCHRE_GREEN    = $E0
OCHRE          = $F0
    ELSE ; PAL or PAL60
GREY           = $00
YELLOW         = $20   ; no real equivalent
ORANGE         = $40
BROWN          = $40   ; brown is darker on PAL displays
RED_ORANGE     = $40
RED            = $60   ; red is darker on PAL displays
PURPLE         = $80
VIOLET         = $A0
INDIGO         = $C0
BLUE           = $D0
BLUE2          = $B0
TURQUOISE      = $90
CYAN           = $70
GREEN          = $50
YELLOW_GREEN   = $30
OCHRE_GREEN    = $30   ; no real equivalent
OCHRE          = $20   ; no real equivalent 
    ENDIF

; Common colors (same in all TV modes)
BLACK          = $00
WHITE          = $0E ; bright white