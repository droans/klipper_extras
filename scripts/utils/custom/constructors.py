from ..enums import PythonVersion, FileActions

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
        self._file_name = None        
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
    def __init__(self, files):
        for file in files:
            if not isinstance(file,File) and not issubclass(file, File):
                raise TypeError('Expected instance `file`, got type `%s`' % file)
        
        self._files = list(files)

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