import sys
from .enums import PythonVersion

def GetPythonVersion():
    v = sys.version
    if v[0] == '2':
        python_version = PythonVersion.PYTHON2
    elif v[0] == '3':
        python_version = PythonVersion.PYTHON3
    else:
        print('Error: Cannot determine Python version running installer!')
        sys.exit()
    return python_version

version = GetPythonVersion()

def Input(text=''):
    if version == PythonVersion.PYTHON2:
        result = raw_input(text)
    elif version == PythonVersion.PYTHON3:
        result = input(text)
    return result