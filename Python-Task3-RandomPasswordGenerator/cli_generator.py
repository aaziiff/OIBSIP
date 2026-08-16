"""
Command-Line Password Generator (Beginner Tier)
-----------------------------------------------
Interactive, beautiful terminal tool with clean input prompts, criteria selection,
entropy & crack-time analysis, clipboard auto-copying, and session loop.
"""

import sys
from typing import Optional
from password_engine import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_CHARACTER_TYPES,
    PasswordCriteria,
    PasswordEngine,
)

# Optional clipboard support
try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


# ANSI Color Codes for Clean Terminal Presentation
CLR_RESET = "\033[0m"
CLR_BOLD = "\033[1m"
CLR_CYAN = "\033[36m"
CLR_GREEN = "\033[32m"
CLR_YELLOW = "\033[33m"
CLR_RED = "\033[31m"
CLR_BLUE = "\033[34m"
CLR_MAGENTA = "\033[35m"
CLR_DIM = "\033[90m"


def print_banner() -> None:
    """Displays a clean CLI welcome banner."""
    print(f"\n{CLR_CYAN}{CLR_BOLD}┌────────────────────────────────────────────────────────────┐{CLR_RESET}")
    print(f"{CLR_CYAN}{CLR_BOLD}│             ⚡ CIPHERCRAFT PASSWORD GENERATOR              │{CLR_RESET}")
    print(f"{CLR_CYAN}{CLR_BOLD}└────────────────────────────────────────────────────────────┘{CLR_RESET}")
    print(f"  {CLR_DIM}🔒 256-bit CSPRNG • Entropy Evaluation • Zero Telemetry{CLR_RESET}\n")


def prompt_yes_no(prompt_text: str, default: bool = True) -> bool:
    """Prompts the user for a Yes/No answer with clean validation."""
    suffix = f" {CLR_DIM}[Y/n]{CLR_RESET}: " if default else f" {CLR_DIM}[y/N]{CLR_RESET}: "
    while True:
        try:
            choice = input(prompt_text + suffix).strip().lower()
        except (EOFError, KeyboardInterrupt):
            print()
            return False
        if not choice:
            return default
        if choice in ("y", "yes"):
            return True
        if choice in ("n", "no"):
            return False
        print(f"  {CLR_YELLOW}⚠️  Please enter 'y' for yes or 'n' for no.{CLR_RESET}")


def prompt_password_length() -> int:
    """Prompts the user for password length and validates >= 8."""
    while True:
        try:
            user_input = input(
                f"  {CLR_BOLD}Desired Password Length{CLR_RESET} ({MIN_PASSWORD_LENGTH}-{MAX_PASSWORD_LENGTH}) {CLR_DIM}[default: 16]{CLR_RESET}: "
            ).strip()
        except (EOFError, KeyboardInterrupt):
            print("\nExiting...")
            sys.exit(0)

        if not user_input:
            return 16

        if not user_input.isdigit():
            print(f"  {CLR_RED}❌ Invalid input! Please enter a valid whole number.{CLR_RESET}")
            continue

        length = int(user_input)
        if length < MIN_PASSWORD_LENGTH:
            print(f"  {CLR_RED}❌ Length too short! Minimum allowed length is {MIN_PASSWORD_LENGTH} characters.{CLR_RESET}")
            continue
        if length > MAX_PASSWORD_LENGTH:
            print(f"  {CLR_RED}❌ Length too long! Maximum allowed length is {MAX_PASSWORD_LENGTH} characters.{CLR_RESET}")
            continue

        return length


def prompt_character_types() -> PasswordCriteria:
    """Prompts user to select character types and validates at least 2 are selected."""
    while True:
        print(f"\n  {CLR_BOLD}Configure Character Rules{CLR_RESET} {CLR_DIM}(select at least 2 types){CLR_RESET}:")
        inc_upper = prompt_yes_no("    Include Uppercase Letters (A-Z)?", default=True)
        inc_lower = prompt_yes_no("    Include Lowercase Letters (a-z)?", default=True)
        inc_digits = prompt_yes_no("    Include Numbers (0-9)?", default=True)
        inc_symbols = prompt_yes_no("    Include Special Symbols (!@#$%...)?", default=True)
        exc_ambiguous = prompt_yes_no("    Exclude Ambiguous Characters (0, O, 1, l, I, etc.)?", default=False)

        selected_count = sum([inc_upper, inc_lower, inc_digits, inc_symbols])
        if selected_count < MIN_CHARACTER_TYPES:
            print(f"\n  {CLR_RED}❌ Validation Error: You selected {selected_count} character type(s).{CLR_RESET}")
            print(f"     {CLR_YELLOW}At least {MIN_CHARACTER_TYPES} character types are required for security.{CLR_RESET}")
            print(f"     Please try again.\n")
            continue

        return PasswordCriteria(
            length=16,
            include_uppercase=inc_upper,
            include_lowercase=inc_lower,
            include_digits=inc_digits,
            include_symbols=inc_symbols,
            exclude_ambiguous=exc_ambiguous,
        )


def copy_to_clipboard(text: str) -> bool:
    """Copies text to clipboard using pyperclip."""
    if HAS_PYPERCLIP:
        try:
            pyperclip.copy(text)
            return True
        except Exception:
            return False
    return False


def run_cli() -> None:
    """Main CLI generator loop with clean presentation."""
    engine = PasswordEngine(history_limit=5)
    print_banner()

    while True:
        try:
            length = prompt_password_length()
            criteria = prompt_character_types()
            criteria.length = length

            # Generate password
            password = engine.generate(criteria)
            strength = engine.calculate_strength(password)

            # Auto-copy
            copied = copy_to_clipboard(password)

            # Color coding for strength
            rating_color = CLR_GREEN if strength.rating in ("Strong", "Very Strong") else (CLR_YELLOW if strength.rating == "Medium" else CLR_RED)

            print(f"\n{CLR_CYAN}┌────────────────────────────────────────────────────────────┐{CLR_RESET}")
            print(f"{CLR_CYAN}│ {CLR_BOLD}GENERATED PASSWORD:{CLR_RESET}                                       {CLR_CYAN}│{CLR_RESET}")
            print(f"{CLR_CYAN}│ {CLR_GREEN}{CLR_BOLD}{password:<58}{CLR_RESET}{CLR_CYAN}│{CLR_RESET}")
            print(f"{CLR_CYAN}├────────────────────────────────────────────────────────────┤{CLR_RESET}")
            print(f"  {CLR_BOLD}Strength Rating{CLR_RESET} : {rating_color}{CLR_BOLD}{strength.rating}{CLR_RESET} ({strength.score}/100)")
            print(f"  {CLR_BOLD}Entropy Bits{CLR_RESET}    : {CLR_CYAN}{strength.entropy_bits} bits{CLR_RESET}")
            print(f"  {CLR_BOLD}Est. Crack Time{CLR_RESET} : {CLR_GREEN}~{strength.crack_time}{CLR_RESET}")
            if copied:
                print(f"  {CLR_BOLD}Clipboard{CLR_RESET}       : {CLR_GREEN}✓ Copied automatically!{CLR_RESET}")
            else:
                print(f"  {CLR_BOLD}Clipboard{CLR_RESET}       : {CLR_DIM}Install 'pyperclip' to enable auto-copying.{CLR_RESET}")

            if strength.feedback:
                print(f"  {CLR_BOLD}Feedback{CLR_RESET}        : {CLR_DIM}{' '.join(strength.feedback)}{CLR_RESET}")
            print(f"{CLR_CYAN}└────────────────────────────────────────────────────────────┘{CLR_RESET}")

            # Option to generate another password without restarting
            again = prompt_yes_no(f"\n  Generate another password?", default=True)
            if not again:
                print(f"\n  {CLR_CYAN}Thank you for using CipherCraft. Stay secure! 👋{CLR_RESET}\n")
                break
            print(f"\n{CLR_DIM}{'─' * 62}{CLR_RESET}\n")

        except (KeyboardInterrupt, EOFError):
            print(f"\n\n  {CLR_DIM}Operation cancelled by user. Exiting... 👋{CLR_RESET}\n")
            sys.exit(0)
        except Exception as err:
            print(f"\n  {CLR_RED}❌ An error occurred: {err}{CLR_RESET}")
            again = prompt_yes_no("  Would you like to try again?", default=True)
            if not again:
                break


if __name__ == "__main__":
    run_cli()
