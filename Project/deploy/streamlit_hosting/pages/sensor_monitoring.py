import streamlit as st
import time
import random
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from core.database_enhanced import (
    get_all_tanks, get_all_pumps, get_all_fuel_types, get_all_stations,
    get_all_employees, record_sensor_reading, get_dashboard_stats,
    get_system_setting, get_all_sensor_readings, get_pump_meter_reading
)
from core.sensor_api import get_sensor_api

def sensor_monitoring():
    # إعدادات الصفحة
    st.set_page_config(
        page_title="لوحة تحكم خزانات الوقود الذكية",
        page_icon="⛽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # إضافة CSS مخصص بتصميم إبداعي يشبه الخزانات والعدادات الحقيقية
    st.markdown("""
    <style>
        /* خلفية محطة الوقود */
        body {
            font-family: 'Cairo', 'Inter', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #ffffff;
            margin: 0;
            padding: 0;
        }

        .main-header {
            text-align: center;
            margin-bottom: 2rem;
            color: #ffffff;
        }

        /* تصميم الخزان الأفقي الإبداعي */
        .tank-container {
            position: relative;
            width: 100%;
            height: 180px;
            background: linear-gradient(145deg, #2c3e50, #34495e);
            border: 4px solid #3498db;
            border-radius: 90px;
            overflow: hidden;
            box-shadow:
                0 10px 30px rgba(52, 152, 219, 0.3),
                inset 0 0 20px rgba(0,0,0,0.3),
                0 0 0 2px rgba(255,255,255,0.1);
            margin: 20px 0;
        }

        .tank-container::before {
            content: '';
            position: absolute;
            top: -15px;
            left: 50%;
            transform: translateX(-50%);
            width: 80px;
            height: 25px;
            background: linear-gradient(45deg, #95a5a6, #7f8c8d);
            border-radius: 50%;
            border: 3px solid #34495e;
            z-index: 2;
        }

        .tank-container::after {
            content: '';
            position: absolute;
            bottom: 15px;
            left: 50%;
            transform: translateX(-50%);
            width: 50px;
            height: 10px;
            background: #7f8c8d;
            border-radius: 5px;
            z-index: 2;
        }

        .fuel-fill {
            position: absolute;
            top: 0;
            left: 0;
            height: 100%;
            transition: width 1s ease-out;
            background: linear-gradient(90deg,
                rgba(231, 76, 60, 0.9) 0%,
                rgba(230, 126, 34, 0.9) 30%,
                rgba(46, 204, 113, 0.9) 70%,
                rgba(52, 152, 219, 0.9) 100%);
            box-shadow: inset 0 0 20px rgba(255,255,255,0.3);
        }

        .fuel-fill::before {
            content: '';
            position: absolute;
            top: 0;
            right: 0;
            width: 3px;
            height: 100%;
            background: linear-gradient(to bottom,
                rgba(255,255,255,0.8) 0%,
                rgba(255,255,255,0.4) 50%,
                rgba(255,255,255,0.8) 100%);
        }

        /* تصميم العداد الرقمي الإبداعي */
        .digital-meter {
            background: linear-gradient(145deg, #1a1a1a, #2d2d2d);
            border: 3px solid #00ff00;
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            box-shadow:
                0 0 20px rgba(0, 255, 0, 0.5),
                inset 0 0 20px rgba(0, 255, 0, 0.1);
            position: relative;
            overflow: hidden;
        }

        .digital-meter::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: linear-gradient(90deg, #ff0000, #ffff00, #00ff00);
        }

        .meter-display {
            font-family: 'Courier New', monospace;
            font-size: 3rem;
            font-weight: bold;
            color: #00ff00;
            text-shadow:
                0 0 10px rgba(0, 255, 0, 0.8),
                0 0 20px rgba(0, 255, 0, 0.6),
                0 0 30px rgba(0, 255, 0, 0.4);
            margin: 10px 0;
            letter-spacing: 2px;
        }

        .meter-label {
            font-size: 0.9rem;
            color: #cccccc;
            margin-bottom: 10px;
        }

        /* تصميم بطاقة المضخة الإبداعية */
        .pump-station {
            background: linear-gradient(145deg, #2c3e50, #34495e);
            border: 3px solid #e74c3c;
            border-radius: 20px;
            padding: 25px;
            margin: 20px 0;
            box-shadow:
                0 8px 25px rgba(231, 76, 60, 0.3),
                inset 0 0 15px rgba(0,0,0,0.2);
            position: relative;
            overflow: hidden;
        }

        .pump-station::before {
            content: '';
            position: absolute;
            top: -10px;
            right: -10px;
            width: 30px;
            height: 30px;
            background: #e74c3c;
            border-radius: 50%;
            box-shadow: 0 0 15px rgba(231, 76, 60, 0.8);
        }

        .pump-station.active {
            border-color: #27ae60;
            box-shadow:
                0 8px 25px rgba(39, 174, 96, 0.4),
                inset 0 0 15px rgba(39, 174, 96, 0.1);
        }

        .pump-station.active::before {
            background: #27ae60;
            box-shadow: 0 0 15px rgba(39, 174, 96, 0.8);
        }

        .pump-title {
            font-size: 1.5rem;
            font-weight: bold;
            color: #ecf0f1;
            margin-bottom: 15px;
            text-shadow: 0 2px 4px rgba(0,0,0,0.5);
        }

        .pump-info {
            display: flex;
            justify-content: space-between;
            margin-bottom: 15px;
            color: #bdc3c7;
            font-size: 0.9rem;
        }

        /* أزرار التحكم الإبداعية */
        .control-button {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            border: 2px solid #c0392b;
            border-radius: 25px;
            padding: 12px 25px;
            font-size: 1rem;
            font-weight: bold;
            color: white;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
            box-shadow: 0 4px 15px rgba(231, 76, 60, 0.3);
        }

        .control-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(231, 76, 60, 0.5);
        }

        .control-button.active {
            background: linear-gradient(45deg, #27ae60, #2ecc71);
            border-color: #27ae60;
            box-shadow: 0 4px 15px rgba(39, 174, 96, 0.3);
        }

        .control-button.active:hover {
            box-shadow: 0 6px 20px rgba(39, 174, 96, 0.5);
        }

        /* إحصائيات محطة الوقود */
        .station-stats {
            background: linear-gradient(145deg, #34495e, #2c3e50);
            border: 2px solid #3498db;
            border-radius: 15px;
            padding: 20px;
            margin: 20px 0;
            box-shadow: 0 4px 15px rgba(52, 152, 219, 0.2);
        }

        .stat-card {
            background: rgba(52, 152, 219, 0.1);
            border: 1px solid rgba(52, 152, 219, 0.3);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            margin: 10px 0;
        }

        .stat-value {
            font-size: 2rem;
            font-weight: bold;
            color: #3498db;
            margin-bottom: 5px;
        }

        .stat-label {
            color: #bdc3c7;
            font-size: 0.9rem;
        }

        /* تأثيرات الإضاءة والظلال */
        .glow-effect {
            animation: glow 2s ease-in-out infinite alternate;
        }

        @keyframes glow {
            from {
                box-shadow: 0 0 20px rgba(52, 152, 219, 0.5);
            }
            to {
                box-shadow: 0 0 30px rgba(52, 152, 219, 0.8), 0 0 40px rgba(52, 152, 219, 0.6);
            }
        }

        /* تصميم التنبيهات */
        .alert-critical {
            background: linear-gradient(45deg, #e74c3c, #c0392b);
            color: white;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            animation: pulse 1s infinite;
        }

        .alert-warning {
            background: linear-gradient(45deg, #f39c12, #e67e22);
            color: white;
            padding: 10px;
            border-radius: 8px;
            margin: 10px 0;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.7; }
            100% { opacity: 1; }
        }
    </style>
    """, unsafe_allow_html=True)
    
    # العنوان الرئيسي
    st.markdown("""
    <div class="main-header">
        <h1 style="font-size: 2.5rem; font-weight: bold; color: #1e40af;">
            لوحة تحكم خزانات الوقود الذكية
        </h1>
        <p style="font-size: 1.25rem; color: #374151;">
            نظام مراقبة متقدم للتشغيل والتحكم
        </p>
    </div>
    """, unsafe_allow_html=True) # <-- وهنا أيضاً

    # --- بيانات التطبيق ---
    # جلب البيانات من قاعدة البيانات المحسنة
    def load_tanks_data():
        """Load enhanced tanks data from database with detailed information"""
        try:
            tanks_db = get_all_tanks()
            sensor_readings = get_all_sensor_readings()
            fuel_types = get_all_fuel_types()
            stations = get_all_stations()

            # Create fuel type mapping
            fuel_type_map = {ft[0]: ft[1] for ft in fuel_types} if fuel_types else {}
            station_map = {st[0]: st[1] for st in stations} if stations else {}

            # Create sensor readings mapping by tank_id
            sensor_map = {}
            if sensor_readings:
                for reading in sensor_readings:
                    tank_id = reading[1]  # FuelTank_ID is at index 1
                    level = reading[3]    # Level is at index 3
                    timestamp = reading[2]  # Timestamp is at index 2
                    if tank_id not in sensor_map or sensor_map[tank_id][1] < timestamp:
                        sensor_map[tank_id] = (level, timestamp)

            tanks_data = []
            for tank in tanks_db:
                tank_id = tank[0]
                fuel_type_id = tank[1]
                capacity = float(tank[2] or 10000)
                current_amount = float(tank[3] or 0)
                station_id = tank[4] if len(tank) > 4 else None
                location = tank[5] if len(tank) > 5 else "غير محدد"
                status = tank[6] if len(tank) > 6 else "نشط"

                # Get fuel type name
                fuel_type_name = fuel_type_map.get(fuel_type_id, f"نوع {fuel_type_id}")
                station_name = station_map.get(station_id, "غير محدد") if station_id else "غير محدد"

                # Get real sensor reading if available
                real_sensor_level = None
                if tank_id in sensor_map:
                    real_sensor_level = sensor_map[tank_id][0]

                # Calculate percentage level
                if real_sensor_level is not None and capacity > 0:
                    level_percent = min(100.0, max(0.0, float(real_sensor_level)))
                    current_amount = (level_percent / 100.0) * capacity
                elif capacity > 0:
                    level_percent = min(100.0, (current_amount / capacity) * 100.0)
                else:
                    level_percent = 0.0

                # Determine color based on fuel type
                color = 'rgb(0, 153, 255)' if 'ديزل' in fuel_type_name or 'diesel' in fuel_type_name.lower() else 'rgb(255, 69, 0)'

                # Determine status color and alerts
                status_color = "#10b981" if status == "نشط" else "#ef4444"
                alert_level = "normal"
                if level_percent < 20:
                    alert_level = "critical"
                elif level_percent < 40:
                    alert_level = "warning"

                tanks_data.append({
                    'id': tank_id,
                    'name': f'خزان {fuel_type_name} - {tank_id}',
                    'capacity': capacity,
                    'current_level': level_percent,
                    'current_amount': current_amount,
                    'color': color,
                    'fuel_type': fuel_type_name,
                    'station': station_name,
                    'location': location,
                    'status': status,
                    'status_color': status_color,
                    'alert_level': alert_level,
                    'sensor_reading': real_sensor_level,
                    'last_updated': datetime.now().strftime('%H:%M:%S')
                })

            return tanks_data

        except Exception as e:
            st.error(f"خطأ في تحميل بيانات الخزانات: {str(e)}")
            return []

    def load_pumps_data():
        """Load enhanced pumps data from database with detailed information"""
        try:
            pumps_db = get_all_pumps()
            employees = get_all_employees()
            tanks_data = get_all_tanks()

            # Create mappings
            employee_map = {emp[0]: f"{emp[1]} ({emp[0]})" for emp in employees} if employees else {}
            tank_map = {tank[0]: f"{tank[1]} - {tank[0]}" for tank in tanks_data} if tanks_data else {}

            pumps_data = []
            for pump in pumps_db:
                pump_id = pump[0]
                pump_name = pump[1]
                fuel_tank_id = pump[2] if len(pump) > 2 else None
                employee_id = pump[3] if len(pump) > 3 else None
                location = pump[4] if len(pump) > 4 else "غير محدد"
                status = pump[5] if len(pump) > 5 else "متوقف"

                # Get associated employee and tank names
                employee_name = employee_map.get(employee_id, "غير محدد") if employee_id else "غير محدد"
                tank_name = tank_map.get(fuel_tank_id, "غير محدد") if fuel_tank_id else "غير محدد"

                # Get pump status and meter reading (legacy functions for compatibility)
                pump_status = "ON" if status == "نشط" else "OFF"
                meter_reading = get_pump_meter_reading(pump_id) or 0.0

                # Associated tanks
                associated_tanks = [tank_name] if fuel_tank_id else []

                # Determine status color and alerts
                status_color = "#10b981" if status == "نشط" else "#ef4444"
                alert_level = "normal"
                if status == "متوقف":
                    alert_level = "warning"

                pumps_data.append({
                    'id': pump_id,
                    'name': pump_name,
                    'status': pump_status,
                    'status_text': status,
                    'meter_reading': meter_reading,
                    'associated_tanks': associated_tanks,
                    'employee': employee_name,
                    'tank': tank_name,
                    'location': location,
                    'status_color': status_color,
                    'alert_level': alert_level,
                    'last_updated': datetime.now().strftime('%H:%M:%S')
                })

            return pumps_data

        except Exception as e:
            st.error(f"خطأ في تحميل بيانات المضخات: {str(e)}")
            return []

    # Load data from database
    tanks_data = load_tanks_data()
    pumps_data = load_pumps_data()

    # --- قسم الخزانات الإبداعية ---
    st.markdown("## ⛽ خزانات الوقود الذكية")

    # إحصائيات سريعة للخزانات
    if tanks_data:
        total_tanks = len(tanks_data)
        active_tanks = len([t for t in tanks_data if t['status'] == 'نشط'])
        low_level_tanks = len([t for t in tanks_data if t['alert_level'] == 'critical'])
        warning_tanks = len([t for t in tanks_data if t['alert_level'] == 'warning'])

        st.markdown('<div class="station-stats">', unsafe_allow_html=True)
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{total_tanks}</div><div class="stat-label">إجمالي الخزانات</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{active_tanks}</div><div class="stat-label">الخزانات النشطة</div></div>', unsafe_allow_html=True)
        with col3:
            alert_class = "alert-critical" if low_level_tanks > 0 else ""
            st.markdown(f'<div class="stat-card {alert_class}"><div class="stat-value">{low_level_tanks}</div><div class="stat-label">تنبيهات حرجة</div></div>', unsafe_allow_html=True)
        with col4:
            alert_class = "alert-warning" if warning_tanks > 0 else ""
            st.markdown(f'<div class="stat-card {alert_class}"><div class="stat-value">{warning_tanks}</div><div class="stat-label">تحذيرات</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # عرض الخزانات في شبكة إبداعية
    cols = st.columns(3)
    for i, tank in enumerate(tanks_data):
        with cols[i % 3]:
            # بطاقة الخزان الإبداعية
            alert_class = ""
            if tank['alert_level'] == 'critical':
                alert_class = "alert-critical"
            elif tank['alert_level'] == 'warning':
                alert_class = "alert-warning"

            # عرض الخزان باستخدام Streamlit فقط - لا مزيد من HTML
            st.markdown(f"### {tank['name']}")

            # عرض مستوى الخزان باستخدام شريط تقدم ملون
            progress_color = "🔴" if tank['current_level'] < 20 else "🟡" if tank['current_level'] < 40 else "🟢"
            st.progress(tank['current_level'] / 100, text=f"{progress_color} {tank['current_level']:.1f}% مستوى الوقود")

            # معلومات الخزان في جدول منظم
            col_a, col_b = st.columns(2)
            with col_a:
                st.markdown(f"**نوع الوقود:** {tank['fuel_type']}")
                st.markdown(f"**السعة:** {tank['capacity']:.0f} لتر")
            with col_b:
                st.markdown(f"**الكمية الحالية:** {tank['current_amount']:.1f} لتر")
                st.markdown(f"**الحالة:** {tank['status']}")

            st.caption(f"آخر تحديث: {tank['last_updated']}")

            # أزرار التحكم الإبداعية
            col1, col2 = st.columns(2)
            with col1:
                if st.button(f"⛽ تعبئة {tank['id']}", key=f"fill_{tank['id']}", use_container_width=True):
                    new_level = min(100, tank['current_level'] + 10)
                    new_amount = (new_level / 100) * tank['capacity']
                    record_sensor_reading(tank['id'], new_level, 'level', 'manual_fill')
                    st.success(f"تم تعبئة {tank['name']} بنجاح!")
                    st.rerun()

            with col2:
                if st.button(f"📊 التفاصيل {tank['id']}", key=f"details_{tank['id']}", use_container_width=True):
                    with st.expander(f"تفاصيل {tank['name']}", expanded=True):
                        st.write(f"**معرف الخزان:** {tank['id']}")
                        st.write(f"**نوع الوقود:** {tank['fuel_type']}")
                        st.write(f"**السعة:** {tank['capacity']:.0f} لتر")
                        st.write(f"**الكمية الحالية:** {tank['current_amount']:.1f} لتر")
                        st.write(f"**نسبة الامتلاء:** {tank['current_level']:.1f}%")
                        st.write(f"**المحطة:** {tank['station']}")
                        st.write(f"**الموقع:** {tank['location']}")
                        st.write(f"**الحالة:** {tank['status']}")
                        if tank['sensor_reading'] is not None:
                            st.write(f"**قراءة المستشعر:** {tank['sensor_reading']:.1f}%")
                        st.write(f"**آخر تحديث:** {tank['last_updated']}")
    
    st.markdown("---")
    
    # --- قسم المضخات الإبداعية ---
    st.markdown("## 🚀 مضخات الوقود الذكية")

    # إحصائيات سريعة للمضخات
    if pumps_data:
        total_pumps = len(pumps_data)
        active_pumps = len([p for p in pumps_data if p['status'] == 'ON'])
        inactive_pumps = len([p for p in pumps_data if p['status'] == 'OFF'])

        st.markdown('<div class="station-stats">', unsafe_allow_html=True)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{total_pumps}</div><div class="stat-label">إجمالي المضخات</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{active_pumps}</div><div class="stat-label">المضخات النشطة</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="stat-card"><div class="stat-value">{inactive_pumps}</div><div class="stat-label">المضخات المتوقفة</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

    # عرض المضخات في شبكة إبداعية
    pump_cols = st.columns(2)
    for i, pump in enumerate(pumps_data):
        with pump_cols[i % 2]:
            # بطاقة المضخة الإبداعية
            active_class = "active" if pump['status'] == 'ON' else ""

            st.markdown(f"""
            <div class="pump-station {active_class}">
                <div class="pump-title">{pump['name']}</div>
                <div class="pump-info">
                    <span>الموظف: {pump['employee']}</span>
                    <span>الموقع: {pump['location']}</span>
                </div>
                <div style="margin-bottom: 15px; color: #bdc3c7;">
                    <strong>الخزان المرتبط:</strong> {pump['tank']}
                </div>
                <div style="margin-bottom: 20px;">
                    <span style="background-color: {pump['status_color']}; color: white; padding: 5px 15px; border-radius: 20px; font-size: 0.9rem; font-weight: bold;">
                        {pump['status_text']}
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # عرض عداد المضخة الرقمي
            st.markdown(f"""
            <div class="digital-meter">
                <div class="meter-label">قراءة العداد الحالية</div>
                <div class="meter-display">{pump['meter_reading']:.2f}</div>
                <div class="meter-label">لتر</div>
            </div>
            """, unsafe_allow_html=True)

            # أزرار التحكم الإبداعية
            col1, col2 = st.columns(2)
            with col1:
                button_class = "control-button active" if pump['status'] == 'ON' else "control-button"
                button_text = "إيقاف المضخة" if pump['status'] == 'ON' else "تشغيل المضخة"
                if st.button(f"{button_text} {pump['id']}", key=f"toggle_{pump['id']}_{i}", use_container_width=True):
                    # محاكاة تبديل حالة المضخة
                    new_status = 'OFF' if pump['status'] == 'ON' else 'ON'
                    st.success(f"تم {button_text.split(' ')[1]} {pump['name']} بنجاح! (الحالة الجديدة: {new_status})")
                    st.rerun()

            with col2:
                if st.button(f"📊 التفاصيل {pump['id']}", key=f"pump_details_{pump['id']}", use_container_width=True):
                    # عرض تفاصيل إضافية
                    with st.expander(f"تفاصيل {pump['name']}", expanded=True):
                        st.write(f"**معرف المضخة:** {pump['id']}")
                        st.write(f"**الاسم:** {pump['name']}")
                        st.write(f"**الحالة:** {pump['status_text']}")
                        st.write(f"**قراءة العداد:** {pump['meter_reading']:.2f} لتر")
                        st.write(f"**الموظف المسؤول:** {pump['employee']}")
                        st.write(f"**الخزان المرتبط:** {pump['tank']}")
                        st.write(f"**الموقع:** {pump['location']}")
                        st.write(f"**آخر تحديث:** {pump['last_updated']}")
    
    # --- قسم الرسوم البيانية والتحليلات ---
    st.markdown("---")
    st.markdown("## 📈 الرسوم البيانية والتحليلات")

    # تبويبات للرسوم البيانية
    tab1, tab2, tab3 = st.tabs(["مستويات الخزانات", "استهلاك المضخات", "التنبيهات والإحصائيات"])

    with tab1:
        if tanks_data:
            # عرض الخزانات كرسوم بيانية على شكل خزانات حقيقية
            st.markdown("### 🛢️ عرض الخزانات البصري")

            # إنشاء أعمدة لعرض الخزانات
            cols = st.columns(min(3, len(tanks_data)))

            for i, tank in enumerate(tanks_data):
                with cols[i % len(cols)]:
                    # حساب النسبة المئوية للخزان
                    fill_percentage = tank['current_level']

                    # تحديد لون الخزان حسب المستوى
                    if fill_percentage < 20:
                        tank_color = "#ef4444"  # أحمر للمستويات الحرجة
                        status_text = "حرج"
                    elif fill_percentage < 40:
                        tank_color = "#f59e0b"  # برتقالي للتحذير
                        status_text = "تحذير"
                    else:
                        tank_color = "#10b981"  # أخضر للمستويات الطبيعية
                        status_text = "طبيعي"

                    # رسم الخزان باستخدام HTML/CSS
                    tank_html = f"""
                    <div style="
                        position: relative;
                        width: 100%;
                        height: 300px;
                        background: linear-gradient(145deg, #34495e, #2c3e50);
                        border: 4px solid {tank_color};
                        border-radius: 25px 25px 50px 50px;
                        overflow: hidden;
                        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                        margin: 20px 0;
                    ">
                        <!-- غطاء الخزان -->
                        <div style="
                            position: absolute;
                            top: -15px;
                            left: 50%;
                            transform: translateX(-50%);
                            width: 60px;
                            height: 20px;
                            background: linear-gradient(45deg, #95a5a6, #7f8c8d);
                            border-radius: 50%;
                            border: 2px solid #34495e;
                            z-index: 3;
                        "></div>

                        <!-- فتحة الخزان -->
                        <div style="
                            position: absolute;
                            top: 10px;
                            left: 50%;
                            transform: translateX(-50%);
                            width: 30px;
                            height: 8px;
                            background: #7f8c8d;
                            border-radius: 4px;
                            z-index: 3;
                        "></div>

                        <!-- مستوى الوقود -->
                        <div style="
                            position: absolute;
                            bottom: 0;
                            left: 0;
                            width: 100%;
                            height: {fill_percentage}%;
                            background: linear-gradient(180deg,
                                rgba(46, 204, 113, 0.9) 0%,
                                rgba(39, 174, 96, 0.9) 50%,
                                rgba(34, 197, 94, 0.9) 100%);
                            transition: height 1s ease-out;
                            box-shadow: inset 0 0 20px rgba(255,255,255,0.2);
                        "></div>

                        <!-- تأثير الانعكاس -->
                        <div style="
                            position: absolute;
                            bottom: {fill_percentage}%;
                            left: 0;
                            width: 100%;
                            height: 20px;
                            background: linear-gradient(180deg,
                                rgba(255,255,255,0.3) 0%,
                                rgba(255,255,255,0.1) 50%,
                                transparent 100%);
                        "></div>

                        <!-- خطوط القياس -->
                        <div style="
                            position: absolute;
                            top: 20px;
                            right: 10px;
                            height: calc(100% - 40px);
                            width: 2px;
                            background: rgba(255,255,255,0.3);
                        "></div>

                        <!-- علامات القياس -->
                        <div style="position: absolute; top: 15px; right: 20px; color: white; font-size: 10px; font-weight: bold;">100%</div>
                        <div style="position: absolute; top: 50%; right: 20px; transform: translateY(-50%); color: white; font-size: 10px; font-weight: bold;">50%</div>
                        <div style="position: absolute; bottom: 15px; right: 20px; color: white; font-size: 10px; font-weight: bold;">0%</div>
                    </div>

                    <!-- معلومات الخزان -->
                    <div style="
                        text-align: center;
                        margin: 15px 0;
                        color: #ecf0f1;
                        background: rgba(52, 73, 94, 0.8);
                        padding: 15px;
                        border-radius: 10px;
                        border: 2px solid {tank_color};
                    ">
                        <h4 style="margin: 0 0 10px 0; color: {tank_color}; font-size: 1.1em;">
                            {tank['name']}
                        </h4>
                        <div style="font-size: 1.8rem; font-weight: bold; margin: 10px 0; color: {tank_color};">
                            {fill_percentage:.1f}%
                        </div>
                        <div style="font-size: 0.9rem; color: #bdc3c7; margin-bottom: 5px;">
                            {tank['current_amount']:.1f} لتر / {tank['capacity']:.0f} لتر
                        </div>
                        <div style="font-size: 0.8rem; color: #95a5a6;">
                            الحالة: <span style="color: {tank_color}; font-weight: bold;">{status_text}</span>
                        </div>
                        <div style="font-size: 0.7rem; color: #7f8c8d; margin-top: 5px;">
                            آخر تحديث: {tank['last_updated']}
                        </div>
                    </div>
                    """

                    st.markdown(tank_html, unsafe_allow_html=True)

                    # أزرار التحكم
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"⛽ تعبئة {tank['id']}", key=f"fill_tank_{tank['id']}", use_container_width=True):
                            # محاكاة تعبئة الخزان
                            new_level = min(100, tank['current_level'] + random.uniform(5, 15))
                            record_sensor_reading(tank['id'], new_level, 'manual_fill')
                            st.success(f"تم تعبئة {tank['name']} بنجاح!")
                            time.sleep(1)
                            st.rerun()

                    with col2:
                        if st.button(f"📊 التفاصيل {tank['id']}", key=f"tank_details_{tank['id']}", use_container_width=True):
                            with st.expander(f"تفاصيل {tank['name']}", expanded=True):
                                st.write(f"**معرف الخزان:** {tank['id']}")
                                st.write(f"**نوع الوقود:** {tank['fuel_type']}")
                                st.write(f"**السعة:** {tank['capacity']:.0f} لتر")
                                st.write(f"**الكمية الحالية:** {tank['current_amount']:.1f} لتر")
                                st.write(f"**نسبة الامتلاء:** {tank['current_level']:.1f}%")
                                st.write(f"**المحطة:** {tank['station']}")
                                st.write(f"**الموقع:** {tank['location']}")
                                st.write(f"**الحالة:** {tank['status']}")
                                if tank['sensor_reading'] is not None:
                                    st.write(f"**قراءة المستشعر:** {tank['sensor_reading']:.1f}%")
                                st.write(f"**آخر تحديث:** {tank['last_updated']}")

            # رسم بياني تقليدي كبديل
            st.markdown("---")
            st.markdown("### 📊 الرسم البياني التقليدي")

            fig = go.Figure()

            for tank in tanks_data:
                color = tank['color']
                alert_color = "#ef4444" if tank['alert_level'] == 'critical' else "#f59e0b" if tank['alert_level'] == 'warning' else "#10b981"

                fig.add_trace(go.Bar(
                    x=[tank['name']],
                    y=[tank['current_level']],
                    name=tank['name'],
                    marker_color=color,
                    showlegend=False,
                    text=f"{tank['current_level']:.1f}%",
                    textposition='auto'
                ))

                # إضافة خطوط التنبيه
                fig.add_hline(y=20, line_dash="dash", line_color="red", annotation_text="مستوى حرج")
                fig.add_hline(y=40, line_dash="dash", line_color="orange", annotation_text="تحذير")

            fig.update_layout(
                title="مستويات الخزانات الحالية",
                xaxis_title="الخزانات",
                yaxis_title="نسبة الامتلاء (%)",
                yaxis_range=[0, 100]
            )

            st.plotly_chart(fig, use_container_width=True)

    with tab2:
        if pumps_data:
            # رسم بياني لقراءات عدادات المضخات
            fig2 = go.Figure()

            for pump in pumps_data:
                color = "#10b981" if pump['status'] == 'ON' else "#ef4444"

                fig2.add_trace(go.Bar(
                    x=[pump['name']],
                    y=[pump['meter_reading']],
                    name=pump['name'],
                    marker_color=color,
                    showlegend=False,
                    text=f"{pump['meter_reading']:.2f} لتر",
                    textposition='auto'
                ))

            fig2.update_layout(
                title="قراءات عدادات المضخات",
                xaxis_title="المضخات",
                yaxis_title="الكمية (لتر)"
            )

            st.plotly_chart(fig2, use_container_width=True)

    with tab3:
        # إحصائيات شاملة
        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📊 إحصائيات الخزانات")
            if tanks_data:
                total_capacity = sum(tank['capacity'] for tank in tanks_data)
                total_current = sum(tank['current_amount'] for tank in tanks_data)

def main():
    """Main function for sensor monitoring page"""
    sensor_monitoring()

# لتشغيل التطبيق من Streamlit
if __name__ == "__main__":
    main()
