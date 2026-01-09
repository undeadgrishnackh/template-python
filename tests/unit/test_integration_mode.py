"""
Integration Mode Behavior - Unit Tests

Business Context:
    When running inside an existing git repository (integration mode),
    the post-generation hook must adapt its behavior to avoid conflicts:

    1. Skip pre-commit install - parent repo manages its own hooks
    2. Skip validation commit - let user commit manually
    3. Environment setup still runs (pipenv install, tests)

Bug Reference:
    When pre-commit hooks are installed in integration mode:
    - Hooks install to PARENT repo's .git/hooks/
    - Hooks reference `.pre-commit-config.yaml` in CHILD directory
    - Hooks try `pipenv run ruff` but Pipfile is in PARENT (no ruff)
    - Result: Hook fails, commit fails

Solution:
    In integration mode, skip pre-commit install and git commit.
    User manually manages their parent repo's hooks and commits.

Reference: docs/architecture/adrs/ADR-001-git-detection-algorithm.md
"""

from __future__ import annotations

import sys
from pathlib import Path
from unittest.mock import patch


# =============================================================================
# IMPORT FUNCTIONS UNDER TEST
# =============================================================================
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "hooks"))

try:
    from post_gen_project import (
        create_validation_commit,
        install_pre_commit_hooks,
        is_inside_git_repo,
        setup_environment,
    )
except ImportError as e:
    # Functions not yet implemented
    raise ImportError(f"Could not import from post_gen_project: {e}") from e


# =============================================================================
# TEST CLASS - Integration Mode Detection
# =============================================================================


class TestIntegrationModeDetection:
    """Test suite for detecting integration mode (inside existing git repo)."""

    def test_detects_parent_git_repo(self, tmp_path, monkeypatch):
        """AC: Detects git repo in parent directory."""
        # Arrange - Create parent git repo structure
        parent_repo = tmp_path / "parent_project"
        parent_repo.mkdir()
        (parent_repo / ".git").mkdir()

        # Child directory (simulating generated project)
        child_dir = parent_repo / "source"
        child_dir.mkdir()
        monkeypatch.chdir(child_dir)

        # Act & Assert
        assert is_inside_git_repo() is True, "Should detect parent git repo"

    def test_detects_no_git_repo(self, tmp_path, monkeypatch):
        """AC: Detects absence of git repo."""
        # Arrange - Clean directory, no git
        clean_dir = tmp_path / "new_project"
        clean_dir.mkdir()
        monkeypatch.chdir(clean_dir)

        # Act & Assert
        assert is_inside_git_repo() is False, "Should detect no git repo"


# =============================================================================
# TEST CLASS - Integration Mode Behavior
# =============================================================================


class TestIntegrationModeSkipsPreCommitInstall:
    """Test suite for integration mode pre-commit install behavior.

    In integration mode, pre-commit install should be skipped because:
    1. Hooks would install to PARENT repo's .git/hooks/
    2. Parent's Pipfile doesn't have ruff, bandit, etc.
    3. This causes hook failures on commit
    """

    def test_setup_environment_does_not_install_precommit(self, tmp_path, monkeypatch):
        """setup_environment() no longer installs pre-commit hooks.

        Pre-commit installation was moved to install_pre_commit_hooks()
        which is conditionally called only in standalone mode.
        """
        # Arrange
        clean_dir = tmp_path / "project"
        clean_dir.mkdir()
        monkeypatch.chdir(clean_dir)

        commands_executed = []

        def mock_run_command(cmd):
            commands_executed.append(cmd)

        # Act
        with patch("post_gen_project.run_command", side_effect=mock_run_command):
            setup_environment()

        # Assert - pre-commit install should NOT be in setup_environment
        precommit_commands = [cmd for cmd in commands_executed if "pre_hooks" in cmd or "pre-commit" in cmd]
        assert len(precommit_commands) == 0, (
            f"setup_environment should not install pre-commit hooks. Found: {precommit_commands}"
        )


class TestIntegrationModeSkipsValidationCommit:
    """Test suite for integration mode commit behavior.

    In integration mode, git commit should be skipped because:
    1. Pre-commit hooks are in PARENT's .git/hooks/
    2. Hooks fail due to Pipfile mismatch
    3. Better to let user commit manually after reviewing
    """

    def test_create_validation_commit_runs_git_commands(self, tmp_path, monkeypatch):
        """create_validation_commit executes git add and commit."""
        # Arrange
        clean_dir = tmp_path / "project"
        clean_dir.mkdir()
        monkeypatch.chdir(clean_dir)

        commands_executed = []

        def mock_run_command(cmd):
            commands_executed.append(cmd)

        # Act
        with patch("post_gen_project.run_command", side_effect=mock_run_command):
            create_validation_commit("test_kata")

        # Assert
        assert any("git add" in cmd for cmd in commands_executed)
        assert any("git commit" in cmd for cmd in commands_executed)


class TestStandaloneModeStillWorks:
    """Test suite ensuring standalone mode is unaffected.

    Standalone mode (no parent git repo) should continue to:
    1. Install pre-commit hooks
    2. Create validation commit
    3. Push to remote
    """

    def test_install_precommit_hooks_runs_command(self, tmp_path, monkeypatch):
        """install_pre_commit_hooks executes pre-commit install."""
        # Arrange
        clean_dir = tmp_path / "project"
        clean_dir.mkdir()
        monkeypatch.chdir(clean_dir)

        commands_executed = []

        def mock_run_command(cmd):
            commands_executed.append(cmd)

        # Act
        with patch("post_gen_project.run_command", side_effect=mock_run_command):
            install_pre_commit_hooks()

        # Assert
        assert any("install_pre_hooks" in cmd for cmd in commands_executed)

    def test_should_detect_standalone_mode(self, tmp_path, monkeypatch):
        """Standalone mode is detected when no git repo in parent tree."""
        # Arrange
        clean_dir = tmp_path / "new_project"
        clean_dir.mkdir()
        monkeypatch.chdir(clean_dir)

        # Act & Assert
        assert is_inside_git_repo() is False


# =============================================================================
# TEST CLASS - Behavior Verification Summary
# =============================================================================


class TestIntegrationModeMainBehavior:
    """Test the expected behavior of main() based on mode detection.

    These tests verify the conditional logic works correctly.
    The main() function cannot be easily tested directly because it uses
    Jinja2 template variables, but we can verify the detection logic.
    """

    def test_integration_mode_should_skip_git_operations(self, tmp_path, monkeypatch):
        """Integration mode detection implies skipping git operations.

        When is_inside_git_repo() returns True, main() should:
        - NOT call install_pre_commit_hooks()
        - NOT call create_validation_commit()
        - NOT call push_to_remote()
        """
        # Arrange - Create parent git repo
        parent_repo = tmp_path / "parent_project"
        parent_repo.mkdir()
        (parent_repo / ".git").mkdir()

        child_dir = parent_repo / "generated"
        child_dir.mkdir()
        monkeypatch.chdir(child_dir)

        # Act
        is_integration_mode = is_inside_git_repo()

        # Assert
        assert is_integration_mode is True, (
            "Detection should identify integration mode. main() uses this to skip git operations."
        )

    def test_standalone_mode_should_run_all_operations(self, tmp_path, monkeypatch):
        """Standalone mode detection implies running all operations.

        When is_inside_git_repo() returns False, main() should:
        - Call initialize_git_repository()
        - Call install_pre_commit_hooks()
        - Call create_validation_commit()
        - Call push_to_remote()
        """
        # Arrange - Clean directory
        clean_dir = tmp_path / "new_project"
        clean_dir.mkdir()
        monkeypatch.chdir(clean_dir)

        # Act
        is_standalone_mode = not is_inside_git_repo()

        # Assert
        assert is_standalone_mode is True, (
            "Detection should identify standalone mode. main() uses this to run all git operations."
        )


# =============================================================================
# IMPLEMENTATION NOTES
# =============================================================================
#
# These tests verify the fix for the integration mode bug:
#
# BUG: When running cookiecutter inside existing git repo:
#   1. pre-commit install puts hooks in PARENT's .git/hooks/
#   2. Hooks reference child's .pre-commit-config.yaml
#   3. Hooks run `pipenv run ruff` but look at PARENT's Pipfile
#   4. PARENT's Pipfile doesn't have ruff -> hook fails
#
# FIX: In integration mode (main() function):
#   - Skip install_pre_commit_hooks() - parent repo manages hooks
#   - Skip create_validation_commit() - let user commit manually
#   - Skip push_to_remote() - user manages their own remote
#
# The setup_environment() function was also updated to NOT install
# pre-commit hooks (that was redundant with install_pre_commit_hooks()).
#
# =============================================================================
