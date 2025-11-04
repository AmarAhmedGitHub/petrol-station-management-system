import streamlit as st
import pandas as pd
from datetime import datetime, time, timedelta
from core.database_enhanced import (
    add_shift, get_all_shifts, assign_employee_to_shift,
    get_employee_assignments, get_all_employees, get_all_stations
)
from core.safe_html import get_safe_html

def shift_management():
    """Advanced shift management interface with modern design"""
    safe_html = get_safe_html()

    # Enhanced header
    safe_html.display_section_header(
        "إدارة المناوبات والدوام",
        "نظام متطور لإدارة فترات العمل والمناوبات مع جدولة ذكية",
        "🕐"
    )

    # Create tabs for different shift management aspects
    tab1, tab2, tab3, tab4 = st.tabs([
        "➕ إنشاء مناوبات",
        "👥 تعيين الموظفين",
        "📅 جدولة المناوبات",
        "📊 إحصائيات الدوام"
    ])

    with tab1:
        create_shifts_tab()

    with tab2:
        assign_employees_tab()

    with tab3:
        schedule_shifts_tab()

    with tab4:
        shift_statistics_tab()


def create_shifts_tab():
    """Create and manage shift definitions"""
    st.markdown("### 🆕 إنشاء مناوبة جديدة")

    # Quick shift templates
    templates = {
        "المناوبة الصباحية": {"start": "06:00", "end": "14:00"},
        "المناوبة المسائية": {"start": "14:00", "end": "22:00"},
        "المناوبة الليلية": {"start": "22:00", "end": "06:00"},
        "مناوبة 12 ساعة": {"start": "06:00", "end": "18:00"},
        "مناوبة قصيرة": {"start": "09:00", "end": "17:00"}
    }

    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### 📋 النماذج الجاهزة")
        selected_template = st.selectbox(
            "اختر نموذج مناوبة",
            list(templates.keys()),
            help="اختر نموذج جاهز أو قم بتخصيص المناوبة يدوياً"
        )

        if selected_template:
            template_data = templates[selected_template]
            default_start = datetime.strptime(template_data["start"], "%H:%M").time()
            default_end = datetime.strptime(template_data["end"], "%H:%M").time()
        else:
            default_start = time(9, 0)
            default_end = time(17, 0)

    with col2:
        st.markdown("#### ⚙️ إعدادات المناوبة")

        with st.form("create_shift_form"):
            shift_name = st.text_input(
                "اسم المناوبة",
                value=selected_template if selected_template else "",
                help="أدخل اسم واضح للمناوبة"
            )

            col_a, col_b = st.columns(2)
            with col_a:
                start_time = st.time_input(
                    "وقت البداية",
                    value=default_start,
                    help="وقت بدء المناوبة"
                )

            with col_b:
                end_time = st.time_input(
                    "وقت النهاية",
                    value=default_end,
                    help="وقت انتهاء المناوبة"
                )

            description = st.text_area(
                "الوصف (اختياري)",
                height=100,
                help="وصف تفصيلي للمناوبة والمهام المطلوبة"
            )

            # Calculate duration
            if start_time and end_time:
                # Convert times to datetime objects for calculation
                start_dt = datetime.combine(datetime.today(), start_time) if isinstance(start_time, time) else datetime.combine(datetime.today(), time.fromisoformat(str(start_time)))
                end_dt = datetime.combine(datetime.today(), end_time) if isinstance(end_time, time) else datetime.combine(datetime.today(), time.fromisoformat(str(end_time)))

                # Handle overnight shifts
                if end_dt <= start_dt:
                    end_dt = datetime.combine(datetime.today() + timedelta(days=1), end_time)

                duration = end_dt - start_dt
                hours = duration.total_seconds() / 3600
                st.info(f"⏱️ مدة المناوبة: {hours:.1f} ساعة")

            submitted = st.form_submit_button("💾 حفظ المناوبة", use_container_width=True)

            if submitted:
                if not shift_name:
                    st.error("❌ يرجى إدخال اسم المناوبة")
                elif start_time == end_time:
                    st.error("❌ وقت البداية والنهاية لا يمكن أن يكونا متطابقين")
                else:
                    success = add_shift(shift_name, start_time, end_time, description)
                    if success:
                        st.success(f"✅ تم إنشاء المناوبة '{shift_name}' بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ فشل في إنشاء المناوبة")

    # Display existing shifts
    st.markdown("---")
    st.markdown("### 📋 المناوبات الموجودة")

    shifts = get_all_shifts()
    if shifts:
        # Enhanced shifts display
        shifts_data = []
        for shift in shifts:
            # Convert times to datetime objects for calculation
            start_dt = datetime.combine(datetime.today(), shift[1]) if isinstance(shift[1], time) else datetime.combine(datetime.today(), time.fromisoformat(str(shift[1])))
            end_dt = datetime.combine(datetime.today(), shift[2]) if isinstance(shift[2], time) else datetime.combine(datetime.today(), time.fromisoformat(str(shift[2])))

            # Handle overnight shifts
            if end_dt <= start_dt:
                end_dt = datetime.combine(datetime.today() + timedelta(days=1), shift[2])

            duration = end_dt - start_dt

            shifts_data.append({
                'المعرف': shift[0],
                'اسم المناوبة': shift[1],
                'وقت البداية': shift[2].strftime('%H:%M'),
                'وقت النهاية': shift[3].strftime('%H:%M'),
                'المدة': f"{duration.total_seconds() / 3600:.1f} ساعة",
                'الوصف': shift[4] or 'لا يوجد وصف',
                'نشط': '✅' if shift[5] else '❌'
            })

        df = pd.DataFrame(shifts_data)
        st.dataframe(df, use_container_width=True)

        # Quick actions for shifts
        st.markdown("#### 🛠️ إجراءات سريعة")
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🔄 تحديث القائمة", use_container_width=True):
                st.rerun()

        with col2:
            if st.button("📊 عرض التفاصيل", use_container_width=True):
                with st.expander("تفاصيل المناوبات", expanded=True):
                    for shift in shifts_data:
                        st.markdown(f"""
                        **{shift['اسم المناوبة']}**
                        - الوقت: {shift['وقت البداية']} - {shift['وقت النهاية']}
                        - المدة: {shift['المدة']}
                        - الوصف: {shift['الوصف']}
                        ---
                        """)

        with col3:
            if st.button("📥 تصدير المناوبات", use_container_width=True):
                csv = df.to_csv(index=False, encoding='utf-8-sig')
                st.download_button(
                    label="تحميل ملف CSV",
                    data=csv,
                    file_name="shifts.csv",
                    mime="text/csv",
                    key="download_shifts"
                )
    else:
        st.info("ℹ️ لا توجد مناوبات محددة حالياً. قم بإنشاء مناوبة جديدة أولاً.")


def assign_employees_tab():
    """Assign employees to shifts and stations"""
    st.markdown("### 👥 تعيين الموظفين للمناوبات")

    # Get data
    employees = get_all_employees()
    stations = get_all_stations()
    shifts = get_all_shifts()

    if not employees or not stations or not shifts:
        st.warning("⚠️ يرجى التأكد من وجود موظفين ومحطات ومناوبات محددة")
        return

    # Assignment form
    with st.form("assign_employee_form"):
        st.markdown("#### 📝 تفاصيل التعيين")

        col1, col2, col3 = st.columns(3)

        with col1:
            # Employee selection
            employee_options = {f"{emp[2]} (ID: {emp[0]})": emp[0] for emp in employees}
            selected_employee = st.selectbox(
                "اختر الموظف",
                list(employee_options.keys()),
                help="اختر الموظف المراد تعيينه"
            )

        with col2:
            # Station selection
            station_options = {f"{st[1]} (ID: {st[0]})": st[0] for st in stations}
            selected_station = st.selectbox(
                "اختر المحطة",
                list(station_options.keys()),
                help="اختر المحطة التي سيعمل بها الموظف"
            )

        with col3:
            # Shift selection
            shift_options = {f"{sh[1]} ({sh[2].strftime('%H:%M')} - {sh[3].strftime('%H:%M')})": sh[0] for sh in shifts}
            selected_shift = st.selectbox(
                "اختر المناوبة",
                list(shift_options.keys()),
                help="اختر المناوبة المطلوبة"
            )

        # Assignment date
        assignment_date = st.date_input(
            "تاريخ التعيين",
            value=datetime.now().date(),
            help="تاريخ بدء التعيين"
        )

        # Additional notes
        notes = st.text_area(
            "ملاحظات (اختياري)",
            height=80,
            help="أي ملاحظات إضافية حول التعيين"
        )

        submitted = st.form_submit_button("🎯 تعيين الموظف", use_container_width=True)

        if submitted:
            employee_id = employee_options[selected_employee]
            station_id = station_options[selected_station]
            shift_id = shift_options[selected_shift]

            success = assign_employee_to_shift(employee_id, station_id, shift_id, assignment_date)
            if success:
                st.success(f"✅ تم تعيين الموظف {selected_employee} للمناوبة بنجاح!")
                st.rerun()
            else:
                st.error("❌ فشل في تعيين الموظف")

    # Display current assignments
    st.markdown("---")
    st.markdown("### 📋 التعيينات الحالية")

    assignments = get_employee_assignments()
    if assignments:
        assignments_data = []
        for assignment in assignments:
            assignments_data.append({
                'المعرف': assignment[0],
                'اسم الموظف': assignment[5],
                'اسم المحطة': assignment[7],
                'اسم المناوبة': assignment[9] or 'غير محدد',
                'وقت البداية': assignment[10].strftime('%H:%M') if assignment[10] else 'غير محدد',
                'وقت النهاية': assignment[11].strftime('%H:%M') if assignment[11] else 'غير محدد',
                'تاريخ التعيين': assignment[4].strftime('%Y-%m-%d'),
                'نشط': '✅' if assignment[6] else '❌'
            })

        df = pd.DataFrame(assignments_data)
        st.dataframe(df, use_container_width=True)

        # Assignment statistics
        active_assignments = len([a for a in assignments_data if a['نشط'] == '✅'])
        total_employees = len(employees)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("التعيينات النشطة", active_assignments)
        with col2:
            st.metric("إجمالي الموظفين", total_employees)
        with col3:
            coverage = (active_assignments / total_employees * 100) if total_employees > 0 else 0
            st.metric("نسبة التغطية", f"{coverage:.1f}%")
    else:
        st.info("ℹ️ لا توجد تعيينات حالية")


def schedule_shifts_tab():
    """Display shift schedule and calendar view"""
    st.markdown("### 📅 جدولة المناوبات")

    # Date range selector
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "من تاريخ",
            value=datetime.now().date(),
            help="تاريخ بدء العرض"
        )
    with col2:
        end_date = st.date_input(
            "إلى تاريخ",
            value=(datetime.now() + timedelta(days=7)).date(),
            help="تاريخ نهاية العرض"
        )

    if start_date > end_date:
        st.error("❌ تاريخ البداية يجب أن يكون قبل تاريخ النهاية")
        return

    # Get assignments for the date range
    assignments = get_employee_assignments()

    if assignments:
        # Create schedule data
        schedule_data = []
        current_date = start_date

        while current_date <= end_date:
            day_assignments = []
            for assignment in assignments:
                if assignment[4] <= current_date and assignment[6]:  # Active assignment
                    day_assignments.append({
                        'التاريخ': current_date.strftime('%Y-%m-%d'),
                        'يوم الأسبوع': current_date.strftime('%A'),
                        'الموظف': assignment[5],
                        'المحطة': assignment[7],
                        'المناوبة': assignment[9] or 'غير محدد',
                        'وقت البداية': assignment[10].strftime('%H:%M') if assignment[10] else 'غير محدد',
                        'وقت النهاية': assignment[11].strftime('%H:%M') if assignment[11] else 'غير محدد'
                    })

            if day_assignments:
                schedule_data.extend(day_assignments)
            else:
                # Add empty day
                schedule_data.append({
                    'التاريخ': current_date.strftime('%Y-%m-%d'),
                    'يوم الأسبوع': current_date.strftime('%A'),
                    'الموظف': 'لا يوجد تعيين',
                    'المحطة': '-',
                    'المناوبة': '-',
                    'وقت البداية': '-',
                    'وقت النهاية': '-'
                })

            current_date += timedelta(days=1)

        df_schedule = pd.DataFrame(schedule_data)
        st.dataframe(df_schedule, use_container_width=True)

        # Calendar view
        st.markdown("#### 📊 عرض التقويم")

        # Group by date for calendar view
        calendar_data = {}
        for _, row in df_schedule.iterrows():
            date = row['التاريخ']
            if date not in calendar_data:
                calendar_data[date] = []
            if row['الموظف'] != 'لا يوجد تعيين':
                calendar_data[date].append(f"{row['الموظف']} ({row['المناوبة']})")

        # Display calendar
        for date, employees in calendar_data.items():
            day_name = datetime.strptime(date, '%Y-%m-%d').strftime('%A')
            with st.expander(f"📅 {date} - {day_name}", expanded=False):
                if employees:
                    for employee in employees:
                        st.markdown(f"• {employee}")
                else:
                    st.info("لا توجد تعيينات لهذا اليوم")
    else:
        st.info("ℹ️ لا توجد تعيينات لعرضها في الجدولة")


def shift_statistics_tab():
    """Display shift statistics and analytics"""
    st.markdown("### 📊 إحصائيات المناوبات والدوام")

    # Get data
    assignments = get_employee_assignments()
    shifts = get_all_shifts()
    employees = get_all_employees()

    if not assignments or not shifts or not employees:
        st.info("ℹ️ لا توجد بيانات كافية لعرض الإحصائيات")
        return

    # Statistics cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_assignments = len([a for a in assignments if a[6]])  # Active assignments
        st.metric("التعيينات النشطة", total_assignments)

    with col2:
        total_shifts = len(shifts)
        st.metric("إجمالي المناوبات", total_shifts)

    with col3:
        total_employees = len(employees)
        st.metric("إجمالي الموظفين", total_employees)

    with col4:
        coverage = (total_assignments / total_employees * 100) if total_employees > 0 else 0
        st.metric("نسبة التغطية", f"{coverage:.1f}%")

    # Shift distribution
    st.markdown("#### 🕐 توزيع المناوبات")

    shift_usage = {}
    for assignment in assignments:
        if assignment[6] and assignment[9]:  # Active assignment with shift name
            shift_name = assignment[9]
            shift_usage[shift_name] = shift_usage.get(shift_name, 0) + 1

    if shift_usage:
        shift_df = pd.DataFrame(list(shift_usage.items()), columns=['المناوبة', 'عدد التعيينات'])
        st.bar_chart(shift_df.set_index('المناوبة'))
    else:
        st.info("لا توجد بيانات توزيع للمناوبات")

    # Station distribution
    st.markdown("#### 🏭 توزيع الموظفين حسب المحطة")

    station_usage = {}
    for assignment in assignments:
        if assignment[6]:  # Active assignment
            station_name = assignment[7]
            station_usage[station_name] = station_usage.get(station_name, 0) + 1

    if station_usage:
        station_df = pd.DataFrame(list(station_usage.items()), columns=['المحطة', 'عدد الموظفين'])
        st.bar_chart(station_df.set_index('المحطة'))
    else:
        st.info("لا توجد بيانات توزيع للمحطات")

    # Detailed statistics table
    st.markdown("#### 📋 تفاصيل الإحصائيات")

    stats_data = []

    # Calculate shift durations
    for shift in shifts:
        # Convert times to datetime objects for calculation
        start_dt = datetime.combine(datetime.today(), shift[2]) if isinstance(shift[2], time) else datetime.combine(datetime.today(), time.fromisoformat(str(shift[2])))
        end_dt = datetime.combine(datetime.today(), shift[3]) if isinstance(shift[3], time) else datetime.combine(datetime.today(), time.fromisoformat(str(shift[3])))

        # Handle overnight shifts
        if end_dt <= start_dt:
            end_dt = datetime.combine(datetime.today() + timedelta(days=1), shift[3])

        duration = end_dt - start_dt
        hours = duration.total_seconds() / 3600
        usage_count = shift_usage.get(shift[1], 0)

        stats_data.append({
            'اسم المناوبة': shift[1],
            'وقت البداية': shift[2].strftime('%H:%M'),
            'وقت النهاية': shift[3].strftime('%H:%M'),
            'المدة (ساعة)': f"{hours:.1f}",
            'عدد التعيينات': usage_count,
            'نسبة الاستخدام': f"{(usage_count / total_assignments * 100):.1f}%" if total_assignments > 0 else "0%"
        })

    if stats_data:
        stats_df = pd.DataFrame(stats_data)
        st.dataframe(stats_df, use_container_width=True)

        # Export functionality
        if st.button("📥 تصدير الإحصائيات", key="export_shift_stats"):
            csv = stats_df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="تحميل ملف CSV",
                data=csv,
                file_name="shift_statistics.csv",
                mime="text/csv",
                key="download_shift_stats"
            )


def main():
    """Main shift management function"""
    shift_management()


if __name__ == "__main__":
    main()