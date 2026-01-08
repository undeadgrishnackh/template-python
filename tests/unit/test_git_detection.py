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
# TEST CLASS - Git Repository Detection Behaviors
# =============================================================================


class TestGitRepositoryDetection:
    """
    Test suite for git repository detection.

    Verifies the algorithm traverses parent directories to find .git markers,
    correctly distinguishing between:
    - Standalone mode: No git repository found -> full git init
    - Integration mode: Git repository found -> skip git init

    Each test method name follows business language:
    - should_<expected_outcome>_when_<business_scenario>
    """

    # -------------------------------------------------------------------------
    # Scenario: Standalone Mode - No Git Repository
    # -------------------------------------------------------------------------

    def test_should_not_detect_repository_when_directory_has_no_git_marker(
        self, temporary_directory: Path
    ) -> None:
        """
        GIVEN a directory with no .git marker
        WHEN checking if inside a git repository
        THEN detection should return False (standalone mode)

        Business Impact:
            Cookiecutter will create a new git repository for the developer.
        """
        # Arrange - temporary_directory fixture provides clean directory
        _start_path = temporary_directory  # Will be used when implementation exists

        # Act
        # NOTE: Implementation pending - TDD red phase
        # result = is_inside_git_repo(_start_path)

        # Assert
        # assert result is False
        pytest.skip("Implementation pending - TDD red phase (step 01-01)")

    # -------------------------------------------------------------------------
    # Scenario: Integration Mode - Inside Git Repository
    # -------------------------------------------------------------------------

    def test_should_detect_repository_when_git_marker_in_current_directory(
        self, directory_inside_git_repo: Path
    ) -> None:
        """
        GIVEN a directory containing a .git marker
        WHEN checking if inside a git repository
        THEN detection should return True (integration mode)

        Business Impact:
            Cookiecutter will skip git repository creation to avoid conflicts.
        """
        # Arrange - fixture provides directory with .git
        _start_path = (
            directory_inside_git_repo  # Will be used when implementation exists
        )

        # Act
        # result = is_inside_git_repo(_start_path)

        # Assert
        # assert result is True
        pytest.skip("Implementation pending - TDD red phase (step 01-01)")

    def test_should_detect_repository_when_git_marker_in_parent_directory(
        self, directory_with_nested_path_inside_git_repo: Path
    ) -> None:
        """
        GIVEN a directory 3 levels below a .git marker
        WHEN checking if inside a git repository
        THEN detection should traverse upward and return True

        Business Impact:
            Developers often run cookiecutter from subdirectories.
            Detection must find the repository regardless of nesting depth.
        """
        # Arrange - fixture provides nested path inside git repo
        _start_path = directory_with_nested_path_inside_git_repo  # Will be used when implementation exists

        # Act
        # result = is_inside_git_repo(_start_path)

        # Assert
        # assert result is True
        pytest.skip("Implementation pending - TDD red phase (step 01-01)")

    def test_should_detect_repository_when_using_git_worktree(
        self, directory_with_git_worktree: Path
    ) -> None:
        """
        GIVEN a directory where .git is a file (worktree format)
        WHEN checking if inside a git repository
        THEN detection should return True (worktrees are valid repos)

        Business Impact:
            Supports developers using git worktrees for parallel development.
            Algorithm uses exists() not is_dir() for this reason.
        """
        # Arrange - fixture provides worktree with .git file
        _start_path = (
            directory_with_git_worktree  # Will be used when implementation exists
        )

        # Act
        # result = is_inside_git_repo(_start_path)

        # Assert
        # assert result is True
        pytest.skip("Implementation pending - TDD red phase (step 01-01)")

    # -------------------------------------------------------------------------
    # Scenario: Edge Cases - Boundary Conditions
    # -------------------------------------------------------------------------

    def test_should_not_detect_repository_when_git_marker_in_sibling_directory(
        self, tmp_path: Path
    ) -> None:
        """
        GIVEN a .git marker in a sibling directory (not parent chain)
        WHEN checking if inside a git repository
        THEN detection should return False (siblings don't count)

        Business Impact:
            A git repo in a neighboring folder doesn't affect our project.
            Only ancestors in the directory tree matter.

        Directory Structure:
            tmp_path/
            +-- other_project/
            |   +-- .git/    <-- NOT in our parent chain
            +-- our_project/  <-- We are here (no .git above)
        """
        # Arrange - create sibling with git, we're in the other sibling
        sibling_project = tmp_path / "other_project"
        sibling_project.mkdir()
        (sibling_project / ".git").mkdir()

        our_project = tmp_path / "our_project"
        our_project.mkdir()
        _start_path = our_project  # Will be used when implementation exists

        # Act
        # result = is_inside_git_repo(_start_path)

        # Assert
        # assert result is False
        pytest.skip("Implementation pending - TDD red phase (step 01-01)")


# =============================================================================
# FUTURE TESTS - Will be added in subsequent TDD steps
# =============================================================================
#
# The following tests will be added as the implementation progresses:
#
# 1. test_should_handle_filesystem_root_gracefully
#    - Edge case: traversal reaches / or C:\ without finding .git
#
# 2. test_should_use_current_directory_when_no_path_specified
#    - Default behavior: is_inside_git_repo() with no args uses cwd
#
# 3. test_should_resolve_symlinks_in_path
#    - Symlink handling: Path.resolve() follows symlinks
#
# =============================================================================
