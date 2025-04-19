import os
import getpass
from rich.console import Console
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TransferSpeedColumn

from algorithms import aes_cbc, aes_gcm, chacha20, triple_des
from user_interface import autocomplete_path, choose_algorithm
from logging_utils import log_action

console = Console()

ALGORITHMS = {
    "aes-cbc": aes_cbc,
    "aes-gcm": aes_gcm,
    "chacha20": chacha20,
    "3des": triple_des,
}

def encrypt_file(settings):
    path = autocomplete_path("Select a file to encrypt:")
    if not os.path.isfile(path):
        console.print("[red][!] File does not exist.[/red]")
        input("\nPress Enter to continue...")
        return

    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")
    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]
    file_size = os.path.getsize(path)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False  # Keep the progress bar after completion
    ) as progress:
        task_id = progress.add_task("Encrypting", total=file_size)

        try:
            output_path = ALGORITHMS[algorithm].encrypt(
                file_path=path,
                password=password,
                output_path=None,
                output_dir=output_dir,
                preserve_extension=settings["preserve_extension"],
                progress_callback=lambda b: progress.update(task_id, advance=b)
            )
        except Exception as e:
            console.print(f"[red][ERROR] {e}[/red]")
            log_action("encrypt", path, algorithm, f"error: {e}", "N/A")
            input("\nPress Enter to continue...")
            return

    # Display result after the progress bar completes
    console.print(f"[green][+] Encrypted successfully! Saved to: {output_path}[/green]")
    log_action("encrypt", path, algorithm, "success", output_path)
    input("\nPress Enter to continue...")

def decrypt_file(settings):
    path = autocomplete_path("Select a file to decrypt:")
    if not os.path.isfile(path):
        console.print("[red][!] File does not exist.[/red]")
        input("\nPress Enter to continue...")
        return

    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")
    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]
    file_size = os.path.getsize(path)

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False  # Keep the progress bar after completion
    ) as progress:
        task_id = progress.add_task("Decrypting", total=file_size)

        try:
            output_path = ALGORITHMS[algorithm].decrypt(
                file_path=path,
                password=password,
                output_path=None,
                output_dir=output_dir,
                preserve_extension=settings["preserve_extension"],
                progress_callback=lambda b: progress.update(task_id, advance=b)
            )
        except Exception as e:
            console.print(f"[red][ERROR] {e}[/red]")
            log_action("decrypt", path, algorithm, f"error: {e}", "N/A")
            input("\nPress Enter to continue...")
            return

    # Display result after the progress bar completes
    console.print(f"[green][+] Decrypted successfully! Saved to: {output_path}[/green]")
    log_action("decrypt", path, algorithm, "success", output_path)
    input("\nPress Enter to continue...")

def batch_encrypt(settings):
    dir_path = autocomplete_path("Select directory for batch encryption:", only_directories=True)
    if not os.path.isdir(dir_path):
        console.print("[red][!] Invalid directory.[/red]")
        input("\nPress Enter to continue...")
        return

    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]
    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")

    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False
    ) as progress:
        for filename in files:
            file_path = os.path.join(dir_path, filename)
            file_size = os.path.getsize(file_path)
            task_id = progress.add_task(f"Encrypting {filename}", total=file_size)

            try:
                output_path = ALGORITHMS[algorithm].encrypt(
                    file_path=file_path,
                    password=password,
                    output_path=None,
                    output_dir=output_dir,
                    preserve_extension=settings["preserve_extension"],
                    progress_callback=lambda b: progress.update(task_id, advance=b)
                )
                log_action("batch-encrypt", file_path, algorithm, "success", output_path)
            except Exception as e:
                log_action("batch-encrypt", file_path, algorithm, f"error: {e}", "N/A")

    if settings["show_summary_after_batch"]:
        console.print("\n[green][+] Batch encryption completed![/green]")
        input("\nPress Enter to continue...")

def batch_decrypt(settings):
    dir_path = autocomplete_path("Select directory for batch decryption:", only_directories=True)
    if not os.path.isdir(dir_path):
        console.print("[red][!] Invalid directory.[/red]")
        input("\nPress Enter to continue...")
        return

    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]
    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")

    files = [f for f in os.listdir(dir_path) if f.endswith(".enc")]

    with Progress(
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        "[progress.percentage]{task.percentage:>3.0f}%",
        TransferSpeedColumn(),
        TimeRemainingColumn(),
        console=console,
        transient=False
    ) as progress:
        for filename in files:
            file_path = os.path.join(dir_path, filename)
            file_size = os.path.getsize(file_path)
            task_id = progress.add_task(f"Decrypting {filename}", total=file_size)

            try:
                output_path = ALGORITHMS[algorithm].decrypt(
                    file_path=file_path,
                    password=password,
                    output_path=None,
                    output_dir=output_dir,
                    preserve_extension=settings["preserve_extension"],
                    progress_callback=lambda b: progress.update(task_id, advance=b)
                )
                log_action("batch-decrypt", file_path, algorithm, "success", output_path)
            except Exception as e:
                log_action("batch-decrypt", file_path, algorithm, f"error: {e}", "N/A")

    if settings["show_summary_after_batch"]:
        console.print("\n[green][+] Batch decryption completed![/green]")
        input("\nPress Enter to continue...")