#!/usr/bin/env python
import os
from pathlib import Path
import subprocess


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def is_inside_git_repo() -> bool:
    """Detect if current directory is inside a git repository.

    Traverses parent directories looking for .git (directory or file).
    Returns True on first match, False if filesystem root reached.

    Handles:
    - Standard .git directories
    - Git worktrees (.git as file)
    - Submodules (.git as file)

    Reference: ADR-001-git-detection-algorithm.md

    Returns:
        bool: True if inside git repo, False otherwise
    """
    current = Path.cwd()
    while current != current.parent:  # Stop at filesystem root
        git_path = current / ".git"
        if git_path.exists():  # Works for both directory and file
            return True
        current = current.parent
    # Check root directory itself
    return (current / ".git").exists()


kata_name = "{{ cookiecutter.directory_name }}"


def run_command(command):
    completed_process = subprocess.run(
        command, cwd=PROJECT_DIRECTORY, shell=True, check=True, timeout=360
    )
    if completed_process.returncode != 0:
        raise Exception(
            f"Command {command} failed with return code {completed_process.returncode}"
        )


def setup_environment():
    """Set up development environment.

    Always runs regardless of git repository status.
    Operations:
    - Install dev dependencies via pipenv
    - Fix typing-extensions packaging
    - Run dry test cycle
    - Install git pre-commit hooks
    """
    print("Setting up development environment...")

    print("  Creating virtual environment...")
    run_command("pipenv install --dev")

    print("  Fixing typing-extensions packaging...")
    run_command("pipenv run forceTypingExtensions")

    print("  Running dry test cycle...")
    run_command("pipenv run tests")

    print("  Installing git hooks...")
    run_command("pipenv run install_pre_hooks")


def initialize_git_repository(kata_name: str) -> None:
    """Initialize a new git repository with GitHub remote.

    Performs repository creation and configuration for STANDALONE mode only.
    In integration mode, this function is NOT called.

    Operations (standalone mode):
    - Create private GitHub repository
    - Initialize local git repository
    - Add remote origin
    - Set main branch

    Args:
        kata_name: Name for the repository
    """
    print("Initializing new git repository...")

    print("  Creating GitHub repository...")
    run_command(f"gh repo create {kata_name} --private")

    print("  Initializing local repository...")
    run_command("git init")

    print("  Adding remote origin...")
    run_command(
        f"git remote add origin git@github.com:undeadgrishnackh/{kata_name}.git"
    )

    print("  Setting main branch...")
    run_command("git branch -M main")


def install_pre_commit_hooks() -> None:
    """Install pre-commit hooks for local quality gate.

    Always runs regardless of git repository status.
    """
    print("Installing pre-commit hooks...")
    run_command("pipenv run install_pre_hooks")


def create_validation_commit(kata_name: str) -> None:
    """Create validation commit with scaffolding.

    Always runs to commit the generated files.
    In integration mode: commits to current branch
    In standalone mode: commits to main branch

    Args:
        kata_name: Name used in commit message
    """
    print("Creating validation commit...")
    print("  Staging all files...")
    run_command("git add --all")
    print("  Committing scaffolding...")
    run_command(f'git commit -m "feat: jumpstart {kata_name} with cookiecutter"')


def push_to_remote() -> None:
    """Push initial commit to remote repository.

    Only runs in standalone mode (new repository).
    Skipped in integration mode (inside existing repo).
    """
    print("Pushing to remote...")
    run_command("git push -u origin main")


def open_ide(ide_option: str) -> None:
    """Open IDE with the generated project directory.

    Supports VS Code and PyCharm. IDE launch failures are non-fatal
    to ensure scaffold generation completes successfully even if
    IDE is unavailable.

    Args:
        ide_option: IDE to open - "none", "vscode", or "pycharm"

    Reference: US-003 IDE Opening Control
    """
    if ide_option == "none":
        print("IDE opening: none (skipped)")
        return

    print(f"Opening IDE: {ide_option}...")

    try:
        if ide_option == "vscode":
            # VS Code CLI: 'code' command opens directory
            subprocess.run(
                ["code", PROJECT_DIRECTORY],
                check=False,  # Non-fatal if VS Code not installed
                timeout=10,
            )
        elif ide_option == "pycharm":
            # PyCharm: try direct command first, fallback to macOS open
            import platform

            if platform.system() == "Darwin":
                # macOS: use 'open -a PyCharm' for .app bundles
                subprocess.run(
                    ["open", "-a", "PyCharm", PROJECT_DIRECTORY],
                    check=False,
                    timeout=10,
                )
            else:
                # Linux/Windows: use pycharm command
                subprocess.run(
                    ["pycharm", PROJECT_DIRECTORY],
                    check=False,
                    timeout=10,
                )
        else:
            print(f"  Warning: Unknown IDE option '{ide_option}', skipping")
    except FileNotFoundError:
        print(f"  Warning: {ide_option} command not found, skipping IDE open")
    except subprocess.TimeoutExpired:
        print(f"  Warning: {ide_option} launch timed out, continuing anyway")
    except Exception as e:
        print(f"  Warning: Failed to open {ide_option}: {e}")


def main():
    """Main orchestration for post-generation hook.

    Execution flow:
    1. Detect if inside existing git repository
    2. Setup environment (always)
    3. Initialize git repository (if not inside existing repo)
    4. Install pre-commit hooks (always)
    5. Create validation commit (always)
    6. Push to remote (only if new repository)
    7. Open IDE (if requested) - US-003

    Reference: docs/architecture/architecture.md Section 5
    """
    kata_name = "{{ cookiecutter.directory_name }}"
    ide_option = "{{ cookiecutter.open_ide }}"

    # Step 1: Detect git repository
    inside_git_repo = is_inside_git_repo()

    if inside_git_repo:
        print("Detected existing git repository - running in integration mode")
    else:
        print("No existing git repository - running in standalone mode")

    # Step 2: Setup environment (always)
    setup_environment()

    # Step 3: Initialize git repository (standalone only)
    if not inside_git_repo:
        initialize_git_repository(kata_name)
    else:
        print("Skipping repository creation (inside existing repo)")

    # Step 4: Install pre-commit hooks (always)
    install_pre_commit_hooks()

    # Step 5: Create validation commit (always)
    create_validation_commit(kata_name)

    # Step 6: Push to remote (standalone only)
    if not inside_git_repo:
        push_to_remote()
    else:
        print("Skipping push (inside existing repo - manage push manually)")

    # Step 7: Open IDE (US-003)
    open_ide(ide_option)

    print("Scaffolding complete!")


if __name__ == "__main__":
    main()
