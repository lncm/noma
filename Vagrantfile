# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/debian10"
  config.vm.hostname = "debian-vagrant"
  config.vm.synced_folder ".", "/media/noma",
                          type: "nfs",
                          nfs_export: true
  config.vm.network "private_network", ip: "192.168.83.33"
  config.vm.provision "shell", inline: "cd /media/noma && ./install.sh"
end
