#!/bin/bash
#CLI installer for the rasberry image

DEVS="$(blkid /dev/sd* | awk '{ match($0,/^\/dev\/sd.[1-9]/) ; print substr($0, RSTART, RLENGTH) }' | grep -v '^$')"

(ls /mnt/usb || mkdir /mnt/usb)

FILES=("charon.cfg" "charon_signature.txt")
for DEV in $DEVS; do
	mount $DEV /mnt/usb 
	if [ $? -eq 0 ]; then
        for FILE in "${FILES[@]}"; do 
            cp /mnt/usb/$FILE /root/$FILE
        done
        cp /var/log/charon.* /mnt/usb
    fi
	umount $DEV
done