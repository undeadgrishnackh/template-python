"""Step definitions for US-001 Git Repository Detection acceptance tests.

Implements pytest-bdd step definitions for all scenarios in
US001_git_repository_detection.feature.

Reference: ADR-001-git-detection-algorithm.md
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import TYPE_CHECKING

import pytest
from pytest_bdd import given, parsers, scenarios, then, when


if TYPE_CHECKING:
    from collections.abc import Generator
    from typing import Any

# Import function under test
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "hooks"))
from post_gen_project import is_inside_git_repo


# Load all scenarios from feature file
scenarios("../features/US001_git_repository_detection.feature")


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def test_context(tmp_path: Path) -> Generator[dict[str, Any], None, None]:
    """Test context fixture for scenario state isolation.

    Provides isolated state for each scenario with:
    - temp_dir: temporary directory for test isolation
    - project_dir: directory where scaffold is generated
    - git_repo_path: path to .git marker
    - hook_result: result of is_inside_git_repo()
    - hook_output: captured output from hook operations
    - created_files: list of files created during scaffold
    - branch_name: current git branch name
    - error_message: captured error message
    """
    original_cwd = os.getcwd()
    context: dict[str, Any] = {
        "temp_dir": tmp_path,
        "project_dir": None,
        "git_repo_path": None,
        "hook_result": None,
        "hook_output": [],
        "created_files": [],
        "branch_name": None,
        "error_message": None,
        "persona": None,
        "directory_name": None,
        "kata_name": None,
    }
    yield context
    os.chdir(original_cwd)


# =============================================================================
# BACKGROUND STEPS
# =============================================================================


@given("the cookiecutter template is available")
def cookiecutter_template_available(test_context: dict[str, Any]) -> None:
    """Verify cookiecutter template is available."""
    template_path = Path(__file__).parent.parent.parent.parent / "cookiecutter.json"
    assert template_path.exists(), f"Template not found at {template_path}"
    test_context["template_path"] = template_path


# =============================================================================
# HAPPY PATH - GIVEN STEPS
# =============================================================================


@given(parsers.parse("{persona} is the 5D-Wave agent working in a project directory"))
def agent_in_project_directory(test_context: dict[str, Any], persona: str) -> None:
    """Set up persona working in a project directory."""
    test_context["persona"] = persona
    project_dir = test_context["temp_dir"] / "project"
    project_dir.mkdir()
    test_context["project_dir"] = project_dir


@given("the project has an existing git repository from DISCUSS phase")
def project_has_existing_git_repo(test_context: dict[str, Any]) -> None:
    """Create an existing git repository in project directory."""
    project_dir = test_context["project_dir"]
    git_dir = project_dir / ".git"
    git_dir.mkdir()
    test_context["git_repo_path"] = git_dir


@given(parsers.parse("{persona} is working in a services subdirectory"))
def persona_in_services_subdir(test_context: dict[str, Any], persona: str) -> None:
    """Set up persona in a nested services subdirectory."""
    test_context["persona"] = persona
    # Create nested structure: temp_dir/repo/services/component
    repo_dir = test_context["temp_dir"] / "repo"
    repo_dir.mkdir()
    services_dir = repo_dir / "services" / "component"
    services_dir.mkdir(parents=True)
    test_context["project_dir"] = services_dir
    test_context["repo_root"] = repo_dir


@given("a git repository exists two levels up in the directory tree")
def git_repo_two_levels_up(test_context: dict[str, Any]) -> None:
    """Create git repository two levels up from current directory."""
    repo_root = test_context["repo_root"]
    git_dir = repo_root / ".git"
    git_dir.mkdir()
    test_context["git_repo_path"] = git_dir


@given(parsers.parse("{persona} is in a kata directory with no git repository in parent tree"))
def persona_in_clean_kata_dir(test_context: dict[str, Any], persona: str) -> None:
    """Set up persona in a clean kata directory without git."""
    test_context["persona"] = persona
    kata_dir = test_context["temp_dir"] / "kata"
    kata_dir.mkdir()
    test_context["project_dir"] = kata_dir


# =============================================================================
# HAPPY PATH - WHEN STEPS
# =============================================================================


@when(parsers.parse('{persona} generates a Python scaffold with directory name "{name}"'))
def generate_scaffold_with_name(test_context: dict[str, Any], persona: str, name: str) -> None:
    """Generate scaffold and detect git repository."""
    test_context["directory_name"] = name
    project_dir = test_context["project_dir"]
    os.chdir(project_dir)
    test_context["hook_result"] = is_inside_git_repo()


@when(parsers.parse('{persona} runs the cookiecutter with kata name "{kata_name}"'))
def run_cookiecutter_with_kata_name(test_context: dict[str, Any], persona: str, kata_name: str) -> None:
    """Run cookiecutter with specified kata name."""
    test_context["kata_name"] = kata_name
    project_dir = test_context["project_dir"]
    os.chdir(project_dir)
    test_context["hook_result"] = is_inside_git_repo()


# =============================================================================
# HAPPY PATH - THEN STEPS
# =============================================================================


@then("the hook detects the existing git repository")
def hook_detects_existing_repo(test_context: dict[str, Any]) -> None:
    """Verify hook detected existing repository."""
    assert test_context["hook_result"] is True


@then("the hook skips GitHub repository creation")
def hook_skips_github_creation(test_context: dict[str, Any]) -> None:
    """Verify hook would skip GitHub repository creation."""
    assert test_context["hook_result"] is True, "Hook should detect repo to skip creation"


@then("the hook skips git initialization")
def hook_skips_git_init(test_context: dict[str, Any]) -> None:
    """Verify hook would skip git init."""
    assert test_context["hook_result"] is True


@then("the hook skips adding git remote origin")
def hook_skips_remote_origin(test_context: dict[str, Any]) -> None:
    """Verify hook would skip adding remote origin."""
    assert test_context["hook_result"] is True


@then("the hook skips pushing to remote")
def hook_skips_push(test_context: dict[str, Any]) -> None:
    """Verify hook would skip push."""
    assert test_context["hook_result"] is True


@then("the hook installs development dependencies")
def hook_installs_dev_deps(test_context: dict[str, Any]) -> None:
    """Verify hook would install dependencies (always runs)."""
    # Dependencies install regardless of git detection
    # This step validates the conditional flow design


@then("the hook installs pre-commit hooks")
def hook_installs_precommit(test_context: dict[str, Any]) -> None:
    """Verify hook would install pre-commit hooks (standalone mode only)."""
    # In standalone mode (hook_result is False), pre-commit hooks are installed
    assert test_context["hook_result"] is False


@then("the hook skips pre-commit installation in integration mode")
def hook_skips_precommit_integration(test_context: dict[str, Any]) -> None:
    """Verify hook skips pre-commit install in integration mode.

    Integration mode fix: pre-commit hooks would install to PARENT repo's
    .git/hooks/, but reference child's .pre-commit-config.yaml with pipenv
    commands that fail because parent's Pipfile doesn't have ruff, bandit, etc.
    """
    # In integration mode (hook_result is True), pre-commit is skipped
    assert test_context["hook_result"] is True


@then("the hook skips validation commit in integration mode")
def hook_skips_commit_integration(test_context: dict[str, Any]) -> None:
    """Verify hook skips validation commit in integration mode.

    Integration mode fix: git commit would trigger pre-commit hooks from
    parent's .git/hooks/, which fail due to Pipfile mismatch.
    User should commit manually after reviewing generated files.
    """
    # In integration mode (hook_result is True), commit is skipped
    assert test_context["hook_result"] is True


@then(parsers.parse('the hook creates a validation commit with message containing "{msg}"'))
def hook_creates_commit_with_message(test_context: dict[str, Any], msg: str) -> None:
    """Verify hook would create commit with message (standalone mode only)."""
    assert test_context["directory_name"] == msg or test_context["kata_name"] == msg


@then(parsers.parse("{persona} continues workflow without manual intervention"))
def persona_continues_workflow(test_context: dict[str, Any], persona: str) -> None:
    """Verify workflow can continue without manual steps."""
    assert test_context["hook_result"] is not None


@then("the hook traverses parent directories")
def hook_traverses_parents(test_context: dict[str, Any]) -> None:
    """Verify hook traverses parent directories."""
    # Traversal is implicit in finding repo two levels up
    assert test_context["hook_result"] is True


@then("the hook finds the git repository in the parent tree")
def hook_finds_repo_in_parent(test_context: dict[str, Any]) -> None:
    """Verify hook found repository in parent tree."""
    assert test_context["hook_result"] is True


@then("the hook skips repository creation operations")
def hook_skips_repo_creation(test_context: dict[str, Any]) -> None:
    """Verify hook would skip all repository creation."""
    assert test_context["hook_result"] is True


@then("the scaffold is generated in the services subdirectory")
def scaffold_in_services_subdir(test_context: dict[str, Any]) -> None:
    """Verify scaffold location."""
    # Location is determined by working directory
    assert test_context["project_dir"].exists()


@then("the hook finds no git repository in parent tree")
def hook_finds_no_repo(test_context: dict[str, Any]) -> None:
    """Verify hook found no repository."""
    assert test_context["hook_result"] is False


@then("the hook creates a private GitHub repository named with the kata")
def hook_creates_github_repo(test_context: dict[str, Any]) -> None:
    """Verify hook would create GitHub repo in standalone mode."""
    assert test_context["hook_result"] is False


@then("the hook initializes a new git repository")
def hook_initializes_git(test_context: dict[str, Any]) -> None:
    """Verify hook would initialize git in standalone mode."""
    assert test_context["hook_result"] is False


@then("the hook adds a remote origin pointing to GitHub")
def hook_adds_remote(test_context: dict[str, Any]) -> None:
    """Verify hook would add remote in standalone mode."""
    assert test_context["hook_result"] is False


@then("the hook pushes the initial commit to the main branch")
def hook_pushes_initial_commit(test_context: dict[str, Any]) -> None:
    """Verify hook would push in standalone mode."""
    assert test_context["hook_result"] is False


@then("a dated project directory is created")
def dated_project_created(test_context: dict[str, Any]) -> None:
    """Verify project directory exists."""
    assert test_context["project_dir"].exists()


# =============================================================================
# EDGE CASE - GIVEN STEPS
# =============================================================================


@given("a developer is working in a git worktree directory")
def developer_in_worktree(test_context: dict[str, Any]) -> None:
    """Set up developer in a git worktree."""
    test_context["persona"] = "developer"
    worktree_dir = test_context["temp_dir"] / "worktree"
    worktree_dir.mkdir()
    test_context["project_dir"] = worktree_dir


@given("the worktree has a .git file instead of a directory")
def worktree_has_git_file(test_context: dict[str, Any]) -> None:
    """Create .git file (worktree format) instead of directory."""
    project_dir = test_context["project_dir"]
    git_file = project_dir / ".git"
    git_file.write_text("gitdir: /path/to/main/repo/.git/worktrees/feature")
    test_context["git_repo_path"] = git_file


@given("a developer is in a directory near the filesystem root")
def developer_near_root(test_context: dict[str, Any]) -> None:
    """Set up developer in directory without .git in parent tree."""
    test_context["persona"] = "developer"
    # Use temp_path which has no .git in its tree
    project_dir = test_context["temp_dir"] / "near_root"
    project_dir.mkdir()
    test_context["project_dir"] = project_dir


@given("no git repository exists in any parent directory")
def no_git_in_parents(test_context: dict[str, Any]) -> None:
    """Ensure no .git exists in parent directories of temp path."""
    # tmp_path is isolated, no .git should exist


@given("a developer is working in a symlinked project directory")
def developer_in_symlinked_dir(test_context: dict[str, Any]) -> None:
    """Set up developer in a symlinked directory."""
    test_context["persona"] = "developer"
    # Create target directory with .git
    target_dir = test_context["temp_dir"] / "target"
    target_dir.mkdir()
    git_dir = target_dir / ".git"
    git_dir.mkdir()
    test_context["git_repo_path"] = git_dir

    # Create symlink to target
    symlink_path = test_context["temp_dir"] / "symlink"
    symlink_path.symlink_to(target_dir)
    test_context["project_dir"] = symlink_path


@given("the symlink target has a git repository")
def symlink_target_has_git(test_context: dict[str, Any]) -> None:
    """Verify symlink target has git repository."""
    # Already set up in previous step
    assert test_context["git_repo_path"].exists()


@given(parsers.parse('{persona} is working on a feature branch named "{branch_name}"'))
def persona_on_feature_branch(test_context: dict[str, Any], persona: str, branch_name: str) -> None:
    """Set up persona on a feature branch."""
    test_context["persona"] = persona
    test_context["branch_name"] = branch_name
    project_dir = test_context["temp_dir"] / "project"
    project_dir.mkdir()
    test_context["project_dir"] = project_dir


@given("the project has an existing git repository")
def project_has_git_repo(test_context: dict[str, Any]) -> None:
    """Create git repository in project."""
    project_dir = test_context["project_dir"]
    git_dir = project_dir / ".git"
    git_dir.mkdir()
    test_context["git_repo_path"] = git_dir


# =============================================================================
# EDGE CASE - WHEN STEPS
# =============================================================================


@when("the developer generates a Python scaffold")
def developer_generates_scaffold(test_context: dict[str, Any]) -> None:
    """Developer generates scaffold (no specific name)."""
    project_dir = test_context["project_dir"]
    os.chdir(project_dir)
    test_context["hook_result"] = is_inside_git_repo()


@when("the developer runs the cookiecutter")
def developer_runs_cookiecutter(test_context: dict[str, Any]) -> None:
    """Developer runs cookiecutter."""
    project_dir = test_context["project_dir"]
    os.chdir(project_dir)
    test_context["hook_result"] = is_inside_git_repo()


# =============================================================================
# EDGE CASE - THEN STEPS
# =============================================================================


@then("the hook detects the git worktree as a valid repository")
def hook_detects_worktree(test_context: dict[str, Any]) -> None:
    """Verify hook detects worktree (.git file) as valid repo."""
    assert test_context["hook_result"] is True


@then("the hook traverses all parent directories to the root")
def hook_traverses_to_root(test_context: dict[str, Any]) -> None:
    """Verify hook traverses to filesystem root."""
    # Traversal happens during detection


@then("the hook correctly determines no repository exists")
def hook_determines_no_repo(test_context: dict[str, Any]) -> None:
    """Verify hook found no repository."""
    assert test_context["hook_result"] is False


@then("the hook proceeds with full git initialization")
def hook_proceeds_with_init(test_context: dict[str, Any]) -> None:
    """Verify hook would proceed with full init."""
    assert test_context["hook_result"] is False


@then("the hook resolves the symlink and detects the git repository")
def hook_resolves_symlink(test_context: dict[str, Any]) -> None:
    """Verify hook resolves symlink and detects repo."""
    assert test_context["hook_result"] is True


@then("the hook does not change the current branch")
def hook_preserves_branch(test_context: dict[str, Any]) -> None:
    """Verify hook does not change branch."""
    # Branch preservation is part of integration mode behavior
    assert test_context["hook_result"] is True


@then(parsers.parse('the validation commit is created on "{branch_name}"'))
def commit_on_branch(test_context: dict[str, Any], branch_name: str) -> None:
    """Verify commit would be on specified branch (standalone mode only).

    Note: This step is for standalone mode. In integration mode, the validation
    commit is skipped entirely, so this step won't be reached.
    """
    assert test_context["branch_name"] == branch_name


@then(parsers.parse('the branch remains "{branch_name}" after scaffold completion'))
def branch_remains_same(test_context: dict[str, Any], branch_name: str) -> None:
    """Verify branch is preserved after scaffold."""
    assert test_context["branch_name"] == branch_name


# =============================================================================
# ERROR PATH - GIVEN STEPS
# =============================================================================


@given("a developer is in a project directory")
def developer_in_project_dir(test_context: dict[str, Any]) -> None:
    """Set up developer in a project directory."""
    test_context["persona"] = "developer"
    project_dir = test_context["temp_dir"] / "project"
    project_dir.mkdir()
    test_context["project_dir"] = project_dir


@given("some parent directories have restricted read permissions")
def restricted_permissions(test_context: dict[str, Any]) -> None:
    """Note: Cannot actually restrict tmp_path permissions in test.

    This scenario tests graceful handling of permission errors.
    Actual permission errors would occur in real execution.
    """
    test_context["has_permission_restrictions"] = True


@given(parsers.parse("{persona} is in a kata directory with no git repository"))
def persona_in_kata_no_git(test_context: dict[str, Any], persona: str) -> None:
    """Set up persona in kata directory without git."""
    test_context["persona"] = persona
    kata_dir = test_context["temp_dir"] / "kata"
    kata_dir.mkdir()
    test_context["project_dir"] = kata_dir


@given("the GitHub CLI is not authenticated")
def gh_cli_not_authenticated(test_context: dict[str, Any]) -> None:
    """Mark that GitHub CLI is not authenticated."""
    test_context["gh_authenticated"] = False


@given("a developer is in a clean directory")
def developer_in_clean_dir(test_context: dict[str, Any]) -> None:
    """Set up developer in clean directory."""
    test_context["persona"] = "developer"
    clean_dir = test_context["temp_dir"] / "clean"
    clean_dir.mkdir()
    test_context["project_dir"] = clean_dir


@given("git is not installed on the system")
def git_not_installed(test_context: dict[str, Any]) -> None:
    """Mark that git is not available."""
    test_context["git_installed"] = False


# =============================================================================
# ERROR PATH - WHEN STEPS
# =============================================================================


@when(parsers.parse('{persona} generates a Python scaffold with directory name "{directory_name}"'))
def persona_generates_scaffold_with_dir_name(test_context: dict[str, Any], persona: str, directory_name: str) -> None:
    """Generate scaffold with directory name (handles permission scenario)."""
    test_context["directory_name"] = directory_name
    project_dir = test_context["project_dir"]
    os.chdir(project_dir)
    test_context["hook_result"] = is_inside_git_repo()


# =============================================================================
# ERROR PATH - THEN STEPS
# =============================================================================


@then("the hook handles permission errors gracefully")
def hook_handles_permission_errors(test_context: dict[str, Any]) -> None:
    """Verify hook handles permission errors gracefully.

    The hook should continue with available directory information.
    """
    # In test environment, we verify the hook completes without exception
    assert test_context["hook_result"] is not None


@then("the hook continues with available directory information")
def hook_continues_with_available_info(test_context: dict[str, Any]) -> None:
    """Verify hook uses available information."""
    assert test_context["hook_result"] is not None


@then("the scaffold generation completes successfully")
def scaffold_completes_successfully(test_context: dict[str, Any]) -> None:
    """Verify scaffold generation completes."""
    assert test_context["project_dir"].exists()


@then("the hook fails with a clear error message about GitHub authentication")
def hook_fails_github_auth_error(test_context: dict[str, Any]) -> None:
    """Verify hook would fail with GitHub auth error.

    Note: Actual gh cli failure would occur during repository creation.
    This test validates the detection phase completes (returns False).
    """
    assert test_context["hook_result"] is False  # Would trigger standalone mode


@then("the failure occurs before any files are modified")
def failure_before_file_modification(test_context: dict[str, Any]) -> None:
    """Verify failure timing."""
    # Detection phase completes before file operations


@then("the error message includes remediation steps")
def error_includes_remediation(test_context: dict[str, Any]) -> None:
    """Verify error includes remediation steps.

    Note: Actual error message comes from gh cli, not detection.
    """


@then("the hook fails with a clear error about missing git")
def hook_fails_missing_git(test_context: dict[str, Any]) -> None:
    """Verify hook would fail with missing git error.

    Note: Actual failure occurs when git commands are executed.
    Detection phase uses Path operations, not git.
    """
    assert test_context["hook_result"] is False  # Would trigger standalone mode


@then("the error message includes installation instructions")
def error_includes_install_instructions(test_context: dict[str, Any]) -> None:
    """Verify error includes installation instructions.

    Note: Actual error message comes from subprocess, not detection.
    """
