
# Headless Stella

**Correct command to run Stella with debug scripts:**

```bash
xvfb-run -a stella -debug -dbg.logexec 1 -dbg.script ./example-roms/debug.script -userdir ./example-roms ./example-roms/amoeba-jump.bin
```

**Important notes:**
- **ALWAYS** include `-dbg.logexec 1` for automated testing (writes output to file)
- Use `-dbg.script <path>` to specify the debug script file to load
- Output is written to `debug.script.output.txt`
- Use `-userdir <dir>` to control where Stella saves output files (screenshots from `saveSnap`, etc.)
- Do NOT use `-exitlauncher` or pipe scripts - this is not how Stella works
