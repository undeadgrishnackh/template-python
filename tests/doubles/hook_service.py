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
from typing import Optional


@dataclass
class ScaffoldResult:
    """Result of running the cookiecutter scaffold generation."""

    success: bool
    exit_code: int
    output: str
    error_output: str
    generated_directory: Optional[Path]
    commands_executed: list = field(default_factory=list)
    commands_skipped: list = field(default_factory=list)
    warnings: list = field(default_factory=list)


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

    def is_integration_mode(
        self, directory_name: str, kata_name: str, start_path: Path
    ) -> bool:
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
        is_default_format = directory_name.endswith(
            f"_{kata_name.lower().replace(' ', '_')}"
        )
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
