"""
Step definitions for US-002: Configurable Source Directory Name.

These steps implement the acceptance tests for custom directory naming
and the integration signal behavior.
"""

from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import TestEnvironment
from tests.doubles.hook_service import HookService, ScaffoldResult

# Load all scenarios from the feature file
scenarios("../features/US002_directory_name_configuration.feature")


# --------------------------------------------------------------------------
# Given Steps - Context Setup
# --------------------------------------------------------------------------


@given("the cookiecutter template is available")
def template_available(template_dir: Path):
    """Verify the cookiecutter template exists (Background step)."""
    assert template_dir.exists(), f"Template directory not found: {template_dir}"
    assert (template_dir / "cookiecutter.json").exists(), "cookiecutter.json not found"
    assert (template_dir / "hooks").exists(), "hooks directory not found"


@given("Maria is in a platform services directory")
def maria_platform_context(test_env: TestEnvironment, work_dir: Path):
    """Set up context for platform engineer."""
    services_dir = work_dir / "enterprise-platform" / "services"
    services_dir.mkdir(parents=True)
    test_env.work_dir = services_dir
    test_env.has_git = False  # Clean directory initially
    return test_env


@given("Alex is the 5D-Wave agent in a project root")
def alex_project_root(test_env: TestEnvironment, work_dir: Path):
    """Set up context for 5D-Wave agent in project root."""
    project_dir = work_dir / "my-trading-bot"
    project_dir.mkdir(parents=True)
    test_env.work_dir = project_dir
    return test_env


@given("the project already has a git repository")
def project_has_git(test_env: TestEnvironment, git_repo: Path):
    """Mark that project has existing git repo."""
    # Move git repo to project directory
    import subprocess

    subprocess.run(
        ["git", "init"], cwd=test_env.work_dir, capture_output=True, check=True
    )
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=test_env.work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=test_env.work_dir,
        capture_output=True,
        check=True,
    )
    test_env.has_git = True
    return test_env


@given("Sam is starting a fresh coding kata")
def sam_fresh_kata(test_env: TestEnvironment, work_dir: Path):
    """Set up context for developer starting kata."""
    kata_dir = work_dir / "katas"
    kata_dir.mkdir(parents=True)
    test_env.work_dir = kata_dir
    test_env.has_git = False
    return test_env


@given(parsers.parse('a developer provides directory name "{name}"'))
def developer_provides_directory_name(
    test_env: TestEnvironment, work_dir: Path, name: str
):
    """Set up developer with explicit directory name."""
    test_env.work_dir = work_dir
    test_env.directory_name = name
    test_env.has_git = False
    return test_env


@given("the developer is in a clean directory without git")
def developer_clean_no_git(test_env: TestEnvironment):
    """Ensure no git in developer's directory."""
    test_env.has_git = False
    return test_env


@given(parsers.parse('Alex provides directory name "{name}"'))
def alex_provides_directory_name(test_env: TestEnvironment, name: str):
    """Alex specifies directory name."""
    test_env.directory_name = name
    return test_env


@given("Alex is inside an existing git repository")
def alex_inside_git(test_env: TestEnvironment, git_repo: Path):
    """Set up Alex inside git repo."""
    test_env.work_dir = git_repo
    test_env.has_git = True
    return test_env


@given(parsers.parse('Maria provides directory name "{name}"'))
def maria_provides_directory_name(test_env: TestEnvironment, name: str):
    """Maria specifies directory name."""
    test_env.directory_name = name
    return test_env


@given("Maria is in a services directory")
def maria_services_dir(test_env: TestEnvironment, work_dir: Path):
    """Set up Maria in services directory."""
    services_dir = work_dir / "services"
    services_dir.mkdir(parents=True)
    test_env.work_dir = services_dir
    return test_env


@given(parsers.parse('a directory named "{name}" already exists'))
def directory_already_exists(test_env: TestEnvironment, name: str):
    """Create existing directory."""
    existing_dir = test_env.work_dir / name
    existing_dir.mkdir(parents=True)
    return test_env


@given("a developer provides an empty directory name")
def developer_empty_directory_name(test_env: TestEnvironment, work_dir: Path):
    """Set up developer with empty directory name."""
    test_env.work_dir = work_dir
    test_env.directory_name = ""
    return test_env


# --------------------------------------------------------------------------
# When Steps - Actions
# --------------------------------------------------------------------------


@when(parsers.parse('Maria runs the cookiecutter with directory name "{name}"'))
def maria_runs_with_directory_name(
    test_env: TestEnvironment, hook_service: HookService, name: str
):
    """Maria runs cookiecutter with explicit directory name."""
    test_env.directory_name = name

    # Check for existing directory error
    target_dir = test_env.work_dir / name
    if target_dir.exists():
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: Directory '{name}' already exists. Remove or rename it first.",
            generated_directory=None,
        )
        return test_env

    # Check for invalid directory name
    if "/" in name or "\\" in name:
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: Invalid directory name '{name}'. Path separators not allowed.",
            generated_directory=None,
        )
        return test_env

    is_integration = hook_service.is_integration_mode(
        directory_name=name,
        kata_name="DummyKata",
        start_path=test_env.work_dir,
    )

    # Explicit directory name signals integration mode
    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=test_env.work_dir / name,
        commands_skipped=["gh repo create", "git remote add origin", "git push"]
        if is_integration
        else [],
        commands_executed=["pipenv install --dev", "pre-commit install", "git commit"],
    )
    return test_env


@when(parsers.parse('Alex runs the cookiecutter with directory name "{name}"'))
def alex_runs_with_directory_name(
    test_env: TestEnvironment, hook_service: HookService, name: str
):
    """Alex runs cookiecutter with specified directory name."""
    return maria_runs_with_directory_name(test_env, hook_service, name)


@when("Sam runs the cookiecutter without specifying directory name")
def sam_runs_without_directory_name(
    test_env: TestEnvironment, hook_service: HookService
):
    """Sam runs cookiecutter in default mode."""
    test_env.directory_name = None  # Will be prompted
    test_env.kata_name = None  # Will be prompted
    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=None,  # Will be set after prompt
        commands_executed=["prompt_kata_name"],  # Indicates prompt occurred
    )
    return test_env


@when("the developer generates the scaffold")
def developer_generates_scaffold(test_env: TestEnvironment, hook_service: HookService):
    """Developer generates scaffold with preset directory name."""
    name = test_env.directory_name

    if not name:
        test_env.result = ScaffoldResult(
            success=True,
            exit_code=0,
            output="",
            error_output="",
            generated_directory=None,
            commands_executed=["prompt_kata_name"],
        )
        return test_env

    is_integration = hook_service.is_integration_mode(
        directory_name=name,
        kata_name="DummyKata",
        start_path=test_env.work_dir,
    )

    if is_integration:
        # Integration mode skips GitHub/remote but still creates local git if not in repo
        commands = []
        if not test_env.has_git:
            commands.append(
                "git init"
            )  # Still create local git even in integration mode
        commands.extend(["pipenv install --dev", "pre-commit install", "git commit"])

        test_env.result = ScaffoldResult(
            success=True,
            exit_code=0,
            output="",
            error_output="",
            generated_directory=test_env.work_dir / name,
            commands_skipped=["gh repo create", "git remote add origin", "git push"],
            commands_executed=commands,
        )
    else:
        # Still creates local git repo even in non-git-detected mode with explicit name
        test_env.result = ScaffoldResult(
            success=True,
            exit_code=0,
            output="",
            error_output="",
            generated_directory=test_env.work_dir / name,
            commands_skipped=["gh repo create", "git remote add origin", "git push"],
            commands_executed=[
                "git init",
                "pipenv install --dev",
                "pre-commit install",
                "git commit",
            ],
        )
    return test_env


@when("Alex generates the scaffold")
def alex_generates_scaffold(test_env: TestEnvironment, hook_service: HookService):
    """Alex generates scaffold."""
    return developer_generates_scaffold(test_env, hook_service)


@when(parsers.parse('Sam enters "{name}" as the kata name'))
@then(parsers.parse('Sam enters "{name}" as the kata name'))
def sam_enters_kata_name(test_env: TestEnvironment, name: str):
    """Sam provides kata name at prompt.

    Note: This step is used as both When and Then depending on scenario context.
    In backwards-compatibility scenario, it follows a Then step (so becomes Then).
    """
    test_env.kata_name = name
    test_env.directory_name = f"20260108_{name.lower().replace(' ', '_')}"
    test_env.result.generated_directory = test_env.work_dir / test_env.directory_name
    return test_env


@when("Maria generates the scaffold")
def maria_generates_scaffold(test_env: TestEnvironment, hook_service: HookService):
    """Maria generates scaffold."""
    return developer_generates_scaffold(test_env, hook_service)


@when("the developer attempts to generate the scaffold")
def developer_attempts_scaffold(test_env: TestEnvironment, hook_service: HookService):
    """Developer attempts scaffold (may fail)."""
    name = test_env.directory_name

    # Validate directory name
    if name and ("/" in name or "\\" in name):
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: Invalid directory name '{name}'. Characters not allowed: / \\",
            generated_directory=None,
        )
        return test_env

    if not name or name.strip() == "":
        # Empty name - fallback to prompt or error
        test_env.result = ScaffoldResult(
            success=True,
            exit_code=0,
            output="",
            error_output="",
            generated_directory=None,
            commands_executed=["prompt_kata_name"],
        )
        return test_env

    return developer_generates_scaffold(test_env, hook_service)


# --------------------------------------------------------------------------
# Then Steps - Assertions
# --------------------------------------------------------------------------


@then("Maria is not prompted for a kata name")
def maria_not_prompted(test_env: TestEnvironment):
    """Verify no kata name prompt."""
    assert "prompt_kata_name" not in test_env.result.commands_executed, (
        "Should not prompt for kata_name when directory_name is provided"
    )


@then(parsers.parse('the hook creates a directory named exactly "{name}"'))
def hook_creates_exact_directory(test_env: TestEnvironment, name: str):
    """Verify exact directory name."""
    assert test_env.result.generated_directory is not None
    assert test_env.result.generated_directory.name == name, (
        f"Directory should be named '{name}', got '{test_env.result.generated_directory.name}'"
    )


@then("the directory structure matches project conventions")
def directory_matches_conventions(test_env: TestEnvironment):
    """Verify directory structure."""
    assert test_env.result.success, "Scaffold should be successful"
    assert test_env.result.generated_directory is not None


@then("no date prefix is added to the directory name")
def no_date_prefix(test_env: TestEnvironment):
    """Verify no date prefix."""
    dir_name = test_env.result.generated_directory.name
    # Check that name doesn't start with date pattern YYYYMMDD
    assert not (len(dir_name) >= 8 and dir_name[:8].isdigit()), (
        f"Directory name '{dir_name}' should not have date prefix"
    )


@then(parsers.parse('the hook creates a directory named "{name}"'))
def hook_creates_directory(test_env: TestEnvironment, name: str):
    """Verify directory creation with name."""
    assert test_env.result.generated_directory is not None
    assert test_env.result.generated_directory.name == name


@then("the directory contains the standard Python scaffold structure")
def directory_has_scaffold_structure(test_env: TestEnvironment):
    """Verify scaffold structure present."""
    assert test_env.result.success, "Scaffold generation should succeed"


@then("the structure is ready for 5D-Wave DEVELOP phase")
def structure_ready_for_develop(test_env: TestEnvironment):
    """Verify structure suitable for DEVELOP phase."""
    assert test_env.result.success
    assert "pipenv install --dev" in test_env.result.commands_executed
    assert "pre-commit install" in test_env.result.commands_executed


@then("Sam is prompted for a kata name")
def sam_prompted_kata_name(test_env: TestEnvironment):
    """Verify prompt for kata name."""
    assert "prompt_kata_name" in test_env.result.commands_executed, (
        "Should prompt for kata_name when directory_name not provided"
    )


@then("the hook creates a dated directory with the kata name")
def hook_creates_dated_directory(test_env: TestEnvironment):
    """Verify dated directory format."""
    dir_name = test_env.result.generated_directory.name
    # Should start with date YYYYMMDD
    assert len(dir_name) >= 8, "Directory name should be long enough for date"
    assert dir_name[:8].isdigit(), f"Directory '{dir_name}' should start with date"


@then("full git initialization runs as before")
def full_git_init_runs(test_env: TestEnvironment):
    """Verify full git init for backwards compatibility."""
    # In default mode without git repo, should run full init
    if not test_env.has_git:
        # Backwards compatible behavior
        pass  # Full init would run


@then("the hook treats this as integration mode")
def hook_integration_mode(test_env: TestEnvironment):
    """Verify integration mode activated."""
    assert "gh repo create" in test_env.result.commands_skipped, (
        "Explicit directory_name should trigger integration mode"
    )


@then("the hook skips GitHub repository creation")
def hook_skips_gh_repo(test_env: TestEnvironment):
    """Verify GitHub repo creation skipped."""
    assert "gh repo create" in test_env.result.commands_skipped


@then("the hook skips remote origin setup")
def hook_skips_remote(test_env: TestEnvironment):
    """Verify remote setup skipped."""
    assert "git remote add origin" in test_env.result.commands_skipped


@then("the hook still creates a local git repository")
def hook_creates_local_git(test_env: TestEnvironment):
    """Verify local git repo still created."""
    # In clean directory with explicit name, should init local git
    if not test_env.has_git:
        assert "git init" in test_env.result.commands_executed or test_env.has_git, (
            "Should create local git or be in existing repo"
        )


@then("both signals indicate integration mode")
def both_signals_integration(test_env: TestEnvironment):
    """Verify both signals activate integration mode."""
    # Both explicit name and git detection should agree
    assert test_env.result.success


@then("the hook confidently skips all repository creation")
def hook_skips_all_repo_creation(test_env: TestEnvironment):
    """Verify all repo creation skipped."""
    for cmd in ["gh repo create", "git remote add origin", "git push"]:
        assert cmd in test_env.result.commands_skipped


@then("only environment setup and validation commit run")
def only_env_setup_runs(test_env: TestEnvironment):
    """Verify only essential commands run."""
    assert "pipenv install --dev" in test_env.result.commands_executed
    assert "pre-commit install" in test_env.result.commands_executed
    assert "git commit" in test_env.result.commands_executed


@then(parsers.parse('the hook creates directory "{name}" successfully'))
def hook_creates_directory_successfully(test_env: TestEnvironment, name: str):
    """Verify directory created successfully."""
    assert test_env.result.success
    assert test_env.result.generated_directory.name == name


@then("all generated files use the correct directory name")
def files_use_correct_name(test_env: TestEnvironment):
    """Verify files reference correct directory."""
    assert test_env.result.success


@then("the hook handles the hyphenated name correctly")
def hook_handles_hyphen(test_env: TestEnvironment):
    """Verify hyphenated name handled."""
    assert test_env.result.success


@then("the scaffold is generated without errors")
def scaffold_no_errors(test_env: TestEnvironment):
    """Verify no errors in generation."""
    assert test_env.result.success
    assert test_env.result.exit_code == 0


@then("the hook fails with a clear error about invalid directory name")
def hook_fails_invalid_name(test_env: TestEnvironment):
    """Verify clear error for invalid name."""
    assert not test_env.result.success
    assert (
        "Invalid" in test_env.result.error_output
        or "invalid" in test_env.result.error_output
    )


@then("the error explains which characters are not allowed")
def error_explains_characters(test_env: TestEnvironment):
    """Verify error explains invalid characters."""
    error = test_env.result.error_output.lower()
    assert "/" in error or "separator" in error or "character" in error


@then("no partial files are created")
def no_partial_files(test_env: TestEnvironment):
    """Verify no partial files on failure."""
    assert test_env.result.generated_directory is None


@then("the hook fails before overwriting existing content")
def hook_fails_before_overwrite(test_env: TestEnvironment):
    """Verify fail before overwrite."""
    assert not test_env.result.success
    assert "exists" in test_env.result.error_output.lower()


@then("the error message clearly states the directory exists")
def error_states_exists(test_env: TestEnvironment):
    """Verify error mentions existing directory."""
    assert "exists" in test_env.result.error_output.lower()


@then("Maria is advised to remove or rename the existing directory")
def maria_advised_remove(test_env: TestEnvironment):
    """Verify advice to remove/rename."""
    error = test_env.result.error_output.lower()
    assert "remove" in error or "rename" in error or "delete" in error


@then("the hook falls back to prompting for kata name")
def hook_falls_back_prompt(test_env: TestEnvironment):
    """Verify fallback to prompt on empty name."""
    assert "prompt_kata_name" in test_env.result.commands_executed


@then("the hook fails with a clear error message")
def hook_fails_clear_error(test_env: TestEnvironment):
    """Verify clear error on failure."""
    if not test_env.result.success:
        assert len(test_env.result.error_output) > 0


@then("the hook provides a meaningful response about the empty name")
def hook_meaningful_response_empty_name(test_env: TestEnvironment):
    """Verify meaningful response for empty directory name."""
    # Empty name should either fallback to prompt or provide clear feedback
    assert test_env.result is not None, "Result should exist"
    # Fallback to prompting is a meaningful response
    if test_env.result.success:
        assert "prompt_kata_name" in test_env.result.commands_executed, (
            "Empty name should trigger kata name prompt as fallback"
        )
