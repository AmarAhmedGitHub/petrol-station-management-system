#!/usr/bin/env python3
"""
Final database fix to drop the foreign key constraint and make Manager_ID nullable.
"""

import mysql.connector

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management_Enhanced"
}

def fix_manager_constraint():
    """Drop the foreign key constraint and make Manager_ID nullable"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()

        print("🔧 Dropping foreign key constraint...")

        # Try to drop the constraint (it might have different names)
        constraint_names = [
            'fk_petrolstations_manager_final',
            'fk_petrolstations_manager',
            'petrolstations_ibfk_1'
        ]

        constraint_dropped = False
        for constraint in constraint_names:
            try:
                c.execute(f"ALTER TABLE PetrolStations DROP FOREIGN KEY {constraint}")
                print(f"✅ Dropped constraint: {constraint}")
                constraint_dropped = True
                break
            except Exception as e:
                print(f"ℹ️  Constraint {constraint} not found: {e}")

        if not constraint_dropped:
            print("⚠️  Could not find the constraint to drop")

        print("🔧 Making Manager_ID column nullable...")

        # Modify the Manager_ID column to allow NULL values
        c.execute("ALTER TABLE PetrolStations MODIFY COLUMN Manager_ID VARCHAR(10) NULL")

        conn.commit()
        print("✅ Manager_ID column updated to allow NULL values!")

        # Test by trying to insert a station without manager
        print("🧪 Testing the fix...")
        c.execute("""
            INSERT INTO PetrolStations
            (Station_ID, Station_Name, Company_Name, Registration_No, Opening_Year, State, City, Address, Phone, Manager_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ('TEST001', 'Test Station', 'Test Company', 'REG001', 2024, 'Test State', 'Test City', 'Test Address', '1234567890', None))

        conn.commit()
        print("✅ Test successful - station added without manager!")

        # Clean up test data
        c.execute("DELETE FROM PetrolStations WHERE Station_ID = 'TEST001'")
        conn.commit()
        print("🧹 Test data cleaned up")

        print("🎉 Database fix completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_manager_constraint()
