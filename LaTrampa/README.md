
# 🚨 **CTF: La Trampa - The Hackers Labs**
## **Writeup & Análisis de Red**

---

**La Trampa** es un laboratorio técnico de la plataforma **The Hackers Labs** enfocado en **Ciberseguridad Defensiva**, **Análisis de Tráfico Forense** y **Blue Teaming**. A diferencia de los entornos CTF tradicionales de intrusión, este reto sitúa al analista ante un archivo de captura de red (`pcap`) donde se debe desentrañar un **incidente de seguridad previo** o una **comunicación sospechosa**.

---

## 📊 **Ficha Técnica del Laboratorio**

| **Categoría**       | **DFIR / Análisis de Tráfico / Wireshark**       |
|---------------------|--------------------------------------------------|
| **Plataforma**      | The Hackers Labs                                |
| **Dificultad**      | Media                                            |
| **Objetivo Principal** | Analizar `La_Trampa.pcap` para identificar:     |
|                     | ✅ Anomalías en el tráfico.                      |
|                     | ✅ Extraer dominios maliciosos (ej: `www`).       |
|                     | ✅ Descubrir exfiltración de información.         |

---

## 🛠️ **Herramientas Utilizadas**

- **Wireshark**: Interfaz gráfica para inspección profunda de paquetes.
- **Tshark**: Motor de Wireshark por línea de comandos para automatización.
- **Herramientas CLI de Linux**: `strings`, `grep`, `sort`, `sed`.

---

## 🚀 **Guía de Resolución y Comandos Esenciales**

### 1️⃣ **Extracción de Dominios de Confianza (`www`)**
El análisis automatizado del tráfico web y las solicitudes DNS requiere evadir la lectura de binarios corruptos. Para extraer dominios únicos de forma limpia desde la terminal:

```bash
tshark -r La_Trampa.pcap -Y "http.host contains www" -T fields -e http.host | sort -u
```
⚠️ **Usa el código con precaución.**

---

### 🔍 **Preguntas Clave y Respuestas**

#### **1. ¿Cuál es la dirección IP del cliente de Windows infectado?**
📌 **Respuesta:** Busca en los paquetes **DNS de tipo "Standard Query"** (consultas DNS estándar) donde aparezca la IP del cliente infectado.
Ejemplo de comando para filtrar:
```bash
tshark -r La_Trampa.pcap -Y "dns.flags.response == 0 && dns.qry.type == 1" -T fields -e ip.dst
```

---

#### **2. ¿Cuál es la dirección MAC del cliente de Windows infectado?**
📌 **Respuesta:** Busca en cualquier sección donde aparezca la **IP del cliente infectado** (ej: en paquetes ARP o DNS). La MAC suele estar en el campo `eth.src` o `arp.src.hw_mac`.
Ejemplo:
```bash
tshark -r La_Trampa.pcap -Y "ip.addr == <IP_DEL_CLIENTE>" -T fields -e eth.src
```

---

#### **3. ¿Cuál es el nombre de host del cliente de Windows infectado?**
📌 **Respuesta:** Busca paquetes con **`packet length == 92 bytes`** (primer paquete de negociación TCP). El nombre de host suele aparecer en el campo **`http.host`** o en consultas **NetBIOS**.
Ejemplo:
```bash
tshark -r La_Trampa.pcap -Y "tcp.len == 92" -T fields -e http.host
```
🔹 **Formato esperado:** Ej: `DESKTOP-THL`.

---

#### **4. ¿Cuál es el sitio web sospechoso? (Cuidado: Hay redirección)**
📌 **Respuesta:** Usa `strings` para limpiar el binario y extraer texto legible. Luego, filtra dominios sospechosos (ej: `.com`, `.com0` repetidos).
Ejemplo:
```bash
strings La_Trampa.pcap | grep -E "\.(com|net|org)" | sort -u
```
la que use:
```bash
strings La_Trampa.pcap | grep "www" | sort -u
```
🔹 **Formato esperado:** Ej: `www.thehackerslabs.com` (cuidado con redirecciones).

---

<img width="1920" height="1080" alt="1" src="https://github.com/user-attachments/assets/fa59ac13-19ba-4d19-ae0b-9580a415df7c" />
<img width="1920" height="1080" alt="4" src="https://github.com/user-attachments/assets/15e807db-f3d6-45d7-b7f9-6b2aa27b9ff0" />
<img width="1920" height="1080" alt="3" src="https://github.com/user-attachments/assets/a7b9f3e4-931e-4a52-9dab-2b7ae7963331" />
