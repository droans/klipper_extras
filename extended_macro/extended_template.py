# Necessary modules for configuration
import os, yaml, imp

# Additional defaults for G-Code
import math, pandas, numpy, datetime, itertools, collections

class Logger():
    def __init__(self, config):
        self.Error = config.error

# Wrapper to call the YAML config file loader
# Allowing users to define loaders so that other config setups can be created. 
# I'm not going to claim to be the smartest, so I don't want to keep others from creating better options
def YamlLoader(fpath, config):
    y = LoadYamlFunctions(fpath, config)

    return y.Functions

# Load YAML config to self.Functions so the template loader can be created
class LoadYamlFunctions():
    def __init__(self, yaml_path, config):
        self.path = yaml_path
        self.Functions = {}

        self.Log = Logger(config)

        with open(yaml_path, 'r') as f:
            self.yaml = yaml.load(f, Loader=yaml.Loader)
        
        func_yaml = self.yaml.get('functions',None)
        raise self.Log.Error(dir(config))
        
        self._import_function_dict(func_yaml)

    # Loops through each item in the config, passes
    # the data off to _import_function which will return
    # the actual function if it exists, and then adds
    # each function to the function dictionary so they can 
    # be added by extended_macro to the Jinja environment
    def _import_function_dict(self, funcs):
        for jinja_name, data in funcs.items():
            func = self._import_function(data['path'], data['function'])
            self.Functions[jinja_name] = func
        return

    # Loads each function 
    def _import_function(self, func_path, func_name):
        module = imp.load_source('script', func_path)

        if func_name not in dir(module):
            raise self.Log.Error('extended_template: Function %s not found in file %s' % (func_name, func_path))
        else:
            func = getattr(module, func_name)
            # print(func)
            return func

    def _import_defaults(self):
# Grabs the Klipper config for extended_template,
# uses the path variable to determine the extension,
# determines the proper loader for that extension,
# and returns the value from that loader which received
# the path and the Klipper config object.
class PythonFunction:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.Log = Logger(config)

        self.config_path = config.get('path')

        ext = self.config_path.split('.')[-1]

        for exts, loader in LOADERS.items():
            if ext in exts:
                self.functions = loader(self.config_path, config)
                break

        if self.functions is None:
            self.Log.Error('extended_template: Cannot get Python functions from path %s. Is the extension acceptable?' % self.config_path)
        elif not os.path.exists(self.config_path):
            self.Log.Error('extended_template: Cannot find file %s' % self.config_path)

def load_config(config):
    return PythonFunction(config)

# Define loaders as (extension <tuple>): loader <function>
# 
# Since different loaders might need or want different methods of parsing the file, 
# the script expects that the loader is a function, not a class. The function should
# process the config file and return a dictionary with the jinja function name as the key
# and the actual Python function as the value
# 
LOADERS = {
    ('yaml','yml'): YamlLoader
}