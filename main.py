# main.py
import os
import getpass
import json
from datetime import datetime
from time import sleep
from algorithms import aes_cbc, aes_gcm, chacha20, triple_des

import questionary
from questionary import Style as QStyle
from tqdm import tqdm
from colorama import Fore, Style, init

init(autoreset=True)

SETTINGS_FILE = "settings.json"

# Setup Questionary Style
custom_style = QStyle([
    ('qmark', 'fg:#E91E63 bold'),
    ('question', 'bold'),
    ('answer', 'fg:#00BCD4 bold'),
    ('pointer', 'fg:#673AB7 bold'),
    ('highlighted', 'fg:#03A9F4 bold'),
    ('selected', 'fg:#4CAF50'),
    ('separator', 'fg:#cc5454'),
    ('instruction', 'fg:#FFC107'),
])

# Load or initialize settings
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        default = {
            "default_algorithm": "aes-cbc",
            "preserve_extension": True,
            "output_directory": "",
            "show_summary_after_batch": True,
            "recent_activity_count": 5,
            "use_colors": True,
            "use_icons": True,
            "default_output_dir": ""
        }
        with open(SETTINGS_FILE, "w") as f:
            json.dump(default, f, indent=4)
        return default
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(data, f, indent=4)

settings = load_settings()

ALGORITHMS = {
    "aes-cbc": aes_cbc,
    "aes-gcm": aes_gcm,
    "chacha20": chacha20,
    "3des": triple_des,
}

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header():
    if settings["use_colors"]:
        print(Fore.CYAN + """
╔════════════════════════════════════════╗
║     FILE ENCRYPTOR & DECRYPTOR TOOL    ║
╚════════════════════════════════════════╝
""" + Style.RESET_ALL)
    else:
        print("==== FILE ENCRYPTOR & DECRYPTOR TOOL ====")

def print_menu():
    icons = settings["use_icons"]
    color = Fore.YELLOW if settings["use_colors"] else ""
    reset = Style.RESET_ALL if settings["use_colors"] else ""
    print(color + f"""
[1] {'🔐 ' if icons else ''}Encrypt a file
[2] {'🔓 ' if icons else ''}Decrypt a file
[3] {'📁 ' if icons else ''}Batch Encrypt (Directory)
[4] {'📂 ' if icons else ''}Batch Decrypt (Directory)
[5] {'⚙️  ' if icons else ''}Settings
[6] {'📘 ' if icons else ''}Help & Usage Guide
[7] {'📑' if icons else ''}View Recent Activities
[8] {'❌ ' if icons else ''}Exit
""" + reset)

def choose_algorithm():
    algorithms = {
        "AES-CBC": "aes-cbc",
        "AES-GCM": "aes-gcm",
        "ChaCha20": "chacha20",
        "Triple DES": "3des"
    }

    default_algo_key = next((k for k, v in algorithms.items() if v == settings["default_algorithm"]), "AES-CBC")

    choice = questionary.select(
        "Select an encryption algorithm:",
        choices=list(algorithms.keys()),
        default=default_algo_key,
        style=custom_style
    ).ask()
    return algorithms[choice]

def autocomplete_path(message, only_directories=False):
    return questionary.path(
        message=message,
        only_directories=only_directories,
        style=custom_style
    ).ask()

def log_action(action, filename, algorithm, status, output_path):
    with open("log.txt", "a") as f:
        f.write(f"{datetime.now()} | {action.upper()} | {filename} | {algorithm} | {status} | {output_path}\n")

def encrypt_file():
    path = autocomplete_path("Select a file to encrypt:")
    if not os.path.isfile(path):
        print(Fore.RED + "[!] File does not exist." + Style.RESET_ALL)
        input("\nPress Enter to continue...")
        return

    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")
    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]

    try:
        output_path = ALGORITHMS[algorithm].encrypt(
            file_path=path,
            password=password,
            output_path=None,
            output_dir=output_dir,
            preserve_extension=settings["preserve_extension"]
        )
        print(Fore.GREEN + f"[+] Encrypted successfully! Saved to: {output_path}" + Style.RESET_ALL)
        log_action("encrypt", path, algorithm, "success", output_path)
    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}" + Style.RESET_ALL)
        log_action("encrypt", path, algorithm, f"error: {e}", "N/A")
    input("\nPress Enter to continue...")

def decrypt_file():
    path = autocomplete_path("Select a file to decrypt:")
    if not os.path.isfile(path):
        print(Fore.RED + "[!] File does not exist." + Style.RESET_ALL)
        input("\nPress Enter to continue...")
        return

    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")
    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]

    try:
        output_path = ALGORITHMS[algorithm].decrypt(
            file_path=path,
            password=password,
            output_path=None,
            output_dir=output_dir,
            preserve_extension=settings["preserve_extension"]
        )
        print(Fore.GREEN + f"[+] Decrypted successfully! Saved to: {output_path}" + Style.RESET_ALL)
        log_action("decrypt", path, algorithm, "success", output_path)
    except Exception as e:
        print(Fore.RED + f"[ERROR] {e}" + Style.RESET_ALL)
        log_action("decrypt", path, algorithm, f"error: {e}", "N/A")
    input("\nPress Enter to continue...")

def batch_encrypt():
    dir_path = autocomplete_path("Select directory for batch encryption:", only_directories=True)
    if not os.path.isdir(dir_path):
        print(Fore.RED + "[!] Invalid directory." + Style.RESET_ALL)
        input("\nPress Enter to continue...")
        return

    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]
    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")

    files = [f for f in os.listdir(dir_path) if os.path.isfile(os.path.join(dir_path, f))]
    for filename in tqdm(files, desc="Encrypting files", ncols=70):
        file_path = os.path.join(dir_path, filename)
        try:
            output_path = ALGORITHMS[algorithm].encrypt(
                file_path=file_path,
                password=password,
                output_path=None,
                output_dir=output_dir,
                preserve_extension=settings["preserve_extension"]
            )
            log_action("batch-encrypt", file_path, algorithm, "success", output_path)
        except Exception as e:
            log_action("batch-encrypt", file_path, algorithm, f"error: {e}", "N/A")

    if settings["show_summary_after_batch"]:
        print(Fore.GREEN + "\n[+] Batch encryption completed!" + Style.RESET_ALL)
        input("\nPress Enter to continue...")

def batch_decrypt():
    dir_path = autocomplete_path("Select directory for batch decryption:", only_directories=True)
    if not os.path.isdir(dir_path):
        print(Fore.RED + "[!] Invalid directory." + Style.RESET_ALL)
        input("\nPress Enter to continue...")
        return

    output_dir = autocomplete_path("Select output directory:", only_directories=True) or settings["default_output_dir"]
    algorithm = choose_algorithm()
    password = getpass.getpass("Enter password: ")

    files = [f for f in os.listdir(dir_path) if f.endswith(".enc")]
    for filename in tqdm(files, desc="Decrypting files", ncols=70):
        file_path = os.path.join(dir_path, filename)
        try:
            output_path = ALGORITHMS[algorithm].decrypt(
                file_path=file_path,
                password=password,
                output_path=None,
                output_dir=output_dir,
                preserve_extension=settings["preserve_extension"]
            )
            log_action("batch-decrypt", file_path, algorithm, "success", output_path)
        except Exception as e:
            log_action("batch-decrypt", file_path, algorithm, f"error: {e}", "N/A")

    if settings["show_summary_after_batch"]:
        print(Fore.GREEN + "\n[+] Batch decryption completed!" + Style.RESET_ALL)
        input("\nPress Enter to continue...")

def show_help():
    clear_screen()
    print_header()
    print(Fore.YELLOW + "📘 Help & Usage Guide\n" + Style.RESET_ALL)
    try:
        with open("help.txt", "r") as help_file:
            print(help_file.read())
    except FileNotFoundError:
        print(Fore.RED + "Help file not found." + Style.RESET_ALL)
    input("\nPress Enter to return to the main menu...")

def settings_menu():
    while True:
        clear_screen()
        print_header()
        print(Fore.YELLOW + "⚙️ Settings\n" + Style.RESET_ALL)

        # Display the current values as part of the menu
        settings_options = [
            f"Set default output directory (Current: {settings.get('default_output_dir', '')})",
            f"Choose default encryption algorithm (Current: {settings.get('default_algorithm', '')})",
            f"Preserve original extension on decryption? (Current: {'Yes' if settings.get('preserve_extension', True) else 'No'})",
            f"Show summary after batch operations? (Current: {'Yes' if settings.get('show_summary_after_batch', True) else 'No'})",
            f"Enable colored output? (Current: {'Yes' if settings.get('use_colors', True) else 'No'})",
            f"Use icons in menu? (Current: {'Yes' if settings.get('use_icons', True) else 'No'})",
            f"Number of recent logs to keep (Current: {settings.get('recent_activity_count', 5)})",
            "Save & Exit",
            "Discard & Exit"
        ]

        selected = questionary.select(
            "Choose a setting to modify:",
            choices=settings_options,
            style=custom_style
        ).ask()

        if selected.startswith("Set default output directory"):
            settings["default_output_dir"] = autocomplete_path("Set default output directory:", only_directories=True)

        elif selected.startswith("Choose default encryption algorithm"):
            settings["default_algorithm"] = questionary.select(
                "Choose the default encryption algorithm:",
                choices=["AES-CBC", "AES-GCM", "ChaCha20", "3DES"],
                default=settings.get("default_algorithm", "AES-CBC"),
                style=custom_style
            ).ask()

        elif selected.startswith("Preserve original extension"):
            settings["preserve_extension"] = questionary.select(
                "Preserve original extension on decryption?",
                choices=["Yes", "No"],
                default="Yes" if settings.get("preserve_extension", True) else "No",
                style=custom_style
            ).ask() == "Yes"

        elif selected.startswith("Show summary"):
            settings["show_summary_after_batch"] = questionary.select(
                "Show summary after batch operations?",
                choices=["Yes", "No"],
                default="Yes" if settings.get("show_summary_after_batch", True) else "No",
                style=custom_style
            ).ask() == "Yes"

        elif selected.startswith("Enable colored output"):
            settings["use_colors"] = questionary.select(
                "Enable colored output?",
                choices=["Yes", "No"],
                default="Yes" if settings.get("use_colors", True) else "No",
                style=custom_style
            ).ask() == "Yes"

        elif selected.startswith("Use icons"):
            settings["use_icons"] = questionary.select(
                "Use icons in menu?",
                choices=["Yes", "No"],
                default="Yes" if settings.get("use_icons", True) else "No",
                style=custom_style
            ).ask() == "Yes"

        elif selected.startswith("Number of recent logs"):
            settings["recent_activity_count"] = int(
                questionary.text(
                    "Number of recent logs to keep (default 5):",
                    default=str(settings.get("recent_activity_count", 5)),
                    style=custom_style
                ).ask()
            )

        elif selected == "Save & Exit":
            save_settings(settings)
            print(Fore.GREEN + "[+] Settings updated successfully!" + Style.RESET_ALL)
            sleep(1)
            break

        elif selected == "Discard & Exit":
            print(Fore.YELLOW + "[!] Changes discarded." + Style.RESET_ALL)
            sleep(1)
            break

def display_recent_activity(settings):
    count = settings.get("recent_activity_count", 5)
    use_colors = settings.get("use_colors", True)
    use_icons = settings.get("use_icons", True)

    color_map = {
        "encrypt": Fore.GREEN,
        "decrypt": Fore.CYAN,
        "batch encrypt": Fore.MAGENTA,
        "batch decrypt": Fore.BLUE,
        "default": Fore.WHITE,
        "error": Fore.RED
    }

    icon_map = {
        "encrypt": "🔒",
        "decrypt": "🔓",
        "batch encrypt": "🗃️ 🔒",
        "batch decrypt": "🗃️ 🔓",
        "default": "⚙️",
        "error": "⚠️"
    }

    try:
        with open("log.txt", "r") as log_file:
            lines = log_file.readlines()
            recent_logs = lines[-count:]
            
            print("\nRecent Activity:\n")
            print("=" * 40,"\n")

            for log in recent_logs:
                clean_log = log.strip()
                action = "default"

                if "error" in clean_log or "Failed" in clean_log:
                    action = "error"
                elif "BATCH-ENCRYPT" in clean_log:
                    action = "batch encrypt"
                elif "BATCH-DECRYPT" in clean_log:
                    action = "batch decrypt"
                elif "ENCRYPT" in clean_log or "Encrypted" in clean_log:
                    action = "encrypt"
                elif "DECRYPT" in clean_log or "Decrypted" in clean_log:
                    action = "decrypt"
                
                

                color = color_map.get(action, Fore.WHITE) if use_colors else ""
                icon = icon_map.get(action, "•")
                reset = Style.RESET_ALL if use_colors else ""

                print(f"{color}{icon} {clean_log}{reset}\n")
                #print("-"*40,"\n")

            print("=" * 40,"\n")

    except FileNotFoundError:
        print("No activity log found.")

def main():
    while True:
        clear_screen()
        print_header()
        print_menu()
        icons = settings["use_icons"]
        color = Fore.YELLOW if settings["use_colors"] else ""
        reset = Style.RESET_ALL if settings["use_colors"] else ""
        choice = questionary.select(
            "Select an option:",
            choices=[
                f"1. {'🔐 ' if icons else ''}Encrypt a file",
                f"2. {'🔓 ' if icons else ''}Decrypt a file",
                f"3. {'📁 ' if icons else ''}Batch Encrypt (Directory)",
                f"4. {'📂 ' if icons else ''}Batch Decrypt (Directory)",
                f"5. {'⚙️  ' if icons else ''}Settings",
                f"6. {'📘 ' if icons else ''}Help & Usage Guide",
                f"7. {'📑' if icons else ''}View Recent Activities",
                f"8. {'❌ ' if icons else ''}Exit"
            ],
            style=custom_style
        ).ask().split(".")[0]

        if choice == '1':
            encrypt_file()
        elif choice == '2':
            decrypt_file()
        elif choice == '3':
            batch_encrypt()
        elif choice == '4':
            batch_decrypt()
        elif choice == '5':
            settings_menu()
        elif choice == '6':
            show_help()
        elif choice == '7':
            clear_screen()
            display_recent_activity(settings)
            input("\nPress Enter to return to the main menu...")
        elif choice == '8':
            print(Fore.CYAN + "\nGoodbye, stay safe!" + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()