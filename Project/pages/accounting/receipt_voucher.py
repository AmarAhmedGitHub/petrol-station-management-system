import streamlit as st
import uuid
from datetime import datetime
from core.accounting_system import create_receipt_voucher, get_receipt_vouchers, get_chart_of_accounts
from core.database_enhanced import get_all_customers

def main():
    """Receipt Voucher Management Interface"""
    st.markdown('<div class="page-header"><h2>📥 سندات القبض</h2></div>', unsafe_allow_html=True)

    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["إنشاء سند قبض", "عرض السندات", "البحث والفلترة"])

    with tab1:
        create_receipt_voucher_form()

    with tab2:
        display_receipt_vouchers()

    with tab3:
        search_receipt_vouchers()

def create_receipt_voucher_form():
    """Form to create new receipt voucher"""
    st.markdown("### إنشاء سند قبض جديد")

    with st.form("receipt_voucher_form"):
        col1, col2 = st.columns(2)

        with col1:
            receipt_date = st.date_input("تاريخ الاستلام", value=datetime.now().date())
            customer_option = st.selectbox(
                "العميل",
                ["عميل جديد", "عميل موجود"],
                help="اختر نوع العميل"
            )

            if customer_option == "عميل موجود":
                customers = get_all_customers()
                customer_options = [""] + [f"{c[0]} - {c[1]}" for c in customers]
                selected_customer = st.selectbox("اختر العميل", customer_options)
                customer_id = selected_customer.split(" - ")[0] if selected_customer else None
                customer_name = None
            else:
                customer_id = None
                customer_name = st.text_input("اسم العميل")

            amount = st.number_input("المبلغ", min_value=0.01, step=0.01, format="%.2f")

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

        description = st.text_area("الوصف", height=100)

        submitted = st.form_submit_button("إنشاء سند القبض", use_container_width=True)

        if submitted:
            if not amount or amount <= 0:
                st.error("يجب إدخال مبلغ صحيح")
                return

            if customer_option == "عميل موجود" and not customer_id:
                st.error("يجب اختيار عميل")
                return

            if customer_option == "عميل جديد" and not customer_name:
                st.error("يجب إدخال اسم العميل")
                return

            receipt_data = {
                'receipt_id': str(uuid.uuid4())[:20],
                'receipt_date': receipt_date,
                'customer_id': customer_id,
                'customer_name': customer_name,
                'amount': amount,
                'payment_method': payment_method,
                'cheque_number': cheque_number,
                'bank_name': bank_name,
                'reference_number': reference_number,
                'description': description,
                'received_by': st.session_state.get('username', 'System')
            }

            try:
                receipt_number = create_receipt_voucher(receipt_data)
                if receipt_number:
                    st.success(f"تم إنشاء سند القبض بنجاح! رقم السند: {receipt_number}")
                    st.balloons()
                else:
                    st.error("فشل في إنشاء سند القبض")
            except Exception as e:
                st.error(f"خطأ في إنشاء سند القبض: {str(e)}")

def display_receipt_vouchers():
    """Display receipt vouchers in a table"""
    st.markdown("### قائمة سندات القبض")

    vouchers = get_receipt_vouchers()

    if not vouchers:
        st.info("لا توجد سندات قبض")
        return

    # Convert to display format
    display_data = []
    for voucher in vouchers:
        display_data.append({
            'رقم السند': voucher[1],  # Receipt_Number
            'التاريخ': voucher[2].strftime('%Y-%m-%d') if voucher[2] else '',
            'اسم العميل': voucher[4] or voucher[13] or 'غير محدد',  # Customer_Name or Customer_Name_DB
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
            }.get(voucher[12], voucher[12]),
            'الوصف': voucher[10][:50] + '...' if voucher[10] and len(voucher[10]) > 50 else voucher[10] or ''
        })

    st.dataframe(display_data, use_container_width=True)

def search_receipt_vouchers():
    """Search and filter receipt vouchers"""
    st.markdown("### البحث في سندات القبض")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("البحث عن", placeholder="رقم السند أو اسم العميل")

    with col2:
        status_filter = st.selectbox(
            "الحالة",
            ["الكل", "مسودة", "مرحل", "ملغي"],
            index=0
        )

    with col3:
        date_from = st.date_input("من تاريخ", value=None)
        date_to = st.date_input("إلى تاريخ", value=None)

    if st.button("بحث", use_container_width=True):
        vouchers = get_receipt_vouchers(limit=1000)

        # Apply filters
        filtered_vouchers = []
        for voucher in vouchers:
            # Search term filter
            if search_term:
                search_text = f"{voucher[1]} {voucher[4] or ''} {voucher[13] or ''} {voucher[10] or ''}".lower()
                if search_term.lower() not in search_text:
                    continue

            # Status filter
            if status_filter != "الكل":
                status_map = {
                    "مسودة": "Draft",
                    "مرحل": "Posted",
                    "ملغي": "Cancelled"
                }
                if voucher[12] != status_map.get(status_filter):
                    continue

            # Date filter
            if date_from and voucher[2] < date_from:
                continue
            if date_to and voucher[2] > date_to:
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
                'اسم العميل': voucher[4] or voucher[13] or 'غير محدد',
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
                }.get(voucher[12], voucher[12]),
                'الوصف': voucher[10][:50] + '...' if voucher[10] and len(voucher[10]) > 50 else voucher[10] or ''
            })

        st.dataframe(display_data, use_container_width=True)
        st.info(f"تم العثور على {len(filtered_vouchers)} سند قبض")

if __name__ == "__main__":
    main()
