from .constructors import RequirementsConstructor, FileConstructor, FilesConstructor
from ..enums import FileActions, PythonVersion
class ExtendedMacroRequirements(RequirementsConstructor):
    def __init__(self, python_version, python2_requirements_file_path, python3_requirements_file_path):
        if python_version == PythonVersion.PYTHON2:
            super(ExtendedMacroRequirements,self).__init__(python_version)
        else:
            super().__init__(python_version)

        self._python_2_mods = self._get_reqs_from_file(python2_requirements_file_path)
        self._python_3_mods = self._get_reqs_from_file(python3_requirements_file_path)
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

    def _get_reqs_from_file(self, file_path):
        with open(file_path, 'r') as f:
            reqs = f.read()
        reqs = reqs.split('\n')
        return reqs

def ExtendedMacroFiles(initial_file_path, link_type = FileActions.SOFT_LINK):
    result = FilesConstructor(
        files=[
            FileConstructor(
                file_name='delayed_extended.py',
                action=link_type,
                action_path='klippy_extras'
            ),
            FileConstructor(
                file_name='extended_macro.py',
                action=link_type,
                action_path='klippy_extras'
            ),
            FileConstructor(
                file_name='extended_template.py',
                action=link_type,
                action_path='klippy_extras'
            )
        ],
        initial_file_path = initial_file_path
    )
    return result
