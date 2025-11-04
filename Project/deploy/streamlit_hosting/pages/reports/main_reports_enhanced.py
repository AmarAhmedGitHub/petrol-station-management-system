import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_fuel_types,
    get_all_employees, get_all_invoices, get_all_supplies, get_dashboard_stats,
    get_pending_debts, get_employee_debts
)
from core.safe_html import get_safe_html

def main():
    """Enhanced reports page"""
    safe_html = get_safe_html()

    # Header with enhanced design
    safe_html.display_dashboard_header(
        "التقارير المحسنة",
        "تحليل شامل ومتقدم لجميع جوانب أداء محطات الوقود",
        "📊"
    )

    # Get dashboard stats
    stats = get_dashboard_stats()

    # Display key metrics with enhanced design
    display_key_metrics(stats)

    # Create tabs for different report categories with enhanced styling
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏭 تقارير المحطات",
        "⛽ تقارير المضخات والخزانات",
        "👥 تقارير الموظفين",
        "💰 تقارير المبيعات",
        "📈 التحليلات المتقدمة",
        "💳 تحليلات ديون الموظفين"
    ])

    with tab1:
        station_reports()

    with tab2:
        pumps_tanks_reports()

    with tab3:
        employees_reports()

    with tab4:
        sales_reports()

    with tab5:
        advanced_analytics()

    with tab6:
        employee_debts_analytics()

def display_key_metrics(stats):
    """Display key performance metrics with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "المؤشرات الرئيسية",
        "نظرة شاملة على أداء النظام والمؤشرات الحيوية",
        "📊"
    )

    # First row of metrics with enhanced design
    metrics_row1 = [
        {
            "icon": "🏭",
            "value": str(stats.get('total_stations', 0)),
            "label": "إجمالي المحطات",
            "color": "#2563eb"
        },
        {
            "icon": "⛽",
            "value": str(stats.get('total_pumps', 0)),
            "label": "إجمالي المضخات",
            "color": "#dc2626"
        },
        {
            "icon": "🗂️",
            "value": str(stats.get('total_tanks', 0)),
            "label": "إجمالي الخزانات",
            "color": "#ea580c"
        },
        {
            "icon": "👥",
            "value": str(stats.get('total_employees', 0)),
            "label": "إجمالي الموظفين",
            "color": "#7c3aed"
        }
    ]

    safe_html.display_metric_grid(metrics_row1)

    # Second row of metrics with enhanced design
    metrics_row2 = [
        {
            "icon": "💰",
            "value": f"{stats.get('today_sales', 0):,.0f}",
            "label": "مبيعات اليوم (ريال)",
            "color": "#059669"
        },
        {
            "icon": "📈",
            "value": f"{stats.get('month_sales', 0):,.0f}",
            "label": "مبيعات الشهر (ريال)",
            "color": "#0891b2"
        },
        {
            "icon": "⚠️",
            "value": str(stats.get('low_fuel_tanks', 0)),
            "label": "خزانات منخفضة الوقود",
            "color": "#dc2626"
        },
        {
            "icon": "🔧",
            "value": str(stats.get('maintenance_pumps', 0)),
            "label": "مضخات تحتاج صيانة",
            "color": "#ea580c"
        }
    ]

    safe_html.display_metric_grid(metrics_row2)

def station_reports():
    """Station-related reports with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "تقارير المحطات",
        "تحليل شامل لأداء المحطات وتوزيع الموارد",
        "🏭"
    )

    stations = get_all_stations()
    pumps = get_all_pumps()
    tanks = get_all_tanks()

    if not stations:
        safe_html.display_info_alert("لا توجد محطات مسجلة", "info", "ℹ️")
        return

    # Station performance overview with enhanced design
    safe_html.display_section_header("أداء المحطات", icon="📈")

    station_data = []
    for station in stations:
        station_id = station[0]
        station_name = station[1]

        # Count pumps for this station
        station_pumps = [p for p in pumps if p[1] == station_id]
        pump_count = len(station_pumps)

        # Count tanks for this station
        station_tanks = [t for t in tanks if t[1] == station_id]
        tank_count = len(station_tanks)

        # Calculate total capacity and current fuel
        total_capacity = sum(float(t[4]) for t in station_tanks)  # Capacity_Liters
        total_current = sum(float(t[5]) for t in station_tanks)  # Current_Amount_Liters
        capacity_utilization = (total_current / total_capacity * 100) if total_capacity > 0 else 0

        station_data.append({
            'المحطة': station_name,
            'عدد المضخات': pump_count,
            'عدد الخزانات': tank_count,
            'إجمالي السعة (لتر)': total_capacity,
            'الكمية الحالية (لتر)': total_current,
            'نسبة الاستخدام %': round(capacity_utilization, 1)
        })

    if station_data:
        df = pd.DataFrame(station_data)

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            df,
            "بيانات أداء المحطات",
            "جدول شامل يوضح أداء كل محطة وتوزيع مواردها"
        )

        # Enhanced charts with better layout
        col1, col2 = st.columns(2)

        with col1:
            safe_html.display_section_header("توزيع المضخات حسب المحطة", icon="📊")
            pump_chart = pd.DataFrame(station_data)[['المحطة', 'عدد المضخات']]
            st.bar_chart(pump_chart.set_index('المحطة'))

        with col2:
            safe_html.display_section_header("توزيع الخزانات حسب المحطة", icon="🗂️")
            tank_chart = pd.DataFrame(station_data)[['المحطة', 'عدد الخزانات']]
            st.bar_chart(tank_chart.set_index('المحطة'))

        # Capacity utilization with enhanced design
        safe_html.display_section_header("استخدام سعة الخزانات", icon="⛽")

        util_df = pd.DataFrame(station_data)[['المحطة', 'نسبة الاستخدام %']]
        st.bar_chart(util_df.set_index('المحطة'))

def pumps_tanks_reports():
    """Pumps and tanks reports with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "تقارير المضخات والخزانات",
        "تحليل شامل للمضخات والخزانات وتوزيع أنواع الوقود",
        "⛽"
    )

    pumps = get_all_pumps()
    tanks = get_all_tanks()
    fuel_types = get_all_fuel_types()

    if not pumps and not tanks:
        safe_html.display_info_alert("لا توجد مضخات أو خزانات مسجلة", "info", "ℹ️")
        return

    # Pumps by fuel type with enhanced design
    if pumps:
        safe_html.display_section_header("المضخات حسب نوع الوقود", icon="⛽")

        fuel_pumps = {}
        for pump in pumps:
            fuel_name = pump[15]  # FuelType_Name
            if fuel_name:
                fuel_pumps[fuel_name] = fuel_pumps.get(fuel_name, 0) + 1

        if fuel_pumps:
            fuel_df = pd.DataFrame(list(fuel_pumps.items()), columns=['نوع الوقود', 'عدد المضخات'])

            # Enhanced data table display
            safe_html.display_data_table_with_header(
                fuel_df,
                "توزيع المضخات حسب نوع الوقود",
                "إحصائيات توزيع المضخات على أنواع الوقود المختلفة"
            )

            fig = px.pie(fuel_df, values='عدد المضخات', names='نوع الوقود',
                        title='توزيع المضخات حسب نوع الوقود')
            st.plotly_chart(fig, use_container_width=True)

    # Tanks by fuel type with enhanced design
    if tanks:
        safe_html.display_section_header("الخزانات حسب نوع الوقود", icon="🗂️")

        fuel_tanks = {}
        for tank in tanks:
            fuel_name = tank[14]  # FuelType_Name
            if fuel_name:
                fuel_tanks[fuel_name] = fuel_tanks.get(fuel_name, 0) + 1

        if fuel_tanks:
            fuel_tank_df = pd.DataFrame(list(fuel_tanks.items()), columns=['نوع الوقود', 'عدد الخزانات'])

            # Enhanced data table display
            safe_html.display_data_table_with_header(
                fuel_tank_df,
                "توزيع الخزانات حسب نوع الوقود",
                "إحصائيات توزيع الخزانات على أنواع الوقود المختلفة"
            )

            fig = px.pie(fuel_tank_df, values='عدد الخزانات', names='نوع الوقود',
                        title='توزيع الخزانات حسب نوع الوقود')
            st.plotly_chart(fig, use_container_width=True)

    # Tank capacity analysis with enhanced design
    if tanks:
        safe_html.display_section_header("تحليل سعة الخزانات", icon="📊")

        tank_analysis = []
        for tank in tanks:
            tank_id = tank[0]
            tank_name = tank[3]
            capacity = float(tank[4])
            current = float(tank[5])
            utilization = (current / capacity * 100) if capacity > 0 else 0

            tank_analysis.append({
                'الخزان': tank_name,
                'السعة': capacity,
                'الكمية الحالية': current,
                'نسبة الاستخدام %': round(utilization, 1),
                'الحالة': 'منخفض' if utilization < 30 else 'متوسط' if utilization < 70 else 'مرتفع'
            })

        if tank_analysis:
            analysis_df = pd.DataFrame(tank_analysis)

            # Enhanced data table display
            safe_html.display_data_table_with_header(
                analysis_df,
                "تحليل حالة الخزانات",
                "تحليل مفصل لحالة كل خزان وسعة استخدامه"
            )

            # Status distribution with enhanced chart
            status_counts = analysis_df['الحالة'].value_counts()
            fig = px.pie(status_counts, values=status_counts.values, names=status_counts.index,
                        title='توزيع حالة الخزانات')
            st.plotly_chart(fig, use_container_width=True)

def employees_reports():
    """Employee reports with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "تقارير الموظفين",
        "تحليل شامل للموظفين وتوزيعهم وأدائهم",
        "👥"
    )

    employees = get_all_employees()
    stations = get_all_stations()

    if not employees:
        safe_html.display_info_alert("لا يوجد موظفون مسجلون", "info", "ℹ️")
        return

    # Employees by station with enhanced design
    safe_html.display_section_header("الموظفون حسب المحطة", icon="🏭")

    station_employees = {}
    for emp in employees:
        station_name = emp[14]  # Station_Name
        if station_name:
            station_employees[station_name] = station_employees.get(station_name, 0) + 1

    if station_employees:
        station_df = pd.DataFrame(list(station_employees.items()), columns=['المحطة', 'عدد الموظفين'])

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            station_df,
            "توزيع الموظفين حسب المحطة",
            "إحصائيات توزيع الموظفين على المحطات المختلفة"
        )

        fig = px.bar(station_df, x='المحطة', y='عدد الموظفين',
                    title='توزيع الموظفين حسب المحطة')
        st.plotly_chart(fig, use_container_width=True)

    # Employees by designation with enhanced design
    safe_html.display_section_header("الموظفون حسب المنصب", icon="👔")

    designations = {}
    for emp in employees:
        designation = emp[4]  # Designation
        if designation:
            designations[designation] = designations.get(designation, 0) + 1

    if designations:
        des_df = pd.DataFrame(list(designations.items()), columns=['المنصب', 'عدد الموظفين'])

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            des_df,
            "توزيع الموظفين حسب المنصب",
            "إحصائيات توزيع الموظفين على المناصب المختلفة"
        )

        fig = px.pie(des_df, values='عدد الموظفين', names='المنصب',
                    title='توزيع الموظفين حسب المنصب')
        st.plotly_chart(fig, use_container_width=True)

    # Salary analysis with enhanced design
    safe_html.display_section_header("تحليل الرواتب", icon="💰")

    salaries = [float(e[6]) for e in employees if e[6]]
    if salaries:
        salary_stats = {
            'الحد الأدنى': min(salaries),
            'الحد الأقصى': max(salaries),
            'المتوسط': sum(salaries) / len(salaries),
            'الإجمالي': sum(salaries)
        }

        stats_df = pd.DataFrame(list(salary_stats.items()), columns=['المؤشر', 'المبلغ'])

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            stats_df,
            "إحصائيات الرواتب",
            "تحليل شامل للرواتب في المحطات"
        )

        # Salary distribution with enhanced chart
        fig = px.histogram(
            x=salaries,
            nbins=10,
            title='توزيع الرواتب',
            labels={'x': 'الراتب', 'y': 'عدد الموظفين'}
        )
        st.plotly_chart(fig, use_container_width=True)

def sales_reports():
    """Sales reports with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "تقارير المبيعات",
        "تحليل شامل للمبيعات والإيرادات",
        "💰"
    )

    invoices = get_all_invoices()

    if not invoices:
        safe_html.display_info_alert("لا توجد فواتير مسجلة", "info", "ℹ️")
        return

    # Sales by station with enhanced design
    safe_html.display_section_header("المبيعات حسب المحطة", icon="🏭")

    station_sales = {}
    for inv in invoices:
        station_name = inv[17]  # Station_Name
        total_amount = float(inv[12])  # Total_Amount
        if station_name:
            station_sales[station_name] = station_sales.get(station_name, 0) + total_amount

    if station_sales:
        station_df = pd.DataFrame(list(station_sales.items()), columns=['المحطة', 'إجمالي المبيعات'])

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            station_df,
            "إحصائيات المبيعات حسب المحطة",
            "تحليل المبيعات لكل محطة على حدة"
        )

        fig = px.bar(station_df, x='المحطة', y='إجمالي المبيعات',
                    title='المبيعات حسب المحطة')
        st.plotly_chart(fig, use_container_width=True)

    # Sales by fuel type with enhanced design
    safe_html.display_section_header("المبيعات حسب نوع الوقود", icon="⛽")

    fuel_sales = {}
    for inv in invoices:
        fuel_name = inv[22]  # FuelType_Name
        total_amount = float(inv[12])  # Total_Amount
        if fuel_name:
            fuel_sales[fuel_name] = fuel_sales.get(fuel_name, 0) + total_amount

    if fuel_sales:
        fuel_df = pd.DataFrame(list(fuel_sales.items()), columns=['نوع الوقود', 'إجمالي المبيعات'])

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            fuel_df,
            "إحصائيات المبيعات حسب نوع الوقود",
            "تحليل المبيعات لكل نوع وقود على حدة"
        )

        fig = px.pie(fuel_df, values='إجمالي المبيعات', names='نوع الوقود',
                    title='المبيعات حسب نوع الوقود')
        st.plotly_chart(fig, use_container_width=True)

    # Daily sales trend with enhanced design
    safe_html.display_section_header("اتجاه المبيعات اليومية", icon="📈")

    # Get last 30 days sales
    daily_sales = {}
    for inv in invoices:
        inv_date = inv[6].date()  # Invoice_Date
        total_amount = float(inv[12])  # Total_Amount
        date_str = inv_date.strftime('%Y-%m-%d')
        daily_sales[date_str] = daily_sales.get(date_str, 0) + total_amount

    if daily_sales:
        daily_df = pd.DataFrame(list(daily_sales.items()), columns=['التاريخ', 'المبيعات'])
        daily_df['التاريخ'] = pd.to_datetime(daily_df['التاريخ'])
        daily_df = daily_df.sort_values('التاريخ')

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            daily_df,
            "المبيعات اليومية",
            "تفصيل المبيعات اليومية للفترة المحددة"
        )

        fig = px.line(daily_df, x='التاريخ', y='المبيعات',
                     title='اتجاه المبيعات اليومية')
        st.plotly_chart(fig, use_container_width=True)

def advanced_analytics():
    """Advanced analytics and insights with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "التحليلات المتقدمة",
        "تحليلات متقدمة ورؤى تنبؤية لتحسين الأداء",
        "📈"
    )

    # Get all data
    stations = get_all_stations()
    pumps = get_all_pumps()
    tanks = get_all_tanks()
    employees = get_all_employees()
    invoices = get_all_invoices()
    supplies = get_all_supplies()

    if not (stations and pumps and tanks):
        safe_html.display_info_alert("لا توجد بيانات كافية للتحليلات المتقدمة", "info", "ℹ️")
        return

    # Efficiency metrics with enhanced design
    safe_html.display_section_header("مؤشرات الكفاءة", icon="⚡")

    efficiency_metrics = []

    # Pump efficiency (pumps per station)
    if stations:
        total_pumps = len(pumps)
        total_stations = len(stations)
        avg_pumps_per_station = total_pumps / total_stations if total_stations > 0 else 0
        efficiency_metrics.append({
            "icon": "⛽",
            "value": f"{avg_pumps_per_station:.1f}",
            "label": "متوسط المضخات لكل محطة",
            "color": "#ea580c"
        })

    # Tank efficiency (tanks per station)
    if stations:
        total_tanks = len(tanks)
        total_stations = len(stations)
        avg_tanks_per_station = total_tanks / total_stations if total_stations > 0 else 0
        efficiency_metrics.append({
            "icon": "🗂️",
            "value": f"{avg_tanks_per_station:.1f}",
            "label": "متوسط الخزانات لكل محطة",
            "color": "#dc2626"
        })

    # Employee efficiency (employees per station)
    if stations:
        total_employees = len(employees)
        total_stations = len(stations)
        avg_employees_per_station = total_employees / total_stations if total_stations > 0 else 0
        efficiency_metrics.append({
            "icon": "👥",
            "value": f"{avg_employees_per_station:.1f}",
            "label": "متوسط الموظفين لكل محطة",
            "color": "#7c3aed"
        })

    # Sales efficiency (sales per pump)
    if pumps and invoices:
        total_sales = sum(float(inv[12]) for inv in invoices)
        total_pumps = len(pumps)
        sales_per_pump = total_sales / total_pumps if total_pumps > 0 else 0
        efficiency_metrics.append({
            "icon": "💰",
            "value": f"{sales_per_pump:,.0f}",
            "label": "المبيعات لكل مضخة (ريال)",
            "color": "#059669"
        })

    safe_html.display_metric_grid(efficiency_metrics)

    # Predictive insights with enhanced design
    safe_html.display_section_header("التنبؤات والتوصيات", icon="🔮")

    # Low fuel alerts with enhanced design
    safe_html.display_section_header("تنبيهات انخفاض الوقود", icon="⚠️")

    low_fuel_tanks = []
    for tank in tanks:
        capacity = float(tank[4])
        current = float(tank[5])
        utilization = (current / capacity * 100) if capacity > 0 else 0

        if utilization < 20:  # Less than 20%
            low_fuel_tanks.append({
                'الخزان': tank[3],
                'المحطة': tank[13],
                'الكمية الحالية': current,
                'السعة': capacity,
                'نسبة الاستخدام %': round(utilization, 1)
            })

    if low_fuel_tanks:
        low_fuel_df = pd.DataFrame(low_fuel_tanks)
        safe_html.display_info_alert("يوجد خزانات منخفضة الوقود تحتاج توريد فوري!", "error", "🚨")
        safe_html.display_data_table_with_header(
            low_fuel_df,
            "خزانات منخفضة الوقود",
            "قائمة بالخزانات التي تحتاج توريد وقود فوري"
        )
    else:
        safe_html.display_info_alert("جميع الخزانات في مستويات وقود جيدة", "success", "✅")

    # Maintenance alerts with enhanced design
    safe_html.display_section_header("تنبيهات الصيانة", icon="🔧")

    maintenance_alerts = []

    # Check pumps needing maintenance
    for pump in pumps:
        next_service = pump[11]  # Next_Service
        if next_service:
            try:
                if isinstance(next_service, str):
                    next_service_date = pd.to_datetime(next_service).date()
                else:
                    next_service_date = next_service

                days_until = (next_service_date - datetime.now().date()).days
                if days_until <= 7:  # Next 7 days
                    maintenance_alerts.append({
                        'النوع': 'مضخة',
                        'الاسم': pump[2],
                        'المحطة': pump[14],
                        'تاريخ الصيانة': next_service_date.strftime('%Y-%m-%d'),
                        'الأيام المتبقية': days_until,
                        'الأولوية': 'عالية' if days_until <= 3 else 'متوسطة'
                    })
            except:
                continue

    # Check tanks needing maintenance
    for tank in tanks:
        next_maintenance = tank[11]  # Next_Maintenance
        if next_maintenance:
            try:
                if isinstance(next_maintenance, str):
                    next_maintenance_date = pd.to_datetime(next_maintenance).date()
                else:
                    next_maintenance_date = next_maintenance

                days_until = (next_maintenance_date - datetime.now().date()).days
                if days_until <= 7:  # Next 7 days
                    maintenance_alerts.append({
                        'النوع': 'خزان',
                        'الاسم': tank[3],
                        'المحطة': tank[13],
                        'تاريخ الصيانة': next_maintenance_date.strftime('%Y-%m-%d'),
                        'الأيام المتبقية': days_until,
                        'الأولوية': 'عالية' if days_until <= 3 else 'متوسطة'
                    })
            except:
                continue

    if maintenance_alerts:
        alerts_df = pd.DataFrame(maintenance_alerts)
        safe_html.display_info_alert("يوجد معدات تحتاج صيانة قريباً!", "warning", "🔧")
        safe_html.display_data_table_with_header(
            alerts_df,
            "جدولة الصيانة المقبلة",
            "قائمة بالمعدات التي تحتاج صيانة في الأسبوع القادم"
        )
    else:
        safe_html.display_info_alert("لا توجد صيانة مقررة في الأسبوع القادم", "success", "✅")

    # Performance recommendations with enhanced design
    safe_html.display_section_header("التوصيات", icon="💡")

    recommendations = []

    # Check for stations without managers
    for station in stations:
        station_id = station[0]
        manager_id = station[9]  # Manager_ID

        if not manager_id:
            recommendations.append({
                'النوع': 'تحذير',
                'المحطة': station[1],
                'التوصية': 'تعيين مدير للمحطة',
                'الأولوية': 'عالية'
            })

    # Check for pumps without assigned employees
    for pump in pumps:
        employee_id = pump[7]  # Employee_ID
        if not employee_id:
            recommendations.append({
                'النوع': 'تحسين',
                'المحطة': pump[14],
                'التوصية': f'تعيين موظف للمضخة {pump[2]}',
                'الأولوية': 'متوسطة'
            })

    # Check for tank capacity optimization
    for tank in tanks:
        capacity = float(tank[4])
        current = float(tank[5])
        utilization = (current / capacity * 100) if capacity > 0 else 0

        if utilization > 90:
            recommendations.append({
                'النوع': 'تحسين',
                'المحطة': tank[13],
                'التوصية': f'الخزان {tank[3]} ممتلئ بنسبة {utilization:.1f}% - قد يحتاج توسيع',
                'الأولوية': 'منخفضة'
            })

    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        safe_html.display_info_alert("توصيات لتحسين الأداء:", "info", "💡")
        safe_html.display_data_table_with_header(
            rec_df,
            "التوصيات المقترحة",
            "اقتراحات لتحسين كفاءة النظام وأدائه"
        )
    else:
        safe_html.display_info_alert("النظام يعمل بكفاءة عالية - لا توجد توصيات حالياً", "success", "✅")

def employee_debts_analytics():
    """Employee debts analytics with enhanced design"""
    safe_html = get_safe_html()

    # Section header with enhanced design
    safe_html.display_section_header(
        "تحليلات ديون الموظفين",
        "تحليل شامل لديون الموظفين وإدارتها",
        "💳"
    )

    # Get employee debts data
    employee_debts = get_employee_debts()
    pending_debts = get_pending_debts()

    if not employee_debts and not pending_debts:
        safe_html.display_info_alert("لا توجد ديون مسجلة للموظفين", "info", "ℹ️")
        return

    # Overall debt metrics with enhanced design
    safe_html.display_section_header("مؤشرات الديون العامة", icon="📊")

    debt_metrics = []

    total_debt_amount = sum(float(debt[3]) for debt in employee_debts) if employee_debts else 0
    debt_metrics.append({
        "icon": "💰",
        "value": f"{total_debt_amount:,.0f}",
        "label": "إجمالي الديون (ريال)",
        "color": "#dc2626"
    })

    total_employees_with_debts = len(set(debt[1] for debt in employee_debts)) if employee_debts else 0
    debt_metrics.append({
        "icon": "👥",
        "value": str(total_employees_with_debts),
        "label": "الموظفون المدينون",
        "color": "#ea580c"
    })

    avg_debt_per_employee = total_debt_amount / total_employees_with_debts if total_employees_with_debts > 0 else 0
    debt_metrics.append({
        "icon": "📈",
        "value": f"{avg_debt_per_employee:,.0f}",
        "label": "متوسط الدين لكل موظف (ريال)",
        "color": "#7c3aed"
    })

    pending_count = len(pending_debts) if pending_debts else 0
    debt_metrics.append({
        "icon": "⏳",
        "value": str(pending_count),
        "label": "الديون المعلقة",
        "color": "#059669"
    })

    safe_html.display_metric_grid(debt_metrics)

    # Employee debts by employee with enhanced design
    if employee_debts:
        safe_html.display_section_header("ديون الموظفين", icon="👥")

        debt_data = []
        for debt in employee_debts:
            debt_data.append({
                'الموظف': debt[2],  # Employee_Name
                'المبلغ': float(debt[3]),  # Debt_Amount
                'تاريخ الدين': debt[4].strftime('%Y-%m-%d') if debt[4] else 'غير محدد',  # Debt_Date
                'الحالة': 'مستحق' if debt[5] else 'معلق',  # Is_Paid
                'المحطة': debt[6] if debt[6] else 'غير محدد'  # Station_Name
            })

        debt_df = pd.DataFrame(debt_data)

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            debt_df,
            "جدول ديون الموظفين",
            "تفصيل شامل لجميع ديون الموظفين وحالاتها"
        )

        # Debt distribution by employee with enhanced chart
        employee_debt_totals = debt_df.groupby('الموظف')['المبلغ'].sum().reset_index()
        employee_debt_totals = employee_debt_totals.sort_values('المبلغ', ascending=False)

        fig = px.bar(employee_debt_totals, x='الموظف', y='المبلغ',
                    title='توزيع الديون حسب الموظف',
                    labels={'المبلغ': 'مبلغ الدين (ريال)', 'الموظف': 'اسم الموظف'})
        st.plotly_chart(fig, use_container_width=True)

    # Pending debts analysis with enhanced design
    if pending_debts:
        safe_html.display_section_header("الديون المعلقة", icon="⏳")

        pending_data = []
        for debt in pending_debts:
            pending_data.append({
                'الموظف': debt[2],  # Employee_Name
                'المبلغ': float(debt[3]),  # Debt_Amount
                'تاريخ الدين': debt[4].strftime('%Y-%m-%d') if debt[4] else 'غير محدد',  # Debt_Date
                'المحطة': debt[6] if debt[6] else 'غير محدد'  # Station_Name
            })

        pending_df = pd.DataFrame(pending_data)

        # Enhanced data table display
        safe_html.display_data_table_with_header(
            pending_df,
            "الديون المعلقة",
            "قائمة بالديون التي لم يتم سدادها بعد"
        )

        # Pending debts by station with enhanced chart
        if 'المحطة' in pending_df.columns:
            station_pending = pending_df.groupby('المحطة')['المبلغ'].sum().reset_index()
            fig = px.pie(station_pending, values='المبلغ', names='المحطة',
                        title='توزيع الديون المعلقة حسب المحطة')
            st.plotly_chart(fig, use_container_width=True)

    # Debt alerts and recommendations with enhanced design
    safe_html.display_section_header("تنبيهات الديون", icon="⚠️")

    alerts = []

    # High debt alerts
    if employee_debts:
        for debt in employee_debts:
            amount = float(debt[3])
            employee_name = debt[2]
            if amount > 5000:  # High debt threshold
                alerts.append({
                    'النوع': 'تحذير',
                    'الموظف': employee_name,
                    'التفاصيل': f'دين مرتفع: {amount:,.2f} ريال',
                    'الأولوية': 'عالية'
                })

    # Pending debts alerts
    if pending_debts and len(pending_debts) > 5:
        alerts.append({
            'النوع': 'تنبيه',
            'الموظف': 'عام',
            'التفاصيل': f'عدد كبير من الديون المعلقة: {len(pending_debts)}',
            'الأولوية': 'متوسطة'
        })

    if alerts:
        alerts_df = pd.DataFrame(alerts)
        safe_html.display_info_alert("تنبيهات متعلقة بالديون:", "warning", "⚠️")
        safe_html.display_data_table_with_header(
            alerts_df,
            "تنبيهات الديون",
            "تنبيهات هامة متعلقة بإدارة الديون"
        )
    else:
        safe_html.display_info_alert("لا توجد تنبيهات ديون حالياً", "success", "✅")

    # Debt recovery recommendations with enhanced design
    safe_html.display_section_header("توصيات استرداد الديون", icon="💡")

    recommendations = []

    if employee_debts:
        # Employees with high debts
        high_debt_employees = [debt for debt in employee_debts if float(debt[3]) > 3000]
        if high_debt_employees:
            recommendations.append({
                'التوصية': 'إنشاء خطة سداد للموظفين ذوي الديون العالية',
                'العدد المعني': len(set(debt[1] for debt in high_debt_employees)),
                'الأولوية': 'عالية'
            })

        # Old debts
        from datetime import datetime, timedelta
        old_debts = []
        for debt in employee_debts:
            if debt[4] and (datetime.now().date() - debt[4]).days > 90:
                old_debts.append(debt)

        if old_debts:
            recommendations.append({
                'التوصية': 'متابعة الديون القديمة (أكثر من 3 أشهر)',
                'العدد المعني': len(old_debts),
                'الأولوية': 'متوسطة'
            })

    if recommendations:
        rec_df = pd.DataFrame(recommendations)
        safe_html.display_info_alert("توصيات لإدارة الديون:", "info", "💡")
        safe_html.display_data_table_with_header(
            rec_df,
            "التوصيات المقترحة",
            "اقتراحات لتحسين إدارة واسترداد الديون"
        )
    else:
        safe_html.display_info_alert("إدارة الديون جيدة - لا توجد توصيات إضافية", "success", "✅")

if __name__ == "__main__":
    main()
