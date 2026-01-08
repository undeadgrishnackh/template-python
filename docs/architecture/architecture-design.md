# Architecture Design: Python Cookiecutter Template Enhancement

**Document ID:** ARCH-COOKIECUTTER-2026-001
**Version:** 1.0
**Status:** DRAFT
**Date:** 2026-01-08
**Author:** Morgan (Solution Architect) / Archer (Visual Architect)
**Wave:** DESIGN

---

## 1. Executive Summary

This document describes the architecture design for enhancing the Python Cookiecutter template to support three integration scenarios: smart git detection, configurable directory naming, and IDE opening control.

**Design Approach:** Minimal modification to existing `post_gen_project.py` hook with clear separation of concerns through well-defined functions.

**Key Architectural Decisions:**
- Single-file modification (no new modules)
- Pure Python standard library (no external dependencies)
- Function-based architecture with clear responsibilities
- Fail-safe defaults for automation compatibility

---

## 2. Current Architecture Analysis

### 2.1 Component Inventory

| Component | Purpose | Modification Required |
|-----------|---------|----------------------|
| `cookiecutter.json` | Template parameters | ADD: `open_ide` parameter |
| `hooks/pre_gen_project.py` | Input validation | NO CHANGE |
| `hooks/post_gen_project.py` | Post-generation automation | MAJOR REFACTOR |

### 2.2 Current Execution Flow

```
cookiecutter invocation
        |
        v
pre_gen_project.py
  - Validate kata_name (MODULE_REGEX)
        |
        v
Template expansion (Jinja2)
        |
        v
post_gen_project.py
  1. pipenv install --dev
  2. forceTypingExtensions
  3. pipenv run tests
  4. gh repo create (PROBLEM: fails in existing repo)
  5. git init (PROBLEM: conflicts with existing .git)
  6. install_pre_hooks
  7. git remote add origin (PROBLEM: assumes new repo)
  8. git branch -M main
  9. git add --all
  10. git commit
  11. git push (PROBLEM: fails without remote)
  12. code . (PROBLEM: blocks headless execution)
```

### 2.3 Problem Analysis

| Step | Issue | Impact |
|------|-------|--------|
| 4 | `gh repo create` fails if repo exists | Blocks 5D-Wave agents |
| 5 | `git init` conflicts with parent `.git` | Git state corruption |
| 7-11 | Remote operations assume new repo | Fatal errors |
| 12 | `code .` blocks headless execution | CI/CD pipeline failure |

---

## 3. Target Architecture

### 3.1 Design Principles

1. **Single Responsibility:** Each function does one thing well
2. **Fail-Safe Defaults:** Automation-friendly default behavior
3. **Backwards Compatibility:** Existing workflows continue to work
4. **Platform Agnostic:** Works on macOS, Linux, Windows
5. **Standard Library Only:** No external dependencies in hooks

### 3.2 Component Design

#### 3.2.1 Function Decomposition

```
post_gen_project.py (refactored)
|
+-- is_inside_git_repo() -> bool
|   Purpose: Detect if running inside existing git repository
|   Algorithm: Traverse parent directories for .git
|
+-- setup_development_environment() -> None
|   Purpose: Install dependencies and quality gates
|   Steps: pipenv install, pre-commit install, run tests
|
+-- initialize_git_repository() -> None
|   Purpose: Create new git repo (only when not inside existing)
|   Steps: gh repo create, git init, git remote add
|
+-- commit_changes(message: str) -> None
|   Purpose: Stage and commit changes (always runs)
|   Steps: git add, git commit
|
+-- push_to_remote() -> None
|   Purpose: Push to origin (only when repo created)
|   Steps: git push -u origin main
|
+-- open_ide(ide_choice: str) -> None
|   Purpose: Open IDE based on parameter (or skip)
|   Options: none, vscode, pycharm
|
+-- main() -> None
    Purpose: Orchestrate execution based on context
    Logic: Conditional flow based on git detection
```

#### 3.2.2 Execution Flow (Target)

```
main()
  |
  v
is_inside_git_repo() -----> returns True/False
  |
  v
setup_development_environment()
  - pipenv install --dev
  - forceTypingExtensions
  - pipenv run tests
  - install_pre_hooks
  |
  +--[if NOT inside git repo]---> initialize_git_repository()
  |                                 - gh repo create
  |                                 - git init
  |                                 - git remote add origin
  |                                 - git branch -M main
  |
  v
commit_changes("feat: add Python source scaffolding")
  - git add --all
  - git commit
  |
  +--[if NOT inside git repo]---> push_to_remote()
  |                                 - git push -u origin main
  |
  v
open_ide({{ cookiecutter.open_ide }})
  - none: skip
  - vscode: code <dir>
  - pycharm: platform-aware launch
  |
  v
DONE
```

### 3.3 Parameter Design

#### cookiecutter.json Changes

```json
{
  "kata_name": "DummyKata",
  "directory_name": "{% now 'local', '%Y%m%d' %}_{{ cookiecutter.kata_name.lower().replace(' ', '_') }}",
  "open_ide": "none",
  "_copy_without_render": [
    ".github/workflows/cicd.yml"
  ]
}
```

| Parameter | Type | Default | Options | Purpose |
|-----------|------|---------|---------|---------|
| `kata_name` | string | "DummyKata" | any valid identifier | Project name |
| `directory_name` | string | dated format | any valid path | Override directory name |
| `open_ide` | string | "none" | none, vscode, pycharm | IDE launch control |

---

## 4. Detailed Component Specifications

### 4.1 is_inside_git_repo()

**Purpose:** Detect if current working directory is inside an existing git repository.

**Algorithm:**
```python
def is_inside_git_repo() -> bool:
    """
    Traverse parent directories looking for .git directory or file.
    Returns True if found, False otherwise.

    Handles:
    - Standard .git directory
    - Git worktrees (.git file)
    - Bare repositories
    - Nested directory structures
    """
    current = Path.cwd()
    while current != current.parent:  # Stop at filesystem root
        git_path = current / ".git"
        if git_path.exists():  # Works for both dir and file
            return True
        current = current.parent
    return False
```

**Edge Cases:**
| Scenario | Detection | Expected Behavior |
|----------|-----------|-------------------|
| `.git` in current dir | Found | Return True |
| `.git` N levels up | Found | Return True |
| No `.git` anywhere | Not found | Return False |
| Git worktree (.git file) | Found | Return True |
| Symlinked .git | Found | Return True |

### 4.2 setup_development_environment()

**Purpose:** Install all development dependencies and quality gates.

**Operations:**
1. `pipenv install --dev` - Install Python dependencies
2. `pipenv run forceTypingExtensions` - Fix typing extensions
3. `pipenv run tests` - Verify environment works
4. `pipenv run install_pre_hooks` - Install pre-commit hooks

**Error Handling:** Fatal - any failure stops execution.

### 4.3 initialize_git_repository()

**Purpose:** Create new GitHub repository and initialize local git.

**Precondition:** Only called when `is_inside_git_repo() == False`

**Operations:**
1. `gh repo create {directory_name} --private`
2. `git init`
3. `git remote add origin git@github.com:undeadgrishnackh/{directory_name}.git`
4. `git branch -M main`

### 4.4 commit_changes()

**Purpose:** Stage and commit all changes.

**Operations:**
1. `git add --all`
2. `git commit -m "{message}"`

**Note:** Always runs, regardless of git detection result.

### 4.5 push_to_remote()

**Purpose:** Push commits to remote origin.

**Precondition:** Only called when `is_inside_git_repo() == False` (new repo was created)

**Operations:**
1. `git push -u origin main`

### 4.6 open_ide()

**Purpose:** Open IDE based on user preference.

**Algorithm:**
```python
def open_ide(ide_choice: str) -> None:
    """
    Open specified IDE or skip if 'none'.
    Non-fatal errors - print warning and continue.
    """
    if ide_choice == "none":
        return

    if ide_choice == "vscode":
        _try_command("code", ["."])

    elif ide_choice == "pycharm":
        # Try pycharm CLI first, fallback to macOS open -a
        if not _try_command("pycharm", ["."]):
            if sys.platform == "darwin":
                _try_command("open", ["-a", "PyCharm", "."])
```

**Error Handling:** Non-fatal - print warning, continue execution.

---

## 5. Architecture Decision Records (ADRs)

### ADR-001: Git Detection Algorithm

**Decision:** Stop at first `.git` found (nearest ancestor).

**Context:** Should detection continue to find "outermost" repo?

**Rationale:**
- Nearest `.git` determines current git context
- Outermost detection adds complexity without benefit
- Standard git behavior uses nearest `.git`

**Status:** APPROVED

### ADR-002: Directory Name as Implicit Signal

**Decision:** Explicit `directory_name` parameter does NOT automatically skip git operations.

**Context:** Should `directory_name=source` always skip repo creation?

**Rationale:**
- Separation of concerns: parameter controls naming, detection controls git
- Explicit is better than implicit
- User can still create named repos in clean directories

**Status:** APPROVED

### ADR-003: IDE Failure Handling

**Decision:** Print warning to stdout, no file logging.

**Context:** Should IDE failures be logged to file?

**Rationale:**
- Hooks should not create unexpected files
- Stdout is appropriate for transient warnings
- Keeps hook behavior simple and predictable

**Status:** APPROVED

### ADR-004: Invalid IDE Parameter Handling

**Decision:** Fail loudly with clear error message.

**Context:** Should invalid `open_ide` values default to `none`?

**Rationale:**
- Explicit errors prevent misconfiguration
- User knows immediately if typo occurred
- Automation scripts catch errors early

**Status:** APPROVED

---

## 6. Interface Contracts

### 6.1 Input Contract (cookiecutter.json)

```json
{
  "kata_name": {
    "type": "string",
    "pattern": "^[_a-zA-Z][_a-zA-Z0-9]+$",
    "required": true
  },
  "directory_name": {
    "type": "string",
    "default": "{% now 'local', '%Y%m%d' %}_{{ cookiecutter.kata_name }}"
  },
  "open_ide": {
    "type": "string",
    "enum": ["none", "vscode", "pycharm"],
    "default": "none"
  }
}
```

### 6.2 Output Contract

| Scenario | Git Operations | IDE | Exit Code |
|----------|---------------|-----|-----------|
| Inside existing repo | Skip creation | Based on parameter | 0 |
| Clean directory | Full git init | Based on parameter | 0 |
| IDE not found | Warning only | Skipped | 0 |
| Environment failure | N/A | N/A | Non-zero |

---

## 7. Quality Attributes

### 7.1 Performance

- No performance requirements (one-time execution)
- Subprocess calls are I/O bound, not CPU bound

### 7.2 Reliability

- Git detection: Must work 100% of time
- IDE opening: Graceful degradation (warning, not error)
- Environment setup: Must succeed for usable output

### 7.3 Security

- No credentials stored in hook
- Uses existing `gh` CLI authentication
- No network calls beyond `gh` and `git push`

### 7.4 Maintainability

- Single file, ~100 LOC total
- Clear function responsibilities
- Standard library only

---

## 8. Testing Strategy

### 8.1 Unit Tests (hooks/tests/)

| Test | Purpose |
|------|---------|
| test_is_inside_git_repo_found | .git in current dir |
| test_is_inside_git_repo_parent | .git in parent dir |
| test_is_inside_git_repo_not_found | No .git anywhere |
| test_is_inside_git_repo_worktree | .git file (worktree) |
| test_open_ide_none | No IDE opens |
| test_open_ide_vscode | VS Code command called |
| test_open_ide_pycharm | PyCharm command called |
| test_open_ide_invalid | Error raised |

### 8.2 Integration Tests

| Test | Purpose |
|------|---------|
| test_full_flow_clean_directory | New repo creation |
| test_full_flow_existing_repo | Git ops skipped |
| test_ide_not_installed | Warning printed |

---

## 9. Implementation Plan

### Phase 1: cookiecutter.json Update
- Add `open_ide` parameter with default "none"
- Estimated: 5 minutes

### Phase 2: post_gen_project.py Refactor
- Extract functions from monolithic script
- Add `is_inside_git_repo()` function
- Conditional git operations based on detection
- Add IDE handling with platform awareness
- Estimated: 2 hours

### Phase 3: Testing
- Unit tests for detection function
- Integration tests for full workflow
- Manual testing on macOS
- Estimated: 1 hour

---

## 10. Handoff to DISTILL Wave

### Deliverables for Acceptance Designer

1. This architecture design document
2. Architecture diagrams (C4 model)
3. ADRs for key decisions
4. Component specifications with test requirements

### Acceptance Criteria for DISTILL

The acceptance designer should create tests for:
- Git detection scenarios (3 scenarios)
- Directory naming scenarios (3 scenarios)
- IDE control scenarios (4 scenarios)
- Error handling scenarios (3 scenarios)

---

## Document Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Solution Architect | Morgan | PENDING | - |
| Visual Architect | Archer | PENDING | - |
| Reviewer | Architect-Reviewer | PENDING | - |
