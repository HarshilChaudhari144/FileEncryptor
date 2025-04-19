# archive_operations.py
import os
import zipfile
import shutil
import tempfile
import getpass
from colorama import Fore, Style
from rich.progress import Progress

from user_interface import autocomplete_path, choose_algorithm
from logging_utils import log_action
from algorithms import aes_cbc, aes_gcm, chacha20, triple_des

ALGORITHMS = {
    "aes-cbc": aes_cbc,
    "aes-gcm": aes_gcm,
    "chacha20": chacha20,
    "3des": triple_des,
}

def zip_directory(source_dir, zip_path):
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(source_dir):
            for file in files:
                abs_path = os.path.join(root, file)
                arcname = os.path.relpath(abs_path, start=source_dir)
                zipf.write(abs_path, arcname)

def unzip_to_directory(zip_path, extract_to):
    with zipfile.ZipFile(zip_path, 'r') as zipf:
        zipf.extractall(extract_to)

def encrypt_archive(settings):
    folder_path = autocomplete_path("Select a folder to encrypt:", only_directories=True)
    if not os.path.isdir(folder_path):
        print(Fore.RED + "[!] Folder does not exist." + Style.RESET_ALL)
        input("\nPress Enter to continue...")
        return

    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")
    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            folder_name = os.path.basename(folder_path.rstrip(os.sep))
            zip_path = os.path.join(tmpdir, folder_name + ".zip")

            zip_directory(folder_path, zip_path)
            total_size = os.path.getsize(zip_path)

            with Progress() as progress:
                task = progress.add_task("[cyan]Encrypting archive...", total=total_size)

                def progress_callback(bytes_processed):
                    progress.update(task, advance=bytes_processed)

                output_path = ALGORITHMS[algorithm].encrypt(
                    file_path=zip_path,
                    password=password,
                    output_path=None,
                    output_dir=output_dir,
                    preserve_extension=settings["preserve_extension"],
                    progress_callback=progress_callback
                )

                # Ensure the bar completes
                progress.update(task, completed=total_size)

        print(Fore.GREEN + f"[+] Folder encrypted as archive: {output_path}" + Style.RESET_ALL)
        log_action("encrypt_archive", folder_path, algorithm, "success", output_path)
    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}" + Style.RESET_ALL)
        log_action("encrypt_archive", folder_path, algorithm, f"error: {e}", "N/A")
    input("\nPress Enter to continue...")

def decrypt_archive(settings):
    enc_path = autocomplete_path("Select an encrypted archive file:")
    if not os.path.isfile(enc_path):
        print(Fore.RED + "[!] File does not exist." + Style.RESET_ALL)
        input("\nPress Enter to continue...")
        return

    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")
    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            total_size = os.path.getsize(enc_path)

            with Progress() as progress:
                task = progress.add_task("[cyan]Decrypting archive...", total=total_size)

                def progress_callback(bytes_processed):
                    progress.update(task, advance=bytes_processed)

                decrypted_zip_path = ALGORITHMS[algorithm].decrypt(
                    file_path=enc_path,
                    password=password,
                    output_path=None,
                    output_dir=tmpdir,
                    preserve_extension=settings["preserve_extension"],
                    progress_callback=progress_callback
                )

                # Ensure the bar completes
                progress.update(task, completed=total_size)

            extract_to = os.path.join(output_dir, "decrypted_" + os.path.splitext(os.path.basename(enc_path))[0])
            unzip_to_directory(decrypted_zip_path, extract_to)

        print(Fore.GREEN + f"[+] Archive decrypted and extracted to: {extract_to}" + Style.RESET_ALL)
        log_action("decrypt_archive", enc_path, algorithm, "success", extract_to)
    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}" + Style.RESET_ALL)
        log_action("decrypt_archive", enc_path, algorithm, f"error: {e}", "N/A")
    input("\nPress Enter to continue...")