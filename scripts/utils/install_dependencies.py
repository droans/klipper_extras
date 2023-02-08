import subprocess
import os 
import sys
from .enums import PythonVersion
from .custom.constructors import Requirements

class PythonDependencyInstaller(object):
    def __init__(self, requirements, python_version = None, python_executable_path = None):
        if python_executable_path is None:
            self._python_exec= os.sys.executable
        else:
            self._python_exec = python_executable_path
        
        if python_version is None:
            v = sys.version
            if v[0] == '2':
                self._python_version = PythonVersion.PYTHON2
            elif v[0] == '3':
                self._python_version = PythonVersion.PYTHON3
        else:
            self._python_version = python_version
            
        if not isinstance(requirements, Requirements) and not issubclass(requirements, Requirements):
            raise TypeError('Expected instance of `Requirements` for requirements, got %s' % requirements)
        self._requirements = requirements      

    @property
    def PythonVersion(self):
        return self._python_version
    
    @PythonVersion.setter
    def PythonVersion(self, version):
        self._python_version = version

    @property
    def PythonExecutablePath(self):
        return self._python_exec
    
    @PythonExecutablePath.setter
    def PythonExecutablePath(self, path):
        self._python_exec = path

    @property
    def Requirements(self):
       return self._requirements

    @Requirements.setter
    def Requirements(self, requirements):
        self._requirements = requirements

    def InstallRequirements(self):
        requirements = self._requirements.Python
        install_command = [self._python_exec, '-m', 'pip', 'install'] + requirements
        print('Installing %s...' % ', '.join(requirements))
        subprocess.call(install_command)
        sys.exit()