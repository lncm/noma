#!/bin/sh

# install noma and dependencies on Alpine and
# Debian-based Linux systems or run with
# "vagrant up" to create VM

set -e

alpine_install() {
    # noma dependencies
    apk add python3 py3-psutil
    # docker
    apk add docker
    service docker start
    # docker-compose
    apk add libffi-dev py3-cffi python3-dev build-base python3 openssl-dev
    # install noma
    python3 setup.py develop
}

run_noma() {
    # run noma
    noma --version
    noma --help
    run_tests
    start_noma
}

debian_install() {
    # only install docker if missing
    if ! command -v docker >/dev/null 2>&1; then
        curl -fsSL https://get.docker.com | sh
    fi

    # apt dependencies
    apt-get install -y python3-pip python3-cffi libffi-dev libssl-dev

    # check if source keyword exists to guard against bashism
    if type source >/dev/null 2>&1; then
        # reload profile to update PATH
        source ~/.profile

        # python virtual environment
        pip3 install virtualenv
        virtualenv /media/noma/venv

        # source python virtual environment
        source /media/noma/venv/bin/activate
    fi

    # noma
    python3 setup.py develop
}

start_noma() {
    noma start
    echo "Waiting 5s for lnd to start up..."
    sleep 5 && noma lnd create
    docker logs neutrino_lnd_1
    echo "Waiting 5s for wallet to be created..."
    sleep 5 && noma info
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
    apk add git >/dev/null 2<&1 || apt-get install git -y >/dev/null 2<&1
    git clone https://github.com/lncm/noma.git
    if [ ! -f setup.py ]; then
        cd noma || exit 1
    fi
    check_os
}

chroot_install() {
    # create alpine chroot before alpine_install
    wget https://raw.githubusercontent.com/alpinelinux/alpine-chroot-install/v0.10.0/alpine-chroot-install \
        && echo 'dcceb34aa63767579f533a7f2e733c4d662b0d1b  alpine-chroot-install' | sha1sum -c \
        || exit 1
    chmod +x ./alpine-chroot-install || exit 1
    ./alpine-chroot-install -d /alpine-v310 -b v3.10
    /alpine-v310/enter-chroot ./install.sh
}

check_os() {
    if [ -f "/etc/alpine-release" ]; then
        alpine_install
        return 0
    fi

    if command -v apt-get >/dev/null 2>&1; then
        debian_install
        return 0
    fi

    echo "Not an Alpine or Debian-based Linux system"
    echo
    echo "Attempting to create Alpine chroot"
    chroot_install
}

check_root() {
    if [ "$(id -u)" != "0" ]; then
       echo "Error: You must be root to install"
       exit 1
    fi
}

fetch_html() {
    apk add curl >/dev/null 2<&1 || apt-get install curl -y >/dev/null 2<&1
    if ! command -v curl >/dev/null 2<&1; then
        echo "Error: curl not available"
        return 1
    fi

    if ! [ -f "public_html/index.html" ]; then
        curl https://raw.githubusercontent.com/lncm/invoicer-ui/master/dist/index.html \
        --create-dirs -o public_html/index.html
        return 0
    fi

    if ! [ -f "public_html/index.html" ]; then
        echo "Error: index.html missing"
        return 1
    fi
}

main() {
    check_root
    if [ -d "/media/noma" ]; then
        echo "Detected source directory"
        # Vagrant mode
        check_os
    else
        echo "Sources not found, fetching from github..."
        mkdir -p /media
        cd /media
        install_git
    fi
    fetch_html
    run_noma
}
main