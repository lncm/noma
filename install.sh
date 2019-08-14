#!/bin/sh

# install noma and dependencies within alpine linux
# or run with "vagrant up" to create alpine VM

alpine_install() {
    # noma dependencies
    apk add python3 py3-psutil
    # docker
    apk add docker
    service docker start
    # docker-compose
    apk add libffi-dev py3-cffi python3-dev build-base python3 openssl-dev
    pip3 install docker-compose
    # install noma
    python3 setup.py develop
    # run noma
    noma --version || exit 1
    noma --help || exit 1
    run_tests
}

run_tests() {
    # test noma
    if [ -x "$(command -v noma)" ]; then
	    python3 tests/test_lnd.py
    else
	    echo "Error: noma python package not available"
	    echo
	    echo "Please ensure python3 and noma are installed correctly."
    fi
}

install_git() {
    apk add git
    git clone https://github.com/lncm/noma.git
    if [ ! -f setup.py ]; then
        cd noma || exit
    fi
    alpine_install
}

chroot_install() {
    # create alpine chroot before alpine_install
    wget https://raw.githubusercontent.com/alpinelinux/alpine-chroot-install/v0.10.0/alpine-chroot-install \
        && echo 'dcceb34aa63767579f533a7f2e733c4d662b0d1b  alpine-chroot-install' | sha1sum -c \
        || exit 1
    chmod +x ./alpine-chroot-install || exit 1
    ./alpine-chroot-install -d /alpine-v310 -b v3.10
    /alpine-v310/enter-chroot install.sh
}

check_vm() {
    if [ -d "/vagrant" ]; then
        echo "Detected vagrant VM"
        mkdir /media/noma
        cp -R /vagrant/* /media/noma/ || exit
        alpine_install
    else
        echo "Vagrant not found!"
        echo
        echo "Fetching noma sources from github instead"
        mkdir /media
        mkdir /media/noma
        cd /media/noma || exit
        install_git
    fi
}

main() {
    if [ -f "/etc/alpine-release" ]; then
        check_vm
    else
        echo "Not an alpine linux system!"
        echo
        echo "Attempting to create alpine chroot"
        chroot_install || exit 1
        check_vm

    fi
}
main
