"""
Oasis Infobyte - Task 2: BMI Calculator (Advanced Tier - GUI Application)
Author: Antigravity
Description: A full-featured, modern Tkinter GUI application featuring
             multi-user profiles, unit conversion (Metric/Imperial),
             SQLite persistence, color-coded health badges, dynamic gauge,
             and embedded Matplotlib trend visualization.
"""

import sys
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import Optional, List, Dict, Any

# Embedded Matplotlib for trend visualization
try:
    import matplotlib
    matplotlib.use("TkAgg")
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    import matplotlib.dates as mdates
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from database import get_db, DatabaseError
from bmi_calculator_cli import calculate_bmi, classify_bmi, calculate_healthy_weight_range


# Color Palette
BG_MAIN = "#F1F5F9"        # Slate 100
CARD_BG = "#FFFFFF"        # Pure White
PRIMARY = "#2563EB"        # Blue 600
PRIMARY_HOVER = "#1D4ED8"  # Blue 700
TEXT_MAIN = "#0F172A"      # Slate 900
TEXT_MUTED = "#64748B"     # Slate 500
BORDER_COLOR = "#E2E8F0"   # Slate 200

# Health Classification Colors
COLOR_UNDERWEIGHT = "#3B82F6"  # Blue 500
COLOR_NORMAL = "#10B981"       # Emerald 500
COLOR_OVERWEIGHT = "#F59E0B"   # Amber 500
COLOR_OBESE = "#EF4444"        # Red 500


class BMICalculatorApp(tk.Tk):
    """Main Application Window for the Advanced BMI Calculator."""

    def __init__(self):
        super().__init__()
        self.title("BMI Calculator & Health Tracker — Oasis Infobyte")
        self.geometry("1100x750")
        self.minsize(950, 680)
        self.configure(bg=BG_MAIN)

        # Database initialization
        try:
            self.db = get_db()
        except DatabaseError as e:
            messagebox.showerror("Database Initialization Error", str(e))
            self.destroy()
            return

        self.current_user: Optional[Dict[str, Any]] = None
        self.user_records: List[Dict[str, Any]] = []

        # Setup UI styles and components
        self._setup_styles()
        self._create_header()
        self._create_main_layout()
        self._load_users()

    def _setup_styles(self):
        """Configures ttk widget styles for a modern, sleek appearance."""
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # General frame style
        self.style.configure("TFrame", background=BG_MAIN)
        self.style.configure("Card.TFrame", background=CARD_BG, relief="flat")
        self.style.configure("Header.TFrame", background="#1E293B")

        # Label styles
        self.style.configure("TLabel", background=BG_MAIN, foreground=TEXT_MAIN, font=("Helvetica", 11))
        self.style.configure("CardLabel.TLabel", background=CARD_BG, foreground=TEXT_MAIN, font=("Helvetica", 11))
        self.style.configure("CardTitle.TLabel", background=CARD_BG, foreground=TEXT_MAIN, font=("Helvetica", 13, "bold"))
        self.style.configure("Muted.TLabel", background=CARD_BG, foreground=TEXT_MUTED, font=("Helvetica", 10))

        # Button styles
        self.style.configure(
            "Primary.TButton",
            font=("Helvetica", 11, "bold"),
            background=PRIMARY,
            foreground="#FFFFFF",
            borderwidth=0,
            padding=8
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", PRIMARY_HOVER), ("pressed", "#1E40AF")]
        )

        self.style.configure(
            "Secondary.TButton",
            font=("Helvetica", 10),
            background="#E2E8F0",
            foreground=TEXT_MAIN,
            borderwidth=0,
            padding=6
        )
        self.style.map(
            "Secondary.TButton",
            background=[("active", "#CBD5E1")]
        )

        self.style.configure(
            "Danger.TButton",
            font=("Helvetica", 10),
            background="#FEE2E2",
            foreground="#991B1B",
            borderwidth=0,
            padding=6
        )
        self.style.map(
            "Danger.TButton",
            background=[("active", "#FECACA")]
        )

        # Entry & Combobox
        self.style.configure("TCombobox", padding=5, font=("Helvetica", 10))
        self.style.configure("TNotebook", background=BG_MAIN)
        self.style.configure("TNotebook.Tab", padding=[16, 8], font=("Helvetica", 10, "bold"))
        self.style.map("TNotebook.Tab", background=[("selected", CARD_BG)])

        # Treeview styling
        self.style.configure(
            "Treeview",
            background="#FFFFFF",
            foreground=TEXT_MAIN,
            rowheight=28,
            fieldbackground="#FFFFFF",
            font=("Helvetica", 10)
        )
        self.style.configure("Treeview.Heading", font=("Helvetica", 10, "bold"), padding=6)
        self.style.map("Treeview", background=[("selected", "#DBEAFE")], foreground=[("selected", TEXT_MAIN)])

    def _create_header(self):
        """Creates top banner header."""
        header = tk.Frame(self, bg="#0F172A", height=60, padx=24, pady=12)
        header.pack(side=tk.TOP, fill=tk.X)

        title_lbl = tk.Label(
            header,
            text="⚖️  BMI Calculator & Health Trend Tracker",
            font=("Helvetica", 16, "bold"),
            bg="#0F172A",
            fg="#FFFFFF"
        )
        title_lbl.pack(side=tk.LEFT)

        subtitle_lbl = tk.Label(
            header,
            text="Oasis Infobyte · Task 2 (Advanced Tier)",
            font=("Helvetica", 11),
            bg="#0F172A",
            fg="#94A3B8"
        )
        subtitle_lbl.pack(side=tk.RIGHT)

    def _create_main_layout(self):
        """Creates main split container with left calculator card and right tabs."""
        main_frame = ttk.Frame(self, padding=16)
        main_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # Left Column: User Profile + Calculator Input + Result Badge
        left_col = tk.Frame(main_frame, bg=BG_MAIN, width=380)
        left_col.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 14), expand=False)
        left_col.pack_propagate(False)

        self._build_user_card(left_col)
        self._build_calculator_card(left_col)
        self._build_result_card(left_col)

        # Right Column: Notebook with Trends, History Table, and BMI Reference
        right_col = ttk.Frame(main_frame)
        right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.notebook = ttk.Notebook(right_col)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Trend Visualization Chart
        self.tab_chart = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_chart, text="📈 BMI Trend Chart")
        self._build_chart_tab(self.tab_chart)

        # Tab 2: Historical Records Table
        self.tab_history = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_history, text="📋 History Log")
        self._build_history_tab(self.tab_history)

        # Tab 3: BMI Standards Reference
        self.tab_reference = ttk.Frame(self.notebook, padding=16)
        self.notebook.add(self.tab_reference, text="ℹ️ BMI Categories Guide")
        self._build_reference_tab(self.tab_reference)

        # Bottom Status Bar
        self.status_var = tk.StringVar(value="Ready. Select or add a user to begin.")
        status_bar = tk.Label(
            self,
            textvariable=self.status_var,
            font=("Helvetica", 9),
            bg="#E2E8F0",
            fg=TEXT_MUTED,
            anchor="w",
            padx=12,
            pady=4
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ------------------ Left Column Cards ------------------

    def _build_user_card(self, parent):
        """User profile selection and management card."""
        card = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 10), ipady=6, padx=2)

        header_frame = tk.Frame(card, bg=CARD_BG, padx=14, pady=8)
        header_frame.pack(fill=tk.X)

        tk.Label(header_frame, text="👤 User Profile", font=("Helvetica", 12, "bold"), bg=CARD_BG, fg=TEXT_MAIN).pack(side=tk.LEFT)

        # User selector frame
        sel_frame = tk.Frame(card, bg=CARD_BG, padx=14, pady=4)
        sel_frame.pack(fill=tk.X)

        self.user_combobox = ttk.Combobox(sel_frame, state="readonly", font=("Helvetica", 10))
        self.user_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        self.user_combobox.bind("<<ComboboxSelected>>", self._on_user_changed)

        btn_new_user = ttk.Button(sel_frame, text="+ New", style="Secondary.TButton", width=6, command=self._prompt_new_user)
        btn_new_user.pack(side=tk.LEFT, padx=(0, 4))

        btn_del_user = ttk.Button(sel_frame, text="✕", style="Danger.TButton", width=3, command=self._delete_current_user)
        btn_del_user.pack(side=tk.LEFT)

    def _build_calculator_card(self, parent):
        """Input fields for height, weight, and calculate action."""
        card = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, highlightthickness=1)
        card.pack(fill=tk.X, pady=(0, 10), ipady=8, padx=2)

        # Card Title
        tk.Label(card, text="🔢 Calculate BMI", font=("Helvetica", 12, "bold"), bg=CARD_BG, fg=TEXT_MAIN).pack(anchor="w", padx=14, pady=(8, 4))

        # Unit System Switcher (Metric vs Imperial)
        unit_frame = tk.Frame(card, bg=CARD_BG, padx=14, pady=4)
        unit_frame.pack(fill=tk.X)

        self.unit_system_var = tk.StringVar(value="Metric")
        rb_metric = tk.Radiobutton(
            unit_frame,
            text="Metric (kg, cm/m)",
            variable=self.unit_system_var,
            value="Metric",
            bg=CARD_BG,
            font=("Helvetica", 10),
            command=self._on_unit_system_changed
        )
        rb_metric.pack(side=tk.LEFT, padx=(0, 14))

        rb_imperial = tk.Radiobutton(
            unit_frame,
            text="Imperial (lbs, ft+in)",
            variable=self.unit_system_var,
            value="Imperial",
            bg=CARD_BG,
            font=("Helvetica", 10),
            command=self._on_unit_system_changed
        )
        rb_imperial.pack(side=tk.LEFT)

        # Weight Input Section
        input_container = tk.Frame(card, bg=CARD_BG, padx=14, pady=6)
        input_container.pack(fill=tk.X)

        self.lbl_weight = tk.Label(input_container, text="Weight (kg):", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=TEXT_MAIN)
        self.lbl_weight.grid(row=0, column=0, sticky="w", pady=(4, 2))

        self.entry_weight = ttk.Entry(input_container, font=("Helvetica", 11))
        self.entry_weight.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        # Height Input Section
        self.lbl_height = tk.Label(input_container, text="Height (m or cm):", font=("Helvetica", 10, "bold"), bg=CARD_BG, fg=TEXT_MAIN)
        self.lbl_height.grid(row=2, column=0, sticky="w", pady=(4, 2))

        # Metric single entry / Imperial split entry
        self.height_metric_frame = tk.Frame(input_container, bg=CARD_BG)
        self.height_metric_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

        self.entry_height = ttk.Entry(self.height_metric_frame, font=("Helvetica", 11))
        self.entry_height.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.height_unit_var = tk.StringVar(value="meters (m)")
        self.combo_height_unit = ttk.Combobox(
            self.height_metric_frame,
            textvariable=self.height_unit_var,
            values=["meters (m)", "centimeters (cm)"],
            state="readonly",
            width=14,
            font=("Helvetica", 9)
        )
        self.combo_height_unit.pack(side=tk.RIGHT, padx=(6, 0))

        # Imperial Height Frame (feet + inches)
        self.height_imperial_frame = tk.Frame(input_container, bg=CARD_BG)
        
        self.entry_height_ft = ttk.Entry(self.height_imperial_frame, font=("Helvetica", 11), width=8)
        self.entry_height_ft.pack(side=tk.LEFT, padx=(0, 4))
        tk.Label(self.height_imperial_frame, text="ft", bg=CARD_BG, fg=TEXT_MUTED, font=("Helvetica", 10)).pack(side=tk.LEFT, padx=(0, 8))

        self.entry_height_in = ttk.Entry(self.height_imperial_frame, font=("Helvetica", 11), width=8)
        self.entry_height_in.pack(side=tk.LEFT, padx=(0, 4))
        tk.Label(self.height_imperial_frame, text="in", bg=CARD_BG, fg=TEXT_MUTED, font=("Helvetica", 10)).pack(side=tk.LEFT)

        # Notes Input (Optional)
        tk.Label(input_container, text="Notes (optional):", font=("Helvetica", 10), bg=CARD_BG, fg=TEXT_MUTED).grid(row=4, column=0, sticky="w", pady=(2, 2))
        self.entry_notes = ttk.Entry(input_container, font=("Helvetica", 10))
        self.entry_notes.grid(row=5, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        input_container.columnconfigure(0, weight=1)

        # Buttons Frame
        btn_frame = tk.Frame(card, bg=CARD_BG, padx=14, pady=4)
        btn_frame.pack(fill=tk.X)

        self.btn_calculate = ttk.Button(
            btn_frame,
            text="⚡ Calculate & Save Record",
            style="Primary.TButton",
            command=self._handle_calculate
        )
        self.btn_calculate.pack(fill=tk.X, pady=(0, 4))

    def _build_result_card(self, parent):
        """Result display with live dynamic badge, gauge, and ideal weight."""
        self.result_card = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, highlightthickness=1)
        self.result_card.pack(fill=tk.BOTH, expand=True, ipady=6, padx=2)

        tk.Label(self.result_card, text="📊 Results & Classification", font=("Helvetica", 12, "bold"), bg=CARD_BG, fg=TEXT_MAIN).pack(anchor="w", padx=14, pady=(8, 4))

        # Big BMI Number
        self.lbl_bmi_val = tk.Label(self.result_card, text="--.--", font=("Helvetica", 28, "bold"), bg=CARD_BG, fg=TEXT_MUTED)
        self.lbl_bmi_val.pack(pady=(4, 0))

        # Color-coded badge label
        self.lbl_category_badge = tk.Label(
            self.result_card,
            text="Enter details & calculate",
            font=("Helvetica", 11, "bold"),
            bg="#F1F5F9",
            fg=TEXT_MUTED,
            padx=12,
            pady=4
        )
        self.lbl_category_badge.pack(pady=4)

        # Visual BMI Gauge Canvas
        self.gauge_canvas = tk.Canvas(self.result_card, bg=CARD_BG, height=36, highlightthickness=0)
        self.gauge_canvas.pack(fill=tk.X, padx=14, pady=4)
        self._draw_gauge_bar(bmi=None)

        # Healthy weight recommendation
        self.lbl_ideal_range = tk.Label(
            self.result_card,
            text="Healthy weight range will appear here.",
            font=("Helvetica", 9),
            bg=CARD_BG,
            fg=TEXT_MUTED,
            wraplength=320,
            justify="center"
        )
        self.lbl_ideal_range.pack(padx=14, pady=(4, 8))

    def _draw_gauge_bar(self, bmi: Optional[float] = None):
        """Draws a visual 4-color BMI gauge with an indicator arrow on the current BMI position."""
        self.gauge_canvas.delete("all")
        width = self.gauge_canvas.winfo_width()
        if width <= 1:
            width = 320  # fallback initial width

        h = 14
        y0 = 6
        y1 = y0 + h

        # Calculate section widths corresponding to BMI scale (15 to 35)
        # Min scale = 15, Underweight cutoff = 18.5, Normal cutoff = 25.0, Overweight cutoff = 30.0, Max scale = 35
        min_scale = 15.0
        max_scale = 35.0
        span = max_scale - min_scale

        x_under = width * ((18.5 - min_scale) / span)
        x_norm = width * ((25.0 - min_scale) / span)
        x_over = width * ((30.0 - min_scale) / span)

        # Draw segment bars
        self.gauge_canvas.create_rectangle(0, y0, x_under, y1, fill=COLOR_UNDERWEIGHT, outline="")
        self.gauge_canvas.create_rectangle(x_under, y0, x_norm, y1, fill=COLOR_NORMAL, outline="")
        self.gauge_canvas.create_rectangle(x_norm, y0, x_over, y1, fill=COLOR_OVERWEIGHT, outline="")
        self.gauge_canvas.create_rectangle(x_over, y0, width, y1, fill=COLOR_OBESE, outline="")

        # Draw BMI indicator pin if BMI is provided
        if bmi is not None:
            clamped_bmi = max(min_scale, min(max_scale, bmi))
            px = width * ((clamped_bmi - min_scale) / span)
            # Arrow triangle pointer
            self.gauge_canvas.create_polygon(
                px, y1 + 1,
                px - 6, y1 + 10,
                px + 6, y1 + 10,
                fill="#0F172A",
                outline=""
            )
            self.gauge_canvas.create_line(px, y0 - 2, px, y1 + 2, fill="#FFFFFF", width=2)

    # ------------------ Right Column Tabs ------------------

    def _build_chart_tab(self, parent):
        """Builds the embedded Matplotlib trend line chart with colored health zones."""
        if not HAS_MATPLOTLIB:
            lbl = tk.Label(parent, text="Matplotlib is not installed. Trend chart unavailable.", font=("Helvetica", 12), fg=COLOR_OBESE)
            lbl.pack(expand=True)
            return

        # Top controls for chart
        ctrl_frame = tk.Frame(parent, bg=BG_MAIN)
        ctrl_frame.pack(fill=tk.X, pady=(0, 6))

        tk.Label(ctrl_frame, text="📊 Visual BMI History & Health Zones", font=("Helvetica", 12, "bold"), bg=BG_MAIN, fg=TEXT_MAIN).pack(side=tk.LEFT)

        btn_refresh = ttk.Button(ctrl_frame, text="🔄 Refresh Chart", style="Secondary.TButton", command=self._update_trend_chart)
        btn_refresh.pack(side=tk.RIGHT)

        # Matplotlib Figure
        self.fig = Figure(figsize=(6.5, 4.5), dpi=100, facecolor="#FFFFFF")
        self.ax = self.fig.add_subplot(111)
        self.fig.tight_layout(pad=3.0)

        self.canvas_chart = FigureCanvasTkAgg(self.fig, master=parent)
        self.canvas_chart.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def _build_history_tab(self, parent):
        """Builds the Treeview table with historical records, CSV export, and deletion."""
        # Top toolbar
        toolbar = tk.Frame(parent, bg=BG_MAIN)
        toolbar.pack(fill=tk.X, pady=(0, 8))

        tk.Label(toolbar, text="Historical Log Entries", font=("Helvetica", 12, "bold"), bg=BG_MAIN, fg=TEXT_MAIN).pack(side=tk.LEFT)

        btn_export = ttk.Button(toolbar, text="📥 Export to CSV", style="Secondary.TButton", command=self._export_csv)
        btn_export.pack(side=tk.RIGHT, padx=(4, 0))

        btn_del_rec = ttk.Button(toolbar, text="🗑️ Delete Entry", style="Danger.TButton", command=self._delete_selected_record)
        btn_del_rec.pack(side=tk.RIGHT, padx=(4, 0))

        btn_clear_all = ttk.Button(toolbar, text="Clear All", style="Secondary.TButton", command=self._clear_user_history)
        btn_clear_all.pack(side=tk.RIGHT, padx=(4, 0))

        # Table with Scrollbar
        table_frame = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "date", "weight", "height", "bmi", "category", "notes")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", selectmode="browse")

        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Date & Time")
        self.tree.heading("weight", text="Weight (kg)")
        self.tree.heading("height", text="Height (m)")
        self.tree.heading("bmi", text="BMI")
        self.tree.heading("category", text="Category")
        self.tree.heading("notes", text="Notes")

        self.tree.column("id", width=45, anchor="center")
        self.tree.column("date", width=140, anchor="center")
        self.tree.column("weight", width=90, anchor="center")
        self.tree.column("height", width=85, anchor="center")
        self.tree.column("bmi", width=75, anchor="center")
        self.tree.column("category", width=120, anchor="center")
        self.tree.column("notes", width=150, anchor="w")

        scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def _build_reference_tab(self, parent):
        """Builds an informative reference tab explaining WHO BMI categories."""
        card = tk.Frame(parent, bg=CARD_BG, bd=1, relief="solid", highlightbackground=BORDER_COLOR, highlightthickness=1, padx=20, pady=20)
        card.pack(fill=tk.BOTH, expand=True)

        tk.Label(card, text="World Health Organization (WHO) BMI Classifications", font=("Helvetica", 14, "bold"), bg=CARD_BG, fg=TEXT_MAIN).pack(anchor="w", pady=(0, 12))

        categories = [
            ("Underweight", "< 18.5", COLOR_UNDERWEIGHT, "May indicate malnutrition or other health conditions. Balanced nutrient-dense diet recommended."),
            ("Normal weight", "18.5 – 24.9", COLOR_NORMAL, "Associated with the lowest risk of cardiovascular diseases and optimal health. Maintain active lifestyle."),
            ("Overweight", "25.0 – 29.9", COLOR_OVERWEIGHT, "Moderate increased risk. Increased physical activity and balanced caloric intake are beneficial."),
            ("Obese (Class I, II, III)", "≥ 30.0", COLOR_OBESE, "Higher health risk. Consulting a physician or dietitian for a structured health plan is advised.")
        ]

        for title, range_str, color, desc in categories:
            item_frame = tk.Frame(card, bg=CARD_BG, pady=8)
            item_frame.pack(fill=tk.X)

            # Color pill
            pill = tk.Label(item_frame, text=f" {title} ({range_str}) ", font=("Helvetica", 11, "bold"), bg=color, fg="#FFFFFF", padx=6, pady=2)
            pill.pack(anchor="w")

            desc_lbl = tk.Label(item_frame, text=desc, font=("Helvetica", 10), bg=CARD_BG, fg=TEXT_MUTED, wraplength=550, justify="left")
            desc_lbl.pack(anchor="w", padx=(4, 0), pady=(2, 0))

        # Formula section
        tk.Label(card, text="BMI Formula:", font=("Helvetica", 11, "bold"), bg=CARD_BG, fg=TEXT_MAIN).pack(anchor="w", pady=(16, 4))
        formula_box = tk.Label(
            card,
            text="Metric Formula:  BMI = Weight (kg) / [Height (m)]²\nImperial Formula: BMI = [Weight (lbs) / Height (in)²] × 703",
            font=("Courier", 10),
            bg="#F8FAFC",
            fg=TEXT_MAIN,
            padx=10,
            pady=8,
            bd=1,
            relief="solid"
        )
        formula_box.pack(anchor="w", fill=tk.X)

    # ------------------ Event Handlers & Logic ------------------

    def _on_unit_system_changed(self):
        """Toggles between Metric and Imperial input fields."""
        system = self.unit_system_var.get()
        if system == "Metric":
            self.lbl_weight.config(text="Weight (kg):")
            self.lbl_height.config(text="Height (m or cm):")
            self.height_imperial_frame.grid_forget()
            self.height_metric_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))
        else:
            self.lbl_weight.config(text="Weight (lbs):")
            self.lbl_height.config(text="Height (feet & inches):")
            self.height_metric_frame.grid_forget()
            self.height_imperial_frame.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(0, 8))

    def _load_users(self):
        """Loads all registered users from database into dropdown."""
        try:
            users = self.db.get_all_users()
            user_names = [u["name"] for u in users]
            self.user_combobox["values"] = user_names

            if users:
                # Select the first user by default if not set
                if not self.current_user or self.current_user["name"] not in user_names:
                    self.current_user = users[0]
                    self.user_combobox.set(self.current_user["name"])
                else:
                    self.user_combobox.set(self.current_user["name"])
                self._load_active_user_data()
            else:
                # Auto create a default user "Default User"
                default_user = self.db.get_or_create_user("Default User")
                self.current_user = default_user
                self.user_combobox["values"] = [default_user["name"]]
                self.user_combobox.set(default_user["name"])
                self._load_active_user_data()
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to load users: {e}")

    def _prompt_new_user(self):
        """Dialog to create a new user profile."""
        dialog = tk.Toplevel(self)
        dialog.title("Add New User Profile")
        dialog.geometry("340x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        dialog.configure(bg=CARD_BG)

        tk.Label(dialog, text="Enter User Name:", font=("Helvetica", 11, "bold"), bg=CARD_BG, fg=TEXT_MAIN).pack(pady=(16, 6))
        entry = ttk.Entry(dialog, font=("Helvetica", 11), width=24)
        entry.pack(pady=4)
        entry.focus()

        def save():
            name = entry.get().strip()
            if not name:
                messagebox.showwarning("Validation Warning", "User name cannot be empty.", parent=dialog)
                return
            try:
                new_user = self.db.get_or_create_user(name)
                self.current_user = new_user
                self._load_users()
                self.user_combobox.set(new_user["name"])
                self._load_active_user_data()
                self.status_var.set(f"Created and switched to user profile: '{name}'")
                dialog.destroy()
            except DatabaseError as e:
                messagebox.showerror("Database Error", str(e), parent=dialog)

        btn_box = tk.Frame(dialog, bg=CARD_BG)
        btn_box.pack(pady=16)

        ttk.Button(btn_box, text="Save Profile", style="Primary.TButton", command=save).pack(side=tk.LEFT, padx=6)
        ttk.Button(btn_box, text="Cancel", style="Secondary.TButton", command=dialog.destroy).pack(side=tk.LEFT, padx=6)

        entry.bind("<Return>", lambda e: save())

    def _delete_current_user(self):
        """Deletes the active user after confirmation."""
        if not self.current_user:
            return

        confirm = messagebox.askyesno(
            "Confirm Delete",
            f"Are you sure you want to delete profile '{self.current_user['name']}' and all their records?",
            icon="warning"
        )
        if not confirm:
            return

        try:
            self.db.delete_user(self.current_user["id"])
            self.current_user = None
            self.status_var.set("User profile deleted.")
            self._load_users()
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to delete user: {e}")

    def _on_user_changed(self, event=None):
        """Handles switching active user from combobox."""
        selected_name = self.user_combobox.get()
        if not selected_name:
            return

        try:
            user = self.db.get_or_create_user(selected_name)
            self.current_user = user
            self._load_active_user_data()
            self.status_var.set(f"Active Profile: '{user['name']}'")
        except DatabaseError as e:
            messagebox.showerror("Database Error", str(e))

    def _load_active_user_data(self):
        """Loads records for current user, populating table and chart."""
        if not self.current_user:
            return

        try:
            self.user_records = self.db.get_user_records(self.current_user["id"])
            self._populate_history_table()
            self._update_trend_chart()
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to load records: {e}")

    def _populate_history_table(self):
        """Fills treeview with records."""
        for item in self.tree.get_children():
            self.tree.delete(item)

        for rec in reversed(self.user_records):  # Show newest first in table
            self.tree.insert("", tk.END, values=(
                rec["id"],
                rec["date"],
                f"{rec['weight_kg']:.2f}",
                f"{rec['height_m']:.2f}",
                f"{rec['bmi']:.2f}",
                rec["category"],
                rec["notes"] or ""
            ))

    def _update_trend_chart(self):
        """Renders/Updates the Matplotlib line chart for BMI trends."""
        if not HAS_MATPLOTLIB:
            return

        self.ax.clear()

        if not self.user_records:
            self.ax.text(
                0.5, 0.5,
                "No BMI records saved yet.\nCalculate and save to view trend line!",
                horizontalalignment='center',
                verticalalignment='center',
                transform=self.ax.transAxes,
                fontsize=11,
                color=TEXT_MUTED
            )
            self.ax.set_xticks([])
            self.ax.set_yticks([])
            self.canvas_chart.draw_idle()
            return

        # Prepare data
        dates = []
        bmis = []
        for r in self.user_records:
            try:
                dt = datetime.strptime(r["date"], "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    dt = datetime.strptime(r["date"], "%Y-%m-%d")
                except ValueError:
                    continue
            dates.append(dt)
            bmis.append(r["bmi"])

        if not dates:
            self.canvas_chart.draw_idle()
            return

        # Determine plot bounds
        min_bmi = min(min(bmis) - 2.0, 14.0)
        max_bmi = max(max(bmis) + 2.0, 36.0)

        # Plot Colored Background Zones
        # Underweight: < 18.5
        self.ax.axhspan(min_bmi, 18.5, color=COLOR_UNDERWEIGHT, alpha=0.15, label="Underweight (<18.5)")
        # Normal: 18.5 to 25.0
        self.ax.axhspan(18.5, 25.0, color=COLOR_NORMAL, alpha=0.18, label="Normal (18.5 - 24.9)")
        # Overweight: 25.0 to 30.0
        self.ax.axhspan(25.0, 30.0, color=COLOR_OVERWEIGHT, alpha=0.15, label="Overweight (25 - 29.9)")
        # Obese: >= 30.0
        self.ax.axhspan(30.0, max_bmi, color=COLOR_OBESE, alpha=0.15, label="Obese (≥30)")

        # Threshold guide lines
        for y, col in [(18.5, COLOR_UNDERWEIGHT), (25.0, COLOR_NORMAL), (30.0, COLOR_OVERWEIGHT)]:
            self.ax.axhline(y, color=col, linestyle="--", linewidth=0.9, alpha=0.7)

        # Plot data line
        if len(dates) == 1:
            self.ax.scatter(dates, bmis, color=PRIMARY, s=80, zorder=5, label="Recorded BMI")
        else:
            self.ax.plot(dates, bmis, marker="o", color=PRIMARY, linewidth=2.5, markersize=6, zorder=5, label="Recorded BMI")

        # Format Axes
        user_name = self.current_user["name"] if self.current_user else "User"
        self.ax.set_title(f"BMI History Trend for {user_name}", fontsize=12, fontweight="bold", pad=10, color=TEXT_MAIN)
        self.ax.set_ylabel("BMI (kg/m²)", fontsize=10, fontweight="bold", color=TEXT_MAIN)
        self.ax.set_ylim(min_bmi, max_bmi)
        self.ax.grid(True, linestyle=":", alpha=0.6)

        # Format Date on X axis
        self.ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d\n%H:%M" if len(dates) < 5 else "%b %d"))
        self.fig.autofmt_xdate(rotation=0, ha="center")

        # Legend
        self.ax.legend(loc="upper left", fontsize=8, framealpha=0.85)

        self.fig.tight_layout()
        self.canvas_chart.draw_idle()

    # ------------------ Calculation & Validation ------------------

    def _handle_calculate(self):
        """Validates inputs, computes BMI, updates UI, and stores in SQLite."""
        if not self.current_user:
            messagebox.showwarning("User Required", "Please select or create a user profile first.")
            return

        weight_str = self.entry_weight.get().strip()
        system = self.unit_system_var.get()
        notes = self.entry_notes.get().strip()

        # Validate Weight
        if not weight_str:
            messagebox.showerror("Input Error", "Please enter your weight.")
            self.entry_weight.focus()
            return
        try:
            raw_weight = float(weight_str)
            if raw_weight <= 0:
                raise ValueError("Weight must be greater than 0.")
        except ValueError:
            messagebox.showerror("Input Error", "Weight must be a valid positive number.")
            self.entry_weight.focus()
            return

        # Convert Weight to kg if imperial
        if system == "Imperial":
            weight_kg = raw_weight * 0.45359237
        else:
            weight_kg = raw_weight

        # Validate Height
        if system == "Metric":
            height_str = self.entry_height.get().strip()
            if not height_str:
                messagebox.showerror("Input Error", "Please enter your height.")
                self.entry_height.focus()
                return
            try:
                raw_height = float(height_str)
                if raw_height <= 0:
                    raise ValueError("Height must be greater than 0.")
            except ValueError:
                messagebox.showerror("Input Error", "Height must be a valid positive number.")
                self.entry_height.focus()
                return

            unit = self.height_unit_var.get()
            if "cm" in unit or raw_height >= 30.0:  # Auto handle if entered in cm
                height_m = raw_height / 100.0 if raw_height >= 30.0 or "cm" in unit else raw_height
            else:
                height_m = raw_height
        else:
            # Imperial (feet + inches)
            ft_str = self.entry_height_ft.get().strip()
            in_str = self.entry_height_in.get().strip() or "0"

            if not ft_str:
                messagebox.showerror("Input Error", "Please enter height in feet.")
                self.entry_height_ft.focus()
                return
            try:
                ft = float(ft_str)
                inch = float(in_str)
                if ft <= 0 and inch <= 0:
                    raise ValueError("Height must be greater than 0.")
            except ValueError:
                messagebox.showerror("Input Error", "Feet and inches must be valid numbers.")
                return

            total_inches = (ft * 12) + inch
            height_m = total_inches * 0.0254

        # Bounds check on height in meters
        if height_m < 0.5 or height_m > 2.7:
            messagebox.showerror("Input Error", f"Height of {height_m:.2f}m is outside standard human range (0.5m – 2.7m).")
            return

        # Compute BMI & Classification
        bmi = calculate_bmi(weight_kg, height_m)
        category, _, advice = classify_bmi(bmi)
        min_w, max_w = calculate_healthy_weight_range(height_m)

        # Update Result Card UI
        self.lbl_bmi_val.config(text=f"{bmi:.2f}")

        badge_color = {
            "Underweight": COLOR_UNDERWEIGHT,
            "Normal weight": COLOR_NORMAL,
            "Overweight": COLOR_OVERWEIGHT,
            "Obese": COLOR_OBESE
        }.get(category, TEXT_MUTED)

        self.lbl_category_badge.config(
            text=f"  {category.upper()}  ",
            bg=badge_color,
            fg="#FFFFFF"
        )

        self._draw_gauge_bar(bmi=bmi)

        if system == "Metric":
            self.lbl_ideal_range.config(
                text=f"🎯 Healthy Weight Range for {height_m:.2f}m: {min_w:.1f} kg – {max_w:.1f} kg\n\n💡 {advice}"
            )
        else:
            min_lbs = min_w * 2.20462
            max_lbs = max_w * 2.20462
            self.lbl_ideal_range.config(
                text=f"🎯 Healthy Weight Range: {min_lbs:.1f} lbs – {max_lbs:.1f} lbs\n\n💡 {advice}"
            )

        # Save to SQLite database with error handling
        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.db.add_record(
                user_id=self.current_user["id"],
                weight_kg=weight_kg,
                height_m=height_m,
                bmi=bmi,
                category=category,
                notes=notes,
                date_str=now_str
            )
            self.status_var.set(f"Record saved successfully at {now_str} (BMI: {bmi:.2f} - {category})")
            self._load_active_user_data()
        except DatabaseError as e:
            messagebox.showerror("Database Write Error", f"Failed to save record to database: {e}")

    # ------------------ History Actions ------------------

    def _delete_selected_record(self):
        """Deletes selected row in Treeview from SQLite database."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("No Selection", "Please select a record from the history table to delete.")
            return

        values = self.tree.item(selected_item, "values")
        record_id = int(values[0])

        confirm = messagebox.askyesno("Confirm Delete", f"Delete record ID #{record_id}?", icon="warning")
        if not confirm:
            return

        try:
            self.db.delete_record(record_id)
            self.status_var.set(f"Deleted record #{record_id}.")
            self._load_active_user_data()
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to delete record: {e}")

    def _clear_user_history(self):
        """Clears all historical records for current user."""
        if not self.current_user:
            return

        confirm = messagebox.askyesno("Clear All Records", f"Delete ALL BMI records for '{self.current_user['name']}'?", icon="warning")
        if not confirm:
            return

        try:
            deleted_count = self.db.clear_user_records(self.current_user["id"])
            self.status_var.set(f"Cleared {deleted_count} records.")
            self._load_active_user_data()
        except DatabaseError as e:
            messagebox.showerror("Database Error", f"Failed to clear records: {e}")

    def _export_csv(self):
        """Prompts save dialog and exports user records to CSV."""
        if not self.current_user or not self.user_records:
            messagebox.showinfo("Export CSV", "No records available to export for this user.")
            return

        default_filename = f"BMI_History_{self.current_user['name']}_{datetime.now().strftime('%Y%m%d')}.csv"
        file_path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            initialfile=default_filename
        )

        if not file_path:
            return

        try:
            count = self.db.export_to_csv(self.current_user["id"], file_path)
            messagebox.showinfo("Export Successful", f"Successfully exported {count} records to:\n{file_path}")
            self.status_var.set(f"Exported {count} records to CSV.")
        except DatabaseError as e:
            messagebox.showerror("Export Failed", str(e))


def launch_gui():
    """Starts the Tkinter BMI Calculator application."""
    app = BMICalculatorApp()
    app.mainloop()


if __name__ == "__main__":
    launch_gui()
