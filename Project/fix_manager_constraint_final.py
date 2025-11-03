#!/usr/bin/env python3
"""
Fix the foreign key constraint issue for Manager_ID in PetrolStations table.
This script makes Manager_ID nullable to allow adding stations without managers.
Uses the existing database connection from core.database_enhanced.
"""

import sys
from core.database_enhanced import get_connection

def fix_manager_constraint():
    """Fix the Manager_ID foreign key constraint to allow NULL values"""
    try:
        conn = get_connection()
        if not conn:
            print("❌ Failed to connect to database")
            sys.exit(1)

        c = conn.cursor()

        print("🔧 Fixing Manager_ID constraint in PetrolStations table...")

        # Try to drop any existing constraints
        constraint_names = [
            'fk_petrolstations_manager',
            'fk_petrolstations_manager_new',
            'petrolstations_ibfk_1',
            'fk_petrolstations_manager_fixed'
        ]

        for constraint in constraint_names:
            try:
                c.execute(f"ALTER TABLE PetrolStations DROP FOREIGN KEY {constraint}")
                print(f"✅ Dropped constraint: {constraint}")
            except Exception as e:
                print(f"ℹ️  Constraint {constraint} not found or already dropped: {e}")

        # Modify the Manager_ID column to allow NULL values
        c.execute("ALTER TABLE PetrolStations MODIFY COLUMN Manager_ID VARCHAR(10) NULL")
        print("✅ Modified Manager_ID column to allow NULL values")

        # Add the foreign key constraint back (allowing NULL) with a unique name
        c.execute("""
            ALTER TABLE PetrolStations
            ADD CONSTRAINT fk_petrolstations_manager_final
            FOREIGN KEY (Manager_ID) REFERENCES Employees(Employee_ID)
        """)
        print("✅ Re-added foreign key constraint (allowing NULL values)")

        conn.commit()
        print("🎉 Successfully fixed Manager_ID constraint!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals() and conn:
            conn.close()

if __name__ == "__main__":
    fix_manager_constraint()
