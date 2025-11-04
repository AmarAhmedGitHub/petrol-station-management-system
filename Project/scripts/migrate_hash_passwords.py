"""Migration helper: add `hashed_password` columns and migrate legacy plaintext values.

This script is conservative:
- It adds `hashed_password` columns to `Owners` and `Employees` if they don't exist.
- For each row where `hashed_password` is NULL/empty and a legacy field exists
  (`Contact_NO` for Owners, `Employee_ID` for Employees), it will create a bcrypt
  hash of that legacy value and store it in `hashed_password` WITHOUT modifying the
  legacy field. This preserves existing identifiers.

Usage: run in environment with Project dependencies installed (bcrypt, mysql-connector-python).
Example (PowerShell):
    python .\Project\scripts\migrate_hash_passwords.py
"""

import sys
from core.database_enhanced import get_connection
import bcrypt


def ensure_column(cursor, table: str, column: str, col_def: str = "VARCHAR(255)"):
    try:
        # Attempt to add column; ignore if exists
        cursor.execute(f"ALTER TABLE {table} ADD COLUMN {column} {col_def}")
        return True
    except Exception:
        # Column likely exists or cannot be added due to permissions; ignore
        return False


def migrate_owners(cursor):
    migrated = 0
    cursor.execute("SELECT Owner_Name, Contact_NO, hashed_password FROM Owners")
    rows = cursor.fetchall()
    for row in rows:
        # Support dict or tuple cursor
        if isinstance(row, dict):
            owner = row.get('Owner_Name')
            contact = row.get('Contact_NO')
            hashed = row.get('hashed_password')
        else:
            owner, contact, hashed = row[0], row[1], row[2] if len(row) > 2 else None

        if (not hashed or str(hashed).strip() == '') and contact:
            try:
                new_hash = bcrypt.hashpw(str(contact).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                cursor.execute("UPDATE Owners SET hashed_password=%s WHERE Owner_Name=%s", (new_hash, owner))
                migrated += 1
            except Exception:
                continue

    return migrated


def migrate_employees(cursor):
    migrated = 0
    # Employee table name may be `Employee` or `Employees` depending on schema; try both
    for tbl in ('Employees', 'Employee'):
        try:
            cursor.execute(f"SELECT Emp_Name, Employee_ID, hashed_password FROM {tbl}")
        except Exception:
            continue

        rows = cursor.fetchall()
        for row in rows:
            if isinstance(row, dict):
                name = row.get('Emp_Name')
                empid = row.get('Employee_ID')
                hashed = row.get('hashed_password')
            else:
                name, empid, hashed = row[0], row[1], row[2] if len(row) > 2 else None

            if (not hashed or str(hashed).strip() == '') and empid:
                try:
                    new_hash = bcrypt.hashpw(str(empid).encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                    cursor.execute(f"UPDATE {tbl} SET hashed_password=%s WHERE Emp_Name=%s", (new_hash, name))
                    migrated += 1
                except Exception:
                    continue

        # if we've reached here, we updated the first matching table; stop searching other names
        break

    return migrated


def main():
    conn = get_connection()
    if not conn:
        print("Failed to get DB connection. Ensure environment variables and DB are accessible.")
        sys.exit(2)

    c = conn.cursor()

    print("Ensuring hashed_password columns exist (Owners, Employees/Employee)...")
    ensure_column(c, 'Owners', 'hashed_password', 'VARCHAR(255)')
    # Try both Employee and Employees
    ensure_column(c, 'Employees', 'hashed_password', 'VARCHAR(255)')
    ensure_column(c, 'Employee', 'hashed_password', 'VARCHAR(255)')

    conn.commit()

    print("Migrating Owners...")
    migrated_owners = migrate_owners(c)
    conn.commit()
    print(f"Owners migrated: {migrated_owners}")

    print("Migrating Employees...")
    migrated_emps = migrate_employees(c)
    conn.commit()
    print(f"Employees migrated: {migrated_emps}")

    print("Migration complete. Note: legacy identifier fields (Contact_NO/Employee_ID) were not modified.")


if __name__ == '__main__':
    main()
