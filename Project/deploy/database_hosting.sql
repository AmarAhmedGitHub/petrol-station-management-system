-- Petrol Station Management System Database Schema
-- For Hosting on External MySQL Server (Hostinger, AWS RDS, etc.)

-- Create Database
CREATE DATABASE IF NOT EXISTS Petrolpump_Management_Enhanced
CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

USE Petrolpump_Management_Enhanced;

-- ===========================================
-- 1. FUEL TYPES TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS FuelTypes (
    FuelType_ID VARCHAR(10) PRIMARY KEY,
    FuelType_Name VARCHAR(50) NOT NULL,
    FuelType_Description TEXT,
    Unit_Price DECIMAL(10,2) NOT NULL,
    Is_Active BOOLEAN DEFAULT TRUE,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- 2. OWNERS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS Owners (
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
);

-- ===========================================
-- 3. PETROL STATIONS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS PetrolStations (
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
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- 4. EMPLOYEES TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS Employees (
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
    FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
    FOREIGN KEY(Manager_ID) REFERENCES Employees(Employee_ID)
);

-- Add foreign key for PetrolStations Manager_ID after Employees table
ALTER TABLE PetrolStations
ADD CONSTRAINT fk_station_manager
FOREIGN KEY(Manager_ID) REFERENCES Employees(Employee_ID);

-- ===========================================
-- 5. FUEL TANKS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS FuelTanks (
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
);

-- ===========================================
-- 6. FUEL PUMPS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS FuelPumps (
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
);

-- ===========================================
-- 7. CUSTOMERS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS Customers (
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
);

-- ===========================================
-- 8. INVOICES TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS Invoices (
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
);

-- ===========================================
-- 9. FUEL SUPPLY TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS FuelSupply (
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
);

-- ===========================================
-- 10. PUMP MAINTENANCE TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS PumpMaintenance (
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
);

-- ===========================================
-- 11. TANK MAINTENANCE TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS TankMaintenance (
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
);

-- ===========================================
-- 12. EMPLOYEE DEBT TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS EmployeeDebt (
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
);

-- ===========================================
-- 13. STATION OWNERS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS StationOwners (
    Station_ID VARCHAR(10) NOT NULL,
    Owner_ID VARCHAR(10) NOT NULL,
    Ownership_Percent DECIMAL(5,2) NOT NULL,
    Is_Primary_Owner BOOLEAN DEFAULT FALSE,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY(Station_ID, Owner_ID),
    FOREIGN KEY(Station_ID) REFERENCES PetrolStations(Station_ID),
    FOREIGN KEY(Owner_ID) REFERENCES Owners(Owner_ID)
);

-- ===========================================
-- 14. SYSTEM SETTINGS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS SystemSettings (
    Setting_ID VARCHAR(20) PRIMARY KEY,
    Setting_Name VARCHAR(50) NOT NULL,
    Setting_Value TEXT,
    Setting_Description TEXT,
    Is_Active BOOLEAN DEFAULT TRUE,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- 15. AUDIT LOG TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS AuditLog (
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
);

-- ===========================================
-- 16. SENSOR READINGS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS SensorReadings (
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
);

-- ===========================================
-- 17. TANK SENSORS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS TankSensors (
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
);

-- ===========================================
-- 18. PUMP SENSORS TABLE
-- ===========================================
CREATE TABLE IF NOT EXISTS PumpSensors (
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
);

-- ===========================================
-- ACCOUNTING TABLES (from accounting_system.py)
-- ===========================================

-- Chart of Accounts
CREATE TABLE IF NOT EXISTS ChartOfAccounts (
    Account_ID VARCHAR(20) PRIMARY KEY,
    Account_Name VARCHAR(100) NOT NULL,
    Account_Type VARCHAR(20) NOT NULL,
    Parent_Account_ID VARCHAR(20),
    Account_Level INT DEFAULT 1,
    Is_Active BOOLEAN DEFAULT TRUE,
    Opening_Balance DECIMAL(15,2) DEFAULT 0,
    Current_Balance DECIMAL(15,2) DEFAULT 0,
    Description TEXT,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(Parent_Account_ID) REFERENCES ChartOfAccounts(Account_ID)
);

-- Journal Entries
CREATE TABLE IF NOT EXISTS JournalEntries (
    Entry_ID INT AUTO_INCREMENT PRIMARY KEY,
    Entry_Date DATE NOT NULL,
    Entry_Number VARCHAR(20) UNIQUE NOT NULL,
    Description TEXT,
    Total_Debit DECIMAL(15,2) DEFAULT 0,
    Total_Credit DECIMAL(15,2) DEFAULT 0,
    Status VARCHAR(20) DEFAULT 'Draft',
    Posted_By VARCHAR(10),
    Posted_Date TIMESTAMP NULL,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(Posted_By) REFERENCES Employees(Employee_ID)
);

-- Journal Entry Details
CREATE TABLE IF NOT EXISTS JournalEntryDetails (
    Detail_ID INT AUTO_INCREMENT PRIMARY KEY,
    Entry_ID INT NOT NULL,
    Account_ID VARCHAR(20) NOT NULL,
    Debit_Amount DECIMAL(15,2) DEFAULT 0,
    Credit_Amount DECIMAL(15,2) DEFAULT 0,
    Description TEXT,
    Reference_No VARCHAR(50),
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(Entry_ID) REFERENCES JournalEntries(Entry_ID),
    FOREIGN KEY(Account_ID) REFERENCES ChartOfAccounts(Account_ID)
);

-- Receipt Vouchers
CREATE TABLE IF NOT EXISTS ReceiptVouchers (
    Receipt_ID VARCHAR(20) PRIMARY KEY,
    Receipt_Date DATE NOT NULL,
    Receipt_Number VARCHAR(20) UNIQUE NOT NULL,
    Received_From VARCHAR(100) NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Payment_Method VARCHAR(20) NOT NULL,
    Reference_No VARCHAR(50),
    Description TEXT,
    Received_By VARCHAR(10),
    Status VARCHAR(20) DEFAULT 'Draft',
    Posted_Date TIMESTAMP NULL,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(Received_By) REFERENCES Employees(Employee_ID)
);

-- Payment Vouchers
CREATE TABLE IF NOT EXISTS PaymentVouchers (
    Payment_ID VARCHAR(20) PRIMARY KEY,
    Payment_Date DATE NOT NULL,
    Payment_Number VARCHAR(20) UNIQUE NOT NULL,
    Paid_To VARCHAR(100) NOT NULL,
    Amount DECIMAL(15,2) NOT NULL,
    Payment_Method VARCHAR(20) NOT NULL,
    Reference_No VARCHAR(50),
    Description TEXT,
    Paid_By VARCHAR(10),
    Status VARCHAR(20) DEFAULT 'Draft',
    Posted_Date TIMESTAMP NULL,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(Paid_By) REFERENCES Employees(Employee_ID)
);

-- Tax Settings
CREATE TABLE IF NOT EXISTS TaxSettings (
    Tax_ID VARCHAR(10) PRIMARY KEY,
    Tax_Name VARCHAR(50) NOT NULL,
    Tax_Rate DECIMAL(5,2) NOT NULL,
    Tax_Type VARCHAR(20) NOT NULL,
    Is_Active BOOLEAN DEFAULT TRUE,
    Description TEXT,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoice Tax Details
CREATE TABLE IF NOT EXISTS InvoiceTaxDetails (
    Tax_Detail_ID INT AUTO_INCREMENT PRIMARY KEY,
    Invoice_No VARCHAR(15) NOT NULL,
    Tax_ID VARCHAR(10) NOT NULL,
    Tax_Amount DECIMAL(10,2) NOT NULL,
    Tax_Rate DECIMAL(5,2) NOT NULL,
    Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(Invoice_No) REFERENCES Invoices(Invoice_No),
    FOREIGN KEY(Tax_ID) REFERENCES TaxSettings(Tax_ID)
);

-- ===========================================
-- INSERT DEFAULT DATA
-- ===========================================

-- Insert default fuel types
INSERT IGNORE INTO FuelTypes (FuelType_ID, FuelType_Name, FuelType_Description, Unit_Price) VALUES
('FUEL001', 'بنزين 95', 'بنزين عادي 95 أوكتان', 8.50),
('FUEL002', 'بنزين 98', 'بنزين سوبر 98 أوكتان', 9.25),
('FUEL003', 'ديزل', 'وقود الديزل', 7.80),
('FUEL004', 'كيروسين', 'وقود الطائرات', 6.90);

-- Insert default system settings
INSERT IGNORE INTO SystemSettings (Setting_ID, Setting_Name, Setting_Value, Setting_Description) VALUES
('MAINT_PUMP', 'Pump Maintenance Interval', '90', 'فترة الصيانة للمضخات بالأيام'),
('MAINT_TANK', 'Tank Maintenance Interval', '180', 'فترة الصيانة للخزانات بالأيام'),
('LOW_FUEL_ALERT', 'Low Fuel Alert Level', '20', 'نسبة التنبيه لانخفاض الوقود (%)'),
('MAX_DISCOUNT', 'Maximum Discount', '15', 'الحد الأقصى للخصم (%)'),
('COMPANY_NAME', 'Company Name', 'شركة محطات الوقود المحدودة', 'اسم الشركة'),
('CURRENCY', 'Currency', 'SAR', 'العملة المستخدمة'),
('TAX_RATE', 'Default Tax Rate', '15', 'معدل الضريبة الافتراضي (%)');

-- Insert default tax settings
INSERT IGNORE INTO TaxSettings (Tax_ID, Tax_Name, Tax_Rate, Tax_Type) VALUES
('VAT', 'ضريبة القيمة المضافة', 15.00, 'VAT'),
('EXCISE', 'ضريبة السلع الانتقائية', 50.00, 'Excise');

-- Insert default chart of accounts (basic structure)
INSERT IGNORE INTO ChartOfAccounts (Account_ID, Account_Name, Account_Type, Account_Level, Description) VALUES
('1000', 'الأصول', 'Asset', 1, 'حسابات الأصول'),
('1001', 'الأصول المتداولة', 'Asset', 2, 'الأصول المتداولة'),
('1001001', 'النقدية', 'Asset', 3, 'النقدية في البنوك'),
('1001002', 'الحسابات المدينة', 'Asset', 3, 'الحسابات المدينة'),
('1001003', 'المخزون', 'Asset', 3, 'مخزون الوقود'),
('1002', 'الأصول الثابتة', 'Asset', 2, 'الأصول الثابتة'),
('1002001', 'الأراضي والمباني', 'Asset', 3, 'الأراضي والمباني'),
('1002002', 'المعدات', 'Asset', 3, 'المعدات والآلات'),
('2000', 'الخصوم', 'Liability', 1, 'حسابات الخصوم'),
('2001', 'الخصوم المتداولة', 'Liability', 2, 'الخصوم المتداولة'),
('2001001', 'الحسابات الدائنة', 'Liability', 3, 'الحسابات الدائنة'),
('2001002', 'القروض قصيرة الأجل', 'Liability', 3, 'القروض قصيرة الأجل'),
('3000', 'حقوق الملكية', 'Equity', 1, 'حقوق الملكية'),
('3001001', 'رأس المال', 'Equity', 2, 'رأس المال'),
('4000', 'الإيرادات', 'Revenue', 1, 'حسابات الإيرادات'),
('4001001', 'إيرادات المبيعات', 'Revenue', 2, 'إيرادات مبيعات الوقود'),
('5000', 'المصروفات', 'Expense', 1, 'حسابات المصروفات'),
('5001001', 'تكلفة المبيعات', 'Expense', 2, 'تكلفة المبيعات'),
('5001002', 'المصروفات التشغيلية', 'Expense', 2, 'المصروفات التشغيلية'),
('5001003', 'مصروفات الصيانة', 'Expense', 2, 'مصروفات الصيانة والإصلاح');

-- Insert default admin user
INSERT IGNORE INTO Employees (Employee_ID, Emp_Name, Designation, Email_ID, Is_Active) VALUES
('ADMIN001', 'Administrator', 'System Administrator', 'admin@petrolstation.com', TRUE);

-- ===========================================
-- CREATE DATABASE USER (Optional - for security)
-- ===========================================
-- Note: Run these commands separately with appropriate privileges
-- CREATE USER 'petrol_user'@'%' IDENTIFIED BY 'secure_password_here';
-- GRANT ALL PRIVILEGES ON Petrolpump_Management_Enhanced.* TO 'petrol_user'@'%';
-- FLUSH PRIVILEGES;

COMMIT;
