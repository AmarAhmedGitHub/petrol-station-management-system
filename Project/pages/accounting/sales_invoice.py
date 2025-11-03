import streamlit as st
import uuid
from datetime import datetime
from decimal import Decimal
from core.accounting_system import create_invoice_with_tax, get_active_taxes, calculate_tax
from core.database_enhanced import get_all_customers, get_fuel_types, get_stations, get_pumps, get_tanks

def main():
    """Sales Invoice Management Interface"""
    st.markdown('<div class="page-header"><h2>🧾 فواتير المبيعات</h2></div>', unsafe_allow_html=True)

    # Create tabs for different functions
    tab1, tab2, tab3 = st.tabs(["إنشاء فاتورة مبيعات", "عرض الفواتير", "البحث والفلترة"])

    with tab1:
        create_sales_invoice_form()

    with tab2:
        display_sales_invoices()

    with tab3:
        search_sales_invoices()

def create_sales_invoice_form():
    """Form to create new sales invoice with tax calculations"""
    st.markdown("### إنشاء فاتورة مبيعات جديدة")

    with st.form("sales_invoice_form"):
        col1, col2 = st.columns(2)

        with col1:
            # Generate invoice number
            invoice_date = st.date_input("تاريخ الفاتورة", value=datetime.now().date())

            # Customer selection
            customers = get_all_customers()
            customer_options = ["عميل نقدي"] + [f"{c[0]} - {c[1]}" for c in customers]
            selected_customer = st.selectbox("العميل", customer_options)
            customer_code = selected_customer.split(" - ")[0] if " - " in selected_customer else None

            # Station selection
            stations = get_stations()
            station_options = [f"{s[0]} - {s[1]}" for s in stations]
            selected_station = st.selectbox("المحطة", station_options)
            station_id = selected_station.split(" - ")[0]

            # Pump selection
            pumps = get_pumps()
            pump_options = [f"{p[0]} - {p[1]}" for p in pumps]
            selected_pump = st.selectbox("المضخة", pump_options)
            pump_id = selected_pump.split(" - ")[0]

        with col2:
            # Tank selection
            tanks = get_tanks()
            tank_options = [f"{t[0]} - {t[1]}" for t in tanks]
            selected_tank = st.selectbox("الخزان", tank_options)
            tank_id = selected_tank.split(" - ")[0]

            # Fuel type selection
            fuel_types = get_fuel_types()
            fuel_options = [f"{f[0]} - {f[1]}" for f in fuel_types]
            selected_fuel = st.selectbox("نوع الوقود", fuel_options)
            fuel_type_id = selected_fuel.split(" - ")[0]

            # Fuel quantity and pricing
            fuel_amount_liters = st.number_input("كمية الوقود (لتر)", min_value=0.01, step=0.01, format="%.2f")
            unit_price = st.number_input("سعر الوحدة", min_value=0.01, step=0.01, format="%.2f")

        # Tax selection
        st.markdown("### إعدادات الضرائب")
        active_taxes = get_active_taxes()

        if active_taxes:
            tax_options = st.multiselect(
                "الضرائب المطبقة",
                [f"{t[0]} - {t[1]} ({t[3]}%)" for t in active_taxes],
                help="اختر الضرائب المراد تطبيقها على هذه الفاتورة"
            )

            selected_tax_ids = [opt.split(" - ")[0] for opt in tax_options]
        else:
            st.info("لا توجد ضرائب مفعلة")
            selected_tax_ids = []

        # Payment and discount
        col3, col4 = st.columns(2)
        with col3:
            payment_type = st.selectbox("طريقة الدفع", ["Cash", "Card", "Credit"])
            discount_amount = st.number_input("خصم (اختياري)", min_value=0.0, step=0.01, format="%.2f")

        with col4:
            notes = st.text_area("ملاحظات", height=80)

        # Calculate totals
        if fuel_amount_liters and unit_price:
            taxable_amount = Decimal(str(fuel_amount_liters)) * Decimal(str(unit_price))
            total_tax = Decimal('0')

            if selected_tax_ids:
                for tax_id in selected_tax_ids:
                    tax_amount = calculate_tax(taxable_amount, tax_id)
                    total_tax += tax_amount

            total_amount = taxable_amount + total_tax - Decimal(str(discount_amount))

            # Display calculation summary
            st.markdown("### ملخص الحساب")
            col5, col6, col7, col8 = st.columns(4)
            with col5:
                st.metric("المبلغ الخاضع للضريبة", f"{taxable_amount:,.2f}")
            with col6:
                st.metric("إجمالي الضرائب", f"{total_tax:,.2f}")
            with col7:
                st.metric("الخصم", f"{discount_amount:,.2f}")
            with col8:
                st.metric("المبلغ الإجمالي", f"{total_amount:,.2f}")

        submitted = st.form_submit_button("إنشاء الفاتورة", use_container_width=True)

        if submitted:
            if not fuel_amount_liters or fuel_amount_liters <= 0:
                st.error("يجب إدخال كمية وقود صحيحة")
                return

            if not unit_price or unit_price <= 0:
                st.error("يجب إدخال سعر وحدة صحيح")
                return

            # Generate invoice number
            invoice_no = f"INV{datetime.now().strftime('%Y%m%d%H%M%S')}"

            invoice_data = {
                'invoice_no': invoice_no,
                'station_id': station_id,
                'pump_id': pump_id,
                'tank_id': tank_id,
                'customer_code': customer_code,
                'fuel_type_id': fuel_type_id,
                'fuel_amount_liters': fuel_amount_liters,
                'unit_price': unit_price,
                'payment_type': payment_type,
                'discount_amount': discount_amount,
                'notes': notes
            }

            # Prepare tax details
            tax_details = [{'tax_id': tax_id} for tax_id in selected_tax_ids] if selected_tax_ids else None

            try:
                success = create_invoice_with_tax(invoice_data, tax_details)
                if success:
                    st.success(f"تم إنشاء الفاتورة بنجاح! رقم الفاتورة: {invoice_no}")

                    # Display invoice summary
                    st.info(f"""
                    **تفاصيل الفاتورة:**
                    - رقم الفاتورة: {invoice_no}
                    - التاريخ: {invoice_date}
                    - العميل: {selected_customer}
                    - نوع الوقود: {selected_fuel}
                    - الكمية: {fuel_amount_liters} لتر
                    - السعر: {unit_price:,.2f} لكل لتر
                    - المبلغ الخاضع للضريبة: {taxable_amount:,.2f}
                    - إجمالي الضرائب: {total_tax:,.2f}
                    - الخصم: {discount_amount:,.2f}
                    - المبلغ الإجمالي: {total_amount:,.2f}
                    """)

                    st.balloons()
                else:
                    st.error("فشل في إنشاء الفاتورة")
            except Exception as e:
                st.error(f"خطأ في إنشاء الفاتورة: {str(e)}")

def display_sales_invoices():
    """Display sales invoices in a table"""
    st.markdown("### قائمة فواتير المبيعات")

    # This would need to be implemented with a function to get invoices with tax details
    # For now, showing a placeholder
    st.info("جاري تطوير عرض الفواتير مع تفاصيل الضرائب")

def search_sales_invoices():
    """Search and filter sales invoices"""
    st.markdown("### البحث في فواتير المبيعات")

    col1, col2, col3 = st.columns(3)

    with col1:
        search_term = st.text_input("البحث عن", placeholder="رقم الفاتورة أو اسم العميل")

    with col2:
        date_from = st.date_input("من تاريخ", value=None)
        date_to = st.date_input("إلى تاريخ", value=None)

    with col3:
        fuel_type_filter = st.selectbox("نوع الوقود", ["الكل"] + [f"{f[0]} - {f[1]}" for f in get_fuel_types()])

    if st.button("بحث", use_container_width=True):
        st.info("جاري تطوير البحث في الفواتير")

if __name__ == "__main__":
    main()
