#!/usr/bin/env python3
import argparse

def get_arguments():
    parser = argparse.ArgumentParser(description="Herramienta para cifrar/descifrar usando Cifrado César")
    parser.add_argument("-t", "--text", required=True, dest="texto", help="Texto a procesar")
    parser.add_argument("-k", "--key", type=int, default=3, help="Clave de desplazamiento (por defecto 3)")
    parser.add_argument("-d", "--descifrar", action="store_true", help="Descifrar en lugar de cifrar")
    
    return parser.parse_args()

def cesar(texto, k, descifrar=False):
    resultado = []
    if descifrar:
        k = -k  # Invertimos el desplazamiento para descifrar
    
    for letra in texto:
        if letra.isalpha():
            base = 'A' if letra.isupper() else 'a'
            nueva_letra = chr((ord(letra) - ord(base) + k) % 26 + ord(base))
            resultado.append(nueva_letra)
        else:
            resultado.append(letra)

    return ''.join(resultado)

def main():
    args = get_arguments()
    
    # Procesar el texto que le pasemos como argumento
    resultado = cesar(
        texto=args.texto,
        k=args.key,
        descifrar=args.descifrar
    )
    
    print(resultado)

if __name__ == '__main__':
    main()
