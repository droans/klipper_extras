# extended_macro
---
* Allow the use of custom Python functions in your Klipper macros by defining the functions in a YAML config file
* By default includes many additional modules and functions. See below for more information.
* Functions can accept parameters and return values to the macro.

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

1. In your Klipper config, add the following section:
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

`extended_macro` comes with many default functions which do not need to be added or declared by the user. These include:

*Types:*
```
list
dict
set
tuple
str
int
float
bool
type
```

*Built-ins:*
```
dir
getattr
setattr
locals
globals
math
itertools
```

*Additional:*
```
pandas
numpy
datetime
collections
```