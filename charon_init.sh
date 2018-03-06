#!/bin/bash
#CLI installer for the rasberry image

apt-get install -q -y python3.5 python3-pip

if [ $? -eq 0 ]; then
    pip3 install git+https://github.com/frobese/charon.git@1.5.x
    if [ $? -eq 0 ]; then
        cron_cmd=(`which charon`)
        cronjob="* * * * */1 $cron_cmd >> /var/log/charon.log 2>&1"
        
        ( crontab -l | grep -v -F "$cron_cmd" ; echo "$cronjob" ) | crontab -
    fi
fi