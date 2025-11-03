  #!/usr/bin/env python3
"""
Complete database fix to make Manager_ID nullable in both PetrolStations and Employees tables.
"""

import mysql.connector

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management_Enhanced"
}

def fix_all_manager_constraints():
    """Drop all foreign key constraints and make Manager_ID columns nullable"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()

        print("🔧 Dropping all Manager_ID foreign key constraints...")

        # List of possible constraint names for both tables
        constraints = [
            # PetrolStations constraints
            'fk_petrolstations_manager_final',
            'fk_petrolstations_manager',
            'petrolstations_ibfk_1',
            # Employees constraints
            'employees_ibfk_1',
            'fk_employees_manager',
        ]

        for constraint in constraints:
            try:
                # Try to drop from PetrolStations
                c.execute(f"ALTER TABLE PetrolStations DROP FOREIGN KEY {constraint}")
                print(f"✅ Dropped constraint: {constraint} from PetrolStations")
            except Exception as e:
                try:
                    # Try to drop from Employees
                    c.execute(f"ALTER TABLE Employees DROP FOREIGN KEY {constraint}")
                    print(f"✅ Dropped constraint: {constraint} from Employees")
                except Exception as e2:
                    # Constraint doesn't exist, continue
                    pass

        print("🔧 Making Manager_ID columns nullable...")

        # Make Manager_ID nullable in both tables
        c.execute("ALTER TABLE PetrolStations MODIFY COLUMN Manager_ID VARCHAR(10) NULL")
        c.execute("ALTER TABLE Employees MODIFY COLUMN Manager_ID VARCHAR(10) NULL")

        conn.commit()
        print("✅ Manager_ID columns updated to allow NULL values!")

        # Test adding a station without manager
        print("🧪 Testing station creation without manager...")
        c.execute("""
            INSERT INTO PetrolStations
            (Station_ID, Station_Name, Company_Name, Registration_No, Opening_Year, State, City, Address, Phone, Manager_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ('TEST001', 'Test Station', 'Test Company', 'REG001', 2024, 'Test State', 'Test City', 'Test Address', '1234567890', None))

        conn.commit()
        print("✅ Station added without manager successfully!")

        # Test adding an employee without manager
        print("🧪 Testing employee creation without manager...")
        c.execute("""
            INSERT INTO Employees
            (Employee_ID, Station_ID, Emp_Name, Emp_Gender, Designation, DOB, Salary, Emp_Address, Email_ID, Phone, Manager_ID)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, ('EMP001', 'TEST001', 'Test Employee', 'ذ', 'عامل مضخة', '1990-01-01', 3000.00, 'Test Address', 'test@example.com', '1234567890', None))

        conn.commit()
        print("✅ Employee added without manager successfully!")

        # Clean up test data
        c.execute("DELETE FROM Employees WHERE Employee_ID = 'EMP001'")
        c.execute("DELETE FROM PetrolStations WHERE Station_ID = 'TEST001'")
        conn.commit()
        print("🧹 Test data cleaned up")

        print("🎉 All database constraints fixed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    fix_all_manager_constraints()
