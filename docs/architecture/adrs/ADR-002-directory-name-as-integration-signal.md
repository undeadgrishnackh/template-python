# ADR-002: Directory Name Parameter as Integration Signal

**Status:** Accepted
**Date:** 2026-01-08
**Deciders:** Morgan (Solution Architect)

---

## Context

The Python cookiecutter template needs to distinguish between two usage modes:

1. **Standalone mode:** New project, full git initialization (existing behavior)
2. **Integration mode:** Inside existing project, skip repo creation (new behavior)

We need to decide how the `directory_name` parameter interacts with git detection.

### Forces at Play

1. **Explicit intent:** Users should be able to clearly signal their intent
2. **Backwards compatibility:** Default behavior must remain unchanged
3. **Fail-safe design:** Integration mode should work even if git detection fails
4. **Simplicity:** Avoid complex conditional logic

### Constraints

- Must support 5D-Wave agent workflows (always provide `directory_name=source`)
- Must preserve kata workflows (interactive prompt for `kata_name`)
- Default `directory_name` value uses Jinja template with `kata_name`

---

## Decision

Explicit `directory_name` parameter value (not derived from `kata_name`) signals integration mode and always skips repository creation.

### Detection Logic

```python
def is_integration_mode() -> bool:
    """Determine if running in integration mode.

    Integration mode is active when:
    1. directory_name was explicitly provided (not default), OR
    2. Running inside an existing git repository

    Integration mode skips: gh repo create, git init, git remote add, git push
    """
    directory_name = "{{ cookiecutter.directory_name }}"
    kata_name = "{{ cookiecutter.kata_name }}"

    # Check if directory_name looks like default format (contains date prefix)
    # Default format: YYYYMMDD_kata_name
    is_default_format = directory_name.endswith(f"_{kata_name.lower().replace(' ', '_')}")

    # Explicit directory_name OR git detected = integration mode
    return not is_default_format or is_inside_git_repo()
```

### Behavior Matrix

| directory_name | .git detected | Mode | Git Operations |
|----------------|---------------|------|----------------|
| Default (dated) | No | Standalone | Full init |
| Default (dated) | Yes | Integration | Skip repo creation |
| Explicit ("source") | No | Integration | Skip repo creation |
| Explicit ("source") | Yes | Integration | Skip repo creation |

---

## Consequences

### Positive

- **Fail-safe:** Explicit `directory_name` guarantees integration mode regardless of git detection
- **Clear intent:** Agents explicitly signal their workflow mode
- **Backwards compatible:** Default behavior unchanged (dated format = standalone)
- **Dual detection:** Both parameter value AND git detection trigger integration mode

### Negative

- **Detection heuristic:** Determining "explicit vs default" relies on format matching
  - *Mitigation:* Default format is distinctive (YYYYMMDD prefix)
- **User education needed:** Must document that explicit `directory_name` changes behavior
  - *Mitigation:* Breaking change notice in release notes

### Trade-offs

- **Implicit over explicit flag:** We infer intent from directory name format rather than adding separate `--integration` flag
  - *Rationale:* Fewer parameters to manage, natural workflow distinction

---

## Alternatives Considered

### Alternative 1: Add explicit `skip_git_init` parameter

**Pros:** Explicit control, no inference needed
**Cons:** Another parameter to manage, redundant with directory_name signal
**Why Rejected:** Directory name already provides clear signal; additional parameter adds complexity

### Alternative 2: Only rely on git detection (no parameter signal)

**Pros:** Simpler logic, single detection mechanism
**Cons:** No fail-safe if git detection fails; less explicit intent
**Why Rejected:** Agents should be able to explicitly signal intent

### Alternative 3: Always prompt for mode choice

**Pros:** Explicit user choice every time
**Cons:** Breaks automation, requires interactive input
**Why Rejected:** Must support headless/agentic workflows

---

## Validation

| Scenario | directory_name | .git | Result |
|----------|----------------|------|--------|
| 5D-Wave agent | `source` | Yes | Skip repo creation |
| 5D-Wave agent (git detection fails) | `source` | No | Skip repo creation |
| Fresh kata | `20260108_fizzbuzz` | No | Full git init |
| Kata in existing repo | `20260108_fizzbuzz` | Yes | Skip repo creation |
| Platform engineer | `trading-engine` | Yes | Skip repo creation |

---

## References

- FR-002: Configurable Source Directory Name
- US-002: Configurable Source Directory Name
- Handoff question #2: Directory Name as Signal
