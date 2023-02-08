from .constructors import Requirements, File, Files
from ..enums import FileActions, PythonVersion
class ExtendedMacroRequirements(Requirements):
    def __init__(self, python_version):
        if python_version == PythonVersion.PYTHON2:
            super(ExtendedMacroRequirements,self).__init__(python_version)
        else:
            super().__init__(python_version)
            
        self._python_2_mods = [
            'pyyaml==3.13',
            'numpy==1.16.6',
            'pandas==0.23.4',
            'flatten-dict==0.4.2'
        ]
        self._python_3_mods = [
            'pyyaml==5.3.1',
            'numpy==1.24.1',
            'pandas==1.5.3',
            'flatten-dict==0.4.2'
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

def ExtendedMacroFiles(initial_file_path):
    result = Files(
        files=[
            File(
                file_name='delayed_extended.py',
                action=FileActions.SOFT_LINK,
                action_path='klippy_extras'
            ),
            File(
                file_name='extended_macro.py',
                action=FileActions.SOFT_LINK,
                action_path='klippy_extras'
            ),
            File(
                file_name='extended_template.py',
                action=FileActions.SOFT_LINK,
                action_path='klippy_extras'
            )
        ],
        initial_file_path = initial_file_path
    )
    return result