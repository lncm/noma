#!/bin/sh

# build and install manpage for noma
set -eu

MANPAGE="noma.1"
MAN_DIR="/usr/local/man/man1"
MAN_DIR_ALPINE="/usr/share/man/man1"


check_root() {
    if [ "$(id -u)" != "0" ]; then
       echo "Error: You must be root to install"
       exit 1
    fi
}

check_directory() {
    if [ ! -d "docs" ]; then
        echo "Error: must be run from the noma root directory (e.g 'docs/install_manpage.sh')"
        exit 1
    fi
}

alpine_os() {
    if [ -f "/etc/alpine-release" ]; then
        return 0
    fi
}

check_root
check_directory

if [ alpine_os ]; then
    MAN_DIR=$MAN_DIR_ALPINE
fi

cd docs
sphinx-build . _build -b man
install -g 0 -o 0 -m 0644 _build/$MANPAGE $MAN_DIR
gzip ${MAN_DIR}/${MANPAGE}
if [ ! alpine_os ]; then
    mandb
fi
