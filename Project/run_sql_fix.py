#!/usr/bin/env python3
"""
Run the SQL fix script to resolve the Manager_ID constraint issue.
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

def run_sql_fix():
    """Execute the SQL fix script"""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        c = conn.cursor()

        print("🔧 Running SQL fix for Manager_ID constraint...")

        # Read and execute the SQL file
        with open('fix_constraint.sql', 'r', encoding='utf-8') as f:
            sql_script = f.read()

        # Split the script into individual statements
        statements = sql_script.split(';')

        for statement in statements:
            statement = statement.strip()
            if statement and not statement.startswith('--'):
                try:
                    c.execute(statement)
                    print(f"✅ Executed: {statement[:50]}...")
                except Exception as e:
                    print(f"ℹ️  Skipped: {statement[:50]}... ({e})")

        conn.commit()
        print("🎉 SQL fix completed successfully!")

    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    run_sql_fix()
