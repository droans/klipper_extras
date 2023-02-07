import sys
import os 
import json
import subprocess

try:
    import requests
    import pathlib
    installer_reqs_installed = True
except:
    installer_reqs_installed = False

INSTALLER_REQUIREMENTS = ['requests', 'pathlib']

REQUIREMENTS = {
    'python3': [
        'pyyaml==5.3.1',
        'numpy==1.24.1',
        'pandas==1.5.3',
        'flatten-dict==0.4.2',
    ],
    'python2': [
        'pyyaml==3.13',
        'numpy==1.16.6',
        'pandas==0.23.4',
        'flatten-dict==0.4.2',
    ]
}

UPDATE_MANAGER = '''
    [update_manager extended_macro]
    type: git_repo
    primary_branch: main
    path: ~/klipper_extras
    origin: https://github/com/droans/klipper_extras.git
    env: ~/klippy-env/bin/python
    requirements: ~/klipper_extras/extended_macro/requirements.txt
    install_script: ~/klipper_extras/extended_macro/install.sh
    is_system_service: False
    managed_services: klipper
    '''

EXTENSION_FILES = [
    'extended_macro/delayed_extended.py',
    'extended_macro/extended_macro.py',
    'extended_macro/extended_template.py'
]

def python_executable():
    return os.sys.executable

def install_installer_requirements():
    python = python_executable()
    install_command = [python, '-m', 'pip', 'install'] + INSTALLER_REQUIREMENTS
    
    print('Installing %s...' % ', '.join(INSTALLER_REQUIREMENTS))
    subprocess.call(install_command)
    print('Finished. Please rerun the install script.')
    sys.exit()

class APIConnection(object):
    def __init__(self):
        self._url = 'http://localhost:80'
        self._api_path = '/printer/info'

    @property
    def base_url(self):
        return self._url

    @base_url.setter
    def base_url(self, url):
        self._url = url

    @property
    def api_path(self):
        return self._api_path

    @api_path.setter
    def api_path(self, path):
        self._api_path = path

    @property
    def url(self):
        return self._url + self._api_path

    def Connect(self):
        return requests.get(self.url)

class Config(object):
    def __init__(self, config={}):
        self.load_config(config)
        self._py_version = None

    def load_config(self, config):
        self._config = config
        self._config_file = config.get('config_file', None)
        self._klipper_path = config.get('klipper_path', None)
        self._python_path = config.get('python_path', None)

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
    def PythonVersion(self):
        if self._py_version is not None:
            return self._py_version

        env_dir = self.EnvDirectory
        if env_dir is None:
            return None

        files = os.listdir(env_dir)
        if 'python3' in files:
            return 'python3'
        else:
            return 'python2'

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

class Moonraker():
    def __init__(self):
        self.connection = APIConnection()
    def get_config(self):
        print('Getting config....')
        result = self.connection.Connect()

        if result.status_code != 200:
            print('Moonraker is not accessible at %s' % self.url)
            print('Received error code: %s' % result.status_code)
            print('Type in the correct URL below. You can also press enter to retry with the same URL or `q` to quit.')
            url = raw_input('URL (%s): ' % self.url)
            if url == 'q':
                sys.exit()
            elif len(url):
                self.url = url
                return self.get_config()
            else:
                return self.get_config()

        unloaded_config = result.text
        config = json.loads(unloaded_config)['result']
        self.config = config
        return config

class Installer():
    def __init__(self):
        self.Moonraker = Moonraker()
        self.Config = Config()

    def _clear_screen(self):
        os.system('clear')

    def LoadConfig(self):
        conf = self.Moonraker.get_config()
        self.Config.load_config(conf)

    def LoadConfigAndMenu(self):
        self.LoadConfig()
        self.MainMenu()

    def InstallRequirements(self):
        if self.Config.Config is None:
            self.LoadConfig()
        
    def screen_template(self, menu_name):
        hdr_mid = 37
        menu_mid = int(len(menu_name) / 2)
        menu_pos = hdr_mid - menu_mid
        menu_name = ' ' * menu_pos + menu_name

        screen_hdr = '''
        --------------------------------------------------------------------------
                                  Klipper Extended Macro
                                           v0.4
        %s
        --------------------------------------------------------------------------
        ''' % menu_name
        print(screen_hdr)

    def report_setting(self, val):
        if val is None:
            return '***Not Set***'
        else:
            return val

    def MainMenu(self):
        x = self.Config
        klippy_dir = self.report_setting(self.Config.EnvDirectory)
        klippy_python = self.report_setting(self.Config.PythonVersion)
        klipper_dir = self.report_setting(self.Config.KlipperDir)
        klipper_mod_dir = self.report_setting(self.Config.ExtrasDir)
        
        self._clear_screen()
        self.screen_template('Main Menu')
        print('''

        1) Install
        2) Load Config From Moonraker
        3) Settings
        0) Quit


        Moonraker:
            * URL: %s
            * API Endpoint: %s
        Klippy Environment:
            * Directory: %s
            * Python Version: %s

        Klipper:
            * Base Directory: %s
            * Extras Module Directory: %s
        ''' % (
            self.Moonraker.connection.base_url, 
            self.Moonraker.connection.api_path,
            klippy_dir,
            klippy_python,
            klipper_dir,
            klipper_mod_dir,)
        )

        result = raw_input('Select Option: ')

        vals = {
            '1': self.InstallMenu,
            '2': self.LoadConfigAndMenu,
            '3': self.SettingsMenu,
            '0': sys.exit
        }
        def_val = 'Invalid Option %s!' % result

        val = vals.get(def_val, None)

        if val == def_val:
            raw_input(def_val)
            self.MainMenu()
        else:
            val()
        
    def InstallMenu(self):
        self._clear_screen()
        self.screen_template('Installing')

    def SettingsMenu(self):
        self._clear_screen()
        self.screen_template('Settings')
        
        print( '''

        1) Change Moonraker URL
        2) Change Klippy Environment Directory
        3) Change Klippy Python Version
        4) Change Klipper Base Directory
        5) Change Klipper Extras Modules Directory
        B) Go Back
        ''')

        result = raw_input('Select Option: ')

        def_val = 'Invalid Option %s!' % result

        vals = {
            '1': self.SetMoonrakerURL,
            '2': self.SetKlippyEnvDir,
            '3': self.SetKlippyPyVersion,
            '4': self.SetKlipperBaseDir,
            '5': self.SetKlipperExtrasDir,
            'b': self.MainMenu,
            'B': self.MainMenu
        }
        func = vals.get(result, def_val)
        if func == def_val:
            raw_input(def_val)
            self.SettingsMenu()
        else:
            func()

    def base_settings_setter(self, default_value, header_text, input_text):
        self._clear_screen()
        self.screen_template(header_text)
        result = raw_input('%s (%s): ' % (input_text, default_value))
        return result

    def SetMoonrakerURL(self):
        def_val = self.report_setting(self.Moonraker.connection.base_url)
        result = self.base_settings_setter(self.Moonraker.connection.base_url, 'Set Moonraker URL','New URL')
        if len(result):
            self.Moonraker.connection.base_url = result
        self.SettingsMenu()
    
    def SetKlippyEnvDir(self):
        def_val = self.report_setting(self.Config.EnvDirectory)
        result = self.base_settings_setter(def_val, 'Set Klippy Environment Directory','New Directory')
        if len(result):
            self.Config.EnvDirectory = result
        self.SettingsMenu()

    def SetKlippyPyVersion(self):
        self._clear_screen()
        self.screen_template('Set Klippy Python Version')
        print('''

        1) Python 2
        2) Python 3
        B) Go Back
        ''')
        vals = {
            '1': 'python2',
            '2': 'python3'
        }
        result = raw_input('New URL (%s): ' % self.report_setting(self.Config.PythonVersion))
        val = vals.get(result, None)
        if val is not None: 
            self.Config.PythonVersion = val
        self.SettingsMenu()
    
    def SetKlipperBaseDir(self):
        def_val = self.report_setting(self.Config.KlipperDir)
        result = self.base_settings_setter(def_val, 'Set Klipper Base Directory','New Directory')
        if len(result):
            self.Config.KlipperDir = result
        self.SettingsMenu()
    
    def SetKlipperExtrasDir(self):
        def_val = self.report_setting(self.Config.ExtrasDir)
        result = self.base_settings_setter(def_val, 'Set Klipper Extras Module Directory','New Directory')
        if len(result):
            self.Config.ExtrasDir = result
        self.SettingsMenu()

if not installer_reqs_installed:
    print('Missing installer requirements. Press Enter to install or Ctrl+C to cancel')
    raw_input()
    install_installer_requirements()

def test():
    x = Installer()
    # x.LoadConfig()
    x.MainMenu()
    return x