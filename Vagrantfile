# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "ubuntu/trusty64"

  config.vm.hostname = "mosaicme-vm"

  config.vm.synced_folder ".", "/home/vagrant/mosaicme"

  config.vm.provider "virtualbox" do |vb|
    vb.memory = "1024"
  end

  config.vm.provision "file", source: "requirements.txt", destination: "/tmp/requirements.txt"

  config.vm.provision :puppet do |puppet|
    puppet.manifests_path = "puppet/manifests"
    puppet.module_path = 'puppet/modules'
  end
end
