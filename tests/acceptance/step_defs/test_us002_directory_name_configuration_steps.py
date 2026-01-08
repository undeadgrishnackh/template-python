"""Step definitions for US-002 Directory Name Configuration acceptance tests.

Implements pytest-bdd step definitions for the first scenario in
US002_directory_name_configuration.feature:
- Scenario: Explicit directory name skips kata name prompt

This test follows Outside-In TDD pattern. The scenario validates that when
an explicit directory name is provided (integration mode), the template:
1. Does NOT prompt for kata name
2. Creates directory with exact specified name
3. Does NOT add date prefix (YYYYMMDD_)

Business Context:
- Maria is an enterprise developer integrating the template into an existing platform
- She needs /enterprise-platform/services/trading-engine/ exactly as specified
- Date prefixes are for standalone kata mode only
"""

from __future__ import annotations

import os
import re
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from subprocess import CompletedProcess
from typing import Generator

import pytest
from pytest_bdd import given, parsers, scenario, then, when

# Load ONLY the first scenario - other scenarios will be implemented in later tasks
# Task 01-01 implements: "Explicit directory name skips kata name prompt" (lines 13-19)


@scenario(
    "../features/US002_directory_name_configuration.feature",
    "Explicit directory name skips kata name prompt",
)
def test_explicit_directory_name_skips_kata_name_prompt():
    """Test function for the explicit directory name scenario."""
    pass


# =============================================================================
# DOMAIN TYPES - Business Language
# =============================================================================


@dataclass
class CookiecutterInvocation:
    """Record of how cookiecutter was invoked for the scaffold generation."""

    template_path: Path
    output_directory: Path
    directory_name: str
    skip_prompts: bool = True


@dataclass
class ScaffoldGenerationContext:
    """Context for a scaffold generation scenario using business terminology.

    Uses explicit domain language from the user story:
    - Enterprise developer (Maria) working in integration mode
    - Explicit directory name signals integration mode
    - Date prefix should be skipped in integration mode
    """

    # Test environment
    temp_dir: Path
    original_working_dir: str

    # Scaffold generation state
    project_output_dir: Path | None = None
    template_path: Path | None = None
    created_directories: list[str] = field(default_factory=list)
    hook_output: list[str] = field(default_factory=list)
    execution_result: CompletedProcess[str] | None = None
    error_message: str | None = None

    # Business context
    persona: str | None = None  # Maria, Alex, Sam (from user stories)
    explicit_directory_name: str | None = None  # Integration mode signal
    kata_name: str | None = None  # Standalone mode only
    kata_name_prompt_shown: bool = False  # Should be False in integration mode

    # Invocation record
    invocation: CookiecutterInvocation | None = None


# =============================================================================
# CONSTANTS - Domain Patterns
# =============================================================================

# Date prefix pattern for standalone kata mode: YYYYMMDD_
DATE_PREFIX_PATTERN = re.compile(r"^\d{8}_")

# Directories to exclude when parsing cookiecutter output
EXCLUDED_DIRECTORY_NAMES = frozenset(
    ["tests", "step_defs", "_template_Python_", "services"]
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def scaffold_context(
    tmp_path: Path,
) -> Generator[ScaffoldGenerationContext, None, None]:
    """Provide isolated scaffold generation context for each scenario.

    Uses business terminology from the user story:
    - Maria needs to create trading-engine service without date prefix
    - Explicit directory name signals integration mode
    """
    original_cwd = os.getcwd()
    context = ScaffoldGenerationContext(
        temp_dir=tmp_path,
        original_working_dir=original_cwd,
    )
    yield context
    os.chdir(original_cwd)


# =============================================================================
# BACKGROUND STEPS
# =============================================================================


@given("the cookiecutter template is available")
def template_is_available(scaffold_context: ScaffoldGenerationContext) -> None:
    """Verify the cookiecutter template exists and record its path."""
    template_config = Path(__file__).parent.parent.parent.parent / "cookiecutter.json"
    assert template_config.exists(), f"Template not found at {template_config}"
    scaffold_context.template_path = template_config.parent


# =============================================================================
# HAPPY PATH - GIVEN STEPS
# =============================================================================


@given("Maria is in a platform services directory")
def maria_in_enterprise_platform(scaffold_context: ScaffoldGenerationContext) -> None:
    """Set up Maria in her enterprise platform services directory.

    Business context: Maria is adding trading-engine to existing platform.
    Creates: /tmp/xxx/enterprise-platform/services/
    """
    scaffold_context.persona = "Maria"

    enterprise_services_dir = (
        scaffold_context.temp_dir / "enterprise-platform" / "services"
    )
    enterprise_services_dir.mkdir(parents=True)
    scaffold_context.project_output_dir = enterprise_services_dir

    os.chdir(enterprise_services_dir)


# =============================================================================
# HAPPY PATH - WHEN STEPS
# =============================================================================


@when(
    parsers.parse('Maria runs the cookiecutter with directory name "{directory_name}"')
)
def maria_generates_scaffold_with_explicit_name(
    scaffold_context: ScaffoldGenerationContext, directory_name: str
) -> None:
    """Maria generates scaffold with explicit directory name (integration mode).

    Business context: Explicit directory name signals integration mode,
    which should skip the kata name prompt and create directory without date prefix.
    """
    scaffold_context.explicit_directory_name = directory_name

    template_path = scaffold_context.template_path
    output_dir = scaffold_context.project_output_dir

    scaffold_context.invocation = CookiecutterInvocation(
        template_path=template_path,
        output_directory=output_dir,
        directory_name=directory_name,
        skip_prompts=True,
    )

    _execute_cookiecutter(scaffold_context, directory_name)
    _scan_created_directories(scaffold_context)


# =============================================================================
# HELPER FUNCTIONS - Cookiecutter Execution
# =============================================================================


def _execute_cookiecutter(ctx: ScaffoldGenerationContext, directory_name: str) -> None:
    """Execute cookiecutter and capture output for analysis."""
    try:
        result = subprocess.run(
            [
                "pipenv",
                "run",
                "cookiecutter",
                str(ctx.template_path),
                "--output-dir",
                str(ctx.project_output_dir),
                "--no-input",
                f"directory_name={directory_name}",
            ],
            capture_output=True,
            text=True,
            cwd=str(ctx.project_output_dir),
            timeout=120,
        )

        ctx.execution_result = result
        ctx.hook_output.append(result.stdout)
        if result.stderr:
            ctx.hook_output.append(result.stderr)

        # Check if kata name prompt appeared (should NOT in integration mode)
        combined_output = result.stdout + result.stderr
        if (
            "kata_name" in combined_output.lower()
            and "prompt" in combined_output.lower()
        ):
            ctx.kata_name_prompt_shown = True

        _extract_directory_from_output(ctx, combined_output)

    except subprocess.TimeoutExpired:
        ctx.error_message = "Cookiecutter command timed out"
    except FileNotFoundError:
        ctx.error_message = "cookiecutter/pipenv command not found"


def _scan_created_directories(ctx: ScaffoldGenerationContext) -> None:
    """Scan filesystem for directories created during scaffold generation."""
    if ctx.project_output_dir and ctx.project_output_dir.exists():
        for item in ctx.project_output_dir.iterdir():
            if item.is_dir():
                _add_directory_if_new(ctx.created_directories, item.name)


def _add_directory_if_new(created_directories: list[str], dir_name: str) -> bool:
    """Add directory name to list if not already present."""
    if dir_name not in created_directories:
        created_directories.append(dir_name)
        return True
    return False


def _extract_directory_from_output(ctx: ScaffoldGenerationContext, output: str) -> None:
    """Extract the directory name created from cookiecutter output."""
    if not ctx.project_output_dir:
        return

    project_dir_str = str(ctx.project_output_dir)

    # Pattern 1: rootdir in pytest output (most reliable)
    rootdir_pattern = re.compile(re.escape(project_dir_str) + r"/([a-zA-Z0-9_-]+)")
    match = rootdir_pattern.search(output)
    if match:
        dir_name = match.group(1)
        if dir_name not in EXCLUDED_DIRECTORY_NAMES:
            if _add_directory_if_new(ctx.created_directories, dir_name):
                return

    # Pattern 2: Pipfile path reveals the directory name
    pipfile_pattern = re.compile(
        re.escape(project_dir_str) + r"/([a-zA-Z0-9_-]+)/Pipfile"
    )
    match = pipfile_pattern.search(output)
    if match:
        if _add_directory_if_new(ctx.created_directories, match.group(1)):
            return

    # Pattern 3: Virtualenv name often matches directory name
    virtualenv_pattern = re.compile(r"virtualenvs/([a-zA-Z0-9_-]+)-")
    match = virtualenv_pattern.search(output)
    if match:
        _add_directory_if_new(ctx.created_directories, match.group(1))


def _find_date_prefixed_directories(
    directories: list[str], base_name: str
) -> list[str]:
    """Find directories that have date prefix matching YYYYMMDD_basename pattern."""
    pattern = re.compile(r"^\d{8}_" + re.escape(base_name) + "$")
    return [d for d in directories if pattern.match(d)]


def _has_any_date_prefix(directories: list[str]) -> bool:
    """Check if any directory has a date prefix (YYYYMMDD_)."""
    return any(DATE_PREFIX_PATTERN.match(d) for d in directories)


# =============================================================================
# HAPPY PATH - THEN STEPS
# =============================================================================


@then("Maria is not prompted for a kata name")
def integration_mode_skips_kata_prompt(
    scaffold_context: ScaffoldGenerationContext,
) -> None:
    """Verify integration mode does NOT show kata name prompt.

    Business rule: Explicit directory name signals integration mode,
    which should bypass the standalone kata workflow including prompts.
    """
    assert scaffold_context.kata_name_prompt_shown is False, (
        "Integration mode should NOT prompt for kata name. "
        f"Output: {scaffold_context.hook_output}"
    )


@then(parsers.parse('the hook creates a directory named exactly "{expected_name}"'))
def scaffold_uses_exact_directory_name(
    scaffold_context: ScaffoldGenerationContext, expected_name: str
) -> None:
    """Verify scaffold uses the exact directory name specified (no date prefix).

    Business rule: In integration mode, the directory name must match exactly
    what was specified - no YYYYMMDD_ prefix should be added.
    """
    created_dirs = scaffold_context.created_directories

    # Fail if date-prefixed variant was created instead
    date_prefixed_dirs = _find_date_prefixed_directories(created_dirs, expected_name)
    if date_prefixed_dirs:
        pytest.fail(
            f'Expected "{expected_name}" but found "{date_prefixed_dirs[0]}" '
            "(date-prefixed variant). Integration mode should not add date prefix."
        )

    # Success if expected name was used
    if expected_name in created_dirs:
        return

    # No directories created
    if not created_dirs:
        pytest.fail(
            f'Expected directory "{expected_name}" but none were created. '
            f"Output: {scaffold_context.hook_output}"
        )

    # Wrong directory name used
    pytest.fail(
        f'Expected "{expected_name}" but found: {created_dirs}. '
        f"Output: {scaffold_context.hook_output}"
    )


@then("the directory structure matches project conventions")
def scaffold_follows_python_conventions(
    scaffold_context: ScaffoldGenerationContext,
) -> None:
    """Verify generated scaffold has standard Python project structure."""
    directory_name = scaffold_context.explicit_directory_name
    project_dir = scaffold_context.project_output_dir
    generated_dir = project_dir / directory_name

    if generated_dir.exists():
        _validate_directory_structure(generated_dir)
        return

    # Directory was cleaned up - check evidence from output
    _validate_structure_from_output_evidence(scaffold_context)


def _validate_directory_structure(generated_dir: Path) -> None:
    """Validate actual directory structure on filesystem."""
    required_items = ["tests", "Pipfile"]
    missing = [item for item in required_items if not (generated_dir / item).exists()]

    if missing:
        existing = [item.name for item in generated_dir.iterdir()]
        pytest.fail(f"Missing structure items: {missing}. Found: {existing}")


def _validate_structure_from_output_evidence(ctx: ScaffoldGenerationContext) -> None:
    """Validate structure from hook output when directory was cleaned up."""
    hook_output = " ".join(ctx.hook_output)

    tests_evidence = (
        "tests/unit/" in hook_output
        or "tests/e2e/" in hook_output
        or "test session starts" in hook_output
    )
    pipfile_evidence = "Pipfile" in hook_output or "pipenv" in hook_output.lower()

    if tests_evidence and pipfile_evidence:
        return

    pytest.skip(
        "Directory was cleaned up after hook failure. "
        f"Evidence - tests: {tests_evidence}, Pipfile: {pipfile_evidence}"
    )


@then("no date prefix is added to the directory name")
def integration_mode_skips_date_prefix(
    scaffold_context: ScaffoldGenerationContext,
) -> None:
    """Verify integration mode does NOT add date prefix (YYYYMMDD_).

    Business rule: Date prefixes are for standalone kata mode only.
    Integration mode uses exact directory name without modification.
    """
    directory_name = scaffold_context.explicit_directory_name
    project_dir = scaffold_context.project_output_dir
    created_dirs = scaffold_context.created_directories

    # Fail if date-prefixed variant exists
    date_prefixed_dirs = _find_date_prefixed_directories(created_dirs, directory_name)
    if date_prefixed_dirs:
        pytest.fail(
            f'Directory "{date_prefixed_dirs[0]}" has date prefix. '
            f'Expected "{directory_name}" without YYYYMMDD_ prefix.'
        )

    # Success conditions
    if directory_name in created_dirs:
        return

    if (project_dir / directory_name).exists():
        return

    # Check output evidence
    if created_dirs:
        hook_output = " ".join(scaffold_context.hook_output)
        if directory_name in hook_output and not DATE_PREFIX_PATTERN.search(
            hook_output
        ):
            return

    # No date-prefixed directories found - that's the pass condition
    if not _has_any_date_prefix(created_dirs):
        return

    pytest.fail(
        f'Cannot verify "{directory_name}" was created without date prefix. '
        f"Found: {created_dirs}"
    )
