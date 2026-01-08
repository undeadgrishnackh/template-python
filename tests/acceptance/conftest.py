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

if TYPE_CHECKING:
    from tests.doubles.hook_service import ScaffoldResult

from tests.doubles.hook_service import HookService


@dataclass
class TestEnvironment:
    """Test environment configuration and state."""

    work_dir: Path
    template_dir: Path
    has_git: bool = False
    git_levels_up: int = 0
    has_gh_cli: bool = True
    has_git_installed: bool = True
    has_vscode: bool = True
    has_pycharm: bool = True
    directory_name: Optional[str] = None
    kata_name: Optional[str] = None
    ide_option: Optional[str] = None
    result: Optional["ScaffoldResult"] = None


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
    subprocess.run(["git", "init"], cwd=work_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    return work_dir


@pytest.fixture
def nested_git_repo(work_dir: Path) -> tuple[Path, Path]:
    """Create a nested directory structure with git repo at root.

    Returns:
        Tuple of (git_root_dir, nested_work_dir)
    """
    subprocess.run(["git", "init"], cwd=work_dir, capture_output=True, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=work_dir,
        capture_output=True,
        check=True,
    )

    nested_dir = work_dir / "services" / "python"
    nested_dir.mkdir(parents=True)

    return work_dir, nested_dir


@pytest.fixture
def git_worktree(work_dir: Path) -> Path:
    """Create a git worktree (where .git is a file, not directory)."""
    bare_repo = work_dir / "bare_repo.git"
    subprocess.run(
        ["git", "init", "--bare", str(bare_repo)], capture_output=True, check=True
    )

    worktree_dir = work_dir / "worktree"
    worktree_dir.mkdir()

    subprocess.run(
        ["git", "clone", str(bare_repo), str(worktree_dir)],
        capture_output=True,
        check=True,
    )

    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=worktree_dir,
        capture_output=True,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test User"],
        cwd=worktree_dir,
        capture_output=True,
        check=True,
    )

    return worktree_dir


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
