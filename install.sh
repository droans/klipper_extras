#!/bin/bash
HOME_DIR="${HOME}"
ENV_DIR="${HOME_DIR}/klippy-env/bin"
EXTRAS_DIR="${HOME_DIR}/klipper/klippy/extras"

KLIPPY_PIP="${ENV_DIR}/pip"
KLIPPY_PY="${ENV_DIR}/python"

validate_env_dir() {
    return
}

validate_extras_dir() {
    return

}

change_env_dir() {
    read -p "New Klippy Python Environ Dir [${ENV_DIR}]: " PROMPTED_ENV_DIR
}

change_extras_dir() {
    read -p "New Klipper Extras Dir [${EXTRAS_DIR}]: " PROMPTED_EXTRAS_DIR

}

change_pip() {
    read -p "New Klippy Environment Pip Location [${KLIPPY_PIP}]: " PROMPTED_KLIPPY_PIP

}

change_py() {
    read -p "New Klippy Environment Python Location [${KLIPPY_PY}]: " PROMPTED_KLIPPY_PY

}

main_menu() {
    return

}

settings_menu() {
    return

}

help() {
    return
    
}

echo "Install Script is not ready to utilize. Please use the readme and manually install instead"