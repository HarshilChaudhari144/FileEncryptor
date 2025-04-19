# algorithms/triple_des.py
from Crypto.Cipher import DES3
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Random import get_random_bytes
import os

# Constants
BLOCK_SIZE = 8
SALT_SIZE = 16
KEY_SIZE = 24  # 3DES uses 24-byte keys
ITERATIONS = 100_000
CHUNK_SIZE = 64 * 1024  # 64KB

def pad(data: bytes) -> bytes:
    padding_len = BLOCK_SIZE - len(data) % BLOCK_SIZE
    return data + bytes([padding_len]) * padding_len

def unpad(data: bytes) -> bytes:
    return data[:-data[-1]]

def derive_key(password: bytes, salt: bytes) -> bytes:
    key = PBKDF2(password, salt, dkLen=KEY_SIZE, count=ITERATIONS)
    return DES3.adjust_key_parity(key)

def resolve_output_path(file_path, output_path=None, output_dir=None, preserve_extension=False, decrypted=False):
    filename = os.path.basename(file_path)

    if decrypted:
        if filename.endswith(".enc"):
            filename = filename[:-4]
        name, ext = os.path.splitext(filename)
        filename = f"decrypted_{name}{ext if preserve_extension else ''}"
    else:
        name, ext = os.path.splitext(filename)
        filename = f"{name}{ext}.enc" if ext != ".enc" else f"{name}.enc"

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
    iv = get_random_bytes(BLOCK_SIZE)
    cipher = DES3.new(key, DES3.MODE_CBC, iv)

    ext = os.path.splitext(file_path)[1].encode() if preserve_extension else b''
    ext_len = len(ext).to_bytes(1, 'big')
    output_file = resolve_output_path(file_path, output_path, output_dir, preserve_extension, decrypted=False)

    with open(file_path, 'rb') as fin, open(output_file, 'wb') as fout:
        fout.write(salt + iv + ext_len + ext)

        while True:
            chunk = fin.read(CHUNK_SIZE)
            if not chunk:
                break
            padded_chunk = pad(chunk) if len(chunk) < CHUNK_SIZE else chunk
            encrypted = cipher.encrypt(padded_chunk)
            fout.write(encrypted)
            if progress_callback:
                progress_callback(len(chunk))

    return output_file

def decrypt(file_path: str, password: str, output_path: str = None,
            output_dir: str = "", preserve_extension: bool = True,
            progress_callback=None) -> str:
    with open(file_path, 'rb') as fin:
        salt = fin.read(SALT_SIZE)
        iv = fin.read(BLOCK_SIZE)
        ext_len = int.from_bytes(fin.read(1), 'big')
        ext = fin.read(ext_len).decode(errors='ignore') if preserve_extension else ''
        key = derive_key(password.encode(), salt)
        cipher = DES3.new(key, DES3.MODE_CBC, iv)

        output_file = resolve_output_path(file_path, output_path, output_dir, preserve_extension, decrypted=True)

        with open(output_file, 'wb') as fout:
            prev_chunk = b''
            while True:
                chunk = fin.read(CHUNK_SIZE)
                if not chunk:
                    break
                decrypted = cipher.decrypt(chunk)
                if prev_chunk:
                    fout.write(prev_chunk)
                prev_chunk = decrypted
                if progress_callback:
                    progress_callback(len(chunk))

            if prev_chunk:
                fout.write(unpad(prev_chunk))

    return output_file