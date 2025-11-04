#!/usr/bin/env python3
"""
Database Setup Script for Hosting
Sets up the Petrol Station Management System database on external MySQL servers
(Hostinger, AWS RDS, DigitalOcean, etc.)
"""

import os
import sys
import mysql.connector
from dotenv import load_dotenv

def setup_database_hosting():
    """Setup database on external hosting service"""

    # Load environment variables
    load_dotenv()

    # Database configuration - Update these with your hosting credentials
    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "your-planetscale-host.aws.connect.psdb.cloud"),
        "user": os.getenv("DB_USER", "your_planetscale_user"),
        "password": os.getenv("DB_PASSWORD", "your_planetscale_password"),
        "database": os.getenv("DB_NAME", "petrolpump_management"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "ssl_ca": os.getenv("DB_SSL_CA", None),  # For PlanetScale SSL
        "ssl_verify_cert": True
    }

    # Remove ssl_ca if not set
    if not DB_CONFIG["ssl_ca"]:
        del DB_CONFIG["ssl_ca"]
        del DB_CONFIG["ssl_verify_cert"]

    print("🔧 Setting up Petrol Station Management Database on Hosting Server")
    print("=" * 60)

    try:
        # Step 1: Connect without database to create it
        print("📡 Connecting to MySQL server...")
        temp_config = DB_CONFIG.copy()
        del temp_config["database"]

        mydb = mysql.connector.connect(**temp_config)
        c = mydb.cursor()

        # Create database if it doesn't exist
        print("🏗️  Creating database...")
        c.execute(f"CREATE DATABASE IF NOT EXISTS `{DB_CONFIG['database']}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
        mydb.commit()
        mydb.close()

        print("✅ Database created successfully")

        # Step 2: Connect with database and run schema
        print("🔗 Connecting to database...")
        mydb = mysql.connector.connect(**DB_CONFIG)
        c = mydb.cursor()

        # Read and execute the schema file
        print("📄 Executing database schema...")
        schema_file = os.path.join(os.path.dirname(__file__), "database_hosting.sql")

        if not os.path.exists(schema_file):
            print(f"❌ Schema file not found: {schema_file}")
            return False

        with open(schema_file, 'r', encoding='utf-8') as f:
            sql_content = f.read()

        # Split SQL commands and execute them
        commands = sql_content.split(';')
        executed_commands = 0

        for command in commands:
            command = command.strip()
            if command and not command.startswith('--'):
                try:
                    c.execute(command)
                    executed_commands += 1
                except mysql.connector.Error as e:
                    if "Duplicate entry" not in str(e):  # Ignore duplicate entries
                        print(f"⚠️  Warning executing command: {e}")

        mydb.commit()
        mydb.close()

        print(f"✅ Database setup completed successfully!")
        print(f"   - Executed {executed_commands} SQL commands")
        print(f"   - Database: {DB_CONFIG['database']}")
        print(f"   - Host: {DB_CONFIG['host']}")

        return True

    except mysql.connector.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_database_connection():
    """Test database connection"""
    load_dotenv()

    DB_CONFIG = {
        "host": os.getenv("DB_HOST", "your-planetscale-host.aws.connect.psdb.cloud"),
        "user": os.getenv("DB_USER", "your_planetscale_user"),
        "password": os.getenv("DB_PASSWORD", "your_planetscale_password"),
        "database": os.getenv("DB_NAME", "petrolpump_management"),
        "port": int(os.getenv("DB_PORT", 3306)),
        "ssl_ca": os.getenv("DB_SSL_CA", None),  # For PlanetScale SSL
        "ssl_verify_cert": True
    }

    # Remove ssl_ca if not set
    if not DB_CONFIG["ssl_ca"]:
        del DB_CONFIG["ssl_ca"]
        del DB_CONFIG["ssl_verify_cert"]

    try:
        print("🧪 Testing database connection...")
        mydb = mysql.connector.connect(**DB_CONFIG)
        c = mydb.cursor()

        # Test query
        c.execute("SELECT COUNT(*) FROM FuelTypes")
        result = c.fetchone()
        print(f"✅ Connection successful! Found {result[0]} fuel types")

        c.execute("SHOW TABLES")
        tables = c.fetchall()
        print(f"📊 Total tables: {len(tables)}")

        mydb.close()
        return True

    except mysql.connector.Error as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Petrol Station Management System - Database Hosting Setup")
    print("=" * 60)

    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠️  No .env file found. Creating template...")
        with open('.env', 'w') as f:
            f.write("""# Database Configuration for PlanetScale
DB_HOST=your-planetscale-host.aws.connect.psdb.cloud
DB_USER=your_planetscale_user
DB_PASSWORD=your_planetscale_password
DB_NAME=petrolpump_management
DB_PORT=3306
DB_SSL_CA=/path/to/planetscale-ca-cert.pem

# Application Configuration
SECRET_KEY=your-secret-key-here
APP_ENV=production
""")
        print("✅ Created .env template. Please update with your PlanetScale credentials.")
        print("   Then run this script again.")
        sys.exit(1)

    # Setup database
    if setup_database_hosting():
        print("\n🎉 Database setup completed!")
        print("\nNext steps:")
        print("1. Update your application .env file with PlanetScale credentials")
        print("2. Test the connection: python setup_database_hosting.py test")
        print("3. Deploy your application to your hosting platform")

        # Test connection
        if len(sys.argv) > 1 and sys.argv[1] == "test":
            test_database_connection()
    else:
        print("\n❌ Database setup failed. Please check your credentials and try again.")
        sys.exit(1)
