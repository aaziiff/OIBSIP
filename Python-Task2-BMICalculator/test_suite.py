"""
Oasis Infobyte - Task 2: BMI Calculator (Comprehensive Test Suite)
Author: Antigravity
Description: Automated tests verifying calculation accuracy, edge cases,
             database persistence, user isolation, and conversions.
"""

import os
import unittest
from bmi_calculator_cli import calculate_bmi, classify_bmi, calculate_healthy_weight_range
from database import DatabaseManager, DatabaseError


class TestBMICalculatorSuite(unittest.TestCase):

    def setUp(self):
        self.test_db = "test_suite_bmi.db"
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        self.db = DatabaseManager(self.test_db)

    def tearDown(self):
        if os.path.exists(self.test_db):
            os.remove(self.test_db)
        test_csv = "test_export_suite.csv"
        if os.path.exists(test_csv):
            os.remove(test_csv)

    # 1. Calculation & Classification Tests
    def test_bmi_exact_formula(self):
        # 60 kg, 1.65 m -> 60 / (1.65^2) = 22.0385...
        bmi = calculate_bmi(60.0, 1.65)
        self.assertAlmostEqual(bmi, 22.03856, places=4)

    def test_zero_or_negative_height_raises_error(self):
        with self.assertRaises(ValueError):
            calculate_bmi(70, 0)
        with self.assertRaises(ValueError):
            calculate_bmi(70, -1.75)

    def test_category_boundaries(self):
        # Underweight (< 18.5)
        cat_under, _, _ = classify_bmi(18.49)
        self.assertEqual(cat_under, "Underweight")

        # Normal weight (18.5 - 24.9)
        cat_normal_min, _, _ = classify_bmi(18.50)
        self.assertEqual(cat_normal_min, "Normal weight")
        cat_normal_max, _, _ = classify_bmi(24.90)
        self.assertEqual(cat_normal_max, "Normal weight")

        # Overweight (25.0 - 29.9)
        cat_over_min, _, _ = classify_bmi(25.00)
        self.assertEqual(cat_over_min, "Overweight")
        cat_over_max, _, _ = classify_bmi(29.90)
        self.assertEqual(cat_over_max, "Overweight")

        # Obese (>= 30.0)
        cat_obese_min, _, _ = classify_bmi(30.00)
        self.assertEqual(cat_obese_min, "Obese")
        cat_obese_high, _, _ = classify_bmi(42.50)
        self.assertEqual(cat_obese_high, "Obese")

    def test_healthy_weight_range(self):
        height = 1.80
        min_w, max_w = calculate_healthy_weight_range(height)
        self.assertEqual(min_w, round(18.5 * (1.80 ** 2), 2))
        self.assertEqual(max_w, round(24.9 * (1.80 ** 2), 2))

    # 2. Database Multi-User & History Persistence Tests
    def test_user_management(self):
        u1 = self.db.get_or_create_user("John Doe")
        self.assertEqual(u1["name"], "John Doe")

        u2 = self.db.get_or_create_user("Jane Smith")
        self.assertEqual(u2["name"], "Jane Smith")

        users = self.db.get_all_users()
        self.assertEqual(len(users), 2)

    def test_multi_user_record_isolation(self):
        u1 = self.db.get_or_create_user("User A")
        u2 = self.db.get_or_create_user("User B")

        # Add records for User A
        self.db.add_record(u1["id"], 65.0, 1.70, 22.49, "Normal weight", "Morning")
        self.db.add_record(u1["id"], 64.5, 1.70, 22.31, "Normal weight", "Evening")

        # Add records for User B
        self.db.add_record(u2["id"], 90.0, 1.80, 27.78, "Overweight", "Post lunch")

        # Verify records are isolated per user
        records_a = self.db.get_user_records(u1["id"])
        records_b = self.db.get_user_records(u2["id"])

        self.assertEqual(len(records_a), 2)
        self.assertEqual(len(records_b), 1)
        self.assertEqual(records_a[0]["weight_kg"], 65.0)
        self.assertEqual(records_b[0]["weight_kg"], 90.0)

    def test_record_deletion(self):
        user = self.db.get_or_create_user("User C")
        rec_id = self.db.add_record(user["id"], 80.0, 1.75, 26.12, "Overweight")
        self.assertEqual(len(self.db.get_user_records(user["id"])), 1)

        # Delete single record
        deleted = self.db.delete_record(rec_id)
        self.assertTrue(deleted)
        self.assertEqual(len(self.db.get_user_records(user["id"])), 0)

    def test_csv_export(self):
        user = self.db.get_or_create_user("User D")
        self.db.add_record(user["id"], 55.0, 1.60, 21.48, "Normal weight", "Baseline")
        self.db.add_record(user["id"], 54.0, 1.60, 21.09, "Normal weight", "Followup")

        export_path = "test_export_suite.csv"
        count = self.db.export_to_csv(user["id"], export_path)
        self.assertEqual(count, 2)
        self.assertTrue(os.path.exists(export_path))


if __name__ == "__main__":
    unittest.main()
