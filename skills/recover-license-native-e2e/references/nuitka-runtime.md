# Nuitka and Embedded CPython Runtime Probing

## Contents

1. Recognize the runtime
2. Attach through CPython
3. Inventory modules and functions
4. Trace high-level boundaries
5. Recover machine-identity composition
6. Qt thread handling
7. Failure handling

## 1. Recognize the Runtime

Look for:

- a loaded `python3xx.dll`;
- Nuitka version objects and `nuitka_module_loader`;
- module strings and paths ending in `.py` even when those files are absent;
- `compiled_function` objects whose `__code__` contains only a placeholder;
- bundled PySide/PyQt, Cryptodome, requests, wmi, or application package names.

Nuitka compiled functions often retain signatures, local-variable names, module globals, class
members, constants, and imported modules even though ordinary Python bytecode is gone.

## 2. Attach Through CPython

Use the bundled executor for short probes:

```powershell
python scripts/nuitka_pyexec.py --pid PID --code-file probe.py --report trace.json
```

The executor finds `python3*.dll` and calls:

```text
PyGILState_Ensure
PyRun_SimpleString
PyGILState_Release
```

Keep probes short. Write detailed results incrementally to an evidence file from inside the target.
A probe that enters an infinite loop can hold the GIL after the controller times out.

## 3. Inventory Modules and Functions

Useful probe patterns:

```python
import inspect
import sys

rows = []
for name, module in sorted(sys.modules.items()):
    if name.startswith("PRODUCT_PACKAGE"):
        rows.append((name, getattr(module, "__file__", None)))

module = sys.modules["PRODUCT_PACKAGE.license"]
for name, value in vars(module).items():
    if callable(value):
        try:
            signature = str(inspect.signature(value))
        except Exception:
            signature = "?"
        rows.append((name, type(value).__name__, signature))
```

Record class members, function signatures, local names, imported crypto/network/storage modules,
permission constants, field labels, keys, and file paths.

## 4. Trace High-Level Boundaries

Wrap module globals before invoking the original function. Typical wrappers include:

- `hashlib.md5/sha*` and object `update/hexdigest`;
- application encrypt/decrypt helpers;
- serializer/parser functions;
- machine-identity providers;
- file open/read/write helpers;
- HTTP client send/receive methods;
- global state get/set functions;
- the original verifier and permission mapper.

Example pattern:

```python
original = license_module.hashlib.md5
events = []

class Proxy:
    def __init__(self, *args, **kwargs):
        self.inner = original(*args, **kwargs)

    def update(self, value):
        events.append(("md5.update", repr(value)))
        return self.inner.update(value)

    def hexdigest(self):
        result = self.inner.hexdigest()
        events.append(("md5.hexdigest", result))
        return result

license_module.hashlib.md5 = lambda *args, **kwargs: Proxy(*args, **kwargs)
```

Restore every wrapper in `finally`. Confirm that the compiled function resolves the module global
dynamically; some Nuitka optimizations cache direct references.

## 5. Recover Machine-Identity Composition

Replace the hardware provider with marker objects. Return a unique marker for every class/property
and call the original machine-code function. The result reveals selection, trimming, slicing, and
concatenation order without guessing from real hardware values.

```python
class MarkerObject:
    qualifiers = {"UUID": "{DISK_UUID}"}
    ProcessorId = " CPU_ID "
    SerialNumber = "BOARD_OR_BIOS_SERIAL"

class MarkerProvider:
    def Win32_DiskDrive(self):
        return [MarkerObject()]
```

Use distinct object classes for disk, CPU, board, network, and BIOS. Log every property access.
Then verify the recovered order against the real function output and a second synthetic identity.

## 6. Qt Thread Handling

Frida executes the CPython call on its own thread. Reading Python state and calling non-UI helpers
is usually reliable. Creating or mutating Qt widgets from that thread may crash or hang.

For GUI actions:

- use external UI automation for clicks and text entry;
- invoke an existing Qt slot through a queued connection;
- post work to an object owned by the main Qt thread;
- keep a Python reference alive until the queued callback completes.

Use the original non-UI generator/verifier directly when available.

## 7. Failure Handling

- `script.load()` timeout: schedule work with `setImmediate`; the bundled executor already does.
- GIL timeout: restart an isolated target process and reduce the probe to one function call.
- Missing Python DLL: confirm the active process and onefile child process; attach to the child that
  owns the window/runtime.
- `compiled_function` has no bytecode: rely on signatures, globals, high-level wrappers, marker
  providers, strings, and native xrefs.
- Wrapper receives no calls: the compiled function may cache the original reference; hook a lower
  boundary or instrument the native call site.
- Random encrypted output: compare decrypted plaintext and fields, not ciphertext bytes.
