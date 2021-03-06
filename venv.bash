#!/bin/bash

# Script for setting up the development environment.

SRC_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
VENV_DIR=${SRC_DIR}/.venv

##############################################################################
# Colours
##############################################################################

BOLD="\e[1m"

CYAN="\e[36m"
GREEN="\e[32m"
RED="\e[31m"
YELLOW="\e[33m"

RESET="\e[0m"

padded_message ()
{
  line="........................................"
  printf "%s %s${2}\n" ${1} "${line:${#1}}"
}

pretty_header ()
{
  echo -e "${BOLD}${1}${RESET}"
}

pretty_print ()
{
  echo -e "${GREEN}${1}${RESET}"
}

pretty_warning ()
{
  echo -e "${YELLOW}${1}${RESET}"
}

pretty_error ()
{
  echo -e "${RED}${1}${RESET}"
}

##############################################################################
# Methods
##############################################################################

install_package ()
{
  PACKAGE_NAME=$1
  dpkg -s ${PACKAGE_NAME} > /dev/null
  if [ $? -ne 0 ]; then
    sudo apt-get -q -y install ${PACKAGE_NAME} > /dev/null
  else
    pretty_print "  $(padded_message ${PACKAGE_NAME} "found")"
    return 0
  fi
  if [ $? -ne 0 ]; then
    pretty_error "  $(padded_message ${PACKAGE_NAME} "failed")"
    return 1
  fi
  pretty_warning "  $(padded_message ${PACKAGE_NAME} "installed")"
  return 0
}

##############################################################################

#############################
# Checks
#############################

[[ "${BASH_SOURCE[0]}" != "${0}" ]] && SOURCED=1
if [ -z "$SOURCED" ]; then
  pretty_error "This script needs to be sourced, i.e. source './setup.bash', not './setup.bash'"
  exit 1
fi

#############################
# System Dependencies
#############################

pretty_header "System Dependencies"
install_package python3-dev || return
install_package python3-venv || return

#############################
# Virtual Env
#############################

pretty_header "Virtual Environment"

if [ -x ${VENV_DIR}/bin/pip3 ]; then
    pretty_print "  $(padded_message "virtual_environment" "found [${VENV_DIR}]")"
else
    python3 -m venv ${VENV_DIR}
    pretty_warning "  $(padded_message "virtual_environment" "created [${VENV_DIR}]")"
fi

source ${VENV_DIR}/bin/activate

#############################
# Pypi Dependencies
#############################

pretty_header "PyPi Dependencies"

# upgrade pip3
python3 -m pip install -U pip

# build environment depedencies
pip3 install wheel
pip3 install "setuptools==45.2"

# Get all dependencies for testing, doc generation (fetches those listed in extra_requires)
# Tox handles testing dependencies now, but you still need tox and regardless, it's convenient
# to be able to run the testing tools directly without tox inbetween.
pip3 install -e .[test]

# Get package dependencies (fetches those listed in install_requires)
python3 setup.py develop

#############################
# Aliases
#############################

alias create-pypi-package="rm -rf build dist && python3 setup.py sdist bdist_wheel && twine upload dist/*"
alias create-pypi-package-test="rm -rf build dist && python3 setup.py sdist bdist_wheel && twine upload --repository-url https://test.pypi.org/legacy/ dist/*"
alias create-deb="rm -rf dist deb_dist && python setup.py --command-packages=stdeb.command bdist_deb"
alias create-source-deb="rm -rf dist deb_dist && python setup.py --command-packages=stdeb.command sdist_deb"
alias tox-all="tox -e py38"
alias tox-flake8="tox -e flake8"

#############################
# Summary
#############################

echo -e ""
echo -e "${BOLD}---------------------------------------${RESET}"
echo -e "${BOLD}        Streamlit Parameters${RESET}"
echo -e "${BOLD}---------------------------------------${RESET}"
echo -e ""
echo -e "${GREEN}Aliases${RESET}"
echo -e "${CYAN} - ${YELLOW}create-pypi-package${RESET}"
echo -e "${CYAN} - ${YELLOW}create-pypi-package-test${RESET}"
echo -e "${CYAN} - ${YELLOW}create-deb${RESET}"
echo -e "${CYAN} - ${YELLOW}create-source-deb${RESET}"
echo -e "${CYAN} - ${YELLOW}tox-all${RESET}"
echo -e "${CYAN} - ${YELLOW}tox-flake8${RESET}"
echo ""
echo "Leave the virtual environment with 'deactivate'"
echo ""
echo "I'm grooty, you should be too."
echo ""
