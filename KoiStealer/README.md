# 🛡️ Análisis Forense de Red: Koi Stealer
<img width="1355" height="645" alt="portada" src="https://github.com/user-attachments/assets/91e7188c-09c9-4f66-a4ec-f9b7b27c978f" />

## 📝 Descripción del Desafío
Este reto de nivel avanzado se centra en la reconstrucción del flujo de ataque e infección del malware conocido como **Koi Stealer** mediante el análisis de un volcado de tráfico de red (PCAP). El objetivo principal es identificar los sistemas afectados, los artefactos descargados y la infraestructura de comando y control (C2) utilizada por el atacante.

---

## 🎯 Objetivos del Análisis
* **Reconstrucción del flujo:** Analizar el tráfico de red (PCAP) para mapear cronológicamente la infección.
* **Identificación del sistema:** Localizar la IP, MAC y Hostname del host comprometido mediante protocolos de descubrimiento (DHCP/NBNS).
* **Identificación de usuarios:** Inspeccionar el tráfico de autenticación Kerberos y consultas LDAP para extraer cuentas afectadas.
* **Filtrado web:** Analizar el tráfico HTTP/TLS para detectar la descarga de payloads y conexiones a dominios maliciosos.
* **Extracción de artefactos:** Recuperar archivos maliciosos (ZIP, DLL) directamente desde los flujos de datos de red.
* **Análisis de IOCs:** Calcular los hashes criptográficos (SHA256) de las muestras extraídas.
* **Actividad C2:** Identificar callbacks y balizamiento (beaconing) hacia el servidor de Command & Control.

---

## 💻 Identificación del Entorno de la Víctima

A través del análisis de protocolos de descubrimiento de red y de autenticación en el Active Directory, se determinaron los siguientes datos del host afectado:

| Atributo | Valor Identificado | Método de Obtención / Filtro Wireshark |
| :--- | :--- | :--- |
| **Dirección IP** | `172.17.0.99` | Análisis general de tráfico / Alertas del IDS |
| **Dirección MAC** | `18:3d:a2:b6:8d:c4` | Inspección de paquetes DHCP / NBNS |
| **Hostname** | `DESKTOP-RNVO9AT` | Consultas NBNS / Registros DHCP |
| **Usuario de Windows** | `afletcher` | Inspección de tickets en tráfico Kerberos |

### 📂 Detalles de Cuenta en Active Directory (LDAP)
Para enriquecer el perfil del usuario afectado, se filtró el tráfico del protocolo **LDAP**. Esto permite inspeccionar las respuestas del controlador de dominio y extraer atributos clave:

* **Nombre Completo:** `[Inserta el givenName + surname aquí]` *(Ej: Andrew Fletcher)*
* **Unidad Organizativa (OU):** `[Inserta la OU de la consulta LDAP aquí]`
* **Filtro útil en Wireshark:** `ldap` (Buscar cadenas que contengan `givenName`, `sn`, o `sAMAccountName==afletcher`)

---

## 🚨 Indicadores de Compromiso (IOCs) Detectados

### 1. Descarga de Payloads y Dominios Relacionados
Al auditar las conexiones cifradas y no cifradas originadas por la víctima (`172.17.0.99`), se identificó infraestructura web sospechosa:

* **Dominio Adicional TLS:** `[Inserta el dominio aquí]` *(Ej: dominio-malicioso.com)*
  * **Filtro Wireshark:** `tls.handshake.type == 1 and ip.src == 172.17.0.99`
  * **Procedimiento:** Revisar el campo **Server Name Indication (SNI)** en el *Client Hello* para descubrir las conexiones HTTPS realizadas.
* **Tráfico de Origen:** Conexiones dirigidas o vinculadas a la plataforma oficial de [The Hackers Labs](https://blog.thehackerslabs.com/resolucion-forense-koi-stealer/ "Resolución Forense Koi Stealer - The Hackers Labs | Blog") durante el desarrollo del reto.

### 2. Extracción de Artefactos Maliciosos
Se reconstruyeron los flujos de datos web para extraer los binarios descargados por la víctima:

* **Archivo 1 (ZIP):** `[Nombre del archivo.zip]` 
  * **Hash SHA256:** `[Hash de 64 caracteres]`
* **Archivo 2 (DLL):** `[Nombre del archivo.dll]`
  * **Hash SHA256:** `[Hash de 64 caracteres]`
* **Procedimiento en Wireshark:** `File` -> `Export Objects` -> `HTTP` (o extraer la secuencia cruda de bytes TCP).

### 3. Comunicación con el Servidor Command & Control (C2)
El malware **Koi Stealer** exfiltra los datos recolectados enviando solicitudes baliza hacia su servidor de control:

* **Dirección IP del C2:** `[Inserta la IP maliciosa aquí]`
* **Comportamiento del tráfico:** Peticiones constantes utilizando el método **HTTP POST** que contienen los datos robados (credenciales, cookies, información del sistema).
* **Filtro Wireshark:** `http.request.method == "POST" and ip.src == 172.17.0.99`

---

## 🏁 Conclusión del Incidente
El análisis confirma el compromiso exitoso del host `DESKTOP-RNVO9AT`. El usuario `afletcher` descargó un archivo comprimido malicioso que posteriormente ejecutó una librería dinámica (DLL), iniciando la baliza hacia la IP del C2 para completar la exfiltración de información del entorno corporativo.
