import streamlit as st
from core.accounting_system import initialize_accounting_system
from pages.accounting.receipt_voucher import main as receipt_voucher_main
from pages.accounting.payment_voucher import main as payment_voucher_main
from pages.accounting.sales_invoice import main as sales_invoice_main
from pages.accounting.journal_entries import main as journal_entries_main

def main():
    """Main Accounting System Interface"""
    st.markdown('<div class="page-header"><h1>💼 النظام المحاسبي</h1></div>', unsafe_allow_html=True)

    # Initialize accounting system
    try:
        initialize_accounting_system()
    except Exception as e:
        st.error(f"خطأ في تهيئة النظام المحاسبي: {e}")
        return

    # Accounting modules navigation
    st.markdown("### الوحدات المحاسبية")

    accounting_modules = {
        "📥 سندات القبض": "إدارة سندات القبض والإيصالات",
        "📤 سندات الصرف": "إدارة سندات الصرف والمدفوعات",
        "🧾 فواتير المبيعات": "إدارة فواتير المبيعات مع الضرائب",
        "📚 القيود اليومية": "إدارة القيود اليومية والحسابات",
        "📊 التقارير المالية": "التقارير المالية والحسابات الختامية"
    }

    selected_module = st.selectbox(
        "اختر الوحدة المحاسبية",
        list(accounting_modules.keys()),
        format_func=lambda x: f"{x} - {accounting_modules[x]}"
    )

    st.markdown("---")

    # Display selected module
    if selected_module == "📥 سندات القبض":
        receipt_voucher_main()

    elif selected_module == "📤 سندات الصرف":
        payment_voucher_main()

    elif selected_module == "🧾 فواتير المبيعات":
        sales_invoice_main()

    elif selected_module == "📚 القيود اليومية":
        journal_entries_main()

    elif selected_module == "📊 التقارير المالية":
        show_financial_reports()

def show_financial_reports():
    """Financial Reports Interface"""
    st.markdown("### 📊 التقارير المالية")

    report_type = st.selectbox(
        "نوع التقرير",
        ["ميزان المراجعة", "قائمة الدخل والخسارة", "تقرير التدفقات النقدية"],
        format_func=lambda x: {
            "ميزان المراجعة": "ميزان المراجعة (Trial Balance)",
            "قائمة الدخل والخسارة": "قائمة الدخل والخسارة (P&L)",
            "تقرير التدفقات النقدية": "تقرير التدفقات النقدية (Cash Flow)"
        }.get(x, x)
    )

    col1, col2 = st.columns(2)

    with col1:
        report_date = st.date_input("تاريخ التقرير", value=None)

    with col2:
        if report_type == "قائمة الدخل والخسارة":
            start_date = st.date_input("من تاريخ")
            end_date = st.date_input("إلى تاريخ")
        else:
            start_date = None
            end_date = None

    if st.button("إنشاء التقرير", use_container_width=True):
        if report_type == "ميزان المراجعة":
            generate_trial_balance_report(report_date)
        elif report_type == "قائمة الدخل والخسارة":
            generate_profit_loss_report(start_date, end_date)
        elif report_type == "تقرير التدفقات النقدية":
            generate_cash_flow_report(report_date)

def generate_trial_balance_report(as_of_date):
    """Generate Trial Balance Report"""
    from core.accounting_system import get_trial_balance

    st.markdown("#### ميزان المراجعة")

    if as_of_date:
        st.info(f"حتى تاريخ: {as_of_date}")
    else:
        st.info("جميع الحركات المرحلة")

    trial_balance = get_trial_balance(as_of_date)

    if not trial_balance:
        st.info("لا توجد بيانات لعرضها")
        return

    # Display trial balance
    display_data = []
    total_debit = 0
    total_credit = 0

    for account in trial_balance:
        display_data.append({
            'رقم الحساب': account[0],
            'اسم الحساب': account[1],
            'نوع الحساب': account[2],
            'المدين': f"{account[3]:,.2f}" if account[3] else "0.00",
            'الدائن': f"{account[4]:,.2f}" if account[4] else "0.00",
            'الرصيد': f"{account[5]:,.2f}"
        })
        total_debit += account[3] or 0
        total_credit += account[4] or 0

    st.dataframe(display_data, use_container_width=True)

    # Totals
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("إجمالي المدين", f"{total_debit:,.2f}")
    with col2:
        st.metric("إجمالي الدائن", f"{total_credit:,.2f}")
    with col3:
        st.metric("الفرق", f"{abs(total_debit - total_credit):,.2f}")

    if abs(total_debit - total_credit) < 0.01:
        st.success("ميزان المراجعة متوازن ✅")
    else:
        st.error("ميزان المراجعة غير متوازن ❌")

def generate_profit_loss_report(start_date, end_date):
    """Generate Profit & Loss Report"""
    from core.accounting_system import get_profit_loss_report

    st.markdown("#### قائمة الدخل والخسارة")

    if start_date and end_date:
        st.info(f"الفترة من {start_date} إلى {end_date}")

        pl_data = get_profit_loss_report(start_date, end_date)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("الإيرادات", f"{pl_data['revenue']:,.2f}")

        with col2:
            st.metric("المصروفات", f"{pl_data['expenses']:,.2f}")

        with col3:
            profit_color = "normal" if pl_data['net_profit'] >= 0 else "inverse"
            st.metric("صافي الربح/الخسارة", f"{pl_data['net_profit']:,.2f}", delta=f"{pl_data['net_profit']:,.2f}")

        # Detailed breakdown
        st.markdown("### تفصيل الإيرادات والمصروفات")
        st.info("جاري تطوير التفاصيل المفصلة للتقرير")

    else:
        st.warning("يرجى تحديد الفترة الزمنية للتقرير")

def generate_cash_flow_report(as_of_date):
    """Generate Cash Flow Report"""
    st.markdown("#### تقرير التدفقات النقدية")

    if as_of_date:
        st.info(f"حتى تاريخ: {as_of_date}")
    else:
        st.info("جميع الحركات المرحلة")

    st.info("جاري تطوير تقرير التدفقات النقدية")

if __name__ == "__main__":
    main()
