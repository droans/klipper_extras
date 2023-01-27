#!/bin/bash

FLAG=1

# Force script to exit if an error occurs
set -e

KLIPPER_PATH="${HOME}/klipper"
SYSTEMDDIR="/etc/systemd/system"
EXTENSION_LIST="extended_macro.py extended_template.py"
SRCDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )"/ && pwd )"

HOME_DIR="${HOME}"
ENV_DIR="${HOME_DIR}/klippy-env/bin"
EXTRAS_DIR="${HOME_DIR}/klipper/klippy/extras"

KLIPPY_PIP="${ENV_DIR}/pip"
KLIPPY_PY="${ENV_DIR}/python"

function produce_newline() {
   echo " "
}


# Step 1:  Verify directories exist and pip and python are installed in ENV_DIR


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
      return
    fi
  else
      echo "Klipper ENV Dirctory does not exists!" >&2
      change_env_dir
  fi
  return
}

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

function change_env_dir() {
    while [ true ]
    do
        read -p "New Klippy Python Environ Dir [${ENV_DIR}]: " PROMPTED_ENV_DIR
        if [ -z "$PROMPTED_ENV_DIR" ]; then
           continue
        else
            break
        fi
    done
    ENV_DIR=$PROMPTED_ENV_DIR
    validate_env_dir
    produce_newline
    return
}

function change_extras_dir() {
    while [ true ]
    do
        read -p "New Klipper Extras Dir [${EXTRAS_DIR}]: " PROMPTED_EXTRAS_DIR
        if [ -z "$PROMPTED_EXTRAS_DIR" ]; then
            continue
        else
            break
        fi
    done
    EXTRAS_DIR=$PROMPTED_EXTRAS_DIR
    validate_extras_dir
    produce_newline
    return
}

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

function validate_python_installed() {
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
}

function change_pip() {
    while [[ $string != 'string' ]] || [[ $string == '' ]]
    do
       read -p "New Klippy Environment Pip Location [${KLIPPY_PIP}]: " string
       echo "Enter a valid string" >&2
    done
    PROMPTED_KLIPPY_PIP=$string
    KLIPPY_PIP=$PROMPTED_KLIPPY_PIP'/pip'
    echo "KLIPPY_PIP BASH variable being set to "$KLIPPY_PIP"...." >&2
    produce_newline
    return
}

function change_py() {
    while [[ $string != 'string' ]] || [[ $string == '' ]]
    do
       read -p "New Klippy Environment Python Location [${KLIPPY_PY}]: " string
       echo "Enter a valid string" >&2
    done
    PROMPTED_KLIPPY_PY=$string
    KLIPPY_PY=$PROMPTED_KLIPPY_PY'/python'
    echo "KLIPPY_PY BASH variable being set to "$KLIPPY_PY"...." >&2
    produce_newline
    return
}

# Step 2: install requirement.txt
function install_requirements() {
    if [[ "$FLAG" == 1 ]]; then
        echo "INSTALLING ADDITIONAL SOFTWARE PACKAGES...."
        echo "NOTE: if this is the first time installing these packages, please be patient, It could take up to 10 minutes"
        #SRCDIR=/home/pi/klipper_extras
        cp ${SRCDIR}'/extended_macro/requirements.txt' ${HOME}'/requirements.txt'
        if [ $? -eq 0 ]; then
            echo "copied requirements.txt to "${HOME}" sucessfully."
            echo "Attempting the pip install of requirements.txt file......"
            $KLIPPY_PIP install -r $HOME/requirements.txt
            if  [ $? -eq 0 ]; then
               produce_newline
               echo "All required Software packages have been sucessfully installed!"
            else
               echo "An error occurred when installing the required Software Packages!">&2
               echo "Please run the following command, manually:" >&2
               echo "run this command:" '"'$KLIPPY_PIP' install -r' ${HOME}'/requirements.txt' '"' >&2
               echo "exiting the script..." >&2
               exit -1
            fi
        else
            echo "The copy of requirements.txt to "${HOME}" did not work, exiting the script" >&2
            exit -1
        fi
    fi
    echo "Reminder: Edit the script file and set FLAG=0 at the top of the script file" >&2
    echo "Installing Additional Software Packages only needs to be done ONE time" >&2
    if [[ "$FLAG" == 0 ]]; then
       echo "If the FLAG=0 setting is due to the fact that the additional software has already been installed,">&2
       echo "please ignore the above three messages.">&2
    fi
}

# Step 3:  Verify Klipper has been installed
function check_klipper() {
    if [ "$(sudo systemctl list-units --full -all -t service --no-legend | grep -F "klipper.service")" ]; then
        echo "Klipper service found!"
    else
        echo "Klipper service not found, please install Klipper first" >&2
        echo "exiting the script..." >&2
        exit -1
    fi
}

# Step 4: Link extension to Klipper
function link_extension() {
    echo "Linking extensions to Klipper..."
    for extension in ${EXTENSION_LIST}; do
        ln -sf "${SRCDIR}/extended_macro/${extension}" "${EXTRAS_DIR}/${extension}"
    done
}

# Step 5: restarting Klipper
function restart_klipper()
{
    echo "Restarting Klipper..."
    sudo systemctl restart klipper
}

function verify_ready() {
    if [ "$(id -u)" -eq 0 ]; then
        echo "This script must not run as root" >&2
        echo "exiting the script..." >&2
        exit -1
    fi
    check_klipper
}

while getopts "k:" arg; do
    case ${arg} in
        k) KLIPPER_PATH=${OPTARG} ;;
    esac
done

validate_env_dir
validate_extras_dir
validate_pip_installed
validate_python_installed
install_requirements
verify_ready
link_extension
restart_klipper
