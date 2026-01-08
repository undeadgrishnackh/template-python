# Architecture Design: Python Cookiecutter Template Enhancement

**Document ID:** ARCH-COOKIECUTTER-2026-001
**Version:** 1.0
**Status:** APPROVED
**Date:** 2026-01-08
**Author:** Morgan (Solution Architect)

---

## 1. Executive Summary

This document defines the technical architecture for enhancing the Python cookiecutter template to support three integration scenarios:

1. **Smart Git Detection** - Skip repository creation when inside existing git repositories
2. **Configurable Directory Name** - Allow custom directory names for integration projects
3. **IDE Opening Control** - Parameterized IDE launching (none/vscode/pycharm)

The design follows a minimal-change principle, modifying only `cookiecutter.json` and `hooks/post_gen_project.py` while maintaining full backwards compatibility with existing standalone kata workflows.

---

## 2. Architecture Overview

### 2.1 System Context

```
                    +------------------+
                    |      USER        |
                    | (Human/Agent)    |
                    +--------+---------+
                             |
                             | cookiecutter command
                             v
+-----------------------------------------------------------+
|                 COOKIECUTTER ENGINE                        |
|-----------------------------------------------------------|
|  1. Read cookiecutter.json (parameters)                   |
|  2. Prompt for missing values (interactive)               |
|  3. Render Jinja2 templates                               |
|  4. Execute hooks/post_gen_project.py                     |
+-----------------------------------------------------------+
                             |
                             v
+-----------------------------------------------------------+
|              POST-GENERATION HOOK (Enhanced)              |
|-----------------------------------------------------------|
|  +------------------+  +------------------+                |
|  | Git Detection    |  | IDE Launcher     |                |
|  | Module           |  | Module           |                |
|  +------------------+  +------------------+                |
|            |                    |                          |
|            v                    v                          |
|  +------------------+  +------------------+                |
|  | Conditional      |  | Platform-Aware   |                |
|  | Git Operations   |  | IDE Opening      |                |
|  +------------------+  +------------------+                |
+-----------------------------------------------------------+
                             |
                             v
              +-----------------------------+
              |    GENERATED PROJECT        |
              |  - Pipfile (dependencies)   |
              |  - pre-commit hooks         |
              |  - modules/ tests/          |
              +-----------------------------+
```

### 2.2 Component Architecture

The enhanced `post_gen_project.py` follows a modular design with clear separation of concerns:

```
post_gen_project.py
|
+-- Configuration Module
|   +-- Parameter extraction (cookiecutter variables)
|   +-- Validation (fail-fast on invalid config)
|
+-- Git Detection Module
|   +-- is_inside_git_repo() - Parent traversal algorithm
|   +-- is_integration_mode() - Combined detection logic
|
+-- Command Execution Module
|   +-- run_required_command() - Fatal on failure
|   +-- run_optional_command() - Warning on failure
|
+-- IDE Launcher Module
|   +-- validate_ide_option() - Parameter validation
|   +-- open_ide() - Dispatcher
|   +-- _open_vscode() - VS Code specific
|   +-- _open_pycharm() - PyCharm with macOS fallback
|
+-- Main Orchestration
    +-- validate_configuration()
    +-- setup_environment() - pipenv, pre-commit
    +-- conditional_git_operations()
    +-- open_ide()
```

---

## 3. Parameter Design

### 3.1 cookiecutter.json Changes

**Current:**
```json
{
  "kata_name": "DummyKata",
  "directory_name": "{% now 'local', '%Y%m%d' %}_{{ cookiecutter.kata_name.lower().replace(' ', '_') }}"
}
```

**Enhanced:**
```json
{
  "kata_name": "DummyKata",
  "directory_name": "{% now 'local', '%Y%m%d' %}_{{ cookiecutter.kata_name.lower().replace(' ', '_') }}",
  "open_ide": "none"
}
```

### 3.2 Parameter Specifications

| Parameter | Type | Default | Valid Values | Description |
|-----------|------|---------|--------------|-------------|
| `kata_name` | string | `DummyKata` | Valid Python identifier | Base name for project |
| `directory_name` | string | (derived) | Any valid directory name | Output directory name |
| `open_ide` | string | `none` | `none`, `vscode`, `pycharm` | IDE to open after generation |

### 3.3 Usage Patterns

**Standalone Kata (existing behavior):**
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_
# Prompts for kata_name, creates 20260108_fizzbuzz/
# Full git initialization, no IDE opens
```

**Integration Mode (5D-Wave agent):**
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_ directory_name=source
# No prompt, creates source/
# Skips git repo creation, no IDE opens
```

**Developer with IDE preference:**
```bash
cookiecutter gh:undeadgrishnackh/_template_Python_ open_ide=vscode
# Prompts for kata_name, creates dated directory
# Full git initialization, opens VS Code
```

---

## 4. Component Design

### 4.1 Git Detection Module

**Responsibility:** Determine if running inside an existing git repository

**Interface:**
```python
def is_inside_git_repo() -> bool:
    """Traverse parent directories for .git presence."""

def is_integration_mode() -> bool:
    """Check if integration mode via parameter or git detection."""
```

**Algorithm:** See ADR-001 for detailed specification.

**Design Decisions:**
- Stop at first `.git` found (not outermost)
- Check for both `.git` directory and file (worktrees)
- Use `pathlib.Path` for cross-platform compatibility

### 4.2 IDE Launcher Module

**Responsibility:** Open specified IDE with generated project

**Interface:**
```python
def validate_ide_option(ide_option: str) -> None:
    """Validate IDE option. Exits on invalid value."""

def open_ide(directory: str, ide_option: str) -> None:
    """Open IDE if specified. Non-fatal on failure."""
```

**Design Decisions:**
- Fail fast on invalid parameter values
- Warn (not fail) on missing IDE commands
- PyCharm uses `open -a` fallback on macOS
- Timeout after 10 seconds to prevent hanging

### 4.3 Command Execution Module

**Responsibility:** Execute shell commands with appropriate error handling

**Interface:**
```python
def run_required_command(command: str, description: str) -> None:
    """Execute command. Fails on error."""

def run_optional_command(command: str, description: str) -> bool:
    """Execute command. Warns on error, returns success status."""
```

**Design Decisions:**
- Required commands: pipenv install, pre-commit install, git operations
- Optional commands: IDE opening
- 360 second timeout for long operations (pipenv)
- 10 second timeout for IDE launch

---

## 5. Execution Flow

### 5.1 Standalone Mode Flow

```
START
  |
  v
[1. Validate Configuration]
  |-- Check open_ide value (fail if invalid)
  |-- Check required tools (pipenv, git, gh)
  |
  v
[2. Setup Environment]
  |-- pipenv install --dev
  |-- pipenv run forceTypingExtensions
  |-- pipenv run tests (dry run)
  |
  v
[3. Git Operations (FULL)]
  |-- gh repo create (GitHub)
  |-- git init
  |-- pipenv run install_pre_hooks
  |-- git remote add origin
  |-- git branch -M main
  |-- git add --all
  |-- git commit
  |-- git push -u origin main
  |
  v
[4. Open IDE (if specified)]
  |-- open_ide("none") -> skip
  |-- open_ide("vscode") -> code .
  |-- open_ide("pycharm") -> pycharm/open -a
  |
  v
END (success)
```

### 5.2 Integration Mode Flow

```
START
  |
  v
[1. Validate Configuration]
  |-- Check open_ide value (fail if invalid)
  |-- Check required tools (pipenv, git)
  |-- Note: gh NOT required (no repo creation)
  |
  v
[2. Setup Environment]
  |-- pipenv install --dev
  |-- pipenv run forceTypingExtensions
  |-- pipenv run tests (dry run)
  |
  v
[3. Git Operations (PARTIAL)]
  |-- SKIP: gh repo create
  |-- SKIP: git init
  |-- pipenv run install_pre_hooks
  |-- SKIP: git remote add origin
  |-- SKIP: git branch -M main
  |-- git add --all
  |-- git commit (validation commit)
  |-- SKIP: git push
  |
  v
[4. Open IDE (if specified)]
  |-- Same as standalone
  |
  v
END (success)
```

### 5.3 Decision Logic

```python
def determine_execution_mode() -> str:
    """Determine which operations to run."""
    directory_name = "{{ cookiecutter.directory_name }}"
    kata_name = "{{ cookiecutter.kata_name }}"

    # Check if directory_name is explicitly provided (not default format)
    is_default_format = directory_name.endswith(
        f"_{kata_name.lower().replace(' ', '_')}"
    )

    # Integration mode if: explicit directory_name OR inside git repo
    if not is_default_format or is_inside_git_repo():
        return "integration"
    else:
        return "standalone"
```

---

## 6. Error Handling

### 6.1 Error Categories

| Category | Response | Exit Code |
|----------|----------|-----------|
| Invalid configuration | Fail immediately with guidance | 1 |
| Missing prerequisites | Fail with installation instructions | 1 |
| Git operation failure | Fail (standalone only) | 1 |
| IDE command not found | Warn and continue | 0 |
| IDE launch timeout | Warn and continue | 0 |

### 6.2 Error Messages

**Configuration Error:**
```
ERROR: Invalid open_ide value: 'vim'
  -> Valid options: none, pycharm, vscode
```

**Prerequisite Error:**
```
ERROR: pipenv not found
  -> Install with: pip install pipenv
```

**Non-Fatal Warning:**
```
WARNING: VS Code 'code' command not found, skipping IDE open
```

---

## 7. Backwards Compatibility

### 7.1 Preserved Behaviors

| Behavior | Standalone Mode | Status |
|----------|-----------------|--------|
| Date-prefixed directory | `20260108_kata_name` | Preserved |
| GitHub repo creation | `gh repo create` | Preserved |
| Git push to origin | `git push -u origin main` | Preserved |
| Pipenv environment | `pipenv install --dev` | Preserved |
| Pre-commit hooks | `pipenv run install_pre_hooks` | Preserved |
| Validation commit | `git commit` | Preserved |

### 7.2 Breaking Changes

| Change | Previous | New | Migration |
|--------|----------|-----|-----------|
| Default IDE | VS Code opened | No IDE opens | Add `open_ide=vscode` |

### 7.3 Migration Guide

Users who want VS Code to open automatically should update their workflow:

```bash
# Old (implicit VS Code)
cookiecutter gh:undeadgrishnackh/_template_Python_

# New (explicit VS Code)
cookiecutter gh:undeadgrishnackh/_template_Python_ open_ide=vscode
```

---

## 8. Quality Attributes

### 8.1 Performance

- Git detection: O(d) where d = directory depth (typically < 10)
- No additional network calls in integration mode
- IDE timeout prevents hanging (10 seconds)

### 8.2 Reliability

- Fail-fast validation prevents partial execution
- Cross-platform path handling via pathlib
- Non-fatal IDE errors preserve generation success

### 8.3 Maintainability

- Modular design with clear responsibilities
- Centralized error handling patterns
- Comprehensive ADRs for future reference

### 8.4 Testability

- Pure functions for git detection (mockable)
- Clear input/output boundaries
- Deterministic behavior based on parameters

---

## 9. Security Considerations

### 9.1 No New Attack Surface

- No network calls beyond existing git/gh operations
- No user input execution (parameters are validated)
- No file system access beyond generation directory

### 9.2 Validated Parameters

- `open_ide` limited to whitelist (`none`, `vscode`, `pycharm`)
- Invalid values rejected before execution

---

## 10. Implementation Scope

### 10.1 Files to Modify

| File | Changes | LOC Delta |
|------|---------|-----------|
| `cookiecutter.json` | Add `open_ide` parameter | +1 |
| `hooks/post_gen_project.py` | Add detection, IDE, error handling | ~+60 |

### 10.2 Estimated Complexity

- **Risk:** Low - isolated changes to single hook file
- **Effort:** ~2 days implementation
- **Testing:** Unit tests for detection, integration tests for flows

---

## 11. Architecture Decision Records

The following ADRs document key architectural decisions:

| ADR | Title | Status |
|-----|-------|--------|
| ADR-001 | Git Repository Detection Algorithm | Accepted |
| ADR-002 | Directory Name Parameter as Integration Signal | Accepted |
| ADR-003 | IDE Opening Parameter Design | Accepted |
| ADR-004 | Error Handling Strategy | Accepted |

---

## 12. Acceptance Test Specifications

### 12.1 Git Detection Tests

| Test ID | Scenario | Expected Result |
|---------|----------|-----------------|
| GIT-001 | .git in current directory | `is_inside_git_repo()` returns True |
| GIT-002 | .git 3 levels up | `is_inside_git_repo()` returns True |
| GIT-003 | No .git in parent tree | `is_inside_git_repo()` returns False |
| GIT-004 | .git is file (worktree) | `is_inside_git_repo()` returns True |

### 12.2 Integration Mode Tests

| Test ID | Scenario | Expected Result |
|---------|----------|-----------------|
| INT-001 | `directory_name=source` provided | Skip repo creation |
| INT-002 | Default directory + inside git | Skip repo creation |
| INT-003 | Default directory + clean dir | Full git init |

### 12.3 IDE Control Tests

| Test ID | Scenario | Expected Result |
|---------|----------|-----------------|
| IDE-001 | `open_ide=none` | No IDE opens |
| IDE-002 | `open_ide=vscode` + code installed | VS Code opens |
| IDE-003 | `open_ide=vscode` + code missing | Warning, continue |
| IDE-004 | `open_ide=vim` (invalid) | Error, exit 1 |

---

## 13. Handoff to DISTILL Wave

### 13.1 Deliverables

- [x] Architecture document (this file)
- [x] ADR-001: Git Detection Algorithm
- [x] ADR-002: Directory Name as Integration Signal
- [x] ADR-003: IDE Parameter Design
- [x] ADR-004: Error Handling Strategy

### 13.2 Acceptance Test Specifications

Ready for `acceptance-designer` to create detailed BDD acceptance tests from:
- Section 12 test specifications
- User stories UAT scenarios (US-001, US-002, US-003)
- Edge cases from requirements document

### 13.3 Implementation Guidance

- Algorithm pseudocode provided in ADR-001
- IDE launcher implementation in ADR-003
- Error handling patterns in ADR-004
- Flow diagrams in Section 5

---

## Document Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Solution Architect | Morgan | APPROVED | 2026-01-08 |
| Peer Reviewer | Morgan (Solution-Architect-Reviewer) | APPROVED | 2026-01-08 |
| Acceptance Designer | (Ready for handoff) | PENDING | - |

---

## Review Sign-Off

**Reviewer:** Morgan (Solution-Architect-Reviewer mode)
**Review Date:** 2026-01-08
**Review Scope:** Architecture completeness, ADR alignment, implementation guidance, quality attributes, backwards compatibility

**Critical Findings:** None blocking
**Recommendations:** See concerns section in review notes
**Overall Assessment:** Architecture is complete, coherent, and production-ready for DISTILL wave
