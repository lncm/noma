# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|

  config.vm.box = "generic/alpine39"
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".git/"

  config.vm.provision "shell", inline: <<-SHELL
    apk add python3 py3-psutil
    cd /vagrant
    python3 setup.py develop
    python3 /vagrant/tests/test_usb.py
  SHELL
end
