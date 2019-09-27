# Noma - lightning node management

CLI utility and Python API to manage bitcoin lightning nodes.

[![Build Status](https://travis-ci.com/lncm/noma.svg?branch=master)](https://travis-ci.com/lncm/noma)
[![Documentation Status](https://readthedocs.org/projects/noma/badge/?version=latest)](https://noma.readthedocs.io/en/latest/?badge=latest)
[![Maintainability](https://api.codeclimate.com/v1/badges/fd95275314bd4f680140/maintainability)](https://codeclimate.com/github/lncm/noma/maintainability)

### What is it?
Noma provides a complete bitcoin + lightning stack for [LNCM's](https://lncm.io) Point-of-Sale app and extendable templates for your own project development.

### How does it work?
Multi-platform `docker` containers are orchestrated by `docker-compose` and `noma`, a thin layer of python. The golang `invoicer` middleware serves `invoicer-ui`, a react webapp and provides the payment API synthesizing `lnd` and `bitcoind`. Internally `lnd` utilizes the light-client neutrino network, while `bitcoind` operates as a fully validating node with optional pruning.

### Highlights
Our containers provide minimal [Alpine](https://alpinelinux.org) environments on 32-bit & 64-bit ARM in addition to the common AMD64 architecture. Special attention been paid to create lightweight images suitable for embedded deployments such as Raspberry Pi's.

Significant effort has been expended to make bootstrapping convenient on Ubuntu, Debian, Alpine and MacOS while staying flexible to support your deployment method of choice.

Default settings are carefully chosen to conserve resources and let nodes participate as quickly as possible.

With the exception of `bitcoind` all critical components and dependencies are either written in Golang or Python, making use of our focused build pipeline.

### Target audience

At the current level of automation we expect users to be familiar with the Linux command-line. Bitcoin & lightning enthusiasts as well as developers may find this opinionated framework to be a useful starting point.

### Target hardware

Given the minimal nature of our stack, Raspberry Pi's and similar SBC's are an ideal candidate. Likewise, low-end VPS will benefit from the reduced resource usage.

Disk and network resource consumption varies according to mode. In the most conservative configuration, using neutrino only, on-disk storage requirements are expected to be around 250-300MB.

In bitcoin full-node mode, the latest 550 blocks are stored and continually fetched for verification. This adds around 4GB of permanently reserved space and at least 144MB of internet traffic per day, equivalent to 4.4GB per month.

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

To get the most out of this tool we highly recommend to have Docker installed.

Note: some `noma` functions are specific to Raspberry Pi hardware.

## Installation

### MacOS Vagrant

The simplest method to try out or work on noma is to use Vagrant, which will automatically set up a small Linux VM, ensuring your environment stays clean.

* Install Vagrant & VirtualBox

With brew available:
```bash
brew cask install virtualbox
brew cask install vagrant
```
Then, start the VM using vagrant
```bash
cd noma
vagrant up
```

Once installation has completed, you may log in
```bash
vagrant ssh alpine
```

Tip: `vagrant up [vm-name]` where `vm-name` can be any of: `alpine`, `ubuntu`, `debian`. Adapt `vagrant ssh alpine` accordingly.

#### MacOS Docker

Using Docker outside of Vagrant requires manual setup and is only recommended for those who are already running Docker.

- Install Docker and docker-compose
```bash
brew cask install docker
brew install docker-compose
```

Create /media directory
```bash
sudo mkdir /media
```

* Ensure the /media directory is writable and added to shares in Docker
* Ensure Docker is running

Install and start the node
```bash
pip3 install noma
sudo noma start
```

### Linux

With Python 3 and Docker installed

```
pip install noma 
sudo noma start
```
Note: You may need to use `pip3` instead of `pip`

For convenience `install.sh` may be used to bootstrap Python 3, Docker and Noma on Debian-based and Alpine systems.

### Windows

While not officially supported, Windows is likely to work using Vagrant, with the caveat that NFS shares are not available and need to be replaced.

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
pip3 install wheel
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
