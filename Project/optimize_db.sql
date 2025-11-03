-- Database Optimization Script for Petrol Pump Management System
-- This script creates indexes to improve query performance

USE Petrolpump_Management_Enhanced;

-- Indexes for PetrolStations table
CREATE INDEX idx_petrol_stations_active ON PetrolStations(Is_Active);
CREATE INDEX idx_petrol_stations_name ON PetrolStations(Station_Name);
CREATE INDEX idx_petrol_stations_manager ON PetrolStations(Manager_ID);

-- Indexes for FuelTypes table
CREATE INDEX idx_fuel_types_active ON FuelTypes(Is_Active);
CREATE INDEX idx_fuel_types_name ON FuelTypes(FuelType_Name);

-- Indexes for Employees table
CREATE INDEX idx_employees_station ON Employees(Station_ID);
CREATE INDEX idx_employees_active ON Employees(Is_Active);
CREATE INDEX idx_employees_manager ON Employees(Manager_ID);
CREATE INDEX idx_employees_name ON Employees(Emp_Name);

-- Indexes for FuelTanks table
CREATE INDEX idx_fuel_tanks_station ON FuelTanks(Station_ID);
CREATE INDEX idx_fuel_tanks_fuel_type ON FuelTanks(FuelType_ID);
CREATE INDEX idx_fuel_tanks_active ON FuelTanks(Is_Active);
CREATE INDEX idx_fuel_tanks_name ON FuelTanks(Tank_Name);

-- Indexes for FuelPumps table
CREATE INDEX idx_fuel_pumps_station ON FuelPumps(Station_ID);
CREATE INDEX idx_fuel_pumps_fuel_type ON FuelPumps(FuelType_ID);
CREATE INDEX idx_fuel_pumps_tank ON FuelPumps(Tank_ID);
CREATE INDEX idx_fuel_pumps_employee ON FuelPumps(Employee_ID);
CREATE INDEX idx_fuel_pumps_active ON FuelPumps(Is_Active);
CREATE INDEX idx_fuel_pumps_number ON FuelPumps(Pump_Number);

-- Indexes for Customers table
CREATE INDEX idx_customers_active ON Customers(Is_Active);
CREATE INDEX idx_customers_name ON Customers(C_Name);
CREATE INDEX idx_customers_phone ON Customers(Phone_No);

-- Indexes for Invoices table (most critical for performance)
CREATE INDEX idx_invoices_station ON Invoices(Station_ID);
CREATE INDEX idx_invoices_pump ON Invoices(Pump_ID);
CREATE INDEX idx_invoices_tank ON Invoices(Tank_ID);
CREATE INDEX idx_invoices_employee ON Invoices(Employee_ID);
CREATE INDEX idx_invoices_customer ON Invoices(Customer_Code);
CREATE INDEX idx_invoices_fuel_type ON Invoices(FuelType_ID);
CREATE INDEX idx_invoices_date ON Invoices(Invoice_Date);
CREATE INDEX idx_invoices_payment_status ON Invoices(Payment_Status);

-- Composite indexes for common query patterns
CREATE INDEX idx_invoices_station_date ON Invoices(Station_ID, Invoice_Date);
CREATE INDEX idx_invoices_date_amount ON Invoices(Invoice_Date, Total_Amount);

-- Indexes for FuelSupply table
CREATE INDEX idx_fuel_supply_station ON FuelSupply(Station_ID);
CREATE INDEX idx_fuel_supply_tank ON FuelSupply(Tank_ID);
CREATE INDEX idx_fuel_supply_fuel_type ON FuelSupply(FuelType_ID);
CREATE INDEX idx_fuel_supply_date ON FuelSupply(Supply_Date);

-- Indexes for PumpMaintenance table
CREATE INDEX idx_pump_maintenance_pump ON PumpMaintenance(Pump_ID);
CREATE INDEX idx_pump_maintenance_station ON PumpMaintenance(Station_ID);
CREATE INDEX idx_pump_maintenance_date ON PumpMaintenance(Maintenance_Date);
CREATE INDEX idx_pump_maintenance_next_date ON PumpMaintenance(Next_Maintenance_Date);

-- Indexes for TankMaintenance table
CREATE INDEX idx_tank_maintenance_tank ON TankMaintenance(Tank_ID);
CREATE INDEX idx_tank_maintenance_station ON TankMaintenance(Station_ID);
CREATE INDEX idx_tank_maintenance_date ON TankMaintenance(Maintenance_Date);
CREATE INDEX idx_tank_maintenance_next_date ON TankMaintenance(Next_Maintenance_Date);

-- Indexes for StationOwners table
CREATE INDEX idx_station_owners_station ON StationOwners(Station_ID);
CREATE INDEX idx_station_owners_owner ON StationOwners(Owner_ID);

-- Indexes for EmployeeDebt table
CREATE INDEX idx_employee_debt_employee ON EmployeeDebt(Employee_ID);
CREATE INDEX idx_employee_debt_date ON EmployeeDebt(Settlement_Date);
CREATE INDEX idx_employee_debt_status ON EmployeeDebt(Status);

-- Indexes for EmployeeStationAssignments table
CREATE INDEX idx_employee_assignments_employee ON EmployeeStationAssignments(Employee_ID);
CREATE INDEX idx_employee_assignments_station ON EmployeeStationAssignments(Station_ID);
CREATE INDEX idx_employee_assignments_shift ON EmployeeStationAssignments(Shift_ID);
CREATE INDEX idx_employee_assignments_date ON EmployeeStationAssignments(Assignment_Date);
CREATE INDEX idx_employee_assignments_active ON EmployeeStationAssignments(Is_Active);

-- Indexes for SensorReadings table
CREATE INDEX idx_sensor_readings_tank ON SensorReadings(FuelTank_ID);
CREATE INDEX idx_sensor_readings_pump ON SensorReadings(Pump_ID);
CREATE INDEX idx_sensor_readings_timestamp ON SensorReadings(Timestamp);

-- Indexes for PumpDirectory table
CREATE INDEX idx_pump_directory_pump ON PumpDirectory(Pump_ID);
CREATE INDEX idx_pump_directory_station ON PumpDirectory(Station_ID);
CREATE INDEX idx_pump_directory_employee ON PumpDirectory(Employee_ID);
CREATE INDEX idx_pump_directory_tank ON PumpDirectory(Tank_ID);
CREATE INDEX idx_pump_directory_fuel_type ON PumpDirectory(FuelType_ID);

-- Indexes for AuditLog table
CREATE INDEX idx_audit_log_table ON AuditLog(Table_Name);
CREATE INDEX idx_audit_log_record ON AuditLog(Record_ID);
CREATE INDEX idx_audit_log_date ON AuditLog(Operation_Date);

-- Indexes for Dispensers table
CREATE INDEX idx_dispensers_station ON Dispensers(Station_ID);
CREATE INDEX idx_dispensers_serial ON Dispensers(Serial_Number);

-- Indexes for Nozzles table
CREATE INDEX idx_nozzles_dispenser ON Nozzles(Dispenser_ID);
CREATE INDEX idx_nozzles_fuel_type ON Nozzles(FuelType_ID);

-- Indexes for Flowmeters table
CREATE INDEX idx_flowmeters_station ON Flowmeters(Station_ID);
CREATE INDEX idx_flowmeters_fuel_type ON Flowmeters(FuelType_ID);
CREATE INDEX idx_flowmeters_serial ON Flowmeters(Serial_Number);

-- Indexes for PriceSigns table
CREATE INDEX idx_price_signs_station ON PriceSigns(Station_ID);
CREATE INDEX idx_price_signs_fuel_type ON PriceSigns(FuelType_ID);
CREATE INDEX idx_price_signs_updated ON PriceSigns(Last_Updated);

-- Indexes for PaymentTerminals table
CREATE INDEX idx_payment_terminals_station ON PaymentTerminals(Station_ID);
CREATE INDEX idx_payment_terminals_type ON PaymentTerminals(Type);

-- Indexes for AVI_Vehicles table
CREATE INDEX idx_avi_vehicles_rfid ON AVI_Vehicles(RFID_Tag);
CREATE INDEX idx_avi_vehicles_customer ON AVI_Vehicles(Customer_ID);
CREATE INDEX idx_avi_vehicles_fuel_type ON AVI_Vehicles(FuelType_ID);

-- Indexes for RFID_Readers table
CREATE INDEX idx_rfid_readers_station ON RFID_Readers(Station_ID);
CREATE INDEX idx_rfid_readers_serial ON RFID_Readers(Serial_Number);

-- Indexes for ForecourtControllers table
CREATE INDEX idx_forecourt_controllers_station ON ForecourtControllers(Station_ID);
CREATE INDEX idx_forecourt_controllers_serial ON ForecourtControllers(Serial_Number);

-- Indexes for SystemLogs table
CREATE INDEX idx_system_logs_station ON SystemLogs(Station_ID);
CREATE INDEX idx_system_logs_event ON SystemLogs(Event_Type);
CREATE INDEX idx_system_logs_timestamp ON SystemLogs(Timestamp);
CREATE INDEX idx_system_logs_severity ON SystemLogs(Severity);

-- Indexes for PTS2_Sensors table
CREATE INDEX idx_pts2_sensors_tank ON PTS2_Sensors(Tank_ID);
CREATE INDEX idx_pts2_sensors_station ON PTS2_Sensors(Station_ID);
CREATE INDEX idx_pts2_sensors_serial ON PTS2_Sensors(Serial_Number);
CREATE INDEX idx_pts2_sensors_active ON PTS2_Sensors(Is_Active);

-- Indexes for ATG_Sensors table
CREATE INDEX idx_atg_sensors_tank ON ATG_Sensors(Tank_ID);
CREATE INDEX idx_atg_sensors_station ON ATG_Sensors(Station_ID);
CREATE INDEX idx_atg_sensors_serial ON ATG_Sensors(Serial_Number);
CREATE INDEX idx_atg_sensors_active ON ATG_Sensors(Is_Active);

-- Indexes for PTS2_Readings table
CREATE INDEX idx_pts2_readings_sensor ON PTS2_Readings(PTS2_ID);
CREATE INDEX idx_pts2_readings_tank ON PTS2_Readings(Tank_ID);
CREATE INDEX idx_pts2_readings_station ON PTS2_Readings(Station_ID);
CREATE INDEX idx_pts2_readings_timestamp ON PTS2_Readings(Timestamp);

-- Indexes for ATG_Readings table
CREATE INDEX idx_atg_readings_sensor ON ATG_Readings(ATG_ID);
CREATE INDEX idx_atg_readings_tank ON ATG_Readings(Tank_ID);
CREATE INDEX idx_atg_readings_station ON ATG_Readings(Station_ID);
CREATE INDEX idx_atg_readings_timestamp ON ATG_Readings(Timestamp);

-- Indexes for Sensor_Alarms table
CREATE INDEX idx_sensor_alarms_sensor ON Sensor_Alarms(Sensor_ID);
CREATE INDEX idx_sensor_alarms_sensor_type ON Sensor_Alarms(Sensor_Type);
CREATE INDEX idx_sensor_alarms_tank ON Sensor_Alarms(Tank_ID);
CREATE INDEX idx_sensor_alarms_station ON Sensor_Alarms(Station_ID);
CREATE INDEX idx_sensor_alarms_type ON Sensor_Alarms(Alarm_Type);
CREATE INDEX idx_sensor_alarms_severity ON Sensor_Alarms(Severity);
CREATE INDEX idx_sensor_alarms_timestamp ON Sensor_Alarms(Timestamp);
CREATE INDEX idx_sensor_alarms_acknowledged ON Sensor_Alarms(Acknowledged);
CREATE INDEX idx_sensor_alarms_resolved ON Sensor_Alarms(Resolved);

-- Performance optimization: Analyze table statistics
ANALYZE TABLE PetrolStations, FuelTypes, Employees, FuelTanks, FuelPumps, Customers, Invoices, FuelSupply, PumpMaintenance, TankMaintenance, StationOwners, SystemSettings, EmployeeDebt, EmployeeShifts, EmployeeStationAssignments, SensorReadings, PumpDirectory, AuditLog, Dispensers, Nozzles, Flowmeters, PriceSigns, PaymentTerminals, AVI_Vehicles, RFID_Readers, ForecourtControllers, SystemLogs, PTS2_Sensors, ATG_Sensors, PTS2_Readings, ATG_Readings, Sensor_Alarms;
