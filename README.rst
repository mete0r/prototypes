unprivileged LXC container in Debian Jessie
===========================================

http://myles.sh/configuring-lxc-unprivileged-containers-in-debian-jessie/

Requirements
------------

:lxc: 1:1.0.6-6+deb8u1
:cgroup-tools: 0.41-6
:uidmap: 1:4.2-3
:linux-image-3.16.0-4-amd64: 3.16.7-ckt11-1+deb8u3
:systemd: 215-17+deb8u2


Usage
-----

Run following as root::

   $ sudo python bootstrap-buildout.py
   $ sudo bin/buildout


Note
----
