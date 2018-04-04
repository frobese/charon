# Prepping the Image


1. mount with `mount -o loop,offset=48234496 <IMG> <TAGET>`  
offset is calculated by using `fdisk -l <IMG>` and then `SECTOR_SIZE * START`
1. place `charon_init.sh` and `charon_sync.sh` into `<TARGET>/usr`
1. under `<TARGET>/etc`:  
    * place `z21_persistent-local.rules` into `./udev/rules.d/`
    * place `charon-sync.service` into `./systemd/system/`
    * edit `rc.local` to run the `charon_init.sh`
1. umount with `umount <TARGET>`