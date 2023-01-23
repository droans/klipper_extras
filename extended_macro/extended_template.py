# Necessary modules for configuration
import os, yaml, imp

# Additional defaults for G-Code
import math, pandas, numpy, datetime, itertools, collections

# DEFAULTS
# The default imports to be loaded by extended_template. 
# These do not need to be defined by the user in their config file
# If there is a name collision, the default imports will be given priority
# while the user defined functions are renamed with an underscore.
# 
# For example, if the user were to define their own function named `list` (the same name as a default below),
# the user defined `list` will be renamed to `_list`.
DEFAULTS = {
    'math': math,
    'pandas': pandas,
    'numpy': numpy,
    'datetime': datetime,
    'itertools': itertools,
    'collections': collections,
    'dir': dir,
    'getattr': getattr,
    'setattr': setattr,
    'locals': locals,
    'globals': globals,
    'list': list,
    'dict': dict,
    'set': set,
    'tuple': tuple,
    'str': str,
    'int': int,
    'float': float,
    'bool': bool,
    'type': type,
}

class Logger():
    def __init__(self, config):
        self.Error = config.error

# Load YAML config to self.Functions so the template loader can be created
class YamlLoader():
    def __init__(self, yaml_path, config):
        self.DefaultsLoaded = False
        self.path = yaml_path
        self.Log = Logger(config)

        with open(yaml_path, 'r') as f:
            self.yaml = yaml.load(f, Loader=yaml.Loader)
        
        func_yaml = self.yaml.get('functions',None)
        self._funcs = self._import_function_dict(func_yaml)

    # Loops through each item in the config, passes
    # the data off to _import_function which will return
    # the actual function if it exists, and then adds
    # each function to the function dictionary so they can 
    # be added by extended_macro to the Jinja environment

    def GetFunctions(self):
        return self._funcs

    def _import_function_dict(self, funcs):
        return_funcs = {}
        for key, val in funcs.items():
            func = self._import_function(val['path'], val['function'])
            return_funcs[key] = func
        return return_funcs

    def _import_function(self, func_path, func_name):
        module = imp.load_source('script', func_path)
        if func_name not in dir(module):
            raise self.Log.Error('extended_template: Function %s not found in file %s' % (func_name, func_path))
        else:
            func = getattr(module, func_name)
            return func

class DefaultLoader:
    def __init__(self, yaml_path, config):
        self.DefaultsLoaded = True
        self.path = yaml_path
        self.Log = Logger(config)
        self.printer = config.printer

        self.custom_defaults = {
            'update_gcode_variable': self.update_gcode_variable,
            'call_macro': self.call_macro
        }

        self._funcs = self._load_defaults()

    def _load_defaults(self):
        def_funcs = {}
        def_funcs.update(DEFAULTS)
        def_funcs.update(self.custom_defaults)
        return def_funcs

    def GetFunctions(self):
        return self._funcs

    def get_macro(self, macro_name):
        if 'extended_macro' not in macro_name and 'gcode_macro' not in macro_name:
            try:
                macro = self.printer.lookup_object('extended_macro %s' % (macro_name))
            except:
                macro = self.printer.lookup_object('gcode_macro %s' % (macro_name))
                
        else:
            macro = self.printer.lookup_object(macro_name)

        return macro

    def update_gcode_variable(self, macro_name, variable, value):
        # macro = self.printer.lookup_object(macro_name)
        macro = self.get_macro(macro_name)
        if variable not in macro.variables:
            raise self.Log.Error('Unknown gcode_macro variable %s' % (variable,))
        macro.variables[variable] = value

    def call_macro(self, macro_name, **params):
        macro = self.get_macro(macro_name)
        kwparams = {}
        kwparams.update(macro.template.create_template_context())
        kwparams['params'] = params
        macro.template.run_gcode_from_command(kwparams)
        
# Grabs the Klipper config for extended_template,
# uses the path variable to determine the extension,
# determines the proper loader for that extension,
# and returns the value from that loader which received
# the path and the Klipper config object.
class PythonFunction:
    def __init__(self, config):
        self.config = config
        self.printer = self.config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.Log = Logger(config)
        
        self.config_path = config.get('path', None)
        self.Functions = self._import()

    def _import(self):
        defaults_loaded = False
        if self.config_path is not None:
            user_funcs, defaults_loaded = self._import_user_functions()
        else:
            user_funcs = []
            defaults_loaded = False

        if not defaults_loaded:
            default_funcs, defaults_loaded = self._load_defaults()

        all_funcs = {}
        all_funcs = default_funcs.copy()

        for key, val in user_funcs.items():
            if key in all_funcs:
                u_key = '_%s' % key
            else:
                u_key = key

            all_funcs[u_key] = val

        print('All Funcs:')
        print(all_funcs)
        return all_funcs

        
    def _get_loader(self, ext):
        loader = None
        for l in LOADERS:
            c_ext = l['extensions']

            if type(c_ext) is str:
                c_ext = [c_ext]

            if ext in l['extensions']:
                loader = l['func_loader']
                return loader

        if loader is None:
            raise self.Log.Error('extended_template: No loader found for extension %s' % ext)

    def _import_user_functions(self):
        ext = self.config_path.split('.')[-1]
        loader = self._get_loader(ext)
        funcs, defaults_loaded = self._load_functions(loader, self.config_path)
        return funcs, defaults_loaded

    def _load_defaults(self):
        loader = self._get_loader('default')
        funcs = self._load_functions(loader)
        return funcs
        
    def _load_functions(self, loader, config_path = None):
        result = loader(config_path, self.config)
        funcs = result.GetFunctions()
        defaults_loaded = result.DefaultsLoaded

        return funcs, defaults_loaded

    def _insert_function(self, func_name, func):
        if func_name in self.Functions: 
            func_name = '_%s' % func_name

def load_config(config):
    return PythonFunction(config)

# LOADERS
# The definitions in this list will be used to determine the proper loader for the extensions given
# 
# Since different loaders might need or want different methods of parsing the file, 
# the script expects that the loader is a function, not a class. The function should
# process the config file and return a dictionary with the jinja function name as the key
# and the actual Python function as the value
# 
# The loader for DEFAULTS should be defined with an extension of ['default']
# This loader will be ignored if the property loader.DefaultsLoaded property is true (see below)
# 
# Definition: {'extensions': <collection_or_string>, 'loader': <class>}
# 
# Arguments received: 
#   * config_path: Path to config set in [extended_template]
#   * config: Config object received from Klipper
#
# Required Properties and Functions:
#   * loader.DefaultsLoaded <property>: <bool>
#       - If True, it is assumed the loader has loaded the defaults listed below. 
#       - If False, assumes the loader has not loaded the defaults listed below.
#       - It is suggested that the Loader should never process defaults unless:
#           * The user defines the defaults in the config file
#           * The loader defines it's own defaults
#           * Any other scenario where it's better to load the defaults by the loader instead of separately
#   * loader.GetFunctions(self) <function> = <dict> 
#       - Loads user-defined functions.
#           * Optionally, 
#       - Returns schema: {defined_function_name_for_jinja <str>: function <callable>}
# 
# 
LOADERS = [
    {
        'extensions': ['yaml','yml'],
        'func_loader': YamlLoader
    },
    {
        'extensions': ['default'],
        'func_loader': DefaultLoader
    }
]

