Houdini Docker Image Generator
==============================

[![Builder](https://github.com/captainhammy/test-docker-builder/actions/workflows/build_houdini_image.yml/badge.svg)](https://github.com/captainhammy/test-docker-builder/actions/workflows/build_houdini_image.yml)
[![Tests](https://github.com/captainhammy/test-docker-builder/actions/workflows/tests.yml/badge.svg)](https://github.com/captainhammy/test-docker-builder/actions/workflows/tests.yml)
[![dockerhub](https://img.shields.io/badge/dockerhub-hython--runner-orange?logo=docker)](https://hub.docker.com/r/captainhammy/hython-runner)

This project is used to generate Docker images which can be used to run **hython** with the goal of performing automated
testing with processes such as GitHub Actions.

# Side Effects License Agreement

Use of these images is subject to the terms and conditions of the [SIDE EFFECTS SOFTWARE
LICENSE AGREEMENT](https://www.sidefx.com/legal/license-agreement/). By using these images, you agree to abide by all the terms and conditions as described in the [SIDE EFFECTS SOFTWARE
LICENSE AGREEMENT](https://www.sidefx.com/legal/license-agreement/)


# VFX Platform

Each image for a particular build of Houdini provides versions of related tools matching those of the [VFX Platform](https://vfxplatform.com/).

Currently, all images provided are created using the **default** build of Houdini, which means libraries that match
those of the VFX Platform year, and not builds with alternative Python or GCC versions.

| Houdini Version | Linux Image   | VFX Platform Year | Python Version | GCC Version    |
|-----------------|---------------|-------------------|----------------| ---------------|
| 20.5            | ubuntu:mantic | 2024              | 3.11           | 11.2           |
| 20.0            | ubuntu:jammy  | 2023              | 3.10           | 11.2           |
| 19.5            | ubuntu:focal  | 2022              | 3.9            | 9.3            |

# Installed System Packages

The following notable system packages are installed:

- git - Available to allow you to check out code required for testing 
- gcc / cmake / build related packages - Packages related to C++ compilation are included to enable building HDK plugins.
- nodejs - Node.js (v20) is installed to facilitate various GitHub Action workflows which rely on it.

# Houdini Specifics

## Installation Notes

The Houdini build is installed to the standard `/opt/hfs{version}` location, along with the {major.minor} symlink:

```bash
$ ls -l /opt/
... hfs19.5 -> /opt/hfs19.5.805
... hfs19.5.805
```

Houdini command line tool locations ($HFS/bin, $HFS/houdini/sbin) are included in `$PATH`, however the only Houdini specific
environment variable defined is `$HFS`. Other variables defined in the `houdini_setup*` files ($HB, $HT, etc.) are not set.
If you need any of these, it is recommended to explicitly source the setup file.

## License Setup

The `hython-runner` containers do not have any Houdini licensing set up which means that Houdini related programs
which require a license will not function by default. **You** are responsible for configuring your own licensing
setup.

## Compiling Plugins

It should be possible to compile HDK plugins right out of the box, using either `hcustom` or `cmake`.

The `CMAKE_PREFIX_PATH` variable is defined and pointing to the `$HT/cmake` directory such that if you are using cmake
to compile HDK plugins, it will be able to find the Houdini config without additional setup.

# Rez

The [rez](https://rez.readthedocs.io/en/stable/) package manager is also available for workflows which use it. A number of already bound or installed
packages which are designed to help facilitate testing.


## Bound Rez Packages
- houdini
- cmake
- gcc
- python

## Installed Rez Packages

### Testing
- [pytest](https://pypi.org/project/pytest/)
- [pytest-cov](https://pypi.org/project/pytest-cov/)
- [pytest-datadir](https://pypi.org/project/pytest-datadir/)
- [pytest-houdini](https://pypi.org/project/pytest-houdini/)
- [pytest-mock](https://pypi.org/project/pytest-mock/)
- [pytest-qt](https://pypi.org/project/pytest-qt/)
- [pytest-subprocess](https://pypi.org/project/pytest-subprocess/)
- [tox](https://pypi.org/project/tox/)
   
### Linting and Analysis
- [black](https://pypi.org/project/black/)
- [isort](https://pypi.org/project/isort/)
- [mypy](https://pypi.org/project/mypy/)
- [pydocstringformatter](https://pypi.org/project/pydocstringformatter/)
- [pylint](https://pypi.org/project/pylint/)
- [ruff](https://pypi.org/project/ruff/) 
 
### Other
- [numpy](https://pypi.org/project/numpy/) - The installed version matches that of the VFX Platform year 
- [PySide2](https://pypi.org/project/PySide2/) or [PySide6](https://pypi.org/project/PySide6/) - The installed version matches that of the VFX Platform year 
- [Qt.py](https://pypi.org/project/Qt.py/)
- [scipy](https://pypi.org/project/scipy/)
- [sphinx](https://pypi.org/project/Sphinx/)
