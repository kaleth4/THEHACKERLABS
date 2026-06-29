from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from hashlib import sha256
import base64

# 1. Leer y decodificar el archivo encriptado
with open("root_dump.dat", "r") as f:
    data_b64 = f.read()
data = base64.b64decode(data_b64)

# 2. Separar el IV (primeros 16 bytes) del texto cifrado
iv = data[:16]
ciphertext = data[16:]

# 3. Derivar la clave criptográfica usando SHA-256 (cortada a 16 bytes)
# Nota: Modifica "lavida3nroja" por el valor completo si la imagen tiene caracteres ocultos
key = sha256(b"lavida3nroja").digest()[:16]

# 4. Configurar y ejecutar el descifrado AES
cipher = AES.new(key, AES.MODE_CBC, iv)
plaintext = unpad(cipher.decrypt(ciphertext), AES.block_size)

# 5. Imprimir el resultado legible por pantalla
print("🛡️ Root Flag:", plaintext.decode('utf-8'))
