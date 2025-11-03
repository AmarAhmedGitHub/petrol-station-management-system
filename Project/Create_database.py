import os
from dotenv import load_dotenv
import mysql.connector

# Load environment variables from .env (if present)
load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_USER = os.getenv("DB_USER", "root")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "Petrolpump_Management_Enhanced")

def create_database_if_not_exists(host=DB_HOST, user=DB_USER, password=DB_PASSWORD, db_name=DB_NAME):
   """Create the configured database if it does not exist."""
   conn = mysql.connector.connect(host=host, user=user, password=password)
   c = conn.cursor()
   c.execute(f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci")
   conn.commit()
   c.close()
   conn.close()

if __name__ == "__main__":
   create_database_if_not_exists()