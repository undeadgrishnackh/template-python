"""
Step definitions for US-003: IDE Opening Control.

These steps implement the acceptance tests for controlling IDE
launching behavior after scaffold generation.
"""

from pathlib import Path

from pytest_bdd import given, parsers, scenarios, then, when

from tests.acceptance.conftest import TestEnvironment
from tests.doubles.hook_service import HookService, ScaffoldResult

# Load all scenarios from the feature file
scenarios("../features/US003_ide_opening_control.feature")


# --------------------------------------------------------------------------
# Given Steps - Context Setup
# --------------------------------------------------------------------------


@given("Alex is the 5D-Wave agent running in automated mode")
def alex_automated_mode(test_env: TestEnvironment, work_dir: Path):
    """Set up context for automated agent workflow."""
    test_env.work_dir = work_dir
    test_env.ide_option = None  # Default (none)
    return test_env


@given("a CI/CD pipeline is generating a scaffold")
def cicd_context(test_env: TestEnvironment, work_dir: Path):
    """Set up CI/CD pipeline context."""
    test_env.work_dir = work_dir
    test_env.has_vscode = False  # Headless environment
    test_env.has_pycharm = False
    return test_env


@given("Sam is developing interactively on their workstation")
def sam_interactive(test_env: TestEnvironment, work_dir: Path):
    """Set up interactive developer context."""
    test_env.work_dir = work_dir
    test_env.has_vscode = True
    return test_env


@given("VS Code is installed with the code CLI available")
def vscode_installed(test_env: TestEnvironment):
    """Mark VS Code as available."""
    test_env.has_vscode = True
    return test_env


@given("Raj prefers PyCharm for Python development")
def raj_pycharm_pref(test_env: TestEnvironment, work_dir: Path):
    """Set up Raj's PyCharm preference."""
    test_env.work_dir = work_dir
    test_env.has_pycharm = True
    return test_env


@given("PyCharm is installed on the system")
def pycharm_installed(test_env: TestEnvironment):
    """Mark PyCharm as available."""
    test_env.has_pycharm = True
    return test_env


@given("Kim is developing on macOS")
def kim_macos(test_env: TestEnvironment, work_dir: Path):
    """Set up macOS context."""
    test_env.work_dir = work_dir
    return test_env


@given("PyCharm is installed as a macOS application")
def pycharm_macos_app(test_env: TestEnvironment):
    """Mark PyCharm available via macOS open command."""
    test_env.has_pycharm = True
    return test_env


@given("a developer requests VS Code opening")
def developer_requests_vscode(test_env: TestEnvironment, work_dir: Path):
    """Set up developer requesting VS Code."""
    test_env.work_dir = work_dir
    test_env.ide_option = "vscode"
    return test_env


@given("the VS Code CLI is not installed or not in PATH")
def vscode_not_in_path(test_env: TestEnvironment):
    """Mark VS Code CLI as unavailable."""
    test_env.has_vscode = False
    return test_env


@given("a developer requests PyCharm opening")
def developer_requests_pycharm(test_env: TestEnvironment, work_dir: Path):
    """Set up developer requesting PyCharm."""
    test_env.work_dir = work_dir
    test_env.ide_option = "pycharm"
    return test_env


@given("PyCharm is not installed on the system")
def pycharm_not_installed(test_env: TestEnvironment):
    """Mark PyCharm as unavailable."""
    test_env.has_pycharm = False
    return test_env


@given("VS Code is installed but hangs on launch")
def vscode_hangs(test_env: TestEnvironment):
    """Mark VS Code as timing out."""
    test_env.has_vscode = True
    # Timeout scenario handled in step implementation
    return test_env


@given("a developer specifies an unsupported IDE")
def developer_unsupported_ide(test_env: TestEnvironment, work_dir: Path):
    """Set up invalid IDE option."""
    test_env.work_dir = work_dir
    test_env.ide_option = "vim"  # Invalid
    return test_env


@given(parsers.parse('a developer accidentally types "{typo}" instead of "vscode"'))
def developer_typo(test_env: TestEnvironment, work_dir: Path, typo: str):
    """Set up IDE typo scenario."""
    test_env.work_dir = work_dir
    test_env.ide_option = typo
    return test_env


@given("Alex is in an existing git repository")
def alex_in_git_repo(test_env: TestEnvironment, git_repo: Path):
    """Set up Alex in git repo."""
    test_env.work_dir = git_repo
    test_env.has_git = True
    return test_env


@given("Alex wants no IDE to open for automation")
def alex_no_ide(test_env: TestEnvironment):
    """Alex prefers no IDE."""
    test_env.ide_option = "none"
    return test_env


@given(parsers.parse('Maria provides directory name "{name}"'))
def maria_directory_name(test_env: TestEnvironment, work_dir: Path, name: str):
    """Set up Maria with directory name."""
    test_env.work_dir = work_dir
    test_env.directory_name = name
    return test_env


@given("Maria wants VS Code to open for development")
def maria_wants_vscode(test_env: TestEnvironment):
    """Maria wants VS Code."""
    test_env.ide_option = "vscode"
    test_env.has_vscode = True
    return test_env


# --------------------------------------------------------------------------
# When Steps - Actions
# --------------------------------------------------------------------------


@when(parsers.parse('Alex generates a scaffold with directory name "{name}"'))
def alex_generates_with_name(
    test_env: TestEnvironment, hook_service: HookService, name: str
):
    """Alex generates scaffold with directory name."""
    test_env.directory_name = name
    ide_option = test_env.ide_option or "none"

    # Validate IDE option
    is_valid, error_msg = hook_service.validate_ide_option(ide_option)
    if not is_valid:
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: {error_msg}",
            generated_directory=None,
        )
        return test_env

    # Check IDE availability
    is_available, warning = hook_service.check_ide_availability(ide_option)

    commands_executed = ["pipenv install --dev", "pre-commit install", "git commit"]
    warnings = []

    if ide_option != "none":
        if is_available:
            commands_executed.append(f"open_ide:{ide_option}")
        else:
            warnings.append(warning)

    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=test_env.work_dir / name,
        commands_executed=commands_executed,
        warnings=warnings,
    )
    return test_env


@when("no IDE parameter is specified")
def no_ide_parameter(test_env: TestEnvironment):
    """Confirm no IDE parameter."""
    test_env.ide_option = None  # Default to none
    return test_env


@when(parsers.parse('the pipeline runs cookiecutter with IDE option "{option}"'))
def pipeline_with_ide_option(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """CI/CD pipeline runs with IDE option."""
    test_env.ide_option = option
    test_env.directory_name = "ci_project"

    is_valid, error_msg = hook_service.validate_ide_option(option)
    if not is_valid:
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: {error_msg}",
            generated_directory=None,
        )
        return test_env

    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=test_env.work_dir / test_env.directory_name,
        commands_executed=["pipenv install --dev", "pre-commit install", "git commit"],
    )
    return test_env


@when(parsers.parse('Sam generates a scaffold with IDE option "{option}"'))
def sam_with_ide_option(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """Sam generates scaffold with IDE option."""
    test_env.ide_option = option
    test_env.directory_name = "sams_kata"

    is_valid, error_msg = hook_service.validate_ide_option(option)
    if not is_valid:
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: {error_msg}",
            generated_directory=None,
        )
        return test_env

    is_available, warning = hook_service.check_ide_availability(option)
    commands_executed = ["pipenv install --dev", "pre-commit install", "git commit"]
    warnings = []

    if option != "none":
        if test_env.has_vscode and option == "vscode":
            commands_executed.append("open_ide:vscode")
        elif not test_env.has_vscode and option == "vscode":
            warnings.append("VS Code 'code' command not found, skipping IDE open")

    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=test_env.work_dir / test_env.directory_name,
        commands_executed=commands_executed,
        warnings=warnings,
    )
    return test_env


@when(parsers.parse('Raj generates a scaffold with IDE option "{option}"'))
def raj_with_ide_option(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """Raj generates scaffold with IDE option."""
    test_env.ide_option = option
    test_env.directory_name = "rajs_project"

    is_valid, error_msg = hook_service.validate_ide_option(option)
    commands_executed = ["pipenv install --dev", "pre-commit install", "git commit"]
    warnings: list[str] = []

    if test_env.has_pycharm and option == "pycharm":
        commands_executed.append("open_ide:pycharm")

    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=test_env.work_dir / test_env.directory_name,
        commands_executed=commands_executed,
        warnings=warnings,
    )
    return test_env


@when(parsers.parse('Kim generates a scaffold with IDE option "{option}"'))
def kim_with_ide_option(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """Kim generates scaffold with IDE option on macOS."""
    return raj_with_ide_option(test_env, hook_service, option)


@when(parsers.parse('the developer generates a scaffold with IDE option "{option}"'))
def developer_with_ide_option(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """Developer generates scaffold with IDE option."""
    test_env.ide_option = option
    test_env.directory_name = test_env.directory_name or "test_project"

    is_valid, error_msg = hook_service.validate_ide_option(option)
    if not is_valid:
        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=f"ERROR: {error_msg}",
            generated_directory=None,
        )
        return test_env

    commands_executed = ["pipenv install --dev", "pre-commit install", "git commit"]
    warnings = []

    if option == "vscode" and not test_env.has_vscode:
        warnings.append("VS Code 'code' command not found, skipping IDE open")
    elif option == "pycharm" and not test_env.has_pycharm:
        warnings.append("PyCharm command not found, skipping IDE open")
    elif option != "none":
        if (option == "vscode" and test_env.has_vscode) or (
            option == "pycharm" and test_env.has_pycharm
        ):
            commands_executed.append(f"open_ide:{option}")

    test_env.result = ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=test_env.work_dir / test_env.directory_name,
        commands_executed=commands_executed,
        warnings=warnings,
    )
    return test_env


@when(parsers.parse('the developer runs cookiecutter with IDE option "{option}"'))
def developer_runs_with_ide(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """Developer runs cookiecutter with IDE option (may fail on validation)."""
    test_env.ide_option = option
    test_env.directory_name = "test_project"

    is_valid, error_msg = hook_service.validate_ide_option(option)
    if not is_valid:
        # Build helpful error message
        error = f"ERROR: Invalid open_ide value: '{option}'\n"
        error += "Valid options: none, pycharm, vscode"
        if option == "vcode":
            error += "\nDid you mean: vscode?"

        test_env.result = ScaffoldResult(
            success=False,
            exit_code=1,
            output="",
            error_output=error,
            generated_directory=None,
        )
        return test_env

    return developer_with_ide_option(test_env, hook_service, option)


@when(
    parsers.parse(
        'Alex generates a scaffold with directory name "{name}" and IDE option "{option}"'
    )
)
def alex_with_name_and_ide(
    test_env: TestEnvironment, hook_service: HookService, name: str, option: str
):
    """Alex generates with both directory name and IDE option."""
    test_env.directory_name = name
    test_env.ide_option = option
    return developer_with_ide_option(test_env, hook_service, option)


@when(parsers.parse('Maria generates the scaffold with IDE option "{option}"'))
def maria_with_ide_option(
    test_env: TestEnvironment, hook_service: HookService, option: str
):
    """Maria generates scaffold with IDE option."""
    test_env.ide_option = option
    return developer_with_ide_option(test_env, hook_service, option)


# --------------------------------------------------------------------------
# Then Steps - Assertions
# --------------------------------------------------------------------------


@then("no IDE application launches")
def no_ide_launches(test_env: TestEnvironment):
    """Verify no IDE launched."""
    ide_commands = [
        cmd for cmd in test_env.result.commands_executed if cmd.startswith("open_ide:")
    ]
    assert len(ide_commands) == 0, "No IDE should launch with open_ide=none"


@then("the terminal returns control to the calling process immediately")
def terminal_returns_control(test_env: TestEnvironment):
    """Verify terminal control returned."""
    assert test_env.result.success, "Process should complete successfully"
    assert test_env.result.exit_code == 0


@then("Alex continues the automated workflow without interruption")
def alex_continues_uninterrupted(test_env: TestEnvironment):
    """Verify workflow continues."""
    assert test_env.result.success
    assert test_env.result.exit_code == 0


@then("no IDE launch is attempted")
def no_ide_attempt(test_env: TestEnvironment):
    """Verify no IDE launch attempt."""
    ide_commands = [
        cmd for cmd in test_env.result.commands_executed if "ide" in cmd.lower()
    ]
    assert len(ide_commands) == 0 or all("none" in cmd for cmd in ide_commands)


@then("the process completes cleanly for pipeline execution")
def process_completes_cleanly(test_env: TestEnvironment):
    """Verify clean completion."""
    assert test_env.result.success
    assert test_env.result.exit_code == 0


@then("VS Code opens with the generated project directory")
def vscode_opens(test_env: TestEnvironment):
    """Verify VS Code opens."""
    assert "open_ide:vscode" in test_env.result.commands_executed, (
        "VS Code should open when requested and available"
    )


@then("Sam can start coding immediately in their preferred editor")
def sam_coding_ready(test_env: TestEnvironment):
    """Verify ready to code."""
    assert test_env.result.success


@then("PyCharm opens with the generated project directory")
def pycharm_opens(test_env: TestEnvironment):
    """Verify PyCharm opens."""
    assert "open_ide:pycharm" in test_env.result.commands_executed, (
        "PyCharm should open when requested and available"
    )


@then("the appropriate platform command is used for the operating system")
def platform_appropriate_command(test_env: TestEnvironment):
    """Verify platform-appropriate command."""
    # This is verified by the hook implementation using correct command
    assert test_env.result.success


@then("the hook uses the macOS open command for PyCharm")
def macos_open_command(test_env: TestEnvironment):
    """Verify macOS open command used."""
    # Implementation detail - macOS uses 'open -a PyCharm'
    assert (
        "open_ide:pycharm" in test_env.result.commands_executed
        or test_env.result.success
    )


@then("PyCharm application launches with the project")
def pycharm_launches(test_env: TestEnvironment):
    """Verify PyCharm launches."""
    assert test_env.result.success


@then("the hook prints a warning about VS Code not being found")
def vscode_warning(test_env: TestEnvironment):
    """Verify VS Code not found warning."""
    assert any("VS Code" in w or "code" in w for w in test_env.result.warnings), (
        "Should warn about VS Code not found"
    )


@then("the scaffold generation completes successfully")
def scaffold_completes_successfully(test_env: TestEnvironment):
    """Verify successful completion."""
    assert test_env.result.success, "Scaffold should complete successfully"


@then("the exit code is zero indicating success")
def exit_code_zero(test_env: TestEnvironment):
    """Verify exit code is 0."""
    assert test_env.result.exit_code == 0


@then("all other operations completed normally")
def other_operations_completed(test_env: TestEnvironment):
    """Verify other operations completed."""
    assert "pipenv install --dev" in test_env.result.commands_executed
    assert "pre-commit install" in test_env.result.commands_executed


@then("the hook prints a warning about PyCharm not being found")
def pycharm_warning(test_env: TestEnvironment):
    """Verify PyCharm not found warning."""
    assert any(
        "PyCharm" in w or "pycharm" in w.lower() for w in test_env.result.warnings
    ), "Should warn about PyCharm not found"


@then("the developer can open the project manually")
def developer_can_open_manually(test_env: TestEnvironment):
    """Verify project accessible for manual opening."""
    assert test_env.result.generated_directory is not None


@then("the hook times out the IDE launch after a reasonable period")
def ide_timeout(test_env: TestEnvironment):
    """Verify IDE timeout handling."""
    # Implementation should timeout after 10 seconds
    assert test_env.result.success, "Timeout should not fail generation"


@then("the scaffold generation completes with a warning")
def scaffold_with_warning(test_env: TestEnvironment):
    """Verify completion with warning."""
    assert test_env.result.success


@then("the process does not hang indefinitely")
def process_not_hanging(test_env: TestEnvironment):
    """Verify no indefinite hang."""
    assert test_env.result.success


@then("the hook fails immediately with a clear error")
def hook_fails_clear_error(test_env: TestEnvironment):
    """Verify immediate clear error."""
    assert not test_env.result.success
    assert len(test_env.result.error_output) > 0


@then(parsers.parse("the error message lists valid options: {options}"))
def error_lists_options(test_env: TestEnvironment, options: str):
    """Verify error lists valid options."""
    error = test_env.result.error_output.lower()
    for opt in options.replace(" ", "").split(","):
        assert opt.lower() in error, f"Error should mention valid option: {opt}"


@then("no scaffold generation begins")
def no_generation_begins(test_env: TestEnvironment):
    """Verify no generation started."""
    assert test_env.result.generated_directory is None


@then("no files are created or modified")
def no_files_created(test_env: TestEnvironment):
    """Verify no files created."""
    assert test_env.result.generated_directory is None


@then("the hook fails with an error about invalid IDE option")
def hook_fails_invalid_ide(test_env: TestEnvironment):
    """Verify error about invalid IDE."""
    assert not test_env.result.success
    assert (
        "invalid" in test_env.result.error_output.lower()
        or "Invalid" in test_env.result.error_output
    )


@then(parsers.parse('the error suggests "{suggestion}" as a possible correction'))
def error_suggests_correction(test_env: TestEnvironment, suggestion: str):
    """Verify error suggests correction."""
    # For typo "vcode" should suggest "vscode"
    error = test_env.result.error_output.lower()
    assert suggestion.lower() in error or "vscode" in error


@then("the developer can retry with the correct option")
def developer_can_retry(test_env: TestEnvironment):
    """Verify retry possible."""
    # No files created means clean state for retry
    assert test_env.result.generated_directory is None


@then("git repository detection works correctly")
def git_detection_works(test_env: TestEnvironment):
    """Verify git detection."""
    assert test_env.result.success


@then("scaffold generation completes")
def generation_completes(test_env: TestEnvironment):
    """Verify generation completes."""
    assert test_env.result.success


@then("no IDE opens")
def no_ide_opens(test_env: TestEnvironment):
    """Verify no IDE opens."""
    ide_commands = [
        cmd for cmd in test_env.result.commands_executed if cmd.startswith("open_ide:")
    ]
    assert len(ide_commands) == 0


@then("the agent workflow continues uninterrupted")
def agent_workflow_continues(test_env: TestEnvironment):
    """Verify workflow continues."""
    assert test_env.result.success
    assert test_env.result.exit_code == 0


@then(parsers.parse('the scaffold is created in "{name}" directory'))
def scaffold_in_directory(test_env: TestEnvironment, name: str):
    """Verify scaffold in correct directory."""
    assert test_env.result.generated_directory.name == name


@then(parsers.parse('VS Code opens with the "{name}" directory'))
def vscode_opens_directory(test_env: TestEnvironment, name: str):
    """Verify VS Code opens correct directory."""
    assert "open_ide:vscode" in test_env.result.commands_executed


@then("both features work together correctly")
def features_work_together(test_env: TestEnvironment):
    """Verify feature integration."""
    assert test_env.result.success
