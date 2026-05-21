
# 🔍 Resolución del CTF: **Conexión Perdida**

> **🎯 Objetivo**: Recuperar las flags **User** y **Root** mediante análisis forense y criptografía.

---

## 🧩 **Estructura del Reto**

Este CTF simula un escenario de **análisis forense digital** combinado con técnicas de **criptografía**, donde deberás:
1. Extraer una clave oculta usando esteganografía.
2. Descifrar un dump cifrado para obtener la **User Flag**.
3. Derivar una clave y descifrar otro archivo para la **Root Flag**.

---

## 🧪 **Paso 1: Extraer la Clave Oculta de `imagen.jpg`**

📌 **Objetivo**: Recuperar la clave `lavida3nroja` escondida en la imagen usando **StegSeek**.

### 🔧 Comandos y Resultados

1. **Extraer la clave con StegSeek**:
   ```bash
   stegseek imagen.jpg /usr/share/wordlists/rockyou.txt
   ```
   📥 **Resultado esperado**:
   ```
   Found passphrase: invisible
   ```

2. **Extraer datos con `steghide`**:
   ```bash
   steghide extract -sf imagen.jpg -p invisible
   ```
   📥 **Resultado esperado**:
   ```
   wrote extracted data to "clave.txt"
   ```

3. **Verificar la clave**:
   ```bash
   cat clave.txt
   ```
   ✅ **Salida esperada**:
   ```
   Ya tienes la clave original (clave1).
   ```

---

## 🔓 **Paso 2: Desencriptar `dump.txt` (User Flag)**

📌 **Objetivo**: Descifrar el archivo `dump.txt` para obtener la **User Flag** usando **AES-128-CBC**.

### 🐍 Script Personalizado: `descifrar_user.py`

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
import base64

# Leer el contenido cifrado
with open("dump.txt", "r") as f:
    data_b64 = f.read()

data = base64.b64decode(data_b64)
iv = data[:16]           # Vector de inicialización (16 bytes)
ciphertext = data[16:]   # Texto cifrado

# Clave obtenida de la imagen (16 bytes)
key = b"lavida3nroja____"

cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

print("🧑‍💻 User Flag:", plaintext.decode())
```

### 🚀 Ejecución
```bash
python3 descifrar_user.py
```
📥 **Resultado esperado**:
```
🧑‍💻 User Flag: THL{conexion_interceptada_correctamente}
```

---

## 🔐 **Paso 3: Derivar Nueva Clave y Descifrar `root_dump.dat`**

📌 **Objetivo**: Descifrar `root_dump.dat` para obtener la **Root Flag** usando una clave derivada con **SHA-256**.

### 🐍 Script Personalizado: `descifrar_root.py`

```python
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha256
import base64

# Leer root_dump.dat
with open("root_dump.dat", "r") as f:
    data_b64 = f.read()

data = base64.b64decode(data_b64)
iv = data[:16]           # Vector de inicialización (16 bytes)
ciphertext = data[16:]   # Texto cifrado

# Derivar clave desde "la" (clave1)
key = sha256(b"la").digest()[:16]

cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

print("🛡️ Root Flag:", plaintext.decode())
```

### 🚀 Ejecución
```bash
python3 descifrar_root.py
```
📥 **Resultado esperado**:
```
🛡️ Root Flag: THL{control_to}
```

---

## 📜 **Descripción del Reto**

Este laboratorio combina **análisis forense** y **criptografía** para simular un escenario real de recuperación de datos. Los pasos clave incluyen:

- **Esteganografía**: Uso de `StegSeek` para extraer datos ocultos en imágenes.
- **Criptografía**: Descifrado de archivos cifrados con **AES-128-CBC**.
- **Derivación de claves**: Uso de **SHA-256** para generar claves a partir de cadenas conocidas.

---

## 🛠️ **Herramientas Utilizadas**

| Herramienta       | Descripción                          |
|-------------------|--------------------------------------|
| **StegSeek**      | Extracción de datos ocultos en imágenes. |
| **OpenSSL**       | Descifrado de archivos cifrados.     |
| **Python**        | Automatización con scripts personalizados. |
| **PyCryptodome**  | Librería para operaciones criptográficas. |
| **xxd**           | Inspección de archivos binarios.     |
| **base64**        | Codificación/decodificación de datos. |

---

## 🔍 **Metodología**

### 1️⃣ **Esteganografía**

📌 **Objetivo**: Encontrar la clave oculta en `imagen.jpg`.

🔧 **Comando**:
```bash
stegseek imagen.jpg /usr/share/wordlists/rockyou.txt
```
📥 **Resultado**:
```
Found passphrase: invisible
```

🔑 **Clave extraída**:
```
lavida3nroja
```

---

### 2️⃣ **Análisis del Dump Cifrado**

📌 **Objetivo**: Identificar la estructura del archivo cifrado (`dump.bin`).

🔧 **Comando**:
```bash
xxd dump.bin
```
📥 **Estructura identificada**:
```
[ IV (16 bytes) ][ Ciphertext ]
```

---

### 3️⃣ **Descifrado AES**

📌 **Objetivo**: Descifrar el archivo usando la clave `lavida3nroja____`.

🔧 **Comando (OpenSSL)**:
```bash
openssl enc -aes-128-cbc -d -in cipher.bin -K 6c6176696461336e726f6a615f5f5f5f -iv 0102030405060708090a0b0c0d0e0f10
```
📥 **User Flag**:
```
THL{conexion_interceptada_correctamente}
```

---

### 4️⃣ **Root Flag**

📌 **Objetivo**: Descifrar `root_dump.dat` para obtener la **Root Flag**.

🔧 **Pasos**:
1. Decodificar Base64:
   ```bash
   base64 -d root_dump.dat > root.bin
   ```
2. Separar IV y Ciphertext:
   ```bash
   dd if=root.bin bs=1 count=16 of=iv_root.bin
   dd if=root.bin bs=1 skip=16 of=cipher_root.bin
   ```

📌 **Script de prueba de claves**:
```python
from Crypto.Cipher import AES
from hashlib import sha256
import base64

with open('root_dump.dat','r') as f:
    data = base64.b64decode(f.read())

iv = data[:16]
ciphertext = data[16:]

for candidate in ['la','lja','lavida3nroja','thisisnottherealkey','invisible']:
    key = sha256(candidate.encode()).digest()[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plaintext = cipher.decrypt(ciphertext)
    print(candidate, plaintext)
```

🔑 **Clave correcta**:
```
lavida3nroja
```

📥 **Root Flag**:
```
THL{control_to}
```

---

## 🎯 **Conclusión**

🔹 **User Flag**: `THL{conexion_interceptada_correctamente}`
🔹 **Root Flag**: `THL{control_to}`

