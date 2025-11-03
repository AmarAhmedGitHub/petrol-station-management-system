#!/usr/bin/env python3
"""
Fix the foreign key constraint issue for Manager_ID in PetrolStations table.
This script makes Manager_ID nullable to allow adding stations without managers.
"""

import mysql.connector
import sys

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management_Enhanced"
}

def fix_manager_constraint():
    """Fix the Manager_ID foreign key constraint to allow NULL values"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()

        print("🔧 Fixing Manager_ID constraint in PetrolStations table...")

        # Drop the existing foreign key constraint
        try:
            c.execute("ALTER TABLE PetrolStations DROP FOREIGN KEY petrolstations_ibfk_1")
            print("✅ Dropped existing foreign key constraint")
        except mysql.connector.Error as e:
            print(f"ℹ️  Foreign key constraint might not exist: {e}")

        # Modify the Manager_ID column to allow NULL values
        c.execute("ALTER TABLE PetrolStations MODIFY COLUMN Manager_ID VARCHAR(10) NULL")
        print("✅ Modified Manager_ID column to allow NULL values")

        # Re-add the foreign key constraint (now allowing NULL)
        c.execute("""
            ALTER TABLE PetrolStations
            ADD CONSTRAINT fk_petrolstations_manager
            FOREIGN KEY (Manager_ID) REFERENCES Employees(Employee_ID)
        """)
        print("✅ Re-added foreign key constraint (allowing NULL values)")

        conn.commit()
        print("🎉 Successfully fixed Manager_ID constraint!")

    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_manager_constraint()
