import sys
import subprocess
from utils.enums import PythonVersion

def GetPythonVersion(python_binary=None):
    if python_binary is None:
        return _get_script_python_binary()
    else:
        return _get_binary_python_version(python_binary)

def _get_script_python_binary():
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

def _get_binary_python_version(python_binary):
    script_py = _get_script_python_binary()
    cmd = python_binary
    cmd += ' -c "import sys; print(sys.version_info.major)"'
    v = subprocess.check_output(cmd, shell=True)
    v = int(v)
    if v == 2:
        result = PythonVersion.PYTHON2
    elif v == 3:
        result = PythonVersion.PYTHON3
    return result

def Input(text=''):
    if version == PythonVersion.PYTHON2:
        result = raw_input(text)
    elif version == PythonVersion.PYTHON3:
        result = input(text)
    return result