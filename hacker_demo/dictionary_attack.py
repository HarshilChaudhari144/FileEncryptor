import os
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

SALT_SIZE = 16
NONCE_SIZE = 12
TAG_SIZE = 16
KEY_SIZE = 32
ITERATIONS = 100_000

def derive_key(password, salt):
    return PBKDF2(password.encode(), salt, dkLen=KEY_SIZE, count=ITERATIONS)

def try_decrypt(file_path, password):
    with open(file_path, 'rb') as f:
        data = f.read()

    salt = data[:SALT_SIZE]
    nonce = data[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
    tag = data[SALT_SIZE + NONCE_SIZE:SALT_SIZE + NONCE_SIZE + TAG_SIZE]
    ciphertext = data[SALT_SIZE + NONCE_SIZE + TAG_SIZE:]

    key = derive_key(password, salt)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode(errors="ignore")
    except Exception:
        return None

def run_attack(file_path, dictionary_file):
    with open(dictionary_file, 'r') as f:
        passwords = [line.strip() for line in f]

    for password in passwords:
        result = try_decrypt(file_path, password)
        if result is not None:
            print(f"[SUCCESS] Password found: {password}")
            print("Decrypted message:")
            print(result)
            return

    print("[FAILURE] No matching password found.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Dictionary attack on AES-GCM encrypted file")
    parser.add_argument("file", help="Encrypted file to attack")
    parser.add_argument("dictionary", help="Path to password dictionary file")
    args = parser.parse_args()

    run_attack(args.file, args.dictionary)