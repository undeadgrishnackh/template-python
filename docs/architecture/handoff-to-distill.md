# DESIGN Wave Handoff: Architecture to Acceptance Tests

**Handoff ID:** HANDOFF-DESIGN-DISTILL-2026-01-08
**From:** Morgan (Solution Architect) / Archer (Visual Architect)
**To:** Taylor (Acceptance Designer - DISTILL Wave)
**Date:** 2026-01-08
**Status:** READY FOR DISTILL

---

## 1. Handoff Summary

The DESIGN wave has completed architecture design, component specifications, and visual documentation for the Python Cookiecutter Template Enhancement.

**Scope:** 3 features with clear component boundaries and interface contracts
**ADRs Created:** 4 architectural decisions documented
**Diagrams:** 5 PlantUML diagrams (C4 + flows)

---

## 2. Deliverables Package

### 2.1 Documents Delivered

| Document | Location | Purpose |
|----------|----------|---------|
| Architecture Design | `docs/architecture/architecture-design.md` | Complete technical specification |
| C4 Context Diagram | `docs/architecture/diagrams/c4-context.puml` | System context |
| C4 Container Diagram | `docs/architecture/diagrams/c4-container.puml` | Container view |
| C4 Component Diagram | `docs/architecture/diagrams/c4-component.puml` | Component detail |
| Execution Flow | `docs/architecture/diagrams/flow-execution.puml` | Main flow |
| Git Detection Flow | `docs/architecture/diagrams/flow-git-detection.puml` | Detection algorithm |
| Sequence Scenarios | `docs/architecture/diagrams/sequence-scenarios.puml` | All 3 scenarios |
| This Handoff | `docs/architecture/handoff-to-distill.md` | Transition context |

### 2.2 Previous Wave Artifacts (from DISCUSS)

| Document | Location |
|----------|----------|
| Requirements | `docs/requirements/requirements.md` |
| User Stories | `docs/requirements/user-stories.md` |
| DISCUSS Handoff | `docs/requirements/handoff-to-architect.md` |

---

## 3. Architecture Decisions Summary

### ADR-001: Git Detection Algorithm
**Decision:** Stop at first `.git` found (nearest ancestor)
**Rationale:** Matches standard git behavior, simplest implementation

### ADR-002: Directory Name Independence
**Decision:** `directory_name` does NOT automatically skip git operations
**Rationale:** Separation of concerns - naming vs. git behavior

### ADR-003: IDE Failure Handling
**Decision:** Print warning to stdout, no file logging
**Rationale:** Hooks should not create unexpected files

### ADR-004: Invalid IDE Parameter
**Decision:** Fail loudly with clear error message
**Rationale:** Explicit errors prevent misconfiguration

---

## 4. Component Specifications for Testing

### 4.1 is_inside_git_repo()

**Signature:** `def is_inside_git_repo() -> bool`

**Test Cases Required:**

| Test ID | Scenario | Setup | Expected |
|---------|----------|-------|----------|
| GIT-001 | .git in current dir | Create temp dir with .git | True |
| GIT-002 | .git in parent dir | Create nested structure | True |
| GIT-003 | .git 3 levels up | Create deep nesting | True |
| GIT-004 | No .git anywhere | Clean temp hierarchy | False |
| GIT-005 | .git file (worktree) | Create .git as file | True |
| GIT-006 | Sibling .git | .git in sibling, not parent | False |

### 4.2 open_ide()

**Signature:** `def open_ide(ide_choice: str) -> None`

**Test Cases Required:**

| Test ID | Scenario | Input | Expected |
|---------|----------|-------|----------|
| IDE-001 | Skip IDE | "none" | No subprocess call |
| IDE-002 | Open VS Code | "vscode" | `code .` executed |
| IDE-003 | Open PyCharm | "pycharm" | `pycharm .` or macOS fallback |
| IDE-004 | Invalid value | "vim" | Exception raised |
| IDE-005 | Command not found | "vscode" (no code CLI) | Warning printed, no error |

### 4.3 Conditional Git Operations

**Test Cases Required:**

| Test ID | Scenario | Git Detection | Expected Operations |
|---------|----------|---------------|---------------------|
| FLOW-001 | Inside repo | True | Skip: create, init, push |
| FLOW-002 | Clean dir | False | Run: create, init, push |
| FLOW-003 | Always run | Any | pipenv, pre-commit, commit |

---

## 5. Acceptance Test Specifications

### 5.1 Feature 1: Git Repository Detection

```gherkin
Feature: Smart Git Repository Detection

  Scenario: Agent detects existing repository and skips creation
    Given a project directory "/my-trading-bot" exists
    And "/my-trading-bot/.git" directory exists
    And current directory is "/my-trading-bot/"
    When cookiecutter executes with directory_name=source
    Then is_inside_git_repo() returns True
    And "gh repo create" is NOT executed
    And "git init" is NOT executed
    And "git push" is NOT executed
    But "pipenv install --dev" IS executed
    And "git add --all" IS executed
    And "git commit" IS executed

  Scenario: Nested monorepo detection
    Given a project directory "/enterprise/services/" exists
    And "/enterprise/.git" directory exists (2 levels up)
    When cookiecutter executes with directory_name=trading-engine
    Then is_inside_git_repo() returns True
    And git repository creation is skipped

  Scenario: Clean directory triggers full initialization
    Given a directory "/Users/dev/katas/" exists
    And no ".git" exists in parent tree
    When cookiecutter executes
    Then is_inside_git_repo() returns False
    And "gh repo create" IS executed
    And "git init" IS executed
    And "git push" IS executed
```

### 5.2 Feature 2: Configurable Directory Name

```gherkin
Feature: Configurable Source Directory Name

  Scenario: Explicit directory name accepted
    When cookiecutter executes with directory_name=source
    Then output directory is named "source"
    And no dated prefix is added

  Scenario: Default behavior preserved
    When cookiecutter executes without directory_name parameter
    And user enters "fizzbuzz" for kata_name
    Then output directory is named "YYYYMMDD_fizzbuzz"
```

### 5.3 Feature 3: IDE Opening Control

```gherkin
Feature: IDE Opening Control

  Scenario: Default is no IDE
    When cookiecutter executes without open_ide parameter
    Then no IDE is launched
    And execution completes successfully

  Scenario: VS Code requested
    When cookiecutter executes with open_ide=vscode
    Then "code <directory>" command is executed

  Scenario: PyCharm requested on macOS
    Given platform is macOS
    When cookiecutter executes with open_ide=pycharm
    Then attempts "pycharm <directory>" first
    And falls back to "open -a PyCharm <directory>" if needed

  Scenario: IDE command not found
    Given VS Code CLI is not installed
    When cookiecutter executes with open_ide=vscode
    Then warning is printed to stdout
    But execution completes with exit code 0

  Scenario: Invalid IDE value
    When cookiecutter executes with open_ide=vim
    Then error is raised with message about valid options
```

---

## 6. Implementation Files

### Files to Modify

| File | Changes Required |
|------|------------------|
| `cookiecutter.json` | Add `open_ide` parameter |
| `hooks/post_gen_project.py` | Refactor to component architecture |

### Files NOT Modified

| File | Reason |
|------|--------|
| `hooks/pre_gen_project.py` | No changes to validation logic |
| Template files | No structural changes |

---

## 7. Dependencies and Constraints

### No External Dependencies
- All detection using Python standard library (`pathlib`)
- IDE launching using `subprocess` (already in use)
- No new pip packages required

### Platform Requirements
- Python 3.11+
- Cross-platform (macOS, Linux, Windows)
- Standard library only in hooks

---

## 8. Risk Mitigation for Testing

### High-Risk Areas

| Area | Risk | Mitigation |
|------|------|------------|
| Git detection edge cases | Symlinks, network drives | Mock filesystem in tests |
| IDE command availability | Not installed | Mock subprocess, verify warning |
| Cross-platform paths | Path separators | Use pathlib throughout |

### Testing Environment Needs

- Ability to create temporary directories with .git
- Ability to mock subprocess calls
- Ability to verify stdout output (warnings)

---

## 9. Success Criteria for DISTILL Wave

The DISTILL wave is successful when:

1. **Acceptance Tests Created** covering:
   - All 3 user stories (US-001, US-002, US-003)
   - All UAT scenarios from user stories
   - Edge cases documented in architecture

2. **Test Specifications Complete**:
   - Unit test specifications for each function
   - Integration test specifications for flows
   - Mock strategies documented

3. **Handoff to DEVELOP Wave** ready with:
   - Complete test suite specifications
   - Clear implementation guidance
   - Traceability to requirements

---

## 10. Open Questions for Acceptance Designer

1. **Mock Strategy:** Should git detection tests use real temp directories or pure mocks?

2. **IDE Testing:** How to verify IDE opens without actually launching it?

3. **CI Integration:** Should tests run in GitHub Actions workflow?

---

## 11. Traceability Matrix

| Requirement | User Story | ADR | Component | Test IDs |
|-------------|------------|-----|-----------|----------|
| FR-001 | US-001 | ADR-001 | is_inside_git_repo() | GIT-001 to GIT-006 |
| FR-002 | US-002 | ADR-002 | cookiecutter.json | (parameter test) |
| FR-003 | US-003 | ADR-003, ADR-004 | open_ide() | IDE-001 to IDE-005 |
| NFR-001 | - | - | (all) | FLOW-001 to FLOW-003 |

---

## Handoff Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Solution Architect | Morgan | APPROVED | 2026-01-08 |
| Visual Architect | Archer | APPROVED | 2026-01-08 |
| Reviewer | Pending | - | - |

**Received By:**
- Taylor (Acceptance Designer): _pending_
