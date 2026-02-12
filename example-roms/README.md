
# Headless Stella

**Correct command to run Stella with debug scripts:**

```bash
cd example-roms

xvfb-run -a -s "-screen 0 1280x720x24" stella -userdir ./example-roms -debug ./example-roms/amoeba-jump.bin -dbg.logexec 1
```

**Important notes:**
- **ALWAYS** include `-dbg.logexec 1` for automated testing (writes output to file)
- Debug script must be named `amoeba-jump.script` and placed in the `-userdir` directory
- Stella automatically loads the script based on ROM name
- Output is written to `amoeba-jump.script.output.txt`
- Do NOT use `-exitlauncher` or pipe scripts - this is not how Stella works