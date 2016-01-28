lxc-bridge-nat
==============

- https://wiki.debian.org/LXC/SimpleBridge
- Debian 8.2 Jessie

Issues
------
- /etc/lxc/lxc-usernet 에서 lxc-bridge-nat에 연결가능한 nic 수를 지정해주어야 함. 아니면 Quota reached 에러가 발생
  https://bugs.launchpad.net/ubuntu/+source/lxc/+bug/1470580
- ufw에서 막히고 있음 - /var/log/syslog 참고
  https://bugs.launchpad.net/ubuntu/+source/ufw/+bug/573461
- ufw를 disable 한 상태에서도 안되고 있음 - 브릿지 자체를 테스트 해봐야
