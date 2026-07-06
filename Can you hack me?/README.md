# 💀 [ Write-Up ] — Operación: Can You Hack Me 💀
**Target IP:** `192.168.0.3`  
**Host Asociado:** `canyouhackme.thl`  
**Dificultad:** Media/Baja  
**Objetivo:** Compromiso total del sistema (Root Access)  

---

## 🛰️ 1. Fase de Reconocimiento y Descubrimiento de Activos

El despliegue operativo comenzó con el mapeo del espectro de red de la víctima. Para maximizar la eficiencia y evitar el ruido innecesario, se ejecutó un escaneo inicial agresivo sobre la totalidad del rango de puertos TCP (`1-65535`).

```bash
nmap -sVC -p- -n --min-rate 5000 192.168.0.3
```

### 🔬 Análisis del Vector de Ataque Superficial
El escaneo de alta velocidad reveló vectores críticos expuestos en la capa de transporte:
*   **Port 22/TCP**: `Open` -> Servicio SSH (Potencial vector de intrusión/persistencia).
*   **Port 80/TCP**: `Open` -> Servicio HTTP (Superficie de ataque web para enumeración).

Para profundizar en la telemetría de las versiones y extraer las firmas exactas de los daemons concurrentes, se dirigió un escaneo quirúrgico y detallado:

```bash
sudo nmap -sCV -p21,22,80 -v 192.168.0.3
```

---

## 🔎 2. Auditoría Web e Inteligencia de Fuentes Abiertas (OSINT)

Con el puerto `80` identificado como el vector de entrada más viable, se procedió a la fase de **Virtual Host Routing**. Antes de interactuar con el backend web, se modificó el mapa de resolución local en `/etc/hosts` para interceptar correctamente las peticiones dirigidas al dominio interno:

```bash
echo "192.168.0.3 canyouhackme.thl" | sudo tee -a /etc/hosts
```

### 🕸️ Análisis Estático del Código Fuente
Al auditar el código fuente del aplicativo web (`http://canyouhackme.thl`), se realizó el hallazgo de una fuga de información (**Information Leakage**). Los desarrolladores dejaron un comentario residual en el HTML exponiendo una cadena de texto crítica:

*   **Identidad comprometida:** `juan` (Usuario válido del sistema).

Con una identidad de sistema confirmada y el puerto `22` abierto, el vector estratégico mutó inmediatamente hacia un ataque de fuerza bruta dirigido sobre el protocolo criptográfico SSH.

---

## 🚀 3. Intrusión y Explotación (Acceso Inicial)

Para quebrar el mecanismo de autenticación del usuario objetivo, se orquestó un ataque de diccionario de alta velocidad utilizando el motor de fuerza bruta **Hydra**, alimentado con el set de contraseñas de la lista `rockyou.txt`.

```bash
hydra -l juan -P /usr/share/wordlists/rockyou.txt ssh://192.168.0.3
```

El ataque de diccionario comprometió exitosamente el backend de autenticación, **extrayendo la contraseña en texto plano** para el operador detectado. Con las credenciales comprometidas en nuestro poder, se procedió a la apertura de un canal seguro interactivo por SSH:

```bash
ssh juan@192.168.0.3
```

**¡Acceso Inicial Consolidado!** Hemos vulnerado el perímetro y establecido un punto de apoyo estable en el host de la víctima bajo el contexto del usuario `juan`.

---

## 🔐 4. Post-Explotación y Escalada de Privilegios (Root)

Una vez dentro de la terminal, el objetivo prioritario cambió a la **elevación vertical de privilegios**. El comando `whoami` confirmó nuestro estado actual como un usuario de bajos privilegios.

### 🕵️‍♂️ Enumeración Interna del Sistema
Se ejecutaron rutinas de auditoría estándar para buscar malas configuraciones:
1.  **Sudoers Check:** `sudo -l` devolvió una restricción total; el usuario no tiene permisos sudo asignados.
2.  **Binarios SUID y Linux Capabilities:** Se ejecutó un pipeline automatizado para auditar vectores SUID y capacidades especiales en el sistema de archivos:
    ```bash
    find / -perm -4000 -user root 2>/dev/null -o -type f -exec getcap {} \; 2>/dev/null
    ```
    *Resultado:* Negativo. Ningún binario nativo explotable mediante técnicas clásicas de GTFOBins.

3.  **Análisis de Grupos de Seguridad (Vector Crítico):** Al inspeccionar los grupos a los que pertenece la identidad actual (`groups`), se identificó una configuración deficiente de alto impacto: **El usuario `juan` es miembro del grupo `docker`**.

### 🐳 Explotación del Unix Socket de Docker
Estar dentro del grupo `docker` equivale implícitamente a poseer privilegios de Root, ya que permite interactuar de forma directa con el socket de control de la API de Docker (`docker.sock`).

Se localizó el socket activo en el sistema:
```bash
find / -name docker.sock 2>/dev/null
```

Posteriormente, se listaron las imágenes almacenadas localmente para utilizarlas como entorno de sandbox:
```bash
docker images
```
*   **Imagen disponible:** `alpine` (Entorno minimalista ideal para la fuga).

### ⚡ Ejecución del Vector de Escape y Chroot (Pwned!)
Para romper los límites del contenedor y tomar el control del sistema operativo anfitrión, se lanzó un contenedor de Alpine montando la raíz del disco duro del host (`/`) directamente dentro del directorio `/host` del contenedor. Acto seguido, se utilizó `chroot` para alterar el entorno de ejecución del root del sistema de archivos hacia la montura del anfitrión:

```bash
docker run -it -v /:/host/ alpine chroot /host/ bash
```

### 🎯 Compromiso Total del Sistema
Al ejecutarse el escape, los privilegios del contenedor se reflejaron directamente sobre el sistema de archivos padre.

```bash
whoami
# Output: root
```

**Sistema comprometido al 100%. Acceso completo como ROOT garantizado.**
