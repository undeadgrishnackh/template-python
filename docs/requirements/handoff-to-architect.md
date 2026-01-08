# DISCUSS Wave Handoff: Requirements to Architecture

**Handoff ID:** HANDOFF-DISCUSS-DESIGN-2026-01-08
**From:** Riley (Product Owner - DISCUSS Wave)
**To:** Morgan (Solution Architect - DESIGN Wave)
**Date:** 2026-01-08
**Status:** READY FOR DESIGN

---

## 1. Handoff Summary

The DISCUSS wave has completed requirements gathering, stakeholder analysis, and user story creation for the Python Cookiecutter Template Enhancement project.

**Scope:** 3 features enabling integration with 5D-Wave workflows and monorepo architectures

**DoR Status:** PASSED (all 8 checklist items validated)

**Reviewer Status:** APPROVED by product-owner-reviewer

---

## 2. Deliverables Package

### 2.1 Documents Delivered

| Document | Location | Purpose |
|----------|----------|---------|
| Requirements Specification | `docs/requirements/requirements.md` | Formal requirements with NFRs |
| User Stories | `docs/requirements/user-stories.md` | LeanUX stories with UAT scenarios |
| Original Analysis | `docs/REQUIREMENTS-git-integration.md` | Stakeholder-approved source document |
| This Handoff | `docs/requirements/handoff-to-architect.md` | Transition context |

### 2.2 Validation Status

| Quality Gate | Status | Evidence |
|--------------|--------|----------|
| DoR Validation | PASSED | All 8 items validated |
| Peer Review | APPROVED | product-owner-reviewer approval |
| Stakeholder Sign-off | APPROVED | Requirements document v2.0 accepted |

---

## 3. Architecture Context

### 3.1 System Under Modification

**Repository:** `gh:undeadgrishnackh/_template_Python_`
**Type:** Cookiecutter template with post-generation hooks

**Key Files:**
- `cookiecutter.json` - Parameter definitions
- `hooks/post_gen_project.py` - Post-generation automation

### 3.2 Current Architecture

```
_template_Python_/
+-- cookiecutter.json              # Template parameters
+-- {{cookiecutter.directory_name}}/
|   +-- Pipfile                    # Python dependencies
|   +-- .pre-commit-config.yaml    # Quality gate configuration
|   +-- modules/                   # Source code
|   +-- tests/                     # Test code
+-- hooks/
    +-- post_gen_project.py        # Post-generation automation
```

**Current post_gen_project.py behavior:**
1. Create GitHub repository (`gh repo create`)
2. Initialize git (`git init`)
3. Add remote and push
4. Install pipenv dependencies
5. Install pre-commit hooks
6. Open VS Code (`code .`)

### 3.3 Target Architecture Changes

**No new components** - modification of existing hook behavior

**Changes Required:**
1. Add `is_inside_git_repo()` detection function
2. Conditional execution of git operations
3. Add `open_ide` parameter handling
4. Platform-aware IDE launching

---

## 4. Feature Summary for Architect

### Feature 1: Smart Git Detection

**Business Need:** Enable 5D-Wave agents to scaffold Python inside existing repos

**Technical Requirement:**
- Traverse parent directories for `.git` presence
- Skip repo creation when detected
- Always run environment setup and validation commit

**Algorithm (Pseudocode):**
```python
def is_inside_git_repo() -> bool:
    current = Path.cwd()
    while current != current.parent:
        if (current / ".git").exists():
            return True
        current = current.parent
    return False
```

### Feature 2: Configurable Directory Name

**Business Need:** Support monorepo integration without dated prefixes

**Technical Requirement:**
- New `directory_name` parameter in cookiecutter.json
- Skip `kata_name` prompt when `directory_name` provided
- Also serves as explicit signal for git detection skip

### Feature 3: IDE Opening Control

**Business Need:** Support headless/CI environments and IDE preferences

**Technical Requirement:**
- New `open_ide` parameter: `none` (default), `vscode`, `pycharm`
- Platform-aware IDE command execution
- Non-fatal failures (warning only)

---

## 5. Constraints for Architect

### 5.1 Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| Python 3.11+ only | Template already requires modern Python |
| No external dependencies | Hook must work with standard library |
| Cross-platform | Must work on macOS, Linux, Windows |
| Single file modification | Changes isolated to `post_gen_project.py` |

### 5.2 Business Constraints

| Constraint | Rationale |
|------------|-----------|
| Backwards compatible | Existing users must not be disrupted |
| Default safe for automation | `open_ide=none` as default |
| ~50 LOC change budget | Minimal modification principle |

### 5.3 Quality Constraints

| Constraint | Rationale |
|------------|-----------|
| Pre-commit hooks work | Quality gates must function after scaffold |
| Validation commit succeeds | Proof that setup is correct |
| No manual intervention | Agentic workflows must complete autonomously |

---

## 6. Risk Assessment

### 6.1 Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Path traversal edge cases | Low | Medium | Test on symlinks, network drives |
| IDE command not found | Medium | Low | Non-fatal with warning |
| Git worktree detection | Low | Medium | Check for `.git` file (not just directory) |

### 6.2 Business Risks

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Breaking change (IDE default) | High | Medium | Document in release notes |
| User confusion | Low | Low | Clear error messages |

---

## 7. Success Criteria for DESIGN Wave

The DESIGN wave is successful when:

1. **Architecture Decision Records** created for:
   - Git detection algorithm selection
   - IDE parameter design
   - Error handling strategy

2. **Component Design** completed for:
   - `is_inside_git_repo()` function
   - Conditional git operation flow
   - IDE launcher with platform awareness

3. **Acceptance Test Specifications** prepared for handoff to DISTILL wave

---

## 8. Questions for Architect

The following questions require architectural decisions:

1. **Git Detection Scope:** Should detection stop at first `.git` found, or continue to find the "outermost" repo?

2. **Directory Name as Signal:** If `directory_name=source`, should this ALWAYS skip repo creation regardless of `.git` detection? (Current spec says yes)

3. **IDE Failure Handling:** Should IDE failures be logged to a file, or only printed to stdout?

4. **Parameter Validation:** Should invalid `open_ide` values (e.g., "vim") fail loudly or default to `none`?

---

## 9. Handoff Checklist

| Item | Status |
|------|--------|
| Requirements document complete | DONE |
| User stories with UAT scenarios | DONE |
| DoR validation passed | DONE |
| Peer review approved | DONE |
| Technical constraints documented | DONE |
| Risk assessment complete | DONE |
| Open questions listed | DONE |
| Handoff package delivered | DONE |

---

## 10. Next Steps

1. **Morgan (Solution Architect)** receives this handoff
2. **DESIGN Wave** begins with architecture review
3. Create ADRs for key decisions
4. Design component interfaces
5. Prepare acceptance test specifications
6. **Handoff to DISTILL Wave** when architecture complete

---

**Handoff Approved By:**
- Riley (Product Owner): 2026-01-08
- Product-Owner-Reviewer: APPROVED

**Received By:**
- Morgan (Solution Architect): _pending_
