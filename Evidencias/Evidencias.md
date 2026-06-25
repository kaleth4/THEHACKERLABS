# 🛡️ The Hackers Labs - Writeup: Evidencia
<img width="1185" height="569" alt="image" src="https://github.com/user-attachments/assets/b10bab78-31b4-42f8-b9d2-42f3220bedcc" />

Este repositorio contiene la documentación técnica y el paso a paso detallado para resolver la máquina **Evidencia** de la plataforma [The Hackers Labs](https://labs.thehackerslabs.com).
Este reto se centra principalmente en el **Análisis Forense Digital e Investigación de Tráfico de Red (DFIR)** mediante la inspección de archivos de captura de paquetes (`.pcap`).

---

## 📊 Información General de la Máquina

* **Nombre de la Máquina:** Evidencia
* **Plataforma:** [The Hackers Labs](https://labs.thehackerslabs.com)
* **Dificultad:** Intermedio
* **Enfoque Principal:** Análisis de tráfico de red / Wireshark / Forense Web
* **Objetivo:** Reconstruir la cadena de intrusión llevada a cabo por un atacante a través del análisis exhaustivo del archivo de tráfico proporcionado.
* **Caracteristicas:** 
    Búsqueda en plataformas de Threat Intelligence
    Recolección rápida de metadatos
    Identificación del contenedor / comprimido
    Descarga segura y verificación (sandbox)
    Extracción de contenidos del comprimido
    Análisis estático rápido del ejecutable
    Cálculo y registro de hashes adicionales
    Análisis dinámico en sandbox
    Análisis de memoria
    Comparativa de detecciones AV
    Correlación y enriquecimiento
    Reporte final (campos clave a completar)
    Comandos / APIs útiles
    Notas de seguridad y ética

---

## 🛠️ Herramientas Utilizadas

* 🦈 **Wireshark:** Análisis visual e inspección profunda del archivo `.pcap`.
* ⌨️ **Tshark:** Filtrado rápido de flujos de texto y credenciales desde la terminal.
* 🌐 **CyberChef:** Decodificación de payloads y hashes en caso de ser necesario.

---

## 🚀 Fases del Análisis Forense

### 1. Enumeración y Descubrimiento (Fuzzing de Directorios)
El atacante inició una fase de descubrimiento web mediante ataques de fuerza bruta (*fuzzing*) buscando directorios ocultos. Para identificar qué directorio real descubrió el atacante:

* **Filtro Wireshark Utilizado:**
  ```bash
  http.response.code == 200 or http.response.code == 301 or http.response.code == 302
  ```
* **Hallazgo:** Filtrando las respuestas exitosas de los miles de intentos `404 Not Found`, se logró identificar el directorio exacto que el atacante logró comprometer.

### 2. Inyección de Código / SQL Injection (SQLi)
Posterior al descubrimiento de la ruta web, el atacante abusó de un parámetro vulnerable para extraer información directamente desde el motor de base de datos.

* **Filtro Wireshark Utilizado:**
  ```text
  http contains "UNION" or http contains "SELECT" or http.request.method == "POST"
  ```
* **Hallazgo:** Se identificó la URL exacta de la aplicación que interactuaba de forma insegura con la Base de Datos. Inspeccionando los strings devueltos en las respuestas HTTP, se extrajo el **Nombre de la Base de Datos** afectada.

### 3. Exfiltración y Robo de Credenciales
Tras explotar la inyección SQL, el atacante procedió a dirigirse al panel de autenticación del sistema para ingresar de manera ilegítima.

* **Filtro Wireshark Utilizado:**
  ```text
  http.request.method == "POST" and http contains "password"
  ```
* **Hallazgo:** Al hacer clic derecho sobre los paquetes filtrados e inspeccionar el flujo TCP (*Follow TCP Stream*), se interceptaron en texto claro los parámetros del formulario HTML que contenían el usuario y contraseña utilizados por el atacante para el inicio de sesión.
<img width="1179" height="646" alt="image" src="https://github.com/user-attachments/assets/4f04add9-25d4-4308-a689-5938f5a9f50c" />

---

## Terminal

El comando ideal para hacer esto no es usar cat directamente (ya que cat intentará procesar todo el archivo binario), sino pasar el archivo por herramientas diseñadas para extraer texto legible.
strings archivo.pcap
 ```bash
  strings archivo.pcap

  ```

como alternativa para seguir usando cat


  ```bash
  cat archivo.pcap | tr -cd '[:print:]\n'
  ```
<img width="1175" height="641" alt="image" src="https://github.com/user-attachments/assets/62b87c91-a094-4b9a-83ab-1e7893eb58e1" />

---
<img width="1175" height="641" alt="image" src="https://github.com/user-attachments/assets/ba0769d7-e92c-4fde-8637-5be561006c51" />



## 🏆 Flags Encontradas

| Pregunta / Objetivo | Respuesta / Flag | Método de Obtención |
| :--- | :--- | :--- |
| ¿Cuál es la IP del atacante? | Parametro Destination
| ¿Nombre del script PHP vulnerable? | Packet length 223 HTTP/1.1 200 OK , JSON (application/json) 
| URL completa del primer intento de SQLi (Sin poner https://dominio.thl) | 200 OK , JSON (application/json) 
| Directorio descubierto por fuzzing | `[Añade_aquí_el_directorio]` | Filtro HTTP códigos 200/302 |
| URL que lee la base de datos | `[Añade_aquí_la_URL]` | Análisis de URIs en peticiones GET/POST |
| Nombre de la Base de Datos | `[Corazon]` | Inspección de respuestas HTTP (SELECT/UNION) |
| Credenciales de inicio de sesión | `[Usuario:Contraseña]` | Análisis del cuerpo POST (Form URL Encoded) |
| 
---

## 💡 Lecciones Aprendidas y Mitigación

1. **Sanitización de Entradas:** La aplicación web sufría de una grave vulnerabilidad de inyección SQL. Es imperativo implementar **consultas preparadas (Prepared Statements)** para prevenir que comandos maliciosos alteren la lógica de la base de datos.
2. **Exposición de Directorios:** Limitar el mapeo público de directorios mediante políticas de visibilidad restrictivas y monitorear ráfagas inusuales de tráfico web (fuzzing) mediante un **WAF (Web Application Firewall)** o sistemas IPS/IDS.
3. **Cifrado en Tránsito:** El tráfico web interceptado utilizaba HTTP plano. Toda transferencia de credenciales o datos sensibles debe realizarse obligatoriamente bajo el protocolo seguro **HTTPS (TLS/SSL)** para mitigar ataques de sniffing en la red.

---
📝 *Nota: Este documento ha sido estructurado con fines estrictamente educativos y profesionales como demostración de habilidades en seguridad defensiva y DFIR.*<img width="1920" height="1080" alt="portada" src="https://github.com/user-attachments/assets/bb91789f-8ea9-4975-a3f3-7c72994ec4c4" />
