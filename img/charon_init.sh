#!/bin/bash
#CLI installer for the rasberry image

apt-get install -q -y python3.5 python3-pip git

if [ $? -eq 0 ]; then
    charon_vers=(`cat /CHARON_VERS`)
    pip3 install git+https://github.com/frobese/charon.git@$charon_vers
    if [ $? -eq 0 ]; then
        cron_cmd=(`which charon`)
        cronjob="*/15 * * * * $cron_cmd >> /var/log/charon.log 2>&1"
        ( crontab -l | grep -v -F "$cron_cmd" ; echo "$cronjob" ) | crontab -

        updater="20 0 * * 0 /sbin/shutdown -r \"now\""
        ( crontab -l | grep -v -F "shutdown" ; echo "$updater" ) | crontab -
    fi
fi