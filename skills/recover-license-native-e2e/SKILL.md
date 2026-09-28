---
name: recover-license-native-e2e
description: Recover software serial, machine-code, card-key, activation, offline-license, and server-issued entitlement flows. Use for keygen, registration, license-file, subscription, or activation tasks where Codex must preserve the original executable and DLL feature path and prove native acceptance, clean-restart persistence, hardware prerequisites, and server-dependent behavior end to end.
---

# Native License Recovery

Recover the complete decision path from license input to original feature execution. Keep the
application's feature implementation in its original EXE, DLL, managed assembly, script bundle,
or service client. Treat a changed label, enabled button, or patched return value as an intermediate
observation rather than completion.

## Start With Evidence

1. Hash the installer, main executable, relevant DLLs, configuration, and accepted/rejected fixtures.
2. Preserve originals and write derived artifacts to a separate workspace.
3. Identify the active runtime before selecting tools: native, .NET, JVM, Python/Nuitka,
   Electron, packed/virtualized, or mixed.
4. Prove one narrow path from machine identity or token input to the final internal entitlement.
5. Initialize the evidence ledger:

```powershell
python scripts/license_evidence.py init WORKDIR --target TARGET
python scripts/license_evidence.py classify WORKDIR --runtime nuitka --authority offline-client --server-role none
```

Read [references/workflow.md](references/workflow.md) before substantial analysis.

## Select the Authorization Profile

- **Offline client**: The client creates or verifies a local serial/license. Recover exact bytes,
  formatting, binding, time policy, cryptography, and permission mapping.
- **Server issued**: The server signs or returns an entitlement while original features remain
  local. Recover the protocol, response parser, refresh and persistence behavior.
- **Hybrid**: Local verification and server state both affect the decision. Trace request order and
  both state machines.
- **Server executed**: The server returns actual feature results or private data. A local backend
  must reproduce that operation; an entitlement-only response does not establish feature parity.

For any networked path, read
[references/server-dependency.md](references/server-dependency.md) before implementing a backend.

## Recover the Decision Chain

Trace these boundaries in order and record exact values:

```text
identity/input -> normalization -> serialization -> checksum/signature/KDF
-> encrypted or signed artifact -> parser -> native verifier
-> internal entitlement -> original feature dispatch
```

Prefer high-level boundary hooks over early instruction-level decompilation. Capture encoding,
case, whitespace, delimiters, field order, numeric formatting, salts, nonces, tags, signature
coverage, clock source, expiry arithmetic, and machine-component selection. Mutate one field at a
time and retain at least one accepted and one rejected vector.

For Python/Nuitka applications, read
[references/nuitka-runtime.md](references/nuitka-runtime.md) and use the bundled runtime executor
when the embedded interpreter remains loaded:

```powershell
python scripts/nuitka_pyexec.py --pid PID --code-file PROBE.py --report TRACE.json
```

## Preserve Original Feature Execution

Prefer compatible license generation, token/backend emulation, public-key substitution, or a
narrow verifier change. Do not replace feature modules with a mock implementation when the
original client or DLL already contains the operation.

Prove all of the following:

1. The original verifier returns the intended internal permission or entitlement.
2. A clean process start reloads the artifact or token and reaches the same state.
3. At least one representative original feature calls its original module, assembly, or DLL.
4. Original artifacts retain their recorded hashes; keep any patched derivative separate.
5. Hardware, driver, configuration, content, and server requirements are listed independently of
   authorization.
6. For a local backend, every required route and server-owned result has parity evidence.

## Enforce the Gates

Record evidence as work progresses:

```powershell
python scripts/license_evidence.py add-fixture WORKDIR --request REQUEST.bin --response LICENSE.bin --expected accepted --label known-good
python scripts/license_evidence.py gate WORKDIR --name native-acceptance --status pass --evidence native-check.json --note "Original verifier returned Full"
python scripts/license_evidence.py verify-integrity WORKDIR
python scripts/license_evidence.py check WORKDIR --profile offline
```

Completion requires the profile-specific gates in
[references/validation-contract.md](references/validation-contract.md). Keep a gate pending or
failed when only UI state is proven, when a clean restart was skipped, when original feature
dispatch was not observed, or when a server still owns unimplemented computation/data.

## Report

Lead with the outcome, then include:

- exact target and derived-artifact hashes;
- recovered transform chain and known-answer vectors;
- native verifier result and clean-restart result;
- representative original feature call evidence;
- server dependency matrix and local-backend coverage;
- remaining hardware, driver, configuration, content, or service prerequisites;
- replay commands and evidence paths.

Never describe an activation as feature-complete solely because a window opened or a permission
label changed.
