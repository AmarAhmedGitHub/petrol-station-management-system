"""
نظام التحقق الشامل من صحة البيانات - Petrol Pump Management System
يوفر هذا النظام التحقق من صحة جميع المدخلات والعمليات
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime, date
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='validators.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class DataValidator:
    """مدقق البيانات الشامل"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # أنماط التحقق من البيانات
        self.patterns = {
            'email': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
            'phone': r'^(\+966|0)?[5][0-9]{8}$',  # رقم سعودي
            'registration_no': r'^[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}$',  # نمط تسجيل المركبات
            'employee_id': r'^EMP\d{6}$',  # معرف الموظف
            'customer_code': r'^CUST\d{6}$',  # معرف العميل
            'invoice_no': r'^INV\d{8}$',  # رقم الفاتورة
            'tanker_id': r'^TNK\d{6}$',  # معرف الخزان
            'tank_id': r'^FT\d{3}$',  # معرف خزان الوقود
        }

        # حدود القيم
        self.limits = {
            'fuel_amount': {'min': 0.1, 'max': 1000.0},
            'fuel_price': {'min': 0.1, 'max': 50.0},
            'salary': {'min': 300000, 'max': 1000000},  # الراتب بالريال
            'age': {'min': 18, 'max': 80},
            'capacity': {'min': 1000, 'max': 100000},  # سعة الخزان باللتر
            'discount': {'min': 0, 'max': 50},  # نسبة الخصم
        }

    def validate_required_fields(self, data: Dict[str, Any], required_fields: List[str]) -> Tuple[bool, str]:
        """
        التحقق من وجود الحقول المطلوبة

        Args:
            data: البيانات المراد التحقق منها
            required_fields: قائمة الحقول المطلوبة

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        missing_fields = []
        for field in required_fields:
            if field not in data or data[field] is None or str(data[field]).strip() == '':
                missing_fields.append(field)

        if missing_fields:
            return False, f"الحقول التالية مطلوبة: {', '.join(missing_fields)}"

        return True, "جميع الحقول المطلوبة موجودة"

    def validate_data_types(self, data: Dict[str, Any], field_types: Dict[str, type]) -> Tuple[bool, str]:
        """
        التحقق من أنواع البيانات

        Args:
            data: البيانات المراد التحقق منها
            field_types: أنواع الحقول المتوقعة

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        errors = []
        for field, expected_type in field_types.items():
            if field in data and data[field] is not None:
                try:
                    if expected_type == int:
                        int(data[field])
                    elif expected_type == float:
                        float(data[field])
                    elif expected_type == str:
                        str(data[field])
                    elif expected_type == date:
                        if isinstance(data[field], str):
                            datetime.strptime(data[field], '%Y-%m-%d')
                        elif not isinstance(data[field], date):
                            errors.append(f"حقل {field} يجب أن يكون تاريخ")
                except (ValueError, TypeError):
                    errors.append(f"حقل {field} يجب أن يكون من نوع {expected_type.__name__}")

        if errors:
            return False, " | ".join(errors)

        return True, "أنواع البيانات صحيحة"

    def validate_patterns(self, data: Dict[str, Any], field_patterns: Dict[str, str]) -> Tuple[bool, str]:
        """
        التحقق من أنماط البيانات باستخدام regex

        Args:
            data: البيانات المراد التحقق منها
            field_patterns: أنماط الحقول

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        errors = []
        for field, pattern in field_patterns.items():
            if field in data and data[field]:
                if not re.match(pattern, str(data[field])):
                    errors.append(f"تنسيق حقل {field} غير صحيح")

        if errors:
            return False, " | ".join(errors)

        return True, "تنسيقات البيانات صحيحة"

    def validate_ranges(self, data: Dict[str, Any], field_ranges: Dict[str, Dict[str, float]]) -> Tuple[bool, str]:
        """
        التحقق من نطاقات القيم

        Args:
            data: البيانات المراد التحقق منها
            field_ranges: نطاقات الحقول

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        errors = []
        for field, limits in field_ranges.items():
            if field in data and data[field] is not None:
                try:
                    value = float(data[field])
                    if 'min' in limits and value < limits['min']:
                        errors.append(f"قيمة حقل {field} يجب أن تكون أكبر من أو تساوي {limits['min']}")
                    if 'max' in limits and value > limits['max']:
                        errors.append(f"قيمة حقل {field} يجب أن تكون أصغر من أو تساوي {limits['max']}")
                except (ValueError, TypeError):
                    errors.append(f"حقل {field} يجب أن يكون رقماً")

        if errors:
            return False, " | ".join(errors)

        return True, "نطاقات القيم صحيحة"

    def validate_petrolpump_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من بيانات المحطة"""
        # الحقول المطلوبة
        required = ['Registration_No', 'Petrolpump_Name', 'City']
        is_valid, message = self.validate_required_fields(data, required)
        if not is_valid:
            return False, message

        # أنواع البيانات
        field_types = {
            'Registration_No': str,
            'Petrolpump_Name': str,
            'Company_Name': str,
            'Opening_Year': int,
            'State': str,
            'City': str
        }
        is_valid, message = self.validate_data_types(data, field_types)
        if not is_valid:
            return False, message

        # أنماط البيانات
        field_patterns = {
            'Registration_No': self.patterns['registration_no']
        }
        is_valid, message = self.validate_patterns(data, field_patterns)
        if not is_valid:
            return False, message

        # نطاقات القيم
        field_ranges = {
            'Opening_Year': {'min': 1900, 'max': datetime.now().year + 1}
        }
        is_valid, message = self.validate_ranges(data, field_ranges)
        if not is_valid:
            return False, message

        return True, "بيانات المحطة صحيحة"

    def validate_employee_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من بيانات الموظف"""
        required = ['Employee_ID', 'Emp_Name', 'Emp_Gender', 'Designation', 'Salary', 'Emp_Address']
        is_valid, message = self.validate_required_fields(data, required)
        if not is_valid:
            return False, message

        field_types = {
            'Employee_ID': str,
            'Emp_Name': str,
            'Emp_Gender': str,
            'Designation': str,
            'Salary': float,
            'Emp_Address': str,
            'Email_ID': str
        }
        is_valid, message = self.validate_data_types(data, field_types)
        if not is_valid:
            return False, message

        field_patterns = {
            'Employee_ID': self.patterns['employee_id'],
            'Email_ID': self.patterns['email']
        }
        is_valid, message = self.validate_patterns(data, field_patterns)
        if not is_valid:
            return False, message

        field_ranges = {
            'Salary': self.limits['salary']
        }
        is_valid, message = self.validate_ranges(data, field_ranges)
        if not is_valid:
            return False, message

        # التحقق من صحة الجنس
        if 'Emp_Gender' in data and data['Emp_Gender'] not in ['ذكر', 'أنثى', 'Male', 'Female']:
            return False, "الجنس يجب أن يكون ذكر أو أنثى"

        return True, "بيانات الموظف صحيحة"

    def validate_customer_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من بيانات العميل"""
        required = ['Customer_Code', 'C_Name', 'City']
        is_valid, message = self.validate_required_fields(data, required)
        if not is_valid:
            return False, message

        field_types = {
            'Customer_Code': str,
            'C_Name': str,
            'Phone_No': str,
            'Email_ID': str,
            'Gender': str,
            'City': str,
            'Age': int
        }
        is_valid, message = self.validate_data_types(data, field_types)
        if not is_valid:
            return False, message

        field_patterns = {
            'Customer_Code': self.patterns['customer_code'],
            'Email_ID': self.patterns['email'],
            'Phone_No': self.patterns['phone']
        }
        is_valid, message = self.validate_patterns(data, field_patterns)
        if not is_valid:
            return False, message

        field_ranges = {
            'Age': self.limits['age']
        }
        is_valid, message = self.validate_ranges(data, field_ranges)
        if not is_valid:
            return False, message

        return True, "بيانات العميل صحيحة"

    def validate_invoice_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من بيانات الفاتورة"""
        required = ['Invoice_No', 'Date', 'Payment_Type', 'Fuel_Amount', 'Fuel_Type', 'Total_Price', 'Customer_Code']
        is_valid, message = self.validate_required_fields(data, required)
        if not is_valid:
            return False, message

        field_types = {
            'Invoice_No': str,
            'Date': date,
            'Payment_Type': str,
            'Fuel_Amount': float,
            'Fuel_Type': str,
            'Discount': float,
            'Total_Price': float,
            'Customer_Code': str
        }
        is_valid, message = self.validate_data_types(data, field_types)
        if not is_valid:
            return False, message

        field_patterns = {
            'Invoice_No': self.patterns['invoice_no'],
            'Customer_Code': self.patterns['customer_code']
        }
        is_valid, message = self.validate_patterns(data, field_patterns)
        if not is_valid:
            return False, message

        field_ranges = {
            'Fuel_Amount': self.limits['fuel_amount'],
            'Discount': self.limits['discount'],
            'Total_Price': {'min': 0.1, 'max': 10000.0}
        }
        is_valid, message = self.validate_ranges(data, field_ranges)
        if not is_valid:
            return False, message

        # التحقق من نوع الدفع
        if 'Payment_Type' in data and data['Payment_Type'] not in ['نقدي', 'بطاقة ائتمان', 'تحويل', 'شيك']:
            return False, "نوع الدفع يجب أن يكون نقدي، بطاقة ائتمان، تحويل، أو شيك"

        return True, "بيانات الفاتورة صحيحة"

    def validate_tanker_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من بيانات الخزان"""
        required = ['Tanker_ID', 'Capacity', 'Fuel_Name', 'Fuel_Price', 'Petrolpump_No']
        is_valid, message = self.validate_required_fields(data, required)
        if not is_valid:
            return False, message

        field_types = {
            'Tanker_ID': str,
            'Capacity': float,
            'pressure': float,
            'Fuel_ID': str,
            'Fuel_Amount': float,
            'Fuel_Name': str,
            'Fuel_Price': float,
            'Petrolpump_No': str
        }
        is_valid, message = self.validate_data_types(data, field_types)
        if not is_valid:
            return False, message

        field_patterns = {
            'Tanker_ID': self.patterns['tanker_id']
        }
        is_valid, message = self.validate_patterns(data, field_patterns)
        if not is_valid:
            return False, message

        field_ranges = {
            'Capacity': self.limits['capacity'],
            'Fuel_Price': self.limits['fuel_price'],
            'Fuel_Amount': {'min': 0, 'max': self.limits['capacity']['max']}
        }
        is_valid, message = self.validate_ranges(data, field_ranges)
        if not is_valid:
            return False, message

        return True, "بيانات الخزان صحيحة"

    def validate_fuel_tank_data(self, data: Dict[str, Any]) -> Tuple[bool, str]:
        """التحقق من بيانات خزان الوقود"""
        required = ['FuelTank_ID', 'Fuel_Type', 'Capacity']
        is_valid, message = self.validate_required_fields(data, required)
        if not is_valid:
            return False, message

        field_types = {
            'FuelTank_ID': str,
            'Fuel_Type': str,
            'Capacity': float,
            'Current_Amount': float
        }
        is_valid, message = self.validate_data_types(data, field_types)
        if not is_valid:
            return False, message

        field_patterns = {
            'FuelTank_ID': self.patterns['tank_id']
        }
        is_valid, message = self.validate_patterns(data, field_patterns)
        if not is_valid:
            return False, message

        field_ranges = {
            'Capacity': self.limits['capacity'],
            'Current_Amount': {'min': 0, 'max': self.limits['capacity']['max']}
        }
        is_valid, message = self.validate_ranges(data, field_ranges)
        if not is_valid:
            return False, message

        # التحقق من أن الكمية الحالية لا تتجاوز السعة
        if 'Current_Amount' in data and 'Capacity' in data:
            if data['Current_Amount'] > data['Capacity']:
                return False, "الكمية الحالية لا يمكن أن تتجاوز سعة الخزان"

        return True, "بيانات خزان الوقود صحيحة"

    def validate_business_logic(self, table_name: str, data: Dict[str, Any], operation: str = 'INSERT') -> Tuple[bool, str]:
        """
        التحقق من منطق العمل

        Args:
            table_name: اسم الجدول
            data: البيانات
            operation: نوع العملية (INSERT, UPDATE, DELETE)

        Returns:
            Tuple[bool, str]: (صحيح/خطأ, رسالة)
        """
        try:
            conn = get_connection()
            if not conn:
                return False, "فشل في الاتصال بقاعدة البيانات"

            c = conn.cursor()

            if table_name == 'Employee' and operation == 'INSERT':
                # التحقق من عدم وجود موظف بنفس المعرف
                if 'Employee_ID' in data:
                    c.execute("SELECT COUNT(*) FROM Employee WHERE Employee_ID = %s", (data['Employee_ID'],))
                    if c.fetchone()[0] > 0:
                        conn.close()
                        return False, f"موظف بمعرف {data['Employee_ID']} موجود مسبقاً"

                # التحقق من صحة محطة العمل
                if 'Petrolpump_No' in data:
                    c.execute("SELECT COUNT(*) FROM Petrolpump WHERE Registration_No = %s", (data['Petrolpump_No'],))
                    if c.fetchone()[0] == 0:
                        conn.close()
                        return False, f"محطة {data['Petrolpump_No']} غير موجودة"

            elif table_name == 'Invoice' and operation == 'INSERT':
                # التحقق من وجود العميل
                if 'Customer_Code' in data:
                    c.execute("SELECT COUNT(*) FROM Customer WHERE Customer_Code = %s", (data['Customer_Code'],))
                    if c.fetchone()[0] == 0:
                        conn.close()
                        return False, f"عميل {data['Customer_Code']} غير موجود"

                # التحقق من صحة الخزان إذا تم تحديده
                if 'FuelTank_ID' in data and data['FuelTank_ID']:
                    c.execute("SELECT COUNT(*) FROM FuelTank WHERE FuelTank_ID = %s", (data['FuelTank_ID'],))
                    if c.fetchone()[0] == 0:
                        conn.close()
                        return False, f"خزان {data['FuelTank_ID']} غير موجود"

            elif table_name == 'Tanker' and operation == 'INSERT':
                # التحقق من صحة المحطة
                if 'Petrolpump_No' in data:
                    c.execute("SELECT COUNT(*) FROM Petrolpump WHERE Registration_No = %s", (data['Petrolpump_No'],))
                    if c.fetchone()[0] == 0:
                        conn.close()
                        return False, f"محطة {data['Petrolpump_No']} غير موجودة"

            conn.close()
            return True, "منطق العمل صحيح"

        except Exception as e:
            self.logger.error(f"خطأ في التحقق من منطق العمل: {str(e)}")
            return False, f"خطأ في النظام: {str(e)}"

# إنشاء instance عالمي
data_validator = DataValidator()

# دوال مساعدة للاستخدام في Streamlit
def validate_and_show_errors(data: Dict[str, Any], validator_func) -> bool:
    """دالة مساعدة للتحقق وعرض الأخطاء في Streamlit"""
    is_valid, message = validator_func(data)
    if not is_valid:
        st.error(message)
    else:
        st.success(message)
    return is_valid

def validate_petrolpump_form(data: Dict[str, Any]) -> bool:
    """التحقق من نموذج المحطة"""
    return validate_and_show_errors(data, data_validator.validate_petrolpump_data)

def validate_employee_form(data: Dict[str, Any]) -> bool:
    """التحقق من نموذج الموظف"""
    return validate_and_show_errors(data, data_validator.validate_employee_data)

def validate_customer_form(data: Dict[str, Any]) -> bool:
    """التحقق من نموذج العميل"""
    return validate_and_show_errors(data, data_validator.validate_customer_data)

def validate_invoice_form(data: Dict[str, Any]) -> bool:
    """التحقق من نموذج الفاتورة"""
    return validate_and_show_errors(data, data_validator.validate_invoice_data)

def validate_tanker_form(data: Dict[str, Any]) -> bool:
    """التحقق من نموذج الخزان"""
    return validate_and_show_errors(data, data_validator.validate_tanker_data)

def validate_fuel_tank_form(data: Dict[str, Any]) -> bool:
    """التحقق من نموذج خزان الوقود"""
    return validate_and_show_errors(data, data_validator.validate_fuel_tank_data)