---
name: shadowtrace-binary-protection
description: Identify packers, integrity checks, opaque control flow, and protected import resolution.
---

# Binary Protection

Measure section entropy and entry-point behavior, identify protection signatures,
then plan a dump and import-recovery checkpoint. Use `die`, `binwalk`, `upx`,
`scylla`, and debugger observations. Verify the recovered image by re-parsing it
and reproducing one original behavior.
