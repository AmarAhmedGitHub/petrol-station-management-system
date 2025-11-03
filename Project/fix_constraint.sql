-- Fix the Manager_ID foreign key constraint in PetrolStations table
-- This script makes Manager_ID nullable to allow adding stations without managers

USE Petrolpump_Management_Enhanced;

-- Drop existing constraints (try multiple names)
SET FOREIGN_KEY_CHECKS = 0;

ALTER TABLE PetrolStations DROP FOREIGN KEY petrolstations_ibfk_1;
ALTER TABLE PetrolStations DROP FOREIGN KEY fk_petrolstations_manager;
ALTER TABLE PetrolStations DROP FOREIGN KEY fk_petrolstations_manager_new;
ALTER TABLE PetrolStations DROP FOREIGN KEY fk_petrolstations_manager_fixed;

SET FOREIGN_KEY_CHECKS = 1;

-- Modify the Manager_ID column to allow NULL values
ALTER TABLE PetrolStations MODIFY COLUMN Manager_ID VARCHAR(10) NULL;

-- Add the foreign key constraint back (allowing NULL)
ALTER TABLE PetrolStations
ADD CONSTRAINT fk_petrolstations_manager_final
FOREIGN KEY (Manager_ID) REFERENCES Employees(Employee_ID);

SELECT 'Manager_ID constraint fixed successfully!' as Result;
