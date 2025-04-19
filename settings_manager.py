# settings_manager.py
import os
import json
from user_interface import autocomplete_path, questionary, QStyle
from colorama import Fore, Style
from time import sleep

SETTINGS_FILE = "settings.json"

# Setup Questionary Style (moved here as it's used in this module)
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

def settings_menu(current_settings):
    settings = current_settings.copy()  # Work on a copy to allow discarding

    while True:
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

        if selected is None:  # Handle Ctrl+C or Escape
            print(Fore.YELLOW + "[!] Changes discarded." + Style.RESET_ALL)
            sleep(1)
            return current_settings

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
            while True:
                try:
                    count_str = questionary.text(
                        "Number of recent logs to keep (default 5):",
                        default=str(settings.get("recent_activity_count", 5)),
                        style=custom_style
                    ).ask()
                    if count_str is None:  # Handle Ctrl+C or Escape
                        break
                    settings["recent_activity_count"] = int(count_str)
                    if settings["recent_activity_count"] < 0:
                        print(Fore.RED + "[!] Please enter a non-negative number." + Style.RESET_ALL)
                    else:
                        break
                except ValueError:
                    print(Fore.RED + "[!] Invalid input. Please enter a number." + Style.RESET_ALL)

        elif selected == "Save & Exit":
            save_settings(settings)
            print(Fore.GREEN + "[+] Settings updated successfully!" + Style.RESET_ALL)
            sleep(1)
            return settings

        elif selected == "Discard & Exit":
            print(Fore.YELLOW + "[!] Changes discarded." + Style.RESET_ALL)
            sleep(1)
            return current_settings