# Server Dependency and Local Backend Analysis

## Contents

1. Classify the server role
2. Capture the protocol contract
3. Prove ownership of each result
4. Design a local backend
5. Validate parity
6. Common false positives

## 1. Classify the Server Role

Classify each endpoint independently. A product may use several roles.

| Role | Server response | Local consequence |
| --- | --- | --- |
| Issuer | signed license or activation blob | original feature code remains client-side |
| Entitlement | role, feature flags, limits, session token | client or downstream API enforces returned state |
| Configuration | project settings, templates, keys, manifests | original feature needs exact configuration/content |
| Content/data | documents, maps, models, databases, live data | feature output depends on supplied data |
| Compute | completed conversion, analysis, inference, or transaction result | server owns part or all of the feature implementation |
| Hybrid | combinations of the above | reproduce every role used by the tested feature |

Do not infer a role from endpoint names. Determine whether the response contains permission to
compute or the computation result itself.

## 2. Capture the Protocol Contract

Capture one complete successful sequence from process start through feature completion:

- DNS host, scheme, route, method, redirects, and request order;
- TLS library, certificate validation, pinning, and client certificates;
- headers, cookies, bearer tokens, refresh tokens, and device/session binding;
- query/body serialization, charset, compression, and content type;
- nonce, timestamp, replay window, request signature, and canonicalization;
- status, headers, body schema, signature/MAC, and error responses;
- retry, polling, websocket, callback, and logout behavior;
- local persistence in files, registry, database, browser storage, or credential manager.

Prefer runtime hooks at the application's HTTP/TLS framework when a proxy sees only ciphertext or
pinning interferes. Typical boundaries include WinHTTP/WinINet, libcurl, OpenSSL, Python requests,
.NET HttpClient, Java HTTP clients, Qt QNetworkAccessManager, Electron fetch/IPC, and websocket
libraries.

Store raw request/response bytes and a redacted report separately. Preserve field ordering when
signatures cover serialized bytes.

## 3. Prove Ownership of Each Result

Use controlled response mutation:

1. Replay the exact successful response.
2. Change one entitlement field and observe the internal role.
3. Replace the payload with the same entitlement but omit content/data.
4. Return structurally valid placeholder results for a feature operation.
5. Block the endpoint after activation and repeat the feature.
6. Expire the token and observe refresh behavior.

Interpretation:

- The client still computes the same result after the endpoint is blocked: the server likely
  issued permission or configuration only.
- The feature waits for or renders the response result: the server owns computation or data.
- The UI opens but a later backend/API rejects the operation: entitlement is enforced at more
  than one boundary.

## 4. Design a Local Backend

Implement the observed contract, not only the first activation response.

### Issuer or Entitlement

Reproduce:

- activation and login routes;
- token/license fields and signatures expected by the client;
- feature list, limits, edition, expiry, and device/account binding;
- refresh, logout, revocation, and persisted state;
- server time if the client relies on it.

When the client contains only a public verification key, issue artifacts with a controlled keypair
and substitute the client's public key or the narrow verification decision. Keep feature modules
unchanged.

### Configuration or Content

Reproduce route semantics plus all files/data consumed by the original feature. Record content
hashes, MIME types, compression, filenames, version manifests, and cache behavior.

### Compute

Implement the operation contract:

```text
input validation -> job creation -> state transitions -> computation
-> result schema -> errors/cancellation -> persistence/download
```

Returning `enabled: true` establishes entitlement only. Backend parity requires representative
inputs to produce structurally and semantically valid results consumed by the original client.

## 5. Validate Parity

For every route used by the selected feature, record:

| Field | Evidence |
| --- | --- |
| Request | exact method, route, headers, and body fixture |
| Response | status, headers, and raw body fixture |
| State | session/job/cache transition before and after |
| Client effect | parser result and internal entitlement/content/result |
| Feature effect | original module/DLL dispatch and final user-visible or file/device effect |
| Failure behavior | invalid token, timeout, malformed data, and retry result |

Run with the original remote endpoint blocked or redirected to the local backend. Start from a
clean client state. Exercise activation, restart, refresh, representative feature execution, and
logout/expiry. Mark `backend-parity` pass only when every endpoint required by that feature is
covered.

## 6. Common False Positives

- A patched `isLicensed()` enables the UI while a downstream API still rejects requests.
- A cached token makes a clean-start test appear successful.
- A local backend returns feature flags but omits configuration downloaded later.
- A response schema is accepted, but server-returned computation is replaced by dummy data.
- TLS interception captures login but misses websocket, polling, or download hosts.
- An updater/document endpoint is mistaken for a core feature dependency.
- One edition is accepted while per-feature limits remain enforced elsewhere.

Record each dependency independently. State that the original client feature is intact only after
its original implementation executes with all required hardware, content, and service inputs.
