#!/usr/bin/env python3
"""
Fix for missing FuelTank_ID column in Petrolpump table.
This adds the FuelTank_ID column and foreign key constraint to the Petrolpump table.
"""

import mysql.connector

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management"
}

def fix_fueltank_column():
    """Add FuelTank_ID column to Petrolpump table"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()

        print("🔧 Adding FuelTank_ID column to Petrolpump table...")

        # Add the FuelTank_ID column
        c.execute("ALTER TABLE Petrolpump ADD COLUMN FuelTank_ID VARCHAR(10)")

        print("✅ FuelTank_ID column added successfully!")

        # Add foreign key constraint
        print("🔧 Adding foreign key constraint...")
        c.execute("ALTER TABLE Petrolpump ADD CONSTRAINT fk_petrolpump_fueltank FOREIGN KEY (FuelTank_ID) REFERENCES FuelTank(FuelTank_ID)")

        print("✅ Foreign key constraint added successfully!")

        conn.commit()

        # Test the fix by running the problematic query
        print("🧪 Testing the fix...")
        c.execute('SELECT Registration_No, Petrolpump_Name, FuelTank_ID FROM Petrolpump LIMIT 1')
        result = c.fetchone()
        print("✅ Query executed successfully! Fix verified.")

    except mysql.connector.Error as err:
        print(f"❌ Error: {err}")
        if "Duplicate column name" in str(err):
            print("⚠️  Column already exists, skipping...")
        elif "Duplicate foreign key constraint name" in str(err):
            print("⚠️  Foreign key constraint already exists, skipping...")
        else:
            raise
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_fueltank_column()
