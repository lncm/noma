# Noma - lightning node management

CLI utility and Python API to manage bitcoin lightning nodes.

[![Build Status](https://travis-ci.com/lncm/noma.svg?branch=master)](https://travis-ci.com/lncm/noma)
[![Documentation Status](https://readthedocs.org/projects/noma/badge/?version=latest)](https://noma.readthedocs.io/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/fd95275314bd4f680140/maintainability)](https://codeclimate.com/github/lncm/noma/maintainability)

### CLI:
**node:**
```bash
noma start
noma stop
noma check
noma logs
noma info
```
**lnd:**
```bash
noma lnd create
noma lnd backup
noma lnd autounlock
noma lnd autoconnect [<path>]
noma lnd savepeers
noma lnd connectstring
```
**noma:**
```
noma (-h|--help)
noma --version
```

### Dependencies

To get the most out of this tool we highly recommend to have `docker` and `docker-compose` installed.

Note: some `noma` functions are specific to Raspberry Pi hardware.

## Installation

#### MacOS Docker
- Install Docker and docker-compose
```base
brew cask install docker
brew install docker-compose
```
- Ensure the /media directory is writable and added to shares in Docker

`sudo mkdir /media`

- Ensure Docker is running

- Install and start the node
```bash
pip3 install noma
sudo noma start
```

#### Vagrant (MacOS/Windows)

- Install Vagrant, VirtualBox (or other virtual-machine such as Parallels or VMware)

```bash
cd noma
vagrant up
```

#### Linux

```
pip install noma 
sudo noma start
```

* Make sure to use Python 3. 

Note: You may need to use `pip3` instead of `pip`

## Usage

After running `sudo noma start` you may create your wallet  

`sudo noma lnd create`

Once your node has synced with the network you are ready for action.

Check it's status with `sudo noma info` and `sudo noma logs`

## Development

We welcome all contributions! Please submit a PR or discuss within an issue.

### Dev mode

```bash
cd noma
python3 setup.py develop
```
now you can run noma and inspect code changes immediately

*Note: vagrant runs this automatically*

### Build instructions

```
pip3 install wheel docker docker-compose
python3 setup.py bdist_wheel
pip3 install dist/noma-*-py3-none-any.whl
```

### API documentation

[Read the Docs](https://noma.readthedocs.io/en/latest/)


### Build docs

```
pip3 install sphinx sphinx-rtd-theme`
cd docs
make html
```

docs can be found at `docs/_build/html/index.html`
