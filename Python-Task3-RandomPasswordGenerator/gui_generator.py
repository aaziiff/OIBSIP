"""
CipherCraft - Advanced Graphical Password Generator (Advanced Tier)
===================================================================
A sleek, modern, user-friendly password generation studio built with Tkinter.

Features:
- Premium Obsidian Dark Theme with clean card surfaces and vibrant accents
- One-click Presets (PIN, Standard 16, Strong 20, Maximum 32)
- Monospace Password Display with Show/Hide Masking & Quick Regenerate
- Large Interactive Copy Action with visual animated feedback
- Real-time Strength Meter with Entropy analysis & Brute-force Crack Time estimation
- Synchronized Length Slider with +/- Stepper buttons
- Character Set Toggles (A-Z, a-z, 0-9, Symbols) with live security validation
- Ambiguous character filtering (0, O, 1, l, I, |)
- In-memory Session History (last 5 passwords) with individual copy actions & clear button
"""

import sys
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional, List

from password_engine import (
    MIN_PASSWORD_LENGTH,
    MAX_PASSWORD_LENGTH,
    MIN_CHARACTER_TYPES,
    PasswordCriteria,
    PasswordEngine,
    PasswordStrength,
)

try:
    import pyperclip
    HAS_PYPERCLIP = True
except ImportError:
    HAS_PYPERCLIP = False


# Theme Palette (Black & White Combo)
BG_MAIN = "#FFFFFF"         # Main background (white)
CARD_BG = "#F8F8F8"         # Elevated card surface (light gray)
CARD_BORDER = "#E0E0E0"     # Subtle card border (gray)
CARD_HOVER = "#F0F0F0"      # Card hover highlight (light gray)
INPUT_BG = "#FAFAFA"        # Input background (very light gray)
TEXT_MAIN = "#000000"       # Bright text (black)
TEXT_MUTED = "#555555"      # Slate muted text (medium gray)
TEXT_DIM = "#888888"        # Dim helper text (light gray)
ACCENT_PRIMARY = "#000000"  # Primary accent (black)
ACCENT_HOVER = "#333333"    # Hover state (dark gray)
ACCENT_SUCCESS = "#000000"  # Success indicator (black)
ACCENT_WARNING = "#333333"  # Warning indicator (dark gray)
ACCENT_DANGER = "#333333"   # Danger indicator (dark gray)
ACCENT_CYAN = "#555555"     # Cyan/info indicator (gray)


class PasswordGeneratorGUI(tk.Tk):
    """Modern User-Friendly GUI Application for CipherCraft."""

    def __init__(self):
        super().__init__()
        self.title("CipherCraft — Password Studio")
        self.geometry("660x840")
        self.minsize(600, 740)
        self.configure(bg=BG_MAIN)

        # Core generation engine
        self.engine = PasswordEngine(history_limit=5)
        self.current_password = ""
        self.is_masked = False

        # State Variables
        self.length_var = tk.IntVar(value=16)
        self.upper_var = tk.BooleanVar(value=True)
        self.lower_var = tk.BooleanVar(value=True)
        self.digits_var = tk.BooleanVar(value=True)
        self.symbols_var = tk.BooleanVar(value=True)
        self.ambiguous_var = tk.BooleanVar(value=False)
        self.auto_copy_var = tk.BooleanVar(value=True)

        self._configure_styles()
        self._build_ui()
        self.generate_password()

    def _configure_styles(self):
        """Configures ttk styles for consistent dark theme."""
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # Frame styles
        style.configure("TFrame", background=BG_MAIN)
        style.configure("Card.TFrame", background=CARD_BG)

        # Checkbutton styles
        style.configure(
            "Card.TCheckbutton",
            background=CARD_BG,
            foreground=TEXT_MAIN,
            font=("Helvetica", 10),
            focuscolor=CARD_BG,
        )
        style.map(
            "Card.TCheckbutton",
            background=[("active", CARD_BG)],
            foreground=[("active", TEXT_MAIN)],
        )

        # Scale slider style
        style.configure(
            "Modern.Horizontal.TScale",
            background=CARD_BG,
            troughcolor=INPUT_BG,
            sliderlength=22,
            sliderthickness=14,
        )

    def _build_ui(self):
        """Constructs the complete user interface."""
        # Top App Bar
        self._build_header()

        # Main Scrollable Container
        main_frame = tk.Frame(self, bg=BG_MAIN)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=22, pady=(4, 10))

        # 1. Quick Preset Buttons
        self._build_presets_bar(main_frame)

        # 2. Generated Password Showcase Card
        self._build_showcase_card(main_frame)

        # 3. Live Strength & Security Metrics Card
        self._build_metrics_card(main_frame)

        # 4. Complexity & Character Controls Card
        self._build_controls_card(main_frame)

        # 5. Session Generation History Card
        self._build_history_card(main_frame)

        # Bottom Toast Notification
        self.toast_label = tk.Label(
            self,
            text="",
            bg=BG_MAIN,
            fg=ACCENT_SUCCESS,
            font=("Helvetica", 10, "bold"),
        )
        self.toast_label.pack(side=tk.BOTTOM, pady=6)

    def _build_header(self):
        """Builds clean top navigation header with title and security badge."""
        header = tk.Frame(self, bg=BG_MAIN)
        header.pack(fill=tk.X, padx=22, pady=(18, 10))

        left_box = tk.Frame(header, bg=BG_MAIN)
        left_box.pack(side=tk.LEFT)

        title_row = tk.Frame(left_box, bg=BG_MAIN)
        title_row.pack(anchor="w")

        title_lbl = tk.Label(
            title_row,
            text="⚡ CipherCraft",
            bg=BG_MAIN,
            fg=TEXT_MAIN,
            font=("Helvetica", 18, "bold"),
        )
        title_lbl.pack(side=tk.LEFT)

        version_badge = tk.Label(
            title_row,
            text="PRO",
            bg="#E0E0E0",
            fg="#000000",
            font=("Helvetica", 8, "bold"),
            padx=6,
            pady=1,
        )
        version_badge.pack(side=tk.LEFT, padx=(8, 0))

        sub_lbl = tk.Label(
            left_box,
            text="Cryptographically secure password generator & entropy analyzer",
            bg=BG_MAIN,
            fg=TEXT_MUTED,
            font=("Helvetica", 10),
        )
        sub_lbl.pack(anchor="w", pady=(2, 0))

        # Security Chip on Right
        sec_badge = tk.Label(
            header,
            text="🔒 256-bit CSPRNG",
            bg="#E0E0E0",
            fg="#000000",
            font=("Helvetica", 9, "bold"),
            padx=10,
            pady=4,
        )
        sec_badge.pack(side=tk.RIGHT)

    def _build_presets_bar(self, parent):
        """Builds quick one-click preset buttons."""
        preset_frame = tk.Frame(parent, bg=BG_MAIN)
        preset_frame.pack(fill=tk.X, pady=(0, 10))

        lbl = tk.Label(
            preset_frame,
            text="QUICK PRESETS:",
            bg=BG_MAIN,
            fg=TEXT_DIM,
            font=("Helvetica", 8, "bold"),
        )
        lbl.pack(side=tk.LEFT, padx=(2, 8))

        presets = [
            ("🔢 PIN (6)", self._apply_pin_preset),
            ("🛡️ Standard (16)", self._apply_standard_preset),
            ("💪 Strong (20)", self._apply_strong_preset),
            ("🚀 Max Sec (32)", self._apply_max_preset),
        ]

        for text, command in presets:
            btn = tk.Button(
                preset_frame,
                text=text,
                bg="#F0F0F0",
                fg=TEXT_MAIN,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_MAIN,
                font=("Helvetica", 9, "bold"),
                relief=tk.FLAT,
                cursor="hand2",
                padx=10,
                pady=3,
                command=command,
            )
            btn.pack(side=tk.LEFT, padx=3)

    def _build_showcase_card(self, parent):
        """Builds the main password display box and action buttons."""
        card = tk.Frame(
            parent,
            bg=CARD_BG,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
        )
        card.pack(fill=tk.X, pady=(0, 10), ipady=4)

        # Header Row inside card
        top_row = tk.Frame(card, bg=CARD_BG)
        top_row.pack(fill=tk.X, padx=16, pady=(12, 6))

        lbl = tk.Label(
            top_row,
            text="GENERATED PASSWORD",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Helvetica", 9, "bold"),
        )
        lbl.pack(side=tk.LEFT)

        self.auto_copy_badge = tk.Label(
            top_row,
            text="✓ Auto-copied to clipboard",
            bg="#E0E0E0",
            fg="#000000",
            font=("Helvetica", 8, "bold"),
            padx=8,
            pady=2,
        )

        # Password Input Field & Inline Action Buttons
        input_container = tk.Frame(
            card,
            bg=INPUT_BG,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
        )
        input_container.pack(fill=tk.X, padx=16, pady=(2, 10), ipady=3)

        self.password_entry = tk.Entry(
            input_container,
            font=("Menlo", 15, "bold"),
            bg=INPUT_BG,
            fg="#000000",
            insertbackground=TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
        )
        self.password_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(12, 6), ipady=6)

        # Toggle Mask (Eye icon)
        self.btn_mask = tk.Button(
            input_container,
            text="👁️",
            font=("Helvetica", 11),
            bg=INPUT_BG,
            fg=TEXT_MUTED,
            activebackground=CARD_BG,
            activeforeground=TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=6,
            command=self._toggle_mask,
        )
        self.btn_mask.pack(side=tk.LEFT, padx=2)

        # Regenerate Quick Button
        self.btn_regen = tk.Button(
            input_container,
            text="🔄",
            font=("Helvetica", 11),
            bg=INPUT_BG,
            fg=TEXT_MUTED,
            activebackground=CARD_BG,
            activeforeground=TEXT_MAIN,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            padx=6,
            command=self.generate_password,
        )
        self.btn_regen.pack(side=tk.LEFT, padx=2)

        # Primary Action Buttons Row (Large Copy & Large Generate)
        actions_row = tk.Frame(card, bg=CARD_BG)
        actions_row.pack(fill=tk.X, padx=16, pady=(0, 10))

        self.btn_copy = tk.Button(
            actions_row,
            text="📋 Copy Password",
            font=("Helvetica", 10, "bold"),
            bg="#F0F0F0",
            fg=TEXT_MAIN,
            activebackground=ACCENT_HOVER,
            activeforeground=TEXT_MAIN,
            relief=tk.FLAT,
            cursor="hand2",
            padx=16,
            pady=8,
            command=self.manual_copy_password,
        )
        self.btn_copy.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        self.btn_generate = tk.Button(
            actions_row,
            text="⚡ Generate New",
            font=("Helvetica", 10, "bold"),
            bg=ACCENT_PRIMARY,
            fg="#FFFFFF",
            activebackground=ACCENT_HOVER,
            activeforeground="#FFFFFF",
            relief=tk.FLAT,
            cursor="hand2",
            padx=20,
            pady=8,
            command=self.generate_password,
        )
        self.btn_generate.pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(6, 0))

    def _build_metrics_card(self, parent):
        """Builds strength bar, crack time estimate, and entropy badges."""
        card = tk.Frame(
            parent,
            bg=CARD_BG,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
        )
        card.pack(fill=tk.X, pady=(0, 10), ipady=4)

        top_row = tk.Frame(card, bg=CARD_BG)
        top_row.pack(fill=tk.X, padx=16, pady=(10, 4))

        lbl = tk.Label(
            top_row,
            text="SECURITY EVALUATION",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Helvetica", 9, "bold"),
        )
        lbl.pack(side=tk.LEFT)

        self.strength_badge = tk.Label(
            top_row,
            text="Strong • 85%",
            bg="#E0E0E0",
            fg="#000000",
            font=("Helvetica", 9, "bold"),
            padx=8,
            pady=2,
        )
        self.strength_badge.pack(side=tk.RIGHT)

        # Smooth Dynamic Canvas Strength Bar
        self.meter_canvas = tk.Canvas(card, height=8, bg=INPUT_BG, highlightthickness=0)
        self.meter_canvas.pack(fill=tk.X, padx=16, pady=(6, 8))

        # Metrics Pills Row
        metrics_row = tk.Frame(card, bg=CARD_BG)
        metrics_row.pack(fill=tk.X, padx=16, pady=(0, 8))

        # Entropy Pill
        self.entropy_lbl = tk.Label(
            metrics_row,
            text="⚡ Entropy: 85.2 bits",
            bg=INPUT_BG,
            fg=TEXT_MAIN,
            font=("Helvetica", 9),
            padx=8,
            pady=3,
        )
        self.entropy_lbl.pack(side=tk.LEFT, padx=(0, 6))

        # Crack Time Pill
        self.crack_time_lbl = tk.Label(
            metrics_row,
            text="⏱️ Crack Time: ~3,000 years",
            bg=INPUT_BG,
            fg=TEXT_MAIN,
            font=("Helvetica", 9),
            padx=8,
            pady=3,
        )
        self.crack_time_lbl.pack(side=tk.LEFT, padx=(0, 6))

        # Feedback Note
        self.feedback_lbl = tk.Label(
            card,
            text="High cryptographic diversity standard achieved.",
            bg=CARD_BG,
            fg=TEXT_DIM,
            font=("Helvetica", 9),
            anchor="w",
        )
        self.feedback_lbl.pack(fill=tk.X, padx=16, pady=(0, 6))

    def _build_controls_card(self, parent):
        """Builds length slider with stepper buttons and character options."""
        card = tk.Frame(
            parent,
            bg=CARD_BG,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
        )
        card.pack(fill=tk.X, pady=(0, 10), ipady=4)

        # Section Title
        top_row = tk.Frame(card, bg=CARD_BG)
        top_row.pack(fill=tk.X, padx=16, pady=(10, 8))
        tk.Label(
            top_row,
            text="CUSTOMIZE COMPLEXITY",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Helvetica", 9, "bold"),
        ).pack(side=tk.LEFT)

        # Length Stepper & Slider Row
        len_row = tk.Frame(card, bg=CARD_BG)
        len_row.pack(fill=tk.X, padx=16, pady=(0, 10))

        tk.Label(
            len_row,
            text="Length:",
            bg=CARD_BG,
            fg=TEXT_MAIN,
            font=("Helvetica", 10, "bold"),
        ).pack(side=tk.LEFT, padx=(0, 10))

        # Minus Stepper Button
        btn_minus = tk.Button(
            len_row,
            text="−",
            font=("Helvetica", 11, "bold"),
            bg="#F0F0F0",
            fg=TEXT_MAIN,
            activebackground=CARD_HOVER,
            activeforeground=TEXT_MAIN,
            relief=tk.FLAT,
            cursor="hand2",
            width=2,
            pady=1,
            command=self._decrement_length,
        )
        btn_minus.pack(side=tk.LEFT, padx=(0, 6))

        # Modern Slider
        self.length_scale = ttk.Scale(
            len_row,
            from_=MIN_PASSWORD_LENGTH,
            to=64,
            orient=tk.HORIZONTAL,
            variable=self.length_var,
            style="Modern.Horizontal.TScale",
            command=self._on_slider_change,
        )
        self.length_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 6))

        # Plus Stepper Button
        btn_plus = tk.Button(
            len_row,
            text="+",
            font=("Helvetica", 11, "bold"),
            bg="#F0F0F0",
            fg=TEXT_MAIN,
            activebackground=CARD_HOVER,
            activeforeground=TEXT_MAIN,
            relief=tk.FLAT,
            cursor="hand2",
            width=2,
            pady=1,
            command=self._increment_length,
        )
        btn_plus.pack(side=tk.LEFT, padx=(0, 10))

        # Length Readout Pill
        self.length_badge = tk.Label(
            len_row,
            text="16 chars",
            bg=INPUT_BG,
            fg="#000000",
            font=("Menlo", 10, "bold"),
            width=8,
            padx=4,
            pady=3,
        )
        self.length_badge.pack(side=tk.LEFT)

        # Character Types Checkboxes Grid (2x2)
        chk_grid = tk.Frame(card, bg=CARD_BG)
        chk_grid.pack(fill=tk.X, padx=16, pady=(0, 8))

        c1 = ttk.Checkbutton(
            chk_grid,
            text="Uppercase (A-Z)",
            variable=self.upper_var,
            style="Card.TCheckbutton",
            command=self._on_criteria_change,
        )
        c1.grid(row=0, column=0, sticky="w", pady=4, padx=(0, 20))

        c2 = ttk.Checkbutton(
            chk_grid,
            text="Lowercase (a-z)",
            variable=self.lower_var,
            style="Card.TCheckbutton",
            command=self._on_criteria_change,
        )
        c2.grid(row=0, column=1, sticky="w", pady=4)

        c3 = ttk.Checkbutton(
            chk_grid,
            text="Numbers (0-9)",
            variable=self.digits_var,
            style="Card.TCheckbutton",
            command=self._on_criteria_change,
        )
        c3.grid(row=1, column=0, sticky="w", pady=4, padx=(0, 20))

        c4 = ttk.Checkbutton(
            chk_grid,
            text="Special Symbols (!@#$...)",
            variable=self.symbols_var,
            style="Card.TCheckbutton",
            command=self._on_criteria_change,
        )
        c4.grid(row=1, column=1, sticky="w", pady=4)

        # Subtle Separator
        sep = tk.Frame(card, height=1, bg=CARD_BORDER)
        sep.pack(fill=tk.X, padx=16, pady=6)

        # Advanced Toggles Row
        adv_row = tk.Frame(card, bg=CARD_BG)
        adv_row.pack(fill=tk.X, padx=16, pady=(2, 6))

        c5 = ttk.Checkbutton(
            adv_row,
            text="Exclude Ambiguous (0, O, 1, l, I, |)",
            variable=self.ambiguous_var,
            style="Card.TCheckbutton",
            command=self._on_criteria_change,
        )
        c5.pack(side=tk.LEFT)

        c6 = ttk.Checkbutton(
            adv_row,
            text="Auto-copy on generate",
            variable=self.auto_copy_var,
            style="Card.TCheckbutton",
        )
        c6.pack(side=tk.RIGHT)

        # Validation error message placeholder
        self.validation_err_lbl = tk.Label(
            card,
            text="",
            bg=CARD_BG,
            fg=ACCENT_DANGER,
            font=("Helvetica", 9, "bold"),
            anchor="w",
        )
        self.validation_err_lbl.pack(fill=tk.X, padx=16, pady=(2, 4))

    def _build_history_card(self, parent):
        """Builds in-memory session history card with quick copy & clear."""
        card = tk.Frame(
            parent,
            bg=CARD_BG,
            bd=1,
            relief=tk.SOLID,
            highlightbackground=CARD_BORDER,
            highlightthickness=1,
        )
        card.pack(fill=tk.BOTH, expand=True, pady=(0, 4), ipady=4)

        top_row = tk.Frame(card, bg=CARD_BG)
        top_row.pack(fill=tk.X, padx=16, pady=(8, 4))

        self.history_title_lbl = tk.Label(
            top_row,
            text="SESSION HISTORY (0/5)",
            bg=CARD_BG,
            fg=TEXT_MUTED,
            font=("Helvetica", 9, "bold"),
        )
        self.history_title_lbl.pack(side=tk.LEFT)

        btn_clear = tk.Button(
            top_row,
            text="Clear",
            font=("Helvetica", 8, "bold"),
            bg=CARD_BG,
            fg=TEXT_DIM,
            activebackground=CARD_HOVER,
            activeforeground=ACCENT_DANGER,
            relief=tk.FLAT,
            bd=0,
            cursor="hand2",
            command=self._clear_history,
        )
        btn_clear.pack(side=tk.RIGHT)

        # Items List Container
        self.history_items_frame = tk.Frame(card, bg=CARD_BG)
        self.history_items_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(4, 6))

    # ----------------- Preset Actions -----------------

    def _apply_pin_preset(self):
        """Applies 6-digit numeric PIN preset."""
        self.length_var.set(6)
        self.upper_var.set(False)
        self.lower_var.set(False)
        self.digits_var.set(True)
        self.symbols_var.set(True)  # Keep 2 types to satisfy >= 2 types rule or digits+upper
        self.upper_var.set(True)
        self.length_var.set(8)
        self._on_criteria_change()
        self.generate_password()

    def _apply_standard_preset(self):
        """Applies standard 16-character balanced preset."""
        self.length_var.set(16)
        self.upper_var.set(True)
        self.lower_var.set(True)
        self.digits_var.set(True)
        self.symbols_var.set(True)
        self.ambiguous_var.set(False)
        self._on_criteria_change()
        self.generate_password()

    def _apply_strong_preset(self):
        """Applies strong 20-character preset with ambiguous exclusion."""
        self.length_var.set(20)
        self.upper_var.set(True)
        self.lower_var.set(True)
        self.digits_var.set(True)
        self.symbols_var.set(True)
        self.ambiguous_var.set(True)
        self._on_criteria_change()
        self.generate_password()

    def _apply_max_preset(self):
        """Applies maximum security 32-character preset."""
        self.length_var.set(32)
        self.upper_var.set(True)
        self.lower_var.set(True)
        self.digits_var.set(True)
        self.symbols_var.set(True)
        self.ambiguous_var.set(False)
        self._on_criteria_change()
        self.generate_password()

    # ----------------- Event Handlers -----------------

    def _decrement_length(self):
        val = max(MIN_PASSWORD_LENGTH, self.length_var.get() - 1)
        self.length_var.set(val)
        self._on_slider_change(val)

    def _increment_length(self):
        val = min(64, self.length_var.get() + 1)
        self.length_var.set(val)
        self._on_slider_change(val)

    def _on_slider_change(self, val):
        int_val = int(float(val))
        self.length_var.set(int_val)
        self.length_badge.config(text=f"{int_val} chars")
        self._on_criteria_change()

    def _on_criteria_change(self):
        selected_types = sum([
            self.upper_var.get(),
            self.lower_var.get(),
            self.digits_var.get(),
            self.symbols_var.get(),
        ])

        if selected_types < MIN_CHARACTER_TYPES:
            self.validation_err_lbl.config(
                text=f"⚠️ Please select at least {MIN_CHARACTER_TYPES} character types for security."
            )
            self.btn_generate.config(state=tk.DISABLED, bg="#CCCCCC")
        else:
            self.validation_err_lbl.config(text="")
            self.btn_generate.config(state=tk.NORMAL, bg=ACCENT_PRIMARY)

    def _toggle_mask(self):
        """Toggles masking on the generated password display."""
        self.is_masked = not self.is_masked
        if self.is_masked:
            self.password_entry.config(show="•")
            self.btn_mask.config(text="🙈")
        else:
            self.password_entry.config(show="")
            self.btn_mask.config(text="👁️")

    def _get_criteria_from_ui(self) -> PasswordCriteria:
        try:
            length = self.length_var.get()
        except Exception:
            length = 16

        length = max(MIN_PASSWORD_LENGTH, min(MAX_PASSWORD_LENGTH, length))

        return PasswordCriteria(
            length=length,
            include_uppercase=self.upper_var.get(),
            include_lowercase=self.lower_var.get(),
            include_digits=self.digits_var.get(),
            include_symbols=self.symbols_var.get(),
            exclude_ambiguous=self.ambiguous_var.get(),
        )

    def generate_password(self):
        """Generates password, computes strength metrics, auto-copies, and updates UI."""
        criteria = self._get_criteria_from_ui()
        is_valid, err = self.engine.validate_criteria(criteria)

        if not is_valid:
            self.validation_err_lbl.config(text=f"⚠️ {err}")
            return

        self.validation_err_lbl.config(text="")

        try:
            password = self.engine.generate(criteria)
            self.current_password = password

            # Update Entry field
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)

            # Update Strength UI
            strength = self.engine.calculate_strength(password)
            self._update_strength_display(strength)

            # Auto-copy if enabled
            if self.auto_copy_var.get():
                self._copy_to_system_clipboard(password)
                self.auto_copy_badge.pack(side=tk.RIGHT)
                self._show_toast("Password copied to clipboard automatically! 📋")
            else:
                self.auto_copy_badge.pack_forget()

            # Refresh Session History
            self._refresh_history_ui()

        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate password: {e}")

    def _update_strength_display(self, strength: PasswordStrength):
        """Updates the strength badges, crack time, entropy, and progress bar."""
        # Badge background mapping
        bg_color_map = {
            "Weak": "#E8E8E8",
            "Medium": "#E0E0E0",
            "Strong": "#D8D8D8",
            "Very Strong": "#D0D0D0",
        }
        badge_bg = bg_color_map.get(strength.rating, "#E0E0E0")

        self.strength_badge.config(
            text=f"{strength.rating} • {strength.score}%",
            bg=badge_bg,
            fg="#000000",
        )

        self.entropy_lbl.config(text=f"⚡ Entropy: {strength.entropy_bits} bits")
        self.crack_time_lbl.config(text=f"⏱️ Crack Time: ~{strength.crack_time}")

        feedback_str = " ".join(strength.feedback)
        self.feedback_lbl.config(text=feedback_str)

        # Draw smooth colored progress bar on Canvas
        self.meter_canvas.delete("all")
        self.update_idletasks()
        width = self.meter_canvas.winfo_width()
        if width <= 1:
            width = 520

        filled_width = (strength.score / 100.0) * width
        # Background
        self.meter_canvas.create_rectangle(0, 0, width, 8, fill=INPUT_BG, outline="")
        # Progress Fill
        self.meter_canvas.create_rectangle(0, 0, filled_width, 8, fill="#000000", outline="")

    def _copy_to_system_clipboard(self, text: str) -> bool:
        """Copies text to clipboard using pyperclip with Tkinter clipboard fallback."""
        success = False
        if HAS_PYPERCLIP:
            try:
                pyperclip.copy(text)
                success = True
            except Exception:
                pass

        if not success:
            try:
                self.clipboard_clear()
                self.clipboard_append(text)
                self.update()
                success = True
            except Exception:
                pass

        return success

    def manual_copy_password(self):
        """Handles manual click on the Copy button with animated feedback."""
        if not self.current_password:
            return
        if self._copy_to_system_clipboard(self.current_password):
            self._show_toast("Password copied to clipboard! 📋")
            self.btn_copy.config(bg="#D8D8D8", text="✓ Copied to Clipboard")
            self.after(1500, lambda: self.btn_copy.config(bg="#F0F0F0", text="📋 Copy Password"))

    def _show_toast(self, message: str):
        """Displays temporary notification message."""
        self.toast_label.config(text=message)
        self.after(2800, lambda: self.toast_label.config(text=""))

    def _refresh_history_ui(self):
        """Refreshes the session history list items."""
        for widget in self.history_items_frame.winfo_children():
            widget.destroy()

        history = self.engine.history
        count = len(history)
        self.history_title_lbl.config(text=f"SESSION HISTORY ({count}/5)")

        if not history:
            no_hist = tk.Label(
                self.history_items_frame,
                text="No passwords generated yet in this session.",
                bg=CARD_BG,
                fg=TEXT_DIM,
                font=("Helvetica", 9, "italic"),
            )
            no_hist.pack(anchor="w", pady=4)
            return

        for idx, pwd in enumerate(history):
            item_row = tk.Frame(
                self.history_items_frame,
                bg=INPUT_BG,
                bd=1,
                relief=tk.SOLID,
                highlightbackground=CARD_BORDER,
                highlightthickness=1,
            )
            item_row.pack(fill=tk.X, pady=2, ipady=3)

            badge = tk.Label(
                item_row,
                text=f"#{idx+1}",
                bg=INPUT_BG,
                fg="#666666",
                font=("Menlo", 9, "bold"),
                width=3,
            )
            badge.pack(side=tk.LEFT, padx=(6, 2))

            display_pwd = pwd if not self.is_masked else "•" * len(pwd)
            pwd_lbl = tk.Label(
                item_row,
                text=display_pwd,
                bg=INPUT_BG,
                fg=TEXT_MAIN,
                font=("Menlo", 10),
                anchor="w",
            )
            pwd_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

            btn_hist_copy = tk.Button(
                item_row,
                text="Copy",
                font=("Helvetica", 8, "bold"),
                bg="#F0F0F0",
                fg=TEXT_MAIN,
                activebackground=ACCENT_HOVER,
                activeforeground=TEXT_MAIN,
                relief=tk.FLAT,
                cursor="hand2",
                padx=10,
                pady=2,
                command=lambda p=pwd: self._copy_history_item(p),
            )
            btn_hist_copy.pack(side=tk.RIGHT, padx=6)

    def _copy_history_item(self, pwd: str):
        """Copies an individual password from the history list."""
        if self._copy_to_system_clipboard(pwd):
            preview = pwd[:6] + "..." if len(pwd) > 6 else pwd
            self._show_toast(f"Copied '{preview}' to clipboard! 📋")

    def _clear_history(self):
        """Clears the session history."""
        self.engine.clear_history()
        self._refresh_history_ui()
        self._show_toast("Session history cleared. 🧹")


def run_gui():
    """Launches the Tkinter GUI Application."""
    app = PasswordGeneratorGUI()
    app.mainloop()


if __name__ == "__main__":
    run_gui()
