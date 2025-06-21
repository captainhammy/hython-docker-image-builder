ARG OS_IMAGE=ubuntu:noble

FROM ${OS_IMAGE} AS houdini-install

ARG EULA_DATE=2021-10-13
ARG PYTHON_VERSION=3.11

ARG HOUDINI_VERSION
ARG HOUDINI_INSTALL_DIR=/opt/hfs${HOUDINI_VERSION}
ARG HOUDINI_INSTALLER_FILENAME=install_houdini_launcher.sh
ARG HOUDINI_ISO_FILENAME

# Settings to install tzdata non-interactively otherwise it will stall waiting on input.
ARG DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC

WORKDIR /tmp/houdini_installation

# Copy in the default list of pip packages to install.
COPY default_pip_packages.txt ./

# Copy in the installer files.
ADD --chmod=755 ${HOUDINI_INSTALLER_FILENAME} ${HOUDINI_ISO_FILENAME} ./

RUN apt update \
    && apt upgrade -y \
    && apt install -y tzdata csh curl git pkg-config procps wget software-properties-common gcc-11 g++-11 libglu1-mesa libsm6 bc libnss3 libx11-6 libx11-xcb1 libxcb1 libxcb1-dev libxcb-icccm4 libx11-xcb-dev libxrandr2 libxcomposite-dev libxdamage1 libxcursor1 libxi6 libxkbcommon-x11-0 libxtst6 libfontconfig1 libxss1 libpci3 libasound2t64 libx11-dev libxi-dev libgl-dev build-essential gfortran cmake \
    # Python 3.11 for noble is not available in the standard repositories so we'll need to access it from deadsnakes.
    && add-apt-repository -y ppa:deadsnakes/ppa \
    && apt update \
    && apt install -y python${PYTHON_VERSION} python${PYTHON_VERSION}-venv \
    # Install a newer version of nodejs to work better with certain github actions.
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt install -y nodejs \
    && apt clean \
    && rm -rf /var/lib/apt/lists/* \
    # Some tools like rez can require a bare 'python' call to run, so generate a symlink for that name
    # to the link containing the major.minor version.
    && ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python \
    # Remove and recreate the 'python3' symlink as it will be pointing to the OS default, 3.12.
    && rm -f /usr/bin/python3 \
    && ln -s /usr/bin/python${PYTHON_VERSION} /usr/bin/python3 \
    # Remove any externally managed file if it exists as we want to easily be able to install tools via \
    # pip without the OS/Python getting in the way.
    && rm -f /usr/lib/python${PYTHON_VERSION}/EXTERNALLY-MANAGED \
    # Download and install the latest pip.
    && wget https://bootstrap.pypa.io/get-pip.py \
    && python${PYTHON_VERSION} get-pip.py \
    && rm get-pip.py \
    # Install a selection of default packages we want available in the container.
    && python -m pip install -r ./default_pip_packages.txt \
    && rm ./default_pip_packages.txt

# Install Houdini and the license server.
# Create '/usr/share/applications/' first, if it doesnt exist, so the installer won't fail trying to install shortcuts.
RUN ./${HOUDINI_INSTALLER_FILENAME} --no-desktop-menus --quiet launcher \
    && launcher/bin/houdini_installer install Houdini --accept-EULA SideFX-${EULA_DATE} --accept-EULA SideFX-Beta-${EULA_DATE} --offline-installer ${HOUDINI_ISO_FILENAME} --desktop-menus no --installdir ${HOUDINI_INSTALL_DIR} \
    && launcher/bin/houdini_installer install "License Server" --accept-EULA SideFX-${EULA_DATE} --accept-EULA  SideFX-Beta-${EULA_DATE} --offline-installer ${HOUDINI_ISO_FILENAME} \
    # We're done with the launcher and source files so we can remove them all.
    # Also, remove extra files we don't want to slim down the eventual image.
    && rm -rf /tmp/houdini_installation ${HOUDINI_INSTALL_DIR}/houdini/pic ${HOUDINI_INSTALL_DIR}/houdini/help ${HOUDINI_INSTALL_DIR}/houdini/public

# Install the latest release tag of rez.

RUN git clone https://github.com/AcademySoftwareFoundation/rez.git \
    && git -C rez fetch --tags \
    && latestTag=$(git -C rez describe --tags `git rev-list --tags --max-count=1`) \
    && git -C rez checkout $latestTag \
    && python rez/install.py \
    && rm -rf rez

# Start from a new, clean image that we'll copy the previous results into.
FROM ${OS_IMAGE}
COPY --from=houdini-install / /

ARG HOUDINI_VERSION
ARG HOUDINI_INSTALL_DIR=/opt/hfs${HOUDINI_VERSION}
ENV HFS=${HOUDINI_INSTALL_DIR}

# Keep track of this for testing purposes.
ENV _CONTAINER_PYTHON_VERSION=3.11

ARG REZ_DIR="/opt/rez"

# Clone custom bind files and add them to the search bath
ADD https://github.com/captainhammy/rez-bind-files.git ${REZ_DIR}/bind_files
ENV REZ_BIND_MODULE_PATH=${REZ_DIR}/bind_files/bind

# Add installed tools to the PATH so they can execute.
ENV PATH="${REZ_DIR}/bin/rez:${HFS}/bin:${HFS}/houdini/sbin:${PATH}"

# Export path to Houdini cmake files.
ENV CMAKE_PREFIX_PATH=${HFS}/toolkit/cmake

# We want to put all the packages under /opt/rez/packages and set the appropriate
# variables to point to this location so that they will all be installed there, and
# any packages installed within the container will also end up there.
ARG _REZ_PACKAGE_DIR=${REZ_DIR}/packages

ENV REZ_PACKAGES_PATH=${_REZ_PACKAGE_DIR}
ENV REZ_LOCAL_PACKAGES_PATH=${_REZ_PACKAGE_DIR}

# Bind and install rez packages.
RUN mkdir ${_REZ_PACKAGE_DIR} \
    && rez-bind --quickstart \
    && rez-bind houdini ${HOUDINI_INSTALL_DIR} \
    && rez-bind cmake \
    && rez-bind gcc --exe /usr/bin/gcc-11 \
    && rez-pip --install black \
    && rez-pip --install humanfriendly \
    && rez-pip --install isort \
    && rez-pip --install mypy[toml] \
    && rez-pip --install 'numpy<1.25' \
    && rez-pip --install PySide6 \
    && rez-pip --install pydocstringformatter \
    && rez-pip --install pylint \
    && rez-pip --install pytest \
    && rez-pip --install pytest-cov \
    && rez-pip --install pytest-datadir \
    && rez-pip --install pytest-houdini \
    && rez-pip --install pytest-mock \
    && rez-pip --install pytest-qt \
    && rez-pip --install pytest-subprocess \
    && rez-pip --install python_singleton \
    && rez-pip --install Qt.py==1.4.1 \
    && rez-pip --install ruff \
    && rez-pip --install scipy \
    && rez-pip --install sphinx \
    && rez-pip --install tox

# Install Houdini Rez CMake tools
RUN git -C /tmp/ clone https://github.com/captainhammy/houdini-rez-cmake-tools.git \
    && cd /tmp/houdini-rez-cmake-tools \
    && rez build --install \
    && cd - \
    && rm -rf /tmp/houdini-rez-cmake-tools
