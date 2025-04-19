# user_interface.py
import os
from colorama import Fore, Style, init
import questionary
from questionary import Style as QStyle

init(autoreset=True)

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

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_header(settings):
    if settings["use_colors"]:
        print(Fore.CYAN + """
╔════════════════════════════════════════╗
║     FILE ENCRYPTOR & DECRYPTOR TOOL    ║
╚════════════════════════════════════════╝
""" + Style.RESET_ALL)
    else:
        print("==== FILE ENCRYPTOR & DECRYPTOR TOOL ====")

def print_menu(settings):
    icons = settings["use_icons"]
    color = Fore.YELLOW if settings["use_colors"] else ""
    reset = Style.RESET_ALL if settings["use_colors"] else ""
    print(color + f"""
[1] {'🔐 ' if icons else ''}Encrypt a file
[2] {'🔓 ' if icons else ''}Decrypt a file
[3] {'📁 ' if icons else ''}Batch Encrypt (Directory)
[4] {'📂 ' if icons else ''}Batch Decrypt (Directory)
[5] {'🗃️ ' if icons else ''}Encrypt Folder (as Archive)
[6] {'🗃️ ' if icons else ''}Decrypt Archive
[7] {'⚙️  ' if icons else ''}Settings
[8] {'📘 ' if icons else ''}Help & Usage Guide
[9] {'📑 ' if icons else ''}View Recent Activities
[10] {'❌ ' if icons else ''}Exit
""" + reset)

def choose_algorithm():
    algorithms = {
        "AES-CBC": "aes-cbc",
        "AES-GCM": "aes-gcm",
        "ChaCha20": "chacha20",
        "Triple DES": "3des"
    }

    # This function now needs to access the current settings to get the default algorithm
    from settings_manager import load_settings
    settings = load_settings()
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

def show_help():
    clear_screen()
    # The header needs settings, but this function is called outside the main loop initially
    # We'll load settings here temporarily. A better approach might be to pass settings.
    from settings_manager import load_settings
    settings = load_settings()
    print_header(settings)
    print(Fore.YELLOW + "📘 Help & Usage Guide\n" + Style.RESET_ALL)
    try:
        with open("help.txt", "r") as help_file:
            print(help_file.read())
    except FileNotFoundError:
        print(Fore.RED + "Help file not found." + Style.RESET_ALL)
    input("\nPress Enter to return to the main menu...")

def display_recent_activity(settings):
    count = settings.get("recent_activity_count", 5)
    use_colors = settings.get("use_colors", True)
    use_icons = settings.get("use_icons", True)

    color_map = {
        "encrypt": Fore.GREEN,
        "decrypt": Fore.CYAN,
        "batch encrypt": Fore.MAGENTA,
        "batch decrypt": Fore.BLUE,
        "encrypt_archive": '\033[38;5;164m',
        "decrypt_archive": '\033[38;5;213m',
        "default": Fore.WHITE,
        "error": Fore.RED
    }

    icon_map = {
        "encrypt": "🔒",
        "decrypt": "🔓",
        "batch encrypt": "📁 🔒",
        "batch decrypt": "📂 🔓",
        "encrypt_archive": "🗃️ 🔒",
        "decrypt_archive": "🗃️ 🔓",
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
                elif "ENCRYPT_ARCHIVE" in clean_log:
                    action = "encrypt_archive"
                elif "DECRYPT_ARCHIVE" in clean_log:
                    action = "decrypt_archive"
                elif "ENCRYPT" in clean_log or "Encrypted" in clean_log:
                    action = "encrypt"
                elif "DECRYPT" in clean_log or "Decrypted" in clean_log:
                    action = "decrypt"

                color = color_map.get(action, Fore.WHITE) if use_colors else ""
                icon = icon_map.get(action, "•")
                reset = Style.RESET_ALL if use_colors else ""

                print(f"{color}{icon} {clean_log}{reset}\n")

            print("=" * 40,"\n")

    except FileNotFoundError:
        print("No activity log found.")