---
name: shadowtrace-ctf-workspace
description: Resume or initialize an evidence-first CTF workspace using explicit state files and reproducible checkpoints.
---

# ShadowTrace CTF Workspace

Use this pack when a task mentions a CTF, challenge attachment, flag, sandbox,
or an existing challenge directory.

## Workflow

1. Inspect the workspace with `workspace_status`.
2. Read existing state files before proposing a new path.
3. Inventory artifacts without executing them.
4. Record facts separately from hypotheses.
5. Choose one narrow proof path and define its success signal.
6. Update the state only after evidence changes.

## State contract

- `progress.md`: current phase, verified work, next action.
- `findings.md`: evidence-backed findings with confidence.
- `task_plan.md`: ordered and checkable tasks.
- `notes.md`: hypotheses and discarded ideas.
- `references/project-state.md`: target, services, hashes, constraints.

Never claim completion from a comment or an unexecuted payload. A solution needs
an artifact, a deterministic solver, or a reproducible command sequence.

