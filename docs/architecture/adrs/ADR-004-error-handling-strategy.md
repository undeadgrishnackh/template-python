# ADR-004: Error Handling Strategy

**Status:** Accepted
**Date:** 2026-01-08
**Deciders:** Morgan (Solution Architect)

---

## Context

The enhanced post-generation hook introduces new operations (git detection, IDE launching) that can fail. We need a consistent error handling strategy that balances reliability with resilience.

### Forces at Play

1. **Automation reliability:** Agentic workflows need predictable outcomes
2. **User experience:** Helpful error messages for human users
3. **Partial success:** Some failures shouldn't block overall generation
4. **Fast feedback:** Configuration errors should fail early

### Constraints

- Must distinguish fatal vs non-fatal errors
- Must provide actionable error messages
- Must maintain backwards compatibility for existing errors

---

## Decision

Implement tiered error handling: fail fast on configuration errors, warn on environmental issues, continue on non-critical failures.

### Error Classification

| Category | Examples | Response | Exit Code |
|----------|----------|----------|-----------|
| Configuration | Invalid `open_ide` value | Fail immediately | 1 |
| Prerequisites | `pipenv` not installed | Fail with guidance | 1 |
| Git Operations | `gh repo create` fails | Fail (standalone mode) | 1 |
| Environment | IDE command not found | Warn and continue | 0 |
| Non-critical | IDE launch timeout | Warn and continue | 0 |

### Implementation Pattern

```python
import sys
from typing import NoReturn

def fail_fast(message: str, guidance: str = "") -> NoReturn:
    """Fail immediately with helpful error message."""
    print(f"ERROR: {message}")
    if guidance:
        print(f"  -> {guidance}")
    sys.exit(1)

def warn_and_continue(message: str) -> None:
    """Log warning but allow process to continue."""
    print(f"WARNING: {message}")

def run_required_command(command: str, description: str) -> None:
    """Run command that must succeed. Fails on error."""
    print(f"{description}...")
    try:
        completed = subprocess.run(
            command, shell=True, check=True, timeout=360,
            cwd=PROJECT_DIRECTORY
        )
    except subprocess.CalledProcessError as e:
        fail_fast(
            f"{description} failed: {command}",
            f"Exit code: {e.returncode}"
        )
    except subprocess.TimeoutExpired:
        fail_fast(
            f"{description} timed out after 360 seconds",
            "Check network connectivity or try again"
        )

def run_optional_command(command: str, description: str) -> bool:
    """Run command that may fail. Warns on error, returns success status."""
    print(f"{description}...")
    try:
        subprocess.run(command, shell=True, check=True, timeout=30)
        return True
    except Exception as e:
        warn_and_continue(f"{description} failed: {e}")
        return False
```

### Validation Order

Validation runs **before** any work begins:

```python
def validate_configuration() -> None:
    """Validate all configuration early. Fail fast on errors."""
    # 1. Check IDE option is valid
    validate_ide_option(IDE_OPTION)

    # 2. Check required tools exist (pipenv, git)
    if not shutil.which("pipenv"):
        fail_fast("pipenv not found", "Install with: pip install pipenv")

    if not shutil.which("git"):
        fail_fast("git not found", "Install git from https://git-scm.com")

    # 3. If standalone mode, check gh CLI
    if not is_integration_mode() and not shutil.which("gh"):
        fail_fast(
            "GitHub CLI (gh) not found",
            "Install from https://cli.github.com or use directory_name parameter for integration mode"
        )
```

---

## Consequences

### Positive

- **Predictable behavior:** Users know which errors are fatal vs warnings
- **Fast feedback:** Configuration errors caught immediately
- **Graceful degradation:** IDE issues don't block generation
- **Actionable messages:** Errors include guidance for resolution

### Negative

- **More code:** Error handling adds implementation complexity
  - *Mitigation:* Centralized helpers reduce duplication
- **Different behavior for similar operations:** Git commands fail, IDE commands warn
  - *Mitigation:* Clear documentation of error categories

### Trade-offs

- **Strictness vs flexibility:** Configuration validation is strict; runtime issues are flexible
  - *Rationale:* Configuration errors are user mistakes; runtime issues are environmental

---

## Alternatives Considered

### Alternative 1: All errors are fatal

**Pros:** Simple, predictable, no partial success
**Cons:** IDE issues would block generation unnecessarily
**Why Rejected:** IDE opening is not critical to template success

### Alternative 2: All errors are warnings

**Pros:** Maximum resilience
**Cons:** Configuration mistakes would be hidden, inconsistent state possible
**Why Rejected:** Some operations must succeed for valid output

### Alternative 3: User-configurable strictness

**Pros:** Maximum flexibility
**Cons:** Adds complexity, more parameters
**Why Rejected:** Predefined error categories are sufficient

---

## Error Message Guidelines

1. **Be specific:** "Invalid open_ide value: 'vim'" not "Invalid parameter"
2. **Be actionable:** Include how to fix when possible
3. **Be consistent:** Use ERROR: prefix for fatal, WARNING: for non-fatal
4. **Be brief:** One line for message, optional second line for guidance

### Examples

```
ERROR: Invalid open_ide value: 'vim'
  -> Valid options: none, pycharm, vscode

ERROR: pipenv not found
  -> Install with: pip install pipenv

WARNING: VS Code 'code' command not found, skipping IDE open

WARNING: PyCharm launch timed out after 10 seconds
```

---

## References

- NFR-002: Error Resilience (IDE failures non-fatal)
- US-003: IDE Opening Control (non-blocking failures)
- Handoff question #3: IDE failure handling
