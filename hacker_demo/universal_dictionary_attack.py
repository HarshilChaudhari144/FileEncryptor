import argparse
from Crypto.Cipher import AES, DES3, ChaCha20
from Crypto.Protocol.KDF import PBKDF2

# Constants
SALT_SIZE = 16
KEY_SIZE = 32
NONCE_SIZE_GCM = 12
TAG_SIZE = 16
NONCE_SIZE_CHACHA = 8
BLOCK_SIZE_DES = 8
ITERATIONS = 100_000

def derive_key(password, salt, key_size):
    return PBKDF2(password.encode(), salt, dkLen=key_size, count=ITERATIONS)

def unpad(data):
    return data[:-data[-1]]

def try_decrypt_aes_cbc(file_data, password):
    salt = file_data[:SALT_SIZE]
    iv = file_data[SALT_SIZE:SALT_SIZE + 16]
    ciphertext = file_data[SALT_SIZE + 16:]

    key = derive_key(password, salt, 32)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    try:
        plaintext = unpad(cipher.decrypt(ciphertext))
        return plaintext.decode(errors="ignore")
    except Exception:
        return None

def try_decrypt_aes_gcm(file_data, password):
    salt = file_data[:SALT_SIZE]
    nonce = file_data[SALT_SIZE:SALT_SIZE + NONCE_SIZE_GCM]
    tag = file_data[SALT_SIZE + NONCE_SIZE_GCM:SALT_SIZE + NONCE_SIZE_GCM + TAG_SIZE]
    ciphertext = file_data[SALT_SIZE + NONCE_SIZE_GCM + TAG_SIZE:]

    key = derive_key(password, salt, 32)
    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)
    try:
        plaintext = cipher.decrypt_and_verify(ciphertext, tag)
        return plaintext.decode(errors="ignore")
    except Exception:
        return None

def try_decrypt_chacha20(file_data, password):
    salt = file_data[:SALT_SIZE]
    nonce = file_data[SALT_SIZE:SALT_SIZE + NONCE_SIZE_CHACHA]
    ciphertext = file_data[SALT_SIZE + NONCE_SIZE_CHACHA:]

    key = derive_key(password, salt, 32)
    cipher = ChaCha20.new(key=key, nonce=nonce)
    try:
        plaintext = cipher.decrypt(ciphertext)
        return plaintext.decode(errors="ignore")
    except Exception:
        return None

def try_decrypt_triple_des(file_data, password):
    salt = file_data[:SALT_SIZE]
    iv = file_data[SALT_SIZE:SALT_SIZE + BLOCK_SIZE_DES]
    ciphertext = file_data[SALT_SIZE + BLOCK_SIZE_DES:]

    key = PBKDF2(password.encode(), salt, dkLen=24, count=ITERATIONS)
    try:
        key = DES3.adjust_key_parity(key)
        cipher = DES3.new(key, DES3.MODE_CBC, iv)
        plaintext = unpad(cipher.decrypt(ciphertext))
        return plaintext.decode(errors="ignore")
    except Exception:
        return None

def run_attack(file_path, dictionary_file, algorithm):
    with open(file_path, 'rb') as f:
        file_data = f.read()

    with open(dictionary_file, 'r') as f:
        passwords = [line.strip() for line in f]

    for password in passwords:
        if algorithm == "aes-cbc":
            result = try_decrypt_aes_cbc(file_data, password)
        elif algorithm == "aes-gcm":
            result = try_decrypt_aes_gcm(file_data, password)
        elif algorithm == "chacha20":
            result = try_decrypt_chacha20(file_data, password)
        elif algorithm == "triple-des":
            result = try_decrypt_triple_des(file_data, password)
        else:
            print(f"[!] Unsupported algorithm: {algorithm}")
            return

        if result is not None:
            print(f"[SUCCESS] Password found: {password}")
            print("Decrypted content:\n")
            print(result)
            return

    print("[FAILURE] No matching password found.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Universal Dictionary Attack Tool")
    parser.add_argument("--file", required=True, help="Encrypted file path")
    parser.add_argument("--dictionary", required=True, help="Password dictionary file")
    parser.add_argument("--algorithm", required=True, choices=["aes-cbc", "aes-gcm", "chacha20", "triple-des"], help="Encryption algorithm")

    args = parser.parse_args()
    run_attack(args.file, args.dictionary, args.algorithm)