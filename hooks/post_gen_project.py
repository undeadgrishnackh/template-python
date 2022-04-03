#!/usr/bin/env python
from cProfile import run
import os
import subprocess


PROJECT_DIRECTORY = os.path.realpath(os.path.curdir)


def run_command(command):
    subprocess.run(command, cwd=PROJECT_DIRECTORY, shell=True, check=True, timeout=360)


if __name__ == '__main__':
    run_command('pipenv install --dev')
    run_command('git init')
    run_command('pipenv run install_pre_hooks')
    run_command('pipenv run tests')
