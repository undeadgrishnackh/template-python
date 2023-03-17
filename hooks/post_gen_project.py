#!/usr/bin/env python
from cProfile import run
import os
import subprocess


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)

kata_name = "{{ cookiecutter.directory_name }}"


def run_command(command):
    completed_process = subprocess.run(
        command, cwd=PROJECT_DIRECTORY, shell=True, check=True, timeout=360
    )
    if completed_process.returncode != 0:
        raise Exception(
            f"Command {command} failed with return code {completed_process.returncode}"
        )


if __name__ == "__main__":
    print("👷🏻 Creating virtual environment...")
    run_command("pipenv install --dev")

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
    run_command("pycharm .")

    print("👋🏿 bye bye! 🐍")
