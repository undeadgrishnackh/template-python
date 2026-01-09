"""
Pytest configuration and fixtures for acceptance tests.

This module provides shared fixtures for testing the cookiecutter
post-generation hook functionality across all user stories:
- US-001: Smart Git Repository Detection
- US-002: Configurable Source Directory Name
- US-003: IDE Opening Control
"""

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import pytest
from pytest_bdd import given


if TYPE_CHECKING:
    from tests.doubles.hook_service import ScaffoldResult

from tests.doubles.hook_service import HookService


# --------------------------------------------------------------------------
# Test Environment Configuration
# --------------------------------------------------------------------------


@dataclass
class TestEnvironment:
    """Test environment configuration and state."""

    work_dir: Path
    template_dir: Path
    has_git: bool = False
    git_levels_up: int = 0
    has_gh_cli: bool = True
    has_git_installed: bool = True
    # Issue 8: IDE defaults to False (not installed until proven)
    has_vscode: bool = False
    has_pycharm: bool = False
    directory_name: str | None = None
    kata_name: str | None = None
    ide_option: str | None = None
    result: Optional["ScaffoldResult"] = None
    current_branch: str | None = None


# --------------------------------------------------------------------------
# Git Helper Functions (Issue 2: DRY)
# --------------------------------------------------------------------------


def configure_git_user(cwd: Path) -> None:
    """Configure git user.email and user.name for a repository.

    Extracted helper to eliminate duplication across fixtures.

    Args:
        cwd: Working directory for git commands.
    """
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=cwd,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=cwd,
        capture_output=True,
        check=True,
    )


def init_git_repo(cwd: Path) -> None:
    """Initialize a git repository with user configuration.

    Args:
        cwd: Directory to initialize git repository in.
    """
    subprocess.run(["git", "init"], cwd=cwd, capture_output=True, check=True)
    configure_git_user(cwd)


# --------------------------------------------------------------------------
# Shared Step Definitions (Issue 1: DRY)
# --------------------------------------------------------------------------


@given("the cookiecutter template is available")
def template_available(template_dir: Path) -> None:
    """Verify the cookiecutter template exists (Background step).

    This shared step is used across all user story feature files
    in the Background section to validate template prerequisites.
    """
    assert template_dir.exists(), f"Template directory not found: {template_dir}"
    assert (template_dir / "cookiecutter.json").exists(), "cookiecutter.json not found"
    assert (template_dir / "hooks").exists(), "hooks directory not found"


@pytest.fixture
def template_dir() -> Path:
    """Path to the cookiecutter template root."""
    return Path(__file__).parent.parent.parent


@pytest.fixture
def work_dir(tmp_path: Path) -> Path:
    """Temporary working directory for test execution."""
    return tmp_path


@pytest.fixture
def test_env(work_dir: Path, template_dir: Path) -> TestEnvironment:
    """Create a fresh test environment for each test."""
    return TestEnvironment(
        work_dir=work_dir,
        template_dir=template_dir,
    )


@pytest.fixture
def git_repo(work_dir: Path) -> Path:
    """Create a git repository in the work directory."""
    init_git_repo(work_dir)
    return work_dir


@pytest.fixture
def nested_git_repo(work_dir: Path) -> tuple[Path, Path]:
    """Create a nested directory structure with git repo at root.

    Returns:
        Tuple of (git_root_dir, nested_work_dir)
    """
    init_git_repo(work_dir)

    nested_dir = work_dir / "services" / "python"
    nested_dir.mkdir(parents=True)

    return work_dir, nested_dir


@pytest.fixture
def git_worktree(work_dir: Path) -> Path:
    """Create a git worktree (where .git is a file, not directory)."""
    bare_repo = work_dir / "bare_repo.git"
    subprocess.run(["git", "init", "--bare", str(bare_repo)], capture_output=True, check=True)

    worktree_dir = work_dir / "worktree"
    worktree_dir.mkdir()

    subprocess.run(
        ["git", "clone", str(bare_repo), str(worktree_dir)],
        capture_output=True,
        check=True,
    )

    configure_git_user(worktree_dir)

    return worktree_dir


@pytest.fixture
def symlinked_git_repo(work_dir: Path) -> Path:
    """Create a symlinked directory pointing to a git repository.

    Returns:
        Path to the symlink that points to a directory with a git repo.
    """
    # Create the actual git repository
    actual_repo = work_dir / "actual_project"
    actual_repo.mkdir(parents=True)

    init_git_repo(actual_repo)

    # Create a symlink pointing to the actual repo
    symlink_path = work_dir / "symlinked_project"
    symlink_path.symlink_to(actual_repo)

    return symlink_path


@pytest.fixture
def git_repo_on_branch(work_dir: Path) -> tuple[Path, str]:
    """Create a git repository on a specific feature branch.

    Returns:
        Tuple of (repo_path, branch_name)
    """
    branch_name = "feature/trading-api"

    init_git_repo(work_dir)

    # Create an initial commit (required before creating branches)
    readme = work_dir / "README.md"
    readme.write_text("# Test Project\n")
    subprocess.run(["git", "add", "."], cwd=work_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "commit", "-m", "Initial commit"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )

    # Create and checkout the feature branch
    subprocess.run(
        ["git", "checkout", "-b", branch_name],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )

    return work_dir, branch_name


@pytest.fixture
def hook_service(template_dir: Path) -> HookService:
    """Provide the hook service test double for acceptance tests."""
    return HookService(template_dir)


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line("markers", "US_001: Smart Git Repository Detection")
    config.addinivalue_line("markers", "US_002: Configurable Source Directory Name")
    config.addinivalue_line("markers", "US_003: IDE Opening Control")
    config.addinivalue_line("markers", "happy_path: Happy path scenario")
    config.addinivalue_line("markers", "error_path: Error handling scenario")
    config.addinivalue_line("markers", "edge_case: Edge case scenario")
    config.addinivalue_line("markers", "integration: Integration scenario")
    config.addinivalue_line("markers", "backwards_compatible: Backwards compatibility")
