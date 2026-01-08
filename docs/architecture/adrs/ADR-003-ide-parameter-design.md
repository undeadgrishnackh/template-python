# ADR-003: IDE Opening Parameter Design

**Status:** Accepted
**Date:** 2026-01-08
**Deciders:** Morgan (Solution Architect)

---

## Context

The Python cookiecutter template currently always opens VS Code after generation (`code .`). This blocks headless automation and doesn't support IDE preferences. We need to design a parameter system for IDE control.

### Forces at Play

1. **Automation support:** Headless environments must not attempt GUI operations
2. **IDE flexibility:** Support multiple IDEs (VS Code, PyCharm)
3. **Non-blocking errors:** IDE failures should not fail generation
4. **Cross-platform:** IDE commands differ by OS

### Constraints

- Default must be safe for automation (`none`)
- Breaking change from current behavior (was `vscode` implicitly)
- No external dependencies for command detection

---

## Decision

Add `open_ide` parameter with enum values: `none` (default), `vscode`, `pycharm`. Invalid values fail loudly with helpful error.

### Parameter Specification

```json
{
  "open_ide": "none"
}
```

### Valid Values

| Value | Behavior | Commands |
|-------|----------|----------|
| `none` | No IDE opens (default) | None |
| `vscode` | Open VS Code | `code <directory>` |
| `pycharm` | Open PyCharm | `pycharm <directory>` or `open -a "PyCharm" <directory>` (macOS) |

### Implementation

```python
import shutil
import subprocess
import sys

VALID_IDE_OPTIONS = {"none", "vscode", "pycharm"}

def validate_ide_option(ide_option: str) -> None:
    """Validate IDE option early, fail fast with helpful error."""
    if ide_option not in VALID_IDE_OPTIONS:
        print(f"ERROR: Invalid open_ide value: '{ide_option}'")
        print(f"Valid options: {', '.join(sorted(VALID_IDE_OPTIONS))}")
        sys.exit(1)

def open_ide(directory: str, ide_option: str) -> None:
    """Open IDE with generated directory. Non-fatal on failure."""
    if ide_option == "none":
        return

    if ide_option == "vscode":
        _open_vscode(directory)
    elif ide_option == "pycharm":
        _open_pycharm(directory)

def _open_vscode(directory: str) -> None:
    """Open VS Code. Warn if command not found."""
    if not shutil.which("code"):
        print("WARNING: VS Code 'code' command not found, skipping IDE open")
        return

    try:
        subprocess.run(["code", directory], check=False, timeout=10)
    except Exception as e:
        print(f"WARNING: Failed to open VS Code: {e}")

def _open_pycharm(directory: str) -> None:
    """Open PyCharm with platform-specific command."""
    # Try pycharm CLI first (Linux, Windows with PATH configured)
    if shutil.which("pycharm"):
        try:
            subprocess.run(["pycharm", directory], check=False, timeout=10)
            return
        except Exception as e:
            print(f"WARNING: pycharm command failed: {e}")

    # macOS fallback: use 'open' command
    if sys.platform == "darwin":
        try:
            subprocess.run(["open", "-a", "PyCharm", directory], check=False, timeout=10)
            return
        except Exception as e:
            print(f"WARNING: macOS open -a PyCharm failed: {e}")

    print("WARNING: PyCharm command not found, skipping IDE open")
```

---

## Consequences

### Positive

- **Safe default:** `none` prevents GUI operations in automation
- **Explicit control:** Users clearly specify IDE preference
- **Non-fatal errors:** IDE failures print warnings but don't block
- **Platform awareness:** PyCharm uses macOS-specific fallback
- **Fast failure:** Invalid options caught early before work begins

### Negative

- **Breaking change:** Existing users expecting VS Code must add `open_ide=vscode`
  - *Mitigation:* Document in release notes, provide migration guide
- **Limited IDE support:** Only VS Code and PyCharm supported initially
  - *Mitigation:* Pattern allows easy addition of new IDEs

### Trade-offs

- **Fail loudly vs gracefully:** Invalid parameter values fail; missing IDE commands warn
  - *Rationale:* Typos should be caught (fail); environment differences should be tolerated (warn)

---

## Alternatives Considered

### Alternative 1: Boolean `skip_ide` parameter

**Pros:** Simple true/false
**Cons:** Doesn't support IDE selection, double negative logic
**Why Rejected:** Need to support multiple IDEs, not just on/off

### Alternative 2: Free-form command string

**Pros:** Maximum flexibility, support any IDE
**Cons:** Security risk (command injection), no validation
**Why Rejected:** Security concern, complex error handling

### Alternative 3: Default to VS Code (current behavior)

**Pros:** No breaking change
**Cons:** Breaks automation, not safe default
**Why Rejected:** Automation support is primary requirement

### Alternative 4: Silent default on invalid values

**Pros:** More forgiving
**Cons:** Hides configuration errors
**Why Rejected:** Typos should be caught early

---

## Error Handling Strategy

| Scenario | Response | Exit Code |
|----------|----------|-----------|
| Invalid `open_ide` value | Error message with valid options | 1 (fail) |
| IDE command not found | Warning message | 0 (success) |
| IDE launch fails | Warning message | 0 (success) |
| IDE launch hangs | Timeout after 10 seconds | 0 (success) |

---

## Validation

| Scenario | open_ide | IDE Installed | Result |
|----------|----------|---------------|--------|
| Agent automation | (default) | - | No IDE opens |
| Developer VS Code | `vscode` | Yes | VS Code opens |
| Developer VS Code | `vscode` | No | Warning, continues |
| Developer PyCharm macOS | `pycharm` | Yes | PyCharm opens |
| Developer typo | `vim` | - | Error, exit 1 |

---

## References

- FR-003: IDE Opening Control
- US-003: IDE Opening Control
- Handoff questions #3 and #4: IDE failure handling and parameter validation
