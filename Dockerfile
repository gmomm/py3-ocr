FROM ubuntu:18.04

ARG BUILD_PACKAGES1="   \
    build-essential     \
    apt-utils           \
    cmake               \
    gfortran            \
    libatlas-base-dev   \
    libavcodec-dev      \
    libavformat-dev     \
    libjpeg8-dev        \
    libgtk2.0-dev       \
    libtiff5-dev        \
    libswscale-dev      \
    libv4l-dev          \
    pkg-config          "

ARG BUILD_PACKAGES2="   \
    autoconf    \
    automake                    \
    g++                         \
    libtool                     \
    libjpeg8-dev                \
    libtiff5-dev                \
    pkg-config                  \
    zlib1g-dev                  "

# Extra build packages installed automatically that we wish to remove

ARG EXTRA_BUILD_PACKAGES="binutils bzip2 cmake-data cpp cpp-5 cpp-6 dpkg-dev \
g++ g++-5 g++-6 gcc gcc-5 gcc-6 gfortran-5 gfortran-6 git-man libavutil-dev  \
libgcc-5-dev libgcc-6-dev libgfortran-6-dev \
libharfbuzz-dev libice-dev libjbig-dev libjpeg-turbo8-dev liblzma-dev libpcre3-dev libpixman-1-dev \
libpthread-stubs0-dev libsm-dev libstdc++-5-dev libswresample-dev  libx11-dev libxau-dev \
libxcb-render0-dev libxcb-shm0-dev libxcb1-dev libxcomposite-dev libxcursor-dev libxdamage-dev \
libxdmcp-dev libxext-dev libxfixes-dev libxi-dev libxinerama-dev libxrandr-dev libxrender-dev \
make patch x11proto-composite-dev x11proto-core-dev x11proto-damage-dev x11proto-fixes-dev \
x11proto-input-dev x11proto-kb-dev x11proto-randr-dev x11proto-render-dev x11proto-xext-dev \
x11proto-xinerama-dev xtrans-dev zlib1g-dev"

ARG EXTRA_PACKAGES="autotools-dev \
    dpkg-dev file libc-dev-bin \
    libcc1-0 libcilkrts5 libdpkg-perl libjbig-dev libjpeg-turbo8-dev \
    liblzma-dev libstdc++-5-dev linux-libc-dev m4 make patch"


RUN apt-get update \
 && apt-get upgrade  -y \
 && apt-get install -y --no-install-recommends $BUILD_PACKAGES1 \
 && apt-get install -y --no-install-recommends $BUILD_PACKAGES2 \ 
 && apt-get install -y --no-install-recommends python3.6-dev  python3-pip
 
RUN pip3 install --upgrade pip 
RUN pip3 install numpy scipy setuptools

RUN mkdir -p /tmp/workdir
WORKDIR /tmp/workdir
    
ADD opencv-contrib-4.1.0.tar.gz .
ADD opencv-4.1.0.tar.gz .
ADD ./leptonica-1.78.0.tar.gz .
ADD ./tesseract-master.tar.gz .

# build and install opencv
RUN cd opencv-4.1.0 \
    && mkdir build \
    && cd build \
    && cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D INSTALL_C_EXAMPLES=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D OPENCV_EXTRA_MODULES_PATH=./opencv_contrib-4.1.0/modules \
    -D BUILD_EXAMPLES=OFF .. \
    && make -j2 \
    && make install \
    && ldconfig

# build and install leptonica
RUN cd ./leptonica-1.78.0 \
    && ./configure \
    && make -j2 \
    && make install \
    && cd ..

# build and install tesseract 4
RUN cd ./tesseract-master \
    && ./autogen.sh LIBLEPT_HEADERSDIR=/usr/local/lib --with-extra-libraries=/usr/local/lib \
    && ./configure \
    && make -j2 \
    && make install \
    && ldconfig

RUN pip3 install pytesseract pillow

# Download english tesseract model
ADD ./por.traineddata /usr/local/share/tessdata/
ADD ./eng.traineddata /usr/local/share/tessdata/

RUN apt-get purge -y $BUILD_PACKAGES $EXTRA_BUILD_PACKAGES \
       $BUILD_PACKAGES2 $EXTRA_PACKAGES \
    && rm -rf /var/lib/apt/lists/* \
    && rm -rf /tmp/workdir/*
 

