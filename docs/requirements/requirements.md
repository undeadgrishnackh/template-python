# Requirements Specification: Python Cookiecutter Template Enhancement

**Document ID:** REQ-COOKIECUTTER-GIT-2026-001
**Version:** 1.0
**Status:** APPROVED (DoR Validated)
**Date:** 2026-01-08
**Author:** Riley (Product Owner)
**Reviewer:** Product-Owner-Reviewer (Approved)

---

## 1. Executive Summary

Enhancement of the Python cookiecutter template to support three integration scenarios:
1. **Smart Git Detection** - Skip repository creation when inside existing git repositories
2. **Configurable Directory Name** - Allow custom directory names for integration projects
3. **IDE Opening Control** - Parameterized IDE launching (none/vscode/pycharm)

These changes enable seamless integration with 5D-Wave agentic workflows and monorepo architectures.

---

## 2. Business Context

### 2.1 Problem Statement

When using the Python cookiecutter template inside an existing git repository, the post-generation hook fails because it attempts to create a new GitHub repository, initialize git, and push changes - operations that conflict with the existing repository structure.

### 2.2 Business Value

| Stakeholder | Value Delivered |
|-------------|-----------------|
| 5D-Wave Agents | Unblocked automated workflows in DESIGN phase |
| Platform Engineers | Seamless monorepo integration |
| Solo Developers | Preserved existing behavior for standalone katas |

### 2.3 Success Metrics

- Zero manual intervention required for 5D-Wave scaffold operations
- 100% backwards compatibility with existing standalone usage
- IDE behavior controllable for headless/CI environments

---

## 3. User Personas

### 3.1 Persona: Agentic AI (5D-Wave Agent)

- **Context:** Executing automated workflows inside pre-initialized project repository
- **Goal:** Scaffold Python production code without human intervention
- **Pain Point:** Git operations designed for greenfield projects block automated pipeline

### 3.2 Persona: Platform Engineer

- **Context:** Adding Python service to existing monorepo with established git history
- **Goal:** Get quality gates (pre-commit, linting, testing) without disrupting version control
- **Pain Point:** Must manually delete generated git artifacts or modify hook script

### 3.3 Persona: Solo Developer

- **Context:** Starting fresh kata or standalone Python project
- **Goal:** Full automation - repo created, pushed to GitHub, IDE opened
- **Pain Point:** None (this is existing default behavior to preserve)

---

## 4. Functional Requirements

### FR-001: Automatic Git Repository Detection

**Priority:** MUST HAVE

**Description:** The post-generation hook SHALL detect when running inside an existing git repository and skip repository creation operations.

**Detection Algorithm:**
```
Traverse parent directories from current working directory
IF .git directory found in any parent -> inside_git_repo = TRUE
IF no .git found at root -> inside_git_repo = FALSE
```

**Operations to Skip (when inside_git_repo = TRUE):**
- `gh repo create`
- `git init`
- `git remote add origin`
- `git branch -M main`
- `git push -u origin main`

**Operations to Execute (always):**
- `pipenv install --dev`
- `pre-commit install`
- `git add --all`
- `git commit -m "feat: add Python source scaffolding"`

### FR-002: Configurable Source Directory Name

**Priority:** MUST HAVE

**Description:** The cookiecutter SHALL accept a `directory_name` parameter to override the default dated directory name format.

**Parameter Specification:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `directory_name` | String | `{{ cookiecutter.today }}_{{ cookiecutter.kata_name }}` | Output directory name |

**Behavior:**
- When `directory_name` is explicitly provided -> use provided value
- When `directory_name` is not provided -> prompt for `kata_name` and use dated format

### FR-003: IDE Opening Control

**Priority:** MUST HAVE

**Description:** The cookiecutter SHALL accept an `open_ide` parameter to control post-generation IDE behavior.

**Parameter Specification:**

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `open_ide` | String | `none` | `none`, `vscode`, `pycharm` | IDE to open after generation |

**Behavior by Option:**
- `none`: No IDE opens (default, safe for automation)
- `vscode`: Execute `code <generated_directory>`
- `pycharm`: Execute `pycharm <generated_directory>` or `open -a "PyCharm" <generated_directory>` on macOS

---

## 5. Non-Functional Requirements

### NFR-001: Backwards Compatibility

**Requirement:** Existing standalone kata workflows SHALL continue to function without modification.

**Acceptance:** Running `cookiecutter gh:undeadgrishnackh/_template_Python_` without parameters produces identical behavior to pre-enhancement version (except IDE defaulting to none).

### NFR-002: Error Resilience

**Requirement:** IDE opening failures SHALL NOT block template generation.

**Acceptance:** If IDE command fails, print warning and continue (non-fatal).

### NFR-003: Cross-Platform Support

**Requirement:** Git detection SHALL work on macOS, Linux, and Windows.

**Acceptance:** Path traversal uses platform-agnostic `pathlib.Path` operations.

---

## 6. Acceptance Criteria (Gherkin)

### Feature 1: Git Repository Detection

```gherkin
Feature: Skip git repo creation inside existing repositories

  Scenario: Cookiecutter detects existing git repository
    Given the 5D-Wave project "my-trading-bot" exists with .git directory
    And current directory is /my-trading-bot/
    When I run: cookiecutter gh:undeadgrishnackh/_template_Python_ directory_name=source
    Then the hook detects /my-trading-bot/.git in parent tree
    And the hook skips: gh repo create, git init, git remote add, git push
    But the hook runs: pipenv install, pre-commit install, git add, git commit

  Scenario: Clean directory triggers full git initialization
    Given I am in /Users/mike/katas/ with no .git in parent tree
    When I run: cookiecutter gh:undeadgrishnackh/_template_Python_
    Then the hook runs ALL git operations (repo create, init, push)
```

### Feature 2: Directory Name Configuration

```gherkin
Feature: Override directory name for integration scenarios

  Scenario: Explicit source directory for 5D-Wave
    Given the 5D-Wave project /my-trading-bot/ exists
    When I run: cookiecutter directory_name=source
    Then create /my-trading-bot/source/ directory
    And do not prompt for kata_name

  Scenario: Default behavior for standalone katas
    Given I am starting a fresh fizzbuzz kata
    When I run: cookiecutter (no directory_name parameter)
    And I enter "fizzbuzz" when prompted
    Then create /20260108_fizzbuzz/ directory
```

### Feature 3: IDE Control

```gherkin
Feature: Control IDE opening via parameter

  Scenario: Default behavior - no IDE
    Given I run: cookiecutter directory_name=source
    When the hook completes
    Then no IDE opens (safe for automation)

  Scenario: Developer requests VS Code
    When I run: cookiecutter open_ide=vscode
    Then VS Code opens with generated directory

  Scenario: Developer requests PyCharm
    When I run: cookiecutter open_ide=pycharm
    Then PyCharm opens with generated directory
```

---

## 7. Edge Cases

### Git Detection Edge Cases

| Scenario | Detection | Behavior |
|----------|-----------|----------|
| `.git` in current directory | Found | Skip repo creation |
| `.git` 3 levels up | Found | Skip repo creation |
| `.git` in sibling directory | Not found | Full git init |
| Bare git repository | Found `.git` file | Skip repo creation |
| Git worktree | Found `.git` file | Skip repo creation |

### IDE Command Failures

| Scenario | Behavior |
|----------|----------|
| `code` command not found | Print warning, continue (non-fatal) |
| `pycharm` command not found | Try macOS fallback, warn on failure |
| IDE fails to open | Print warning, continue (non-fatal) |

---

## 8. Implementation Scope

### Files to Modify

| File | Changes |
|------|---------|
| `cookiecutter.json` | Add `open_ide` parameter with default `none` |
| `hooks/post_gen_project.py` | Add `is_inside_git_repo()`, conditional git ops, IDE handling |

### Breaking Change Notice

- **Change:** Default IDE behavior changes from "open VS Code" to "open nothing"
- **Migration:** Users wanting VS Code must add `open_ide=vscode`
- **Rationale:** Safe default for automation; interactive users can easily add parameter

---

## 9. Definition of Ready Validation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Concrete 5D-Wave workflow example provided |
| User/persona identified | PASS | 3 personas with real context |
| 3+ domain examples | PASS | Multiple scenarios with real data |
| UAT scenarios (3-7) | PASS | 7 Gherkin scenarios covering all features |
| Acceptance criteria from UAT | PASS | All AC derived from scenarios |
| Right-sized (1-3 days) | PASS | 2 files, ~50 LOC changes |
| Technical notes present | PASS | Edge cases, error handling documented |
| Dependencies tracked | PASS | No external dependencies |

**DoR Status:** PASSED

---

## 10. Traceability

| Requirement ID | User Story | Business Objective |
|----------------|------------|-------------------|
| FR-001 | US-001 | Enable 5D-Wave automation |
| FR-002 | US-002 | Support monorepo integration |
| FR-003 | US-003 | Support headless/CI environments |

---

## Document Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Riley | APPROVED | 2026-01-08 |
| Reviewer | Product-Owner-Reviewer | APPROVED | 2026-01-08 |
| Architect Handoff | Pending | - | - |
