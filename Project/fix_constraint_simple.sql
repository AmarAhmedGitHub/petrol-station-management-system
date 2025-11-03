-- Simple fix for Manager_ID column to allow NULL values
-- This resolves the foreign key constraint error when adding stations without managers

USE Petrolpump_Management_Enhanced;

-- Modify the Manager_ID column to allow NULL values
ALTER TABLE PetrolStations MODIFY COLUMN Manager_ID VARCHAR(10) NULL;

SELECT 'Manager_ID column updated to allow NULL values successfully!' as Result;
