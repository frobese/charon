# Charon Installation
## Vorraussetzungen
Für den Betrieb wird benötigt:

+ Raspberry Pi 3
+ micro-SD-Karte mit 8GB oder mehr
+ kompatibles SD-Lesegerät
+ micro-USB Netzteil

Für die Installation wird außerdem benötigt:

+ HDMI fähiger Bildschirm
+ USB-Tastatur

## Installation
1. Die SD Karte muss mit dem bereitgestellten `charon-*.img` versehen werden, Anleitungen unter:      
[Linux](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)  
[MacOS](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)  
[Windows](https://www.raspberrypi.org/documentation/installation/installing-images/windows.md)  

1. Raspberry mit **SD-Karte**, **Tastatur**, **Bildschirm** (HDMI) und **Ethernet** verbinden.  
*(Hinweis) Ohne Internetzugang kann die Anwendung nicht installiert werden*
1. Raspberry via micro-USB mit dem Strom verbinden.  
Eine Grüne LED sollte nun aufleuchten, falls nicht wiederholen Sie Schritt 1.  
Der Raspberry bootet nun.
1. Ist der Bootvorgang beendet ist es möglich sich am System an zu melden:  
**Nutzer:**  
pi  
**Passwort:**  
raspberry  
*(Hinweis) Das Betreibssystem geht von einer QUERTY-Tastatur aus: **y** und **z** sind also vertauscht*
1. *(Optional)* Das Keyboard-Layout kann wie folgt angepasst werden: 

        sudo dpkg-reconfigure console-setup

1. War das Betriebssystem in der Lage Charon zu installieren liefert

        charon -h

    in etwa diese Ausgabe:

        usage: charon [-h] [-d] [--crconf] [-s] [--diff] [-l PATH]

        IMAP/STMP script handling absence messages, commands marked with [DEBUG]
        trigger the debug mode

        optional arguments:
            -h, --help  show this help message and exit
            -d          run the script in debug mode
            --crconf    create conf in user homedir
            -s          [DEBUG] steps each mail
            --diff      [DEBUG] only shows wrongly assigned mails from matched or
                        unmachted
            -l PATH     loads mails from PATH, send mails are displayed

1. *(Optional)* E-Mail-Signatur erstellen mit:

        sudo nano /root/footer.txt

1. Eine Standartkonfiguration wird mit 

        sudo charon --crconf
    
    erzeugt. Diese kann nun mit

        sudo nano /root/.charon.cfg

    editiert werden.
    
    `keep_attachment` ist dieser Wert *True* wird der erste gefundene PDF-Anhang weitergeleitet.  
    `reply_to` die hier aufgeführte E-Mail-Adresse wird im *Antwort An*-Feld der Mails verwendet.   
    `origin` die hier aufgeführte E-Mail-Adresse wird im *Absender*-Feld der Mails verwendet.  
    `report_recipients` die hier aufgeführten, durch Komma getrennten, Adressen erhalten einen Bericht über die verarbeiteten E-Mails.  
    `footer_path` Pfad zur Signatur im Normalfall `/root/footer.txt`.

    Nach Anpassung der im [Mail]-Segment aufgeführten IMAP und SMTP Einstellungen ist Charon betriebsfertig.

1. Charon wird nun jede Viertelstunde mit der bereitgestellten Konfiguration ausgeführt.  
Das System kann mit `sudo shutdown now` heruntergefahren werden.  
Für den tatsächlichen betrieb können Tastatur und Bildschirm getrennt werden.