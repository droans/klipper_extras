import os
from utils.enums import PythonVersion
from utils.helpers import GetPythonVersion

class Config(object):
    def __init__(self, config={}):
        self.load_config(config)
        self._py_version = None

    def load_config(self, config):
        self._config = config
        printer_config = config.get('printer', {})
        self._config_file = printer_config.get('config_file', None)
        self._klipper_path = printer_config.get('klipper_path', None)
        self._python_path = printer_config.get('python_path', None)

        if self._klipper_path is not None:
            self._klippy_extra_dir = self._klipper_path + '/klippy/extras'
        else:
            self._klippy_extra_dir = None

    @property
    def Config(self):
        return self._config

    @property
    def EnvDirectory(self):
        if self._python_path is None:
            return None
        return os.path.dirname(self._python_path)

    @EnvDirectory.setter
    def EnvDirectory(self, directory):
        if directory[:-1] != '/':
            directory = directory + '/'
        self._python_path = directory

    @property
    def PythonEnvBinary(self):
        return self._python_path

    @property
    def PythonVersion(self):
        if self._py_version is not None:
            return self._py_version
        elif self.PythonEnvBinary is None:
            return None
        python_binary = self.PythonEnvBinary
        result = GetPythonVersion(python_binary)
        return result

    @PythonVersion.setter
    def PythonVersion(self, version):
        self._py_version = version

    @property
    def KlipperDir(self):
        return self._klipper_path

    @KlipperDir.setter
    def KlipperDir(self, directory):
        if directory[:-1] != '/':
            directory = directory + '/'
        self._klipper_path = directory

    @property
    def ExtrasDir(self):
        if self._klippy_extra_dir is None:
            return None
        if os.path.exists(self._klippy_extra_dir):
            return self._klippy_extra_dir
        else:
            return None

    @ExtrasDir.setter
    def ExtrasDir(self, directory):
        if directory[:-1] != '/':
            directory = directory + '/'
        self._klippy_extra_dir = directory

    @property
    def ConfigDirectory(self):
        result = os.path.split(self._config_file)[0]
        return result

    @property
    def KlipperConfig(self):
        result = self._config_file
        return result

    @property
    def MoonrakerConfPath(self):
        config_dir = self.ConfigDirectory
        server_conf = self._config.get('server', None)
        moonraker_conf = server_conf.get('files', None)[0]
        moonraker_conf = moonraker_conf.get('filename', None)
        result = os.path.join(config_dir, moonraker_conf)
        if not os.path.exists(result):
            raise FileNotFoundError()
        return result

    @property
    def UpdateManagerExists(self):
        result = False

        server_conf = self._config.get('server', {})
        conf = server_conf.get('config', {})
        conf_keys = conf.keys()
        conf_keys = list(conf_keys)
        updater_keys = [key for key in conf_keys if 'update_manager' in key]

        for key in updater_keys:
            updater_conf = conf.get(key, {})
            repo_origin = updater_conf.get('origin', None)

            if repo_origin == 'https://github.com/droans/klipper_extras.git':
                result = True
        return result

    def UpdateMoonrakerConfig(self, update_list):
        fname = self.MoonrakerConfPath
        with open(fname, 'r') as f:
            conf = f.readlines()

        conf = conf + ['\n'] + update_list
        with open(fname, 'w') as f:
            f.writelines(conf)
        return