# Informe Forense: Desafío "Rata Callejera" (STRRAT Malware)

Este informe técnico documenta el análisis forense digital del desafío **"Rata Callejera"**. El escenario simula la infección de un host corporativo mediante **STRRAT**, un troyano de acceso remoto (RAT) basado en Java, diseñado para el robo de credenciales, registro de pulsaciones de teclas (keylogging) y control remoto del sistema afectado.

---

## 1. Resumen Ejecutivo

El objetivo de este análisis es reconstruir la intrusión en el host corporativo a partir de la captura de tráfico de red (`.pcap`), identificando los datos de la víctima, el comportamiento del malware y los principales Indicadores de Compromiso (IoCs).

*   **Categorías:** Análisis de Malware / Informáicta Forense
*   **Malware Identificado:** STRRAT RAT
*   **Hash SHA-256:** `4c249b325125235b50d9690560c4197a28fd62901b5e02d9eba7436b29447cdd`

---

## 2. Identificación de la Víctima

A través de la inspección del tráfico en Wireshark (analizando paquetes DHCP, NBNS, LLMNR y tráfico HTTP/SMB), se determinaron las credenciales e identidad del host afectado:

### Dirección IP de la Víctima
*   **Evidencia:** Menú *Statistics > IPv4 Statistics > Addresses* o mediante el filtrado de paquetes de broadcast iniciales.
*   **Resultado:** `[Insertar IP de la víctima, ej. 192.168.1.X]`
<img width="1920" height="1080" alt="¿Cuál es la IP de la víctima_" src="https://github.com/user-attachments/assets/812c0a2d-91fc-422d-a691-9913983d71c2" />

### Hostname de la Víctima
*   **Evidencia:** Identificado en los paquetes DHCP Request (Option 12) o mediante consultas NBNS (NetBIOS Name Service).
*   **Resultado:** `[Insertar Hostname, ej. DESKTOP-XXXXX]`
<img width="1920" height="1080" alt="¿Cuál es el nombre completo del usuario_" src="https://github.com/user-attachments/assets/def6a76b-6686-44bd-9203-287f58273ec7" />

### Dirección MAC de la Víctima
*   **Evidencia:** Dirección física de origen en las tramas Ethernet emitidas por la IP afectada.
*   **Resultado:** `[Insertar MAC, ej. 00:0C:29:XX:XX:XX]`
<img width="1920" height="1080" alt="¿Cuál es la dirección MAC de la víctima_" src="https://github.com/user-attachments/assets/e491c4b9-2f58-4d17-9b13-f744bfbce683" />

---

## 3. Identificación del Perfil de Usuario (Windows)

El malware STRRAT recolecta activamente información sobre el entorno local para enviarla a su servidor de Comando y Control (C2). Esta información suele viajar cifrada o en texto plano en los campos de *User-Agent* o el cuerpo de solicitudes HTTP/TCP.

### Nombre de Cuenta de Usuario de Windows
*   **Evidencia:** String de configuración del sistema recolectado por el malware.
*   **Resultado:** `[Insertar Nombre de Cuenta, ej. Administrador / jdoe]`
<img width="1920" height="1080" alt="¿Cuál es el nombre de la cuenta de usuario de Windows_ " src="https://github.com/user-attachments/assets/95449b32-a5d5-4c28-b017-3e9d76571819" />

### Nombre Completo del Usuario
*   **Evidencia:** Extraído de los artefactos de red correspondientes al perfil de Windows de la víctima.
*   **Resultado:** `[Insertar Nombre Completo del Usuario]`
<img width="1920" height="1080" alt="¿Cuál es el nombre completo del usuario_" src="https://github.com/user-attachments/assets/a8a27058-52fe-41f7-a8f0-f2db4d580043" />

---

## 4. Análisis de Red e Indicadores de Compromiso (IoCs)

### Solicitud HTTP desde la IP Víctima
*   **Filtro Wireshark:** `http.request`
*   **Dominio Consultado:** `[Insertar Dominio, ej. thehackerslabs.com]`

### Intención de la Consulta a la URL
*   **Propósito:** El malware consulta esta dirección con el fin de **[Insertar función, ej. Validar conectividad a internet / Descargar la carga útil (Payload) de la etapa 2 / Enviar el check-in inicial del host]**.
<img width="1920" height="1080" alt="¿Qué dominio recibe una solicitud HTTP desde la IP víctima_" src="https://github.com/user-attachments/assets/48221219-02c8-425c-92ea-02f4b471969c" />

---

## 5. Análisis del Archivo Malicioso

El análisis estático y la correlación en bases de datos de amenazas de la muestra de STRRAT arrojan los siguientes metadatos técnicos:

### Hash SHA-256 del Malware
*   `4c249b325125235b50d9690560c4197a28fd62901b5e02d9eba7436b29447cdd`
<img width="1920" height="965" alt="hash" src="https://github.com/user-attachments/assets/9ec3c26b-0645-4166-a9d1-b51b87b5d497" />

### Nombre Real del Archivo Malicioso
*   **Evidencia:** Nombre original detectado en la cabecera HTTP de descarga (*Content-Disposition*) o en los registros de persistencia.
*   **Resultado:** `[Insertar nombre real del archivo, ej. strrat.jar / invoice.vbs]`

### Tamaño del Archivo
*   **Resultado  en bytes
<img width="1920" height="955" alt="¿Cuál es el tamaño del archivo_" src="https://github.com/user-attachments/assets/c88fd1f5-4d56-4187-8e80-90a4a0a800f2" />



