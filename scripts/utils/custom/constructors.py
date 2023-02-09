from ..enums import PythonVersion, FileActions
from ..helpers import Input
import os
import shutil
class Requirements(object):
    def __init__(self, python_version):
        self._python_version = python_version

    @property
    def Python3Modules(self):
        raise NotImplementedError

    @property
    def Python2Modules(self):
        raise NotImplementedError

    @property
    def Python2Apt(self):
        raise NotImplementedError

    @property
    def Python3Apt(self):
        raise NotImplementedError

    @property
    def Python(self):
        raise NotImplementedError

    @property
    def Apt(self):
        raise NotImplementedError

class File(object):
    def __init__(self, file_name = None, action = None, action_path = None):
        self._file_name = file_name
        self._action = action
        self._action_path = action_path

    @property
    def Name(self):
        return self._file_name

    @Name.setter
    def Name(self, name):
        self._file_name = name

    @property
    def Action(self):
        return self._action

    @Action.setter
    def Action(self, action):
        self._action = action


    @property
    def ActionPath(self):
        return self._action_path

    @ActionPath.setter
    def ActionPath(self, path):
        self._action_path = path


class Files(object):
    def __init__(self, files, initial_file_path, action_path_variables={}):
        for file in files:
            if not isinstance(file,File) and not issubclass(file, File):
                raise TypeError('Expected instance `file`, got type `%s`' % file)
            file.Name = os.path.join(initial_file_path, file.Name)

        self._files = files
        self._action_path_variables = action_path_variables

        self._actions = {
            FileActions.SOFT_LINK: self._soft_link,
            FileActions.HARD_LINK: self._hard_link,
            FileActions.COPY: self._copy,
            FileActions.MOVE: self._move
        }

    @property
    def AllFiles(self):
        return self._files

    @property
    def FileNames(self):
        result = [file.Name for file in self._files]
        return result

    def AddFile(self, file):
        if not isinstance(file,File) and not issubclass(file, File):
            raise TypeError('Expected instance `file`, got type `%s`' % file)

        self._files.append(files)

    @property
    def ActionPathVariables(self):
        return self._action_path_variables

    def AddActionPathVariable(self, variable, value):
        self._action_path_variables[variable] = value

    def ProcessFiles(self):
        print(self._action_path_variables)
        for f in self._files:
            action = self._actions[f.Action]
            print('Processing %s' % f.Name)
            action_path = f.ActionPath
            path = self._action_path_variables.get(action_path, action_path)
            path = os.path.join(path, os.path.split(f.Name)[-1])
            action(f, path)

    def _ask_and_overwrite(self, path):
        print('File %s already exists. Overwrite? (Y/N/C)' % path)
        print('Note: If current file is a symlink and points back to extended_macro/file_name.py, there is no need to overwrite')
        result = Input()

        if result.lower() == 'y':
            os.remove(path)
            return True
        elif result.lower() == 'n':
            return False
        elif result.lower() == 'c':
            sys.exit()
        else:
            print('Unrecognized option %s!' % result)
            return self._ask_and_overwrite(path)

    def _soft_link(self, file, path):
        if os.path.exists(path) or os.path.islink(path):
            if not self._ask_and_overwrite(path):
                return
        os.symlink(file.Name, path)

    def _hard_link(self, file, path):
        if os.path.exists(path) or os.path.islink(path):
            if not self._ask_and_overwrite(path):
                return
        os.link(file.Name, path)

    def _copy(self, file, path):
        if os.path.exists(path) or os.path.islink(path):
            if not self._ask_and_overwrite(path):
                return
        shutil.copy2(file.Name, path, follow_symlinks=True)

    def _move(self, file, path):
        if os.path.exists(path) or os.path.islink(path):
            if not self._ask_and_overwrite(path):
                return
        shutil.move(file.Name, path)

