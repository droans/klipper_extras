from .constructors import RequirementsConstructor
from ..enums import PythonVersion

class InstallerRequirements(RequirementsConstructor):
    def __init__(self, python_version):

        if python_version == PythonVersion.PYTHON2:
            super(InstallerRequirements,self).__init__(python_version)
        else:
            super().__init__(python_version)
        self._python_3_mods = [
            'requests==2.27.1',
            'pathlib==1.0.1',
        ]
        self._python_2_mods = [
            'requests==2.27.1',
            'pathlib==1.0.1',
        ]
        self._python_3_apt = []
        self._python_2_apt = []

    @property
    def Python3Modules(self):
        return self._python_3_mods

    @property
    def Python2Modules(self):
        return self._python_2_mods

    @property
    def Python2Apt(self):
        return self._python_2_apt

    @property
    def Python3Apt(self):
        return self._python_3_apt

    @property
    def Python(self):
        if self._python_version == PythonVersion.PYTHON2:
            return self._python_2_mods
        elif self._python_version == PythonVersion.PYTHON3:
            return self._python_3_mods

    @property
    def Apt(self):
        if self._python_version == PythonVersion.PYTHON2:
            return self._python_2_apt
        elif self._python_version == PythonVersion.PYTHON3:
            return self._python_3_apt