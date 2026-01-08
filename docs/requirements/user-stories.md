# User Stories: Python Cookiecutter Template Enhancement

**Document ID:** US-COOKIECUTTER-GIT-2026-001
**Version:** 1.0
**Status:** DoR VALIDATED
**Date:** 2026-01-08
**Author:** Riley (Product Owner)

---

## US-001: Smart Git Repository Detection

### Problem (The Pain)

**Alex** is a 5D-Wave AI agent executing the DESIGN wave inside the `/my-trading-bot/` project directory. The project was initialized in the DISCUSS wave with `git init` and already has a `.git` directory.

Alex finds it **blocking** to scaffold Python code because the cookiecutter `post_gen_project.py` hook attempts to run `gh repo create source --private`, which fails with "Repository already exists" or "Must have admin rights" errors.

### Who (The User)

- 5D-Wave AI agent in automated DESIGN phase workflow
- Operating inside pre-initialized git repository
- Requires zero human intervention for successful execution

### Solution (What We Build)

Add a `is_inside_git_repo()` function that traverses parent directories looking for `.git`. When found, skip repository creation operations (gh repo create, git init, git remote add, git push) while still executing environment setup operations (pipenv install, pre-commit install, validation commit).

### Domain Examples

#### Example 1: Agent Inside Existing Repository (Happy Path)
Alex the 5D-Wave agent is working in `/my-trading-bot/` where `/my-trading-bot/.git` exists from DISCUSS phase.
Alex runs `cookiecutter gh:undeadgrishnackh/_template_Python_ directory_name=source`.
The hook detects `.git` in parent tree, skips repo creation, generates `/my-trading-bot/source/` with quality gates installed, and commits "feat: add Python source scaffolding".

#### Example 2: Nested Monorepo Structure (Edge Case)
Platform engineer Maria is working in `/enterprise-platform/services/` where `/enterprise-platform/.git` exists.
Maria runs `cookiecutter directory_name=trading-engine`.
The hook traverses 2 levels up, finds `.git`, skips repo creation, generates `/enterprise-platform/services/trading-engine/` successfully.

#### Example 3: Clean Kata Directory (Existing Behavior)
Developer Sam is in `/Users/sam/katas/` with no `.git` anywhere in parent tree.
Sam runs `cookiecutter gh:undeadgrishnackh/_template_Python_` and enters "fizzbuzz" when prompted.
The hook finds no `.git`, runs full git initialization (gh repo create, git init, git push), creates `/Users/sam/katas/20260108_fizzbuzz/`.

### UAT Scenarios (BDD)

```gherkin
Scenario: Agent detects existing repository and skips repo creation
  Given Alex is the 5D-Wave agent working in /my-trading-bot/
  And /my-trading-bot/.git exists from DISCUSS phase initialization
  When Alex runs: cookiecutter gh:undeadgrishnackh/_template_Python_ directory_name=source
  Then the hook detects /my-trading-bot/.git in parent tree
  And the hook skips: gh repo create
  And the hook skips: git init
  And the hook skips: git remote add origin
  And the hook skips: git push -u origin main
  But the hook runs: pipenv install --dev
  And the hook runs: pre-commit install
  And the hook runs: git add --all
  And the hook runs: git commit -m "feat: add Python source scaffolding"
  And Alex continues workflow without manual intervention

Scenario: Nested monorepo detection traverses multiple levels
  Given Maria is working in /enterprise-platform/services/
  And /enterprise-platform/.git exists (2 levels up)
  When Maria runs: cookiecutter directory_name=trading-engine
  Then the hook traverses parent directories
  And finds .git at /enterprise-platform/
  And skips repository creation operations
  And generates /enterprise-platform/services/trading-engine/ successfully

Scenario: Clean directory triggers full git initialization
  Given Sam is in /Users/sam/katas/ with no .git in parent tree
  When Sam runs: cookiecutter gh:undeadgrishnackh/_template_Python_
  And enters "fizzbuzz" when prompted for kata_name
  Then the hook finds no .git in parent tree
  And runs: gh repo create fizzbuzz --private
  And runs: git init
  And runs: git remote add origin
  And runs: git push -u origin main
  And creates /Users/sam/katas/20260108_fizzbuzz/
```

### Acceptance Criteria

- [ ] `is_inside_git_repo()` function traverses parent directories correctly
- [ ] Detection works for `.git` directory at any parent level
- [ ] Detection works for `.git` file (bare repos, worktrees)
- [ ] Repository creation skipped when inside existing repo
- [ ] Environment setup (pipenv, pre-commit) always executes
- [ ] Validation commit always executes when inside existing repo
- [ ] Clean directory triggers full git initialization (backwards compatible)

### Technical Notes

- Use `pathlib.Path` for cross-platform path traversal
- Check for both `.git` directory and `.git` file (worktrees use files)
- Detection algorithm must handle root directory edge case (stop at filesystem root)

---

## US-002: Configurable Source Directory Name

### Problem (The Pain)

**Maria** is a platform engineer integrating Python services into the `/enterprise-platform/` monorepo. She needs a Python service at `/enterprise-platform/services/trading-engine/`.

Maria finds it **frustrating** that the cookiecutter generates `20260108_trading-engine/` with a dated prefix that clutters the monorepo structure and doesn't match her project conventions.

### Who (The User)

- Platform engineer maintaining monorepo or multi-language project
- Requires consistent directory naming across services
- Values clean project structure over dated prefixes

### Solution (What We Build)

Add a `directory_name` parameter that allows explicit override of the generated directory name. When provided, skip the `kata_name` prompt and use the provided value directly.

### Domain Examples

#### Example 1: Explicit Source Directory (Happy Path)
Maria runs `cookiecutter directory_name=trading-engine` in `/enterprise-platform/services/`.
The hook creates `/enterprise-platform/services/trading-engine/` without prompting for kata_name.
The directory structure is clean: `trading-engine/` not `20260108_trading-engine/`.

#### Example 2: 5D-Wave Standard Source Directory
Alex the agent runs `cookiecutter directory_name=source` in `/my-trading-bot/`.
The hook creates `/my-trading-bot/source/` matching 5D-Wave conventions.
The agent workflow continues with consistent directory structure.

#### Example 3: Default Kata Behavior Preserved
Sam runs `cookiecutter` without `directory_name` parameter.
Sam is prompted for `kata_name` and enters "fizzbuzz".
The hook creates `20260108_fizzbuzz/` preserving existing behavior.

### UAT Scenarios (BDD)

```gherkin
Scenario: Explicit directory name skips kata_name prompt
  Given Maria is in /enterprise-platform/services/
  When Maria runs: cookiecutter directory_name=trading-engine
  Then Maria is NOT prompted for kata_name
  And the hook creates /enterprise-platform/services/trading-engine/
  And the directory structure matches project conventions

Scenario: 5D-Wave source directory convention
  Given Alex is the 5D-Wave agent in /my-trading-bot/
  When Alex runs: cookiecutter directory_name=source
  Then the hook creates /my-trading-bot/source/
  And the structure matches 5D-Wave expectations:
    """
    my-trading-bot/
    +-- .git/                  (existing)
    +-- docs/                  (from 5D-Wave phases)
    +-- source/                (newly generated)
        +-- Pipfile
        +-- .pre-commit-config.yaml
        +-- modules/
        +-- tests/
    """

Scenario: Default behavior preserved for standalone katas
  Given Sam is starting a fresh kata
  When Sam runs: cookiecutter (no directory_name)
  Then Sam is prompted for kata_name
  And Sam enters "fizzbuzz"
  And the hook creates 20260108_fizzbuzz/
  And full git initialization runs
```

### Acceptance Criteria

- [ ] `directory_name` parameter accepted by cookiecutter.json
- [ ] When `directory_name` provided, skip `kata_name` prompt
- [ ] Generated directory uses exact `directory_name` value
- [ ] Default behavior (dated prefix) preserved when parameter not provided
- [ ] Parameter works in combination with git detection (US-001)

### Technical Notes

- Default value in cookiecutter.json: `{{ cookiecutter.today }}_{{ cookiecutter.kata_name }}`
- Jinja2 conditional logic needed to handle parameter presence
- Parameter triggers git detection skip even if `.git` detection fails (explicit signal)

---

## US-003: IDE Opening Control

### Problem (The Pain)

**Alex** is a 5D-Wave AI agent executing cookiecutter in headless DESIGN wave automation. The current hook always runs `code .` which attempts to open VS Code.

Alex finds it **blocking** that the IDE launch command hangs the automated pipeline (no GUI available) or produces error output that confuses workflow validation.

### Who (The User)

- 5D-Wave AI agent in headless automation
- CI/CD pipeline in Docker container
- Developer with IDE preference (PyCharm over VS Code)

### Solution (What We Build)

Add an `open_ide` parameter with options `none` (default), `vscode`, and `pycharm`. Default to `none` for safe automation behavior.

### Domain Examples

#### Example 1: Agentic Workflow - No IDE (Happy Path)
Alex runs `cookiecutter directory_name=source` without specifying `open_ide`.
The hook completes, no IDE opens, terminal returns control to calling process.
Alex continues automated workflow without interruption.

#### Example 2: Developer Wants VS Code
Sam runs `cookiecutter open_ide=vscode` for interactive kata development.
After generation, VS Code opens with the new project.
Sam starts coding immediately in preferred editor.

#### Example 3: PyCharm User
Developer Raj runs `cookiecutter open_ide=pycharm`.
After generation, PyCharm opens with the new project.
The hook uses platform-appropriate command (pycharm CLI or macOS open -a).

#### Example 4: IDE Command Fails (Error Handling)
Developer Kim runs `cookiecutter open_ide=vscode` but `code` CLI not installed.
The hook prints warning: "VS Code command not found, skipping IDE open".
Generation completes successfully (non-fatal error).

### UAT Scenarios (BDD)

```gherkin
Scenario: Default behavior is no IDE (agentic safe)
  Given Alex is the 5D-Wave agent
  When Alex runs: cookiecutter directory_name=source
  And open_ide parameter is not specified
  Then no IDE opens
  And the terminal returns control to calling process
  And Alex continues automated workflow

Scenario: Developer requests VS Code
  Given Sam is developing interactively
  When Sam runs: cookiecutter open_ide=vscode
  Then VS Code opens with the generated directory
  And command executed: code <generated_directory>

Scenario: Developer requests PyCharm
  Given Raj uses PyCharm IDE
  When Raj runs: cookiecutter open_ide=pycharm
  Then PyCharm opens with the generated directory
  And command executed: pycharm <generated_directory>
  Or on macOS: open -a "PyCharm" <generated_directory>

Scenario: IDE command not found is non-fatal
  Given Kim runs: cookiecutter open_ide=vscode
  And code CLI is not installed
  Then the hook prints warning: "VS Code command not found"
  But generation completes successfully
  And exit code is 0 (success)
```

### Acceptance Criteria

- [ ] `open_ide` parameter added to cookiecutter.json with default `none`
- [ ] `open_ide=none` results in no IDE launch
- [ ] `open_ide=vscode` executes `code <directory>`
- [ ] `open_ide=pycharm` executes `pycharm <directory>` with macOS fallback
- [ ] IDE failures are non-fatal (warning only, generation succeeds)
- [ ] Invalid `open_ide` values produce helpful error message

### Technical Notes

- PyCharm command varies by platform: `pycharm` CLI on Linux, `open -a "PyCharm"` on macOS
- Use `shutil.which()` to check command availability before execution
- Wrap IDE launch in try/except to ensure non-fatal behavior
- Breaking change: existing users expecting VS Code must now specify `open_ide=vscode`

---

## Story Sizing Summary

| Story | Effort | Scenarios | Demonstrable Value |
|-------|--------|-----------|-------------------|
| US-001 | 1 day | 3 | Git detection enables automation |
| US-002 | 0.5 day | 3 | Directory naming enables integration |
| US-003 | 0.5 day | 4 | IDE control enables all environments |

**Total:** ~2 days implementation
**Risk:** Low - isolated changes to single hook file

---

## Dependencies

```
US-001 (Git Detection) <-- signals --> US-002 (Directory Name)
         |
         | When directory_name=source provided,
         | it's an explicit signal to skip repo creation
         | (even if .git detection somehow fails)
         |
         +-- independent of --> US-003 (IDE Control)
```

All stories can be developed in parallel after cookiecutter.json parameters are added.
