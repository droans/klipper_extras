# Klipper Extended Macro
---
* Allow the use of custom Python functions in your Klipper macros by defining the functions in a YAML config file
* By default includes many additional modules and functions. See below for more information.
* Functions can accept parameters and return values to the macro.
* Enables the `do` and `loopcontrols` Jinja2 extensions

### WARNING:

**Do not blindly download Python scripts, both for use in your macros and this script itself.** Read the script and ensure you understand what is going on. The scripts can be powerful and useful, but they can also be dangerous. If the script looks questionable, dangerous, or too confusing, it's better to assume that it is malicious.

---
## Installation:

This script utilizes Moonraker to ensure that files are placed in their proper locations, no matter the original install method.

1. On the server running Klipper, run the following commands:

```BASH
cd ~
git clone https://github.com/droans/klipper_extras.git
cd klipper_extras
python scripts/install.py
```

If necessary, the script will also install `requests` and `pathlib`. You will then need to rerun the script to continue.

2. Ensure that Moonraker is accessible at the default URL. If you believe it is correct, skip to step 6.

3. If the URL is incorrect, select `Settings`.

4. At the Settings menu, select `Change Moonraker URL`. Type in the correct URL for Moonraker and press enter. While you can also manually set the other options, please note that these **will** be overwritten once Moonraker is contacted. As such, you should instead allow Moonraker to update the values first and then override them manually.

5. Select `Go Back` to return to the Main Menu

6. Select `Load Config From Moonraker`. As Moonraker should be running on the same machine or at least the same network, this should take less than one second to complete. If there is a delay, either the URL you are using is wrong or Moonraker is not running.

7. If the config options listed are correct, select Install. At this point, all dependencies are installed to the Klippy Python environment and the modules will be soft-linked to the Klipper Extras Directory. 

8. If the modules already exist (eg, old install), you will be prompted on whether the old files should be kept, replaced, or if you want to cancel the installation. If the files are symlinked, you usually are fine keeping them. If not, you will need to replace them. 

```
${KLIPPY_ENV}/pip install -r ${HOME}/requirements.txt
```

---
## Setup:

1. In your Klipper config, add the following section.
```
# Config Header
# Enables extended_macro
[extended_template]

# The path to your extended_template config file.
# If you do not plan on creating your own Python scripts, this is not required.
# See example/function_config.yaml for the configuration schema. 
path: /home/pi/printer_data/functions/config.yaml    
```

---
**Adding your own Python functions**

*See the examples folder for more guidance.*

1. Create your Python script(s) with the function(s) you intend to use and add them to your Extended Template `config.yaml`. 
2. Reference them in your Klipper G-Code macro. They will be usable just like any other object.

---
**Automating Updates**

Add the section below to your `moonraker.conf`. 

```BASH
[update_manager extended_macro]
type: git_repo
primary_branch: add-python-install
path: ~/klipper_extras
origin: https://github.com/droans/klipper_extras.git
env: ~/klippy-env/bin/python
requirements: extended_macro/requirements.txt
is_system_service: False
managed_services: 
    klipper
```



---
## Usage:

This module will add all Python functions in your configuration to the Jinja globals namespace. As such, they will be accessible like any other available function or object. See the examples folder for more guidance.

When defining the macro, use `extended_macro` as the config name instead of `gcode_macro` (eg, use `[extended_macro MY_MACRO]` instead of `[gcode_macro MY_MACRO]`). 

---

## Defaults

`extended_macro` comes with many default functions which do not need to be added or declared by the user. 

*Custom Utility Functions*:

`update_gcode_variable(macro_name: str, variable: str, value: Any)`: Update a G-Code variable for any macro. Unlike `SET_GCODE_VARIABLE`, allows for non-literals to be passed and updated. 

`update_dict(dict: dict, keys: Union[list, tuple, set, str], value: Any)`: Update the value of a dictionary. Allows for a nested value to be updated if a list, tuple, or set is passed for `keys`.

`call_macro(self, macro_name: str, **params)`: Call any macro. As the G-Code interpreter is not used for this function, the params can be of any type.

---

#### Data Types:

* `list`
* `dict`
* `set`
* `tuple`
* `str`
* `int`
* `float`
* `bool`
* `type`
---

#### Python Built-ins:

* `dir`
* `getattr`
* `setattr`
* `locals`
* `globals`
* `math`
* `itertools`
---
#### Additional:
* `pandas`
* `numpy`
* `datetime`
* `collections`
