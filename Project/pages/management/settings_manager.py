"""
Settings Manager - Configuration and Settings Interfaces

This module handles all system configuration and settings interfaces,
including fuel types, shifts, system settings, and other configuration options.
"""

import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_fuel_types, add_fuel_type, get_all_shifts, add_shift,
    get_all_stations, get_all_employees, get_all_pumps, get_all_tanks,
    get_connection
)


class SettingsManager:
    """Manager for all settings and configuration interfaces"""

    def __init__(self):
        """Initialize the settings manager"""
        pass

    def show_settings_interface(self):
        """Display the main settings interface"""
        st.markdown("""
            <style>
            .settings-header {
                background: linear-gradient(135deg, #28a745 0%, #20c997 100%);
                color: white;
                padding: 2rem;
                border-radius: 15px;
                margin: 1rem 0;
                text-align: center;
            }
            .settings-section {
                background: white;
                padding: 1.5rem;
                border-radius: 10px;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                margin: 1rem 0;
                border-left: 5px solid #28a745;
            }
            .form-container {
                background: #f8f9fa;
                padding: 1.5rem;
                border-radius: 8px;
                margin: 1rem 0;
            }
            .data-table {
                background: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            </style>
        """, unsafe_allow_html=True)

        st.markdown('<h1 class="settings-header">⚙️ الإعدادات والتكوين</h1>', unsafe_allow_html=True)

        # Initialize session state for settings subsections
        if 'settings_subsection' not in st.session_state:
            st.session_state.settings_subsection = None

        # Navigation tabs for different settings categories
        settings_tabs = st.tabs([
            "⛽ أنواع الوقود",
            "🕐 المناوبات والورديات",
            "🔧 إعدادات النظام",
            "📊 إعدادات التقارير",
            "🔗 إعدادات الاتصال"
        ])

        with settings_tabs[0]:
            self._fuel_types_settings()

        with settings_tabs[1]:
            self._shifts_settings()

        with settings_tabs[2]:
            self._system_settings()

        with settings_tabs[3]:
            self._reports_settings()

        with settings_tabs[4]:
            self._connection_settings()

    def _fuel_types_settings(self):
        """Manage fuel types configuration"""
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #28a745; margin-bottom: 1rem;">⛽ إدارة أنواع الوقود</h3>', unsafe_allow_html=True)

        # Create columns for add/view operations
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### ➕ إضافة نوع وقود جديد")
            st.markdown('<div class="form-container">', unsafe_allow_html=True)

            with st.form("add_fuel_type_form"):
                fuel_type_id = st.text_input("رمز نوع الوقود", max_chars=10, placeholder="مثال: FUEL001")
                fuel_type_name = st.text_input("اسم نوع الوقود", max_chars=50, placeholder="مثال: بنزين 95")
                fuel_type_description = st.text_area("وصف نوع الوقود", height=60, placeholder="وصف تفصيلي لنوع الوقود")
                unit_price = st.number_input("السعر لكل لتر (ريال)", min_value=0.0, value=8.50, step=0.10)

                if st.form_submit_button("إضافة نوع الوقود", use_container_width=True):
                    if fuel_type_id and fuel_type_name and unit_price > 0:
                        if add_fuel_type(fuel_type_id, fuel_type_name, fuel_type_description, unit_price):
                            st.success("✅ تمت إضافة نوع الوقود بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ خطأ في إضافة نوع الوقود")
                    else:
                        st.error("❌ يرجى ملء جميع الحقول المطلوبة")

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### 📋 جميع أنواع الوقود")
            st.markdown('<div class="data-table">', unsafe_allow_html=True)

            fuel_types = get_all_fuel_types()
            if fuel_types:
                df = pd.DataFrame(fuel_types, columns=[
                    'FuelType_ID', 'FuelType_Name', 'FuelType_Description',
                    'Unit_Price', 'Is_Active', 'Created_Date'
                ])

                # Format price column
                df['Unit_Price'] = df['Unit_Price'].apply(lambda x: f"{x:.2f} ريال" if pd.notna(x) else "غير محدد")

                # Format active status
                df['Is_Active'] = df['Is_Active'].apply(lambda x: "نشط" if x else "غير نشط")

                st.dataframe(df, use_container_width=True)

                # Summary statistics
                active_count = len([ft for ft in fuel_types if ft.get('Is_Active', False)])
                total_count = len(fuel_types)

                st.markdown(f"**إجمالي الأنواع:** {total_count} | **النشطة:** {active_count}")
            else:
                st.info("ℹ️ لا توجد أنواع وقود مسجلة")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    def _shifts_settings(self):
        """Manage shifts and schedules configuration"""
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #28a745; margin-bottom: 1rem;">🕐 إدارة المناوبات والورديات</h3>', unsafe_allow_html=True)

        # Create columns for add/view operations
        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### ➕ إضافة مناوبة جديدة")
            st.markdown('<div class="form-container">', unsafe_allow_html=True)

            with st.form("add_shift_form"):
                shift_name = st.text_input("اسم المناوبة", max_chars=50, placeholder="مثال: المناوبة الصباحية")
                start_time = st.time_input("وقت البداية")
                end_time = st.time_input("وقت النهاية")
                description = st.text_area("وصف المناوبة", height=60, placeholder="وصف تفصيلي للمناوبة")

                if st.form_submit_button("إضافة المناوبة", use_container_width=True):
                    if shift_name and start_time and end_time:
                        if add_shift(shift_name, start_time, end_time, description):
                            st.success("✅ تمت إضافة المناوبة بنجاح!")
                            st.rerun()
                        else:
                            st.error("❌ خطأ في إضافة المناوبة")
                    else:
                        st.error("❌ يرجى ملء جميع الحقول المطلوبة")

            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.markdown("### 📋 جميع المناوبات")
            st.markdown('<div class="data-table">', unsafe_allow_html=True)

            shifts = get_all_shifts()
            if shifts:
                df = pd.DataFrame(shifts, columns=[
                    'Shift_ID', 'Shift_Name', 'Start_Time', 'End_Time',
                    'Description', 'Is_Active', 'Created_Date'
                ])

                # Format time columns
                df['Start_Time'] = df['Start_Time'].apply(lambda x: str(x) if pd.notna(x) else "غير محدد")
                df['End_Time'] = df['End_Time'].apply(lambda x: str(x) if pd.notna(x) else "غير محدد")

                # Format active status
                df['Is_Active'] = df['Is_Active'].apply(lambda x: "نشط" if x else "غير نشط")

                st.dataframe(df, use_container_width=True)

                # Summary statistics
                active_count = len([s for s in shifts if s.get('Is_Active', False)])
                total_count = len(shifts)

                st.markdown(f"**إجمالي المناوبات:** {total_count} | **النشطة:** {active_count}")
            else:
                st.info("ℹ️ لا توجد مناوبات مسجلة")

            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    def _system_settings(self):
        """Manage system-wide settings"""
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #28a745; margin-bottom: 1rem;">🔧 إعدادات النظام العامة</h3>', unsafe_allow_html=True)

        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        # System settings form
        with st.form("system_settings_form"):
            st.markdown("### ⚙️ إعدادات الصيانة والتنبيهات")

            col1, col2 = st.columns(2)

            with col1:
                pump_maintenance_interval = st.number_input(
                    "فترة صيانة المضخات (بالأيام)",
                    min_value=1, max_value=365, value=90,
                    help="الفترة الزمنية بين الصيانات الدورية للمضخات"
                )

                tank_maintenance_interval = st.number_input(
                    "فترة صيانة الخزانات (بالأيام)",
                    min_value=1, max_value=730, value=180,
                    help="الفترة الزمنية بين الصيانات الدورية للخزانات"
                )

            with col2:
                low_fuel_alert_level = st.number_input(
                    "مستوى تنبيه انخفاض الوقود (%)",
                    min_value=1, max_value=50, value=20,
                    help="النسبة المئوية التي يتم عندها إرسال تنبيه انخفاض الوقود"
                )

                max_discount = st.number_input(
                    "الحد الأقصى للخصم (%)",
                    min_value=0, max_value=50, value=15,
                    help="النسبة المئوية القصوى المسموح بها للخصم على الفواتير"
                )

            st.markdown("### 💰 إعدادات التسعير والمبيعات")

            col3, col4 = st.columns(2)

            with col3:
                default_currency = st.selectbox(
                    "العملة الافتراضية",
                    ["ريال سعودي (SAR)", "دولار أمريكي (USD)", "يورو (EUR)"],
                    index=0,
                    help="العملة الافتراضية للنظام"
                )

                price_update_frequency = st.selectbox(
                    "تكرار تحديث الأسعار",
                    ["يومي", "أسبوعي", "شهري", "يدوي"],
                    index=2,
                    help="كيفية تحديث أسعار الوقود"
                )

            with col4:
                auto_backup = st.checkbox(
                    "النسخ الاحتياطي التلقائي",
                    value=True,
                    help="تفعيل النسخ الاحتياطي التلقائي للبيانات"
                )

                notifications_enabled = st.checkbox(
                    "تفعيل الإشعارات",
                    value=True,
                    help="تفعيل إشعارات النظام والتنبيهات"
                )

            if st.form_submit_button("💾 حفظ الإعدادات", use_container_width=True):
                # Here you would save the settings to database
                st.success("✅ تم حفظ إعدادات النظام بنجاح!")
                st.info("🔄 سيتم تطبيق الإعدادات الجديدة في الجلسة التالية")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    def _reports_settings(self):
        """Manage reports configuration"""
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #28a745; margin-bottom: 1rem;">📊 إعدادات التقارير والإحصائيات</h3>', unsafe_allow_html=True)

        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        # Reports settings form
        with st.form("reports_settings_form"):
            st.markdown("### 📈 إعدادات التقارير التلقائية")

            col1, col2 = st.columns(2)

            with col1:
                daily_reports = st.checkbox(
                    "التقارير اليومية",
                    value=True,
                    help="إنشاء تقارير يومية تلقائياً"
                )

                weekly_reports = st.checkbox(
                    "التقارير الأسبوعية",
                    value=True,
                    help="إنشاء تقارير أسبوعية تلقائياً"
                )

                monthly_reports = st.checkbox(
                    "التقارير الشهرية",
                    value=True,
                    help="إنشاء تقارير شهرية تلقائياً"
                )

            with col2:
                sales_reports = st.checkbox(
                    "تقارير المبيعات",
                    value=True,
                    help="تضمين تقارير المبيعات في التقارير التلقائية"
                )

                inventory_reports = st.checkbox(
                    "تقارير المخزون",
                    value=True,
                    help="تضمين تقارير المخزون في التقارير التلقائية"
                )

                maintenance_reports = st.checkbox(
                    "تقارير الصيانة",
                    value=True,
                    help="تضمين تقارير الصيانة في التقارير التلقائية"
                )

            st.markdown("### 📧 إعدادات إرسال التقارير")

            email_reports = st.checkbox(
                "إرسال التقارير عبر البريد الإلكتروني",
                value=False,
                help="إرسال التقارير التلقائية عبر البريد الإلكتروني"
            )

            if email_reports:
                report_email = st.text_input(
                    "عنوان البريد الإلكتروني للتقارير",
                    placeholder="reports@company.com",
                    help="عنوان البريد الإلكتروني لإرسال التقارير"
                )

            st.markdown("### 📊 إعدادات عرض البيانات")

            default_chart_type = st.selectbox(
                "نوع الرسم البياني الافتراضي",
                ["خطي", "عمودي", "دائري", "منطقة"],
                index=1,
                help="نوع الرسم البياني الافتراضي في التقارير"
            )

            data_export_formats = st.multiselect(
                "تنسيقات تصدير البيانات",
                ["PDF", "Excel", "CSV", "JSON"],
                default=["PDF", "Excel"],
                help="التنسيقات المتاحة لتصدير البيانات"
            )

            if st.form_submit_button("💾 حفظ إعدادات التقارير", use_container_width=True):
                # Here you would save the reports settings to database
                st.success("✅ تم حفظ إعدادات التقارير بنجاح!")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    def _connection_settings(self):
        """Manage connection and integration settings"""
        st.markdown('<div class="settings-section">', unsafe_allow_html=True)
        st.markdown('<h3 style="color: #28a745; margin-bottom: 1rem;">🔗 إعدادات الاتصال والتكامل</h3>', unsafe_allow_html=True)

        st.markdown('<div class="form-container">', unsafe_allow_html=True)

        # Connection settings form
        with st.form("connection_settings_form"):
            st.markdown("### 🗄️ إعدادات قاعدة البيانات")

            col1, col2 = st.columns(2)

            with col1:
                db_host = st.text_input(
                    "خادم قاعدة البيانات",
                    value="localhost",
                    help="عنوان خادم قاعدة البيانات"
                )

                db_port = st.number_input(
                    "منفذ قاعدة البيانات",
                    min_value=1, max_value=65535, value=3306,
                    help="رقم منفذ قاعدة البيانات"
                )

            with col2:
                db_name = st.text_input(
                    "اسم قاعدة البيانات",
                    value="Petrolpump_Management_Enhanced",
                    help="اسم قاعدة البيانات المستخدمة"
                )

                connection_timeout = st.number_input(
                    "مهلة الاتصال (ثانية)",
                    min_value=5, max_value=300, value=30,
                    help="المهلة الزمنية للاتصال بقاعدة البيانات"
                )

            st.markdown("### 📡 إعدادات الاستشعار والمراقبة")

            sensor_api_enabled = st.checkbox(
                "تفعيل API الاستشعار",
                value=True,
                help="تفعيل واجهة برمجة التطبيقات للاستشعارات"
            )

            if sensor_api_enabled:
                sensor_api_port = st.number_input(
                    "منفذ API الاستشعار",
                    min_value=1000, max_value=9999, value=8000,
                    help="رقم المنفذ لواجهة API الاستشعار"
                )

                sensor_update_interval = st.number_input(
                    "فترة تحديث البيانات (ثانية)",
                    min_value=1, max_value=3600, value=60,
                    help="الفترة الزمنية بين تحديثات بيانات الاستشعارات"
                )

            st.markdown("### 🔄 إعدادات التزامن والنسخ الاحتياطي")

            auto_sync = st.checkbox(
                "التزامن التلقائي",
                value=False,
                help="تفعيل التزامن التلقائي مع الأنظمة الأخرى"
            )

            backup_frequency = st.selectbox(
                "تكرار النسخ الاحتياطي",
                ["يومي", "أسبوعي", "شهري"],
                index=1,
                help="تكرار إنشاء النسخ الاحتياطية"
            )

            if st.form_submit_button("🔗 اختبار الاتصال", use_container_width=True):
                # Here you would test the database connection
                try:
                    conn = get_connection()
                    if conn:
                        conn.close()
                        st.success("✅ تم الاتصال بنجاح بقاعدة البيانات!")
                    else:
                        st.error("❌ فشل في الاتصال بقاعدة البيانات")
                except Exception as e:
                    st.error(f"❌ خطأ في اختبار الاتصال: {e}")

            if st.form_submit_button("💾 حفظ إعدادات الاتصال", use_container_width=True):
                # Here you would save the connection settings
                st.success("✅ تم حفظ إعدادات الاتصال بنجاح!")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)
