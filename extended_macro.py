# Utilize Python Code in your GCode Macros
#
#  Usage:
#   * Currently requires a hard-coded PATH below for Python files.
#   * Create one or more functions inside the file. As these are added to Jinja globals, any working Python function is accepted
#   * Each file must contain a list at the top named FUNCTIONS.
#   * Example:
# 
#       --------
#       test.py:
#       --------
#        
#       FUNCTIONS = [
#           {
#               'name': 'repeater',
#               'function': 'repeat_back'
#           }
#       ]
#
#       def repeat_back(text):
#           return rept + ' ' + rept
#    
#
#       -----------------
#       repeat_macro.cfg:
#       -----------------
#        
#       [extended_macro REPEATER]
#       gcode:
#           {% set message = params.MESSAGE %}
#           {% set result = repeater(message) %}
#           M118 {result}
#
#
# Copyright (C) 2022  Michael Carroll <mc999984@gmail.com>
# Some of this code may have been used, sourced, or referenced from Klipper source code
#
# This file may be distributed under the terms of the GNU GPLv3 license.

import traceback, logging, ast, copy
import jinja2
import imp
import os, sys
from .gcode_macro import (
    GetStatusWrapper,
    TemplateWrapper,
    PrinterGCodeMacro,
    GCodeMacro
)

PATH = '/home/pi/klipper_config/funcs'


######################################################################
# Extended Template handling
######################################################################

# Wrapper around a Jinja2 template
# Inherits TemplateWrapper from gcode_macro.py
# Only Change is the template context to utilize extended_macro

class ExtendedTemplateWrapper(TemplateWrapper):
    def __init__(self, printer, env, name, script):
        self.printer = printer
        self.name = name
        self.gcode = self.printer.lookup_object('gcode')
        gcode_macro = self.printer.lookup_object('extended_macro')
        self.create_template_context = gcode_macro.create_template_context
        try:
            self.template = env.from_string(script)
        except Exception as e:
            msg = "Error loading template '%s': %s" % (
                 name, traceback.format_exception_only(type(e), e)[-1])
            logging.exception(msg)
            raise printer.config_error(msg)

# Inherits PrinterGCodeMacro from gcode_macro.py
# Code added to utilize 
class ExtendedPrinterGCodeMacro(PrinterGCodeMacro, object):     #object required due to the Python 2 requirement for using super()
    def __init__(self, config):
        super(ExtendedPrinterGCodeMacro, self).__init__(config)

        self._functions = []
        self._add_gcode_functions()

    def _load_funcs_to_environment(self):
        funcs = self._functions

        for func in funcs:
            jinja_func = {func['func_name']:func['function']}
            self.env.globals.update(**jinja_func)
        return 
    
    def _import_function(self, module, function_data):
        if type(function_data) is not dict:
            self.logger.exception('Function data %s should be dict with keys "name" and "function".' %(function_data))
            return

        f = {}
        f['function'] = getattr(module, function_data['function'])
        f['func_name'] = function_data['name']

        if f not in self._functions:
            self._functions.append(f)


    def _import_functions(self, module):
        functions = module.FUNCTIONS

        if type(functions) is not list:
            self.logger.exception('FUNCTION Module %s should be list. Received %s' %(module, functions))
            return

        for function in functions:
            self._import_function(module, function)

    def _import_single_script(self, script_path):
        module = imp.load_source('script', script_path)

        if 'FUNCTIONS' not in dir(module):
            self.logger.exception('Script %s missing FUNCTION identifier' %(script_path.split('/')[-1]))
        else:
            self._import_functions(module)

    def _import_all_scripts(self, scripts):
        for script in scripts:
            self._import_single_script(script)

    def _find_python_files(self, path):
        scripts = []

        if path[-1] != '/':
            path = path + '/'

        for item in os.listdir(path):
            if item[-3:] == '.py':
                scripts.append(path + item)
        
        return scripts

    def _add_gcode_functions(self):
        path = PATH

        scripts = self._find_python_files(path)
        self._import_all_scripts(scripts)
        self._load_funcs_to_environment()


def load_config(config):
    return ExtendedPrinterGCodeMacro(config)


######################################################################
# Extended GCode macro
######################################################################

# Inherits GCodeMacro from gcode_macro.py
# Only changes the template objects

class ExtendedGCodeMacro(GCodeMacro):
    def __init__(self, config):
        if len(config.get_name().split()) > 2:
            raise config.error(
                    "Name of section '%s' contains illegal whitespace"
                    % (config.get_name()))
        name = config.get_name().split()[1]
        self.alias = name.upper()
        self.printer = printer = config.get_printer()
        gcode_macro = printer.load_object(config, 'extended_macro')
        self.template = gcode_macro.load_template(config, 'gcode')
        self.gcode = printer.lookup_object('gcode')
        self.rename_existing = config.get("rename_existing", None)
        self.cmd_desc = config.get("description", "G-Code macro")
        if self.rename_existing is not None:
            if (self.gcode.is_traditional_gcode(self.alias)
                != self.gcode.is_traditional_gcode(self.rename_existing)):
                raise config.error(
                    "G-Code macro rename of different types ('%s' vs '%s')"
                    % (self.alias, self.rename_existing))
            printer.register_event_handler("klippy:connect",
                                           self.handle_connect)
        else:
            self.gcode.register_command(self.alias, self.cmd,
                                        desc=self.cmd_desc)
        self.gcode.register_mux_command("SET_GCODE_VARIABLE", "MACRO",
                                        name, self.cmd_SET_GCODE_VARIABLE,
                                        desc=self.cmd_SET_GCODE_VARIABLE_help)
        self.in_script = False
        self.variables = {}
        prefix = 'variable_'
        for option in config.get_prefix_options(prefix):
            try:
                self.variables[option[len(prefix):]] = ast.literal_eval(
                    config.get(option))
            except ValueError as e:
                raise config.error(
                    "Option '%s' in section '%s' is not a valid literal" % (
                        option, config.get_name()))


def load_config_prefix(config):
    return ExtendedGCodeMacro(config)
