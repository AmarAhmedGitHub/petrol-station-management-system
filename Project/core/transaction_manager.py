"""
مدير المعاملات المتقدم - Petrol Pump Management System
يوفر هذا النظام إدارة معاملات قاعدة البيانات للعمليات المعقدة
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from contextlib import contextmanager
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='transaction_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class TransactionManager:
    """مدير المعاملات المتقدم"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def database_transaction(self, connection=None):
        """
        Context manager لإدارة معاملات قاعدة البيانات

        Args:
            connection: اتصال قاعدة البيانات (اختياري)
        """
        conn = connection or get_connection()
        if not conn:
            raise Exception("فشل في الاتصال بقاعدة البيانات")

        try:
            conn.begin()
            yield conn
            conn.commit()
            self.logger.info("تم تأكيد المعاملة بنجاح")
        except Exception as e:
            conn.rollback()
            self.logger.error(f"تم التراجع عن المعاملة: {str(e)}")
            raise
        finally:
            if not connection:  # إغلاق الاتصال فقط إذا تم إنشاؤه هنا
                conn.close()

    def execute_transactional_operation(self, operations: List[Dict[str, Any]],
                                      rollback_operations: Optional[List[Dict[str, Any]]] = None) -> Tuple[bool, str]:
        """
        تنفيذ عمليات متعددة في معاملة واحدة

        Args:
            operations: قائمة العمليات المراد تنفيذها
            rollback_operations: عمليات التراجع (اختيارية)

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        conn = get_connection()
        if not conn:
            return False, "فشل في الاتصال بقاعدة البيانات"

        try:
            with self.database_transaction(conn):
                c = conn.cursor()

                for operation in operations:
                    operation_type = operation.get('type', 'execute')
                    sql = operation.get('sql', '')
                    params = operation.get('params', ())

                    if operation_type == 'execute':
                        c.execute(sql, params)
                    elif operation_type == 'executemany':
                        c.executemany(sql, params)
                    elif operation_type == 'callproc':
                        c.callproc(sql, params)

                    self.logger.debug(f"تم تنفيذ العملية: {operation_type} - {sql[:50]}...")

                return True, "تم تنفيذ جميع العمليات بنجاح"

        except Exception as e:
            # محاولة تنفيذ عمليات التراجع
            if rollback_operations:
                try:
                    with self.database_transaction(conn):
                        c = conn.cursor()
                        for operation in rollback_operations:
                            c.execute(operation['sql'], operation.get('params', ()))
                        self.logger.info("تم تنفيذ عمليات التراجع بنجاح")
                except Exception as rollback_error:
                    self.logger.error(f"فشل في تنفيذ عمليات التراجع: {str(rollback_error)}")

            error_msg = f"فشل في تنفيذ المعاملة: {str(e)}"
            self.logger.error(error_msg)
            return False, error_msg

    def create_invoice_with_inventory_update(self, invoice_data: Dict[str, Any],
                                           employee_id: str) -> Tuple[bool, str]:
        """
        إنشاء فاتورة مع تحديث المخزون في معاملة واحدة

        Args:
            invoice_data: بيانات الفاتورة
            employee_id: معرف الموظف

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        operations = []

        # 1. إضافة الفاتورة
        operations.append({
            'type': 'execute',
            'sql': '''INSERT INTO Invoice
                     (Invoice_No, Date, Payment_Type, Fuel_Amount, Fuel_Type, Discount, Total_Price,
                      Customer_Code, Petrolpump_No, FuelTank_ID, Fuel_Type_Actual, Employee_ID)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            'params': (
                invoice_data['Invoice_No'],
                invoice_data['Date'],
                invoice_data['Payment_Type'],
                invoice_data['Fuel_Amount'],
                invoice_data['Fuel_Type'],
                invoice_data['Discount'],
                invoice_data['Total_Price'],
                invoice_data['Customer_Code'],
                invoice_data.get('Petrolpump_No'),
                invoice_data.get('FuelTank_ID'),
                invoice_data.get('Fuel_Type_Actual'),
                employee_id
            )
        })

        # 2. تحديث المخزون إذا كان هناك خزان محدد
        if invoice_data.get('FuelTank_ID') and invoice_data.get('Fuel_Amount'):
            operations.append({
                'type': 'execute',
                'sql': 'UPDATE FuelTank SET Current_Amount = Current_Amount - %s WHERE FuelTank_ID = %s',
                'params': (invoice_data['Fuel_Amount'], invoice_data['FuelTank_ID'])
            })

            # 3. تسجيل حركة المخزون
            operations.append({
                'type': 'execute',
                'sql': '''INSERT INTO InventoryTransactions
                         (Tank_ID, Transaction_Type, Amount, Employee_ID, Transaction_Date, Notes)
                         VALUES (%s, 'SALE', %s, %s, %s, %s)''',
                'params': (
                    invoice_data['FuelTank_ID'],
                    invoice_data['Fuel_Amount'],
                    employee_id,
                    datetime.now(),
                    f"بيع وقود - فاتورة رقم: {invoice_data['Invoice_No']}"
                )
            })

        # 4. تحديث ديون الموظف إذا كان هناك عمولة
        if invoice_data.get('Employee_Commission'):
            operations.append({
                'type': 'execute',
                'sql': '''INSERT INTO EmployeeDebt
                         (Employee_ID, Settlement_Date, Sold_Quantity, Unit_Price, Owed_Amount, Notes)
                         VALUES (%s, %s, %s, %s, %s, %s)''',
                'params': (
                    employee_id,
                    datetime.now(),
                    invoice_data['Fuel_Amount'],
                    invoice_data.get('Unit_Price', 0),
                    invoice_data['Employee_Commission'],
                    f"عمولة من فاتورة رقم: {invoice_data['Invoice_No']}"
                )
            })

        # عمليات التراجع
        rollback_operations = []
        if invoice_data.get('FuelTank_ID') and invoice_data.get('Fuel_Amount'):
            rollback_operations.append({
                'sql': 'UPDATE FuelTank SET Current_Amount = Current_Amount + %s WHERE FuelTank_ID = %s',
                'params': (invoice_data['Fuel_Amount'], invoice_data['FuelTank_ID'])
            })

        success, message = self.execute_transactional_operation(operations, rollback_operations)

        if success:
            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'Invoice',
                invoice_data['Invoice_No'],
                'INSERT',
                new_values=invoice_data
            )

        return success, message

    def supply_fuel_with_inventory_update(self, supply_data: Dict[str, Any],
                                        supplier_name: str) -> Tuple[bool, str]:
        """
        توريد وقود مع تحديث المخزون في معاملة واحدة

        Args:
            supply_data: بيانات التوريد
            supplier_name: اسم المورد

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        operations = []

        # 1. إضافة سجل التوريد
        operations.append({
            'type': 'execute',
            'sql': '''INSERT INTO FuelSupply
                     (Supply_Invoice_No, Supply_Date, Supplier_Name, Fuel_Type, Quantity,
                      Unit_Price, Total_Amount, FuelTank_ID, Notes)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)''',
            'params': (
                supply_data['Supply_Invoice_No'],
                supply_data['Supply_Date'],
                supplier_name,
                supply_data['Fuel_Type'],
                supply_data['Quantity'],
                supply_data['Unit_Price'],
                supply_data['Total_Amount'],
                supply_data['FuelTank_ID'],
                supply_data.get('Notes', '')
            )
        })

        # 2. تحديث المخزون
        operations.append({
            'type': 'execute',
            'sql': 'UPDATE FuelTank SET Current_Amount = Current_Amount + %s WHERE FuelTank_ID = %s',
            'params': (supply_data['Quantity'], supply_data['FuelTank_ID'])
        })

        # 3. تسجيل حركة المخزون
        operations.append({
            'type': 'execute',
            'sql': '''INSERT INTO InventoryTransactions
                     (Tank_ID, Transaction_Type, Amount, Transaction_Date, Notes)
                     VALUES (%s, 'SUPPLY', %s, %s, %s)''',
            'params': (
                supply_data['FuelTank_ID'],
                supply_data['Quantity'],
                datetime.now(),
                f"توريد وقود من {supplier_name} - فاتورة: {supply_data['Supply_Invoice_No']}"
            )
        })

        # عمليات التراجع
        rollback_operations = [
            {
                'sql': 'UPDATE FuelTank SET Current_Amount = Current_Amount - %s WHERE FuelTank_ID = %s',
                'params': (supply_data['Quantity'], supply_data['FuelTank_ID'])
            }
        ]

        success, message = self.execute_transactional_operation(operations, rollback_operations)

        if success:
            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'FuelSupply',
                supply_data['Supply_Invoice_No'],
                'INSERT',
                new_values=supply_data
            )

        return success, message

    def update_employee_with_permissions(self, employee_data: Dict[str, Any],
                                       permissions: List[str]) -> Tuple[bool, str]:
        """
        تحديث بيانات الموظف مع صلاحياته في معاملة واحدة

        Args:
            employee_data: بيانات الموظف
            permissions: الصلاحيات الجديدة

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        operations = []

        # 1. تحديث بيانات الموظف
        operations.append({
            'type': 'execute',
            'sql': '''UPDATE Employee SET
                     Emp_Name=%s, Emp_Gender=%s, Designation=%s, DOB=%s, Salary=%s,
                     Emp_Address=%s, Email_ID=%s, Petrolpump_No=%s, Manager_ID=%s
                     WHERE Employee_ID=%s''',
            'params': (
                employee_data['Emp_Name'],
                employee_data['Emp_Gender'],
                employee_data['Designation'],
                employee_data['DOB'],
                employee_data['Salary'],
                employee_data['Emp_Address'],
                employee_data['Email_ID'],
                employee_data.get('Petrolpump_No'),
                employee_data.get('Manager_ID'),
                employee_data['Employee_ID']
            )
        })

        # 2. حذف الصلاحيات القديمة
        operations.append({
            'type': 'execute',
            'sql': 'DELETE FROM EmployeePermissions WHERE Employee_ID = %s',
            'params': (employee_data['Employee_ID'],)
        })

        # 3. إضافة الصلاحيات الجديدة
        if permissions:
            permission_params = [(employee_data['Employee_ID'], perm) for perm in permissions]
            operations.append({
                'type': 'executemany',
                'sql': 'INSERT INTO EmployeePermissions (Employee_ID, Permission) VALUES (%s, %s)',
                'params': permission_params
            })

        success, message = self.execute_transactional_operation(operations)

        if success:
            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'Employee',
                employee_data['Employee_ID'],
                'UPDATE',
                new_values={**employee_data, 'permissions': permissions}
            )

        return success, message

    def bulk_update_fuel_prices(self, price_updates: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        تحديث أسعار الوقود بشكل مجمع في معاملة واحدة

        Args:
            price_updates: قائمة تحديثات الأسعار

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        operations = []

        for update in price_updates:
            operations.append({
                'type': 'execute',
                'sql': 'UPDATE Tanker SET Fuel_Price = %s WHERE Fuel_Name = %s',
                'params': (update['new_price'], update['fuel_name'])
            })

        success, message = self.execute_transactional_operation(operations)

        if success:
            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'Tanker',
                'BULK_UPDATE',
                'UPDATE',
                new_values={'price_updates': price_updates}
            )

        return success, message

    def process_employee_debt_settlement(self, debt_ids: List[int],
                                       settlement_date: datetime) -> Tuple[bool, str]:
        """
        تسوية ديون الموظفين في معاملة واحدة

        Args:
            debt_ids: معرفات الديون المراد تسويتها
            settlement_date: تاريخ التسوية

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        operations = []

        # تحديث حالة الديون
        for debt_id in debt_ids:
            operations.append({
                'type': 'execute',
                'sql': 'UPDATE EmployeeDebt SET Status = %s, Settlement_Date = %s WHERE Debt_ID = %s',
                'params': ('Paid', settlement_date, debt_id)
            })

        success, message = self.execute_transactional_operation(operations)

        if success:
            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'EmployeeDebt',
                f'SETTLEMENT_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
                'UPDATE',
                new_values={'settled_debts': debt_ids, 'settlement_date': settlement_date}
            )

        return success, message

# إنشاء instance عالمي
transaction_manager = TransactionManager()

# دوال مساعدة للاستخدام في Streamlit
def create_invoice_transactional(invoice_data: Dict[str, Any], employee_id: str) -> bool:
    """إنشاء فاتورة مع تحديث المخزون بشكل آمن"""
    success, message = transaction_manager.create_invoice_with_inventory_update(invoice_data, employee_id)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success

def supply_fuel_transactional(supply_data: Dict[str, Any], supplier_name: str) -> bool:
    """توريد وقود مع تحديث المخزون بشكل آمن"""
    success, message = transaction_manager.supply_fuel_with_inventory_update(supply_data, supplier_name)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success

def update_employee_transactional(employee_data: Dict[str, Any], permissions: List[str]) -> bool:
    """تحديث بيانات الموظف مع صلاحياته بشكل آمن"""
    success, message = transaction_manager.update_employee_with_permissions(employee_data, permissions)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success

def bulk_update_prices_transactional(price_updates: List[Dict[str, Any]]) -> bool:
    """تحديث أسعار الوقود بشكل مجمع وآمن"""
    success, message = transaction_manager.bulk_update_fuel_prices(price_updates)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success

def settle_employee_debts_transactional(debt_ids: List[int], settlement_date: datetime) -> bool:
    """تسوية ديون الموظفين بشكل آمن"""
    success, message = transaction_manager.process_employee_debt_settlement(debt_ids, settlement_date)
    if success:
        st.success(message)
    else:
        st.error(message)
    return success