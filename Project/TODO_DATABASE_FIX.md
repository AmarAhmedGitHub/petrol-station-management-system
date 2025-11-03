# TODO: Fix Database Creation Error

## Issue
- MySQL error: Can't create table `employees` (errno: 121 "Duplicate key on write or update")
- Occurs when adding foreign key constraint `fk_employees_station` on Employees table
- Error happens during ALTER TABLE in create_enhanced_tables()

## Root Cause
- The foreign key constraint `fk_employees_station` already exists from previous runs
- No cleanup of existing constraints before adding them
- Duplicate Owners table creation in the script

## Tasks
- [ ] Remove duplicate Owners table creation in create_enhanced_tables()
- [ ] Add logic to drop existing `fk_employees_station` constraint before adding it
- [ ] Test database creation after fixes
- [ ] Verify all tables and constraints are created correctly

## Files to Edit
- Project/core/database_enhanced.py

## Followup
- Run the application to ensure no database errors
- Check MySQL database for correct schema
