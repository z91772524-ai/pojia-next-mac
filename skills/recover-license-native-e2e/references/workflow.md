# License Recovery Workflow

## Contents

1. Outcome model
2. Intake and baseline
3. Runtime and protection routing
4. Decision-graph recovery
5. Transform-chain recovery
6. Implementation selection
7. Native acceptance
8. Original feature parity
9. Clean replay
10. Platform routing notes

## 1. Outcome Model

Separate these outcomes. Do not collapse them into a single "activated" claim.

| Outcome | Required observation |
| --- | --- |
| Visual unlock | A label, menu, or button changed |
| Internal entitlement | The original verifier assigned the intended role/feature set |
| Persistent activation | A clean restart loaded the artifact/token and restored that role |
| Local feature parity | An original module/assembly/DLL executed a representative operation |
| Service parity | Every server-owned route, state transition, content item, or computation used by that operation was reproduced |

Visual unlock is useful for navigation but is never the final proof.

## 2. Intake and Baseline

1. Record the exact installer and executable hashes.
2. Inventory sidecar DLLs, managed assemblies, script archives, configuration, databases,
   certificates, public keys, and cached activation files.
3. Preserve accepted and rejected serial/license fixtures as exact bytes. Record source,
   encoding, line endings, and whether the application accepted each fixture.
4. Start the evidence workspace with `scripts/license_evidence.py`.
5. Keep these paths separate:

```text
originals/   immutable inputs or their manifest
fixtures/    accepted/rejected request and response bytes
traces/      runtime, debugger, traffic, and state observations
outputs/     generators, backends, licenses, tokens, and patches
reports/     integrity and completion-gate reports
```

Capture the current runtime before trusting source-like files. Installers may carry stale,
duplicate, debug, or decoy payloads.

## 3. Runtime and Protection Routing

Identify the active format before deep analysis.

| Runtime | First evidence | Preferred boundary |
| --- | --- | --- |
| Native PE/ELF | headers, imports, strings, sections, TLS, mitigations | compare/hash/crypto/file/network APIs and final permission store |
| .NET | CLR header, assemblies, metadata | verifier method, serializer, crypto provider, property setter |
| JVM | class/JAR metadata, manifests | verifier method, keystore/signature calls, feature registry |
| Python/Nuitka | Python DLL, module strings, compiled-function objects | embedded interpreter and high-level module calls |
| Electron/JS | ASAR, JS bundles, IPC routes | response parser, storage, feature flags, native addon boundary |
| Packed/virtualized | high entropy, sparse imports, entry stub, VM sections | post-unpack memory and stable API boundaries |

For a commercial protector, first decide whether the authorization routine itself is
virtualized. A full devirtualization is often unnecessary when machine identity, hashing,
signature verification, file IO, response parsing, and permission assignment remain observable
at stable boundaries.

## 4. Decision-Graph Recovery

Build an explicit graph with real values:

```text
input source
  -> parse/normalize
  -> machine or account binding
  -> version/edition selection
  -> checksum, MAC, signature, or online request
  -> expiry and clock policy
  -> accepted/rejected branch
  -> internal role and feature-set storage
  -> feature dispatch
```

Record every trusted input. Include registry, WMI, SMBIOS, disk/adapter identifiers, files,
environment, current time, secure clock, account ID, product version, server nonce, response
headers, and cached state.

Use a known accepted vector first. Change one field at a time. Generate a rejected vector by
changing one authenticated byte while keeping all formatting valid. This distinguishes parser
failure from cryptographic or policy failure.

## 5. Transform-Chain Recovery

For every transform, record:

- source bytes and resulting bytes;
- string encoding and Unicode normalization;
- whitespace, case, sorting, separators, and field order;
- integer/float/date formatting and timezone;
- hash/MAC/signature algorithm and covered range;
- KDF password, salt, work factors, and derived-key length;
- cipher mode, IV/nonce, padding, tag, and output framing;
- compression and Base64/hex variants;
- version-specific branches and permission mapping.

Prefer structured parsers and crypto libraries. Use hooks to log the bytes passed into a hash,
MAC, signing, verification, encryption, and decryption API. Validate recovered rules against all
accepted and rejected fixtures before implementing a generator.

## 6. Implementation Selection

Choose the smallest implementation that preserves original feature code.

| Condition | Preferred implementation |
| --- | --- |
| Symmetric/offline format fully recovered | Compatible keygen or license writer |
| Client verifies an asymmetric server signature | Substitute a controlled public key and issue compatible artifacts, or change only the verifier decision |
| Server returns roles/features while operations are local | Protocol-compatible local backend or narrow response-parser fixture |
| Server supplies configuration/content | Backend plus complete content/config fixtures |
| Server performs the operation | Reimplement that operation and its state/data contract |
| Protector obscures only the verifier | Narrow runtime or binary change with original and derivative kept separately |

Do not replace the original feature module merely to make a smoke test pass.

## 7. Native Acceptance

Prove acceptance using the application's original code:

1. Feed the generated artifact through the normal parser.
2. Call or observe the original verifier.
3. Capture its return value and the internal role/feature store.
4. Capture the rejection result for a one-byte-invalid artifact.
5. Confirm that the accepted state is not inherited from a previous process or cache.

Good evidence includes a debugger trace, runtime probe JSON, application log, or memory/state
snapshot naming the original verifier and final internal entitlement.

## 8. Original Feature Parity

Select at least one representative feature per distinct implementation boundary. Examples:

- a native driver DLL call for hardware operations;
- a managed assembly method for document conversion;
- an original Python module method for data processing;
- an IPC call from Electron to its native backend;
- a real server response for server-executed computation.

Capture the call target, inputs, outputs, side effects, and module/DLL hash. A button becoming
enabled is not feature execution. Keep external prerequisites separate:

```text
authorization: role/feature permission
hardware: device, cable, firmware, driver
configuration: project, calibration, certificates, paths
content: templates, databases, downloaded resources
service: issuer, entitlement, data, or compute endpoints
```

## 9. Clean Replay

Reset or isolate prior state, then replay:

1. Restore the original application and baseline configuration.
2. Remove only the activation fixture/cache created by the test.
3. Generate or obtain the artifact using recorded commands.
4. Start the untouched original application normally.
5. Observe native acceptance and internal role.
6. Execute the representative original feature.
7. Recompute original hashes.
8. Save commands, fixture hashes, logs, screenshots, and reports.

Repeat once from a new process. For machine-bound licenses, repeat on a second synthetic identity
or by mocking the identity provider to prove field order and binding.

## 10. Platform Routing Notes

- **Native**: start with xrefs from license strings, file paths, crypto imports, compare calls,
  permission constants, and network endpoints. Use runtime data breakpoints on the final role.
- **.NET**: inspect metadata and resources before instruction patching. Trace serializer and
  cryptography calls, then invoke the original verifier through reflection or a small harness.
- **JVM**: preserve exact charset and provider behavior. Trace keystore/public-key loading and
  the feature registry updated after verification.
- **Electron**: inspect ASAR and browser storage, but follow IPC into native addons or services.
  Verify both renderer state and backend enforcement.
- **Python/Nuitka**: use module metadata and the loaded CPython runtime; see
  `nuitka-runtime.md`.
- **Packed/virtualized**: dump only after the real modules and imports are materialized, or remain
  at stable API boundaries when the authorization code is virtualized.
