"""
CipherCraft - Random Password Generator
=======================================
Dual-mode launcher supporting both GUI (Advanced Tier) and CLI (Beginner Tier).

Usage:
  python main.py          # Launches the Graphical User Interface (GUI)
  python main.py --cli    # Launches the Command Line Interface (CLI)
  python main.py --help   # Displays usage information
"""

import sys
import argparse


def main():
    parser = argparse.ArgumentParser(
        description="CipherCraft - Cryptographically Secure Random Password Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py         Launch modern GUI interface
  python main.py --cli   Run interactive command-line mode
        """
    )
    parser.add_argument(
        "--cli", "-c",
        action="store_true",
        help="Run interactive Command Line Interface (Beginner Tier)"
    )

    args = parser.parse_args()

    if args.cli:
        from cli_generator import run_cli
        run_cli()
    else:
        try:
            from gui_generator import run_gui
            run_gui()
        except Exception as e:
            # If graphical display is not available, fallback gracefully to CLI
            print(f"⚠️  Could not start graphical window ({e}). Falling back to CLI mode...\n")
            from cli_generator import run_cli
            run_cli()


if __name__ == "__main__":
    main()
