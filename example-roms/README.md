
# Headless Stella

```
cd example-roms

xvfb-run -a -s "-screen 0 1280x720x24" stella -userdir ./example-roms -debug ./example-roms/amoeba-jump.bin -dbg.logexec 1
```