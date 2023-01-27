# Utilize Python Code in your GCode Macros as Jinja2 Filters
#
# Copyright (C) 2022  Michael Carroll <mc999984@gmail.com>
# Some of this code may have been used, sourced, or referenced from Klipper source code
#
# This file may be distributed under the terms of the GNU GPLv3 license.
#
#

import logging
import delayed_gcode

######################################################################
# Extended Delayed GCode macro
######################################################################
#
# Inherits DelayedGcode from delayed_gcode.py
# Only changes the template objects
class ExtendedDelayedGcode(delayed_gcode.DelayedGcode):
    def __init__(self, config):
        self.printer = config.get_printer()
        self.reactor = self.printer.get_reactor()
        self.name = config.get_name().split()[1]
        self.gcode = self.printer.lookup_object('gcode')
        gcode_macro = self.printer.load_object(config, 'extended_macro')
        self.timer_gcode = gcode_macro.load_template(config, 'gcode')
        self.duration = config.getfloat('initial_duration', 0., minval=0.)
        self.timer_handler = None
        self.inside_timer = self.repeat = False
        self.printer.register_event_handler("klippy:ready", self._handle_ready)
        self.gcode.register_mux_command(
            "UPDATE_DELAYED_GCODE", "ID", self.name,
            self.cmd_UPDATE_DELAYED_GCODE,
            desc=self.cmd_UPDATE_DELAYED_GCODE_help)

def load_config_prefix(config):
    return ExtendedDelayedGcode(config)