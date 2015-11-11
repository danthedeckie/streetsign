Deploying Streetsign in Production
==================================

How to deploy a 'production-ready' streetsign installation.

Dependencies
------------

First you need to install the python headers (for compiling some extra modules),
imagemagick (to generate thumbnails), and pip for installing other python modules,
and git for downloading streetsign itself.

On Debian/Ubuntu Server, this will be something like ::

    sudo apt-get install python-pip python-dev imagemagick git

User/Group
----------

Streetsign, as every other service, should really run as it's own user, for
security's sake ::

    sudo useradd streetsign

Which will also create a new group for it.

Installation path
-----------------

As per the LSB, probably the best place for public facing services to install their
data is ``/srv/``.  So we should create that directory, and install streetsign there::

    sudo mkdir /srv/streetsign
    sudo chown -R streetsign:streetsign /srv/streetsign

Actually Installing it
----------------------

We'll use git to get the latest version, and set it up as normal::

    cd /srv/streetsign
    sudo su streetsign
    git clone https://bitbucket.org/dfairhead/streetsign-server.git .
    ./setup.sh

Test it's all ready to go
-------------------------

This step is technically un-needed, but probably a good idea.  While still ``su``'d as
streetsign::

    ./run.py waitress

and then from a web browser, browse to that server's IP at port 5000.  If you don't know
the server IP::

    ifconfig |grep 'inet addr:'

And then you can ``exit`` from the streetsign user.

Configure streetsign to start on system-boot
--------------------------------------------

Unfortunately, this is different on practically every linux distribution, and even different
between Ubuntu 14 and Ubuntu 15, for instance.

There are startup files in the streetsign source, in the ``deployment`` folder.

systemd systems (Ubuntu 15.x, Debian Jessie, etc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

If you're on a systemd based linux (Such as Ubuntu 15.x),
then copy the ``deployment/systemd/streetsign.service`` file to ``/var/systemd/system``,
edit it to make sure it's all correct for your system (which it should be, if you've followed
the above instructions).::

    sudo cp /etc/streetsign/deployment/systemd/streetsign.service /var/systemd/system/

And then tell enable the service.::

    sudo systemctl enable streetsign

And then you can actually start it up::

    sudo systemctl start streetsign

If it's all running quite happily, then cool.  If you want to test that it does actually start on
boot, feel free to reboot the server and see what happens.

upstartd systems (Ubuntu 14.x, etc)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Copy the streetsign upstart configuration file to ``/etc/init``::

    sudo cp /srv/streetsign/deployment/upstart/streetsign.conf /etc/init/

And then you should edit /etc/init/streetsign.conf to make sure it's all correct for your system.
If you've followed the above instructions, then it should be.

You can now start the service, to test it's all working OK::

    sudo start streetsign

And it should automatically run on boot as well.  To stop that, you can edit the
``/etc/init/streetsign.conf`` file, and put a ``#`` in front of ``start on runlevel [2345]``.


System-V (initscript) Systems
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

TODO

Getting Streetsign on to Port 80
--------------------------------

If streetsign is going to be 'public facing', and so you want it to be running on the regular
HTTP port 80, or over HTTPS, then it's best to run a 'reverse proxy' in front of it.

The most popular options are Apache and NGiNX.

Apache
~~~~~~

Apache is pretty easy to install::

    sudo apt-get install apache2

is usually enough.  There's a default configuration file to put streetsign on its own
virtualhost in the ``deployment/apache`` folder.  If streetsign is the only site running behind
apache here, then that configuration file may be enough.  Usually, however, you'll need to
modify the VirtualHost / Server Name / other settings a bit yourself.

You will need the apache ``mod_proxy``  and ``proxy_http`` modules enabled::

    sudo a2enmod proxy proxy_http

You can then copy in the config file::

    sudo cp /srv/streetsign/deployment/apache/streetsign.conf /etc/apache2/sites-available/

Edit it to have the settings you need, and enable it::

    sudo a2ensite streetsign

And if you want to, disable the default apache welcome-page/site::

    sudo a2dissite 000-default

Finally, restart apache::

    sudo service apache2 restart

and it should all be working.

nginx
~~~~~

Install nginx::

    sudo apt-get install nginx

copy the basic streetsign configuration file in::

    sudo cp /srv/streetsign/deployment/nginx/streetsign /etc/nginx/sites-available/

Edit it with whatever settings you wish.

Enable it::

    sudo ln -s /etc/nginx/sites-available/streetsign /etc/nginx/sites-enabled/

And if streetsign is the only thing you're using nginx for, and you don't need
the default welcome page, turn that off::

    sudo rm /etc/nginx/sites-enabled/default

And of course, restart nginx::

    sudo service nginx restart
