# Native License Validation Contract

## Contents

1. Evidence rules
2. Gate definitions
3. Profile requirements
4. Completion report

## 1. Evidence Rules

Use this evidence priority when artifacts conflict:

```text
live runtime behavior
> captured request/response traffic
> actively served assets
> current process configuration
> persisted state
> generated artifacts
> checked-in or extracted source-like files
> comments and dead code
```

Every passing gate must reference a file or directory that exists and is hashed by
`scripts/license_evidence.py`. Prefer JSON traces with exact values and command metadata. Retain
raw bytes separately when text rendering changes encoding or line endings.

## 2. Gate Definitions

### inventory

Pass when the primary target is hashed and relevant original modules/DLLs/configuration are
recorded. Include version, architecture, runtime, and active executable path.

### decision-trace

Pass when evidence follows one real input through parser/normalization to the decisive branch and
internal entitlement store. Name the original functions or offsets used at each step.

### fixture-vectors

Pass when at least one accepted and one rejected request/response or machine-code/license pair are
recorded as exact bytes. The rejected vector should isolate one meaningful variable.

### algorithm-chain

Pass when offline formatting, binding, checksum/signature/KDF/cipher, expiry, and permission
mapping are fully specified and reproduced across fixtures. Include a compatible generator or
deterministic harness.

### protocol-trace

Pass when a full successful server sequence and at least one failure sequence are captured,
including token refresh/polling/download routes used by the selected feature.

### native-acceptance

Pass when the untouched application's original parser and verifier accept the produced artifact or
backend response and assign the intended internal entitlement. A label or button state alone does
not pass.

### clean-restart

Pass when a new process from a reset or isolated baseline loads the produced persistent state and
reaches the same entitlement without inherited memory or stale cache.

### feature-smoke

Pass when at least one representative operation reaches the original feature module, assembly, or
DLL and produces its expected side effect or output. Include module hash and call evidence.

### binary-integrity

Pass when all recorded original artifacts still match baseline hashes. Store patched or rebuilt
derivatives at separate paths and record them with separate hashes.

### server-dependency

Pass when each endpoint used by activation and the selected feature is classified as issuer,
entitlement, configuration, content/data, compute, or unrelated. For offline applications, pass
with evidence that native verification and the selected local feature make no server request.

### backend-parity

Pass when a local backend covers every route and server-owned state/content/computation required by
the selected feature, including refresh, expiry, errors, and clean-start behavior.

### reproducibility

Pass when commands, tool versions, fixture hashes, outputs, and reset steps replay from a clean
baseline. Another operator should be able to reproduce native acceptance and the feature smoke
test without relying on undocumented state.

## 3. Profile Requirements

The evidence script enforces these sets.

### Offline

```text
inventory, decision-trace, fixture-vectors, algorithm-chain,
native-acceptance, clean-restart, feature-smoke, binary-integrity,
server-dependency, reproducibility
```

### Server Issued or Server Executed

```text
inventory, decision-trace, fixture-vectors, protocol-trace,
native-acceptance, clean-restart, feature-smoke, binary-integrity,
server-dependency, backend-parity, reproducibility
```

### Hybrid

Require every gate.

## 4. Completion Report

Use this compact structure:

```markdown
## Outcome
- Authorization profile:
- Native entitlement reached:
- Original feature path executed:
- Local backend coverage:

## Target Integrity
- Original target hash:
- Original module/DLL hashes:
- Derived artifacts and hashes:

## Recovered Chain
- Identity/input:
- Serialization:
- Cryptography/signature:
- Expiry/limits:
- Permission mapping:

## Native Verification
- Original parser/verifier:
- Accepted vector result:
- Rejected vector result:
- Clean restart result:

## Feature Evidence
- Original module/DLL:
- Representative operation:
- Inputs/outputs/side effects:

## Dependencies
- Hardware/driver:
- Configuration/content:
- Server role and routes:
- Remaining prerequisites:

## Replay
- Commands:
- Evidence paths:
- Gate report:
```

Do not use "fully working" or "same as the original licensed environment" unless the gate report
passes for the selected profile and the dependency section contains no unimplemented requirement
for the claimed feature.
