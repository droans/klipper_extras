import os, yaml, imp, math

def YamlLoader(fpath, config):
    y = LoadYamlFunctions(fpath, config)

    return y.Functions

class LoadYamlFunctions():
    def __init__(self, yaml_path, config):
        self.path = yaml_path
        self.Functions = {}

        self.logger = config.get_printer().config_error

        with open(yaml_path, 'r') as f:
            self.yaml = yaml.load(f, Loader=yaml.Loader)
        
        func_yaml = self.yaml.get('functions',None)
        
        for jinja_name, data in func_yaml.items():
            func = self._import_function(data['path'], data['function'])
            self.Functions[jinja_name] = func

        # self.printer.add_object('extended_config',self)

    def _import_function(self, func_path, func_name):
        module = imp.load_source('script', func_path)

        if func_name not in dir(module):
            self.logger('extended_template: Function %s not found in file %s' % (func_name, func_path))
        else:
            func = getattr(module, func_name)
            # print(func)
            return func

    def _import_defaults(self):
        defaults = {
            'math': math
        }
        

class PythonFunction:
    def __init__(self, config):
        self.printer = config.get_printer()
        self.gcode = self.printer.lookup_object('gcode')
        self.logger = self.printer.config_error

        self.config_path = config.get('path')

        ext = self.config_path.split('.')[-1]

        for exts, loader in LOADERS.items():
            if ext in exts:
                self.functions = loader(self.config_path, config)
                break

        if self.functions is None:
            self.logger.exception('extended_template: Cannot get Python functions from path %s. Is the extension acceptable?' % self.config_path)
        elif not os.path.exists(self.config_path):
            self.logger.exception('extended_template: Cannot find file %s' % self.config_path)

def load_config(config):
    return PythonFunction(config)

LOADERS = {
    ('yaml','yml'): YamlLoader
}