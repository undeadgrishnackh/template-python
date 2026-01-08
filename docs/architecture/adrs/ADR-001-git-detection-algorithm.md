# ADR-001: Git Repository Detection Algorithm

**Status:** Accepted
**Date:** 2026-01-08
**Deciders:** Morgan (Solution Architect)

---

## Context

The Python cookiecutter template enhancement (US-001) requires detecting when running inside an existing git repository to skip repository creation operations. We need to decide on the detection algorithm and termination criteria.

### Forces at Play

1. **Reliability:** Detection must work on all platforms (macOS, Linux, Windows)
2. **Performance:** Hook execution should remain fast
3. **Correctness:** Must handle edge cases (worktrees, bare repos, nested repos)
4. **Simplicity:** No external dependencies allowed

### Constraints

- Python 3.11+ standard library only
- Must work with git worktrees (`.git` can be a file, not directory)
- Must handle filesystem root edge case

---

## Decision

Implement parent directory traversal using `pathlib.Path`, stopping at the **first** `.git` found.

### Algorithm

```python
from pathlib import Path

def is_inside_git_repo() -> bool:
    """Detect if current directory is inside a git repository.

    Traverses parent directories looking for .git (directory or file).
    Returns True on first match, False if filesystem root reached.
    """
    current = Path.cwd()
    while current != current.parent:  # Stop at filesystem root
        git_path = current / ".git"
        if git_path.exists():  # Works for both directory and file
            return True
        current = current.parent
    # Check root directory itself
    return (current / ".git").exists()
```

### Design Choices

1. **Stop at first `.git`:** No need to find "outermost" repo - any git presence means skip repo creation
2. **Use `exists()` not `is_dir()`:** Git worktrees use `.git` files pointing to actual git directory
3. **Explicit root check:** The while loop condition `current != current.parent` exits at root without checking root itself

---

## Consequences

### Positive

- **Simple implementation:** ~10 lines of code
- **Cross-platform:** `pathlib` handles path separators correctly
- **Handles worktrees:** Using `exists()` detects both directory and file forms
- **Fast termination:** Stops immediately when `.git` found
- **No false negatives:** Any repository in parent tree triggers detection

### Negative

- **No nested repo distinction:** Cannot detect if we're in a nested submodule vs parent repo
  - *Mitigation:* Not required by business need - any git presence suffices
- **Symlink following:** `exists()` follows symlinks, which is generally correct but could theoretically cause issues
  - *Mitigation:* Edge case with low probability in practice

### Trade-offs

- **Simplicity over precision:** We don't report which repo was found, just that one exists
- **Performance over features:** No caching, re-runs detection each time (but fast enough)

---

## Alternatives Considered

### Alternative 1: Use `git rev-parse --is-inside-work-tree`

**Pros:** Git's own detection, handles all edge cases
**Cons:** Requires git CLI on PATH, subprocess overhead
**Why Rejected:** Adds external dependency, slower execution

### Alternative 2: Find outermost `.git` (traverse to root always)

**Pros:** Could report which repo we're in
**Cons:** Unnecessary traversal, no business value
**Why Rejected:** Adds complexity without benefit

### Alternative 3: Environment variable override

**Pros:** Allows forcing detection result
**Cons:** Another configuration point, potential misconfiguration
**Why Rejected:** `directory_name` parameter already serves as override signal

---

## Validation

Algorithm tested against these scenarios:

| Scenario | Detection | Expected Result |
|----------|-----------|-----------------|
| `.git` in current directory | Found | Skip repo creation |
| `.git` 3 levels up in parent tree | Found | Skip repo creation |
| `.git` in sibling directory | Not found | Full git init |
| Git worktree (`.git` is file) | Found | Skip repo creation |
| Bare repository | Found | Skip repo creation |
| Filesystem root, no git | Not found | Full git init |

---

## References

- FR-001: Automatic Git Repository Detection
- US-001: Smart Git Repository Detection
- Python pathlib documentation: https://docs.python.org/3/library/pathlib.html
