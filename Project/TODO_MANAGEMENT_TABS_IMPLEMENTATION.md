# TODO: Implement Management Interface Tab Conversion

## Current Status
- Management interface uses card grid with session state navigation
- Separate files exist for maintenance, invoices, and supply management with full CRUD
- Need to integrate all management functions into main_management.py with tab interface

## Implementation Steps
- [ ] Modify `show_management_interface()` to use `st.tabs()` with 6 tabs: إدارة المحطات, إدارة الموظفين, إدارة التعييئات, إدارة الفواتير, إدارة التوريد, إدارة الصيانة
- [ ] Integrate `show_filling_management()` from main_management_supply.py (using FuelSupply table)
- [ ] Integrate `show_invoice_management()` from main_management_invoices.py (using Invoices table)
- [ ] Integrate `show_supply_management()` from main_management_supply.py (using FuelSupply table)
- [ ] Integrate `show_maintenance_management()` from main_management_maintenance.py (using PumpMaintenance and TankMaintenance tables)
- [ ] Update `main()` function to remove session state navigation logic
- [ ] Test tab functionality and styling
- [ ] Ensure Arabic labels and styling consistency

## Files to Edit
- Project/pages/management/main_management.py (main changes)

## Notes
- Keep existing petrol pump and employee management implementations
- Each management function should have Add/View/Edit/Delete tabs structure
- Use existing database functions from database_enhanced.py
- Maintain consistent Arabic UI and styling
