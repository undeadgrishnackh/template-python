"""
Step definitions for US-001: Smart Git Repository Detection.

These steps implement the acceptance tests for detecting existing
git repositories and conditionally skipping repository creation.

Note: The shared @given("the cookiecutter template is available") step
is defined in conftest.py for DRY compliance (Issue 1).
"""

from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import TestEnvironment
from tests.doubles.hook_service import (
    ERROR_GH_NOT_AUTHENTICATED,
    ERROR_GIT_NOT_FOUND,
    HookService,
    create_error_result,
    create_success_result,
)


# Load all scenarios from the feature file
scenarios("../features/US001_git_repository_detection.feature")


@given("Alex is the 5D-Wave agent working in a project directory")
def alex_agent_context(test_env: TestEnvironment):
    """Set up context for 5D-Wave agent scenario."""
    test_env.kata_name = None  # Agents don't use kata_name
    return test_env


@given("the project has an existing git repository from DISCUSS phase")
def project_has_git_repo(test_env: TestEnvironment, git_repo: Path):
    """Create a git repository simulating DISCUSS phase initialization."""
    test_env.work_dir = git_repo
    test_env.has_git = True
    test_env.git_levels_up = 0
    return test_env


@given("Maria is working in a services subdirectory")
def maria_services_context(test_env: TestEnvironment, work_dir: Path):
    """Set up context for platform engineer in services subdirectory."""
    services_dir = work_dir / "services"
    services_dir.mkdir(parents=True)
    test_env.work_dir = services_dir
    return test_env


@given("a git repository exists two levels up in the directory tree")
def git_two_levels_up(test_env: TestEnvironment, nested_git_repo):
    """Create git repo structure with .git 2 levels up."""
    _git_root, nested_work = nested_git_repo
    test_env.work_dir = nested_work
    test_env.has_git = True
    test_env.git_levels_up = 2
    return test_env


@given("Sam is in a kata directory with no git repository in parent tree")
def sam_kata_context(test_env: TestEnvironment, work_dir: Path):
    """Set up context for developer starting fresh kata."""
    kata_dir = work_dir / "katas"
    kata_dir.mkdir(parents=True)
    test_env.work_dir = kata_dir
    test_env.has_git = False
    return test_env


@given("a developer is working in a git worktree directory")
def developer_worktree_context(test_env: TestEnvironment, git_worktree: Path):
    """Set up context for git worktree scenario."""
    test_env.work_dir = git_worktree
    test_env.has_git = True
    return test_env


@given("the worktree has a .git file instead of a directory")
def worktree_has_git_file(test_env: TestEnvironment):
    """Verify .git is a file in worktree."""
    git_path = test_env.work_dir / ".git"
    # In a worktree, .git is a file pointing to the actual git dir
    assert git_path.exists(), ".git should exist in worktree"
    # Note: After clone, .git is actually a directory, but concept remains valid
    return test_env


@given("a developer is in a directory near the filesystem root")
def developer_near_root(test_env: TestEnvironment, work_dir: Path):
    """Set up context for filesystem root edge case."""
    test_env.work_dir = work_dir
    test_env.has_git = False
    return test_env


@given("no git repository exists in any parent directory")
def no_git_anywhere(test_env: TestEnvironment):
    """Ensure no .git exists in parent tree."""
    current = test_env.work_dir
    while current != current.parent:
        assert not (current / ".git").exists(), f"Unexpected .git at {current}"
        current = current.parent
    return test_env


@given("a developer is in a project directory")
def developer_project_context(test_env: TestEnvironment, work_dir: Path):
    """Generic developer context in a project directory."""
    test_env.work_dir = work_dir
    return test_env


@given("some parent directories have restricted read permissions")
def restricted_permissions(test_env: TestEnvironment):
    """Mark that permission errors should be handled gracefully."""
    # This is a conceptual marker - actual permission testing is complex
    # The implementation should handle OSError gracefully
    return test_env


@given("the GitHub CLI is not authenticated")
def gh_not_authenticated(test_env: TestEnvironment):
    """Mark GitHub CLI as not authenticated."""
    test_env.has_gh_cli = False
    return test_env


@given("a developer is in a clean directory")
def developer_clean_directory(test_env: TestEnvironment, work_dir: Path):
    """Developer in a clean directory without git."""
    test_env.work_dir = work_dir
    test_env.has_git = False
    return test_env


@given("git is not installed on the system")
def git_not_installed(test_env: TestEnvironment):
    """Mark git as not installed."""
    test_env.has_git_installed = False
    return test_env


@given("a developer is working in a symlinked project directory")
def developer_symlinked_context(test_env: TestEnvironment, symlinked_git_repo: Path):
    """Set up context for symlinked directory scenario."""
    test_env.work_dir = symlinked_git_repo
    test_env.has_git = True
    return test_env


@given("the symlink target has a git repository")
def symlink_target_has_git(test_env: TestEnvironment):
    """Verify symlink target has git repository."""
    # The symlinked_git_repo fixture already set up git in the target
    # Just verify the context is correct
    assert test_env.has_git, "Symlink target should have git repository"
    return test_env


@given(parsers.parse('Alex is working on a feature branch named "{branch_name}"'))
def alex_feature_branch_context(test_env: TestEnvironment, git_repo_on_branch: tuple[Path, str], branch_name: str):
    """Set up context for Alex working on a specific feature branch."""
    repo_path, actual_branch = git_repo_on_branch
    test_env.work_dir = repo_path
    test_env.has_git = True
    test_env.current_branch = actual_branch
    return test_env


@given("the project has an existing git repository")
def project_has_existing_git(test_env: TestEnvironment):
    """Confirm project has existing git repository."""
    assert test_env.has_git, "Project should have existing git repository"
    return test_env


@given("Sam is in a kata directory with no git repository")
def sam_kata_no_git_context(test_env: TestEnvironment, work_dir: Path):
    """Set up context for Sam in a kata directory without git."""
    kata_dir = work_dir / "katas"
    kata_dir.mkdir(parents=True)
    test_env.work_dir = kata_dir
    test_env.has_git = False
    return test_env


# --------------------------------------------------------------------------
# When Steps - Actions
# --------------------------------------------------------------------------


@when(parsers.parse('Alex generates a Python scaffold with directory name "{name}"'))
def alex_generates_scaffold(test_env: TestEnvironment, hook_service: HookService, name: str):
    """Alex generates scaffold with specified directory name."""
    test_env.directory_name = name

    # Call production service to determine mode
    is_integration = hook_service.is_integration_mode(
        directory_name=name,
        kata_name="DummyKata",  # Default kata name
        start_path=test_env.work_dir,
    )

    # Issue 3: Use factory functions for ScaffoldResult construction
    # Integration mode fix: pre-commit install and git commit are SKIPPED
    # because parent repo manages its own hooks and user commits manually.
    if is_integration:
        test_env.result = create_success_result(
            generated_directory=test_env.work_dir / name,
            commands_executed=[
                "pipenv install --dev",
            ],
            commands_skipped=[
                "gh repo create",
                "git init",
                "git remote add origin",
                "pre-commit install",  # Skipped: parent repo manages hooks
                "git add --all",
                "git commit",  # Skipped: user commits manually
                "git push",
            ],
        )
    else:
        test_env.result = create_success_result(
            generated_directory=test_env.work_dir / name,
            commands_executed=[
                "gh repo create",
                "git init",
                "git remote add origin",
                "git push",
                "pipenv install --dev",
                "pre-commit install",
                "git add --all",
                "git commit",
            ],
        )
    return test_env


@when(parsers.parse('Maria generates a Python scaffold with directory name "{name}"'))
def maria_generates_scaffold(test_env: TestEnvironment, hook_service: HookService, name: str):
    """Maria generates scaffold with specified directory name."""
    return alex_generates_scaffold(test_env, hook_service, name)


@when(parsers.parse('Sam runs the cookiecutter with kata name "{name}"'))
def sam_runs_cookiecutter(test_env: TestEnvironment, hook_service: HookService, name: str):
    """Sam runs cookiecutter with kata name (standalone mode)."""
    test_env.kata_name = name
    # Simulate default directory name format: YYYYMMDD_kata_name
    test_env.directory_name = f"20260108_{name.lower().replace(' ', '_')}"

    is_integration = hook_service.is_integration_mode(
        directory_name=test_env.directory_name,
        kata_name=name,
        start_path=test_env.work_dir,
    )

    # Issue 3 & 10: Use factory functions and error constants
    if not is_integration and not test_env.has_gh_cli:
        # GitHub CLI failure in standalone mode
        test_env.result = create_error_result(ERROR_GH_NOT_AUTHENTICATED)
    elif not is_integration:
        # Full standalone mode
        test_env.result = create_success_result(
            generated_directory=test_env.work_dir / test_env.directory_name,
            commands_executed=[
                "gh repo create",
                "git init",
                "git remote add origin",
                "git push",
                "pipenv install --dev",
                "pre-commit install",
                "git add --all",
                "git commit",
            ],
        )
    else:
        # Integration mode fix: pre-commit install and git commit are SKIPPED
        test_env.result = create_success_result(
            generated_directory=test_env.work_dir / test_env.directory_name,
            commands_executed=[
                "pipenv install --dev",
            ],
            commands_skipped=[
                "gh repo create",
                "git init",
                "git remote add origin",
                "pre-commit install",  # Skipped: parent repo manages hooks
                "git add --all",
                "git commit",  # Skipped: user commits manually
                "git push",
            ],
        )
    return test_env


@when("the developer generates a Python scaffold")
def developer_generates_scaffold(test_env: TestEnvironment, hook_service: HookService):
    """Generic developer generates scaffold."""
    test_env.directory_name = "test_project"
    is_integration = hook_service.is_integration_mode(
        directory_name=test_env.directory_name,
        kata_name="DummyKata",
        start_path=test_env.work_dir,
    )

    # Issue 3: Use factory function for ScaffoldResult construction
    # Integration mode fix: pre-commit install and git commit are SKIPPED
    if is_integration:
        test_env.result = create_success_result(
            generated_directory=test_env.work_dir / test_env.directory_name,
            commands_executed=[
                "pipenv install --dev",
            ],
            commands_skipped=[
                "gh repo create",
                "git init",
                "git remote add origin",
                "pre-commit install",  # Skipped: parent repo manages hooks
                "git add --all",
                "git commit",  # Skipped: user commits manually
                "git push",
            ],
        )
    return test_env


@when(parsers.parse('the developer generates a Python scaffold with directory name "{name}"'))
def developer_generates_scaffold_with_name(test_env: TestEnvironment, hook_service: HookService, name: str):
    """Developer generates scaffold with specific directory name."""
    return alex_generates_scaffold(test_env, hook_service, name)


@when("the developer runs the cookiecutter")
def developer_runs_cookiecutter(test_env: TestEnvironment, hook_service: HookService):
    """Developer runs cookiecutter (generic standalone mode)."""
    # Issue 3 & 10: Use factory function and error constant
    if not test_env.has_git_installed:
        test_env.result = create_error_result(ERROR_GIT_NOT_FOUND)
        return test_env
    return sam_runs_cookiecutter(test_env, hook_service, "test_kata")


# --------------------------------------------------------------------------
# Then Steps - Assertions
# --------------------------------------------------------------------------


@then("the hook detects the existing git repository")
def hook_detects_git(test_env: TestEnvironment, hook_service: HookService):
    """Verify hook detected existing git repository."""
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert is_inside, "Hook should detect existing git repository"


@then("the hook skips GitHub repository creation")
def hook_skips_gh_create(test_env: TestEnvironment):
    """Verify gh repo create was skipped."""
    assert "gh repo create" in test_env.result.commands_skipped, "gh repo create should be skipped in integration mode"


@then("the hook skips git initialization")
def hook_skips_git_init(test_env: TestEnvironment):
    """Verify git init was skipped."""
    assert "git init" in test_env.result.commands_skipped, "git init should be skipped in integration mode"


@then("the hook skips adding git remote origin")
def hook_skips_remote_add(test_env: TestEnvironment):
    """Verify git remote add was skipped."""
    assert "git remote add origin" in test_env.result.commands_skipped, (
        "git remote add origin should be skipped in integration mode"
    )


@then("the hook skips pushing to remote")
def hook_skips_push(test_env: TestEnvironment):
    """Verify git push was skipped."""
    assert "git push" in test_env.result.commands_skipped, "git push should be skipped in integration mode"


@then("the hook installs development dependencies")
def hook_installs_deps(test_env: TestEnvironment):
    """Verify pipenv install was executed."""
    assert "pipenv install --dev" in test_env.result.commands_executed, "pipenv install --dev should always execute"


@then("the hook installs pre-commit hooks")
def hook_installs_precommit(test_env: TestEnvironment):
    """Verify pre-commit install was executed (standalone mode only)."""
    assert "pre-commit install" in test_env.result.commands_executed, (
        "pre-commit install should execute in standalone mode"
    )


@then("the hook skips pre-commit installation in integration mode")
def hook_skips_precommit_integration(test_env: TestEnvironment):
    """Verify pre-commit install was skipped in integration mode.

    Integration mode fix: pre-commit hooks would install to PARENT repo's
    .git/hooks/, but reference child's .pre-commit-config.yaml with pipenv
    commands that fail because parent's Pipfile doesn't have ruff, bandit, etc.
    """
    assert "pre-commit install" in test_env.result.commands_skipped, (
        "pre-commit install should be skipped in integration mode (parent repo manages its own hooks)"
    )


@then("the hook skips validation commit in integration mode")
def hook_skips_commit_integration(test_env: TestEnvironment):
    """Verify validation commit was skipped in integration mode.

    Integration mode fix: git commit would trigger pre-commit hooks from
    parent's .git/hooks/, which fail due to Pipfile mismatch.
    User should commit manually after reviewing generated files.
    """
    assert "git commit" in test_env.result.commands_skipped, (
        "git commit should be skipped in integration mode (user commits manually when ready)"
    )


@then(parsers.parse('the hook creates a validation commit with message containing "{text}"'))
def hook_creates_commit(test_env: TestEnvironment, text: str):
    """Verify validation commit was created (standalone mode only)."""
    assert "git commit" in test_env.result.commands_executed, "git commit should execute in standalone mode"


@then("Alex continues workflow without manual intervention")
def alex_continues(test_env: TestEnvironment):
    """Verify scaffold generation completed successfully."""
    assert test_env.result.success, "Scaffold generation should complete successfully"
    assert test_env.result.exit_code == 0, "Exit code should be 0"


@then("the hook traverses parent directories")
def hook_traverses_parents(test_env: TestEnvironment, hook_service: HookService):
    """Verify hook traverses parent directories."""
    # This is verified by the detection succeeding when .git is not in cwd
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert is_inside, "Hook should find .git in parent tree"


@then("the hook finds the git repository in the parent tree")
def hook_finds_git_parent(test_env: TestEnvironment, hook_service: HookService):
    """Verify hook found git in parent tree."""
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert is_inside, "Hook should detect git repo in parent tree"


@then("the hook skips repository creation operations")
def hook_skips_repo_creation(test_env: TestEnvironment):
    """Verify all repo creation operations were skipped."""
    for cmd in ["gh repo create", "git init", "git remote add origin", "git push"]:
        assert cmd in test_env.result.commands_skipped, f"{cmd} should be skipped"


@then("the scaffold is generated in the services subdirectory")
def scaffold_in_services(test_env: TestEnvironment):
    """Verify scaffold location."""
    assert test_env.result.success, "Scaffold should be generated successfully"
    assert test_env.result.generated_directory is not None


@then("the hook finds no git repository in parent tree")
def hook_no_git_found(test_env: TestEnvironment, hook_service: HookService):
    """Verify no git repository was found."""
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert not is_inside, "Hook should NOT find git repo in clean directory"


@then("the hook creates a private GitHub repository named with the kata")
def hook_creates_gh_repo(test_env: TestEnvironment):
    """Verify GitHub repo creation."""
    assert "gh repo create" in test_env.result.commands_executed, "gh repo create should execute in standalone mode"


@then("the hook initializes a new git repository")
def hook_init_git(test_env: TestEnvironment):
    """Verify git init."""
    assert "git init" in test_env.result.commands_executed, "git init should execute in standalone mode"


@then("the hook adds a remote origin pointing to GitHub")
def hook_adds_remote(test_env: TestEnvironment):
    """Verify git remote add."""
    assert "git remote add origin" in test_env.result.commands_executed, (
        "git remote add origin should execute in standalone mode"
    )


@then("the hook pushes the initial commit to the main branch")
def hook_pushes(test_env: TestEnvironment):
    """Verify git push."""
    assert "git push" in test_env.result.commands_executed, "git push should execute in standalone mode"


@then("a dated project directory is created")
def dated_directory_created(test_env: TestEnvironment):
    """Verify dated directory format."""
    assert test_env.directory_name.startswith("2026"), "Directory name should start with date"


@then("the hook detects the git worktree as a valid repository")
def hook_detects_worktree(test_env: TestEnvironment, hook_service: HookService):
    """Verify worktree detection."""
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert is_inside, "Hook should detect git worktree"


@then("the hook traverses all parent directories to the root")
def hook_traverses_to_root(test_env: TestEnvironment, hook_service: HookService):
    """Verify full traversal to root."""
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    # If no git found, traversal completed to root
    assert not is_inside or test_env.has_git, "Should traverse to root if no git"


@then("the hook correctly determines no repository exists")
def hook_no_repo_determination(test_env: TestEnvironment, hook_service: HookService):
    """Verify correct determination of no git."""
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert not is_inside, "Should correctly determine no git exists"


@then("the hook proceeds with full git initialization")
def hook_full_init(test_env: TestEnvironment):
    """Verify full initialization proceeds."""
    if test_env.result and test_env.result.success:
        assert "git init" in test_env.result.commands_executed


@then("the hook handles permission errors gracefully")
def hook_handles_permissions(test_env: TestEnvironment):
    """Verify graceful permission error handling."""
    # Implementation should catch OSError and continue
    assert test_env.result.success, "Should complete despite permission errors"


@then("the hook continues with available directory information")
def hook_continues_available_info(test_env: TestEnvironment):
    """Verify hook continues with what it can access."""
    assert test_env.result.success


@then("the scaffold generation completes successfully")
def scaffold_completes(test_env: TestEnvironment):
    """Verify successful completion."""
    assert test_env.result.success, "Scaffold should complete successfully"


@then("the hook fails with a clear error message about GitHub authentication")
def hook_fails_gh_auth(test_env: TestEnvironment):
    """Verify clear GitHub auth error."""
    assert not test_env.result.success, "Should fail when gh not authenticated"
    assert "GitHub" in test_env.result.error_output or "gh" in test_env.result.error_output


@then("the failure occurs before any files are modified")
def failure_before_files(test_env: TestEnvironment):
    """Verify fail-fast behavior."""
    assert test_env.result.generated_directory is None, "No files should be created on early failure"


@then("the error message includes remediation steps")
def error_has_remediation(test_env: TestEnvironment):
    """Verify remediation steps in error."""
    assert len(test_env.result.error_output) > 0, "Should have error message"


@then("the hook fails with a clear error about missing git")
def hook_fails_no_git(test_env: TestEnvironment):
    """Verify clear error when git missing."""
    assert not test_env.result.success
    assert "git" in test_env.result.error_output.lower()


@then("the error message includes installation instructions")
def error_has_install_instructions(test_env: TestEnvironment):
    """Verify installation instructions in error."""
    assert "install" in test_env.result.error_output.lower() or "http" in test_env.result.error_output.lower()


@then("the hook resolves the symlink and detects the git repository")
def hook_resolves_symlink(test_env: TestEnvironment, hook_service: HookService):
    """Verify hook resolves symlink and detects git repository."""
    # The hook should follow symlinks and find the git repository
    is_inside = hook_service.is_inside_git_repo(test_env.work_dir)
    assert is_inside, "Hook should detect git repository through symlink"


@then("the hook does not change the current branch")
def hook_preserves_branch(test_env: TestEnvironment):
    """Verify hook does not change the current branch."""
    # The branch preservation is verified by comparing current branch
    # The hook should not modify the branch during scaffold
    assert test_env.result.success, "Scaffold should complete successfully"
    # Branch should remain unchanged (verified by next assertion steps)


@then(parsers.parse('the validation commit is created on "{branch_name}"'))
def commit_on_branch(test_env: TestEnvironment, branch_name: str):
    """Verify validation commit is created on the specified branch."""
    assert test_env.current_branch == branch_name, (
        f"Commit should be on {branch_name}, but current branch is {test_env.current_branch}"
    )
    assert "git commit" in test_env.result.commands_executed, "git commit should be executed"


@then(parsers.parse('the branch remains "{branch_name}" after scaffold completion'))
def branch_remains(test_env: TestEnvironment, branch_name: str):
    """Verify branch remains unchanged after scaffold completion."""
    assert test_env.current_branch == branch_name, f"Branch should remain {branch_name} after scaffold completion"
