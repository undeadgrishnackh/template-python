import re
import sys


MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

kata_name = '{{ cookiecutter.kata_name}}'

kata_dir = '{{ cookiecutter.directory_name }}'

if not re.match(MODULE_REGEX, kata_name):
    print(
        f'ERROR: The project directory ({kata_name}) is not a valid Python module name. Please do not use a - and use _ instead'
    )


    #Exit to cancel project
    sys.exit(1)