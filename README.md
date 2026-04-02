# 🔐 PyCryptor: Multi-Algorithm File Security Tool

PyCryptor is a feature-rich CLI utility designed for encrypting and decrypting files and directories. It supports multiple encryption modes, batch processing, folder archiving, and includes educational "hacker demo" scripts to demonstrate the importance of strong passwords.

## ✨ Features

-   **Multiple Algorithms:** Choose between `AES-GCM` (Authenticated), `AES-CBC`, `ChaCha20`, and `Triple DES`.
-   **Batch Processing:** Encrypt or decrypt entire directories at once.
-   **Folder Encryption:** Automatically zips a folder and encrypts the resulting archive.
-   **Secure Key Derivation:** Uses `PBKDF2` with 100,000 iterations and a unique salt for every file.
-   **Rich User Interface:** 
    *   Interactive menus using `questionary`.
    *   Real-time progress bars via `rich`.
    *   Color-coded logging and activity history.
-   **Customizable Settings:** Set default algorithms, output directories, and toggle UI icons/colors.
-   **Hacker Demo:** Includes dictionary attack scripts for educational purposes to test password strength.

---

## 📂 Project Structure

```text
FileEncryptor/
├── main.py                 # Application entry point
├── encryption_operations.py # File and Batch logic
├── archive_operations.py    # Folder-to-Archive logic
├── settings_manager.py     # Configuration and settings menu
├── user_interface.py       # Menu layouts and styling
├── logging_utils.py        # Activity logging (log.txt)
├── settings.json           # User configuration file
├── algorithms/             # Cryptographic implementations
│   ├── aes_cbc.py
│   ├── aes_gcm.py
│   ├── chacha20.py
│   └── triple_des.py
└── hacker_demo/            # Educational attack scripts
    ├── dictionary_attack.py
    └── universal_dictionary_attack.py
```

---

## 🚀 Getting Started

### Prerequisites

-   Python 3.8+
-   `pip` (Python package manager)

### Installation

1.  **Clone or download** the project files.
2.  **Install dependencies**:
    ```bash
    pip install pycryptodome questionary colorama rich
    ```

### Running the Tool

Start the main interface:
```bash
python main.py
```

---

## 🛠 Usage Guide

1.  **Encrypt/Decrypt File:** Select a single file, choose your algorithm, and enter a password. The tool will output a `.enc` file (or decrypt one).
2.  **Batch Mode:** Point the tool to a directory. It will process all files inside (or all `.enc` files for decryption) using the same password and algorithm.
3.  **Encrypt Folder:** Select a folder. The tool will ZIP the contents into a temporary archive, encrypt it, and save it to your output path.
4.  **Settings:** Use the settings menu to:
    *   Change the `Default Output Directory`.
    *   Set a preferred `Default Algorithm`.
    *   Toggle `UI Icons` and `Colors`.

---

## 🛡️ Encryption Details

| Algorithm | Key Size | Mode | Notes |
| :--- | :--- | :--- | :--- |
| **AES-GCM** | 256-bit | Authenticated | **Recommended.** Provides both secrecy and integrity. |
| **AES-CBC** | 256-bit | Cipher Block Chaining | Classic standard; requires manual padding. |
| **ChaCha20** | 256-bit | Stream Cipher | High performance; excellent for software-only environments. |
| **Triple DES**| 192-bit | CBC | Legacy support; slower and less secure than AES. |

**Key Derivation:** All algorithms use **PBKDF2-HMAC-SHA256** with a random 16-byte salt and **100,000 iterations** to derive keys from your password, making brute-force attacks significantly harder.

---

## 🧪 Hacker Demo (Educational)

The `hacker_demo` folder contains scripts that demonstrate why using a weak password (e.g., "password123") makes encryption useless.

**How to use the Dictionary Attack:**
1.  Encrypt a file using a common word as a password.
2.  Run the attack script:
    ```bash
    python hacker_demo/universal_dictionary_attack.py --file secret.txt.enc --dictionary passwords.txt --algorithm aes-gcm
    ```
3.  If the password is in `passwords.txt`, the script will recover the file content instantly.

---

## ⚠️ Disclaimer

This tool is intended for **educational and personal use**. While it uses strong cryptographic standards, always ensure you:
-   **Never forget your password:** There is no "Password Recovery" feature. If the password is lost, the data is gone.
-   **Use strong passwords:** Use the Hacker Demo to see how easily weak passwords can be cracked.
-   **Verify for Production:** For highly sensitive enterprise data, consider audited solutions like VeraCrypt or BitLocker.

---
