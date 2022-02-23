#!/bin/sh
# set ftp user password

echo "${USER_NAME}:${USER_PASS}" |/usr/sbin/chpasswd
chown "${USER_NAME}:${USER_NAME}" "/${USER_NAME}/" -R

if [ -z "$1" ]; then
  /usr/sbin/vsftpd /etc/vsftpd/vsftpd.conf
else
  "$@"
fi
