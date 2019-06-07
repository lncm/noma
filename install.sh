#!/bin/sh

# install noma and dependencies within alpine linux 
# or run with "vagrant up" to create alpine VM

alpine_install() 
{
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
    # test noma
    python3 tests/test_usb.py
    python3 tests/test_install.py
    # run noma
    noma --version
    noma --help
}

install_git() 
{
    apk add git
    git clone https://github.com/lncm/noma.git
    cd noma || exit
    alpine_install
}

vagrant_install()
{
    if [ -f "/vagrant" ]; then
        cd /vagrant || exit
        alpine_install
    else
        install_git
    fi
}

# chroot_install() 
# {
#     # TODO: alpine-chroot and then install()
# }

check_vm() 
{
    if [ -f "/vagrant" ]; then
        echo "detected vagrant VM"
        vagrant_install
    else
        echo "fetching noma sources"
        install_git
    fi
}

main()
{
    if [ -f "/etc/alpine-release" ]; then
        check_vm
    else
        # TODO: Create chroot here on Ubuntu
        echo "Error: not an alpine linux system!"
        exit 1
    fi
}
main