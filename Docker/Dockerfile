FROM ubuntu:focal AS builder
MAINTAINER JFG
LABEL "About"="Madness+Tequila in one container"

USER root

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone && \
    apt-get clean && apt-get update
# install python3.8 in the same way as for the standard orquestra container
# so that we can use this container with the python3 runtime of orquestra

RUN apt-get install --no-install-recommends -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install -y wget \
        git \
        vim \
        sbcl \
        curl \
        gfortran \
        clang-7 \
        libzmq3-dev \
        libz-dev \
        openssh-client \
        build-essential \
        cmake   \
        libgtk2.0-dev \
        pkg-config \
        libswscale-dev\
        libgomp1 \
        mpich 

# install madness
#RUN python -m pip --upgrade install mkl
RUN wget https://apt.repos.intel.com/intel-gpg-keys/GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    apt-key add GPG-PUB-KEY-INTEL-SW-PRODUCTS-2019.PUB && \
    sh -c 'echo deb https://apt.repos.intel.com/mkl all main > /etc/apt/sources.list.d/intel-mkl.list' && \
    apt-get update && \
    apt-get install -y intel-mkl-64bit-2020.4-912
ENV MKLROOT=/opt/intel/compilers_and_libraries/linux/mkl

RUN wget https://boostorg.jfrog.io/artifactory/main/release/1.73.0/source/boost_1_73_0.tar.bz2 && \
    tar --bzip2 -xf boost_1_73_0.tar.bz2
ENV BOOSTROOT=/app/boost_1_73_0

RUN git clone https://github.com/dpilger26/NumCpp.git numcpp
ENV NUMCPPROOT=/app/numcpp

RUN git clone https://github.com/kottmanj/madness.git madsrc && \
    mkdir madroot

RUN cmake -D ENABLE_MKL=ON -D MKL_ROOT_DIR=/opt/intel/compilers_and_libraries/linux/mkl -D CMAKE_CXX_FLAGS="-O3 -DNDEBUG -march=x86-64 -I/app/numcpp/include/ -I/app/boost_1_73_0/"  -D BUILD_SHARED_LIBS=OFF madsrc -Bmadroot && \
    sed -i 's/#include <cmath>/#include <stdexcept>\n#include <cmath>/g' madsrc/src/apps/chem/polynomial.cc && \
    make -C madroot 
# Temporary fix below to get around list of option issue: just delete some options
# Otherwise cmake puts quotes around them and compilation fails
#RUN sed -i "s/-flto=auto;-ffat-lto-objects;-flto=auto/-flto=auto/g" madroot/CMakeCache.txt


FROM ubuntu:focal 
MAINTAINER JFG
LABEL "About"="Madness+Tequila in one container"

USER root

WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$CONTAINER_TIMEZONE /etc/localtime && echo $CONTAINER_TIMEZONE > /etc/timezone && \
    apt-get clean && apt-get update
# install python3.8 in the same way as for the standard orquestra container
# so that we can use this container with the python3 runtime of orquestra

RUN apt-get install --no-install-recommends -y software-properties-common && \
    add-apt-repository -y ppa:deadsnakes/ppa && \
    apt-get install --no-install-recommends -y python3.8 && \
    apt-get install --no-install-recommends -y python3-pip && \
    apt-get install --no-install-recommends -y python3.8-dev \
        wget \
        git \
        sbcl \
        curl \
        libzmq3-dev \
        libz-dev \
        openssh-client \
        mpich 

RUN update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.8 1 && \
    update-alternatives --set python3 /usr/bin/python3.8

ENV PYTHONPATH="/usr/local/lib/python3.8/dist-packages:${PYTHONPATH}"

RUN python3 -m pip install --upgrade pip && python3 -m pip install --upgrade setuptools 


# install tequila
# PyPi version is fine here
RUN python3 -m pip install pyscf && \
    python3 -m pip install git+https://github.com/aspuru-guzik-group/tequila.git@devel && \
    python3 -m pip install periodictable 
#   for MRA-PNO, qulacs is not needed
#    python3 -m pip install qulacs

# Add SSH enhancments to allow GITHUB/SSH access
RUN true \
    && mkdir -p -m 0700 ~/.ssh \
    && ssh-keyscan github.com >> ~/.ssh/known_hosts \
    && chmod 600 $HOME/.ssh/known_hosts \
    && true

RUN python3 -m pip install \
          pyyaml \
          codecarbon==1.2.0 

COPY --from=builder /app/madroot /app/madroot
COPY --from=builder /app/madsrc /app/madsrc
# export the madness root dir, so that tq can find the executable automatically
ENV MAD_ROOT_DIR=/app/madroot

RUN ln -s /madroot/src/apps/pno/pno_integrals /usr/bin/pno_integrals

WORKDIR /app
ENTRYPOINT bash
