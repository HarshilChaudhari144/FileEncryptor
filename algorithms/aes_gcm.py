# algorithms/aes_gcm.py
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os

# Constants
SALT_SIZE = 16
KEY_SIZE = 32
ITERATIONS = 100_000
NONCE_SIZE = 12
TAG_SIZE = 16
CHUNK_SIZE = 4096

def derive_key(password: bytes, salt: bytes) -> bytes:
    return PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)

def resolve_output_path(file_path, output_path=None, output_dir=None, preserve_extension=False, decrypted=False):
    filename = os.path.basename(file_path)

    if decrypted:
        if filename.endswith(".enc"):
            filename = filename[:-4]
        name, ext = os.path.splitext(filename)
        if preserve_extension:
            filename = f"decrypted_{name}{ext}"
        else:
            filename = f"decrypted_{name}"
    else:
        name, ext = os.path.splitext(filename)
        if ext == ".enc":
            filename = f"{name}.enc"
        else:
            filename = f"{name}{ext}.enc"

    if output_path:
        return os.path.abspath(output_path)

    output_dir = os.path.normpath(output_dir or os.getcwd())
    os.makedirs(output_dir, exist_ok=True)

    return os.path.abspath(os.path.join(output_dir, filename))

def encrypt(file_path: str, password: str, output_path: str = None,
            output_dir: str = "", preserve_extension: bool = True,
            progress_callback=None) -> str:
    salt = get_random_bytes(SALT_SIZE)
    key = derive_key(password.encode(), salt)
    nonce = get_random_bytes(NONCE_SIZE)

    cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

    ext = os.path.splitext(file_path)[1].encode() if preserve_extension else b''
    ext_len = len(ext).to_bytes(1, 'big')

    output_file = resolve_output_path(file_path, output_path, output_dir, preserve_extension, decrypted=False)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(file_path, 'rb') as fin, open(output_file, 'wb') as fout:
        fout.write(salt)
        fout.write(nonce)
        fout.write(b'\x00' * TAG_SIZE)  # Reserve space for tag
        fout.write(ext_len)
        fout.write(ext)

        total_written = 0
        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            ciphertext = cipher.encrypt(chunk)
            fout.write(ciphertext)
            total_written += len(chunk)
            if progress_callback:
                progress_callback(len(chunk))

        tag = cipher.digest()
        fout.seek(SALT_SIZE + NONCE_SIZE)
        fout.write(tag)

    return output_file

def decrypt(file_path: str, password: str, output_path: str = None,
            output_dir: str = "", preserve_extension: bool = True,
            progress_callback=None) -> str:
    with open(file_path, 'rb') as fin:
        salt = fin.read(SALT_SIZE)
        nonce = fin.read(NONCE_SIZE)
        tag = fin.read(TAG_SIZE)
        ext_len = int.from_bytes(fin.read(1), 'big')
        ext = fin.read(ext_len).decode(errors='ignore') if preserve_extension else ''

        key = derive_key(password.encode(), salt)
        cipher = AES.new(key, AES.MODE_GCM, nonce=nonce)

        ciphertext = fin.read()
        plaintext = b''

        for i in range(0, len(ciphertext), CHUNK_SIZE):
            chunk = ciphertext[i:i+CHUNK_SIZE]
            plaintext += cipher.decrypt(chunk)
            if progress_callback:
                progress_callback(len(chunk))

        cipher.verify(tag)

    output_file = resolve_output_path(file_path, output_path, output_dir, preserve_extension, decrypted=True)
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'wb') as fout:
        fout.write(plaintext)

    return output_file