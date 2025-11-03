import mysql.connector
import sys

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management_Enhanced"
}

try:
    # First connect without database to create it
    temp_config = DB_CONFIG.copy()
    del temp_config["database"]
    mydb = mysql.connector.connect(**temp_config)
    c = mydb.cursor()
    c.execute("CREATE DATABASE IF NOT EXISTS Petrolpump_Management_Enhanced")
    print("Database 'Petrolpump_Management_Enhanced' created successfully")
    mydb.close()

    # Now connect with database and create tables
    mydb = mysql.connector.connect(**DB_CONFIG)
    c = mydb.cursor()

    # Create tables (copy from database_enhanced.py)
    # Fuel Types
    c.execute('''CREATE TABLE IF NOT EXISTS FuelTypes (
        FuelType_ID VARCHAR(10) PRIMARY KEY,
        FuelType_Name VARCHAR(50) NOT NULL,
        FuelType_Description TEXT,
        Unit_Price DECIMAL(10,2) NOT NULL,
        Is_Active BOOLEAN DEFAULT TRUE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Owners
    c.execute('''CREATE TABLE IF NOT EXISTS Owners (
        Owner_ID VARCHAR(10) PRIMARY KEY,
        Owner_Name VARCHAR(50) NOT NULL,
        Contact_No VARCHAR(15) NOT NULL,
        Email VARCHAR(100),
        DOB DATE,
        Gender CHAR(1),
        Address TEXT,
        Partnership_Percent DECIMAL(5,2),
        Is_Active BOOLEAN DEFAULT TRUE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Employees
    c.execute('''CREATE TABLE IF NOT EXISTS Employees (
        Employee_ID VARCHAR(10) PRIMARY KEY,
        Station_ID VARCHAR(10),
        Emp_Name VARCHAR(50) NOT NULL,
        Emp_Gender CHAR(1),
        Designation VARCHAR(30),
        DOB DATE,
        Salary DECIMAL(10,2),
        Emp_Address TEXT,
        Email_ID VARCHAR(100),
        Phone VARCHAR(15),
        Manager_ID VARCHAR(10),
        Hire_Date DATE,
        Is_Active BOOLEAN DEFAULT TRUE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Manager_ID) REFERENCES Employees(Employee_ID)
    )''')

    # Petrol Stations
    c.execute('''CREATE TABLE IF NOT EXISTS PetrolStations (
        Station_ID VARCHAR(10) PRIMARY KEY,
        Station_Name VARCHAR(100) NOT NULL,
        Company_Name VARCHAR(50),
        Registration_No VARCHAR(20) UNIQUE,
        Opening_Year INT,
        State VARCHAR(30),
        City VARCHAR(40) NOT NULL,
        Address TEXT,
        Phone VARCHAR(15),
        Manager_ID VARCHAR(10),
        Total_Pumps INT DEFAULT 0,
        Total_Tanks INT DEFAULT 0,
        Is_Active BOOLEAN DEFAULT TRUE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Manager_ID) REFERENCES Employees(Employee_ID)
    )''')

    # Add foreign key for Employees after PetrolStations
    try:
        c.execute('''ALTER TABLE Employees
                     ADD CONSTRAINT fk_employees_station
                     FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)''')
    except mysql.connector.Error:
        pass

    # Fuel Tanks
    c.execute('''CREATE TABLE IF NOT EXISTS FuelTanks (
        Tank_ID VARCHAR(10) PRIMARY KEY,
        Station_ID VARCHAR(10) NOT NULL,
        FuelType_ID VARCHAR(10) NOT NULL,
        Tank_Name VARCHAR(50) NOT NULL,
        Capacity_Liters DECIMAL(15,2) NOT NULL,
        Current_Amount_Liters DECIMAL(15,2) DEFAULT 0,
        Max_Pressure DECIMAL(10,2),
        Min_Pressure DECIMAL(10,2),
        Location VARCHAR(50),
        Is_Active BOOLEAN DEFAULT TRUE,
        Last_Maintenance DATE,
        Next_Maintenance DATE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
        FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
    )''')

    # Fuel Pumps
    c.execute('''CREATE TABLE IF NOT EXISTS FuelPumps (
        Pump_ID VARCHAR(10) PRIMARY KEY,
        Station_ID VARCHAR(10) NOT NULL,
        Pump_Name VARCHAR(50) NOT NULL,
        Pump_Number INT NOT NULL,
        Location VARCHAR(50),
        FuelType_ID VARCHAR(10) NOT NULL,
        Tank_ID VARCHAR(10),
        Employee_ID VARCHAR(10),
        Max_Flow_Rate DECIMAL(10,2),
        Is_Active BOOLEAN DEFAULT TRUE,
        Last_Service DATE,
        Next_Service DATE,
        Total_Liters_Dispensed DECIMAL(15,2) DEFAULT 0,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
        FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID),
        FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
        FOREIGN KEY(Employee_ID) REFERENCES Employees(Employee_ID)
    )''')

    # Customers
    c.execute('''CREATE TABLE IF NOT EXISTS Customers (
        Customer_Code VARCHAR(10) PRIMARY KEY,
        C_Name VARCHAR(50) NOT NULL,
        Phone_No VARCHAR(15),
        Email_ID VARCHAR(100),
        Gender CHAR(1),
        City VARCHAR(50),
        Age INT,
        Loyalty_Points INT DEFAULT 0,
        Is_Active BOOLEAN DEFAULT TRUE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Invoices
    c.execute('''CREATE TABLE IF NOT EXISTS Invoices (
        Invoice_No VARCHAR(15) PRIMARY KEY,
        Station_ID VARCHAR(10) NOT NULL,
        Pump_ID VARCHAR(10) NOT NULL,
        Tank_ID VARCHAR(10) NOT NULL,
        Employee_ID VARCHAR(10),
        Customer_Code VARCHAR(10),
        Invoice_Date DATETIME DEFAULT CURRENT_TIMESTAMP,
        FuelType_ID VARCHAR(10) NOT NULL,
        Fuel_Amount_Liters DECIMAL(10,2) NOT NULL,
        Unit_Price DECIMAL(10,2) NOT NULL,
        Discount_Percent DECIMAL(5,2) DEFAULT 0,
        Discount_Amount DECIMAL(10,2) DEFAULT 0,
        Total_Amount DECIMAL(10,2) NOT NULL,
        Payment_Type VARCHAR(20) NOT NULL,
        Payment_Status VARCHAR(20) DEFAULT 'Completed',
        Notes TEXT,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
        FOREIGN KEY(Pump_ID) REFERENCES FuelPumps(Pump_ID),
        FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
        FOREIGN KEY(Employee_ID) REFERENCES Employees(Employee_ID),
        FOREIGN KEY(Customer_Code) REFERENCES Customers(Customer_Code),
        FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
    )''')

    # Fuel Supply
    c.execute('''CREATE TABLE IF NOT EXISTS FuelSupply (
        Supply_ID INT AUTO_INCREMENT PRIMARY KEY,
        Station_ID VARCHAR(10) NOT NULL,
        Tank_ID VARCHAR(10) NOT NULL,
        FuelType_ID VARCHAR(10) NOT NULL,
        Supply_Invoice_No VARCHAR(20),
        Supply_Date DATE NOT NULL,
        Supplier_Name VARCHAR(100),
        Quantity_Liters DECIMAL(15,2) NOT NULL,
        Unit_Price DECIMAL(10,2) NOT NULL,
        Total_Amount DECIMAL(15,2) NOT NULL,
        Previous_Amount DECIMAL(15,2),
        New_Amount DECIMAL(15,2),
        Supply_Type VARCHAR(20) DEFAULT 'Delivery',
        Notes TEXT,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
        FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
        FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
    )''')

    # Pump Maintenance
    c.execute('''CREATE TABLE IF NOT EXISTS PumpMaintenance (
        Maintenance_ID INT AUTO_INCREMENT PRIMARY KEY,
        Pump_ID VARCHAR(10) NOT NULL,
        Station_ID VARCHAR(10) NOT NULL,
        Maintenance_Type VARCHAR(50) NOT NULL,
        Maintenance_Date DATE NOT NULL,
        Technician_Name VARCHAR(50),
        Description TEXT,
        Cost DECIMAL(10,2),
        Next_Maintenance_Date DATE,
        Status VARCHAR(20) DEFAULT 'Completed',
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Pump_ID) REFERENCES FuelPumps(Pump_ID),
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
    )''')

    # Tank Maintenance
    c.execute('''CREATE TABLE IF NOT EXISTS TankMaintenance (
        Maintenance_ID INT AUTO_INCREMENT PRIMARY KEY,
        Tank_ID VARCHAR(10) NOT NULL,
        Station_ID VARCHAR(10) NOT NULL,
        Maintenance_Type VARCHAR(50) NOT NULL,
        Maintenance_Date DATE NOT NULL,
        Technician_Name VARCHAR(50),
        Description TEXT,
        Cost DECIMAL(10,2),
        Next_Maintenance_Date DATE,
        Status VARCHAR(20) DEFAULT 'Completed',
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
    )''')

    # Employee Debts
    c.execute('''CREATE TABLE IF NOT EXISTS EmployeeDebt (
        Debt_ID INT AUTO_INCREMENT PRIMARY KEY,
        Employee_ID VARCHAR(10) NOT NULL,
        Settlement_Date DATE NOT NULL,
        Sold_Quantity DECIMAL(10,2) NOT NULL,
        Unit_Price DECIMAL(10,2) NOT NULL,
        Owed_Amount DECIMAL(10,2) NOT NULL,
        Status VARCHAR(20) DEFAULT 'Pending',
        Notes TEXT,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Employee_ID) REFERENCES Employees(Employee_ID)
    )''')

    # Station Owners
    c.execute('''CREATE TABLE IF NOT EXISTS StationOwners (
        Station_ID VARCHAR(10) NOT NULL,
        Owner_ID VARCHAR(10) NOT NULL,
        Ownership_Percent DECIMAL(5,2) NOT NULL,
        Is_Primary_Owner BOOLEAN DEFAULT FALSE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY(Station_ID, Owner_ID),
        FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
        FOREIGN KEY(Owner_ID) REFERENCES Owners(Owner_ID)
    )''')

    # System Settings
    c.execute('''CREATE TABLE IF NOT EXISTS SystemSettings (
        Setting_ID VARCHAR(20) PRIMARY KEY,
        Setting_Name VARCHAR(50) NOT NULL,
        Setting_Value TEXT,
        Setting_Description TEXT,
        Is_Active BOOLEAN DEFAULT TRUE,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')

    # Audit Log
    c.execute('''CREATE TABLE IF NOT EXISTS AuditLog (
        Log_ID INT AUTO_INCREMENT PRIMARY KEY,
        Table_Name VARCHAR(50) NOT NULL,
        Record_ID VARCHAR(20) NOT NULL,
        Operation_Type VARCHAR(10) NOT NULL,
        User_ID VARCHAR(10),
        Old_Values TEXT,
        New_Values TEXT,
        Operation_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        IP_Address VARCHAR(45),
        User_Agent TEXT
    )''')

    # Sensor Readings (for backward compatibility)
    c.execute('''CREATE TABLE IF NOT EXISTS SensorReadings (
        Reading_ID INT AUTO_INCREMENT PRIMARY KEY,
        FuelTank_ID VARCHAR(10) NOT NULL,
        Timestamp DATETIME NOT NULL,
        Level DECIMAL(10,2) NOT NULL,
        Sensor_Type VARCHAR(20) NOT NULL,
        Pump_ID VARCHAR(10),
        Temperature DECIMAL(5,2),
        Pressure DECIMAL(10,2),
        Notes TEXT,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(FuelTank_ID) REFERENCES FuelTanks(Tank_ID),
        FOREIGN KEY(Pump_ID) REFERENCES FuelPumps(Pump_ID)
    )''')

    # Tank Sensors
    c.execute('''CREATE TABLE IF NOT EXISTS TankSensors (
        Sensor_ID INT AUTO_INCREMENT PRIMARY KEY,
        Tank_ID VARCHAR(10) NOT NULL,
        Sensor_Type VARCHAR(20) NOT NULL,
        Sensor_Model VARCHAR(50),
        Installation_Date DATE,
        Last_Calibration DATE,
        Next_Calibration DATE,
        Is_Active BOOLEAN DEFAULT TRUE,
        Sensor_Location VARCHAR(50),
        Measurement_Unit VARCHAR(10) DEFAULT 'Liters',
        Min_Threshold DECIMAL(10,2),
        Max_Threshold DECIMAL(10,2),
        Alert_Enabled BOOLEAN DEFAULT TRUE,
        Notes TEXT,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID)
    )''')

    # Pump Sensors
    c.execute('''CREATE TABLE IF NOT EXISTS PumpSensors (
        Sensor_ID INT AUTO_INCREMENT PRIMARY KEY,
        Pump_ID VARCHAR(10) NOT NULL,
        Sensor_Type VARCHAR(20) NOT NULL,
        Sensor_Model VARCHAR(50),
        Installation_Date DATE,
        Last_Calibration DATE,
        Next_Calibration DATE,
        Is_Active BOOLEAN DEFAULT TRUE,
        Sensor_Location VARCHAR(50),
        Measurement_Unit VARCHAR(10) DEFAULT 'L/min',
        Min_Threshold DECIMAL(10,2),
        Max_Threshold DECIMAL(10,2),
        Alert_Enabled BOOLEAN DEFAULT TRUE,
        Notes TEXT,
        Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(Pump_ID) REFERENCES FuelPumps(Pump_ID)
    )''')

    # Insert default data
    c.execute('''INSERT IGNORE INTO FuelTypes (FuelType_ID, FuelType_Name, FuelType_Description, Unit_Price) VALUES
        ('FUEL001', 'بنزين 95', 'بنزين عادي 95 أوكتان', 8.50),
        ('FUEL002', 'بنزين 98', 'بنزين سوبر 98 أوكتان', 9.25),
        ('FUEL003', 'ديزل', 'وقود الديزل', 7.80),
        ('FUEL004', 'كيروسين', 'وقود الطائرات', 6.90)
    ''')

    c.execute('''INSERT IGNORE INTO SystemSettings (Setting_ID, Setting_Name, Setting_Value, Setting_Description) VALUES
        ('MAINT_PUMP', 'Pump Maintenance Interval', '90', 'فترة الصيانة للمضخات بالأيام'),
        ('MAINT_TANK', 'Tank Maintenance Interval', '180', 'فترة الصيانة للخزانات بالأيام'),
        ('LOW_FUEL_ALERT', 'Low Fuel Alert Level', '20', 'نسبة التنبيه لانخفاض الوقود (%)'),
        ('MAX_DISCOUNT', 'Maximum Discount', '15', 'الحد الأقصى للخصم (%)')
    ''')

    mydb.commit()
    mydb.close()
    print("Database and tables created successfully")

except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
