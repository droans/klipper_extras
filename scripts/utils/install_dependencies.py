import subprocess
import os
import sys
from utils.enums import PythonVersion
from utils.custom.constructors import RequirementsConstructor
from utils.helpers import Input

class DependencyInstaller(object):
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

        if not isinstance(requirements, RequirementsConstructor) and not issubclass(requirements, RequirementsConstructor):
            raise TypeError('Expected instance of `RequirementsConstructor` for requirements, got %s' % requirements)
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
        self.InstallAptRequirements()
        self.InstallPythonRequirements()

    def InstallAptRequirements(self):
        requirements = self._requirements.Apt
        install_command = []
        if len(requirements):
            print('System package requirements are about to be installed. You may be required to input the root password.')
            print('If you do NOT want to run this as root, type \'N\' below. Otherwise, press enter.')
            result = Input()
            if result.lower() != 'n':
                install_command.append('sudo')
            install_command += ['apt','install'] + requirements + ['-y']
            print('Installing %s...' % ', '.join(requirements))
            print(' '.join(install_command))
            subprocess.call(install_command)
        return

    def InstallPythonRequirements(self):
        requirements = self._requirements.Python
        install_command = [self._python_exec, '-m', 'pip', 'install'] + requirements
        print('Installing %s...' % ', '.join(requirements))
        print(' '.join(install_command))
        subprocess.call(install_command)

    def SaveRequirementsToFile(self, path):
        reqs = '\n'.join(self.Requirements.Python)
        with open(path, 'w') as f:
            f.write(reqs)
            f.close()
        return