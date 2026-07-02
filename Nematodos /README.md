
# Reporte de Análisis Forense: Máquina Nematodos

## 📊 Información General
* **Categoría:** Forense
* **Puntos:** 20 / 4.0
* **Dificultad:** Definida por los usuarios

---

## 🎯 Objetivos de Aprendizaje
* **Análisis de tráfico de red (PCAP):** Identificación de hosts infectados y patrones de comunicación anómalos.
* **Identificación de activos:** Extracción de direcciones IP y MAC de la víctima mediante tráfico ARP y conexiones salientes.
* **Descubrimiento pasivo en Windows:** Inspección de protocolos NBNS, LLMNR y Kerberos (TGS-REP) para hallar el Hostname y cuentas de usuario.
* **Detección de amenazas web:** Análisis de consultas DNS y tráfico HTTP/HTTPS para identificar dominios maliciosos y técnicas de *Typosquatting*.
* **Análisis de infraestructura comprometida:** Identificación de sitios web legítimos vulnerados y usados como intermediarios o *redirectors*.
* **Análisis de C2:** Detección de canales de Comando y Control (C2) y exfiltración de datos en tráfico cifrado (TLS/HTTPS).
* **Inteligencia de Amenazas:** Correlación de Indicadores de Compromiso (IOCs) con herramientas como VirusTotal y Urlscan.io para confirmar la presencia de *NetSupport RAT*.
* **Reconstrucción del ataque:** Trazabilidad de la cadena de infección desde la redirección inicial hasta el compromiso final.

---

## 🔍 Resolución del Cuestionario

### 1. ¿Cuál es la dirección IP del host infectado?
* **Respuesta:** `10.11.26.183`
* **Metodología:** Es la dirección IP local utilizada por el equipo de la víctima durante el intercambio de tráfico malicioso. Se logró identificar analizando el volumen y comportamiento de las conexiones salientes hacia servicios HTTP y consultas DNS.
<img width="1920" height="1044" alt="¿Cuál es la dirección IP del host infectado_" src="https://github.com/user-attachments/assets/772a202a-5568-4748-811e-0da8abafbdc2" />

### 2. ¿Cuál es la dirección MAC de la víctima?
* **Metodología:** Para verificar la dirección física (MAC) de origen del host infectado, se aplicaron filtros combinados en Wireshark (`eth.src` e `ip.src`). Posteriormente, se inspeccionó la cabecera de las tramas Ethernet en los paquetes enviados por la IP de la víctima para extraer la dirección MAC correspondiente.
<img width="1920" height="1039" alt="Cual es la mac_" src="https://github.com/user-attachments/assets/86f6cd27-b2cb-4081-a064-bf5833189a35" />

### 3. ¿Cuál es el HostName del equipo de la víctima?
* **Metodología:** Recuperado mediante la inspección de paquetes del protocolo **LLMNR** (Link-Local Multicast Name Resolution). Se analizaron las solicitudes de transmisión (*Queries*) donde el sistema operativo de la víctima anuncia activamente su propio nombre en la red local.
<img width="1920" height="1047" alt="¿Cuál es el HostName del equipo de la victima2" src="https://github.com/user-attachments/assets/cbd4a61e-ff87-41dd-bf60-a289bec7fbaa" />

### 4. ¿Cuál es el nombre de la cuenta del usuario de Windows infectado?
* **Metodología:** El nombre de la cuenta se obtuvo revisando de manera detallada los mensajes del protocolo **Kerberos**, específicamente en las respuestas **TGS-REP** (Ticket Granting Service Reply). Dentro de estas estructuras, se aisló el campo `CNameString`, el cual reveló de forma explícita el nombre de usuario de la sesión de Windows activa.

### 5. ¿Cuál es el dominio malicioso usado en la infección (FakeUpdate/ZPHP)?
* **Indicadores clave:**
  * Dominio con patrón tipo `mod/cracked`, comportamiento típico de sitios web que distribuyen malware o cargas útiles (*payloads*) camufladas como aplicaciones o software crackeado legítimo.
  * Clasificado directamente por **VirusTotal** dentro de las categorías de *phishing* y *malicious*.
  * No cuenta con ninguna relación ni correspondencia con servicios legítimos del sistema operativo.
  * La víctima realiza consultas DNS hacia este dominio momentos antes de iniciar las conexiones HTTP sospechosas.

### 6. ¿Cuál es el sitio probablemente compromised (comprometido)?
* **Metodología:** Identificación del dominio que, a diferencia del host malicioso original, corresponde a un sitio legítimo que fue explotado por los atacantes para actuar como intermediario o pivote de redirección en la cadena de infección.

### 7. ¿Cuál es la IP y URL del C2 del malware?
* **Evidencia Técnica (Paquete Clave):**
  * **Frame:** 20340
  * **Hora:** 04:50:45
  * **IP Origen (Víctima):** `10.11.26.183`
  * **IP Destino (Atacante):** `194.180.191.64`
  * **Protocolo:** HTTPS (Puerto 443) / HTTP encapsulado
  * **Método:** `POST`
  * **Contenido (Content-Type):** `application/x-www-form-urlencoded`
  * **URI:** `http://194.180.191.64/fakeurl.htm`
<img width="1920" height="1042" alt="Cual es la ip del malware" src="https://github.com/user-attachments/assets/4495751c-207a-486e-b5e1-3e38d96d1c9c" />

---

## 🚨 Importancia del Análisis del Paquete Post (C2)

Este paquete en específico representa el **Indicador de Compromiso (IOC) #1** y es el punto más crítico de la investigación debido a las siguientes razones:

1. **Comunicación Activa del RAT:** Este método `POST` expone la baliza (*beacon*) o comunicación directa del malware **NetSupport RAT** reportándose con el servidor del atacante.
2. **Exfiltración Cifrada:** El uso de HTTPS (Puerto 443) garantiza que los datos que viajan hacia el servidor externo lo hagan de forma cifrada, dificultando la inspección directa del contenido del formulario sin el uso de llaves de descifrado o certificados intermedios.
3. **Firma de la Campaña:** El recurso específico `/fakeurl.htm` es un artefacto y patrón de URL ampliamente documentado y asociado a las campañas de distribución de malware conocidas como **FakeUpdate / ZPHP / SmartApeSG**.
