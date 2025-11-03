"""
نظام محاسبي متكامل لإدارة محطات الوقود
Accounting System for Petrol Pump Management
"""

import pymysql
import streamlit as st
import logging
from datetime import datetime, date
from decimal import Decimal
from contextlib import contextmanager

logger = logging.getLogger(__name__)

# Database configuration
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "Petrolpump_Management_Enhanced",
    "charset": "utf8mb4"
}

@contextmanager
def get_db_connection():
    """Database connection context manager"""
    conn = None
    try:
        conn = pymysql.connect(**DB_CONFIG)
        yield conn
    except pymysql.Error as err:
        logger.error(f"Database connection error: {err}")
        raise
    finally:
        if conn:
            conn.close()

def create_accounting_tables():
    """Create accounting system tables"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # 1. دليل الحسابات (Chart of Accounts)
            c.execute('''CREATE TABLE IF NOT EXISTS ChartOfAccounts (
                Account_ID VARCHAR(20) PRIMARY KEY,
                Account_Name VARCHAR(100) NOT NULL,
                Account_Type ENUM('Asset', 'Liability', 'Equity', 'Revenue', 'Expense', 'CostOfSales') NOT NULL,
                Account_Category VARCHAR(50),
                Parent_Account_ID VARCHAR(20),
                Is_Active BOOLEAN DEFAULT TRUE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Parent_Account_ID) REFERENCES ChartOfAccounts(Account_ID)
            )''')

            # 2. القيود اليومية (Journal Entries)
            c.execute('''CREATE TABLE IF NOT EXISTS JournalEntries (
                Entry_ID INT AUTO_INCREMENT PRIMARY KEY,
                Entry_Number VARCHAR(20) UNIQUE NOT NULL,
                Entry_Date DATE NOT NULL,
                Description TEXT,
                Reference_Type ENUM('Invoice', 'Receipt', 'Payment', 'Adjustment', 'Opening') DEFAULT 'Adjustment',
                Reference_Number VARCHAR(50),
                Total_Debit DECIMAL(15,2) DEFAULT 0,
                Total_Credit DECIMAL(15,2) DEFAULT 0,
                Status ENUM('Draft', 'Posted', 'Voided') DEFAULT 'Draft',
                Posted_By VARCHAR(10),
                Posted_Date TIMESTAMP NULL,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # 3. تفاصيل القيود (Journal Entry Details)
            c.execute('''CREATE TABLE IF NOT EXISTS JournalEntryDetails (
                Detail_ID INT AUTO_INCREMENT PRIMARY KEY,
                Entry_ID INT NOT NULL,
                Account_ID VARCHAR(20) NOT NULL,
                Description TEXT,
                Debit DECIMAL(15,2) DEFAULT 0,
                Credit DECIMAL(15,2) DEFAULT 0,
                Reference VARCHAR(100),
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Entry_ID) REFERENCES JournalEntries(Entry_ID) ON DELETE CASCADE,
                FOREIGN KEY(Account_ID) REFERENCES ChartOfAccounts(Account_ID)
            )''')

            # 4. سندات القبض (Receipt Vouchers)
            c.execute('''CREATE TABLE IF NOT EXISTS ReceiptVouchers (
                Receipt_ID VARCHAR(20) PRIMARY KEY,
                Receipt_Number VARCHAR(20) UNIQUE NOT NULL,
                Receipt_Date DATE NOT NULL,
                Customer_ID VARCHAR(10),
                Customer_Name VARCHAR(100),
                Amount DECIMAL(15,2) NOT NULL,
                Payment_Method ENUM('Cash', 'Bank', 'Cheque', 'Card') DEFAULT 'Cash',
                Cheque_Number VARCHAR(50),
                Bank_Name VARCHAR(100),
                Reference_Number VARCHAR(50),
                Description TEXT,
                Received_By VARCHAR(10),
                Entry_ID INT,
                Status ENUM('Draft', 'Posted', 'Cancelled') DEFAULT 'Draft',
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Customer_ID) REFERENCES Customers(Customer_Code),
                FOREIGN KEY(Entry_ID) REFERENCES JournalEntries(Entry_ID)
            )''')

            # 5. سندات الصرف (Payment Vouchers)
            c.execute('''CREATE TABLE IF NOT EXISTS PaymentVouchers (
                Payment_ID VARCHAR(20) PRIMARY KEY,
                Payment_Number VARCHAR(20) UNIQUE NOT NULL,
                Payment_Date DATE NOT NULL,
                Vendor_ID VARCHAR(10),
                Vendor_Name VARCHAR(100),
                Amount DECIMAL(15,2) NOT NULL,
                Payment_Method ENUM('Cash', 'Bank', 'Cheque', 'Card') DEFAULT 'Cash',
                Cheque_Number VARCHAR(50),
                Bank_Name VARCHAR(100),
                Reference_Number VARCHAR(50),
                Description TEXT,
                Paid_By VARCHAR(10),
                Entry_ID INT,
                Status ENUM('Draft', 'Posted', 'Cancelled') DEFAULT 'Draft',
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Entry_ID) REFERENCES JournalEntries(Entry_ID)
            )''')

            # 6. إعدادات الضرائب (Tax Settings)
            c.execute('''CREATE TABLE IF NOT EXISTS TaxSettings (
                Tax_ID VARCHAR(10) PRIMARY KEY,
                Tax_Name VARCHAR(50) NOT NULL,
                Tax_Type ENUM('VAT', 'SalesTax', 'ServiceTax', 'Withholding') NOT NULL,
                Tax_Rate DECIMAL(5,2) NOT NULL,
                Is_Active BOOLEAN DEFAULT TRUE,
                Effective_From DATE NOT NULL,
                Effective_To DATE,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )''')

            # 7. تفاصيل الضرائب للفواتير (Invoice Tax Details)
            c.execute('''CREATE TABLE IF NOT EXISTS InvoiceTaxDetails (
                Tax_Detail_ID INT AUTO_INCREMENT PRIMARY KEY,
                Invoice_No VARCHAR(15) NOT NULL,
                Tax_ID VARCHAR(10) NOT NULL,
                Taxable_Amount DECIMAL(15,2) NOT NULL,
                Tax_Amount DECIMAL(15,2) NOT NULL,
                Created_Date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(Invoice_No) REFERENCES Invoices(Invoice_No),
                FOREIGN KEY(Tax_ID) REFERENCES TaxSettings(Tax_ID)
            )''')

            # Insert default chart of accounts
            default_accounts = [
                ('1000', 'النقدية', 'Asset', 'Current Assets'),
                ('1100', 'البنك', 'Asset', 'Current Assets'),
                ('1200', 'المدينون', 'Asset', 'Current Assets'),
                ('1300', 'المخزون', 'Asset', 'Current Assets'),
                ('2000', 'الدائنون', 'Liability', 'Current Liabilities'),
                ('2100', 'الضرائب المستحقة', 'Liability', 'Current Liabilities'),
                ('3000', 'رأس المال', 'Equity', 'Equity'),
                ('3100', 'الأرباح المحتجزة', 'Equity', 'Equity'),
                ('4000', 'إيرادات المبيعات', 'Revenue', 'Revenue'),
                ('4100', 'إيرادات أخرى', 'Revenue', 'Revenue'),
                ('5000', 'تكلفة المبيعات', 'CostOfSales', 'Cost of Sales'),
                ('6000', 'المصروفات التشغيلية', 'Expense', 'Operating Expenses'),
                ('6100', 'الرواتب والأجور', 'Expense', 'Operating Expenses'),
                ('6200', 'الإيجارات', 'Expense', 'Operating Expenses'),
                ('6300', 'الصيانة', 'Expense', 'Operating Expenses'),
                ('6400', 'الضرائب', 'Expense', 'Operating Expenses')
            ]

            for account in default_accounts:
                c.execute('''INSERT IGNORE INTO ChartOfAccounts
                           (Account_ID, Account_Name, Account_Type, Account_Category)
                           VALUES (%s, %s, %s, %s)''', account)

            # Insert default tax settings
            default_taxes = [
                ('VAT', 'ضريبة القيمة المضافة', 'VAT', 15.00, '2024-01-01'),
                ('SALESTAX', 'ضريبة المبيعات', 'SalesTax', 10.00, '2024-01-01')
            ]

            for tax in default_taxes:
                c.execute('''INSERT IGNORE INTO TaxSettings
                           (Tax_ID, Tax_Name, Tax_Type, Tax_Rate, Effective_From)
                           VALUES (%s, %s, %s, %s, %s)''', tax)

            conn.commit()
            logger.info("Accounting system tables created successfully")

    except Exception as e:
        logger.error(f"Error creating accounting tables: {e}")
        st.error(f"خطأ في إنشاء جداول النظام المحاسبي: {e}")
        raise

# Chart of Accounts Functions
def get_chart_of_accounts():
    """Get all active accounts"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM ChartOfAccounts WHERE Is_Active = TRUE ORDER BY Account_ID')
            return c.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving chart of accounts: {e}")
        return []

def add_account(Account_ID, Account_Name, Account_Type, Account_Category, Parent_Account_ID=None):
    """Add new account to chart of accounts"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''INSERT INTO ChartOfAccounts
                       (Account_ID, Account_Name, Account_Type, Account_Category, Parent_Account_ID)
                       VALUES (%s, %s, %s, %s, %s)''',
                     (Account_ID, Account_Name, Account_Type, Account_Category, Parent_Account_ID))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error adding account: {e}")
        return False

# Journal Entries Functions
def create_journal_entry(entry_number, entry_date, description, details, reference_type='Adjustment', reference_number=None):
    """Create a new journal entry with details"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Calculate totals
            total_debit = sum(Decimal(str(d.get('debit', 0))) for d in details)
            total_credit = sum(Decimal(str(d.get('credit', 0))) for d in details)

            if total_debit != total_credit:
                raise ValueError("Debit and Credit totals must be equal")

            # Insert journal entry
            c.execute('''INSERT INTO JournalEntries
                       (Entry_Number, Entry_Date, Description, Reference_Type, Reference_Number, Total_Debit, Total_Credit)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)''',
                     (entry_number, entry_date, description, reference_type, reference_number, total_debit, total_credit))

            entry_id = c.lastrowid

            # Insert journal entry details
            for detail in details:
                c.execute('''INSERT INTO JournalEntryDetails
                           (Entry_ID, Account_ID, Description, Debit, Credit, Reference)
                           VALUES (%s, %s, %s, %s, %s, %s)''',
                         (entry_id, detail['account_id'], detail.get('description', ''),
                          detail.get('debit', 0), detail.get('credit', 0), detail.get('reference', '')))

            conn.commit()
            return entry_id

    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        return False

def get_journal_entries(limit=100):
    """Get journal entries with details"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT je.*, jed.Detail_ID, jed.Account_ID, coa.Account_Name,
                               jed.Description as Detail_Description, jed.Debit, jed.Credit, jed.Reference
                        FROM JournalEntries je
                        LEFT JOIN JournalEntryDetails jed ON je.Entry_ID = jed.Entry_ID
                        LEFT JOIN ChartOfAccounts coa ON jed.Account_ID = coa.Account_ID
                        ORDER BY je.Entry_Date DESC, je.Entry_ID DESC
                        LIMIT %s''', (limit,))
            return c.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving journal entries: {e}")
        return []

def post_journal_entry(entry_id, posted_by):
    """Post a journal entry"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''UPDATE JournalEntries
                       SET Status = 'Posted', Posted_By = %s, Posted_Date = NOW()
                       WHERE Entry_ID = %s''', (posted_by, entry_id))
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error posting journal entry: {e}")
        return False

# Receipt Voucher Functions
def create_receipt_voucher(receipt_data):
    """Create a receipt voucher with journal entry"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Generate receipt number
            c.execute("SELECT MAX(CAST(SUBSTRING(Receipt_Number, 4) AS UNSIGNED)) FROM ReceiptVouchers")
            max_num = c.fetchone()[0] or 0
            receipt_number = f"REC{str(max_num + 1).zfill(6)}"

            # Insert receipt voucher
            c.execute('''INSERT INTO ReceiptVouchers
                       (Receipt_ID, Receipt_Number, Receipt_Date, Customer_ID, Customer_Name,
                        Amount, Payment_Method, Cheque_Number, Bank_Name, Reference_Number,
                        Description, Received_By)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                     (receipt_data['receipt_id'], receipt_number, receipt_data['receipt_date'],
                      receipt_data.get('customer_id'), receipt_data.get('customer_name'),
                      receipt_data['amount'], receipt_data.get('payment_method', 'Cash'),
                      receipt_data.get('cheque_number'), receipt_data.get('bank_name'),
                      receipt_data.get('reference_number'), receipt_data.get('description'),
                      receipt_data.get('received_by')))

            # Create journal entry
            entry_number = f"JE{str(max_num + 1).zfill(6)}"
            description = f"Receipt Voucher: {receipt_number} - {receipt_data.get('description', '')}"

            # Journal entry details
            details = [
                {
                    'account_id': '1000',  # Cash/Bank
                    'description': description,
                    'debit': receipt_data['amount'],
                    'reference': receipt_number
                },
                {
                    'account_id': '1200',  # Accounts Receivable
                    'description': description,
                    'credit': receipt_data['amount'],
                    'reference': receipt_number
                }
            ]

            entry_id = create_journal_entry(entry_number, receipt_data['receipt_date'],
                                          description, details, 'Receipt', receipt_number)

            # Update receipt with entry ID
            c.execute('UPDATE ReceiptVouchers SET Entry_ID = %s WHERE Receipt_ID = %s',
                     (entry_id, receipt_data['receipt_id']))

            conn.commit()
            return receipt_number

    except Exception as e:
        logger.error(f"Error creating receipt voucher: {e}")
        return False

def get_receipt_vouchers(limit=100):
    """Get receipt vouchers"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT rv.*, c.C_Name as Customer_Name_DB
                        FROM ReceiptVouchers rv
                        LEFT JOIN Customers c ON rv.Customer_ID = c.Customer_Code
                        ORDER BY rv.Receipt_Date DESC
                        LIMIT %s''', (limit,))
            return c.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving receipt vouchers: {e}")
        return []

# Payment Voucher Functions
def create_payment_voucher(payment_data):
    """Create a payment voucher with journal entry"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Generate payment number
            c.execute("SELECT MAX(CAST(SUBSTRING(Payment_Number, 4) AS UNSIGNED)) FROM PaymentVouchers")
            max_num = c.fetchone()[0] or 0
            payment_number = f"PAY{str(max_num + 1).zfill(6)}"

            # Insert payment voucher
            c.execute('''INSERT INTO PaymentVouchers
                       (Payment_ID, Payment_Number, Payment_Date, Vendor_ID, Vendor_Name,
                        Amount, Payment_Method, Cheque_Number, Bank_Name, Reference_Number,
                        Description, Paid_By)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                     (payment_data['payment_id'], payment_number, payment_data['payment_date'],
                      payment_data.get('vendor_id'), payment_data.get('vendor_name'),
                      payment_data['amount'], payment_data.get('payment_method', 'Cash'),
                      payment_data.get('cheque_number'), payment_data.get('bank_name'),
                      payment_data.get('reference_number'), payment_data.get('description'),
                      payment_data.get('paid_by')))

            # Create journal entry
            entry_number = f"JE{str(max_num + 1).zfill(6)}"
            description = f"Payment Voucher: {payment_number} - {payment_data.get('description', '')}"

            # Journal entry details
            details = [
                {
                    'account_id': '6000',  # Expenses
                    'description': description,
                    'debit': payment_data['amount'],
                    'reference': payment_number
                },
                {
                    'account_id': '1000',  # Cash/Bank
                    'description': description,
                    'credit': payment_data['amount'],
                    'reference': payment_number
                }
            ]

            entry_id = create_journal_entry(entry_number, payment_data['payment_date'],
                                          description, details, 'Payment', payment_number)

            # Update payment with entry ID
            c.execute('UPDATE PaymentVouchers SET Entry_ID = %s WHERE Payment_ID = %s',
                     (entry_id, payment_data['payment_id']))

            conn.commit()
            return payment_number

    except Exception as e:
        logger.error(f"Error creating payment voucher: {e}")
        return False

def get_payment_vouchers(limit=100):
    """Get payment vouchers"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT * FROM PaymentVouchers ORDER BY Payment_Date DESC LIMIT %s', (limit,))
            return c.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving payment vouchers: {e}")
        return []

# Tax Functions
def get_active_taxes():
    """Get active tax settings"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('''SELECT * FROM TaxSettings
                        WHERE Is_Active = TRUE
                        AND Effective_From <= CURDATE()
                        AND (Effective_To IS NULL OR Effective_To >= CURDATE())
                        ORDER BY Tax_Type, Tax_Rate DESC''')
            return c.fetchall()
    except Exception as e:
        logger.error(f"Error retrieving tax settings: {e}")
        return []

def calculate_tax(amount, tax_id):
    """Calculate tax amount"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()
            c.execute('SELECT Tax_Rate FROM TaxSettings WHERE Tax_ID = %s AND Is_Active = TRUE', (tax_id,))
            result = c.fetchone()
            if result:
                tax_rate = Decimal(str(result[0]))
                return (amount * tax_rate) / 100
            return Decimal('0')
    except Exception as e:
        logger.error(f"Error calculating tax: {e}")
        return Decimal('0')

# Enhanced Invoice Functions with Tax
def create_invoice_with_tax(invoice_data, tax_details=None):
    """Create invoice with tax calculations and journal entries"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Calculate taxes
            taxable_amount = Decimal(str(invoice_data['fuel_amount_liters'])) * Decimal(str(invoice_data['unit_price']))
            total_tax = Decimal('0')

            if tax_details:
                for tax in tax_details:
                    tax_amount = calculate_tax(taxable_amount, tax['tax_id'])
                    total_tax += tax_amount

            total_amount = taxable_amount + total_tax

            # Insert invoice
            c.execute('''INSERT INTO Invoices
                       (Invoice_No, Station_ID, Pump_ID, Tank_ID, Employee_ID, Customer_Code,
                        FuelType_ID, Fuel_Amount_Liters, Unit_Price, Total_Amount, Payment_Type,
                        Discount_Amount, Notes)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''',
                     (invoice_data['invoice_no'], invoice_data['station_id'], invoice_data['pump_id'],
                      invoice_data['tank_id'], invoice_data.get('employee_id'), invoice_data.get('customer_code'),
                      invoice_data['fuel_type_id'], invoice_data['fuel_amount_liters'], invoice_data['unit_price'],
                      total_amount, invoice_data.get('payment_type', 'Cash'), invoice_data.get('discount_amount', 0),
                      invoice_data.get('notes')))

            # Insert tax details
            if tax_details:
                for tax in tax_details:
                    tax_amount = calculate_tax(taxable_amount, tax['tax_id'])
                    c.execute('''INSERT INTO InvoiceTaxDetails
                               (Invoice_No, Tax_ID, Taxable_Amount, Tax_Amount)
                               VALUES (%s, %s, %s, %s)''',
                             (invoice_data['invoice_no'], tax['tax_id'], taxable_amount, tax_amount))

            # Create journal entry
            entry_number = f"JE{invoice_data['invoice_no'][3:]}"
            description = f"Sales Invoice: {invoice_data['invoice_no']}"

            details = [
                {
                    'account_id': '1000',  # Cash/Bank
                    'description': description,
                    'debit': total_amount,
                    'reference': invoice_data['invoice_no']
                },
                {
                    'account_id': '4000',  # Sales Revenue
                    'description': description,
                    'credit': taxable_amount,
                    'reference': invoice_data['invoice_no']
                },
                {
                    'account_id': '2100',  # Tax Payable
                    'description': f"Tax for {description}",
                    'credit': total_tax,
                    'reference': invoice_data['invoice_no']
                }
            ]

            create_journal_entry(entry_number, date.today(), description, details, 'Invoice', invoice_data['invoice_no'])

            # Update tank and pump
            c.execute('UPDATE FuelTanks SET Current_Amount_Liters = Current_Amount_Liters - %s WHERE Tank_ID = %s',
                     (invoice_data['fuel_amount_liters'], invoice_data['tank_id']))
            c.execute('UPDATE FuelPumps SET Total_Liters_Dispensed = Total_Liters_Dispensed + %s WHERE Pump_ID = %s',
                     (invoice_data['fuel_amount_liters'], invoice_data['pump_id']))

            conn.commit()
            return True

    except Exception as e:
        logger.error(f"Error creating invoice with tax: {e}")
        return False

# Financial Reports Functions
def get_trial_balance(as_of_date=None):
    """Generate trial balance report"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            date_filter = ""
            if as_of_date:
                date_filter = f"AND je.Entry_Date <= '{as_of_date}'"

            query = f"""
                SELECT coa.Account_ID, coa.Account_Name, coa.Account_Type,
                       SUM(jed.Debit) as Total_Debit, SUM(jed.Credit) as Total_Credit,
                       (SUM(jed.Debit) - SUM(jed.Credit)) as Balance
                FROM ChartOfAccounts coa
                LEFT JOIN JournalEntryDetails jed ON coa.Account_ID = jed.Account_ID
                LEFT JOIN JournalEntries je ON jed.Entry_ID = je.Entry_ID
                WHERE coa.Is_Active = TRUE AND je.Status = 'Posted' {date_filter}
                GROUP BY coa.Account_ID, coa.Account_Name, coa.Account_Type
                HAVING Balance != 0
                ORDER BY coa.Account_ID
            """

            c.execute(query)
            return c.fetchall()

    except Exception as e:
        logger.error(f"Error generating trial balance: {e}")
        return []

def get_profit_loss_report(start_date, end_date):
    """Generate profit and loss report"""
    try:
        with get_db_connection() as conn:
            c = conn.cursor()

            # Revenue
            c.execute("""
                SELECT SUM(jed.Credit - jed.Debit) as Revenue
                FROM JournalEntryDetails jed
                JOIN JournalEntries je ON jed.Entry_ID = je.Entry_ID
                JOIN ChartOfAccounts coa ON jed.Account_ID = coa.Account_ID
                WHERE coa.Account_Type = 'Revenue' AND je.Status = 'Posted'
                AND je.Entry_Date BETWEEN %s AND %s
            """, (start_date, end_date))

            revenue = c.fetchone()[0] or 0

            # Expenses
            c.execute("""
                SELECT SUM(jed.Debit - jed.Credit) as Expenses
                FROM JournalEntryDetails jed
                JOIN JournalEntries je ON jed.Entry_ID = je.Entry_ID
                JOIN ChartOfAccounts coa ON jed.Account_ID = coa.Account_ID
                WHERE coa.Account_Type IN ('Expense', 'CostOfSales') AND je.Status = 'Posted'
                AND je.Entry_Date BETWEEN %s AND %s
            """, (start_date, end_date))

            expenses = c.fetchone()[0] or 0

            return {
                'revenue': revenue,
                'expenses': expenses,
                'net_profit': revenue - expenses
            }

    except Exception as e:
        logger.error(f"Error generating P&L report: {e}")
        return {'revenue': 0, 'expenses': 0, 'net_profit': 0}

# Initialize accounting system
def initialize_accounting_system():
    """Initialize the accounting system by creating tables"""
    create_accounting_tables()
    logger.info("Accounting system initialized successfully")
