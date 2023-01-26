# extended_macro
---
* Allow the use of custom Python functions in your Klipper macros by defining the functions in a YAML config file
* By default includes many additional modules and functions. See below for more information.
* Functions can accept parameters and return values to the macro.
* Enables the `do` and `loopcontrols` Jinja2 extensions

### WARNING:

**Do not blindly download Python scripts, both for use in your macros and this script itself.** Read the script and ensure you understand what is going on. The scripts can be powerful and useful, but they can also be dangerous. If the script looks questionable, dangerous, or too confusing, it's better to assume that it is malicious.

**Installation:**
1. Write down the location of the following directories:
    * Klipper Extras: Usually located at `/home/USER/klipper/klippy/extras`.
    * Klippy Virtual Environment `bin` directory: Usually located at `/home/USER/klippy/bin`
2. Clone this repository or download `extended_macro.py`, `extended_template.py`, and `requirements.txt`
3. Move `extended_macro.py` and `extended_template.py` to your Klipper Extras folder. 
4. Move `requirements.txt` to your home directory.
5. Run the following command, substituting `${KLIPPY_ENV}` with the Klippy Virtual Environment bin directory:

```
${KLIPPY_ENV}/pip install -r ${HOME}/requirements.txt
```

---
**Setup:**

1. In your Klipper config, add the following section. Nothing more is needed if you do not plan on using your own Python scripts:
```
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

See the examples folder for more guidance.

When defining the macro, use `extended_macro` as the config name instead of `gcode_macro`. To use your function, you will wrap the name with curly brackets (`{gcode_function_name_goes_here}`). 

---
**Defaults**

`extended_macro` comes with many default functions which do not need to be added or declared by the user. 

---

## Installation Instructions

Do the following commands at the command prompt of the Raspberry Pi running Klipper for your 3D printer:

```BASH
cd ~
```

```BASH
git clone https://github.com/droans/klipper_extras.git
```

```BASH
./klipper_extras/install.sh
```

When the script finishes, do the following:

copy the script file to your home directory (i.e. /home/pi):

```BASH
cp /home/pi/klipper_extras/install.sh /home/pi/extended_macro_install.sh

```

edit the script and change the `FLAG=1` to a `FLAG=0` on the third line of the script file:

```BASH
nano /home/pi/extended_macro_install.sh
```

The reason for copying the file to your home directory is Moonraker will not like it if you edit the file while it is in the clone repo directory and will force you to overwrite the changes.

Now, set up the moonraker section of your printer, so it can keep this extension updated for you automatically:

Edit your `moonraker.conf` file and add the following:

```BASH
[update_manager extended_macro]
type: git_repo
primary_branch: main
path: ~/klipper_extras
origin: https://github.com/droans/klipper_extras.git
env: ~/klippy-env/bin/python
requirements: extended_macro/requirements.txt
install_script: ./../extended_macro_install.sh
is_system_service: False
managed_services: klipper
```

With this above setup pointing the installation script to your home directory, anytime the extended_macro extension gets updated, your extended_macro_install.sh file will not be overwritten by the GitHub clone of the repo.

We want the `FLAG=0` to stay that way.  You only need to install the additional software packages one time. Moonraker will take care of ensuring that the packages needed by the extension are updated (the `requirements` option takes care of that for you).

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
