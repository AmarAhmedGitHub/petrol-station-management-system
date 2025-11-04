import pymysql
import streamlit as st
import logging
from contextlib import contextmanager
import time

logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management_Enhanced",
    "charset": "utf8mb4"
}

def get_connection():
    """Get database connection"""
    try:
        # Override DB_CONFIG with environment variables for Streamlit Cloud
        import os
        db_config = {
            "host": os.getenv("DB_HOST", DB_CONFIG.get("host", "localhost")),
            "user": os.getenv("DB_USER", DB_CONFIG.get("user", "root")),
            "password": os.getenv("DB_PASSWORD", DB_CONFIG.get("password", "")),
            "database": os.getenv("DB_NAME", DB_CONFIG.get("database", "Petrolpump_Management_Enhanced")),
            "port": int(os.getenv("DB_PORT", DB_CONFIG.get("port", 3306))),
            "charset": "utf8mb4"
        }
        conn = pymysql.connect(**db_config)
        logger.debug("Database connection established successfully")
        return conn
    except pymysql.Error as err:
        logger.error(f"Database connection error: {err}")
        st.error(f"خطأ في الاتصال بقاعدة البيانات: {err}")
        return None

# Removed duplicate get_cursor function - using context manager instead

# Function aliases for backward compatibility
def get_fuel_types():
    """Alias for get_all_fuel_types for backward compatibility"""
    return get_all_fuel_types()

def get_stations():
    """Alias for get_all_stations for backward compatibility"""
    return get_all_stations()

def get_pumps():
    """Alias for get_all_pumps for backward compatibility"""
    return get_all_pumps()

def get_tanks():
    """Alias for get_all_tanks for backward compatibility"""
    return get_all_tanks()

def get_pump_meter_reading(pump_id):
    """Get pump meter reading from FuelPumps table Total_Liters_Dispensed"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT Total_Liters_Dispensed FROM FuelPumps WHERE Pump_ID = %s', (pump_id,))
            result = c.fetchone()
            if result and result[0] is not None:
                return float(result[0])
            else:
                # If no reading found, try to get from associated nozzles
                c.execute('''SELECT SUM(Meter_Reading_Current) as total_reading
                           FROM Nozzles n
                           JOIN Dispensers d ON n.Dispenser_ID = d.Dispenser_ID
                           JOIN FuelPumps p ON d.Station_ID = p.Station_ID
                           WHERE p.Pump_ID = %s''', (pump_id,))
                nozzle_result = c.fetchone()
                if nozzle_result and nozzle_result[0] is not None:
                    return float(nozzle_result[0])
                else:
                    # Fallback to flowmeter data
                    c.execute('''SELECT Total_Flow_Liters
                               FROM Flowmeters f
                               JOIN FuelPumps p ON f.Station_ID = p.Station_ID AND f.FuelType_ID = p.FuelType_ID
                               WHERE p.Pump_ID = %s
                               ORDER BY f.Last_Reading_Timestamp DESC
                               LIMIT 1''', (pump_id,))
                    flow_result = c.fetchone()
                    if flow_result and flow_result[0] is not None:
                        return float(flow_result[0])
                    else:
                        return 0.0
    except Exception as e:
        logger.error(f"Error retrieving pump meter reading for {pump_id}: {e}")
        return 0.0

def create_enhanced_tables():
    """Create enhanced database tables with proper separation between stations and pumps"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            logger.info("Starting enhanced database table creation")

            # 1. أنواع الوقود (Fuel Types)
            c.execute('''CREATE TABLE IF NOT EXISTS FuelTypes (
                FuelType_ID VARCHAR(10) PRIMARY KEY,
                FuelType_Name VARCHAR(50) NOT NULL,
                FuelType_Description TEXT,
                Unit_Price DECIMAL(10,2) NOT NULL,
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # 2. المالكين (Owners)
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

            # 3. الموظفين (Employees) - مرتبطين بالمحطات
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

            # 4. المحطات (Petrol Stations) - المحطة الرئيسية
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

            # Update Employees table to add Station_ID foreign key after PetrolStations is created
            try:
                # Check if constraint exists and drop it
                c.execute("SHOW CREATE TABLE Employees")
                create_table = c.fetchone()
                create_sql = create_table[1]  # Access by index since cursor returns tuples
                if 'fk_employees_station' in create_sql:
                    c.execute('ALTER TABLE Employees DROP FOREIGN KEY fk_employees_station')
                    logger.info("Dropped existing fk_employees_station constraint")
            except pymysql.Error as drop_err:
                if drop_err.args[0] != 1091:  # 1091: can't DROP because doesn't exist
                    logger.warning(f"Warning dropping constraint: {drop_err}")
                pass

            try:
                # Add the constraint if it doesn't exist
                c.execute('''ALTER TABLE Employees
                             ADD CONSTRAINT fk_employees_station
                             FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)''')
                logger.info("Added fk_employees_station constraint successfully")
            except pymysql.Error as err:
                if err.args[0] in [1005, 121, 1822]:  # 1005: can't create, 121: duplicate, 1822: constraint already exists
                    logger.info(f"Constraint fk_employees_station already exists or handled: {err}")
                else:
                    raise

            # 5. الخزانات (Fuel Tanks)
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

            # 6. المضخات (Fuel Pumps)
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

            # 6. العملاء (Customers)
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

            # 7. الفواتير (Invoices) - مرتبطة بالمضخات والخزانات
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

            # 8. توريد الوقود (Fuel Supply)
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

            # 9. صيانة المضخات (Pump Maintenance)
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

            # 10. صيانة الخزانات (Tank Maintenance)
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

            # 12. ربط المالكين بالمحطات (Station Owners)
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

            # 13. إعدادات النظام (System Settings)
            c.execute('''CREATE TABLE IF NOT EXISTS SystemSettings (
                Setting_ID VARCHAR(20) PRIMARY KEY,
                Setting_Name VARCHAR(50) NOT NULL,
                Setting_Value TEXT,
                Setting_Description TEXT,
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # 11. ديون الموظفين (Employee Debt)
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

            # 15. مناوبات الموظفين (Employee Shifts)
            c.execute('''CREATE TABLE IF NOT EXISTS EmployeeShifts (
                Shift_ID INT AUTO_INCREMENT PRIMARY KEY,
                Shift_Name VARCHAR(50) NOT NULL,
                Start_Time TIME NOT NULL,
                End_Time TIME NOT NULL,
                Description TEXT,
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # 16. تعيين الموظفين للمحطات (Employee Station Assignments)
            c.execute('''CREATE TABLE IF NOT EXISTS EmployeeStationAssignments (
                Assignment_ID INT AUTO_INCREMENT PRIMARY KEY,
                Employee_ID VARCHAR(10) NOT NULL,
                Station_ID VARCHAR(10) NOT NULL,
                Shift_ID INT,
                Assignment_Date DATE NOT NULL,
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Employee_ID) REFERENCES Employees(Employee_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
                FOREIGN KEY(Shift_ID) REFERENCES EmployeeShifts(Shift_ID)
            )''')

            # 12. قراءات المستشعرات (Sensor Readings)
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

            # 12b. قراءات بداية ونهاية المناوبات للموظفين (Employee Shift Readings)
            c.execute('''CREATE TABLE IF NOT EXISTS EmployeeShiftReadings (
                ShiftReading_ID INT AUTO_INCREMENT PRIMARY KEY,
                Employee_ID VARCHAR(10) NOT NULL,
                Shift_ID INT,
                Directory_ID INT,
                Pump_ID VARCHAR(10),
                FuelTank_ID VARCHAR(10),
                Reading_Type ENUM('baseline','end') DEFAULT 'baseline',
                Timestamp DATETIME NOT NULL,
                Level DECIMAL(10,2) NOT NULL,
                Notes TEXT,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Employee_ID) REFERENCES Employees(Employee_ID),
                FOREIGN KEY(Shift_ID) REFERENCES EmployeeShifts(Shift_ID),
                FOREIGN KEY(Directory_ID) REFERENCES PumpDirectory(Directory_ID),
                FOREIGN KEY(Pump_ID) REFERENCES FuelPumps(Pump_ID),
                FOREIGN KEY(FuelTank_ID) REFERENCES FuelTanks(Tank_ID)
            )''')

            # 13. دليل المضخات (Pump Directory)
            c.execute('''CREATE TABLE IF NOT EXISTS PumpDirectory (
                Directory_ID INT AUTO_INCREMENT PRIMARY KEY,
                Pump_ID VARCHAR(10) NOT NULL,
                Station_ID VARCHAR(10) NOT NULL,
                Employee_ID VARCHAR(10),
                Tank_ID VARCHAR(10),
                FuelType_ID VARCHAR(10) NOT NULL,
                Status VARCHAR(20) DEFAULT 'Active',
                Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                FOREIGN KEY(Pump_ID) REFERENCES FuelPumps(Pump_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
                FOREIGN KEY(Employee_ID) REFERENCES Employees(Employee_ID),
                FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
                FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
            )''')

            # 14. سجل العمليات (Audit Log)
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

            # Insert default fuel types
            c.execute('''INSERT IGNORE INTO FuelTypes (FuelType_ID, FuelType_Name, FuelType_Description, Unit_Price) VALUES
                ('FUEL001', 'بنزين 95', 'بنزين عادي 95 أوكتان', 8.50),
                ('FUEL002', 'بنزين 98', 'بنزين سوبر 98 أوكتان', 9.25),
                ('FUEL003', 'ديزل', 'وقود الديزل', 7.80),
                ('FUEL004', 'كيروسين', 'وقود الطائرات', 6.90)
            ''')

            # Insert default system settings
            c.execute('''INSERT IGNORE INTO SystemSettings (Setting_ID, Setting_Name, Setting_Value, Setting_Description) VALUES
                ('MAINT_PUMP', 'Pump Maintenance Interval', '90', 'فترة الصيانة للمضخات بالأيام'),
                ('MAINT_TANK', 'Tank Maintenance Interval', '180', 'فترة الصيانة للخزانات بالأيام'),
                ('LOW_FUEL_ALERT', 'Low Fuel Alert Level', '20', 'نسبة التنبيه لانخفاض الوقود (%)'),
                ('MAX_DISCOUNT', 'Maximum Discount', '15', 'الحد الأقصى للخصم (%)')
            ''')

            # 17. Dispensers
            c.execute('''CREATE TABLE IF NOT EXISTS Dispensers (
                Dispenser_ID VARCHAR(10) PRIMARY KEY,
                Station_ID VARCHAR(10) NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                Status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
                Last_Communication TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 18. Nozzles
            c.execute('''CREATE TABLE IF NOT EXISTS Nozzles (
                Nozzle_ID VARCHAR(10) PRIMARY KEY,
                Dispenser_ID VARCHAR(10) NOT NULL,
                FuelType_ID VARCHAR(10) NOT NULL,
                Meter_Reading_Start DECIMAL(15,3) NOT NULL,
                Meter_Reading_Current DECIMAL(15,3) NOT NULL,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Dispenser_ID) REFERENCES Dispensers(Dispenser_ID),
                FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
            )''')

            # 19. Flowmeters
            c.execute('''CREATE TABLE IF NOT EXISTS Flowmeters (
                Flowmeter_ID VARCHAR(10) PRIMARY KEY,
                Station_ID VARCHAR(10) NOT NULL,
                FuelType_ID VARCHAR(10) NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                Total_Flow_Liters DECIMAL(15,3) NOT NULL,
                Last_Reading_Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
                FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
            )''')

            # 20. Price Signs
            c.execute('''CREATE TABLE IF NOT EXISTS PriceSigns (
                PriceSign_ID VARCHAR(10) PRIMARY KEY,
                Station_ID VARCHAR(10) NOT NULL,
                FuelType_ID VARCHAR(10) NOT NULL,
                Price DECIMAL(10,3) NOT NULL,
                Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
                FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
            )''')

            # 21. Payment Terminals
            c.execute('''CREATE TABLE IF NOT EXISTS PaymentTerminals (
                Terminal_ID VARCHAR(10) PRIMARY KEY,
                Station_ID VARCHAR(10) NOT NULL,
                Type ENUM('POS', 'Outdoor', 'Mobile') NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                Status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
                Last_Communication TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 22. AVI Vehicles
            c.execute('''CREATE TABLE IF NOT EXISTS AVI_Vehicles (
                Vehicle_ID VARCHAR(10) PRIMARY KEY,
                RFID_Tag VARCHAR(50) UNIQUE NOT NULL,
                License_Plate VARCHAR(20) UNIQUE,
                Customer_ID VARCHAR(10),
                FuelType_ID VARCHAR(10),
                Last_Seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(FuelType_ID) REFERENCES FuelTypes(FuelType_ID)
            )''')

            # 23. RFID Readers
            c.execute('''CREATE TABLE IF NOT EXISTS RFID_Readers (
                Reader_ID VARCHAR(10) PRIMARY KEY,
                Station_ID VARCHAR(10) NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                Location VARCHAR(100),
                Status ENUM('active', 'inactive', 'maintenance') DEFAULT 'active',
                Last_Communication TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 24. Forecourt Controllers
            c.execute('''CREATE TABLE IF NOT EXISTS ForecourtControllers (
                Controller_ID VARCHAR(10) PRIMARY KEY,
                Station_ID VARCHAR(10) UNIQUE NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                IP_Address VARCHAR(15),
                Firmware_Version VARCHAR(50),
                Status ENUM('online', 'offline', 'error') DEFAULT 'online',
                Last_Heartbeat TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 25. System Logs
            c.execute('''CREATE TABLE IF NOT EXISTS SystemLogs (
                Log_ID INT AUTO_INCREMENT PRIMARY KEY,
                Station_ID VARCHAR(10),
                Event_Type VARCHAR(100) NOT NULL,
                Description TEXT,
                Severity ENUM('info', 'warning', 'error', 'critical') DEFAULT 'info',
                Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 26. PTS2 Sensors (Product Sensing Technology 2)
            c.execute('''CREATE TABLE IF NOT EXISTS PTS2_Sensors (
                PTS2_ID VARCHAR(10) PRIMARY KEY,
                Tank_ID VARCHAR(10) NOT NULL,
                Station_ID VARCHAR(10) NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                Model VARCHAR(50) DEFAULT 'PTS2',
                Installation_Date DATE,
                Last_Calibration DATE,
                Next_Calibration DATE,
                Status ENUM('active', 'inactive', 'maintenance', 'error') DEFAULT 'active',
                Firmware_Version VARCHAR(20),
                IP_Address VARCHAR(15),
                Port INT DEFAULT 502,
                Modbus_Address INT DEFAULT 1,
                Measurement_Range_Min DECIMAL(10,2) DEFAULT 0,
                Measurement_Range_Max DECIMAL(10,2) DEFAULT 100,
                Units VARCHAR(10) DEFAULT 'cm',
                Temperature_Compensation BOOLEAN DEFAULT TRUE,
                Last_Reading_Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Last_Level_Reading DECIMAL(10,2),
                Last_Temperature_Reading DECIMAL(5,2),
                Alert_Level_Low DECIMAL(10,2),
                Alert_Level_High DECIMAL(10,2),
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 27. ATG Sensors (Automatic Tank Gauge)
            c.execute('''CREATE TABLE IF NOT EXISTS ATG_Sensors (
                ATG_ID VARCHAR(10) PRIMARY KEY,
                Tank_ID VARCHAR(10) NOT NULL,
                Station_ID VARCHAR(10) NOT NULL,
                Serial_Number VARCHAR(50) UNIQUE NOT NULL,
                Model VARCHAR(50) DEFAULT 'ATG',
                Manufacturer VARCHAR(50),
                Installation_Date DATE,
                Last_Calibration DATE,
                Next_Calibration DATE,
                Status ENUM('active', 'inactive', 'maintenance', 'error') DEFAULT 'active',
                Firmware_Version VARCHAR(20),
                Communication_Type ENUM('serial', 'tcp', 'modbus', 'api') DEFAULT 'serial',
                Connection_String TEXT,
                Baud_Rate INT DEFAULT 9600,
                Data_Bits INT DEFAULT 8,
                Stop_Bits INT DEFAULT 1,
                Parity ENUM('none', 'even', 'odd') DEFAULT 'none',
                IP_Address VARCHAR(15),
                Port INT DEFAULT 10001,
                API_Endpoint TEXT,
                Measurement_Type ENUM('continuous', 'discrete') DEFAULT 'continuous',
                Probe_Type ENUM('magnetostrictive', 'radar', 'capacitive', 'ultrasonic') DEFAULT 'magnetostrictive',
                Probe_Length DECIMAL(10,2),
                Last_Reading_Timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                Last_Level_Reading DECIMAL(10,2),
                Last_Temperature_Reading DECIMAL(5,2),
                Last_Water_Level_Reading DECIMAL(10,2),
                Alert_Level_Low DECIMAL(10,2),
                Alert_Level_High DECIMAL(10,2),
                Alert_Water_Level DECIMAL(10,2),
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 28b. Raw Sensor Responses (store raw API responses for troubleshooting)
            c.execute('''CREATE TABLE IF NOT EXISTS SensorRawResponses (
                Raw_ID INT AUTO_INCREMENT PRIMARY KEY,
                Sensor_Type VARCHAR(20) NOT NULL,
                Sensor_ID VARCHAR(50),
                Tank_ID VARCHAR(10),
                Timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                Response_JSON LONGTEXT,
                Status VARCHAR(20),
                Notes TEXT
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4''')

            # 28. PTS2 Readings
            c.execute('''CREATE TABLE IF NOT EXISTS PTS2_Readings (
                Reading_ID INT AUTO_INCREMENT PRIMARY KEY,
                PTS2_ID VARCHAR(10) NOT NULL,
                Tank_ID VARCHAR(10) NOT NULL,
                Station_ID VARCHAR(10) NOT NULL,
                Timestamp DATETIME NOT NULL,
                Level DECIMAL(10,2) NOT NULL,
                Temperature DECIMAL(5,2),
                Status_Code INT DEFAULT 0,
                Quality_Flag ENUM('good', 'uncertain', 'bad') DEFAULT 'good',
                Raw_Data TEXT,
                Processed BOOLEAN DEFAULT FALSE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(PTS2_ID) REFERENCES PTS2_Sensors(PTS2_ID),
                FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 29. ATG Readings
            c.execute('''CREATE TABLE IF NOT EXISTS ATG_Readings (
                Reading_ID INT AUTO_INCREMENT PRIMARY KEY,
                ATG_ID VARCHAR(10) NOT NULL,
                Tank_ID VARCHAR(10) NOT NULL,
                Station_ID VARCHAR(10) NOT NULL,
                Timestamp DATETIME NOT NULL,
                Level DECIMAL(10,2) NOT NULL,
                Temperature DECIMAL(5,2),
                Water_Level DECIMAL(10,2),
                Product_Volume DECIMAL(15,2),
                Ullage_Volume DECIMAL(15,2),
                Status_Code INT DEFAULT 0,
                Quality_Flag ENUM('good', 'uncertain', 'bad') DEFAULT 'good',
                Raw_Data TEXT,
                Processed BOOLEAN DEFAULT FALSE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(ATG_ID) REFERENCES ATG_Sensors(ATG_ID),
                FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            # 30. Sensor Alarms
            c.execute('''CREATE TABLE IF NOT EXISTS Sensor_Alarms (
                Alarm_ID INT AUTO_INCREMENT PRIMARY KEY,
                Sensor_ID VARCHAR(10) NOT NULL,
                Sensor_Type ENUM('PTS2', 'ATG', 'TankSensor', 'PumpSensor') NOT NULL,
                Tank_ID VARCHAR(10),
                Station_ID VARCHAR(10) NOT NULL,
                Alarm_Type ENUM('level_low', 'level_high', 'water_detected', 'sensor_error', 'communication_lost', 'calibration_due') NOT NULL,
                Severity ENUM('low', 'medium', 'high', 'critical') DEFAULT 'medium',
                Description TEXT,
                Value_Actual DECIMAL(10,2),
                Value_Threshold DECIMAL(10,2),
                Timestamp DATETIME NOT NULL,
                Acknowledged BOOLEAN DEFAULT FALSE,
                Acknowledged_By VARCHAR(10),
                Acknowledged_At TIMESTAMP NULL,
                Resolved BOOLEAN DEFAULT FALSE,
                Resolved_At TIMESTAMP NULL,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Tank_ID) REFERENCES FuelTanks(Tank_ID),
                FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID)
            )''')

            conn.commit()
            logger.info("Extended enhanced database tables created successfully")

            conn.commit()
            logger.info("Enhanced database tables created successfully")
            # Ensure hashed_password columns exist for Owners and Employees (safe migration)
            try:
                c.execute("ALTER TABLE Owners ADD COLUMN hashed_password VARCHAR(255) NULL")
                logger.info("Added hashed_password to Owners")
            except pymysql.Error as e:
                # Column may already exist or other error; ignore if exists
                logger.debug(f"Owners hashed_password alter result: {e}")

            try:
                c.execute("ALTER TABLE Employees ADD COLUMN hashed_password VARCHAR(255) NULL")
                logger.info("Added hashed_password to Employees")
            except pymysql.Error as e:
                logger.debug(f"Employees hashed_password alter result: {e}")
    except Exception as e:
        logger.error(f"Error creating enhanced tables: {e}")
        st.error(f"خطأ في إنشاء الجداول المحسنة: {e}")
        raise

# CRUD Operations for Enhanced Database

# Fuel Types Operations
def add_fuel_type(FuelType_ID, FuelType_Name, FuelType_Description, Unit_Price):
    """Add a new fuel type with validation"""
    if not all([FuelType_ID, FuelType_Name, Unit_Price]):
        logger.error("Missing required parameters for fuel type")
        st.error("جميع الحقول مطلوبة لإضافة نوع وقود")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO FuelTypes (FuelType_ID, FuelType_Name, FuelType_Description, Unit_Price) VALUES (%s,%s,%s,%s)',
                      (FuelType_ID, FuelType_Name, FuelType_Description, Unit_Price))
            conn.commit()
            logger.info(f"Fuel type {FuelType_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding fuel type: {e}")
        st.error("نوع الوقود موجود بالفعل أو خطأ في البيانات")
        return False
    except Exception as e:
        logger.error(f"Error adding fuel type: {e}")
        st.error(f"خطأ في إضافة نوع الوقود: {e}")
        return False

def get_all_fuel_types():
    """Get all active fuel types"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM FuelTypes WHERE Is_Active = TRUE ORDER BY FuelType_Name')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} fuel types")
            return data
    except Exception as e:
        logger.error(f"Error retrieving fuel types: {e}")
        st.error(f"خطأ في استرجاع أنواع الوقود: {e}")
        return []

# Station Operations
def add_petrol_station(Station_ID, Station_Name, Company_Name, Registration_No, Opening_Year, State, City, Address, Phone, Manager_ID):
    """Add a new petrol station with validation"""
    if not all([Station_ID, Station_Name, City]):
        logger.error("Missing required parameters for station")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO PetrolStations
                         (Station_ID, Station_Name, Company_Name, Registration_No, Opening_Year, State, City, Address, Phone, Manager_ID)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Station_ID, Station_Name, Company_Name, Registration_No, Opening_Year, State, City, Address, Phone, Manager_ID))
            conn.commit()
            logger.info(f"Station {Station_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding station: {e}")
        st.error("رقم المحطة أو التسجيل موجود بالفعل")
        return False
    except Exception as e:
        logger.error(f"Error adding station: {e}")
        st.error(f"خطأ في إضافة المحطة: {e}")
        return False

@st.cache_data(ttl=300)
def get_all_stations():
    """Get all active stations with optimized query"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM PetrolStations WHERE Is_Active = TRUE ORDER BY Station_Name LIMIT 1000')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} stations")
            return data
    except Exception as e:
        logger.error(f"Error retrieving stations: {e}")
        st.error(f"خطأ في استرجاع المحطات: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_fuel_types():
    """Get all active fuel types"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM FuelTypes WHERE Is_Active = TRUE ORDER BY FuelType_Name')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} fuel types")
            return data
    except Exception as e:
        logger.error(f"Error retrieving fuel types: {e}")
        st.error(f"خطأ في استرجاع أنواع الوقود: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_tanks():
    """Get all active fuel tanks with station and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT t.*, s.Station_Name, ft.FuelType_Name
                         FROM FuelTanks t
                         JOIN PetrolStations s ON t.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON t.FuelType_ID = ft.FuelType_ID
                         WHERE t.Is_Active = TRUE
                         ORDER BY s.Station_Name, t.Tank_Name''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} fuel tanks")
            return data
    except Exception as e:
        logger.error(f"Error retrieving fuel tanks: {e}")
        st.error(f"خطأ في استرجاع الخزانات: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_pumps():
    """Get all active fuel pumps with station, fuel type, tank and employee info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT p.*, s.Station_Name, ft.FuelType_Name, t.Tank_Name, e.Emp_Name as Employee_Name
                         FROM FuelPumps p
                         JOIN PetrolStations s ON p.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON p.FuelType_ID = ft.FuelType_ID
                         LEFT JOIN FuelTanks t ON p.Tank_ID = t.Tank_ID
                         LEFT JOIN Employees e ON p.Employee_ID = e.Employee_ID
                         WHERE p.Is_Active = TRUE
                         ORDER BY s.Station_Name, p.Pump_Number''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} fuel pumps")
            return data
    except Exception as e:
        logger.error(f"Error retrieving fuel pumps: {e}")
        st.error(f"خطأ في استرجاع المضخات: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_employees():
    """Get all active employees with station and manager info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT e.*, s.Station_Name, m.Emp_Name as Manager_Name
                         FROM Employees e
                         JOIN PetrolStations s ON e.Station_ID = s.Station_ID
                         LEFT JOIN Employees m ON e.Manager_ID = m.Employee_ID
                         WHERE e.Is_Active = TRUE
                         ORDER BY s.Station_Name, e.Emp_Name''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} employees")
            return data
    except Exception as e:
        logger.error(f"Error retrieving employees: {e}")
        st.error(f"خطأ في استرجاع الموظفين: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_customers():
    """Get all active customers"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM Customers WHERE Is_Active = TRUE ORDER BY C_Name')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} customers")
            return data
    except Exception as e:
        logger.error(f"Error retrieving customers: {e}")
        st.error(f"خطأ في استرجاع العملاء: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_invoices(limit=1000):
    """Get all invoices with station, pump, tank, employee and customer info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT i.*, s.Station_Name, p.Pump_Name, t.Tank_Name, e.Emp_Name, c.C_Name, ft.FuelType_Name
                         FROM Invoices i
                         JOIN PetrolStations s ON i.Station_ID = s.Station_ID
                         JOIN FuelPumps p ON i.Pump_ID = p.Pump_ID
                         JOIN FuelTanks t ON i.Tank_ID = t.Tank_ID
                         JOIN FuelTypes ft ON i.FuelType_ID = ft.FuelType_ID
                         LEFT JOIN Employees e ON i.Employee_ID = e.Employee_ID
                         LEFT JOIN Customers c ON i.Customer_Code = c.Customer_Code
                         ORDER BY i.Invoice_Date DESC
                         LIMIT %s''', (limit,))
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} invoices")
            return data
    except Exception as e:
        logger.error(f"Error retrieving invoices: {e}")
        st.error(f"خطأ في استرجاع الفواتير: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_supplies(limit=1000):
    """Get all fuel supplies with station, tank and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT fs.*, s.Station_Name, t.Tank_Name, ft.FuelType_Name
                         FROM FuelSupply fs
                         JOIN PetrolStations s ON fs.Station_ID = s.Station_ID
                         JOIN FuelTanks t ON fs.Tank_ID = t.Tank_ID
                         JOIN FuelTypes ft ON fs.FuelType_ID = ft.FuelType_ID
                         ORDER BY fs.Supply_Date DESC
                         LIMIT %s''', (limit,))
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} supplies")
            return data
    except Exception as e:
        logger.error(f"Error retrieving supplies: {e}")
        st.error(f"خطأ في استرجاع التوريدات: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_sensor_readings(limit=1000):
    """Get all sensor readings with tank and station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT sr.*, t.Tank_Name, s.Station_Name, ft.FuelType_Name
                         FROM SensorReadings sr
                         JOIN FuelTanks t ON sr.FuelTank_ID = t.Tank_ID
                         JOIN PetrolStations s ON t.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON t.FuelType_ID = ft.FuelType_ID
                         ORDER BY sr.Timestamp DESC
                         LIMIT %s''', (limit,))
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} sensor readings")
            return data
    except Exception as e:
        logger.error(f"Error retrieving sensor readings: {e}")
        st.error(f"خطأ في استرجاع قراءات المستشعرات: {e}")
        return []

@st.cache_data(ttl=300)
def get_all_system_logs(limit=100):
    """Get system logs with station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT sl.*, s.Station_Name
                         FROM SystemLogs sl
                         LEFT JOIN PetrolStations s ON sl.Station_ID = s.Station_ID
                         ORDER BY sl.Timestamp DESC
                         LIMIT %s''', (limit,))
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} system logs")
            return data
    except Exception as e:
        logger.error(f"Error retrieving system logs: {e}")
        st.error(f"خطأ في استرجاع سجلات النظام: {e}")
        return []

@st.cache_data(ttl=300)
def get_system_settings():
    """Get all system settings"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM SystemSettings WHERE Is_Active = TRUE ORDER BY Setting_Name')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} system settings")
            return data
    except Exception as e:
        logger.error(f"Error retrieving system settings: {e}")
        st.error(f"خطأ في استرجاع إعدادات النظام: {e}")
        return []

# Tank Operations
def add_fuel_tank(Tank_ID, Station_ID, FuelType_ID, Tank_Name, Capacity_Liters, Max_Pressure, Min_Pressure, Location):
    """Add a new fuel tank with validation"""
    if not all([Tank_ID, Station_ID, FuelType_ID, Tank_Name, Capacity_Liters]):
        logger.error("Missing required parameters for fuel tank")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO FuelTanks
                         (Tank_ID, Station_ID, FuelType_ID, Tank_Name, Capacity_Liters, Max_Pressure, Min_Pressure, Location)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Tank_ID, Station_ID, FuelType_ID, Tank_Name, Capacity_Liters, Max_Pressure, Min_Pressure, Location))
            conn.commit()
            logger.info(f"Fuel tank {Tank_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding fuel tank: {e}")
        st.error("رقم الخزان موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding fuel tank: {e}")
        st.error(f"خطأ في إضافة الخزان: {e}")
        return False

def get_all_tanks():
    """Get all active fuel tanks with station and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT t.*, s.Station_Name, ft.FuelType_Name
                         FROM FuelTanks t
                         JOIN PetrolStations s ON t.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON t.FuelType_ID = ft.FuelType_ID
                         WHERE t.Is_Active = TRUE
                         ORDER BY s.Station_Name, t.Tank_Name''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} fuel tanks")
            return data
    except Exception as e:
        logger.error(f"Error retrieving fuel tanks: {e}")
        st.error(f"خطأ في استرجاع الخزانات: {e}")
        return []

# Pump Operations
def add_fuel_pump(Pump_ID, Station_ID, Pump_Name, Pump_Number, Location, FuelType_ID, Tank_ID, Employee_ID):
    """Add a new fuel pump with validation"""
    if not all([Pump_ID, Station_ID, Pump_Name, Pump_Number, FuelType_ID]):
        logger.error("Missing required parameters for fuel pump")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO FuelPumps
                         (Pump_ID, Station_ID, Pump_Name, Pump_Number, Location, FuelType_ID, Tank_ID, Employee_ID)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Pump_ID, Station_ID, Pump_Name, Pump_Number, Location, FuelType_ID, Tank_ID, Employee_ID))
            conn.commit()
            logger.info(f"Fuel pump {Pump_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding fuel pump: {e}")
        st.error("رقم المضخة موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding fuel pump: {e}")
        st.error(f"خطأ في إضافة المضخة: {e}")
        return False

def get_all_pumps():
    """Get all active fuel pumps with station, fuel type, tank and employee info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT p.*, s.Station_Name, ft.FuelType_Name, t.Tank_Name, e.Emp_Name as Employee_Name
                         FROM FuelPumps p
                         JOIN PetrolStations s ON p.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON p.FuelType_ID = ft.FuelType_ID
                         LEFT JOIN FuelTanks t ON p.Tank_ID = t.Tank_ID
                         LEFT JOIN Employees e ON p.Employee_ID = e.Employee_ID
                         WHERE p.Is_Active = TRUE
                         ORDER BY s.Station_Name, p.Pump_Number''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} fuel pumps")
            return data
    except Exception as e:
        logger.error(f"Error retrieving fuel pumps: {e}")
        st.error(f"خطأ في استرجاع المضخات: {e}")
        return []

# Employee Operations
def add_employee(Employee_ID, Station_ID, Emp_Name, Emp_Gender, Designation, DOB, Salary, Emp_Address, Email_ID, Phone, Manager_ID):
    """Add a new employee with validation"""
    if not all([Employee_ID, Station_ID, Emp_Name]):
        logger.error("Missing required parameters for employee")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO Employees
                         (Employee_ID, Station_ID, Emp_Name, Emp_Gender, Designation, DOB, Salary, Emp_Address, Email_ID, Phone, Manager_ID)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Employee_ID, Station_ID, Emp_Name, Emp_Gender, Designation, DOB, Salary, Emp_Address, Email_ID, Phone, Manager_ID))
            conn.commit()
            logger.info(f"Employee {Employee_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding employee: {e}")
        st.error("رقم الموظف موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding employee: {e}")
        st.error(f"خطأ في إضافة الموظف: {e}")
        return False

def get_all_employees():
    """Get all active employees with station and manager info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT e.*, s.Station_Name, m.Emp_Name as Manager_Name
                         FROM Employees e
                         JOIN PetrolStations s ON e.Station_ID = s.Station_ID
                         LEFT JOIN Employees m ON e.Manager_ID = m.Employee_ID
                         WHERE e.Is_Active = TRUE
                         ORDER BY s.Station_Name, e.Emp_Name''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} employees")
            return data
    except Exception as e:
        logger.error(f"Error retrieving employees: {e}")
        st.error(f"خطأ في استرجاع الموظفين: {e}")
        return []

# Invoice Operations
def add_invoice(Invoice_No, Station_ID, Pump_ID, Tank_ID, Employee_ID, Customer_Code, FuelType_ID, Fuel_Amount_Liters, Unit_Price, Discount_Percent, Payment_Type):
    """Add invoice with transaction management"""
    if not all([Invoice_No, Station_ID, Pump_ID, Tank_ID, FuelType_ID, Fuel_Amount_Liters, Unit_Price, Payment_Type]):
        logger.error("Missing required parameters for invoice")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()

            # Calculate totals
            discount_amount = (Fuel_Amount_Liters * Unit_Price * Discount_Percent) / 100
            total_amount = (Fuel_Amount_Liters * Unit_Price) - discount_amount

            # Insert invoice
            c.execute('''INSERT INTO Invoices
                         (Invoice_No, Station_ID, Pump_ID, Tank_ID, Employee_ID, Customer_Code, FuelType_ID, Fuel_Amount_Liters, Unit_Price, Discount_Percent, Discount_Amount, Total_Amount, Payment_Type)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Invoice_No, Station_ID, Pump_ID, Tank_ID, Employee_ID, Customer_Code, FuelType_ID, Fuel_Amount_Liters, Unit_Price, Discount_Percent, discount_amount, total_amount, Payment_Type))

            # Update tank current amount
            c.execute('UPDATE FuelTanks SET Current_Amount_Liters = Current_Amount_Liters - %s WHERE Tank_ID = %s',
                      (Fuel_Amount_Liters, Tank_ID))

            # Update pump total dispensed
            c.execute('UPDATE FuelPumps SET Total_Liters_Dispensed = Total_Liters_Dispensed + %s WHERE Pump_ID = %s',
                      (Fuel_Amount_Liters, Pump_ID))

            conn.commit()
            logger.info(f"Invoice {Invoice_No} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding invoice: {e}")
        st.error("رقم الفاتورة موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding invoice: {e}")
        st.error(f"خطأ في إضافة الفاتورة: {e}")
        return False

def get_all_invoices():
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('''SELECT i.*, s.Station_Name, p.Pump_Name, t.Tank_Name, e.Emp_Name, c.C_Name, ft.FuelType_Name
                 FROM Invoices i
                 JOIN PetrolStations s ON i.Station_ID = s.Station_ID
                 JOIN FuelPumps p ON i.Pump_ID = p.Pump_ID
                 JOIN FuelTanks t ON i.Tank_ID = t.Tank_ID
                 JOIN FuelTypes ft ON i.FuelType_ID = ft.FuelType_ID
                 LEFT JOIN Employees e ON i.Employee_ID = e.Employee_ID
                 LEFT JOIN Customers c ON i.Customer_Code = c.Customer_Code
                 ORDER BY i.Invoice_Date DESC''')
    data = c.fetchall()
    conn.close()
    return data

# Supply Operations
def add_fuel_supply(Station_ID, Tank_ID, FuelType_ID, Supply_Invoice_No, Supply_Date, Supplier_Name, Quantity_Liters, Unit_Price, Supply_Type, Notes):
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()

    # Get current amount before supply
    c.execute('SELECT Current_Amount_Liters FROM FuelTanks WHERE Tank_ID = %s', (Tank_ID,))
    result = c.fetchone()
    previous_amount = result[0] if result else 0

    # Calculate totals
    total_amount = Quantity_Liters * Unit_Price
    new_amount = previous_amount + Quantity_Liters

    c.execute('''INSERT INTO FuelSupply
                 (Station_ID, Tank_ID, FuelType_ID, Supply_Invoice_No, Supply_Date, Supplier_Name, Quantity_Liters, Unit_Price, Total_Amount, Previous_Amount, New_Amount, Supply_Type, Notes)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
              (Station_ID, Tank_ID, FuelType_ID, Supply_Invoice_No, Supply_Date, Supplier_Name, Quantity_Liters, Unit_Price, total_amount, previous_amount, new_amount, Supply_Type, Notes))

    # Update tank current amount
    c.execute('UPDATE FuelTanks SET Current_Amount_Liters = %s WHERE Tank_ID = %s', (new_amount, Tank_ID))

    conn.commit()
    conn.close()
    return True

def get_all_supplies():
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('''SELECT fs.*, s.Station_Name, t.Tank_Name, ft.FuelType_Name
                 FROM FuelSupply fs
                 JOIN PetrolStations s ON fs.Station_ID = s.Station_ID
                 JOIN FuelTanks t ON fs.Tank_ID = t.Tank_ID
                 JOIN FuelTypes ft ON fs.FuelType_ID = ft.FuelType_ID
                 ORDER BY fs.Supply_Date DESC''')
    data = c.fetchall()
    conn.close()
    return data

# Dashboard Statistics
def get_dashboard_stats():
    """Get dashboard statistics with error handling"""
    stats = {}
    try:
        with get_connection() as conn:
            c = conn.cursor()

            # Total stations
            c.execute('SELECT COUNT(*) FROM PetrolStations WHERE Is_Active = TRUE')
            stats['total_stations'] = c.fetchone()[0]

            # Total pumps
            c.execute('SELECT COUNT(*) FROM FuelPumps WHERE Is_Active = TRUE')
            stats['total_pumps'] = c.fetchone()[0]

            # Total tanks
            c.execute('SELECT COUNT(*) FROM FuelTanks WHERE Is_Active = TRUE')
            stats['total_tanks'] = c.fetchone()[0]

            # Total employees
            c.execute('SELECT COUNT(*) FROM Employees WHERE Is_Active = TRUE')
            stats['total_employees'] = c.fetchone()[0]

            # Today's sales
            c.execute('''SELECT SUM(Total_Amount) FROM Invoices
                         WHERE DATE(Invoice_Date) = CURDATE()''')
            stats['today_sales'] = c.fetchone()[0] or 0

            # This month's sales
            c.execute('''SELECT SUM(Total_Amount) FROM Invoices
                         WHERE YEAR(Invoice_Date) = YEAR(CURDATE())
                         AND MONTH(Invoice_Date) = MONTH(CURDATE())''')
            stats['month_sales'] = c.fetchone()[0] or 0

            # Low fuel tanks (less than 20%)
            c.execute('''SELECT COUNT(*) FROM FuelTanks
                         WHERE Is_Active = TRUE
                         AND (Current_Amount_Liters / Capacity_Liters) * 100 < 20''')
            stats['low_fuel_tanks'] = c.fetchone()[0]

            # Pumps needing maintenance
            c.execute('''SELECT COUNT(*) FROM FuelPumps
                         WHERE Is_Active = TRUE
                         AND Next_Service <= CURDATE()''')
            stats['maintenance_pumps'] = c.fetchone()[0]

            logger.debug(f"Dashboard stats retrieved: {stats}")
            return stats
    except Exception as e:
        logger.error(f"Error retrieving dashboard stats: {e}")
        st.error(f"خطأ في استرجاع إحصائيات لوحة التحكم: {e}")
        return {}

def update_pump_assignment(pump_id, employee_id=None, tank_id=None):
    """Update pump assignment (employee and/or tank)"""
    conn = get_connection()
    if not conn:
        return False

    c = conn.cursor()

    try:
        if employee_id and tank_id:
            # Update both employee and tank
            c.execute('''UPDATE FuelPumps
                        SET Employee_ID = %s, Tank_ID = %s
                        WHERE Pump_ID = %s''',
                     (employee_id, tank_id, pump_id))
        elif employee_id:
            # Update only employee
            c.execute('''UPDATE FuelPumps
                        SET Employee_ID = %s
                        WHERE Pump_ID = %s''',
                     (employee_id, pump_id))
        elif tank_id:
            # Update only tank
            c.execute('''UPDATE FuelPumps
                        SET Tank_ID = %s
                        WHERE Pump_ID = %s''',
                     (tank_id, pump_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"خطأ في تحديث التعيين: {e}")
        conn.close()
        return False

def update_employee_station(employee_id, station_id):
    """Update employee station assignment"""
    conn = get_connection()
    if not conn:
        return False

    c = conn.cursor()

    try:
        c.execute('''UPDATE Employees
                    SET Station_ID = %s
                    WHERE Employee_ID = %s''',
                 (station_id, employee_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"خطأ في تحديث تعيين الموظف: {e}")
        conn.close()
        return False

def create_tables():
    """Create all necessary tables (backward compatibility)"""
    create_enhanced_tables()

# Automation-related functions for enhanced database
def record_sensor_reading(tank_id, level, sensor_type, pump_id=None):
    """Record a sensor reading"""
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()
    from datetime import datetime
    timestamp = datetime.now()
    c.execute('INSERT INTO SensorReadings (FuelTank_ID, Timestamp, Level, Sensor_Type, Pump_ID) VALUES (%s, %s, %s, %s, %s)',
              (tank_id, timestamp, level, sensor_type, pump_id))
    conn.commit()
    conn.close()
    return True


def record_raw_sensor_response(sensor_type, sensor_id, tank_id, response_json, status='OK', notes=None):
    """Record raw sensor API response for later troubleshooting"""
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()
    from datetime import datetime
    timestamp = datetime.now()
    try:
        c.execute('''INSERT INTO SensorRawResponses (Sensor_Type, Sensor_ID, Tank_ID, Timestamp, Response_JSON, Status, Notes)
                     VALUES (%s,%s,%s,%s,%s,%s,%s)''',
                  (sensor_type, sensor_id, tank_id, timestamp, response_json, status, notes))
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"Failed to record raw sensor response: {e}")
        try:
            conn.rollback()
        except Exception:
            pass
        return False


def record_shift_reading(employee_id, shift_id, directory_id, pump_id, tank_id, reading_type, level, notes=None):
    """Record a baseline or end reading for a shift for a specific employee and pump/tank."""
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()
    from datetime import datetime
    timestamp = datetime.now()
    c.execute('''INSERT INTO EmployeeShiftReadings
                 (Employee_ID, Shift_ID, Directory_ID, Pump_ID, FuelTank_ID, Reading_Type, Timestamp, Level, Notes)
                 VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
              ''', (employee_id, shift_id, directory_id, pump_id, tank_id, reading_type, timestamp, level, notes))
    conn.commit()
    conn.close()
    return True


def get_shift_reading(employee_id, shift_id, directory_id, reading_type='baseline'):
    """Get the latest shift reading (baseline or end) for an employee and assignment."""
    conn = get_connection()
    if not conn:
        return None
    c = conn.cursor()
    c.execute('''SELECT Level, Timestamp FROM EmployeeShiftReadings
                 WHERE Employee_ID=%s AND Shift_ID=%s AND Directory_ID=%s AND Reading_Type=%s
                 ORDER BY Timestamp DESC LIMIT 1''', (employee_id, shift_id, directory_id, reading_type))
    res = c.fetchone()
    conn.close()
    return res


def clear_shift_readings(employee_id, shift_id, directory_id=None):
    """Clear shift readings after reconciliation (optional)."""
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()
    try:
        if directory_id:
            c.execute('DELETE FROM EmployeeShiftReadings WHERE Employee_ID=%s AND Shift_ID=%s AND Directory_ID=%s', (employee_id, shift_id, directory_id))
        else:
            c.execute('DELETE FROM EmployeeShiftReadings WHERE Employee_ID=%s AND Shift_ID=%s', (employee_id, shift_id))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        logger.error(f"Error clearing shift readings: {e}")
        conn.close()
        return False

def get_last_reading(tank_id, pump_id=None):
    """Get the last sensor reading for a tank/pump"""
    conn = get_connection()
    if not conn:
        return None
    c = conn.cursor()
    if pump_id:
        c.execute('SELECT Level, Timestamp FROM SensorReadings WHERE FuelTank_ID=%s AND Pump_ID=%s ORDER BY Timestamp DESC LIMIT 1',
                  (tank_id, pump_id))
    else:
        c.execute('SELECT Level, Timestamp FROM SensorReadings WHERE FuelTank_ID=%s ORDER BY Timestamp DESC LIMIT 1',
                  (tank_id,))
    result = c.fetchone()
    conn.close()
    return result

def add_employee_debt(employee_id, settlement_date, sold_quantity, unit_price, owed_amount, notes=None):
    """Add a new employee debt record"""
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()
    c.execute('INSERT INTO EmployeeDebt (Employee_ID, Settlement_Date, Sold_Quantity, Unit_Price, Owed_Amount, Notes) VALUES (%s, %s, %s, %s, %s, %s)',
              (employee_id, settlement_date, sold_quantity, unit_price, owed_amount, notes))
    conn.commit()
    conn.close()
    return True

def update_employee_debt_status(debt_id, status):
    """Update debt status (Paid/Pending)"""
    conn = get_connection()
    if not conn:
        return False
    c = conn.cursor()
    c.execute('UPDATE EmployeeDebt SET Status=%s WHERE Debt_ID=%s', (status, debt_id))
    conn.commit()
    conn.close()
    return True

def get_pending_debts():
    """Get all pending debts"""
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('''SELECT d.Debt_ID, d.Employee_ID, e.Emp_Name, d.Settlement_Date, d.Sold_Quantity, d.Unit_Price, d.Owed_Amount, d.Status, d.Notes
                 FROM EmployeeDebt d
                 JOIN Employees e ON d.Employee_ID = e.Employee_ID
                 WHERE d.Status = 'Pending'
                 ORDER BY d.Settlement_Date DESC''')
    data = c.fetchall()
    conn.close()
    return data

def get_employee_debts(employee_id):
    """Get debts for a specific employee"""
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('SELECT * FROM EmployeeDebt WHERE Employee_ID=%s ORDER BY Settlement_Date DESC', (employee_id,))
    data = c.fetchall()
    conn.close()
    return data

def get_fuel_price(fuel_type):
    """Get average fuel price from recent invoices"""
    conn = get_connection()
    if not conn:
        return 8.50  # Default price
    c = conn.cursor()
    c.execute('''SELECT AVG(Unit_Price) FROM Invoices
                 WHERE FuelType_ID=%s AND Invoice_Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)''', (fuel_type,))
    result = c.fetchone()
    conn.close()
    return result[0] if result and result[0] else 8.50

def get_pump_directory():
    """Get pump directory with employee assignments"""
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('SELECT * FROM PumpDirectory')
    data = c.fetchall()
    conn.close()
    return data


def add_pump_assignment(pump_id, station_id, employee_id=None, tank_id=None, fueltype_id=None, status='Active'):
    """Assign an employee/tank to a pump (insert into PumpDirectory).

    Returns True on success, False on failure.
    """
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO PumpDirectory (Pump_ID, Station_ID, Employee_ID, Tank_ID, FuelType_ID, Status)
                         VALUES (%s,%s,%s,%s,%s,%s)''',
                      (pump_id, station_id, employee_id, tank_id, fueltype_id, status))
            conn.commit()
            logger.info(f"Assigned pump {pump_id} -> employee {employee_id} / tank {tank_id}")
            return True
    except Exception as e:
        logger.error(f"Error adding pump assignment: {e}")
        try:
            # If using streamlit context, show error
            import streamlit as st
            st.error(f"خطأ في إضافة تعيين المضخة: {e}")
        except Exception:
            pass
        return False


def update_pump_assignment(directory_id, **kwargs):
    """Update an existing PumpDirectory entry by Directory_ID.

    kwargs: fields to update (Employee_ID, Tank_ID, FuelType_ID, Status, Pump_ID, Station_ID)
    """
    if not directory_id:
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            fields = []
            values = []
            for k, v in kwargs.items():
                fields.append(f"{k}=%s")
                values.append(v)
            values.append(directory_id)
            sql = f"UPDATE PumpDirectory SET {', '.join(fields)} WHERE Directory_ID=%s"
            c.execute(sql, tuple(values))
            conn.commit()
            logger.info(f"Updated PumpDirectory {directory_id}")
            return True
    except Exception as e:
        logger.error(f"Error updating pump assignment: {e}")
        try:
            import streamlit as st
            st.error(f"خطأ في تحديث تعيين المضخة: {e}")
        except Exception:
            pass
        return False


def delete_pump_assignment(directory_id):
    """Delete a PumpDirectory entry by Directory_ID."""
    if not directory_id:
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM PumpDirectory WHERE Directory_ID=%s', (directory_id,))
            conn.commit()
            logger.info(f"Deleted PumpDirectory {directory_id}")
            return True
    except Exception as e:
        logger.error(f"Error deleting pump assignment: {e}")
        try:
            import streamlit as st
            st.error(f"خطأ في حذف تعيين المضخة: {e}")
        except Exception:
            pass
        return False

def view_all_FuelTank_data():
    """Get all fuel tank data"""
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('SELECT * FROM FuelTanks WHERE Is_Active = TRUE')
    data = c.fetchall()
    conn.close()
    return data

def view_all_Employee_data():
    """Get all employee data (compatibility function)"""
    conn = get_connection()
    if not conn:
        return []
    c = conn.cursor()
    c.execute('SELECT * FROM Employees WHERE Is_Active = TRUE')
    data = c.fetchall()
    conn.close()
    return data

# Shift Operations
def add_shift(shift_name, start_time, end_time, description=None):
    """Add a new employee shift"""
    if not all([shift_name, start_time, end_time]):
        logger.error("Missing required parameters for shift")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('INSERT INTO EmployeeShifts (Shift_Name, Start_Time, End_Time, Description) VALUES (%s, %s, %s, %s)',
                      (shift_name, start_time, end_time, description))
            conn.commit()
            logger.info(f"Shift {shift_name} added successfully")
            return True
    except Exception as e:
        logger.error(f"Error adding shift: {e}")
        st.error(f"خطأ في إضافة المناوبة: {e}")
        return False

def get_all_shifts():
    """Get all active shifts"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM EmployeeShifts WHERE Is_Active = TRUE ORDER BY Start_Time')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} shifts")
            return data
    except Exception as e:
        logger.error(f"Error retrieving shifts: {e}")
        st.error(f"خطأ في استرجاع المناوبات: {e}")
        return []

# TankSensors CRUD
def add_tank_sensor(Tank_ID, Sensor_Type, Sensor_Model=None, Installation_Date=None, Last_Calibration=None, Next_Calibration=None, Is_Active=True, Sensor_Location=None, Measurement_Unit='Liters', Min_Threshold=None, Max_Threshold=None, Alert_Enabled=True, Notes=None):
    """Add a new tank sensor"""
    if not all([Tank_ID, Sensor_Type]):
        logger.error("Missing required parameters for tank sensor")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO TankSensors (Tank_ID, Sensor_Type, Sensor_Model, Installation_Date, Last_Calibration, Next_Calibration, Is_Active, Sensor_Location, Measurement_Unit, Min_Threshold, Max_Threshold, Alert_Enabled, Notes)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Tank_ID, Sensor_Type, Sensor_Model, Installation_Date, Last_Calibration, Next_Calibration, Is_Active, Sensor_Location, Measurement_Unit, Min_Threshold, Max_Threshold, Alert_Enabled, Notes))
            conn.commit()
            logger.info(f"Tank sensor added for tank {Tank_ID}")
            return True
    except Exception as e:
        logger.error(f"Error adding tank sensor: {e}")
        st.error(f"خطأ في إضافة مستشعر الخزان: {e}")
        return False

def get_all_tank_sensors():
    """Get all tank sensors"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM TankSensors')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} tank sensors")
            return data
    except Exception as e:
        logger.error(f"Error retrieving tank sensors: {e}")
        st.error(f"خطأ في استرجاع مستشعرات الخزانات: {e}")
        return []

def update_tank_sensor(sensor_id, **kwargs):
    """Update tank sensor details"""
    if not sensor_id:
        logger.error("Sensor ID is required for update")
        st.error("معرف المستشعر مطلوب للتحديث")
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key}=%s")
                values.append(value)
            values.append(sensor_id)
            sql = f"UPDATE TankSensors SET {', '.join(fields)} WHERE Sensor_ID=%s"
            c.execute(sql, tuple(values))
            conn.commit()
            logger.info(f"Tank sensor {sensor_id} updated")
            return True
    except Exception as e:
        logger.error(f"Error updating tank sensor: {e}")
        st.error(f"خطأ في تحديث مستشعر الخزان: {e}")
        return False

def delete_tank_sensor(sensor_id):
    """Delete tank sensor"""
    if not sensor_id:
        logger.error("Sensor ID is required for deletion")
        st.error("معرف المستشعر مطلوب للحذف")
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM TankSensors WHERE Sensor_ID=%s', (sensor_id,))
            conn.commit()
            logger.info(f"Tank sensor {sensor_id} deleted")
            return True
    except Exception as e:
        logger.error(f"Error deleting tank sensor: {e}")
        st.error(f"خطأ في حذف مستشعر الخزان: {e}")
        return False

# PumpSensors CRUD
def add_pump_sensor(Pump_ID, Sensor_Type, Sensor_Model=None, Installation_Date=None, Last_Calibration=None, Next_Calibration=None, Is_Active=True, Sensor_Location=None, Measurement_Unit='L/min', Min_Threshold=None, Max_Threshold=None, Alert_Enabled=True, Notes=None):
    """Add a new pump sensor"""
    if not all([Pump_ID, Sensor_Type]):
        logger.error("Missing required parameters for pump sensor")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO PumpSensors (Pump_ID, Sensor_Type, Sensor_Model, Installation_Date, Last_Calibration, Next_Calibration, Is_Active, Sensor_Location, Measurement_Unit, Min_Threshold, Max_Threshold, Alert_Enabled, Notes)
                         VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                      (Pump_ID, Sensor_Type, Sensor_Model, Installation_Date, Last_Calibration, Next_Calibration, Is_Active, Sensor_Location, Measurement_Unit, Min_Threshold, Max_Threshold, Alert_Enabled, Notes))
            conn.commit()
            logger.info(f"Pump sensor added for pump {Pump_ID}")
            return True
    except Exception as e:
        logger.error(f"Error adding pump sensor: {e}")
        st.error(f"خطأ في إضافة مستشعر المضخة: {e}")
        return False

def get_all_pump_sensors():
    """Get all pump sensors"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM PumpSensors')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} pump sensors")
            return data
    except Exception as e:
        logger.error(f"Error retrieving pump sensors: {e}")
        st.error(f"خطأ في استرجاع مستشعرات المضخات: {e}")
        return []

def update_pump_sensor(sensor_id, **kwargs):
    """Update pump sensor details"""
    if not sensor_id:
        logger.error("Sensor ID is required for update")
        st.error("معرف المستشعر مطلوب للتحديث")
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            fields = []
            values = []
            for key, value in kwargs.items():
                fields.append(f"{key}=%s")
                values.append(value)
            values.append(sensor_id)
            sql = f"UPDATE PumpSensors SET {', '.join(fields)} WHERE Sensor_ID=%s"
            c.execute(sql, tuple(values))
            conn.commit()
            logger.info(f"Pump sensor {sensor_id} updated")
            return True
    except Exception as e:
        logger.error(f"Error updating pump sensor: {e}")
        st.error(f"خطأ في تحديث مستشعر المضخة: {e}")
        return False

def delete_pump_sensor(sensor_id):
    """Delete pump sensor"""
    if not sensor_id:
        logger.error("Sensor ID is required for deletion")
        st.error("معرف المستشعر مطلوب للحذف")
        return False
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('DELETE FROM PumpSensors WHERE Sensor_ID=%s', (sensor_id,))
            conn.commit()
            logger.info(f"Pump sensor {sensor_id} deleted")
            return True
    except Exception as e:
        logger.error(f"Error deleting pump sensor: {e}")
        st.error(f"خطأ في حذف مستشعر المضخة: {e}")
        return False

def assign_employee_to_shift(employee_id, station_id, shift_id, assignment_date):
    """Assign employee to a shift at a station"""
    if not all([employee_id, station_id, shift_id, assignment_date]):
        logger.error("Missing required parameters for assignment")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO EmployeeStationAssignments
                         (Employee_ID, Station_ID, Shift_ID, Assignment_Date)
                         VALUES (%s, %s, %s, %s)''',
                      (employee_id, station_id, shift_id, assignment_date))
            conn.commit()
            logger.info(f"Employee {employee_id} assigned to shift {shift_id} successfully")
            return True
    except Exception as e:
        logger.error(f"Error assigning employee to shift: {e}")
        st.error(f"خطأ في تعيين الموظف للمناوبة: {e}")
        return False

def get_employee_assignments():
    """Get all employee shift assignments"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT esa.*, e.Emp_Name, s.Station_Name, sh.Shift_Name, sh.Start_Time, sh.End_Time
                         FROM EmployeeStationAssignments esa
                         JOIN Employees e ON esa.Employee_ID = e.Employee_ID
                         JOIN PetrolStations s ON esa.Station_ID = s.Station_ID
                         LEFT JOIN EmployeeShifts sh ON esa.Shift_ID = sh.Shift_ID
                         WHERE esa.Is_Active = TRUE
                         ORDER BY esa.Assignment_Date DESC''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} assignments")
            return data
    except Exception as e:
        logger.error(f"Error retrieving assignments: {e}")
        st.error(f"خطأ في استرجاع التعيينات: {e}")
        return []

# Dispensers CRUD Operations
def add_dispenser(Dispenser_ID, Station_ID, Serial_Number, Status='active'):
    """Add a new dispenser"""
    if not all([Dispenser_ID, Station_ID, Serial_Number]):
        logger.error("Missing required parameters for dispenser")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO Dispensers (Dispenser_ID, Station_ID, Serial_Number, Status)
                         VALUES (%s, %s, %s, %s)''',
                      (Dispenser_ID, Station_ID, Serial_Number, Status))
            conn.commit()
            logger.info(f"Dispenser {Dispenser_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding dispenser: {e}")
        st.error("رقم الموزع موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding dispenser: {e}")
        st.error(f"خطأ في إضافة الموزع: {e}")
        return False

def get_all_dispensers():
    """Get all dispensers with station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT d.*, s.Station_Name
                         FROM Dispensers d
                         JOIN PetrolStations s ON d.Station_ID = s.Station_ID
                         ORDER BY s.Station_Name, d.Dispenser_ID''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} dispensers")
            return data
    except Exception as e:
        logger.error(f"Error retrieving dispensers: {e}")
        st.error(f"خطأ في استرجاع الموزعات: {e}")
        return []

# Nozzles CRUD Operations
def add_nozzle(Nozzle_ID, Dispenser_ID, FuelType_ID, Meter_Reading_Start, Meter_Reading_Current):
    """Add a new nozzle"""
    if not all([Nozzle_ID, Dispenser_ID, FuelType_ID, Meter_Reading_Start, Meter_Reading_Current]):
        logger.error("Missing required parameters for nozzle")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO Nozzles (Nozzle_ID, Dispenser_ID, FuelType_ID, Meter_Reading_Start, Meter_Reading_Current)
                         VALUES (%s, %s, %s, %s, %s)''',
                      (Nozzle_ID, Dispenser_ID, FuelType_ID, Meter_Reading_Start, Meter_Reading_Current))
            conn.commit()
            logger.info(f"Nozzle {Nozzle_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding nozzle: {e}")
        st.error("رقم الفوهة موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding nozzle: {e}")
        st.error(f"خطأ في إضافة الفوهة: {e}")
        return False

def get_all_nozzles():
    """Get all nozzles with dispenser and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT n.*, d.Serial_Number as Dispenser_Serial, ft.FuelType_Name
                         FROM Nozzles n
                         JOIN Dispensers d ON n.Dispenser_ID = d.Dispenser_ID
                         JOIN FuelTypes ft ON n.FuelType_ID = ft.FuelType_ID
                         ORDER BY d.Serial_Number, n.Nozzle_ID''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} nozzles")
            return data
    except Exception as e:
        logger.error(f"Error retrieving nozzles: {e}")
        st.error(f"خطأ في استرجاع الفوهات: {e}")
        return []

# Flowmeters CRUD Operations
def add_flowmeter(Flowmeter_ID, Station_ID, FuelType_ID, Serial_Number, Total_Flow_Liters):
    """Add a new flowmeter"""
    if not all([Flowmeter_ID, Station_ID, FuelType_ID, Serial_Number, Total_Flow_Liters]):
        logger.error("Missing required parameters for flowmeter")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO Flowmeters (Flowmeter_ID, Station_ID, FuelType_ID, Serial_Number, Total_Flow_Liters)
                         VALUES (%s, %s, %s, %s, %s)''',
                      (Flowmeter_ID, Station_ID, FuelType_ID, Serial_Number, Total_Flow_Liters))
            conn.commit()
            logger.info(f"Flowmeter {Flowmeter_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding flowmeter: {e}")
        st.error("رقم عداد التدفق موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding flowmeter: {e}")
        st.error(f"خطأ في إضافة عداد التدفق: {e}")
        return False

def get_all_flowmeters():
    """Get all flowmeters with station and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT f.*, s.Station_Name, ft.FuelType_Name
                         FROM Flowmeters f
                         JOIN PetrolStations s ON f.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON f.FuelType_ID = ft.FuelType_ID
                         ORDER BY s.Station_Name, f.Flowmeter_ID''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} flowmeters")
            return data
    except Exception as e:
        logger.error(f"Error retrieving flowmeters: {e}")
        st.error(f"خطأ في استرجاع عدادات التدفق: {e}")
        return []

# Price Signs CRUD Operations
def add_price_sign(PriceSign_ID, Station_ID, FuelType_ID, Price):
    """Add a new price sign"""
    if not all([PriceSign_ID, Station_ID, FuelType_ID, Price]):
        logger.error("Missing required parameters for price sign")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO PriceSigns (PriceSign_ID, Station_ID, FuelType_ID, Price)
                         VALUES (%s, %s, %s, %s)''',
                      (PriceSign_ID, Station_ID, FuelType_ID, Price))
            conn.commit()
            logger.info(f"Price sign {PriceSign_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding price sign: {e}")
        st.error("رقم لوحة السعر موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding price sign: {e}")
        st.error(f"خطأ في إضافة لوحة السعر: {e}")
        return False

def get_all_price_signs():
    """Get all price signs with station and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT ps.*, s.Station_Name, ft.FuelType_Name
                         FROM PriceSigns ps
                         JOIN PetrolStations s ON ps.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON ps.FuelType_ID = ft.FuelType_ID
                         ORDER BY s.Station_Name, ps.Last_Updated DESC''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} price signs")
            return data
    except Exception as e:
        logger.error(f"Error retrieving price signs: {e}")
        st.error(f"خطأ في استرجاع لوحات الأسعار: {e}")
        return []

# Payment Terminals CRUD Operations
def add_payment_terminal(Terminal_ID, Station_ID, Type, Serial_Number, Status='active'):
    """Add a new payment terminal"""
    if not all([Terminal_ID, Station_ID, Type, Serial_Number]):
        logger.error("Missing required parameters for payment terminal")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO PaymentTerminals (Terminal_ID, Station_ID, Type, Serial_Number, Status)
                         VALUES (%s, %s, %s, %s, %s)''',
                      (Terminal_ID, Station_ID, Type, Serial_Number, Status))
            conn.commit()
            logger.info(f"Payment terminal {Terminal_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding payment terminal: {e}")
        st.error("رقم الجهاز الطرفي موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding payment terminal: {e}")
        st.error(f"خطأ في إضافة الجهاز الطرفي: {e}")
        return False

def get_all_payment_terminals():
    """Get all payment terminals with station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT pt.*, s.Station_Name
                         FROM PaymentTerminals pt
                         JOIN PetrolStations s ON pt.Station_ID = s.Station_ID
                         ORDER BY s.Station_Name, pt.Type''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} payment terminals")
            return data
    except Exception as e:
        logger.error(f"Error retrieving payment terminals: {e}")
        st.error(f"خطأ في استرجاع الأجهزة الطرفية: {e}")
        return []

# AVI Vehicles CRUD Operations
def add_avi_vehicle(Vehicle_ID, RFID_Tag, License_Plate=None, Customer_ID=None, FuelType_ID=None):
    """Add a new AVI vehicle"""
    if not all([Vehicle_ID, RFID_Tag]):
        logger.error("Missing required parameters for AVI vehicle")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO AVI_Vehicles (Vehicle_ID, RFID_Tag, License_Plate, Customer_ID, FuelType_ID)
                         VALUES (%s, %s, %s, %s, %s)''',
                      (Vehicle_ID, RFID_Tag, License_Plate, Customer_ID, FuelType_ID))
            conn.commit()
            logger.info(f"AVI vehicle {Vehicle_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding AVI vehicle: {e}")
        st.error("رقم المركبة أو علامة RFID موجودة بالفعل")
        return False
    except Exception as e:
        logger.error(f"Error adding AVI vehicle: {e}")
        st.error(f"خطأ في إضافة مركبة AVI: {e}")
        return False

def get_all_avi_vehicles():
    """Get all AVI vehicles with customer and fuel type info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT av.*, c.C_Name as Customer_Name, ft.FuelType_Name
                         FROM AVI_Vehicles av
                         LEFT JOIN Customers c ON av.Customer_ID = c.Customer_Code
                         LEFT JOIN FuelTypes ft ON av.FuelType_ID = ft.FuelType_ID
                         ORDER BY av.Last_Seen DESC''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} AVI vehicles")
            return data
    except Exception as e:
        logger.error(f"Error retrieving AVI vehicles: {e}")
        st.error(f"خطأ في استرجاع مركبات AVI: {e}")
        return []

# RFID Readers CRUD Operations
def add_rfid_reader(Reader_ID, Station_ID, Serial_Number, Location=None, Status='active'):
    """Add a new RFID reader"""
    if not all([Reader_ID, Station_ID, Serial_Number]):
        logger.error("Missing required parameters for RFID reader")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO RFID_Readers (Reader_ID, Station_ID, Serial_Number, Location, Status)
                         VALUES (%s, %s, %s, %s, %s)''',
                      (Reader_ID, Station_ID, Serial_Number, Location, Status))
            conn.commit()
            logger.info(f"RFID reader {Reader_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding RFID reader: {e}")
        st.error("رقم قارئ RFID موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding RFID reader:    ز22 {e}")
        st.error(f"خطأ في إضافة قارئ RFID: {e}")
        return False

def get_all_rfid_readers():
    """Get all RFID readers with station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT rr.*, s.Station_Name
                         FROM RFID_Readers rr
                         JOIN PetrolStations s ON rr.Station_ID = s.Station_ID
                         ORDER BY s.Station_Name, rr.Reader_ID''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} RFID readers")
            return data
    except Exception as e:
        logger.error(f"Error retrieving RFID readers: {e}")
        st.error(f"خطأ في استرجاع قارئات RFID: {e}")
        return []

# Forecourt Controllers CRUD Operations
def add_forecourt_controller(Controller_ID, Station_ID, Serial_Number, IP_Address=None, Firmware_Version=None, Status='online'):
    """Add a new forecourt controller"""
    if not all([Controller_ID, Station_ID, Serial_Number]):
        logger.error("Missing required parameters for forecourt controller")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO ForecourtControllers (Controller_ID, Station_ID, Serial_Number, IP_Address, Firmware_Version, Status)
                         VALUES (%s, %s, %s, %s, %s, %s)''',
                      (Controller_ID, Station_ID, Serial_Number, IP_Address, Firmware_Version, Status))
            conn.commit()
            logger.info(f"Forecourt controller {Controller_ID} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding forecourt controller: {e}")
        st.error("رقم وحدة التحكم موجود بالفعل أو خطأ في البيانات المرجعية")
        return False
    except Exception as e:
        logger.error(f"Error adding forecourt controller: {e}")
        st.error(f"خطأ في إضافة وحدة التحكم: {e}")
        return False

def get_all_forecourt_controllers():
    """Get all forecourt controllers with station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT fc.*, s.Station_Name
                         FROM ForecourtControllers fc
                         JOIN PetrolStations s ON fc.Station_ID = s.Station_ID
                         ORDER BY s.Station_Name, fc.Controller_ID''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} forecourt controllers")
            return data
    except Exception as e:
        logger.error(f"Error retrieving forecourt controllers: {e}")
        st.error(f"خطأ في استرجاع وحدات التحكم: {e}")
        return []

# System Logs CRUD Operations
def add_system_log(Station_ID, Event_Type, Description, Severity='info'):
    """Add a new system log entry"""
    if not all([Event_Type, Description]):
        logger.error("Missing required parameters for system log")
        st.error("جميع الحقول المطلوبة غير مكتملة")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO SystemLogs (Station_ID, Event_Type, Description, Severity)
                         VALUES (%s, %s, %s, %s)''',
                      (Station_ID, Event_Type, Description, Severity))
            conn.commit()
            logger.info(f"System log added successfully")
            return True
    except Exception as e:
        logger.error(f"Error adding system log: {e}")
        st.error(f"خطأ في إضافة سجل النظام: {e}")
        return False

def get_all_system_logs(limit=100):
    """Get system logs with station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT sl.*, s.Station_Name
                         FROM SystemLogs sl
                         LEFT JOIN PetrolStations s ON sl.Station_ID = s.Station_ID
                         ORDER BY sl.Timestamp DESC
                         LIMIT %s''', (limit,))
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} system logs")
            return data
    except Exception as e:
        logger.error(f"Error retrieving system logs: {e}")
        st.error(f"خطأ في استرجاع سجلات النظام: {e}")
        return []

def get_all_customers():
    """Get all اactive customers"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM Customers WHERE Is_Active = TRUE ORDER BY C_Name')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} customers")
            return data
    except Exception as e:
        logger.error(f"Error retrieving customers: {e}")
        st.error(f"خطأ في استرجاع العملاء: {e}")
        return []

# System Settings Operations
def get_system_settings():
    """Get all system settings"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM SystemSettings WHERE Is_Active = TRUE ORDER BY Setting_Name')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} system settings")
            return data
    except Exception as e:
        logger.error(f"Error retrieving system settings: {e}")
        st.error(f"خطأ في استرجاع إعدادات النظام: {e}")
        return []

def get_system_setting(setting_id):
    """Get a specific system setting by ID"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM SystemSettings WHERE Setting_ID = %s AND Is_Active = TRUE', (setting_id,))
            data = c.fetchone()
            return data
    except Exception as e:
        logger.error(f"Error retrieving system setting {setting_id}: {e}")
        return None

def update_system_setting(setting_id, setting_value, setting_description=None):
    """Update a system setting value"""
    if not setting_id or setting_value is None:
        logger.error("Missing required parameters for system setting update")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            if setting_description:
                c.execute('''UPDATE SystemSettings
                            SET Setting_Value = %s, Setting_Description = %s
                            WHERE Setting_ID = %s''',
                         (setting_value, setting_description, setting_id))
            else:
                c.execute('''UPDATE SystemSettings
                            SET Setting_Value = %s
                            WHERE Setting_ID = %s''',
                         (setting_value, setting_id))
            conn.commit()
            logger.info(f"System setting {setting_id} updated successfully")
            return True
    except Exception as e:
        logger.error(f"Error updating system setting {setting_id}: {e}")
        st.error(f"خطأ في تحديث إعداد النظام: {e}")
        return False

def add_system_setting(setting_id, setting_name, setting_value, setting_description=None):
    """Add a new system setting"""
    if not all([setting_id, setting_name]):
        logger.error("Missing required parameters for system setting")
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO SystemSettings (Setting_ID, Setting_Name, Setting_Value, Setting_Description)
                         VALUES (%s, %s, %s, %s)''',
                      (setting_id, setting_name, setting_value, setting_description))
            conn.commit()
            logger.info(f"System setting {setting_id} added successfully")
            return True
    except pymysql.IntegrityError as e:
        logger.error(f"Integrity error adding system setting: {e}")
        st.error("معرف الإعداد موجود بالفعل")
        return False
    except Exception as e:
        logger.error(f"Error adding system setting: {e}")
        st.error(f"خطأ في إضافة إعداد النظام: {e}")
        return False

def get_setting_value(setting_id, default_value=None):
    """Get the value of a specific setting"""
    setting = get_system_setting(setting_id)
    if setting:
        return setting[2]  # Setting_Value is at index 2
    return default_value

def update_multiple_settings(settings_dict):
    """Update multiple system settings at once"""
    if not settings_dict:
        return False

    try:
        with get_connection() as conn:
            c = conn.cursor()
            for setting_id, setting_value in settings_dict.items():
                c.execute('''UPDATE SystemSettings
                            SET Setting_Value = %s
                            WHERE Setting_ID = %s''',
                         (setting_value, setting_id))
            conn.commit()
            logger.info(f"Updated {len(settings_dict)} system settings successfully")
            return True
    except Exception as e:
        logger.error(f"Error updating multiple system settings: {e}")
        st.error(f"خطأ في تحديث إعدادات النظام: {e}")
        return False

def get_all_sensor_readings():
    """Get all sensor readings with tank and station info"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT sr.*, t.Tank_Name, s.Station_Name, ft.FuelType_Name
                         FROM SensorReadings sr
                         JOIN FuelTanks t ON sr.FuelTank_ID = t.Tank_ID
                         JOIN PetrolStations s ON t.Station_ID = s.Station_ID
                         JOIN FuelTypes ft ON t.FuelType_ID = ft.FuelType_ID
                         ORDER BY sr.Timestamp DESC
                         LIMIT 1000''')
            data = c.fetchall()
            logger.debug(f"Retrieved {len(data)} sensor readings")
            return data
    except Exception as e:
        logger.error(f"Error retrieving sensor readings: {e}")
        st.error(f"خطأ في استرجاع قراءات المستشعرات: {e}")
        return []

def get_pump_meter_reading(pump_id):
    """Get pump meter reading from FuelPumps table Total_Liters_Dispensed"""
    try:
        with get_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT Total_Liters_Dispensed FROM FuelPumps WHERE Pump_ID = %s', (pump_id,))
            result = c.fetchone()
            if result and result[0] is not None:
                return float(result[0])
            else:
                # If no reading found, try to get from associated nozzles
                c.execute('''SELECT SUM(Meter_Reading_Current) as total_reading
                           FROM Nozzles n
                           JOIN Dispensers d ON n.Dispenser_ID = d.Dispenser_ID
                           JOIN FuelPumps p ON d.Station_ID = p.Station_ID
                           WHERE p.Pump_ID = %s''', (pump_id,))
                nozzle_result = c.fetchone()
                if nozzle_result and nozzle_result[0] is not None:
                    return float(nozzle_result[0])
                else:
                    # Fallback to flowmeter data
                    c.execute('''SELECT Total_Flow_Liters
                               FROM Flowmeters f
                               JOIN FuelPumps p ON f.Station_ID = p.Station_ID AND f.FuelType_ID = p.FuelType_ID
                               WHERE p.Pump_ID = %s
                               ORDER BY f.Last_Reading_Timestamp DESC
                               LIMIT 1''', (pump_id,))
                    flow_result = c.fetchone()
                    if flow_result and flow_result[0] is not None:
                        return float(flow_result[0])
                    else:
                        return 0.0
    except Exception as e:
        logger.error(f"Error retrieving pump meter reading for {pump_id}: {e}")
        return 0.0
