import os
import pymysql
import streamlit as st
from dotenv import load_dotenv

# Load .env from project root (if present)
load_dotenv()

def _get_env(key: str, default: str = "") -> str:
    return os.getenv(key, default)

def get_connection():
    """Get database connection using environment variables (with sensible defaults)

    Reads DB_HOST, DB_USER, DB_PASSWORD, DB_NAME from the environment or .env file.
    """
    db_host = _get_env("DB_HOST", "localhost")
    db_user = _get_env("DB_USER", "root")
    db_password = _get_env("DB_PASSWORD", "")
    db_name = _get_env("DB_NAME", "Petrolpump_Management_Enhanced")
    db_port = int(_get_env("DB_PORT", "3306"))
    try:
        conn = pymysql.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name,
            port=db_port,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=False
        )
        return conn
    except pymysql.Error as err:
        try:
            st.error(f"خطأ في الاتصال بقاعدة البيانات: {err}")
        except Exception:
            print(f"Database connection error: {err}")
        return None

def create_tables():
    """Create all necessary tables in a safe order so FKs can be created."""
    conn = get_connection()
    if not conn:
        return

    c = conn.cursor()

    # Create foundational tables first (no FKs to others)
    c.execute('''CREATE TABLE IF NOT EXISTS FuelTank (
        FuelTank_ID varchar(10) NOT NULL,
        Fuel_Type varchar(20) NOT NULL,
        Capacity float(15) DEFAULT NULL,
        Current_Amount float(15) DEFAULT NULL,
        PRIMARY KEY(FuelTank_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS Owners(
        Owner_Name varchar(50) NOT NULL,
        Contact_NO varchar(20) NOT NULL,
        DOB date DEFAULT NULL,
        Gender varchar(10) DEFAULT NULL,
        Address varchar(255) DEFAULT NULL,
        Partnership int(5) DEFAULT NULL,
        PRIMARY KEY(Owner_Name)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS Petrolpump (
        Registration_No varchar(20) NOT NULL,
        Petrolpump_Name varchar(100) NOT NULL,
        Company_Name varchar(100) DEFAULT NULL,
        Opening_Year int(5) DEFAULT NULL,
        State varchar(50) DEFAULT NULL,
        City varchar(100) NOT NULL,
        FuelTank_ID varchar(10),
        PRIMARY KEY(Registration_No),
        FOREIGN KEY(FuelTank_ID) REFERENCES FuelTank(FuelTank_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS Employee(
        Employee_ID varchar(20) NOT NULL,
        Emp_Name varchar(100) NOT NULL,
        Emp_Gender varchar(10) DEFAULT NULL,
        Designation varchar(50) DEFAULT NULL,
        DOB date DEFAULT NULL,
        Salary int(20) DEFAULT NULL,
        Emp_Address varchar(255) DEFAULT NULL,
        Email_ID varchar(100) DEFAULT NULL,
        Petrolpump_No varchar(20) DEFAULT NULL,
        Manager_ID varchar(20) DEFAULT NULL,
        PRIMARY KEY(Employee_ID),
        FOREIGN KEY(Petrolpump_No) REFERENCES Petrolpump(Registration_No)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS Customer(
        Customer_Code varchar(20) NOT NULL,
        C_Name varchar(100) NOT NULL,
        Phone_No varchar(20) DEFAULT NULL,
        Email_ID varchar(100) DEFAULT NULL,
        Gender varchar(10) DEFAULT NULL,
        City varchar(100) DEFAULT NULL,
        Age int(3) DEFAULT NULL,
        PRIMARY KEY(Customer_Code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS Invoice(
        Invoice_No varchar(20) NOT NULL,
        Date date NOT NULL,
        Payment_Type varchar(50) NOT NULL,
        Fuel_Amount float(15) DEFAULT NULL,
        Fuel_Type varchar(50) DEFAULT NULL,
        Discount int(5) DEFAULT NULL,
        Total_Price float(15) NOT NULL,
        Customer_Code varchar(20) NULL,
        Petrolpump_No varchar(20) DEFAULT NULL,
        FuelTank_ID varchar(10) DEFAULT NULL,
        Fuel_Type_Actual varchar(50) DEFAULT NULL,
        Employee_ID varchar(20) DEFAULT NULL,
        PRIMARY KEY(Invoice_No),
        FOREIGN KEY(Customer_Code) REFERENCES Customer(Customer_Code),
        FOREIGN KEY(Petrolpump_No) REFERENCES Petrolpump(Registration_No),
        FOREIGN KEY(FuelTank_ID) REFERENCES FuelTank(FuelTank_ID),
        FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS Tanker(
        Tanker_ID varchar(20) NOT NULL,
        Capacity float(15) DEFAULT NULL,
        pressure float(15) DEFAULT NULL,
        Fuel_ID varchar(20) DEFAULT NULL,
        Fuel_Amount float(15) DEFAULT NULL,
        Fuel_Name varchar(100) DEFAULT NULL,
        Fuel_Price float(10) DEFAULT NULL,
        Petrolpump_No varchar(20) DEFAULT NULL,
        PRIMARY KEY(Tanker_ID),
        FOREIGN KEY(Petrolpump_No) REFERENCES Petrolpump(Registration_No)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    # Now create tables that reference foundational tables
    c.execute('''CREATE TABLE IF NOT EXISTS FuelSupply (
        Supply_ID INT AUTO_INCREMENT PRIMARY KEY,
        Supply_Invoice_No VARCHAR(50) NOT NULL,
        Supply_Date DATE NOT NULL,
        Supplier_Name VARCHAR(100),
        Fuel_Type VARCHAR(50),
        Quantity FLOAT(15),
        Unit_Price FLOAT(15),
        Total_Amount FLOAT(15),
        FuelTank_ID VARCHAR(10),
        Notes TEXT,
        FOREIGN KEY(FuelTank_ID) REFERENCES FuelTank(FuelTank_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS PumpDirectory (
        ID INT AUTO_INCREMENT PRIMARY KEY,
        Petrolpump_No VARCHAR(20) NOT NULL,
        FuelTank_ID VARCHAR(10),
        Employee_ID VARCHAR(20),
        FOREIGN KEY(Petrolpump_No) REFERENCES Petrolpump(Registration_No),
        FOREIGN KEY(FuelTank_ID) REFERENCES FuelTank(FuelTank_ID),
        FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS EmployeePermissions (
        Employee_ID varchar(20) NOT NULL,
        Permission varchar(50) NOT NULL,
        PRIMARY KEY(Employee_ID, Permission),
        FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS EmployeeDebt (
        Debt_ID INT AUTO_INCREMENT PRIMARY KEY,
        Employee_ID VARCHAR(20) NOT NULL,
        Settlement_Date DATE DEFAULT NULL,
        Sold_Quantity FLOAT DEFAULT 0,
        Unit_Price FLOAT DEFAULT 0,
        Owed_Amount FLOAT DEFAULT 0,
        Status ENUM('Pending', 'Paid') DEFAULT 'Pending',
        Notes TEXT,
        FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS SensorReadings (
        Reading_ID INT AUTO_INCREMENT PRIMARY KEY,
        FuelTank_ID VARCHAR(10) NOT NULL,
        Timestamp DATETIME NOT NULL,
        Level FLOAT NOT NULL,
        Sensor_Type ENUM('PTS2', 'ATG') NOT NULL,
        Pump_ID VARCHAR(20),
        FOREIGN KEY(FuelTank_ID) REFERENCES FuelTank(FuelTank_ID),
        FOREIGN KEY(Pump_ID) REFERENCES Petrolpump(Registration_No)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    # جداول إدارة المخزون الجديدة
    c.execute('''CREATE TABLE IF NOT EXISTS InventoryTransactions (
        Transaction_ID INT AUTO_INCREMENT PRIMARY KEY,
        Tank_ID VARCHAR(10) NOT NULL,
        Transaction_Type ENUM('SALE', 'SUPPLY', 'ADJUSTMENT') NOT NULL,
        Amount FLOAT NOT NULL,
        Employee_ID VARCHAR(20),
        Transaction_Date DATETIME NOT NULL,
        Notes TEXT,
        FOREIGN KEY(Tank_ID) REFERENCES FuelTank(FuelTank_ID),
        FOREIGN KEY(Employee_ID) REFERENCES Employee(Employee_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS InventoryAlerts (
        Alert_ID INT AUTO_INCREMENT PRIMARY KEY,
        Tank_ID VARCHAR(10) NOT NULL,
        Alert_Type VARCHAR(50) NOT NULL,
        Message TEXT NOT NULL,
        Severity ENUM('LOW', 'MEDIUM', 'HIGH', 'CRITICAL') DEFAULT 'MEDIUM',
        Created_Date DATETIME NOT NULL,
        Resolved BOOLEAN DEFAULT FALSE,
        Resolved_Date DATETIME,
        FOREIGN KEY(Tank_ID) REFERENCES FuelTank(FuelTank_ID)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    # جدول Audit Trail للتغييرات الحساسة
    c.execute('''CREATE TABLE IF NOT EXISTS AuditTrail (
        Audit_ID INT AUTO_INCREMENT PRIMARY KEY,
        Table_Name VARCHAR(50) NOT NULL,
        Record_ID VARCHAR(50) NOT NULL,
        Action_Type ENUM('INSERT', 'UPDATE', 'DELETE') NOT NULL,
        Old_Values JSON,
        New_Values JSON,
        User_ID VARCHAR(50),
        User_Type ENUM('Admin', 'Owner', 'Employee') NOT NULL,
        Action_Date DATETIME NOT NULL,
        IP_Address VARCHAR(45),
        User_Agent TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    # جداول النظام الجديدة
    c.execute('''CREATE TABLE IF NOT EXISTS PasswordResetTokens (
        Token_ID INT AUTO_INCREMENT PRIMARY KEY,
        User_Type ENUM('Owner', 'Employee') NOT NULL,
        User_Identifier VARCHAR(100) NOT NULL,
        Reset_Token VARCHAR(128) NOT NULL,
        Expiry_Time DATETIME NOT NULL,
        Created_At DATETIME DEFAULT CURRENT_TIMESTAMP,
        Used BOOLEAN DEFAULT FALSE,
        Used_At DATETIME,
        UNIQUE KEY unique_reset_token (Reset_Token)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS LoyaltyPoints (
        Loyalty_ID INT AUTO_INCREMENT PRIMARY KEY,
        Customer_Code VARCHAR(20) NOT NULL,
        Current_Points FLOAT DEFAULT 0,
        Total_Earned_Points FLOAT DEFAULT 0,
        Total_Redeemed_Points FLOAT DEFAULT 0,
        Last_Updated DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Customer_Code) REFERENCES Customer(Customer_Code),
        UNIQUE KEY unique_customer_loyalty (Customer_Code)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    c.execute('''CREATE TABLE IF NOT EXISTS QualityControlTests (
        Test_ID INT AUTO_INCREMENT PRIMARY KEY,
        Sample_ID VARCHAR(50) NOT NULL,
        Fuel_Type VARCHAR(50),
        Test_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
        Overall_Quality ENUM('EXCELLENT', 'GOOD', 'PASS', 'FAIL') DEFAULT 'PASS',
        Test_Results TEXT,
        Recommendations TEXT
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

    conn.commit()
    c.close()
    conn.close()
