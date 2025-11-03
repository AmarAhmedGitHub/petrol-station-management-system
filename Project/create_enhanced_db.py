import mysql.connector

try:
    mydb = mysql.connector.connect(
       host="localhost",
       user="root",
       password=""
    )

    c = mydb.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS Petrolpump_Management_Enhanced")
    print("Database 'Petrolpump_Management_Enhanced' created successfully")
    mydb.close()
except Exception as e:
    print(f"Error creating database: {e}")
