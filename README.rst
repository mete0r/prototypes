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


Install Wheezy, then upgrade to Jessie
--------------------------------------

1. Install wheezy::

      $ lxc-create -n MYCONT -t lxc-download -- --dist debian --release wheezy --arch amd64
      $ lxc-start -n MYCONT

2. On other terminal, change root passwd::

      $ lxc-attach -n MYCONT -- bash -l
      MYCONT:$ passwd

3. Change the container's ``/etc/apt/sources.list`` to point jessie repositories, i.e.::

      deb http://ftp.kr.debian.org/debian/ jessie main non-free contrib

4. Upgrade to jessie::

      MYCONT:$ apt-get update
      MYCONT $ apt-get dist-upgrade sysvinit-core

5. To avoid login failure with 'cannot make/remove an entry for the specified session', disable pam_loginuid::

      MYCONT $ sed -ri 's/^session\s+required\s+pam_loginuid.so$/session optional pam_loginuid.so/' /etc/pam.d/*

6. Try login::

      $ lxc-console -n MYCONT


For pam_loginuid problem:

https://github.com/docker/docker/issues/5663
https://bugzilla.redhat.com/show_bug.cgi?id=893751
