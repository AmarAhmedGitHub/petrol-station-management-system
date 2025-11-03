import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_fuel_types,
    get_all_employees, get_all_invoices, get_all_supplies, get_dashboard_stats,
    get_pump_directory, add_pump_assignment, update_pump_assignment, delete_pump_assignment,
    record_shift_reading, get_shift_reading
)
from core.automation import get_automation_settings, update_automation_settings, manual_reconciliation, start_scheduler, get_real_sensor_reading, reconcile_shift
from core.sensor_api import get_sensor_api, initialize_sensor_api
import os
from dotenv import load_dotenv
import json

def main():
    """System interface main function"""
    st.markdown("""
        <style>
        .system-header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 2rem;
            border-radius: 15px;
            text-align: center;
            margin-bottom: 2rem;
        }
        .system-content {
            background: white;
            padding: 2rem;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="system-header">', unsafe_allow_html=True)
    st.markdown('<h1>🔧 واجهة النظام</h1>', unsafe_allow_html=True)
    st.markdown('<p>إدارة إعدادات النظام والأتمتة</p>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="system-content">', unsafe_allow_html=True)

    # System settings tabs
    tab1, tab2, tab3, tab4 = st.tabs(["⚙️ إعدادات الأتمتة", "📊 إحصائيات النظام", "🔧 الصيانة", "👥 تعيين الموظفين للمضخات"])

    with tab1:
        st.subheader("إعدادات الأتمتة")
        automation_settings = get_automation_settings()

        # Display and edit automation settings via a form
        settings_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'core', 'automation_settings.json'))

        if automation_settings:
            st.info("الإعدادات الحالية محملة من ملف الإعدادات")
        else:
            st.info("لا توجد إعدادات أتمتة محددة - يمكنك إنشاء واحدة أدناه")

        with st.form(key='automation_settings_form'):
            recon_interval = st.number_input("فاصل التسوية بالساعات (RECONCILIATION_INTERVAL_HOURS)",
                                             value=float(automation_settings.get('RECONCILIATION_INTERVAL_HOURS', 7.5)),
                                             min_value=0.1, step=0.1)
            automation_enabled = st.checkbox("تمكين الأتمتة (AUTOMATION_ENABLED)",
                                             value=bool(automation_settings.get('AUTOMATION_ENABLED', True)))
            fallback_to_mock = st.checkbox("الرجوع إلى محاكاة الحساسات عند الفشل (FALLBACK_TO_MOCK)",
                                           value=bool(automation_settings.get('FALLBACK_TO_MOCK', True)))

            submit = st.form_submit_button("حفظ إعدادات الأتمتة")

            if submit:
                new_settings = {
                    'RECONCILIATION_INTERVAL_HOURS': float(recon_interval),
                    'AUTOMATION_ENABLED': bool(automation_enabled),
                    'FALLBACK_TO_MOCK': bool(fallback_to_mock)
                }
                ok = update_automation_settings(new_settings)
                if ok:
                    st.success("تم حفظ إعدادات الأتمتة بنجاح")
                    # Refresh local copy
                    automation_settings = get_automation_settings()
                else:
                    st.error("فشل في حفظ إعدادات الأتمتة - تحقق من أذونات الكتابة")

        st.markdown("---")

        # Action buttons: test sensors, manual reconciliation, reinitialize API/scheduler
        col_a, col_b, col_c = st.columns(3)

        with col_a:
            if st.button("🔌 اختبار اتصال الحساسات"):
                try:
                    sensor_api = get_sensor_api()
                    pts2_ok = sensor_api.test_connection('PTS2')
                    atg_ok = sensor_api.test_connection('ATG')
                    msg = f"PTS2: {'✅' if pts2_ok else '❌'} -- ATG: {'✅' if atg_ok else '❌'}"
                    st.info(msg)
                except Exception as e:
                    st.error(f"خطأ أثناء اختبار الحساسات: {e}")

        with col_b:
            if st.button("🔁 تشغيل تسوية يدوية الآن"):
                try:
                    manual_reconciliation()
                    st.success("تم تشغيل التسوية يدوياً")
                except Exception as e:
                    st.error(f"فشل تشغيل التسوية اليدوية: {e}")

        with col_c:
            if st.button("🔄 إعادة تهيئة واجهة الحساسات وإعادة تشغيل المجدول"):
                try:
                    initialize_sensor_api()
                    # Restart scheduler safely
                    if 'scheduler' in st.session_state and st.session_state['scheduler']:
                        try:
                            st.session_state['scheduler'].shutdown(wait=False)
                        except Exception:
                            pass
                    sch = start_scheduler()
                    st.session_state['scheduler'] = sch
                    st.success("تمت إعادة التهيئة وإعادة تشغيل المجدول")
                except Exception as e:
                    st.error(f"فشل في إعادة التهيئة: {e}")

        st.markdown("---")

        # Show path and manual edit instructions
        with st.expander("📁 معلومات ملف الإعدادات وتحرير يدوي"):
            st.write("مسار ملف الإعدادات المتوقع:")
            st.code(settings_path)
            st.write("مثال محتوى JSON لإعدادات الأتمتة:")
            example = {
                "RECONCILIATION_INTERVAL_HOURS": 7.5,
                "AUTOMATION_ENABLED": True,
                "FALLBACK_TO_MOCK": True
            }
            st.code(json.dumps(example, ensure_ascii=False, indent=4))
            st.markdown(
                "للتعديل برمجياً يمكنك تشغيل هذا في بايثون ضمن بيئة المشروع:\n"
                "```python\nfrom core.automation import update_automation_settings\n"
                "update_automation_settings({\n    'RECONCILIATION_INTERVAL_HOURS': 6,\n    'AUTOMATION_ENABLED': True,\n    'FALLBACK_TO_MOCK': False\n})\n```"
            )

    with tab2:
        st.subheader("إحصائيات النظام")
        stats = get_dashboard_stats()

        if stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("إجمالي المحطات", stats.get('total_stations', 0))
            with col2:
                st.metric("إجمالي الطرمبات", stats.get('total_pumps', 0))
            with col3:
                st.metric("إجمالي الخزانات", stats.get('total_tanks', 0))
            with col4:
                st.metric("إجمالي الموظفين", stats.get('total_employees', 0))
        else:
            st.info("لا توجد إحصائيات متاحة")

    with tab3:
        st.subheader("أدوات الصيانة")
        st.info("أدوات الصيانة ستكون متاحة قريباً")

    with tab4:
        st.subheader("تعيين الموظفين للمضخات والخزانات")

        # Load reference data
        pumps = get_all_pumps() or []
        pumps_map = {p[0]: p for p in pumps}  # assuming Pump_ID is first column

        stations = get_all_stations() or []
        stations_map = {s[0]: s for s in stations}

        employees = get_all_employees() or []
        employees_map = {e[0]: e for e in employees}

        tanks = get_all_tanks() or []
        tanks_map = {t[0]: t for t in tanks}

        fuels = get_all_fuel_types() or []
        fuels_map = {f[0]: f for f in fuels}

        # Show current directory
        st.markdown("### الدليل الحالي للمضخات (Pump Directory)")
        directory = get_pump_directory() or []
        if directory:
            df = pd.DataFrame(directory, columns=["Directory_ID", "Pump_ID", "Station_ID", "Employee_ID", "Tank_ID", "FuelType_ID", "Status", "Last_Updated"])
            st.dataframe(df, use_container_width=True)
        else:
            st.info("لا توجد تعيينات حالياً")

        st.markdown("---")

        st.markdown("### إضافة تعيين جديد")
        with st.form(key='add_pump_assignment_form'):
            col1, col2 = st.columns(2)
            pump_id = col1.selectbox("اختر المضخة (Pump)", options=[p[0] for p in pumps], format_func=lambda x: f"{x}") if pumps else col1.text_input("رقم المضخة (Pump_ID)")
            station_id = col2.selectbox("اختر المحطة (Station)", options=[s[0] for s in stations], format_func=lambda x: f"{x}") if stations else col2.text_input("Station_ID")
            employee_id = st.selectbox("اختر الموظف (Employee)", options=[e[0] for e in employees], format_func=lambda x: f"{x} - {employees_map[x][1] if x in employees_map else ''}") if employees else st.text_input("Employee_ID")
            tank_id = st.selectbox("اختر الخزان (Tank)", options=[t[0] for t in tanks], format_func=lambda x: f"{x}") if tanks else st.text_input("Tank_ID")
            fueltype_id = st.selectbox("اختر نوع الوقود (FuelType)", options=[f[0] for f in fuels], format_func=lambda x: f"{x}") if fuels else st.text_input("FuelType_ID")
            add_sub = st.form_submit_button("إضافة التعيين")

            if add_sub:
                ok = add_pump_assignment(pump_id, station_id, employee_id, tank_id, fueltype_id)
                if ok:
                    st.success("تمت إضافة التعيين بنجاح")
                else:
                    st.error("فشل في إضافة التعيين - تحقق من السجلات")

        st.markdown("---")

        st.markdown("### تعديل / حذف تعيين موجود")
        if directory:
            dir_map = {str(d[0]): d for d in directory}
            sel = st.selectbox("اختر السجل للتعديل", options=[str(d[0]) for d in directory], format_func=lambda x: f"{x} - {dir_map[x][1]} / Emp:{dir_map[x][3]}")
            sel_entry = dir_map[sel]

            with st.form(key='update_pump_assignment_form'):
                new_employee = st.selectbox("الموظف الجديد", options=[e[0] for e in employees], index=0)
                new_tank = st.selectbox("الخزان الجديد", options=[t[0] for t in tanks], index=0)
                new_fuel = st.selectbox("نوع الوقود الجديد", options=[f[0] for f in fuels], index=0)
                new_status = st.selectbox("الحالة", options=['Active','Inactive'], index=0)
                upd = st.form_submit_button("تحديث التعيين")
                if upd:
                    ok = update_pump_assignment(int(sel), Employee_ID=new_employee, Tank_ID=new_tank, FuelType_ID=new_fuel, Status=new_status)
                    if ok:
                        st.success("تم تحديث التعيين")
                    else:
                        st.error("فشل في تحديث التعيين")

            if st.button("حذف التعيين المختار"):
                ok = delete_pump_assignment(int(sel))
                if ok:
                    st.success("تم حذف التعيين")
                else:
                    st.error("فشل في حذف التعيين")
            # Start / End shift controls for selected directory
            st.markdown("---")
            st.markdown("### بدء / إنهاء المناوبة (تسجيل قراءات البداية والنهاية)")
            st.write("اختر السجل ثم اضغط 'بدء' لتسجيل قراءة baseline، و'إنهاء' لتسجيل نهاية المناوبة وتشغيل التسوية لهذا السجل.")

            try:
                sel_dir_id = int(sel)
                sel_entry = dir_map[sel]
                sel_pump = sel_entry[1]
                sel_employee = sel_entry[3]
                sel_tank = sel_entry[4]
            except Exception:
                sel_dir_id = None
                sel_pump = None
                sel_employee = None
                sel_tank = None

            shift_id_input = st.text_input("معرف المناوبة (Shift ID) - اتركه فارغًا لتوليد قيمة تلقائية")
            if not shift_id_input:
                auto_shift_id = datetime.now().strftime("%Y%m%d%H%M%S")
            else:
                auto_shift_id = shift_id_input

            col_start, col_end = st.columns(2)
            with col_start:
                if st.button("▶️ بدء المناوبة (تسجيل baseline)", key=f"start_shift_{sel}"):
                    if not sel_dir_id or not sel_employee or not sel_tank:
                        st.error("لا يمكن بدء المناوبة: سجل غير مكتمل أو لم يُحدد")
                    else:
                        try:
                            level = get_real_sensor_reading(sel_tank, sel_pump)
                            ok = record_shift_reading(sel_employee, auto_shift_id, sel_dir_id, sel_pump, sel_tank, 'baseline', level, notes='Started shift via UI')
                            if ok:
                                st.success(f"تم تسجيل قراءة البداية للمناوبة {auto_shift_id}: {level:.2f} L")
                            else:
                                st.error("فشل في تسجيل قراءة البداية")
                        except Exception as e:
                            st.error(f"خطأ أثناء تسجيل قراءة البداية: {e}")

            with col_end:
                if st.button("⏹️ انهاء المناوبة (تسجيل end وتشغيل التسوية)", key=f"end_shift_{sel}"):
                    if not sel_dir_id or not sel_employee or not sel_tank:
                        st.error("لا يمكن إنهاء المناوبة: سجل غير مكتمل أو لم يُحدد")
                    else:
                        try:
                            level = get_real_sensor_reading(sel_tank, sel_pump)
                            ok = record_shift_reading(sel_employee, auto_shift_id, sel_dir_id, sel_pump, sel_tank, 'end', level, notes='Ended shift via UI')
                            if ok:
                                st.success(f"تم تسجيل قراءة النهاية للمناوبة {auto_shift_id}: {level:.2f} L")
                                reconciled = reconcile_shift(sel_employee, auto_shift_id, sel_dir_id)
                                if reconciled:
                                    st.success("تمت تسوية المناوبة وإنشاء قيد الدين (إن وُجد)")
                                else:
                                    st.info("التسوية لم تُنشئ دينًا — تحقق من القراءات أو سجل المهام.")
                            else:
                                st.error("فشل في تسجيل قراءة النهاية")
                        except Exception as e:
                            st.error(f"خطأ أثناء تسجيل قراءة النهاية أو التسوية: {e}")
        else:
            st.info("لا توجد سجلات لحذفها أو تعديلها")

    st.markdown('</div>', unsafe_allow_html=True)
