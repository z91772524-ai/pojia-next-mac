---
name: shadowtrace-artifact-triage
description: Perform bounded passive triage of CTF files using inventory, hashes, text excerpts, and printable strings.
---

# ShadowTrace Artifact Triage

Start with the least invasive evidence available.

## First pass

1. Use `list_artifacts` to establish names, sizes, and extensions.
2. Hash decisive files with `hash_file`.
3. Use `extract_strings` for binary or unknown formats.
4. Use `read_text_excerpt` only for bounded text inspection.
5. Identify the smallest next tool that can confirm the leading hypothesis.

## Output shape

For every important artifact, record:

- relative path;
- size and SHA-256;
- observed format;
- decisive strings or headers;
- fact versus hypothesis;
- next verification action.

Do not execute attachments merely because their extension appears familiar.

