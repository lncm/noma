# -*- mode: ruby -*-
# vi: set ft=ruby :
Vagrant.configure("2") do |config|

  config.vm.box = "generic/alpine39"
  config.vm.hostname = "alpine-vagrant"
  config.vm.synced_folder ".", "/vagrant", type: "rsync", rsync__exclude: ".git/"

  config.vm.provision "shell", path: "install.sh"
end
