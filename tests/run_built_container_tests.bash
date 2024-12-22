#! /usr/bin/env bash

# Start hserver
hserver --clientid ${CLIENT_ID} --clientsecret ${CLIENT_SECRET} --host ${LICENSE_SERVER}

# Check that hython runs.
hython -c "print(hou.applicationVersionString())"

# Check some rez packages.
rez-env houdini -- hython -c "print(hou.applicationVersionString())"

# Verify that the Python version is as expected for the various aliases and package binding.  This is to catch any
# weirdness with the container default Python versions and symlinks that might need to be corrected.
python --version | grep ${_CONTAINER_PYTHON_VERSION}
python3 --version | grep ${_CONTAINER_PYTHON_VERSION}
rez-env python -- python --version | grep ${_CONTAINER_PYTHON_VERSION}

# Test that pip is accessible and sourced from the correct Python version.
pip --version | grep "python${_CONTAINER_PYTHON_VERSION}"
pip3 --version | grep "python${_CONTAINER_PYTHON_VERSION}"
python -m pip --version | grep "python${_CONTAINER_PYTHON_VERSION}"
python3 -m pip --version | grep "python${_CONTAINER_PYTHON_VERSION}"
