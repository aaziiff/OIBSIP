#!/usr/bin/env python3
"""
Oasis Infobyte - Task 2: BMI Calculator (Beginner Tier - CLI)
Author: Antigravity
Description: A robust command-line Body Mass Index (BMI) calculator
             with input validation, standard WHO classifications,
             and ideal weight recommendations.
"""

import sys


# ANSI Color Codes for terminal formatting
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"
    RESET = "\033[0m"


def print_banner():
    """Prints a styled banner for the CLI BMI Calculator."""
    print(f"\n{Colors.CYAN}{'=' * 58}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}         OASIS INFOBYTE - BMI CALCULATOR (CLI)         {Colors.RESET}")
    print(f"{Colors.CYAN}{'=' * 58}{Colors.RESET}")
    print(f"{Colors.BLUE}Calculate your Body Mass Index (BMI) & health category.{Colors.RESET}\n")


def get_positive_float_input(prompt: str, field_name: str, max_limit: float = 500.0) -> float:
    """
    Prompts the user for a numeric input, validating that it is a positive number
    and within realistic human bounds.
    
    Args:
        prompt: The input prompt string shown to the user.
        field_name: The name of the field (for error messages).
        max_limit: The maximum plausible value.

    Returns:
        float: The validated positive float value.
    """
    while True:
        user_input = input(f"{Colors.BOLD}{prompt}{Colors.RESET}").strip()
        
        # Check for empty input
        if not user_input:
            print(f"{Colors.RED}❌ Error: {field_name} cannot be empty. Please enter a number.{Colors.RESET}\n")
            continue
            
        # Check for non-numeric input
        try:
            val = float(user_input)
        except ValueError:
            print(f"{Colors.RED}❌ Error: Invalid input '{user_input}'. Please enter a valid numeric value for {field_name}.{Colors.RESET}\n")
            continue
            
        # Check for zero or negative values
        if val <= 0:
            print(f"{Colors.RED}❌ Error: {field_name} must be a positive number greater than 0.{Colors.RESET}\n")
            continue
            
        # Check for unrealistic upper limits
        if val > max_limit:
            print(f"{Colors.YELLOW}⚠️  Warning: {val} seems unrealistically high for {field_name} (max: {max_limit}). Please check your input.{Colors.RESET}\n")
            continue
            
        return val


def calculate_bmi(weight_kg: float, height_m: float) -> float:
    """
    Calculates Body Mass Index (BMI) using the standard formula:
    BMI = weight (kg) / (height (m) ^ 2)
    
    Args:
        weight_kg: Weight in kilograms.
        height_m: Height in meters.

    Returns:
        float: Calculated BMI value.
    """
    if height_m <= 0:
        raise ValueError("Height must be greater than zero.")
    return weight_kg / (height_m ** 2)


def classify_bmi(bmi: float) -> tuple[str, str, str]:
    """
    Classifies a BMI value into standard WHO categories.
    
    Categories:
      - Underweight: BMI < 18.5
      - Normal weight: 18.5 <= BMI < 25.0 (or 18.5 - 24.9)
      - Overweight: 25.0 <= BMI < 30.0 (or 25.0 - 29.9)
      - Obese: BMI >= 30.0
      
    Returns:
        tuple[str, str, str]: (Category Name, Color Code, Health Advice / Description)
    """
    if bmi < 18.5:
        return (
            "Underweight",
            Colors.BLUE,
            "Your BMI suggests you may be underweight. Consider consulting a healthcare professional for nutritional advice."
        )
    elif bmi < 25.0:
        return (
            "Normal weight",
            Colors.GREEN,
            "Congratulations! Your BMI falls within the healthy, normal weight range. Keep up the good work!"
        )
    elif bmi < 30.0:
        return (
            "Overweight",
            Colors.YELLOW,
            "Your BMI indicates you are in the overweight range. Regular exercise and balanced nutrition are recommended."
        )
    else:
        return (
            "Obese",
            Colors.RED,
            "Your BMI falls in the obese category. It is advisable to consult a healthcare provider for a personalized wellness plan."
        )


def calculate_healthy_weight_range(height_m: float) -> tuple[float, float]:
    """
    Calculates the ideal healthy weight range (BMI 18.5 to 24.9) for a given height.
    
    Args:
        height_m: Height in meters.
        
    Returns:
        tuple[float, float]: (min_healthy_weight_kg, max_healthy_weight_kg)
    """
    min_weight = 18.5 * (height_m ** 2)
    max_weight = 24.9 * (height_m ** 2)
    return round(min_weight, 2), round(max_weight, 2)


def display_results(weight_kg: float, height_m: float, bmi: float):
    """Prints a formatted summary of the BMI calculation and health category."""
    category, color, advice = classify_bmi(bmi)
    min_w, max_w = calculate_healthy_weight_range(height_m)
    
    print(f"\n{Colors.CYAN}{'─' * 58}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}                   CALCULATION RESULTS                   {Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 58}{Colors.RESET}")
    print(f" • Input Weight        : {weight_kg:.2f} kg")
    print(f" • Input Height        : {height_m:.2f} m ({height_m * 100:.1f} cm)")
    print(f" • Body Mass Index (BMI): {Colors.BOLD}{color}{bmi:.2f}{Colors.RESET}")
    print(f" • Health Category     : {Colors.BOLD}{color}{category}{Colors.RESET}")
    print(f" • Ideal Weight Range  : {min_w:.1f} kg – {max_w:.1f} kg (for your height)")
    print(f"{Colors.CYAN}{'─' * 58}{Colors.RESET}")
    print(f"{Colors.BOLD}Health Insight:{Colors.RESET}")
    print(f" {color}{advice}{Colors.RESET}")
    print(f"{Colors.CYAN}{'─' * 58}{Colors.RESET}\n")


def run_cli_session():
    """Runs a single interactive BMI calculation session."""
    print_banner()
    
    # Prompt for weight
    weight = get_positive_float_input(
        prompt="Enter your weight in kilograms (kg): ",
        field_name="Weight",
        max_limit=400.0
    )
    
    # Prompt for height with flexibility (supports meters or auto-detects cm)
    while True:
        height_input = get_positive_float_input(
            prompt="Enter your height in meters (m) [e.g., 1.75] or cm [e.g., 175]: ",
            field_name="Height",
            max_limit=300.0
        )
        
        # If user entered in centimeters (e.g. >= 30), auto-convert to meters
        if height_input >= 30.0:
            height_m = height_input / 100.0
            print(f"{Colors.CYAN}ℹ️  Interpreted {height_input:.1f} cm as {height_m:.2f} meters.{Colors.RESET}")
        else:
            height_m = height_input
            
        if height_m < 0.5 or height_m > 2.7:
            print(f"{Colors.YELLOW}⚠️  Height of {height_m:.2f}m is outside standard human range (0.5m - 2.7m). Please re-enter.{Colors.RESET}\n")
            continue
        break
        
    bmi = calculate_bmi(weight, height_m)
    display_results(weight, height_m, bmi)


def main():
    """Main loop allowing multiple calculations."""
    try:
        while True:
            run_cli_session()
            
            again = input(f"{Colors.BOLD}Would you like to calculate another BMI? (y/n): {Colors.RESET}").strip().lower()
            if again not in ('y', 'yes'):
                print(f"\n{Colors.GREEN}Thank you for using the BMI Calculator! Stay healthy! 👋{Colors.RESET}\n")
                break
    except (KeyboardInterrupt, EOFError):
        print(f"\n\n{Colors.YELLOW}Session interrupted. Goodbye! 👋{Colors.RESET}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
