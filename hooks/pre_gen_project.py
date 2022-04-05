import re
import sys


MODULE_REGEX = r'^[_a-zA-Z][_a-zA-Z0-9]+$'

kata_name = '{{ cookiecutter.kata_name}}'

if not re.match(MODULE_REGEX, kata_name):
    print('ERROR: The project directory (%s) is not a valid Python module name. Please do not use a - and use _ instead' % kata_name)

    #Exit to cancel project
    sys.exit(1)