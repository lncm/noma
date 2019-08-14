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
  config.vm.box = "generic/alpine310"
  config.vm.hostname = "alpine-vagrant"
  config.vm.synced_folder ".", "/vagrant",
                          type: "nfs",
                          nfs_export: true
  config.vm.network "private_network", ip: "192.168.83.33"
  config.vm.provision "shell", inline: "cd /vagrant && ./install.sh"
end
