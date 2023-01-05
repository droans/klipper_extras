# Utilize Python Code in your GCode Macros
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
class ExtendedPrinterGCodeMacro(PrinterGCodeMacro, object):     #Dummy `object` required due to the Python 2 requirement for using super()
    def __init__(self, config):
        super(ExtendedPrinterGCodeMacro, self).__init__(config)

        config = self.printer.load_object(config, 'extended_template')

        for name, func in config.Functions.items():
            jinja_func = {name:func}
            self.env.globals.update(**jinja_func)

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