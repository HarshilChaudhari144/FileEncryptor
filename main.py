# main.py
import os
from time import sleep
from colorama import Fore, Style

from encryption_operations import encrypt_file, decrypt_file, batch_encrypt, batch_decrypt
from archive_operations import encrypt_archive, decrypt_archive
from settings_manager import load_settings, settings_menu
from user_interface import clear_screen, print_header, print_menu, show_help, display_recent_activity, questionary, QStyle

def main():
    settings = load_settings()

    while True:
        clear_screen()
        print_header(settings)
        print_menu(settings)

        choice = questionary.select(
            "Select an option:",
            choices=[
                f"1. {'🔐 ' if settings['use_icons'] else ''}Encrypt a file",
                f"2. {'🔓 ' if settings['use_icons'] else ''}Decrypt a file",
                f"3. {'📁 ' if settings['use_icons'] else ''}Batch Encrypt (Directory)",
                f"4. {'📂 ' if settings['use_icons'] else ''}Batch Decrypt (Directory)",
                f"5. {'🗃️ ' if settings['use_icons'] else ''}Encrypt Folder (as Archive)",
                f"6. {'🗃️ ' if settings['use_icons'] else ''}Decrypt Archive",
                f"7. {'⚙️  ' if settings['use_icons'] else ''}Settings",
                f"8. {'📘 ' if settings['use_icons'] else ''}Help & Usage Guide",
                f"9. {'📑 ' if settings['use_icons'] else ''}View Recent Activities",
                f"10. {'❌ ' if settings['use_icons'] else ''}Exit",
            ],
            style=QStyle([
                ('qmark', 'fg:#E91E63 bold'),
                ('question', 'bold'),
                ('answer', 'fg:#00BCD4 bold'),
                ('pointer', 'fg:#673AB7 bold'),
                ('highlighted', 'fg:#03A9F4 bold'),
                ('selected', 'fg:#4CAF50'),
                ('separator', 'fg:#cc5454'),
                ('instruction', 'fg:#FFC107'),
            ])
        ).ask().split(".")[0]

        if choice == '1':
            encrypt_file(settings)
        elif choice == '2':
            decrypt_file(settings)
        elif choice == '3':
            batch_encrypt(settings)
        elif choice == '4':
            batch_decrypt(settings)
        elif choice == '5':
            encrypt_archive(settings)
        elif choice == '6':
            decrypt_archive(settings)
        elif choice == '7':
            updated_settings = settings_menu(settings)
            if updated_settings:
                settings = updated_settings
        elif choice == '8':
            show_help()
        elif choice == '9':
            clear_screen()
            display_recent_activity(settings)
            input("\nPress Enter to return to the main menu...")
        elif choice == '10':
            print(Fore.CYAN + "\nGoodbye, stay safe!" + Style.RESET_ALL)
            break

if __name__ == "__main__":
    main()