# Oasis Infobyte (OIBSIP) — Python Development Internship
## Task 2: BMI Calculator (Beginner & Advanced Tiers)

A complete, feature-packed Body Mass Index (BMI) calculator application in Python, covering both the **Beginner Tier (Interactive CLI)** and the **Advanced Tier (Modern GUI with SQLite Persistence & Matplotlib Trend Visualization)**.

---

## 📋 Feature Checklist

### Beginner Tier
- [x] **CLI Prompt**: Prompts user for weight (kg) and height (m or cm) via the command line.
- [x] **BMI Calculation**: Calculates BMI using standard formula: $\text{BMI} = \frac{\text{weight}}{\text{height}^2}$.
- [x] **Standard Classification**: Accurately classifies results into WHO health categories:
  - **Underweight**: $< 18.5$
  - **Normal weight**: $18.5 – 24.9$
  - **Overweight**: $25.0 – 29.9$
  - **Obese**: $\ge 30.0$
- [x] **Rounded Output**: Displays the BMI value rounded to 2 decimal places alongside health category and ideal weight range.
- [x] **Input Validation**: Robustly rejects non-numeric input, negative values, and zero values with helpful error messages and prompt retries.

### Advanced Tier
- [x] **Modern GUI Window**: Built with `tkinter` and `ttk` card layout with custom styled badges and gauge indicators.
- [x] **Input Fields & Units**: Clean input fields for weight and height with support for both **Metric (kg, cm/m)** and **Imperial (lbs, ft+in)**.
- [x] **Color-Coded Feedback**: Dynamic visual feedback badge and needle gauge:
  - 🔵 **Underweight**: Blue
  - 🟢 **Normal**: Emerald Green
  - 🟠 **Overweight**: Amber / Orange
  - 🔴 **Obese**: Crimson Red
- [x] **Multi-User Support**: Add, switch, and delete named user profiles with isolated history logs.
- [x] **SQLite Database Persistence**: Stores timestamped history (`date`, `weight`, `height`, `bmi`, `category`, `notes`) with cascading user deletion.
- [x] **Graph View (Trend Visualization)**: Interactive line chart of user's BMI history over time using `matplotlib` with colored horizontal health zones and threshold markers.
- [x] **History Log & Export**: View historical records in a table, delete individual entries, clear all history, or export to CSV.
- [x] **Error Handling**: Graceful error handling for database read/write failures, malformed data, and boundary violations.

---

## 🛠️ Tech Stack & Dependencies

- **Language**: Python 3.9+
- **GUI Framework**: `tkinter` & `ttk` (Standard Python Library)
- **Database**: `sqlite3` (Standard Python Library)
- **Plotting & Visualization**: `matplotlib`

---

## 🚀 Getting Started

### 1. Clone & Set Up Virtual Environment

```bash
# Navigate to the project directory
cd Python-Task2-BMICalculator

# Create and activate a virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install required dependencies
pip install -r requirements.txt
```

### 2. Running the Application

#### Option A: Unified Launcher
```bash
# Launch the Advanced GUI Application (default)
python3 main.py

# Launch the Beginner CLI Application
python3 main.py --cli
```

#### Option B: Standalone Modules
```bash
# Run the Beginner Tier CLI Calculator directly
python3 bmi_calculator_cli.py

# Run the Advanced Tier GUI Application directly
python3 bmi_calculator_gui.py
```

---

## 📐 Formulas & Standards

### Metric System
$$\text{BMI} = \frac{\text{Weight (kg)}}{[\text{Height (m)}]^2}$$

### Imperial System
$$\text{BMI} = \frac{\text{Weight (lbs)}}{[\text{Height (in)}]^2} \times 703$$

### Ideal Healthy Weight Range
$$\text{Min Healthy Weight} = 18.5 \times [\text{Height (m)}]^2$$
$$\text{Max Healthy Weight} = 24.9 \times [\text{Height (m)}]^2$$

---

## 🗄️ Database Architecture (`bmi_records.db`)

### `users` Table
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` |
| `name` | `TEXT` | `NOT NULL UNIQUE COLLATE NOCASE` |
| `created_at` | `TEXT` | `NOT NULL` |

### `bmi_records` Table
| Column | Type | Constraints |
| :--- | :--- | :--- |
| `id` | `INTEGER` | `PRIMARY KEY AUTOINCREMENT` |
| `user_id` | `INTEGER` | `FOREIGN KEY REFERENCES users(id) ON DELETE CASCADE` |
| `date` | `TEXT` | `NOT NULL` |
| `weight_kg` | `REAL` | `NOT NULL` |
| `height_m` | `REAL` | `NOT NULL` |
| `bmi` | `REAL` | `NOT NULL` |
| `category` | `TEXT` | `NOT NULL` |
| `notes` | `TEXT` | `DEFAULT ''` |

---

## 📂 Project Structure

```
Python-Task2-BMICalculator/
├── bmi_calculator_cli.py     # Beginner Tier: Interactive CLI tool with validation
├── database.py               # SQLite backend manager with multi-user & CRUD support
├── bmi_calculator_gui.py     # Advanced Tier: Full Tkinter + Matplotlib GUI application
├── main.py                   # Main launcher script (GUI default, --cli option)
├── requirements.txt          # Python dependencies
└── README.md                 # Documentation and guide
```

---

## 👨‍💻 Author
- **Internship**: Oasis Infobyte (OIBSIP)
- **Task**: Task 2 — BMI Calculator
