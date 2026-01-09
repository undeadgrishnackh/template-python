# Requirements Specification: Python Cookiecutter Template Enhancement

**Document ID:** REQ-COOKIECUTTER-GIT-2026-001
**Version:** 1.1
**Status:** APPROVED (DoR Validated)
**Date:** 2026-01-09
**Author:** Riley (Product Owner)
**Reviewer:** Product-Owner-Reviewer (Approved)

---

## 1. Executive Summary

Enhancement of the Python cookiecutter template to support five integration scenarios:
1. **Smart Git Detection** - Skip repository creation when inside existing git repositories
2. **Configurable Directory Name** - Allow custom directory names for integration projects
3. **IDE Opening Control** - Parameterized IDE launching (none/vscode/pycharm)
4. **Configurable GitHub Username** - Allow custom GitHub username for repository creation
5. **Repository Visibility Control** - Choose public or private repository creation

These changes enable seamless integration with 5D-Wave agentic workflows, monorepo architectures, and multi-user GitHub configurations.

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
| Multi-Account Users | Flexibility to create repos under different GitHub accounts |
| OSS Contributors | Control over repository visibility (public/private) |

### 2.3 Success Metrics

- Zero manual intervention required for 5D-Wave scaffold operations
- 100% backwards compatibility with existing standalone usage
- IDE behavior controllable for headless/CI environments
- Clear, actionable error messages when prerequisites fail (git, gh CLI, username validation)
- Repository creation works for any valid GitHub username

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

### 3.4 Persona: Multi-Account Developer

- **Context:** Developer with multiple GitHub accounts (personal, work, client projects)
- **Goal:** Create repositories under the correct GitHub account without editing template code
- **Pain Point:** Username hardcoded to "undeadgrishnackh" - must fork/modify template for different accounts

### 3.5 Persona: OSS Contributor

- **Context:** Developer starting open-source or private projects
- **Goal:** Control whether new repository is public (OSS) or private (proprietary/early-stage)
- **Pain Point:** No control over repository visibility at creation time

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

### FR-004: Configurable GitHub Username

**Priority:** MUST HAVE

**Description:** The cookiecutter SHALL accept a `github_username` parameter to specify the GitHub account for repository creation, replacing the hardcoded "undeadgrishnackh" value.

**Parameter Specification:**

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `github_username` | String | `undeadgrishnackh` | GitHub username for repository creation |

**Prerequisite Validation (Standalone Mode Only):**

Before repository creation in standalone mode, the hook SHALL validate:

1. **Git Installation Check:**
   - Verify `git --version` succeeds
   - Error: "Git is not installed. Please install git and try again."

2. **Git Configuration Check:**
   - Verify `git config user.name` returns a value
   - Verify `git config user.email` returns a value
   - Error: "Git is not configured. Run: git config --global user.name 'Your Name' && git config --global user.email 'your@email.com'"

3. **GitHub CLI Installation Check:**
   - Verify `gh --version` succeeds
   - Error: "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/"

4. **GitHub CLI Authentication Check:**
   - Verify `gh auth status` succeeds
   - Error: "GitHub CLI is not authenticated. Run: gh auth login"

5. **GitHub Username Validation:**
   - Call `gh api users/{github_username}` to verify account exists
   - Error: "GitHub user '{github_username}' not found. Please check the username."

**Failure Behavior:** HARD FAIL - Stop immediately with clear error message, no files generated.

**Behavior:**
- When `inside_git_repo = TRUE` -> Skip all prerequisite checks (username not used)
- When `inside_git_repo = FALSE` -> Run all prerequisite checks before any file generation
- Repository created as: `gh repo create {github_username}/{project_name}`

### FR-005: Repository Visibility Control

**Priority:** MUST HAVE

**Description:** The cookiecutter SHALL accept a `repo_type` parameter to control whether the created repository is public or private.

**Parameter Specification:**

| Parameter | Type | Default | Options | Description |
|-----------|------|---------|---------|-------------|
| `repo_type` | String | `public` | `public`, `private` | Repository visibility on GitHub |

**Behavior by Option:**
- `public`: Execute `gh repo create --public` (default, accessible to everyone)
- `private`: Execute `gh repo create --private` (requires GitHub subscription for unlimited private repos)

**Default Rationale:** Public is the default because not all GitHub users have paid subscriptions that allow unlimited private repositories.

**Behavior:**
- When `inside_git_repo = TRUE` -> Parameter ignored (no repo creation)
- When `inside_git_repo = FALSE` -> Apply visibility setting during `gh repo create`

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

### Feature 4: GitHub Username Configuration

```gherkin
Feature: Configurable GitHub username for repository creation

  Scenario: Custom GitHub username with valid account
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And git is installed and configured
    And gh CLI is installed and authenticated
    When I run: cookiecutter github_username=octocat
    Then the hook validates GitHub user "octocat" exists via gh api
    And the repository is created as "octocat/{project_name}"

  Scenario: Default username when not specified
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And git is installed and configured
    And gh CLI is installed and authenticated
    When I run: cookiecutter (no github_username parameter)
    Then the hook uses default username "undeadgrishnackh"
    And the repository is created as "undeadgrishnackh/{project_name}"

  Scenario: Invalid GitHub username causes hard fail
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And git is installed and configured
    And gh CLI is installed and authenticated
    When I run: cookiecutter github_username=nonexistent-user-xyz-12345
    Then the hook fails with error "GitHub user 'nonexistent-user-xyz-12345' not found"
    And no files are generated

  Scenario: Git not installed causes hard fail
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And git is NOT installed
    When I run: cookiecutter github_username=octocat
    Then the hook fails with error "Git is not installed"
    And no files are generated

  Scenario: GitHub CLI not authenticated causes hard fail
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And git is installed and configured
    And gh CLI is installed but NOT authenticated
    When I run: cookiecutter github_username=octocat
    Then the hook fails with error "GitHub CLI is not authenticated"
    And no files are generated

  Scenario: Integration mode skips username validation
    Given the 5D-Wave project "my-trading-bot" exists with .git directory
    And current directory is /my-trading-bot/
    When I run: cookiecutter directory_name=source github_username=invalid-user
    Then the hook skips all prerequisite validation
    And no repository is created
    And files are generated successfully
```

### Feature 5: Repository Visibility Control

```gherkin
Feature: Control repository visibility (public/private)

  Scenario: Create public repository (default)
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And all prerequisites are met
    When I run: cookiecutter github_username=octocat
    Then the repository is created with: gh repo create octocat/{project_name} --public

  Scenario: Create public repository (explicit)
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And all prerequisites are met
    When I run: cookiecutter github_username=octocat repo_type=public
    Then the repository is created with: gh repo create octocat/{project_name} --public

  Scenario: Create private repository
    Given I am in /Users/mike/katas/ with no .git in parent tree
    And all prerequisites are met
    When I run: cookiecutter github_username=octocat repo_type=private
    Then the repository is created with: gh repo create octocat/{project_name} --private

  Scenario: Integration mode ignores repo_type
    Given the 5D-Wave project "my-trading-bot" exists with .git directory
    And current directory is /my-trading-bot/
    When I run: cookiecutter directory_name=source repo_type=private
    Then no repository is created
    And the repo_type parameter is ignored
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

### Prerequisite Validation Edge Cases (FR-004)

| Scenario | Behavior |
|----------|----------|
| Git not installed | HARD FAIL: "Git is not installed. Please install git and try again." |
| Git installed but not configured (no user.name) | HARD FAIL: "Git is not configured. Run: git config --global user.name 'Your Name'" |
| Git installed but not configured (no user.email) | HARD FAIL: "Git is not configured. Run: git config --global user.email 'your@email.com'" |
| gh CLI not installed | HARD FAIL: "GitHub CLI (gh) is not installed. Install from: https://cli.github.com/" |
| gh CLI installed but not authenticated | HARD FAIL: "GitHub CLI is not authenticated. Run: gh auth login" |
| gh authenticated to different account than username | Allow (user may have permission to create repos for orgs/other users) |
| GitHub username does not exist | HARD FAIL: "GitHub user '{username}' not found. Please check the username." |
| GitHub API rate limited | HARD FAIL: "GitHub API rate limit exceeded. Please try again later." |
| Network unavailable during validation | HARD FAIL: "Unable to reach GitHub API. Check your network connection." |
| Inside existing git repo | SKIP all prerequisite checks (parameters ignored) |

### Repository Visibility Edge Cases (FR-005)

| Scenario | Behavior |
|----------|----------|
| `repo_type=public` | Create with `--public` flag |
| `repo_type=private` | Create with `--private` flag |
| `repo_type` not specified | Default to `--public` |
| Invalid `repo_type` value (e.g., "internal") | Cookiecutter template validation rejects before hook runs |
| Inside existing git repo | `repo_type` parameter ignored (no repo creation) |
| Private repo without GitHub subscription | GitHub CLI returns error (handle gracefully with clear message) |

---

## 8. Implementation Scope

### Files to Modify

| File | Changes |
|------|---------|
| `cookiecutter.json` | Add `open_ide`, `github_username`, `repo_type` parameters |
| `hooks/post_gen_project.py` | Add `is_inside_git_repo()`, conditional git ops, IDE handling, prerequisite validation, username/visibility configuration |

### Breaking Change Notice

- **Change:** Default IDE behavior changes from "open VS Code" to "open nothing"
- **Migration:** Users wanting VS Code must add `open_ide=vscode`
- **Rationale:** Safe default for automation; interactive users can easily add parameter

### New Parameters Summary (v1.1)

| Parameter | Type | Default | Options | Used In |
|-----------|------|---------|---------|---------|
| `github_username` | String | `undeadgrishnackh` | Any valid GitHub username | Standalone mode only |
| `repo_type` | String | `public` | `public`, `private` | Standalone mode only |

---

## 9. Definition of Ready Validation

| DoR Item | Status | Evidence |
|----------|--------|----------|
| Problem statement clear | PASS | Concrete 5D-Wave workflow example provided; username hardcoding pain point identified |
| User/persona identified | PASS | 5 personas with real context (added Multi-Account Developer, OSS Contributor) |
| 3+ domain examples | PASS | Multiple scenarios with real data across 5 features |
| UAT scenarios (3-7) | PASS | 17 Gherkin scenarios covering all features (7 original + 10 new) |
| Acceptance criteria from UAT | PASS | All AC derived from scenarios |
| Right-sized (1-3 days) | PASS | 2 files, ~100 LOC changes (expanded from original scope) |
| Technical notes present | PASS | Edge cases, error handling, prerequisite validation documented |
| Dependencies tracked | PASS | External dependencies: git, gh CLI (documented with validation) |

**DoR Status:** PASSED

---

## 10. Traceability

| Requirement ID | User Story | Business Objective |
|----------------|------------|-------------------|
| FR-001 | US-001 | Enable 5D-Wave automation |
| FR-002 | US-002 | Support monorepo integration |
| FR-003 | US-003 | Support headless/CI environments |
| FR-004 | US-004 | Support multi-account GitHub users with prerequisite validation |
| FR-005 | US-005 | Control repository visibility (public/private) |

---

## Document Approval

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Riley | APPROVED | 2026-01-08 |
| Reviewer | Product-Owner-Reviewer | APPROVED | 2026-01-08 |
| Architect Handoff | Pending | - | - |

### Version 1.1 Amendment (2026-01-09)

| Role | Name | Status | Date |
|------|------|--------|------|
| Product Owner | Riley | APPROVED | 2026-01-09 |
| Stakeholder | Mike | APPROVED | 2026-01-09 |

**Amendment Summary:**
- Added FR-004: Configurable GitHub Username with prerequisite validation
- Added FR-005: Repository Visibility Control (public/private)
- Added 2 new personas: Multi-Account Developer, OSS Contributor
- Added 10 new Gherkin scenarios for Features 4 and 5
- Added edge cases for prerequisite validation and visibility control
- Updated traceability matrix with US-004 and US-005
