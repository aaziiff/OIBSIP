#!/usr/bin/env python3
"""
Oasis Infobyte - Task 2: BMI Calculator (Main Launcher)
Author: Antigravity
Description: Unified entry point for the BMI Calculator. Launches the
             Advanced GUI Application by default or the Beginner CLI Tool
             via command-line arguments (--cli).
"""

import sys
import argparse


def show_banner():
    print("=" * 60)
    print("        OASIS INFOBYTE - TASK 2: BMI CALCULATOR        ")
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(
        description="Oasis Infobyte Task 2 - BMI Calculator (Beginner & Advanced Tiers)"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run the Beginner Tier Command-Line Interface (CLI) version"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run the Advanced Tier Graphical User Interface (GUI) version (default)"
    )
    args = parser.parse_args()

    if args.cli:
        from bmi_calculator_cli import main as run_cli
        run_cli()
    elif args.gui:
        from bmi_calculator_gui import launch_gui
        launch_gui()
    else:
        # If no flag passed, try launching GUI; fallback to CLI if GUI fails (e.g. headless environment)
        try:
            from bmi_calculator_gui import launch_gui
            launch_gui()
        except Exception as e:
            print(f"Note: Could not launch GUI ({e}). Switching to CLI mode...\n")
            from bmi_calculator_cli import main as run_cli
            run_cli()


if __name__ == "__main__":
    main()
