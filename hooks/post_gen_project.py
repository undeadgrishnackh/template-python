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


def launch_ide() -> None:
    """Launch IDE for development.

    Opens VS Code in the project directory.
    """
    print("Launching IDE...")
    run_command("code .")


if __name__ == "__main__":
    print("👷🏻 Creating virtual environment...")
    run_command("pipenv install --dev")

    print(
        "👨🏻‍🔧 Forcing virtual environment with the new typing-extensions packaging..."
    )
    run_command("pipenv run forceTypingExtensions")

    print("🧪 running dry test cycle...")
    run_command("pipenv run tests")

    print("😻 git repo creation...")
    run_command(f"gh repo create {kata_name} --private")

    print("😻 Git initializing...")
    run_command("git init")

    print("🐍 Creating local quality gate with git hooks...")
    run_command("pipenv run install_pre_hooks")

    print("😻 Git add remote...")
    run_command(
        f"git remote add origin git@github.com:undeadgrishnackh/{kata_name}.git"
    )

    print("😻 Git branch main...")
    run_command("git branch -M main")

    print("😻 git add all the items in the repo...")
    run_command("git add --all")

    print("😻 git commit the jumpstart...")
    run_command(f'git commit -m "feat: jumpstart {kata_name} with cookiecutter"')

    print("😻 git push the jumpstart...")
    run_command("git push -u origin main")

    print("👩🏻‍💻 time to code!")
    run_command("code .")

    print("👋🏿 bye bye! 🐍")
