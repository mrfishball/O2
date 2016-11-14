***Test Case 1 (Email confirmed and with admin access)***
Email: test@gmail.com
Password: test123

***Test Case 2 (Unconfirmed email and admin access blocked)***
Email: test2@gmail.com	
Password: test123

***All accounts created will be set unconfirmed by default***

------------------------------------------------------------------------>

Change log / Bugfix

-FIXED Where users can edit and delete posts that don't belong to them.
-FIXED Default login page routed correctly.

-NEW Posts section renamed to Topics with "Trending now" as page title.
-NEW Improve how entries are displayed in the Topics page. Viewers can 
now see the name of the author as well as a small section of the entry.
-NEW Improved user profile page.
-NEW Google+ and Facebook integration. Users can now login with either service.

----------------------------------------------------------------------->

Downloads and install

-Vagrant -http://vagrantup.com/
-VirtualBox -https://www.virtualbox.org/
-Git -https://git-scm.com/

How-to

-Run git bash
-cd into the vagrant path for example. cd /c/users/user_name/fullstack/vagrant
-Run the Vagrant VM in the terminal using the command vagrant up followed by vagrant ssh
-Execute cd /vagrant/catalog to change directory to the sync folders.
-Execute python run.py
-Navigate to localhost:5000 in any broswer.

Hope you like it! :)