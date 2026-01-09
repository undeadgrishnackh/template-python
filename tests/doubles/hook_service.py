"""
Test double for the post_gen_project hook service.

This module provides a test double implementation of the hook functionality
for acceptance testing. It mirrors the expected behavior of the production
code in hooks/post_gen_project.py.

During DEVELOP wave, this test double will be replaced with calls to the
actual production implementation following Outside-In TDD pattern.
"""

import os
import shutil
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ScaffoldResult:
    """Result of running the cookiecutter scaffold generation."""

    success: bool
    exit_code: int
    output: str
    error_output: str
    generated_directory: Path | None
    # Issue 4: Added type hints to list fields
    commands_executed: list[str] = field(default_factory=list)
    commands_skipped: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


# --------------------------------------------------------------------------
# Issue 10: Error Message Constants
# --------------------------------------------------------------------------

ERROR_DIRECTORY_EXISTS = "ERROR: Directory '{name}' already exists. Remove or rename it first."
ERROR_INVALID_DIRECTORY_NAME = "ERROR: Invalid directory name '{name}'. Path separators not allowed."
ERROR_INVALID_CHARACTERS = "ERROR: Invalid directory name '{name}'. Characters not allowed: / \\"
ERROR_GH_NOT_AUTHENTICATED = "ERROR: GitHub CLI not authenticated. Run 'gh auth login' first."
ERROR_GIT_NOT_FOUND = "ERROR: git not found. Install git first: https://git-scm.com/downloads"


# --------------------------------------------------------------------------
# Issue 11: Configuration Constants
# --------------------------------------------------------------------------

GITHUB_USERNAME = "undeadgrishnackh"


# --------------------------------------------------------------------------
# Issue 3 & 7: ScaffoldResult Factories and Validation Utilities
# --------------------------------------------------------------------------


def create_error_result(error_message: str) -> ScaffoldResult:
    """Create a failed ScaffoldResult with the given error message.

    Args:
        error_message: The error message to include.

    Returns:
        A ScaffoldResult indicating failure.
    """
    return ScaffoldResult(
        success=False,
        exit_code=1,
        output="",
        error_output=error_message,
        generated_directory=None,
    )


def create_success_result(
    generated_directory: Path,
    commands_executed: list[str] | None = None,
    commands_skipped: list[str] | None = None,
    warnings: list[str] | None = None,
) -> ScaffoldResult:
    """Create a successful ScaffoldResult.

    Args:
        generated_directory: Path to the generated directory.
        commands_executed: List of commands that were executed.
        commands_skipped: List of commands that were skipped.
        warnings: List of warning messages.

    Returns:
        A ScaffoldResult indicating success.
    """
    return ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=generated_directory,
        commands_executed=commands_executed or [],
        commands_skipped=commands_skipped or [],
        warnings=warnings or [],
    )


def create_prompt_fallback_result() -> ScaffoldResult:
    """Create result indicating fallback to kata name prompt.

    Returns:
        A ScaffoldResult indicating prompt fallback was triggered.
    """
    return ScaffoldResult(
        success=True,
        exit_code=0,
        output="",
        error_output="",
        generated_directory=None,
        commands_executed=["prompt_kata_name"],
    )


def contains_path_separators(name: str) -> bool:
    """Check if directory name contains path separator characters.

    Args:
        name: Directory name to check.

    Returns:
        True if name contains path separators.
    """
    return "/" in name or "\\" in name


def validate_directory_name(name: str, work_dir: Path) -> tuple[bool, ScaffoldResult | None]:
    """Validate directory name and return error result if invalid.

    Args:
        name: Directory name to validate.
        work_dir: Working directory to check for existing directories.

    Returns:
        Tuple of (is_valid, error_result). If is_valid is True, error_result is None.
    """
    # Check for existing directory
    target_dir = work_dir / name
    if target_dir.exists():
        return False, create_error_result(ERROR_DIRECTORY_EXISTS.format(name=name))

    # Check for path separators (invalid characters)
    if contains_path_separators(name):
        return False, create_error_result(ERROR_INVALID_DIRECTORY_NAME.format(name=name))

    return True, None


class HookService:
    """Test double for the post_gen_project hook.

    This class provides a testable interface for acceptance tests,
    implementing the expected behavior defined in the architecture
    and ADRs.

    Once production code is implemented in hooks/post_gen_project.py,
    this test double should be updated to call the actual production
    functions for integration testing.
    """

    def __init__(self, template_dir: Path):
        self.template_dir = template_dir
        self.hooks_dir = template_dir / "hooks"

    def is_inside_git_repo(self, start_path: Path) -> bool:
        """Check if path is inside a git repository.

        Implements ADR-001: Git Detection Algorithm.
        Traverses parent directories looking for .git directory or file.

        Args:
            start_path: The directory to start searching from.

        Returns:
            True if inside a git repository, False otherwise.
        """
        current = start_path.resolve()
        while current != current.parent:
            git_path = current / ".git"
            if git_path.exists():
                return True
            current = current.parent
        return (current / ".git").exists()

    def is_integration_mode(self, directory_name: str, kata_name: str, start_path: Path) -> bool:
        """Determine if running in integration mode.

        Implements ADR-002: Directory Name as Integration Signal.

        Integration mode is triggered when:
        1. Explicit directory_name provided (not default format), OR
        2. Running inside existing git repository

        Args:
            directory_name: The directory name parameter value.
            kata_name: The kata name parameter value.
            start_path: The path to check for git repository.

        Returns:
            True if in integration mode, False for standalone mode.
        """
        is_default_format = directory_name.endswith(f"_{kata_name.lower().replace(' ', '_')}")
        return not is_default_format or self.is_inside_git_repo(start_path)

    def validate_ide_option(self, ide_option: str) -> tuple[bool, str]:
        """Validate IDE option parameter.

        Implements ADR-003: IDE Parameter Design.
        Fails fast on invalid options with helpful error message.

        Args:
            ide_option: The open_ide parameter value.

        Returns:
            Tuple of (is_valid, error_message).
        """
        valid_options = {"none", "vscode", "pycharm"}
        if ide_option not in valid_options:
            suggestion = ""
            if ide_option.lower() == "code":
                suggestion = " Did you mean 'vscode'?"
            elif ide_option.lower() in ("charm", "jetbrains"):
                suggestion = " Did you mean 'pycharm'?"
            return (
                False,
                f"Invalid open_ide value: '{ide_option}'. "
                f"Valid options: {', '.join(sorted(valid_options))}.{suggestion}",
            )
        return True, ""

    def check_ide_availability(self, ide_option: str) -> tuple[bool, str]:
        """Check if requested IDE is available on the system.

        Implements ADR-003: Non-fatal IDE availability checking.

        Args:
            ide_option: The validated IDE option.

        Returns:
            Tuple of (is_available, warning_message).
        """
        if ide_option == "none":
            return True, ""

        if ide_option == "vscode":
            if shutil.which("code"):
                return True, ""
            return False, "VS Code 'code' command not found, skipping IDE open"

        if ide_option == "pycharm":
            if shutil.which("pycharm"):
                return True, ""
            if os.path.exists("/Applications/PyCharm.app"):
                return True, ""
            return False, "PyCharm command not found, skipping IDE open"

        return False, f"Unknown IDE option: {ide_option}"
