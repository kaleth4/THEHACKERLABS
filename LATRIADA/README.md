<img width="1920" height="1080" alt="¿Cuál es la IP de la víctima_" src="https://github.com/user-attachments/assets/db833a6c-a2ac-40ae-b3dd-8cb20020dc24" /># 🧪 La Tríada del Malware — Incident Response & Network Forensics

[![Security Level](https://shields.io)]()
[![Platform](https://shields.io)]()
[![Analysis Type](https://shields.io)]()

Repositorio dedicado a la documentación, análisis de tráfico y resolución del laboratorio forense **La Tríada del Malware**. El objetivo de este ejercicio es reconstruir de extremo a extremo la cadena de infección de un host corporativo comprometido por tres familias de malware secuenciales: **Hancitor**, **Cobalt Strike** y **Ficker Stealer**.

---

## 🚨 Alerta de Seguridad (Malware Handling)

> [!WARNING]
> Los artefactos y el tráfico analizados en este laboratorio corresponden a muestras reales extraídas *in the wild*. El análisis y extracción de objetos se ejecutaron bajo un entorno controlado de Sandbox y redes virtuales aisladas (*Host-Only*).

---

## 📊 Resumen de la Cadena de Infección

El compromiso del host se estructuró en tres etapas tácticas diferenciadas:
1. **Acceso Inicial (Hancitor):** Descarga maliciosa inicial que actúa como *loader* y balizamiento (beaconing) primario hacia la infraestructura del atacante.
2. **Post-Explotación & Persistencia (Cobalt Strike):** Despliegue de agentes interactivos (*beacons* HTTP/HTTPS) para control remoto avanzado y movimiento lateral.
3. **Exfiltración de Activos (Ficker Stealer):** Ejecución de un *infostealer* diseñado para recolectar credenciales, cookies de sesión, datos de billeteras cripto y exfiltrarlos a un C2 centralizado.

---

## 🔍 Reporte Técnico Forense (Investigación del PCAP)

A continuación se detallan los hallazgos y evidencias extraídas mediante el análisis profundo del flujo de paquetes (`Wireshark` / `Tshark` / `Zeek`).

### 🖥️ 1. Identificación y Perfilado de la Víctima

Para delimitar el alcance del compromiso dentro de la infraestructura interna, se aislaron los datos de identidad del host afectado mediante el tráfico DHCP, Kerberos y NetBIOS:

* **Dirección IP de la Víctima:** `[INSERTA_AQUÍ_LA_IP_DE_LA_VÍCTIMA]`
* <img width="1920" height="1080" alt="¿Cuál es la IP de la víctima_" src="https://github.com/user-attachments/assets/0c50d96b-3eda-4928-9292-42948094425d" />

* **Hostname del Equipo:** `[INSERTA_AQUÍ_EL_HOSTNAME_DE_LA_VÍCTIMA]`
* <img width="1920" height="1080" alt="¿Cuál es el Hostname de la víctima_" src="https://github.com/user-attachments/assets/2a36e90a-a42d-4dfe-b61d-519117883567" />

* **Dirección MAC:** `[INSERTA_AQUÍ_LA_MAC_DE_LA_VÍCTIMA]`
* **Dominio / Cuenta de Usuario de Windows:** `[INSERTA_AQUÍ_EL_USUARIO_O_DOMINIO]` *(Ej: `thehackerslabs.com`)*
<img width="1920" height="1080" alt="¿Cuál es el nombre de la cuenta de usuario de Windows_" src="https://github.com/user-attachments/assets/9fb5b16f-c03d-4485-a2ae-d5a98913058c" />

---

### 🌐 2. Análisis de Reconocimiento y Exfiltración Temprana

Inmediatamente después de la ejecución del artefacto inicial, el malware fuerza al host comprometido a mapear su salida hacia internet:

* **Dominio consultado para determinar la IP pública:** `[INSERTA_AQUÍ_EL_DOMINIO_IP_PÚBLICA]` *(Ej: `api.thehackerslabs.com` / `api.ipify.org`)*

---

### 🦠 3. Infraestructura de Comando y Control (C2)

#### 🔹 Etapa 1: Hancitor (Loader)
Monitoreo de solicitudes `HTTP POST / GET` con estructuras de datos codificadas o peticiones anómalas dirigidas a la infraestructura de comando inicial:
* **Dominio del C2 Principal de Hancitor:** `[INSERTA_AQUÍ_EL_DOMINIO_C2_HANCITOR]`
<img width="1920" height="1080" alt="¿Nombre del ejecutable descargado desde el mismo dominio_ " src="https://github.com/user-attachments/assets/7ff2591b-b572-48ef-b0a9-1d9d95eee3f6" />

#### 🔹 Etapa 2: Cobalt Strike (Lateral Movement & Persistence)
Identificación de la descarga de la segunda etapa mediante tráfico de red y perfiles de balizamiento:
* **Dominio de descarga de la segunda etapa:** `[INSERTA_AQUÍ_EL_DOMINIO_DESCARGA_COBALT]`
* **Nombre del ejecutable descargado:** `[INSERTA_AQUÍ_EL_NOMBRE_DEL_EXE]` *(Ej: `dgadgdg.exe`)*
* **Dirección IP y Puerto del C2 (Primer Beacon - HTTP):** `[INSERTA_IP]:[PUERTO]`
* **Dirección IP y Puerto del C2 (Segundo Beacon - HTTPS):** `[INSERTA_IP]:[PUERTO]`
<img width="1920" height="1080" alt="¿Dirección IP del C2 de Cobalt Strike (primer beacon) y puerto_ Ej_ 192 168 18 55_9000" src="https://github.com/user-attachments/assets/97d0398f-33df-4f00-ae80-41926a42079c" />

#### 🔹 Etapa 3: Ficker Stealer (Data Exfiltration)
Análisis de conexiones TCP/TLS anómalas de alto volumen orientadas a la sustracción de datos confidenciales:
* **Dirección IP del Servidor C2 de Ficker Stealer:** `[INSERTA_AQUÍ_LA_IP_C2_FICKER]`
<img width="1920" height="1080" alt="¿Qué dominio consulta la víctima inmediatamente después para obtener su IP pública_" src="https://github.com/user-attachments/assets/c5ddb108-bd1d-450f-8fcd-0b13e4fba099" />

---

## 🛠️ Metodología de Análisis Recomendada

Para replicar la investigación de este PCAP en tu propia estación forense:
1. **Filtros de Wireshark útiles para Hancitor:**
   ```text
   http.request.method == "POST" || http.request.uri contains ".php"
   ```
2. **Identificación de credenciales de máquina (Windows Auth / Kerberos):**
   ```text
   kerberos.CNameString || nbsns
   ```
3. **Búsqueda de ejecutables descargados vía HTTP:**
   ```text
   http.json or (http.content_type contains "application")
   ```
   *(O a través de `File -> Export Objects -> HTTP`)*

---

## 🎯 Conclusión e Indicadores de Compromiso (IoCs)

Este caso demuestra una infección modular estructurada donde cada actor cumple un rol especializado dentro de la cadena de suministro del cibercrimen (*Malware-as-a-Service*). Los indicadores de compromiso recopilados en este repositorio sirven para alimentar reglas de detección **YARA** y firmas **Suricata/Snort** en sistemas perimetrales.

