# 🔐 CipherCraft — Random Password Generator

A robust, cryptographically secure Python tool that generates strong, customizable passwords based on user-defined criteria. Supports both a streamlined **Interactive Command-Line Interface (Beginner Tier)** and a modern **Graphical User Interface with Complexity Controls & History (Advanced Tier)**.

---

## 🌟 Feature Matrix

### 🟢 Beginner Tier (CLI)
- [x] **Enforced Length**: Minimum 8 characters enforced (customizable up to 128 characters).
- [x] **Character Type Selection**: Choose uppercase letters (`A-Z`), lowercase letters (`a-z`), numbers (`0-9`), and special symbols (`!@#$%...`).
- [x] **Multi-Type Security Rule**: Requires at least **2 character types** to be selected.
- [x] **Strict Input Validation**: Rejects invalid lengths, non-integers, or insufficient character type selections.
- [x] **Continuous Generation Loop**: Generate new passwords repeatedly without restarting the application.
- [x] **Clipboard Integration**: Automatically copies generated password to system clipboard via `pyperclip`.

### 🚀 Advanced Tier (GUI & Cryptographic Security)
- [x] **Modern Dark GUI Window**: Custom-styled slate/obsidian dark theme built with Tkinter.
- [x] **Synchronized Length Controls**: Real-time synchronized slider and numeric spinbox controls (8 to 64 characters).
- [x] **CSPRNG `secrets` Module**: Uses Python's cryptographically secure `secrets` library (SystemRandom) instead of pseudo-random generators.
- [x] **Security Guaranteed**: Guaranteed to contain **at least one character from each selected category**, followed by a cryptographic shuffle.
- [x] **Visual Password Strength Meter**: Live color-coded progress bar (Weak / Medium / Strong / Very Strong) with NIST Shannon entropy calculation in bits.
- [x] **Clipboard Auto-Copy & Manual Copy**: Passwords copy to clipboard automatically upon generation with visual toast feedback and explicit "Copy" button.
- [x] **Exclude Ambiguous Characters**: Checkbox toggle to eliminate easily confused characters (`0`, `O`, `o`, `1`, `l`, `I`, `|`, etc.).
- [x] **In-Memory Session History**: Displays the last 5 generated passwords with individual quick-copy buttons (never persisted to disk for security).

---

## 🛠️ Tech Stack

- **Language**: Python 3.8+
- **Security Engine**: `secrets` (Cryptographically Secure Pseudo-Random Number Generator - CSPRNG), `string`, `math`
- **GUI Framework**: `tkinter` + `ttk` with custom styling
- **Clipboard Management**: `pyperclip` (with Tkinter fallback)
- **Testing**: `unittest`

---

## 📂 Project Structure

```
Python-Task3-RandomPasswordGenerator/
├── password_engine.py       # Core cryptographic engine, entropy meter & history buffer
├── cli_generator.py         # Interactive CLI interface (Beginner Tier)
├── gui_generator.py         # Modern Dark-themed Tkinter GUI (Advanced Tier)
├── main.py                  # Dual-mode launcher (GUI by default, CLI with --cli)
├── requirements.txt         # Project dependencies
├── README.md                # Project documentation
└── tests/
    └── test_generator.py    # Automated test suite
```

---

## ⚡ Installation & Setup

1. **Clone or Navigate to the Repository**:
   ```bash
   cd Python-Task3-RandomPasswordGenerator
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

---

## 🚀 Usage

### 1. Launch Modern GUI (Default)
```bash
python main.py
```
*Or directly:*
```bash
python gui_generator.py
```

### 2. Launch Interactive CLI
```bash
python main.py --cli
```
*Or directly:*
```bash
python cli_generator.py
```

---

## 🧪 Running Automated Tests

Run the complete test suite to verify cryptographic rules, validation constraints, entropy calculations, and history tracking:

```bash
python3 -m unittest discover -s tests -v
```

---

## 🔒 Security Principles

1. **Cryptographic Randomness**: The generator relies on Python's `secrets` module, which interfaces directly with the operating system's kernel CSPRNG (`/dev/urandom` on Unix/macOS or `CryptGenRandom` on Windows).
2. **Deterministic Position Prevention**: Even after picking guaranteed characters from each selected pool, the final array is shuffled using `secrets.SystemRandom().shuffle()` to eliminate predictable character positions.
3. **Ephemeral History**: The generation history is strictly maintained in-memory (using `collections.deque`) and is discarded upon program exit. No passwords are ever written to disk or transmitted over networks.
