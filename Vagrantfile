$script = <<SCRIPT
sudo apt update
sudo apt install python3-pip -y
sudo apt-get install libpq-dev python3-dev -y
sudo apt install python3-tk -y gnome-terminal
sudo apt-get install xauth -y
sudo apt-get install x11-apps -y
sudo pip3 install -r /vagrant/requirements.txt
SCRIPT


$addaliases = <<SCRIPT
    if ! cat /home/vagrant/.bashrc | grep "alias createdb"; then
        echo "alias createdb='docker exec -it mydb createdb -U postgres'" >> /home/vagrant/.bashrc
    fi
    if ! cat /home/vagrant/.bashrc | grep "alias dropdb"; then
        echo "alias dropdb='docker exec -it mydb dropdb -U postgres'" >> /home/vagrant/.bashrc
    fi
    if ! cat /home/vagrant/.bashrc | grep "alias psql"; then
        echo "alias psql='docker exec -it mydb psql -U postgres'" >> /home/vagrant/.bashrc
    fi
    if ! cat /home/vagrant/.bashrc | grep "PYTHONPATH"; then
        echo "export PYTHONPATH=/" >> /home/vagrant/.bashrc
    fi
    if ! cat /home/vagrant/.bashrc | grep "alias nv"; then
        echo "alias nv='/cogni_scan/front_end/nifti_viewer.py'" >> /home/vagrant/.bashrc
    fi
    if ! cat /home/vagrant/.bashrc | grep "alias updatedb"; then
        echo "alias updatedb='/cogni_scan/db/update-docker.sh'" >> /home/vagrant/.bashrc
    fi
SCRIPT


$create_settings = <<SCRIPT
    mkdir -p /home/vagrant/.cogni_scan
    if [ ! -f "/home/vagrant/.cogni_scan/settings.json" ]; then
        echo "{" >> /home/vagrant/.cogni_scan/settings.json
        echo '    "CONN_STR": "postgresql://postgres:postgres@localhost:5433/scans" ' >> /home/vagrant/.cogni_scan/settings.json
        echo "}" >> /home/vagrant/.cogni_scan/settings.json
    fi
SCRIPT


Vagrant.configure("2") do |config|
  config.vm.box = "bento/ubuntu-20.04"
  config.vm.synced_folder "./", "/cogni_scan/"
  config.vm.synced_folder "~/nifti-files",  "/cogni_scan/shared"
  config.ssh.forward_agent = true
  config.ssh.forward_x11 = true
  config.vm.provision "shell", inline: $script
  config.vm.provision "shell", inline: $addaliases
  config.vm.provision "shell", inline: $create_settings
  config.vm.provider "virtualbox" do |vb|
    vb.name = "CogniScan"
  end
  config.vm.provision "docker" do |d|
    d.pull_images "postgres"
    d.run "postgres", args: "-p 5433:5432 -e POSTGRES_PASSWORD=postgres --name mydb -d postgres"
  end
end

