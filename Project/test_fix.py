#!/usr/bin/env python3
"""
Test script to verify the FuelTank_ID column fix
"""

import mysql.connector

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management"
}

def test_fix():
    """Test if the FuelTank_ID column exists and the query works"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()

        print("🧪 Testing if FuelTank_ID column exists...")

        # Try the problematic query
        c.execute('SELECT Registration_No, Petrolpump_Name, FuelTank_ID FROM Petrolpump LIMIT 1')
        result = c.fetchone()

        if result is not None:
            print("✅ Query executed successfully!")
            print(f"Sample data: {result}")
        else:
            print("✅ Query executed successfully (no data in table)")

        # Check column existence
        c.execute("DESCRIBE Petrolpump")
        columns = c.fetchall()
        column_names = [col[0] for col in columns]

        if 'FuelTank_ID' in column_names:
            print("✅ FuelTank_ID column exists in Petrolpump table")
        else:
            print("❌ FuelTank_ID column still missing")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    test_fix()
