"""
Oasis Infobyte - Task 2: BMI Calculator (Database Module)
Author: Antigravity
Description: SQLite database manager for storing multi-user profiles,
             historical BMI records, and providing CSV export/import capabilities
             with comprehensive error handling.
"""

import os
import csv
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple, Any

DEFAULT_DB_NAME = "bmi_records.db"


class DatabaseError(Exception):
    """Custom exception class for database operation failures."""
    pass


class DatabaseManager:
    """Manages SQLite database connections and CRUD operations for BMI Calculator."""

    def __init__(self, db_path: str = DEFAULT_DB_NAME):
        self.db_path = db_path
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Establishes and returns a SQLite connection with foreign keys enabled."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            return conn
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to connect to database at '{self.db_path}': {e}") from e

    def _init_db(self):
        """Initializes tables if they do not exist."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL UNIQUE COLLATE NOCASE,
                        created_at TEXT NOT NULL
                    )
                """)

                # BMI records table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS bmi_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER NOT NULL,
                        date TEXT NOT NULL,
                        weight_kg REAL NOT NULL,
                        height_m REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        notes TEXT DEFAULT '',
                        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            raise DatabaseError(f"Database initialization failed: {e}") from e

    # ------------------ User Management ------------------

    def get_all_users(self) -> List[Dict[str, Any]]:
        """Returns a list of all registered users."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, created_at FROM users ORDER BY name ASC")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to fetch users: {e}") from e

    def get_or_create_user(self, name: str) -> Dict[str, Any]:
        """
        Retrieves an existing user by name, or creates a new one if not found.
        """
        cleaned_name = name.strip()
        if not cleaned_name:
            raise ValueError("User name cannot be empty.")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, name, created_at FROM users WHERE name = ?", (cleaned_name,))
                row = cursor.fetchone()
                if row:
                    return dict(row)

                # Create new user
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                cursor.execute("INSERT INTO users (name, created_at) VALUES (?, ?)", (cleaned_name, now))
                conn.commit()
                user_id = cursor.lastrowid
                return {"id": user_id, "name": cleaned_name, "created_at": now}
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to get or create user '{cleaned_name}': {e}") from e

    def delete_user(self, user_id: int) -> bool:
        """Deletes a user and all their associated records (via CASCADE)."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete user ID {user_id}: {e}") from e

    # ------------------ BMI Records Management ------------------

    def add_record(
        self,
        user_id: int,
        weight_kg: float,
        height_m: float,
        bmi: float,
        category: str,
        notes: str = "",
        date_str: Optional[str] = None
    ) -> int:
        """
        Inserts a new BMI record for the specified user.
        
        Returns:
            int: The inserted record ID.
        """
        if weight_kg <= 0 or height_m <= 0 or bmi <= 0:
            raise ValueError("Weight, height, and BMI must all be positive values.")

        if not date_str:
            date_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO bmi_records (user_id, date, weight_kg, height_m, bmi, category, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (user_id, date_str, round(weight_kg, 2), round(height_m, 2), round(bmi, 2), category, notes))
                conn.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to save BMI record: {e}") from e

    def get_user_records(self, user_id: int) -> List[Dict[str, Any]]:
        """
        Retrieves all BMI records for a user, sorted chronologically (oldest to newest).
        """
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, user_id, date, weight_kg, height_m, bmi, category, notes
                    FROM bmi_records
                    WHERE user_id = ?
                    ORDER BY datetime(date) ASC, id ASC
                """, (user_id,))
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to retrieve records for user ID {user_id}: {e}") from e

    def delete_record(self, record_id: int) -> bool:
        """Deletes a specific BMI record by its ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bmi_records WHERE id = ?", (record_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to delete record ID {record_id}: {e}") from e

    def clear_user_records(self, user_id: int) -> int:
        """Deletes all BMI records for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM bmi_records WHERE user_id = ?", (user_id,))
                conn.commit()
                return cursor.rowcount
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to clear records for user ID {user_id}: {e}") from e

    # ------------------ CSV Export & Import ------------------

    def export_to_csv(self, user_id: int, file_path: str) -> int:
        """
        Exports the user's BMI records to a CSV file.
        
        Returns:
            int: Number of exported records.
        """
        records = self.get_user_records(user_id)
        try:
            with open(file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["ID", "Date", "Weight (kg)", "Height (m)", "BMI", "Category", "Notes"])
                for r in records:
                    writer.writerow([
                        r["id"],
                        r["date"],
                        f"{r['weight_kg']:.2f}",
                        f"{r['height_m']:.2f}",
                        f"{r['bmi']:.2f}",
                        r["category"],
                        r["notes"] or ""
                    ])
            return len(records)
        except (IOError, csv.Error) as e:
            raise DatabaseError(f"Failed to export records to CSV '{file_path}': {e}") from e


# Global singleton instance helper
_db_instance: Optional[DatabaseManager] = None


def get_db(db_path: str = DEFAULT_DB_NAME) -> DatabaseManager:
    """Returns a singleton DatabaseManager instance."""
    global _db_instance
    if _db_instance is None or _db_instance.db_path != db_path:
        _db_instance = DatabaseManager(db_path)
    return _db_instance
