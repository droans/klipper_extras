#!/bin/bash

# Force script to exit if an error occurs
set -e

KLIPPER_PATH="${HOME}/klipper"
SYSTEMDDIR="/etc/systemd/system"
EXTENSION_LIST="extended_macro.py extended_template.py delayed_extended.py"

SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"

HOME_DIR="${HOME}"
ENV_DIR="${HOME_DIR}/klippy-env/bin"
EXTRAS_DIR="${HOME_DIR}/klipper/klippy/extras"
OLD_PRINTER_CONFIG_DIR="${HOME_DIR}/klipper_config"
PRINTER_CONFIG_DIR="${HOME_DIR}/printer_data/config"

KLIPPY_PIP="${ENV_DIR}/pip"
KLIPPY_PY="${ENV_DIR}/python"
KLIPPY_PY3="${ENV_DIR}/python3"

PROMPTED_INPUT="Yes"

function produce_newline() {
   echo " "
}

# Step 1: Ensure script is not running as superuser
function verify_ready() {
    if [ "$(id -u)" -eq 0 ]; then
        echo "This script must not run as root" >&2
        echo "exiting the script..." >&2
        exit -1
    fi
    check_klipper
}

function check_klipper() {
    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F "klipper.service")" ]; then
        echo "Klipper service found!"
    else
        echo "Klipper service not found, please install Klipper first" >&2
        echo "exiting the script..." >&2
        exit -1
    fi
    return
}

# Step 2:  Verify Klipper's virtual environment directory
function validate_env_dir() {
  if [ -d "$ENV_DIR" ]; then
    if [ -L "$ENV_DIR" ]; then
      # It is a symbolic links #
      echo "Klipper ENV folder is a symbolic link found so this is not a real directory, try again ..." >&2
      change_env_dir
    else
      # It is a directory #
      echo "Klipper ENV Directory exists ..."
      echo "ENV_DIR BASH variable being set to "$ENV_DIR"...." >&2
      KLIPPY_PIP="${ENV_DIR}/pip"
      KLIPPY_PY="${ENV_DIR}/python"
      KLIPPY_PY3="${ENV_DIR}/python3"
      return
    fi
  else
      echo "Klipper ENV Dirctory does not exists!" >&2
      change_env_dir
  fi
  return
}

function change_env_dir() {
    while [ true ]
    do
        read -p "New Klippy Python Environ Dir [${ENV_DIR}]: " PROMPTED_ENV_DIR
        if [ -z "$PROMPTED_ENV_DIR" ]; then
            PROMPTED_ENV_DIR=$ENV_DIR
            break
        else
            break
        fi
    done
    ENV_DIR=$PROMPTED_ENV_DIR
    validate_env_dir
    produce_newline
    return
}

# Step 3:  Verify Klipper's EXTRAS directory
function validate_extras_dir() {
  if [ -d "$EXTRAS_DIR" ]; then
    if [ -L "$EXTRAS_DIR" ]; then
      # It is a symbolic links #
      echo "Klipper Extra folder is a symbolic link found so this is not a real directory, try again ..." >&2
      change_extras_dir
    else
      # It is a directory #
      echo "Klipper Extras Directory exists ..."
      echo "EXTRAS_DIR BASH variable being set to "$EXTRAS_DIR"...." >&2
      return
    fi
  else
      echo "Klipper Extras Dirctory does not exists!" >&2
      change_extras_dir
  fi
  return
}

function change_extras_dir() {
    while [ true ]
    do
        read -p "New Klipper Extras Dir [${EXTRAS_DIR}]: " PROMPTED_EXTRAS_DIR
        if [ -z "$PROMPTED_EXTRAS_DIR" ]; then
            PROMPTED_EXTRAS_DIR=$EXTRAS_DIR
            break
        else
            break
        fi
    done
    EXTRAS_DIR=$PROMPTED_EXTRAS_DIR
    validate_extras_dir
    produce_newline
    return
}

# Step 4:  Verify Klipper's PRINTER CONFIG directory
function validate_printer_config_dir() {
  if [ -d "$PRINTER_CONFIG_DIR" ]; then
    if [ -L "$PRINTER_CONFIG_DIR" ]; then
      # It is a symbolic links #
      echo "Klipper Printer Config is a symbolic link found so this is not a real directory, try again ..." >&2
      PRINTER_CONFIG_DIR=$OLD_PRINTER_CONFIG_DIR
      change_printer_config_dir
    else
      # It is a directory #
      echo "Klipper Printer Config Directory exists ..."
      echo "PRINTER_CONFIG_DIR BASH variable being set to "$PRINTER_CONFIG_DIR"...." >&2
      return
    fi
  else
      echo "Klipper Printer Config Dirctory does not exists!..." >&2
      PRINTER_CONFIG_DIR=$OLD_PRINTER_CONFIG_DIR
      change_printer_config_dir
  fi
  return
}

function change_printer_config_dir() {
    while [ true ]
    do
        read -p "New Printer Config Dir [${PRINTER_CONFIG_DIR}]: " PROMPTED_PRINTER_CONFIG_DIR
        if [ -z "$PROMPTED_PRINTER_CONFIG_DIR" ]; then
            PROMPTED_PRINTER_CONFIG_DIR=$PRINTER_CONFIG_DIR
            break
        else
            break
        fi
    done
    PRINTER_CONFIG_DIR=$PROMPTED_PRINTER_CONFIG_DIR
    validate_printer_config_dir
    produce_newline
    return
}

# Step 5:  Deteremine Klipper's virtual enviroment python version
function check_env_version() {
    export PYTHON_VERSION=`$KLIPPY_PY -c 'import sys; print(".".join(map(str, sys.version_info[:1])))'`
    if  [ $? -eq 0 ]; then
        echo "Found Python version for virtual environment; Python version="$PYTHON_VERSION
    fi
}

# Step 6:  Verify PIP is installed in Klipper's virtual environment
function validate_pip_installed() {
    if ! [ -x "$(command -v ${KLIPPY_PIP})" ]; then
        echo 'Error: pip is not installed.' >&2
        change_pip
        if ! [ -x "$(command -v ${KLIPPY_PIP})" ]; then
            echo 'Error: pip is still not installed.' >&2
            echo 'Exiting the script, please install pip into the Klipper Environment, manually!' >&2
            echo "exiting the script..." >&2
            exit -1
        fi
    fi
    echo "pip is found to be installed into the Klipper Environment!"
}

function change_pip() {
    while [ true ]
    do
        read -p "New Klippy Environment Pip Location [${KLIPPY_PIP}]: " PROMPTED_KLIPPY_PIP
        if [ -z "$PROMPTED_KLIPPY_PIP" ]; then
            PROMPTED_KLIPPY_PIP="${KLIPPY_PIP//pip}"
            break
        else
            break
        fi
    done
    KLIPPY_PIP=$PROMPTED_KLIPPY_PIP'/pip'
    echo "KLIPPY_PIP BASH variable being set to "$KLIPPY_PIP"...." >&2
    produce_newline
    return
}

# Step 7:  Verify the appropriate version of python is installed in Klipper's virtual environment
function validate_python_installed() {
    if  [[ $PYTHON_VERSION == 2 ]]; then
        if ! [ -x "$(command -v ${KLIPPY_PY})" ]; then
            echo 'Error: python is not installed.' >&2
            change_py
            if ! [ -x "$(command -v ${KLIPPY_PY})" ]; then
                echo 'Error: python is still not installed.' >&2
                echo 'Exiting the script, please install python into the Klipper Environment, manually!' >&2
                echo "exiting the script..." >&2
                exit -1
            fi
        fi
        echo "python is found to be installed into the Klipper Environment!"
    elif [[ $PYTHON_VERSION == 3 ]]; then
        validate_python3_installed
    fi
}

function change_py() {
    while [ true ]
    do
        read -p "New Klippy Environment Python Location [${KLIPPY_PY}]: " PROMPTED_KLIPPY_PY
        if [ -z "$PROMPTED_KLIPPY_PY" ]; then
            PROMPTED_KLIPPY_PY="${KLIPPY_PY//python}"
            break
        else
            break
        fi
    done
    KLIPPY_PY=$PROMPTED_KLIPPY_PY'/python'
    echo "KLIPPY_PY BASH variable being set to "$KLIPPY_PY"...." >&2
    produce_newline
    return
}

function validate_python3_installed() {
    if ! [ -x "$(command -v ${KLIPPY_PY3})" ]; then
         echo 'Error: python3 is not installed.' >&2
        change_py3
        if ! [ -x "$(command -v ${KLIPPY_PY3})" ]; then
            echo 'Error: python3 is still not installed.' >&2
            echo 'Exiting the script, please install python3 into the Klipper Environment, manually!' >&2
            echo "exiting the script..." >&2
            exit -1
        fi
    fi
    echo "python3 is found to be installed into the Klipper Environment!"
    return
}

function change_py3() {
    while [ true ]
    do
        read -p "New Klippy Environment Python3 Location [${KLIPPY_PY3}]: " PROMPTED_KLIPPY_PY3
        if [ -z "$PROMPTED_KLIPPY_PY3" ]; then
            PROMPTED_KLIPPY_PY3="${KLIPPY_PY3//python3}"
            break
        else
            break
        fi
    done
    KLIPPY_PY3=$PROMPTED_KLIPPY_PY3'/python3'
    echo "KLIPPY_PY3 BASH variable being set to "$KLIPPY_PY3"...." >&2
    produce_newline
    return
}

# Step 8: Check if the extensions are already present.
# This is a way to check if this is the initial installation.
function check_existing() {
    local -i existing=0
    for extension in ${EXTENSION_LIST}; do
        [ -e "${KLIPPER_PATH}/klippy/extras/${extension}" ] && existing=1 || existing=0
        [ ${existing} -eq 0 ] && break
    done
    echo ${existing}
}

# Step 9: optionaly install requirement.txt
function install_requirements() {
    echo "CREATING requirements.txt file for the python"$PYTHON_VERSION" Klipper virtual environment....."
    create_requirements_file
    echo "INSTALLING ADDITIONAL SOFTWARE PACKAGES...."
    echo "NOTE: if this is the first time installing these packages, please be patient, It could take up to 10 minutes"
    #SRCDIR=/home/pi/klipper_extras
    echo "Attempting the python install of requirements.txt file......"
    $KLIPPY_PIP install -r $SRCDIR/extended_macro/requirements.txt
    if  [ $? -eq 0 ]; then
        produce_newline
        echo "All required Software packages have been sucessfully installed!"
        prompt_user_update
    else
        echo "An error occurred when installing the required Software Packages!" >&2
        echo "Please run the following command, manually:" >&2
        echo "run this command:" '"'$KLIPPY_PIP' install -r' $SRCDIR'/extended_macro/requirements.txt' '"' >&2
        echo "exiting the script..." >&2
        exit -1
    fi
}

function create_requirements_file() {
    if  [[ $PYTHON_VERSION == 2 ]]; then
            touch ${SRCDIR}/extended_macro/requirements.txt
            echo "pyyaml==3.13" >> ${SRCDIR}/extended_macro/requirements.txt
            echo "numpy==1.16.6" >> ${SRCDIR}/extended_macro/requirements.txt
            echo "flatten-dict==0.4.2" >> ${SRCDIR}/extended_macro/requirements.txt
            echo "pandas==0.23.4" >> ${SRCDIR}/extended_macro/requirements.txt
    elif [[ $PYTHON_VERSION == 3 ]]; then
            touch ${SRCDIR}/extended_macro/requirements.txt
            echo "pyyaml==5.3.1" >> ${SRCDIR}/extended_macro/requirements.txt
            echo "numpy==1.24.1" >> ${SRCDIR}/extended_macro/requirements.txt
            echo "flatten-dict==0.4.2" >> ${SRCDIR}/extended_macro/requirements.txt
            echo "pandas==1.5.3" >> ${SRCDIR}/extended_macro/requirements.txt
    else
        echo "The Python Version of '"$PYTHON_VERSION"' does not exists for the Klipper firmware, exiting the script" >&2
        exit -1
    fi
    return
}

function prompt_user_update() {
    produce_newline
    while [ true ]
    do
        read -p "Do you plan on using moonraker's update manager to automatically update this extension: [${PROMPTED_INPUT}]: " PROMPT_INPUT
        if [ -z "$PROMPT_INPUT" ]; then
            PROMPT_INPUT=$PROMPTED_INPUT
            break
        else
            break
        fi
    done
    PROMPTED_INPUT=$PROMPT_INPUT
    echo "PROMPTED_INPUT BASH variable being set to "$PROMPTED_INPUT"...." >&2
    validate_user_response
    return
}

function validate_user_response() {
    while true; do
        case $PROMPTED_INPUT in
	        yes )   echo ok, we will proceed;
                    copy_moonraker_update_file;
		            break;;
            Yes )   echo ok, we will proceed;
                    copy_moonraker_update_file;
                    break;;
	        y )     echo ok, we will proceed;
                    copy_moonraker_update_file;
		            break;;
            Y )     echo ok, we will proceed;
                    copy_moonraker_update_file;
                    break;;
	        no )    echo ok, we will not proceed;
		            break;;
	        No )    echo ok, we will not proceed;
		            break;;
	        n )     echo ok, we will not proceed;
		            break;;
	        N )     echo ok, we will not proceed;
		            break;;
	        * )     echo invalid response;;
        esac
    done
    return
}

function copy_moonraker_update_file() {
    produce_newline
    produce_newline
    echo "CREATING extended_template_update.conf file for Moonraker's [update manager]....."
    create_moonraker_file
    echo "Trying to add include statement to the end of moonraker.conf file"
    echo "    " >> ${PRINTER_CONFIG_DIR}/moonraker.conf
    echo "#add extended_template extension to Klipper    " >> ${PRINTER_CONFIG_DIR}/moonraker.conf
    echo "[include extended_template_update.conf]" >> ${PRINTER_CONFIG_DIR}/moonraker.conf
    if [ $? -eq 0 ]; then
        echo "Sucessfully appended [include extended_template_update.conf] to the end of "${PRINTER_CONFIG_DIR}"/moonraker.conf file!"
    else
        echo "An error occurred when trying to append [include extended_template_update.conf] to the "${PRINTER_CONFIG_DIR}"/moonraker.conf file!" >&2
        echo "Please run the following command, manually:" >&2
        echo "run this command:" '"'`echo `"[include extended_template_update.conf]"` >> moonraker.conf`'"' >&2
        echo "exiting the script..." >&2
        exit -1
    fi
    # copy the include file over to ${PRINTER_CONFIG_DIR}
    #SRCDIR=/home/pi/klipper_extras
    echo "Trying...cp "${SRCDIR}"/extended_macro/extended_template_update.conf "${PRINTER_CONFIG_DIR}"/extended_template_update.conf"
    cp ${SRCDIR}'/extended_macro/extended_template_update.conf' ${PRINTER_CONFIG_DIR}'/extended_template_update.conf'
    if [ $? -eq 0 ]; then
        echo "Sucessfully copied extended_template_update.conf to "${PRINTER_CONFIG_DIR}"!"
    else
        echo "An error occurred when trying to copy extended_template_update.conf to "${PRINTER_CONFIG_DIR}"!">&2
        echo "Please run the following command, manually:" >&2
        echo "run this command:" '"'`cp `${SRCDIR}'/extended_macro/extended_template_update.conf' ${PRINTER_CONFIG_DIR}'/extended_template_update.conf''"' >&2
        echo "exiting the script..." >&2
        exit -1
    fi
    return
}

function create_moonraker_file() {
    touch ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "[update_manager extended_template]" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "type: git_repo" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "primary_branch: main" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "path: ~/klipper_extras" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "origin: https://github.com/droans/klipper_extras.git" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "env: ~/klippy-env/bin/python" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "requirements: extended_macro/requirements.txt" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "install_script: install.sh" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "is_system_service: False" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    echo "managed_services: klipper" >> ${SRCDIR}/extended_macro/extended_template_update.conf
    return
}

# Step 10: Link extension to Klipper
function link_extension() {
    echo "Linking extensions to Klipper..."
    for extension in ${EXTENSION_LIST}; do
        ln -sf "${SRCDIR}/extended_macro/${extension}" "${EXTRAS_DIR}/${extension}"
    done
}

# Step 11: optionally restarting Klipper
function restart_klipper()
{
    echo "Restarting Klipper..."
    sudo systemctl restart klipper
}

while getopts "k:" arg; do
    case ${arg} in
        k) KLIPPER_PATH=${OPTARG} ;;
    esac
done


verify_ready
validate_env_dir
validate_extras_dir
validate_printer_config_dir
check_env_version
validate_pip_installed
validate_python_installed
existing_install=$(check_existing)
if [ ${existing_install} -eq 0 ]; then
    install_requirements
fi
link_extension
if [ ${existing_install} -eq 0 ]; then
    restart_klipper
fi
