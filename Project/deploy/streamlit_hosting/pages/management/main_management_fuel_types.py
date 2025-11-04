import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_fuel_types, add_fuel_type, get_all_tanks, get_all_pumps
)

def main():
    """Main management page for fuel types"""

    st.title("⛽ إدارة أنواع الوقود")

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs([
        "➕ إضافة نوع وقود",
        "📋 جميع أنواع الوقود",
        "📊 تقارير أنواع الوقود"
    ])

    with tab1:
        add_fuel_type_tab()

    with tab2:
        view_fuel_types_tab()

    with tab3:
        fuel_types_reports_tab()

def add_fuel_type_tab():
    """Add new fuel type"""
    st.subheader("➕ إضافة نوع وقود جديد")

    with st.form("add_fuel_type_form"):
        col1, col2 = st.columns(2)

        with col1:
            fuel_type_id = st.text_input("كود نوع الوقود", max_chars=10, help="مثال: FUEL001")
            fuel_type_name = st.text_input("اسم نوع الوقود", max_chars=50, help="مثال: بنزين 95")
            unit_price = st.number_input("السعر للتر", min_value=0.0, value=8.50, step=0.01)

        with col2:
            fuel_type_description = st.text_area("وصف نوع الوقود", height=100)
            is_active = st.checkbox("نشط", value=True)

        if st.form_submit_button("إضافة نوع الوقود", use_container_width=True):
            if fuel_type_id and fuel_type_name:
                if add_fuel_type(fuel_type_id, fuel_type_name, fuel_type_description, unit_price):
                    st.success("✅ تمت إضافة نوع الوقود بنجاح!")
                    st.rerun()
                else:
                    st.error("❌ خطأ في إضافة نوع الوقود")
            else:
                st.error("❌ يرجى ملء جميع الحقول المطلوبة")

def view_fuel_types_tab():
    """View all fuel types"""
    st.subheader("📋 جميع أنواع الوقود")

    fuel_types = get_all_fuel_types()

    if fuel_types:
        df = pd.DataFrame(fuel_types, columns=[
            'FuelType_ID', 'FuelType_Name', 'FuelType_Description',
            'Unit_Price', 'Is_Active', 'Created_Date'
        ])

        # Add price formatting
        df['Unit_Price'] = df['Unit_Price'].apply(lambda x: f"{x:.2f} ريال")

        st.dataframe(df, use_container_width=True)

        # Summary statistics
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("إجمالي أنواع الوقود", len(fuel_types))

        with col2:
            active_types = len([ft for ft in fuel_types if ft[4]])  # Is_Active
            st.metric("الأنواع النشطة", active_types)

        with col3:
            avg_price = sum(float(ft[3]) for ft in fuel_types) / len(fuel_types)
            st.metric("متوسط السعر", f"{avg_price:.2f} ريال")

        # Price range
        prices = [float(ft[3]) for ft in fuel_types]
        st.markdown(f"**نطاق الأسعار:** {min(prices):.2f} - {max(prices):.2f} ريال للتر")
    else:
        st.info("ℹ️ لا توجد أنواع وقود مسجلة")

def fuel_types_reports_tab():
    """Reports for fuel types"""
    st.subheader("📊 تقارير أنواع الوقود")

    # Get related data
    fuel_types = get_all_fuel_types()
    tanks = get_all_tanks()
    pumps = get_all_pumps()

    if not fuel_types:
        st.info("ℹ️ لا توجد بيانات لعرض التقارير")
        return

    # Fuel types with tank and pump counts
    st.subheader("🔗 أنواع الوقود والخزانات والمضخات المرتبطة")

    fuel_data = []
    for fuel_type in fuel_types:
        fuel_id = fuel_type[0]
        fuel_name = fuel_type[1]

        # Count tanks for this fuel type
        tank_count = len([t for t in tanks if t[2] == fuel_id])  # FuelType_ID

        # Count pumps for this fuel type
        pump_count = len([p for p in pumps if p[5] == fuel_id])  # FuelType_ID

        fuel_data.append({
            'نوع الوقود': fuel_name,
            'السعر (ريال/لتر)': float(fuel_type[3]),
            'عدد الخزانات': tank_count,
            'عدد المضخات': pump_count,
            'الإجمالي': tank_count + pump_count
        })

    if fuel_data:
        df = pd.DataFrame(fuel_data)
        st.dataframe(df, use_container_width=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("📊 توزيع الخزانات حسب نوع الوقود")
            tank_chart = pd.DataFrame(fuel_data)[['نوع الوقود', 'عدد الخزانات']]
            st.bar_chart(tank_chart.set_index('نوع الوقود'))

        with col2:
            st.subheader("⛽ توزيع المضخات حسب نوع الوقود")
            pump_chart = pd.DataFrame(fuel_data)[['نوع الوقود', 'عدد المضخات']]
            st.bar_chart(pump_chart.set_index('نوع الوقود'))

    # Price analysis
    st.subheader("💰 تحليل الأسعار")

    prices = [float(ft[3]) for ft in fuel_types]
    if prices:
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("أعلى سعر", f"{max(prices):.2f} ريال")

        with col2:
            st.metric("أقل سعر", f"{min(prices):.2f} ريال")

        with col3:
            avg_price = sum(prices) / len(prices)
            st.metric("متوسط السعر", f"{avg_price:.2f} ريال")

        with col4:
            price_range = max(prices) - min(prices)
            st.metric("نطاق الأسعار", f"{price_range:.2f} ريال")

    # Fuel type utilization
    st.subheader("📈 استخدام أنواع الوقود")

    if tanks and pumps:
        utilization_data = []

        for fuel_type in fuel_types:
            fuel_id = fuel_type[0]
            fuel_name = fuel_type[1]

            # Get tanks for this fuel type
            fuel_tanks = [t for t in tanks if t[2] == fuel_id]

            if fuel_tanks:
                total_capacity = sum(float(t[4]) for t in fuel_tanks)  # Capacity_Liters
                total_current = sum(float(t[5]) for t in fuel_tanks)  # Current_Amount_Liters
                utilization_rate = (total_current / total_capacity * 100) if total_capacity > 0 else 0

                utilization_data.append({
                    'نوع الوقود': fuel_name,
                    'إجمالي السعة (لتر)': total_capacity,
                    'الكمية الحالية (لتر)': total_current,
                    'نسبة الاستخدام %': round(utilization_rate, 1)
                })

        if utilization_data:
            util_df = pd.DataFrame(utilization_data)
            st.dataframe(util_df, use_container_width=True)

            # Color coding for utilization levels
            st.markdown("""
            <style>
            .low-util { color: green; font-weight: bold; }
            .med-util { color: orange; font-weight: bold; }
            .high-util { color: red; font-weight: bold; }
            </style>
            """, unsafe_allow_html=True)

            for _, row in util_df.iterrows():
                utilization = row['نسبة الاستخدام %']
                if utilization < 30:
                    st.markdown(f"🟢 **{row['نوع الوقود']}**: {utilization}% (منخفض)")
                elif utilization < 70:
                    st.markdown(f"🟡 **{row['نوع الوقود']}**: {utilization}% (متوسط)")
                else:
                    st.markdown(f"🔴 **{row['نوع الوقود']}**: {utilization}% (مرتفع)")

if __name__ == "__main__":
    main()
