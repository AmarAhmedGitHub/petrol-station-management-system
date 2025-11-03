import streamlit as st
from database import *


def create_for_Petrolpump():
    with st.container():
        Registration_No = st.text_input("Registration_No:")
        Petrolpump_Name = st.text_input("Petrolpump_Name:")
        Company_Name = st.text_input("Company_Name:")
        Opening_Year = st.number_input("Opening_Year:")
        State = st.text_input("State:")
        City = st.text_input("City:")
    
    if st.button("Add Petrolpump Details"):
        add_Petrolpump_data(Registration_No,Petrolpump_Name,Company_Name,Opening_Year,State,City)
        st.success("Successfully added Petrolpump details: {}".format(Registration_No))


def create_for_Owners():
    with st.container():
        Owner_Name = st.text_input("Owner_Name:")
        Contact_NO = st.text_input("Contact_NO:")
        DOB = st.date_input("DOB:")
        Gender = st.text_input("Gender:")
        Address = st.text_input("Enter Address")
        Partnership = st.number_input("Your Partership")
        
    if st.button("Add Owners Details"):
        add_Owners_data(Owner_Name, Contact_NO, DOB, Gender, Address, Partnership)
        st.success("Successfully added Owners details: {}".format(Owner_Name))


def create_for_Employee():
    with st.container():
        Employee_ID = st.text_input("Employee_ID")
        Emp_Name = st.text_input("Emp_Name:")
        Emp_Gender = st.text_input("Emp_Gender:")
        Designation = st.text_input(" Designation:")
        DOB= st.date_input("DOB:")
        Salary = st.number_input("Salary:")
        Emp_Address=st.text_input("Emp_Address:")
        Email_ID=st.text_input("Email_ID:")
        Petrolpump_No=st.text_input("Petrolpump_No:")
        Manager_ID=st.text_input("Manager_ID:")

    if st.button("Add Employee Details"):
        add_Employee_data(Employee_ID, Emp_Name,  Emp_Gender,   Designation,  DOB, Salary,  Emp_Address, Email_ID , Petrolpump_No, Manager_ID)
        st.success("Successfully added Employee details: {}".format(Employee_ID))


def create_for_Customer():
    with st.container():
        Customer_Code = st.text_input("Customer_Code")
        C_Name = st.text_input("C_Name:")
        Phone_No = st.text_input("Phone_No:")
        Email_ID=st.text_input("Email_ID")
        Gender = st.text_input("Gender:")
        City = st.text_input("City:")
        Age = st.number_input("Age")
    
    if st.button("Add Customer Details"):
        add_Customer_data(Customer_Code , C_Name , Phone_No  , Email_ID , Gender,  City , Age)
        st.success("Successfully added Customer details: {}".format(Customer_Code))



def create_for_Invoice():
    import streamlit as st
    import database
    with st.container():
        Invoice_No = st.text_input("Invoice_No:")
        Date = st.date_input("Date:")
        Payment_Type = st.text_input("Payment_Type:")
        Fuel_Amount = st.number_input("Fuel_Amount:")
        Fuel_Type = st.text_input("Fuel_Type:")
        Discount = st.number_input("Discount:")
        Total_Price = st.number_input("Total_Price:")
        Customer_Code = st.text_input("Customer_Code:")


        # ربط الفاتورة بالطرمبة وخزان الوقود والموظف من دليل الطرمبة
        pump_no = None
        pump_name = None
        tank_id = None
        fuel_type = None
        emp_id = None
        if "user_type" in st.session_state and st.session_state.user_type == "Employee":
            emp_name = st.session_state.username
            # جلب رقم الموظف
            database.c.execute("SELECT Employee_ID FROM Employee WHERE Emp_Name=%s", (emp_name,))
            emp_result = database.c.fetchone()
            if emp_result and emp_result[0]:
                emp_id = emp_result[0]
                # جلب الربط من PumpDirectory
                database.c.execute("SELECT Petrolpump_No, FuelTank_ID FROM PumpDirectory WHERE Employee_ID=%s", (emp_id,))
                pd_result = database.c.fetchone()
                if pd_result:
                    pump_no = pd_result[0]
                    tank_id = pd_result[1]
                    # جلب اسم الطرمبة
                    database.c.execute("SELECT Pump_Name FROM FuelPumps WHERE Pump_ID=%s", (pump_no,))
                    pump_info = database.c.fetchone()
                    if pump_info:
                        pump_name = pump_info[0]
                    # جلب نوع البترول من الخزان
                    if tank_id:
                        database.c.execute("SELECT FuelType_ID FROM FuelTanks WHERE Tank_ID=%s", (tank_id,))
                        fuel_info = database.c.fetchone()
                        if fuel_info:
                            fuel_type = fuel_info[0]
            st.info(f"سيتم ربط الفاتورة تلقائياً بالطرمبة رقم: {pump_no} ({pump_name}) وخزان الوقود: {tank_id} ونوع البترول: {fuel_type}")
        else:
            pump_no = st.text_input("رقم الطرمبة (اختياري)")
            tank_id = st.text_input("رقم خزان الوقود (اختياري)")
            fuel_type = st.text_input("نوع البترول (اختياري)")

    if st.button("Add Invoice Details"):
        # تمرير رقم الطرمبة، رقم الخزان، ونوع البترول الفعلي إذا كان الموظف
        if "user_type" in st.session_state and st.session_state.user_type == "Employee":
            add_Invoice_data(Invoice_No, Date, Payment_Type, Fuel_Amount, Fuel_Type, Discount, Total_Price, Customer_Code, pump_no, tank_id, fuel_type)
            st.success(f"Successfully added Invoice details: {Invoice_No} (Pump: {pump_no}, Tank: {tank_id}, Fuel: {fuel_type})")
        else:
            add_Invoice_data(Invoice_No, Date, Payment_Type, Fuel_Amount, Fuel_Type, Discount, Total_Price, Customer_Code, pump_no, tank_id, fuel_type)
            st.success(f"Successfully added Invoice details: {Invoice_No} (Pump: {pump_no}, Tank: {tank_id}, Fuel: {fuel_type})")

def create_for_Tanker():
    with st.container():
        Tanker_ID = st.text_input("Tanker_ID:")
        Capacity = st.number_input("Capacity:")
        pressure = st.number_input("pressure:")
        Fuel_ID = st.text_input("Fuel_ID")
        Fuel_Amount = st.number_input("Fuel_Amount")
        Fuel_Name= st.text_input("Fuel_Name:")
        Fuel_Price= st.number_input("Fuel_Price:")
        Petrolpump_No=st.text_input("Petrolpump_No:")

    if st.button("Add Tanker Details"):
        add_Tanker_data(Tanker_ID  , Capacity,  pressure,  Fuel_ID , Fuel_Amount, Fuel_Name , Fuel_Price , Petrolpump_No)
        st.success("Successfully added Tanker details: {}".format(Tanker_ID))