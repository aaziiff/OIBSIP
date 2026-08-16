"""
Core Password Generation Engine
--------------------------------
Implements cryptographically secure password generation using Python's `secrets` module,
rule validation, character set customization, ambiguous character filtering,
password entropy & strength evaluation, and in-memory session history.
"""

import math
import secrets
import string
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, List, Optional, Set, Tuple


# Character Pools
UPPERCASE_CHARS: str = string.ascii_uppercase
LOWERCASE_CHARS: str = string.ascii_lowercase
DIGIT_CHARS: str = string.digits
SYMBOL_CHARS: str = "!@#$%^&*()-_=+[]{}|;:,.<>?/"

# Ambiguous characters often confused in print / display
# (e.g., 0, O, o, 1, l, I, |, `, ', ", ;)
AMBIGUOUS_CHARS: Set[str] = {
    "0", "O", "o", "1", "l", "I", "|", "`", "'", '"', ";", ":", ",", ".", "~", "/"
}

MIN_PASSWORD_LENGTH: int = 8
MAX_PASSWORD_LENGTH: int = 128
MIN_CHARACTER_TYPES: int = 2


@dataclass
class PasswordCriteria:
    length: int = 16
    include_uppercase: bool = True
    include_lowercase: bool = True
    include_digits: bool = True
    include_symbols: bool = True
    exclude_ambiguous: bool = False


@dataclass
class PasswordStrength:
    score: int  # 0 to 100
    rating: str  # "Weak", "Medium", "Strong", "Very Strong"
    color: str  # Hex code for UI representation
    entropy_bits: float
    feedback: List[str]
    crack_time: str = ""


class PasswordEngine:
    """Cryptographically secure password generator engine."""

    def __init__(self, history_limit: int = 5):
        self.history_limit = history_limit
        self._history: Deque[str] = deque(maxlen=history_limit)

    @staticmethod
    def filter_ambiguous(char_set: str) -> str:
        """Removes ambiguous characters from a given character set string."""
        return "".join(ch for ch in char_set if ch not in AMBIGUOUS_CHARS)

    @classmethod
    def get_character_pools(cls, criteria: PasswordCriteria) -> Dict[str, str]:
        """
        Builds individual character pools based on user criteria.
        Returns a dictionary of category name -> available characters.
        """
        pools: Dict[str, str] = {}

        if criteria.include_uppercase:
            chars = cls.filter_ambiguous(UPPERCASE_CHARS) if criteria.exclude_ambiguous else UPPERCASE_CHARS
            if chars:
                pools["uppercase"] = chars

        if criteria.include_lowercase:
            chars = cls.filter_ambiguous(LOWERCASE_CHARS) if criteria.exclude_ambiguous else LOWERCASE_CHARS
            if chars:
                pools["lowercase"] = chars

        if criteria.include_digits:
            chars = cls.filter_ambiguous(DIGIT_CHARS) if criteria.exclude_ambiguous else DIGIT_CHARS
            if chars:
                pools["digits"] = chars

        if criteria.include_symbols:
            chars = cls.filter_ambiguous(SYMBOL_CHARS) if criteria.exclude_ambiguous else SYMBOL_CHARS
            if chars:
                pools["symbols"] = chars

        return pools

    @classmethod
    def validate_criteria(cls, criteria: PasswordCriteria) -> Tuple[bool, Optional[str]]:
        """
        Validates criteria according to Beginner and Advanced Tier constraints.
        Returns (is_valid, error_message).
        """
        if not isinstance(criteria.length, int):
            return False, "Password length must be an integer."

        if criteria.length < MIN_PASSWORD_LENGTH:
            return False, f"Password length must be at least {MIN_PASSWORD_LENGTH} characters."

        if criteria.length > MAX_PASSWORD_LENGTH:
            return False, f"Password length cannot exceed {MAX_PASSWORD_LENGTH} characters."

        selected_types_count = sum([
            criteria.include_uppercase,
            criteria.include_lowercase,
            criteria.include_digits,
            criteria.include_symbols,
        ])

        if selected_types_count < MIN_CHARACTER_TYPES:
            return False, f"At least {MIN_CHARACTER_TYPES} character types must be selected."

        pools = cls.get_character_pools(criteria)
        if len(pools) < MIN_CHARACTER_TYPES:
            return False, f"Selected character types yielded fewer than {MIN_CHARACTER_TYPES} valid pools after filtering."

        return True, None

    def generate(self, criteria: PasswordCriteria) -> str:
        """
        Generates a cryptographically secure password based on the criteria.
        Guarantees that at least one character from each selected category is included.
        Stores generated password in the in-memory session history.
        """
        is_valid, error_msg = self.validate_criteria(criteria)
        if not is_valid:
            raise ValueError(error_msg)

        pools = self.get_character_pools(criteria)
        password_chars: List[str] = []

        # 1. Guarantee at least one character from each selected category
        for category_chars in pools.values():
            password_chars.append(secrets.choice(category_chars))

        # 2. Combine all chosen pools for remaining characters
        combined_pool = "".join(pools.values())

        remaining_length = criteria.length - len(password_chars)
        for _ in range(remaining_length):
            password_chars.append(secrets.choice(combined_pool))

        # 3. Cryptographically shuffle the result to avoid predictable positions
        system_random = secrets.SystemRandom()
        system_random.shuffle(password_chars)

        password = "".join(password_chars)

        # 4. Add to session history
        self._history.appendleft(password)

        return password

    @property
    def history(self) -> List[str]:
        """Returns the in-memory session history of last generated passwords."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clears the in-memory session history."""
        self._history.clear()

    @staticmethod
    def calculate_strength(password: str) -> PasswordStrength:
        """
        Evaluates the password's strength based on entropy, length, and character diversity.
        Returns a PasswordStrength object with score (0-100), rating, color, entropy, and feedback.
        """
        if not password:
            return PasswordStrength(
                score=0,
                rating="None",
                color="#6B7280",
                entropy_bits=0.0,
                feedback=["Password is empty."],
            )

        length = len(password)
        has_upper = any(c in UPPERCASE_CHARS for c in password)
        has_lower = any(c in LOWERCASE_CHARS for c in password)
        has_digit = any(c in DIGIT_CHARS for c in password)
        has_symbol = any(c in SYMBOL_CHARS or (not c.isalnum() and not c.isspace()) for c in password)

        # Calculate character pool size (N)
        pool_size = 0
        if has_upper:
            pool_size += len(UPPERCASE_CHARS)
        if has_lower:
            pool_size += len(LOWERCASE_CHARS)
        if has_digit:
            pool_size += len(DIGIT_CHARS)
        if has_symbol:
            pool_size += len(SYMBOL_CHARS)

        pool_size = max(pool_size, 1)

        # Shannon / NIST Entropy bits: E = L * log2(N)
        entropy = length * math.log2(pool_size)

        # Diversity score calculation
        diversity_count = sum([has_upper, has_lower, has_digit, has_symbol])

        # Scoring heuristics (0-100)
        length_score = min(45, (length / 16) * 45)
        entropy_score = min(35, (entropy / 75) * 35)
        diversity_score = (diversity_count / 4) * 20

        total_score = int(round(length_score + entropy_score + diversity_score))
        total_score = max(5, min(100, total_score))

        feedback: List[str] = []
        if length < 10:
            feedback.append("Consider a length of 12+ characters for higher security.")
        if not has_upper:
            feedback.append("Add uppercase letters.")
        if not has_lower:
            feedback.append("Add lowercase letters.")
        if not has_digit:
            feedback.append("Add numbers.")
        if not has_symbol:
            feedback.append("Add special symbols.")

        # Classify strength tier
        if total_score < 40 or length < 8 or diversity_count < 2:
            rating = "Weak"
            color = "#EF4444"  # Red
        elif total_score < 75 or length < 12:
            rating = "Medium"
            color = "#F59E0B"  # Amber / Yellow
        elif total_score < 90:
            rating = "Strong"
            color = "#10B981"  # Emerald Green
        else:
            rating = "Very Strong"
            color = "#06B6D4"  # Cyan / Blue-Green

        # Estimate brute-force crack time assuming 10 billion guesses/sec
        guesses = 2 ** entropy
        seconds = (guesses / 2) / 10_000_000_000

        if seconds < 1:
            crack_time = "Instant (< 1 sec)"
        elif seconds < 60:
            crack_time = f"{int(seconds)} seconds"
        elif seconds < 3600:
            crack_time = f"{int(seconds // 60)} minutes"
        elif seconds < 86400:
            crack_time = f"{int(seconds // 3600)} hours"
        elif seconds < 31536000:
            crack_time = f"{int(seconds // 86400)} days"
        elif seconds < 31536000 * 1000:
            crack_time = f"{int(seconds // 31536000)} years"
        elif seconds < 31536000 * 1_000_000:
            crack_time = f"{int(seconds // (31536000 * 1000))}k years"
        elif seconds < 31536000 * 1_000_000_000:
            crack_time = f"{int(seconds // (31536000 * 1_000_000))}M years"
        else:
            crack_time = "Trillions of years"

        if not feedback:
            feedback.append("Great password! Meets high cryptographic diversity standards.")

        return PasswordStrength(
            score=total_score,
            rating=rating,
            color=color,
            entropy_bits=round(entropy, 1),
            feedback=feedback,
            crack_time=crack_time,
        )
