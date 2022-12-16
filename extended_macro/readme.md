# extended_macro
---
* Allow the use of custom Python functions in your Klipper macros by defining the functions in a YAML config file
* Functions can accept parameters and return values to the macro.

### WARNING:

**Do not blindly download Python scripts, both for use in your macros and this script itself.** Read the script and ensure you understand what is going on. The scripts can be powerful and useful, but they can also be dangerous. If the script looks questionable, dangerous, or too confusing, it's better to assume that it is malicious.

**Installation:**
1. Clone this repository or download both `extended_macro.py` and `extended_template.py`
2. Locate where the `klippy-env` directory is on your Klipper instance.
3. Run the following command, substituting `~/klippy-env/` with the location found above:

`~/klippy-env/bin/python -m pip install pyyaml==3.1.4`

4. Finally, move `extended_macro.py` and `extended_template.py` to your Klippy Extras file. This usually is located at `~/klipper/klippy/extras`.

---
**Setup:**

See the examples folder for more guidance.
1. Create your Python script(s) with the function(s) you intend to use.
2. Create a function configuration file using `example/function_config.yaml` as reference. YAML is the allowed schema. The extension must be `yml` or `yaml`
3. In your Klipper config, add the `[extended_template]` section to define the location of your function config file.

---
**Usage:**

See the examples folder for more guidance.

When defining the macro, use `extended_macro` as the config name instead of `gcode_macro`. To use your function, you will wrap the name with curly brackets (`{gcode_function_name_goes_here}`). 