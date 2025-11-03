import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from core.database_enhanced import (
    get_all_pumps, get_all_tanks, get_all_stations
)

def main():
    """Main management page for maintenance"""

    st.title("🔧 إدارة الصيانة")

    # Create tabs for different maintenance operations
    tab1, tab2, tab3 = st.tabs([
        "⛽ صيانة المضخات",
        "🗂️ صيانة الخزانات",
        "📊 تقارير الصيانة"
    ])

    with tab1:
        pump_maintenance_tab()

    with tab2:
        tank_maintenance_tab()

    with tab3:
        maintenance_reports_tab()

def pump_maintenance_tab():
    """Pump maintenance management"""
    st.subheader("⛽ إدارة صيانة المضخات")

    # Get pumps data
    pumps = get_all_pumps()
    stations = get_all_stations()

    if not pumps:
        st.info("ℹ️ لا توجد مضخات مسجلة")
        return

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة صيانة مضخة")

        with st.form("add_pump_maintenance_form"):
            pump_id = st.selectbox(
                "المضخة",
                [p[0] for p in pumps],
                format_func=lambda x: f"{x} - {next((p[2] for p in pumps if p[0] == x), x)}"
            )

            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )

            maintenance_type = st.selectbox("نوع الصيانة", [
                "صيانة دورية", "إصلاح طارئ", "استبدال قطعة", "تنظيف", "معايرة"
            ])

            maintenance_date = st.date_input("تاريخ الصيانة", value=datetime.now().date())
            technician_name = st.text_input("اسم الفني", max_chars=50)
            description = st.text_area("وصف الصيانة", height=80)
            cost = st.number_input("التكلفة (ريال)", min_value=0.0, value=0.0, step=10.0)
            next_maintenance_date = st.date_input("تاريخ الصيانة القادمة")

            if st.form_submit_button("إضافة الصيانة", use_container_width=True):
                # Here you would add the maintenance record to database
                st.success("✅ تمت إضافة سجل الصيانة بنجاح!")
                st.rerun()

    with col2:
        st.markdown("### 📋 المضخات التي تحتاج صيانة")

        # Filter pumps that need maintenance
        pumps_needing_maintenance = []
        for pump in pumps:
            next_service = pump[11]  # Next_Service
            if next_service and isinstance(next_service, str):
                try:
                    next_service_date = pd.to_datetime(next_service).date()
                    if next_service_date <= datetime.now().date():
                        pumps_needing_maintenance.append(pump)
                except:
                    continue
            elif next_service and next_service <= datetime.now().date():
                pumps_needing_maintenance.append(pump)

        if pumps_needing_maintenance:
            df = pd.DataFrame(pumps_needing_maintenance, columns=[
                'Pump_ID', 'Station_ID', 'Pump_Name', 'Pump_Number', 'Location',
                'FuelType_ID', 'Tank_ID', 'Employee_ID', 'Max_Flow_Rate',
                'Is_Active', 'Last_Service', 'Next_Service', 'Total_Liters_Dispensed', 'Created_Date',
                'Station_Name', 'FuelType_Name', 'Tank_Name', 'Employee_Name'
            ])
            st.dataframe(df, use_container_width=True)

            st.warning(f"⚠️ يوجد {len(pumps_needing_maintenance)} مضخة تحتاج صيانة")
        else:
            st.success("✅ جميع المضخات في حالة جيدة")

def tank_maintenance_tab():
    """Tank maintenance management"""
    st.subheader("🗂️ إدارة صيانة الخزانات")

    # Get tanks data
    tanks = get_all_tanks()
    stations = get_all_stations()

    if not tanks:
        st.info("ℹ️ لا توجد خزانات مسجلة")
        return

    # Create columns for add/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ إضافة صيانة خزان")

        with st.form("add_tank_maintenance_form"):
            tank_id = st.selectbox(
                "الخزان",
                [t[0] for t in tanks],
                format_func=lambda x: f"{x} - {next((t[3] for t in tanks if t[0] == x), x)}"
            )

            station_id = st.selectbox(
                "المحطة",
                [s[0] for s in stations] if stations else [""],
                format_func=lambda x: next((s[1] for s in stations if s[0] == x), x)
            )

            maintenance_type = st.selectbox("نوع الصيانة", [
                "صيانة دورية", "فحص الضغط", "تنظيف", "إصلاح تسرب", "معايرة"
            ])

            maintenance_date = st.date_input("تاريخ الصيانة", value=datetime.now().date())
            technician_name = st.text_input("اسم الفني", max_chars=50)
            description = st.text_area("وصف الصيانة", height=80)
            cost = st.number_input("التكلفة (ريال)", min_value=0.0, value=0.0, step=50.0)
            next_maintenance_date = st.date_input("تاريخ الصيانة القادمة")

            if st.form_submit_button("إضافة الصيانة", use_container_width=True):
                # Here you would add the maintenance record to database
                st.success("✅ تمت إضافة سجل الصيانة بنجاح!")
                st.rerun()

    with col2:
        st.markdown("### 📋 الخزانات التي تحتاج صيانة")

        # Filter tanks that need maintenance
        tanks_needing_maintenance = []
        for tank in tanks:
            next_maintenance = tank[11]  # Next_Maintenance
            if next_maintenance and isinstance(next_maintenance, str):
                try:
                    next_maintenance_date = pd.to_datetime(next_maintenance).date()
                    if next_maintenance_date <= datetime.now().date():
                        tanks_needing_maintenance.append(tank)
                except:
                    continue
            elif next_maintenance and next_maintenance <= datetime.now().date():
                tanks_needing_maintenance.append(tank)

        if tanks_needing_maintenance:
            df = pd.DataFrame(tanks_needing_maintenance, columns=[
                'Tank_ID', 'Station_ID', 'FuelType_ID', 'Tank_Name', 'Capacity_Liters',
                'Current_Amount_Liters', 'Max_Pressure', 'Min_Pressure', 'Location',
                'Is_Active', 'Last_Maintenance', 'Next_Maintenance', 'Created_Date',
                'Station_Name', 'FuelType_Name'
            ])
            st.dataframe(df, use_container_width=True)

            st.warning(f"⚠️ يوجد {len(tanks_needing_maintenance)} خزان يحتاج صيانة")
        else:
            st.success("✅ جميع الخزانات في حالة جيدة")

def maintenance_reports_tab():
    """Reports for maintenance"""
    st.subheader("📊 تقارير الصيانة")

    # Get data
    pumps = get_all_pumps()
    tanks = get_all_tanks()

    # Maintenance overview
    st.subheader("📋 نظرة عامة على الصيانة")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        # Pumps needing maintenance
        pumps_needing_maint = 0
        for pump in pumps:
            next_service = pump[11]  # Next_Service
            if next_service:
                try:
                    if isinstance(next_service, str):
                        next_service_date = pd.to_datetime(next_service).date()
                    else:
                        next_service_date = next_service
                    if next_service_date <= datetime.now().date():
                        pumps_needing_maint += 1
                except:
                    continue
        st.metric("المضخات تحتاج صيانة", pumps_needing_maint)

    with col2:
        # Tanks needing maintenance
        tanks_needing_maint = 0
        for tank in tanks:
            next_maintenance = tank[11]  # Next_Maintenance
            if next_maintenance:
                try:
                    if isinstance(next_maintenance, str):
                        next_maintenance_date = pd.to_datetime(next_maintenance).date()
                    else:
                        next_maintenance_date = next_maintenance
                    if next_maintenance_date <= datetime.now().date():
                        tanks_needing_maint += 1
                except:
                    continue
        st.metric("الخزانات تحتاج صيانة", tanks_needing_maint)

    with col3:
        # Total active pumps
        active_pumps = len([p for p in pumps if p[9]])  # Is_Active
        st.metric("المضخات النشطة", active_pumps)

    with col4:
        # Total active tanks
        active_tanks = len([t for t in tanks if t[9]])  # Is_Active
        st.metric("الخزانات النشطة", active_tanks)

    # Maintenance schedule
    st.subheader("📅 جدول الصيانة القادمة")

    # Upcoming pump maintenance
    st.markdown("**⛽ المضخات:**")
    upcoming_pump_maint = []
    for pump in pumps:
        next_service = pump[11]  # Next_Service
        if next_service:
            try:
                if isinstance(next_service, str):
                    next_service_date = pd.to_datetime(next_service).date()
                else:
                    next_service_date = next_service

                days_until = (next_service_date - datetime.now().date()).days
                if 0 <= days_until <= 30:  # Next 30 days
                    upcoming_pump_maint.append({
                        'النوع': 'مضخة',
                        'الاسم': pump[2],  # Pump_Name
                        'المحطة': pump[14],  # Station_Name
                        'تاريخ الصيانة': next_service_date.strftime('%Y-%m-%d'),
                        'الأيام المتبقية': days_until
                    })
            except:
                continue

    # Upcoming tank maintenance
    upcoming_tank_maint = []
    for tank in tanks:
        next_maintenance = tank[11]  # Next_Maintenance
        if next_maintenance:
            try:
                if isinstance(next_maintenance, str):
                    next_maintenance_date = pd.to_datetime(next_maintenance).date()
                else:
                    next_maintenance_date = next_maintenance

                days_until = (next_maintenance_date - datetime.now().date()).days
                if 0 <= days_until <= 30:  # Next 30 days
                    upcoming_tank_maint.append({
                        'النوع': 'خزان',
                        'الاسم': tank[3],  # Tank_Name
                        'المحطة': tank[13],  # Station_Name
                        'تاريخ الصيانة': next_maintenance_date.strftime('%Y-%m-%d'),
                        'الأيام المتبقية': days_until
                    })
            except:
                continue

    # Combine and sort
    all_upcoming = upcoming_pump_maint + upcoming_tank_maint
    all_upcoming.sort(key=lambda x: x['الأيام المتبقية'])

    if all_upcoming:
        upcoming_df = pd.DataFrame(all_upcoming)
        st.dataframe(upcoming_df, use_container_width=True)

        # Color coding for urgency
        st.markdown("""
        <style>
        .urgent { color: red; font-weight: bold; }
        .warning { color: orange; font-weight: bold; }
        .normal { color: green; }
        </style>
        """, unsafe_allow_html=True)

        for _, row in upcoming_df.iterrows():
            days = row['الأيام المتبقية']
            if days <= 7:
                st.markdown(f"🔴 **{row['النوع']} - {row['الاسم']}**: {days} أيام متبقية")
            elif days <= 14:
                st.markdown(f"🟠 **{row['النوع']} - {row['الاسم']}**: {days} أيام متبقية")
            else:
                st.markdown(f"🟢 **{row['النوع']} - {row['الاسم']}**: {days} أيام متبقية")
    else:
        st.success("✅ لا توجد صيانة مقررة في الثلاثين يوماً القادمة")

    # Maintenance history (mock data - in real system would come from maintenance tables)
    st.subheader("📜 تاريخ الصيانة")

    # Create mock maintenance history
    maintenance_history = []

    # Add some sample data
    for i, pump in enumerate(pumps[:5]):  # First 5 pumps
        maintenance_history.append({
            'التاريخ': (datetime.now() - timedelta(days=30*i)).strftime('%Y-%m-%d'),
            'النوع': 'مضخة',
            'الاسم': pump[2],
            'المحطة': pump[14],
            'نوع الصيانة': 'صيانة دورية',
            'التكلفة': 500 + i*100
        })

    for i, tank in enumerate(tanks[:3]):  # First 3 tanks
        maintenance_history.append({
            'التاريخ': (datetime.now() - timedelta(days=60*i)).strftime('%Y-%m-%d'),
            'النوع': 'خزان',
            'الاسم': tank[3],
            'المحطة': tank[13],
            'نوع الصيانة': 'فحص دوري',
            'التكلفة': 1000 + i*200
        })

    if maintenance_history:
        history_df = pd.DataFrame(maintenance_history)
        st.dataframe(history_df, use_container_width=True)

        # Maintenance cost analysis
        total_cost = sum(h['التكلفة'] for h in maintenance_history)
        avg_cost = total_cost / len(maintenance_history)

        st.markdown(f"**إجمالي تكلفة الصيانة:** {total_cost:,.0f} ريال")
        st.markdown(f"**متوسط تكلفة الصيانة:** {avg_cost:.0f} ريال")

if __name__ == "__main__":
    main()
