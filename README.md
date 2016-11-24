# O2 - A catalog application

## Description

A social media blog made with Python and Flask.

## Version 2.0 (change log / bugfix)

- NEW Posts section renamed to Topics with "Trending now" as page title.
- NEW Improve how entries are displayed in the Topics page. Viewers can 
  now see the name of the author as well as a small section of the entry.
- NEW Improved user profile page.
- NEW Google+ and Facebook integration. Users can now login with either service.

- FIXED Where users can edit and delete posts that don't belong to them.
- FIXED Default login page routed correctly.

## Local Run (Prerequisites & Instructions)
### Download:
- Vagrant (https://www.vagrantup.com/downloads.html) then setup (https://www.vagrantup.com/docs/getting-started/)
- Text Editor (ex. Sublime (https://www.sublimetext.com/3) or Atom (https://atom.io/))
- VirtualBox -https://www.virtualbox.org/
- Git -https://git-scm.com/

### 1 - Change port forwarding setting for Vagrantfile.

1. Edit the `Vagrantfile` in the same directory as the `.vagrant` folder with a text editor.
2. Forward guest port 5000 to host 5555 (Must change port for Google / Facebook login to work as they both check for point of origin):

```Ruby
# -*- mode: ruby -*-
# vi: set ft=ruby :

VAGRANTFILE_API_VERSION = "2"

Vagrant.configure(VAGRANTFILE_API_VERSION) do |config|
  config.vm.provision "shell", path: "pg_config.sh"
  # config.vm.box = "hashicorp/precise32"
  config.vm.box = "ubuntu/trusty32"
  # config.vm.network "forwarded_port", guest: 8000, host: 8888
  # config.vm.network "forwarded_port", guest: 8080, host: 8088
  config.vm.network "forwarded_port", guest: 5000, host: 5555
end
```
### 2 - Install project dependencies

1. Run `git bash' and cd ino the vagrant directory.
2. Initialize vagrant with 'vagrant up and login with `vagrant ssh'.
3. cd into the project directory and install pip with command `sudo easy_install pip`.
4. Run `sudo pip install -r requirements.txt`.

### 3 - Create new database

1. Run `python create_db.py`.

### 4 - Running the app

1. Run `python run.py`.
2. App is running on debug mode on port 5000 (5555 for host).
3. Navegate to localhost:5555 in your broswer to see the app running.

### EXTRA

*You must use your own oauth credentials(client ID, client secret) that you obtained from your providers, then modify the config.py with your own credentials.