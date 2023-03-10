import sys
import os
import json
import subprocess

from utils.enums import PythonVersion
from utils.install_dependencies import DependencyInstaller
from utils.helpers import Input, GetPythonVersion
from utils.custom.installer import InstallerRequirements
from utils.custom.extended_macro import ExtendedMacroRequirements, ExtendedMacroFiles
from utils.enums import FileActions
from utils.moonraker import Moonraker
from utils.config import Config

try:
    import requests
    installer_reqs_installed = True
except:
    installer_reqs_installed = False

class Installer():
    def __init__(self):
        self.Moonraker = Moonraker()
        self.Config = Config()

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

    def _clear_screen(self):
        os.system('clear')

    def LoadConfig(self):
        conf = self.Moonraker.get_config()
        self.Config.load_config(conf)

    def MainMenu(self):
        x = self.Config
        klippy_dir = self.report_setting(self.Config.EnvDirectory)
        if self.Config.PythonVersion == PythonVersion.PYTHON2:
            klippy_python = 'python2'
        elif self.Config.PythonVersion == PythonVersion.PYTHON3:
            klippy_python = 'python3'
        else:
            klippy_python = None
        klippy_python = self.report_setting(klippy_python)

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
        Klippy Environment:
            * Directory: %s
            * Python Version: %s

        Klipper:
            * Base Directory: %s
            * Extras Module Directory: %s
        ''' % (
            self.Moonraker.connection.base_url,
            klippy_dir,
            klippy_python,
            klipper_dir,
            klipper_mod_dir,)
        )

        result = Input('Select Option: ')

        vals = {
            '1': self.InstallMenu,
            '2': self.LoadConfigAndMenu,
            '3': self.SettingsMenu,
            '0': sys.exit
        }
        def_val = 'Invalid Option: %s!' % result
        val = vals.get(result, def_val)

        if val == def_val:
            Input(def_val)
            self.MainMenu()
        else:
            val()

    def report_setting(self, val):
        if val is None:
            return '***Not Set***'
        else:
            return val

    def LoadConfigAndMenu(self):
        self.LoadConfig()
        self.MainMenu()

    def InstallMenu(self):
        if self.Config.Config is None or self.Config.Config == {}:
            self.LoadConfig()

        self._clear_screen()
        self.screen_template('Installer: Dependencies')
        self.InstallRequirements()

        self._clear_screen()
        self.screen_template('Installer: Files')
        self.InstallExtendedMacro()

        self._clear_screen()
        self.screen_template("Finalizing Install...")
        self.AddUpdater()
        self.RestartServices()

        print('Install Finished!')
        Input('Type enter to continue.')

        self.MainMenu()

    def InstallRequirements(self):

        py_exec = self.Config.PythonEnvBinary
        py_ver = self.Config.PythonVersion

        py2_reqs_path = self.get_requirements_file(PythonVersion.PYTHON2)
        py3_reqs_path = self.get_requirements_file(PythonVersion.PYTHON3)
        py_reqs = ExtendedMacroRequirements(py_ver, py2_reqs_path, py3_reqs_path)
        req_installer = DependencyInstaller(
            python_version = py_ver,
            python_executable_path = py_exec,
            requirements = py_reqs
        )
        req_installer.InstallRequirements()
        return
    
    def InstallExtendedMacro(self):
        script_path = os.path.normpath(os.path.dirname(__file__))
        macro_path = os.path.join(script_path, os.pardir, 'extended_macro')
        macro_path = os.path.normpath(macro_path)
        f = ExtendedMacroFiles(macro_path, FileActions.SOFT_LINK)
        f.AddActionPathVariable(
            variable = 'klippy_extras',
            value = self.Config.ExtrasDir
        )
        f.ProcessFiles()

    def get_requirements_file(self, python_version):
        script_path = os.path.normpath(os.path.dirname(__file__))
        reqs_path = os.path.join(script_path, os.path.pardir, 'extended_macro', 'requirements')
        reqs_path = os.path.normpath(reqs_path)
        if python_version == PythonVersion.PYTHON2:
            result = os.path.join(reqs_path,'requirements-python2.txt')
        else:
            result = os.path.join(reqs_path,'requirements-python3.txt')
        return result

    def AddUpdater(self):
        print('Checking Moonraker Update Manager...')
        if self.Config.PythonVersion == PythonVersion.PYTHON2:
            self._warn_unsupported_python()
            return
        if not self.Config.UpdateManagerExists:
            result = Input('Would you like to add Extended Macro to your Moonraker Update Manager? Y/n ')
            if result.lower() == 'y':
                print('Adding entry to Update Manager for Extended Macro...')
                self.AddMoonrakerUpdater()
            else:
                print('Update Manager entry not wanted.')
        else:
            print('Update Manager entry already exists.')
        return
    
    def AddMoonrakerUpdater(self):
        script_path = os.path.normpath(os.path.dirname(__file__))
        updater_path = os.path.join(script_path, os.path.pardir, 'extended_macro', 'extended_macro_updater.conf')

        script_path = os.path.normpath(os.path.dirname(__file__))
        reqs_path = os.path.join('extended_macro', 'requirements')

        if self.Config.PythonVersion == PythonVersion.PYTHON2:
            reqs_path = os.path.join(reqs_path, 'requirements-python2.txt')
        elif self.Config.PythonVersion == PythonVersion.PYTHON3:
            reqs_path = os.path.join(reqs_path, 'requirements-python3.txt')

        with open(updater_path, 'r') as f:
            lines = f.readlines()

        req_string = '\nrequirements: %s' % reqs_path
        lines.append(req_string)
        self.Config.UpdateMoonrakerConfig(lines)

    def _warn_unsupported_python(self):
            print('')
            print('********     PLEASE READ:    ********')
            print('')
            print('You are using Python 2.x for your Klippy virtual environment.')
            print('')
            print('While this isn\'t currently an issue, support for Python 2 will end after v1.0 is released.')
            print('Because of this, we will not be adding a section to your Moonraker config to enable updates.')
            print('If you have added this section previously, please remove the entry from your config.')
            print('')
            print('Please consider updating your Klippy environment to Python 3 in the future.')
            print('Press enter to continue...')
            Input()

    def RestartServices(self):
        print('Restarting Klippy...')
        self.Moonraker.RestartKlippy()
        print('Restarting Moonraker...')
        self.Moonraker.RestartMoonraker()
        return

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

        result = Input('Select Option: ')

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
            Input(def_val)
            self.SettingsMenu()
        else:
            func()

    def base_settings_setter(self, default_value, header_text, input_text):
        self._clear_screen()
        self.screen_template(header_text)
        result = Input('%s (%s): ' % (input_text, default_value))
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
        result = Input('New URL (%s): ' % self.report_setting(self.Config.PythonVersion))
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

def check_installer_requirements():
    if not installer_reqs_installed:
        print('Missing installer requirements. Press Enter to install or Ctrl+C to cancel')
        Input()

        py_exec = python_executable()
        py_ver = GetPythonVersion()
        py_reqs = InstallerRequirements(py_ver)
        req_installer = DependencyInstaller(
            python_executable_path = py_exec,
            requirements = py_reqs
        )
        req_installer.InstallRequirements()
        sys.exit()

def install_extras():
    check_installer_requirements()
    installer = Installer()
    installer.MainMenu()

def main():
    install_extras()

if __name__ == '__main__':
    main()

