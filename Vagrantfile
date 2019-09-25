# -*- mode: ruby -*-
# vi: set ft=ruby :

required_plugins = %w(vagrant-alpine)

plugins_to_install = required_plugins.select { |plugin| not Vagrant.has_plugin? plugin }
if not plugins_to_install.empty?
  puts "Installing plugins: #{plugins_to_install.join(' ')}"
  if system "vagrant plugin install #{plugins_to_install.join(' ')}"
    exec "vagrant #{ARGV.join(' ')}"
  else
    abort "Installation of one or more plugins has failed. Aborting."
  end
end

Vagrant.configure("2") do |config|
  config.vm.define "alpine", autostart: true do |alpine|
    alpine.vm.box = "generic/alpine310"
    alpine.vm.hostname = "alpine-vagrant"
    alpine.vm.synced_folder ".", "/media/noma",
                            type: "nfs",
                            nfs_export: true
    alpine.vm.network "private_network", ip: "192.168.83.33"
    alpine.vm.network "forwarded_port", guest: 9735, host: 9735
    alpine.vm.network "forwarded_port", guest: 10009, host: 10009
    alpine.vm.network "forwarded_port", guest: 8080, host: 8080
    alpine.vm.network "forwarded_port", guest: 8181, host: 8181
    alpine.vm.provision "shell", inline: "cd /media/noma && ./install.sh"
  end

  config.vm.define "debian", autostart: false do |debian|
    debian.vm.box = "generic/debian10"
    debian.vm.hostname = "debian-vagrant"
    debian.vm.synced_folder ".", "/media/noma",
                          type: "nfs",
                          nfs_export: true
    debian.vm.network "private_network", ip: "192.168.83.33"
    debian.vm.provision "shell", inline: "cd /media/noma && ./install.sh"
  end

  config.vm.define "ubuntu", autostart: false do |ubuntu|
    ubuntu.vm.box = "ubuntu/bionic64"
    ubuntu.vm.hostname = "ubuntu-vagrant"
    ubuntu.vm.synced_folder ".", "/media/noma",
                          type: "nfs",
                          nfs_export: true
    ubuntu.vm.network "private_network", ip: "192.168.83.33"
    ubuntu.vm.provision "shell", inline: "cd /media/noma && ./install.sh"
  end

  config.vm.define "alpine-empty", autostart: false do |empty|
    empty.vm.box = "generic/alpine310"
    empty.vm.hostname = "alpine-empty"
    empty.vm.network "private_network", ip: "192.168.83.33"
    empty.vm.network "forwarded_port", guest: 9735, host: 9735
    empty.vm.network "forwarded_port", guest: 10009, host: 10009
    empty.vm.network "forwarded_port", guest: 8080, host: 8080
    empty.vm.network "forwarded_port", guest: 8181, host: 8181
  end
end
