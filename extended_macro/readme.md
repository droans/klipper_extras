# Extended_Template
---
* Allow the use of custom Python functions in your Klipper macros by defining the functions in a YAML config file
* By default includes many additional modules and functions. See below for more information.
* Functions can accept parameters and return values to the macro.
* Enables the `do` and `loopcontrols` Jinja2 extensions

### WARNING:

**Do not blindly download Python scripts, both for use in your macros and this script itself.** Read the script and ensure you understand what is going on. The scripts can be powerful and useful, but they can also be dangerous. If the script looks questionable, dangerous, or too confusing, it's better to assume that it is malicious.

**What will happen when you run the Installation script:**
1. The script will determine if the following directories exist:
    * Klipper Extras: Usually located at `/home/USER/klipper/klippy/extras`.
    * Klippy Virtual Environment `bin` directory: Usually located at `/home/USER/klippy/bin`
2. It will clone this repository; the following files will be downloaded:
             `extended_macro.py`, `extended_template.py`, and `delayed_extended.py`
3. The script will install additional software if this extension has not been installed before
4. The script creates a symbolic link from the clone Repo to the Klipper Extras folder for the following files:
            `extended_macro.py`, `extended_template.py` and `delayed_extended.py`
5. If Klipper needs to be restarted the script will cause a Klipper restart.

---
**Setup:**

1. In your Klipper config, add the following section. Nothing more is needed if you do not plan on using your own Python scripts:
```INI
[extended_template]
```
---
**Adding your own Python functions**

*See the examples folder for more guidance.*

1. Create your Python script(s) with the function(s) you intend to use.
2. Create a function configuration file using `example/function_config.yaml` as reference. YAML is the allowed schema. The extension must be `yml` or `yaml`
3. In the `[extended_template]` section of your Klipper config, add the variable `path` with the value being the location of where you saved the config YAML file.

---
**Usage:**

See the examples' folder for more guidance.

When defining the macro, use `extended_macro` as the config name instead of `gcode_macro`. To use your function, you will wrap the name with curly brackets (`{gcode_function_name_goes_here}`).

When you need the macro to be used on an timer instead of `extended_macro` use `delayed_extended` as the section definition.

---
**Defaults**

`extended_macro` and `delayed_extended` comes with many default functions which do not need to be added or declared by the user.

---

## Installation Instructions

Download the files onto your Klipper host machine using the following command:
On your Run the following commands in the command prompt of the Raspberry Pi running Klipper for your 3D printer:

```BASH
cd ~
git clone https://github.com/droans/klipper_extras.git
cd ~/klipper_extras
git checkout shell-install
```

Next, install Extended Template using our installation script. As with any script, please take time and read the script first, so you can ensure the safety. Alternatively, if you understand how, you may download the files and manually install Extended Macro:

```BASH
cd ~
./klipper_extras/install.sh
```

At this point, Extended Macro is ready to be used. If you wish to add this to your update manager, edit your `moonraker.conf` file and add the following:

```INI
[update_manager extended_template]
type: git_repo
primary_branch: shell-install
path: ~/klipper_extras
origin: https://github.com/droans/klipper_extras.git
env: ~/klippy-env/bin/python
requirements: extended_macro/requirements.txt
install_script: install.sh
is_system_service: False
managed_services: klipper
```

The script will automatically generate the `requirements.txt` file and (if the use chooses to have moonraker update this extension automatically) `extended_template_update.conf` file.

If the user chooses to have moonraker update this extension automatically, then the script will append the following to the end of your `moonraker.conf` file:

```INI
#add extended_template extension to Klipper
[include extended_template_update.conf]
```
---

*Custom Utility Functions*:

`update_gcode_variable(macro_name: str, variable: str, value: Any)`: Update a G-Code variable for any macro. Unlike `SET_GCODE_VARIABLE`, allows for non-literals to be passed and updated.

`update_dict(dict: dict, keys: Union[list, tuple, set, str], value: Any)`: Update the value of a dictionary. Allows for a nested value to be updated if a list, tuple, or set is passed for `keys`.

`call_macro(self, macro_name: str, **params)`: Call any macro. As the G-Code interpreter is not used for this function, the params can be of any type.

---

*Data Types:*

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

*Python Built-ins:*

* `dir`
* `getattr`
* `setattr`
* `locals`
* `globals`
* `math`
* `itertools`
---
*Additional:*
* `pandas`
* `numpy`
* `datetime`
* `collections`
