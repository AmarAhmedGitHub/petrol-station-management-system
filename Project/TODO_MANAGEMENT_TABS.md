# TODO: Convert Management Interface to Tab Buttons

## Current Status
- Management interface currently uses card grid layout
- Navigation handled via session state and separate functions

## Required Changes
- Replace card grid with tab buttons for the specified list:
  - إدارة المحطات (Station Management)
  - إدارة الموظفين (Employee Management)
  - إدارة التعييئات (Filling Management)
  - إدارة الفواتير (Invoice Management)
  - إدارة التوريد (Supply Management)
  - إدارة الصيانة (Maintenance Management)

## Implementation Steps
- [x] Modify `show_management_interface()` to use `st.tabs()`
- [x] Implement missing management functions for filling, invoice, supply, maintenance
- [x] Update main() function to remove navigation logic
- [x] Test tab functionality and styling

## Files to Edit
- Project/pages/management/main_management.py

## Notes
- Keep existing petrol pump and employee management implementations
- Create similar tab structure (Add, View, Edit, Delete) for new management sections
- Ensure Arabic labels and styling consistency
