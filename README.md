# Noma - lightning node management

CLI utility and Python API to manage bitcoin lightning nodes.

[![Build Status](https://travis-ci.com/lncm/noma.svg?branch=master)](https://travis-ci.com/lncm/noma)
[![Documentation Status](https://readthedocs.org/projects/noma/badge/?version=latest)](https://noma.readthedocs.io/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/fd95275314bd4f680140/maintainability)](https://codeclimate.com/github/lncm/noma/maintainability)

### Command-line usage:

**node**:

```
noma (info|start|stop|restart|logs|check|status)
noma (temp|swap|ram)
noma (freq|memory|voltage) [<device>]
noma usb-setup
noma tunnel <port> <host>
noma (backup|restore|source|diff|devtools)
noma reinstall [--full]
```

**bitcoind**:

```
noma bitcoind (start|stop|info|fastsync|status|check)
noma bitcoind get <key>
noma bitcoind set <key> <value>
noma bitcoind logs [--tail]
```

**lnd**:

```
noma lnd (start|stop|info)
noma lnd logs [--tail]
noma lnd connect <address>
noma lnd (create|unlock|status|check)
noma lnd lncli [<command>...]
noma lnd get <key> [<section>] [<path>]
noma lnd set <key> <value> [<section>] [<path>]
noma lnd autounlock
noma lnd autoconnect [<path>]
```

**noma**:

```
noma (-h|--help)
noma --version

 Options:
-h --help     Show this screen.
--version     Show version.
```

### API documentation

[Read the Docs](https://noma.readthedocs.io/en/latest/)

### Dependencies

To get the most out of this tool we highly recommend to have `docker` and `docker-compose` installed.

Currently, some third-party components need to be installed and configured separately when not using `noma` in combination with https://github.com/lncm/pi-factory to enable all functionality.

Some `noma` functions are specific to Raspberry Pi hardware.

### Installation

#### Vagrant (MacOS/Windows)

- Install Vagrant, VirtualBox (or other virtual-machine such as Parallels or VMware)

```
cd noma
vagrant up
```

#### Linux

`pip install noma`

### Build instructions

```
pip3 install wheel docker docker-compose
python3 setup.py bdist_wheel
pip install dist/noma-*-py3-none-any.whl
```

### Build docs

```
pip3 install sphinx sphinx-rtd-theme`
cd docs
make html
```

docs can be found at `docs/_build/html/index.html`
