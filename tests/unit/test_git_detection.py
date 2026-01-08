"""
Git Repository Detection - Unit Tests

Business Context:
    When a developer runs the cookiecutter template, we need to detect
    if they're already inside a git repository. This determines whether
    to skip repository creation (integration mode) or create a new repo
    (standalone mode).

Domain Language:
    - Git Repository Detection: The act of traversing parent directories
      to find a .git marker (directory or file for worktrees)
    - Integration Mode: Running inside existing git repo - skip git init
    - Standalone Mode: Running outside any git repo - full git init

Algorithm (ADR-001):
    Traverse parent directories from start_path until either:
    1. A .git marker is found (return True - inside repository)
    2. Filesystem root is reached (return False - not inside repository)

Reference: docs/architecture/adrs/ADR-001-git-detection-algorithm.md
"""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, NewType

import pytest

if TYPE_CHECKING:
    from typing import Generator


# =============================================================================
# DOMAIN TYPES - Business Language in the Type System
# =============================================================================

# Type aliases for business domain clarity
GitMarkerPath = NewType("GitMarkerPath", Path)
"""A path that represents a .git marker location (directory or worktree file)."""

DirectoryUnderTest = NewType("DirectoryUnderTest", Path)
"""A directory being examined for git repository membership."""


def create_git_marker(parent_directory: Path) -> GitMarkerPath:
    """Create a GitMarkerPath for the .git marker in given directory."""
    return GitMarkerPath(parent_directory / ".git")


# =============================================================================
# TEST FIXTURES - Business Scenarios as Reusable Setup
# =============================================================================


@pytest.fixture
def temporary_directory(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a clean temporary directory for testing.

    Business Context:
        Simulates a project directory where cookiecutter would generate files.
        Starts with no git repository - the "standalone mode" baseline.
    """
    yield tmp_path


@pytest.fixture
def directory_inside_git_repo(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a directory that is inside a git repository.

    Business Context:
        Simulates "integration mode" - developer is adding template files
        to an existing project that's already under version control.
    """
    git_marker = create_git_marker(tmp_path)
    git_marker.mkdir()  # Create .git directory (standard repo)
    yield tmp_path


@pytest.fixture
def directory_with_nested_path_inside_git_repo(
    tmp_path: Path,
) -> Generator[Path, None, None]:
    """Provide a nested directory inside a git repository.

    Business Context:
        Developer runs cookiecutter from a subdirectory of their project.
        The .git directory is in a parent, not the current directory.
        Algorithm must traverse upward to detect the repository.

    Directory Structure:
        tmp_path/
        +-- .git/            <-- Repository root
        +-- src/
            +-- components/  <-- Working directory (3 levels deep)
    """
    git_marker = create_git_marker(tmp_path)
    git_marker.mkdir()  # Repository root

    # Create nested directory structure
    nested_path = tmp_path / "src" / "components"
    nested_path.mkdir(parents=True)

    yield nested_path


@pytest.fixture
def directory_with_git_worktree(tmp_path: Path) -> Generator[Path, None, None]:
    """Provide a directory using git worktree (.git is a file, not directory).

    Business Context:
        Git worktrees allow multiple working directories from a single repository.
        In worktrees, .git is a FILE containing: "gitdir: /path/to/actual/.git"
        Detection must use exists() not is_dir() to handle both cases.
    """
    git_marker = create_git_marker(tmp_path)
    git_marker.write_text("gitdir: /path/to/main/repo/.git/worktrees/feature-branch")
    yield tmp_path


# =============================================================================
# TEST CLASS - is_inside_git_repo() Detection Behaviors
# =============================================================================


class TestIsInsideGitRepo:
    """Test suite for is_inside_git_repo() function.

    Verifies the algorithm traverses parent directories to find .git markers,
    correctly distinguishing between:
    - Standalone mode: No git repository found -> full git init
    - Integration mode: Git repository found -> skip git init

    TDD Red Phase: These tests call is_inside_git_repo() which does not exist yet.
    All tests should fail with NameError until the function is implemented.
    """

    def test_detects_git_directory_in_current_directory(self, tmp_path, monkeypatch):
        """AC-001: Detection works for .git in current directory."""
        # Arrange
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        monkeypatch.chdir(tmp_path)

        # Act
        result = is_inside_git_repo()  # noqa: F821 - TDD Red phase, function pending

        # Assert
        assert result is True

    def test_detects_git_directory_in_parent_directory(self, tmp_path, monkeypatch):
        """AC-002: Detection works for .git at any parent level."""
        # Arrange - .git 2 levels up
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        nested_dir = tmp_path / "level1" / "level2"
        nested_dir.mkdir(parents=True)
        monkeypatch.chdir(nested_dir)

        # Act
        result = is_inside_git_repo()  # noqa: F821 - TDD Red phase, function pending

        # Assert
        assert result is True

    def test_detects_git_directory_three_levels_up(self, tmp_path, monkeypatch):
        """AC-002: Detection works for .git 3+ levels up (monorepo scenario)."""
        # Arrange - .git 3 levels up
        git_dir = tmp_path / ".git"
        git_dir.mkdir()
        nested_dir = tmp_path / "services" / "trading" / "source"
        nested_dir.mkdir(parents=True)
        monkeypatch.chdir(nested_dir)

        # Act
        result = is_inside_git_repo()  # noqa: F821 - TDD Red phase, function pending

        # Assert
        assert result is True

    def test_detects_git_file_for_worktree(self, tmp_path, monkeypatch):
        """AC-003: Detection works for .git file (worktrees, submodules)."""
        # Arrange - .git as file (worktree format)
        git_file = tmp_path / ".git"
        git_file.write_text("gitdir: /path/to/actual/git/dir")
        monkeypatch.chdir(tmp_path)

        # Act
        result = is_inside_git_repo()  # noqa: F821 - TDD Red phase, function pending

        # Assert
        assert result is True


# =============================================================================
# FUTURE TESTS - Will be added in subsequent TDD steps
# =============================================================================
#
# The following tests will be added as the implementation progresses:
#
# 1. test_returns_false_when_no_git_marker_exists
#    - Standalone mode: directory has no .git anywhere in parent chain
#
# 2. test_should_not_detect_repository_when_git_marker_in_sibling_directory
#    - Edge case: .git in sibling directory should not count
#
# 3. test_should_handle_filesystem_root_gracefully
#    - Edge case: traversal reaches / or C:\ without finding .git
#
# =============================================================================
