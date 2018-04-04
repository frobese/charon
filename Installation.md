# Charon Installation
## Vorraussetzungen
Für den Betrieb wird benötigt:

+ Raspberry Pi 3
+ micro-SD-Karte mit 8GB oder mehr
+ kompatibles SD-Lesegerät
+ micro-USB Netzteil

## Installation
1. Die SD Karte muss mit dem bereitgestellten `charon-*.img` versehen werden, Anleitungen unter:      
[Linux](https://www.raspberrypi.org/documentation/installation/installing-images/linux.md)  
[MacOS](https://www.raspberrypi.org/documentation/installation/installing-images/mac.md)  
[Windows](https://www.raspberrypi.org/documentation/installation/installing-images/windows.md)  

1. **SD-Karte** in den Raspberry einsetzen und mit **Ethernet** verbinden.  
*(Hinweis) Ohne Internetzugang kann die Anwendung nicht installiert werden*
1. Raspberry via micro-USB mit dem Strom verbinden.  
Eine Grüne LED sollte nun aufleuchten, falls nicht wiederholen Sie Schritt 1.  
Der Raspberry bootet nun.
1. Konfiguration und Signatur einspielen.  
    Beim Einstecken eines USB-Sticks in den laufenden Raspberry-Pi werden Konfiguration und Signatur kopiert, wenn diese unter den Namen `charon.cfg` und `charon_signature.txt` auf dem Stick vorhanden sind.  
    Außerdem werden alle vorhandenen Logs auf den Stick kopiert.

    Folgende Optionen sind für den Einsatz relevant:  
    `reply_to` die hier aufgeführte E-Mail-Adresse wird im *Antwort An*-Feld der Mails verwendet.   
    `origin` die hier aufgeführte E-Mail-Adresse wird im *Absender*-Feld der Mails verwendet.  
    `report_recipients` die hier aufgeführten, durch Komma getrennten, Adressen erhalten einen Bericht über die verarbeiteten E-Mails.

    `positive_box` E-Mails, die zugeordnet werden konnten, werden im Mailpostfach in den hier angegebenen Ordner verschoben.  
    `negative_box` E-Mails, die *nicht* zugeordnet werden konnten, werden im Mailpostfach in den hier angegebenen Ordner verschoben.  

    Nach Anpassung der im `[Mail]`-Segment aufgeführten IMAP und SMTP Einstellungen ist Charon betriebsfertig.

1. Charon wird nun jede Viertelstunde mit der bereitgestellten Konfiguration ausgeführt.