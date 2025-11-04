import streamlit as st
import uuid
from datetime import datetime
from core.accounting_system import create_payment_voucher, get_payment_vouchers
from core.database_enhanced import get_all_employees

def main():
    """Payment Voucher Management Interface"""
    st.markdown('<div class="page-header"><h2>📤 سندات الصرف</h2></div>', unsafe_allow_html=True)

    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["إنشاء سند صرف", "عرض السندات", "البحث والفلترة"])

    with tab1:
        create_payment_voucher_form()

    with tab2:
        display_payment_vouchers()

    with tab3:
        search_payment_vouchers()

def create_payment_voucher_form():
    """Form to create new payment voucher"""
    st.markdown("### إنشاء سند صرف جديد")

    with st.form("payment_voucher_form"):
        col1, col2 = st.columns(2)

        with col1:
            payment_date = st.date_input("تاريخ الصرف", value=datetime.now().date())

            vendor_name = st.text_input("اسم المورد/المستفيد")
            amount = st.number_input("المبلغ", min_value=0.01, step=0.01, format="%.2f")

            # Employee selection for who made the payment
            employees = get_all_employees()
            employee_options = [""] + [f"{e[0]} - {e[1]}" for e in employees]
            selected_employee = st.selectbox("من قام بالصرف", employee_options)
            paid_by = selected_employee.split(" - ")[0] if selected_employee else None

        with col2:
            payment_method = st.selectbox(
                "طريقة الدفع",
                ["Cash", "Bank", "Cheque", "Card"],
                format_func=lambda x: {
                    "Cash": "نقدي",
                    "Bank": "تحويل بنكي",
                    "Cheque": "شيك",
                    "Card": "بطاقة ائتمان"
                }.get(x, x)
            )

            if payment_method == "Cheque":
                cheque_number = st.text_input("رقم الشيك")
                bank_name = st.text_input("اسم البنك")
            else:
                cheque_number = None
                bank_name = None

            if payment_method == "Bank":
                reference_number = st.text_input("رقم المرجع")
            else:
                reference_number = None

        description = st.text_area("الوصف والتفاصيل", height=100)

        # Expense categories
        expense_categories = [
            "رواتب وأجور",
            "إيجارات",
            "صيانة وإصلاحات",
            "وقود وطاقة",
            "مستلزمات مكتبية",
            "تأمين",
            "ضرائب ورسوم",
            "نقل وبوابة",
            "اتصالات",
            "إعلان وتسويق",
            "مصروفات متنوعة",
            "أخرى"
        ]

        expense_category = st.selectbox("تصنيف المصروف", expense_categories)

        submitted = st.form_submit_button("إنشاء سند الصرف", use_container_width=True)

        if submitted:
            if not amount or amount <= 0:
                st.error("يجب إدخال مبلغ صحيح")
                return

            if not vendor_name:
                st.error("يجب إدخال اسم المورد/المستفيد")
                return

            payment_data = {
                'payment_id': str(uuid.uuid4())[:20],
                'payment_date': payment_date,
                'vendor_name': vendor_name,
                'amount': amount,
                'payment_method': payment_method,
                'cheque_number': cheque_number,
                'bank_name': bank_name,
                'reference_number': reference_number,
                'description': f"{expense_category}: {description}",
                'paid_by': paid_by
            }

            try:
                payment_number = create_payment_voucher(payment_data)
                if payment_number:
                    st.success(f"تم إنشاء سند الصرف بنجاح! رقم السند: {payment_number}")

                    # Display voucher details
                    st.info(f"""
                    **تفاصيل السند:**
                    - رقم السند: {payment_number}
                    - التاريخ: {payment_date}
                    - المستفيد: {vendor_name}
                    - المبلغ: {amount:,.2f}
                    - التصنيف: {expense_category}
                    """)

                    st.balloons()
                else:
                    st.error("فشل في إنشاء سند الصرف")
            except Exception as e:
                st.error(f"خطأ في إنشاء سند الصرف: {str(e)}")

def display_payment_vouchers():
    """Display payment vouchers in a table"""
    st.markdown("### قائمة سندات الصرف")

    vouchers = get_payment_vouchers()

    if not vouchers:
        st.info("لا توجد سندات صرف")
        return

    # Convert to display format
    display_data = []
    for voucher in vouchers:
        display_data.append({
            'رقم السند': voucher[1],  # Payment_Number
            'التاريخ': voucher[2].strftime('%Y-%m-%d') if voucher[2] else '',
            'المستفيد': voucher[4] or 'غير محدد',  # Vendor_Name
            'المبلغ': f"{voucher[5]:,.2f}",
            'طريقة الدفع': {
                'Cash': 'نقدي',
                'Bank': 'تحويل بنكي',
                'Cheque': 'شيك',
                'Card': 'بطاقة ائتمان'
            }.get(voucher[6], voucher[6]),
            'الحالة': {
                'Draft': 'مسودة',
                'Posted': 'مرحل',
                'Cancelled': 'ملغي'
            }.get(voucher[11], voucher[11]),
            'الوصف': voucher[9][:50] + '...' if voucher[9] and len(voucher[9]) > 50 else voucher[9] or ''
        })

    st.dataframe(display_data, use_container_width=True)

def search_payment_vouchers():
    """Search and filter payment vouchers"""
    st.markdown("### البحث في سندات الصرف")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("البحث عن", placeholder="رقم السند أو اسم المستفيد")

    with col2:
        status_filter = st.selectbox(
            "الحالة",
            ["الكل", "مسودة", "مرحل", "ملغي"],
            index=0
        )

    with col3:
        date_from = st.date_input("من تاريخ", value=None)
        date_to = st.date_input("إلى تاريخ", value=None)

    # Amount range filter
    col4, col5 = st.columns(2)
    with col4:
        min_amount = st.number_input("المبلغ الأدنى", min_value=0.0, step=0.01)
    with col5:
        max_amount = st.number_input("المبلغ الأعلى", min_value=0.0, step=0.01, value=1000000.0)

    if st.button("بحث", use_container_width=True):
        vouchers = get_payment_vouchers(limit=1000)

        # Apply filters
        filtered_vouchers = []
        for voucher in vouchers:
            # Search term filter
            if search_term:
                search_text = f"{voucher[1]} {voucher[4] or ''} {voucher[9] or ''}".lower()
                if search_term.lower() not in search_text:
                    continue

            # Status filter
            if status_filter != "الكل":
                status_map = {
                    "مسودة": "Draft",
                    "مرحل": "Posted",
                    "ملغي": "Cancelled"
                }
                if voucher[11] != status_map.get(status_filter):
                    continue

            # Date filter
            if date_from and voucher[2] < date_from:
                continue
            if date_to and voucher[2] > date_to:
                continue

            # Amount filter
            if voucher[5] < min_amount or voucher[5] > max_amount:
                continue

            filtered_vouchers.append(voucher)

        if not filtered_vouchers:
            st.info("لا توجد نتائج مطابقة")
            return

        # Display filtered results
        display_data = []
        for voucher in filtered_vouchers:
            display_data.append({
                'رقم السند': voucher[1],
                'التاريخ': voucher[2].strftime('%Y-%m-%d') if voucher[2] else '',
                'المستفيد': voucher[4] or 'غير محدد',
                'المبلغ': f"{voucher[5]:,.2f}",
                'طريقة الدفع': {
                    'Cash': 'نقدي',
                    'Bank': 'تحويل بنكي',
                    'Cheque': 'شيك',
                    'Card': 'بطاقة ائتمان'
                }.get(voucher[6], voucher[6]),
                'الحالة': {
                    'Draft': 'مسودة',
                    'Posted': 'مرحل',
                    'Cancelled': 'ملغي'
                }.get(voucher[11], voucher[11]),
                'الوصف': voucher[9][:50] + '...' if voucher[9] and len(voucher[9]) > 50 else voucher[9] or ''
            })

        st.dataframe(display_data, use_container_width=True)
        st.info(f"تم العثور على {len(filtered_vouchers)} سند صرف")

        # Summary statistics
        total_amount = sum(v[5] for v in filtered_vouchers)
        st.metric("إجمالي المبالغ", f"{total_amount:,.2f}")

if __name__ == "__main__":
    main()
