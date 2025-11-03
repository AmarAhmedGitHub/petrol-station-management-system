import streamlit as st
import uuid
from datetime import datetime
from decimal import Decimal
from core.accounting_system import (
    create_journal_entry, get_journal_entries, post_journal_entry,
    get_chart_of_accounts
)

def main():
    """Journal Entries Management Interface"""
    st.markdown('<div class="page-header"><h2>📚 القيود اليومية</h2></div>', unsafe_allow_html=True)

    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["إنشاء قيد يومي", "عرض القيود", "البحث والفلترة"])

    with tab1:
        create_journal_entry_form()

    with tab2:
        display_journal_entries()

    with tab3:
        search_journal_entries()

def create_journal_entry_form():
    """Form to create new journal entry"""
    st.markdown("### إنشاء قيد يومي جديد")

    # Get chart of accounts
    accounts = get_chart_of_accounts()
    if not accounts:
        st.error("لا توجد حسابات في دليل الحسابات. يرجى إضافة حسابات أولاً.")
        return

    account_options = [f"{acc[0]} - {acc[1]}" for acc in accounts]

    with st.form("journal_entry_form"):
        col1, col2 = st.columns(2)

        with col1:
            entry_date = st.date_input("تاريخ القيد", value=datetime.now().date())
            reference_type = st.selectbox(
                "نوع المرجع",
                ["Adjustment", "Invoice", "Receipt", "Payment", "Opening"],
                format_func=lambda x: {
                    "Adjustment": "تسوية",
                    "Invoice": "فاتورة",
                    "Receipt": "قبض",
                    "Payment": "صرف",
                    "Opening": "افتتاحي"
                }.get(x, x)
            )

        with col2:
            reference_number = st.text_input("رقم المرجع (اختياري)")
            description = st.text_input("وصف القيد")

        # Dynamic entry lines
        st.markdown("### تفاصيل القيد")

        # Initialize session state for entry lines
        if 'entry_lines' not in st.session_state:
            st.session_state.entry_lines = [
                {'account': '', 'description': '', 'debit': 0.0, 'credit': 0.0}
            ]

        # Add/Remove lines buttons
        col_add, col_remove = st.columns([1, 1])
        with col_add:
            if st.form_submit_button("➕ إضافة سطر", use_container_width=True):
                st.session_state.entry_lines.append(
                    {'account': '', 'description': '', 'debit': 0.0, 'credit': 0.0}
                )
                st.rerun()

        with col_remove:
            if st.form_submit_button("➖ حذف آخر سطر", use_container_width=True) and len(st.session_state.entry_lines) > 1:
                st.session_state.entry_lines.pop()
                st.rerun()

        # Display entry lines
        total_debit = Decimal('0')
        total_credit = Decimal('0')

        for i, line in enumerate(st.session_state.entry_lines):
            st.markdown(f"**سطر {i+1}:**")
            col_acc, col_desc, col_deb, col_cred = st.columns([3, 3, 2, 2])

            with col_acc:
                selected_account = st.selectbox(
                    f"الحساب {i+1}",
                    account_options,
                    key=f"account_{i}",
                    index=account_options.index(line['account']) if line['account'] in account_options else 0
                )
                line['account'] = selected_account

            with col_desc:
                line['description'] = st.text_input(
                    f"الوصف {i+1}",
                    value=line['description'],
                    key=f"description_{i}"
                )

            with col_deb:
                debit_val = st.number_input(
                    f"مدين {i+1}",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=line['debit'],
                    key=f"debit_{i}"
                )
                line['debit'] = debit_val
                total_debit += Decimal(str(debit_val))

            with col_cred:
                credit_val = st.number_input(
                    f"دائن {i+1}",
                    min_value=0.0,
                    step=0.01,
                    format="%.2f",
                    value=line['credit'],
                    key=f"credit_{i}"
                )
                line['credit'] = credit_val
                total_credit += Decimal(str(credit_val))

            st.markdown("---")

        # Display totals
        col_totals1, col_totals2 = st.columns(2)
        with col_totals1:
            st.metric("إجمالي المدين", f"{total_debit:,.2f}")
        with col_totals2:
            st.metric("إجمالي الدائن", f"{total_credit:,.2f}")

        # Balance check
        if total_debit != total_credit:
            st.error(f"القيد غير متوازن! الفرق: {abs(total_debit - total_credit):,.2f}")
        else:
            st.success("القيد متوازن ✅")

        submitted = st.form_submit_button("حفظ القيد", use_container_width=True, disabled=total_debit != total_credit)

        if submitted and total_debit == total_credit:
            # Prepare entry details
            details = []
            for line in st.session_state.entry_lines:
                if line['account'] and (line['debit'] > 0 or line['credit'] > 0):
                    account_id = line['account'].split(' - ')[0]
                    details.append({
                        'account_id': account_id,
                        'description': line['description'] or description,
                        'debit': line['debit'],
                        'credit': line['credit'],
                        'reference': reference_number or ''
                    })

            if not details:
                st.error("يجب إدخال تفاصيل القيد")
                return

            # Generate entry number
            entry_number = f"JE{datetime.now().strftime('%Y%m%d%H%M%S')}"

            try:
                entry_id = create_journal_entry(
                    entry_number, entry_date, description,
                    details, reference_type, reference_number
                )

                if entry_id:
                    st.success(f"تم إنشاء القيد بنجاح! رقم القيد: {entry_number}")

                    # Display entry summary
                    st.info(f"""
                    **تفاصيل القيد:**
                    - رقم القيد: {entry_number}
                    - التاريخ: {entry_date}
                    - الوصف: {description}
                    - نوع المرجع: {reference_type}
                    - إجمالي المدين: {total_debit:,.2f}
                    - إجمالي الدائن: {total_credit:,.2f}
                    """)

                    # Reset form
                    st.session_state.entry_lines = [
                        {'account': '', 'description': '', 'debit': 0.0, 'credit': 0.0}
                    ]

                    st.balloons()
                else:
                    st.error("فشل في إنشاء القيد")

            except Exception as e:
                st.error(f"خطأ في إنشاء القيد: {str(e)}")

def display_journal_entries():
    """Display journal entries in a table"""
    st.markdown("### قائمة القيود اليومية")

    entries = get_journal_entries()

    if not entries:
        st.info("لا توجد قيود يومية")
        return

    # Group entries by entry_id
    entries_dict = {}
    for entry in entries:
        entry_id = entry[0]
        if entry_id not in entries_dict:
            entries_dict[entry_id] = {
                'entry_number': entry[1],
                'entry_date': entry[2],
                'description': entry[3],
                'reference_type': entry[4],
                'reference_number': entry[5],
                'total_debit': entry[6],
                'total_credit': entry[7],
                'status': entry[8],
                'details': []
            }
        if entry[9]:  # Detail_ID exists
            entries_dict[entry_id]['details'].append({
                'account_name': entry[12] or 'غير محدد',
                'detail_description': entry[13] or '',
                'debit': entry[14] or 0,
                'credit': entry[15] or 0,
                'reference': entry[16] or ''
            })

    # Display entries
    for entry_id, entry_data in entries_dict.items():
        with st.expander(f"📄 {entry_data['entry_number']} - {entry_data['description'][:50]}..."):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.write(f"**التاريخ:** {entry_data['entry_date'].strftime('%Y-%m-%d') if entry_data['entry_date'] else ''}")
                st.write(f"**الحالة:** {entry_data['status']}")
            with col2:
                st.write(f"**نوع المرجع:** {entry_data['reference_type']}")
                st.write(f"**رقم المرجع:** {entry_data['reference_number'] or 'غير محدد'}")
            with col3:
                st.write(f"**إجمالي المدين:** {entry_data['total_debit']:,.2f}")
                st.write(f"**إجمالي الدائن:** {entry_data['total_credit']:,.2f}")

            # Display details
            if entry_data['details']:
                st.markdown("**تفاصيل القيد:**")
                details_data = []
                for detail in entry_data['details']:
                    details_data.append({
                        'الحساب': detail['account_name'],
                        'الوصف': detail['detail_description'],
                        'مدين': f"{detail['debit']:,.2f}",
                        'دائن': f"{detail['credit']:,.2f}",
                        'المرجع': detail['reference']
                    })
                st.dataframe(details_data, use_container_width=True)

            # Post button for draft entries
            if entry_data['status'] == 'Draft':
                if st.button(f"ترحيل القيد {entry_data['entry_number']}", key=f"post_{entry_id}"):
                    try:
                        success = post_journal_entry(entry_id, st.session_state.get('username', 'System'))
                        if success:
                            st.success("تم ترحيل القيد بنجاح!")
                            st.rerun()
                        else:
                            st.error("فشل في ترحيل القيد")
                    except Exception as e:
                        st.error(f"خطأ في ترحيل القيد: {str(e)}")

def search_journal_entries():
    """Search and filter journal entries"""
    st.markdown("### البحث في القيود اليومية")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("البحث عن", placeholder="رقم القيد أو الوصف")

    with col2:
        status_filter = st.selectbox(
            "الحالة",
            ["الكل", "Draft", "Posted", "Voided"],
            format_func=lambda x: {
                "الكل": "الكل",
                "Draft": "مسودة",
                "Posted": "مرحل",
                "Voided": "ملغي"
            }.get(x, x)
        )

    with col3:
        reference_type_filter = st.selectbox(
            "نوع المرجع",
            ["الكل", "Adjustment", "Invoice", "Receipt", "Payment", "Opening"],
            format_func=lambda x: {
                "الكل": "الكل",
                "Adjustment": "تسوية",
                "Invoice": "فاتورة",
                "Receipt": "قبض",
                "Payment": "صرف",
                "Opening": "افتتاحي"
            }.get(x, x)
        )

    date_col1, date_col2 = st.columns(2)
    with date_col1:
        date_from = st.date_input("من تاريخ", value=None)
    with date_col2:
        date_to = st.date_input("إلى تاريخ", value=None)

    if st.button("بحث", use_container_width=True):
        entries = get_journal_entries(limit=1000)

        # Apply filters
        filtered_entries = []
        seen_entries = set()

        for entry in entries:
            entry_id = entry[0]

            if entry_id in seen_entries:
                continue

            # Search term filter
            if search_term:
                search_text = f"{entry[1]} {entry[3] or ''} {entry[5] or ''}".lower()
                if search_term.lower() not in search_text:
                    continue

            # Status filter
            if status_filter != "الكل" and entry[8] != status_filter:
                continue

            # Reference type filter
            if reference_type_filter != "الكل" and entry[4] != reference_type_filter:
                continue

            # Date filter
            if date_from and entry[2] < date_from:
                continue
            if date_to and entry[2] > date_to:
                continue

            filtered_entries.append(entry)
            seen_entries.add(entry_id)

        if not filtered_entries:
            st.info("لا توجد نتائج مطابقة")
            return

        # Display summary
        unique_entries = len(set(e[0] for e in filtered_entries))
        total_debit = sum(e[6] for e in filtered_entries)
        total_credit = sum(e[7] for e in filtered_entries)

        col_sum1, col_sum2, col_sum3 = st.columns(3)
        with col_sum1:
            st.metric("عدد القيود", unique_entries)
        with col_sum2:
            st.metric("إجمالي المدين", f"{total_debit:,.2f}")
        with col_sum3:
            st.metric("إجمالي الدائن", f"{total_credit:,.2f}")

        st.info(f"تم العثور على {unique_entries} قيد يومي")

if __name__ == "__main__":
    main()
