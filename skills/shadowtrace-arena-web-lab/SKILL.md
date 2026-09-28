---
name: shadowtrace-web-lab
description: Structure local Web CTF investigation around routes, parameters, traffic evidence, and single-variable verification.
---

# ShadowTrace Web Lab

Use a request ledger instead of an unstructured payload list.

## Request ledger

For each experiment, capture:

- method and route;
- changed field;
- baseline response signature;
- candidate response signature;
- server-side effect, if any;
- conclusion and confidence.

## Sequence

1. Map served routes and client-visible assets.
2. Establish one clean baseline request.
3. Change one field at a time.
4. Prefer response and state deltas over status-code guesses.
5. Stop repeating a path when it produces no new evidence.
6. Preserve the minimal end-to-end request that proves the finding.

Keep challenge tokens and session material out of shared reports.

