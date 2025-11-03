import streamlit as st
import pandas as pd
from core.database_enhanced import (
    get_all_stations, get_all_pumps, get_all_tanks, get_all_employees,
    get_all_fuel_types, update_pump_assignment, update_employee_station,
    get_connection
)

def main():
    """Main assignments management page"""
    st.title("🔗 إدارة الربط والتعيينات")

    # Create tabs for different assignment types
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 تعيين الموظفين للمضخات",
        "🗂️ ربط المضخات بالخزانات",
        "🏭 تعيين الموظفين للمحطات",
        "📊 تقارير التعيينات"
    ])

    with tab1:
        employee_pump_assignments()

    with tab2:
        pump_tank_assignments()

    with tab3:
        employee_station_assignments()

    with tab4:
        assignments_reports()

def employee_pump_assignments():
    """Manage employee to pump assignments with enhanced logic and workflow"""
    safe_html = get_safe_html()

    # Enhanced header
    safe_html.display_section_header(
        "تعيين الموظفين للمضخات",
        "ربط منطقي وذكي بين الموظفين والمضخات مع مراعاة التوافق والكفاءة",
        "👥"
    )

    # Get data
    pumps = get_all_pumps()
    employees = get_all_employees()
    stations = get_all_stations()

    if not pumps or not employees:
        safe_html.display_info_alert("يرجى إضافة مضخات وموظفين أولاً", "warning", "⚠️")
        return

    # Smart assignment logic
    assignment_logic = SmartAssignmentLogic(pumps, employees, stations)

    # Create tabs for different assignment approaches
    tab1, tab2, tab3 = st.tabs([
        "🎯 التعيين الذكي",
        "🔧 التعيين اليدوي",
        "📊 عرض التعيينات"
    ])

    with tab1:
        smart_employee_pump_assignment(assignment_logic)

    with tab2:
        manual_employee_pump_assignment(assignment_logic)

    with tab3:
        view_employee_pump_assignments(assignment_logic)


class SmartAssignmentLogic:
    """Smart assignment logic for employees and pumps"""

    def __init__(self, pumps, employees, stations):
        self.pumps = pumps
        self.employees = employees
        self.stations = stations

    def get_available_pumps(self):
        """Get pumps without assigned employees"""
        return [p for p in self.pumps if not p[17]]  # Employee_Name is None

    def get_available_employees(self, station_filter=None):
        """Get available pump operators with optional station filter"""
        operators = [e for e in self.employees if e[4] in ["عامل مضخة", "مشرف", "مدير محطة"]]

        if station_filter:
            operators = [e for e in operators if e[1] == station_filter]  # Station_ID match

        return operators

    def get_compatibility_score(self, employee, pump):
        """Calculate compatibility score between employee and pump"""
        score = 0

        # Station match bonus
        if employee[1] == pump[1]:  # Same station
            score += 50

        # Designation compatibility
        if employee[4] == "مدير محطة":
            score += 30  # Managers can operate any pump
        elif employee[4] == "مشرف":
            score += 20  # Supervisors have good compatibility
        elif employee[4] == "عامل مضخة":
            score += 15  # Basic pump operators

        # Experience factor (simulated)
        # In real implementation, this would be based on actual experience data
        score += 10  # Base experience

        return min(score, 100)  # Cap at 100

    def suggest_assignments(self, max_suggestions=5):
        """Suggest optimal employee-pump assignments"""
        available_pumps = self.get_available_pumps()
        available_employees = self.get_available_employees()

        suggestions = []

        for pump in available_pumps:
            pump_suggestions = []

            for employee in available_employees:
                score = self.get_compatibility_score(employee, pump)
                pump_suggestions.append({
                    'employee': employee,
                    'pump': pump,
                    'score': score,
                    'reason': self.get_assignment_reason(employee, pump, score)
                })

            # Sort by score and take top suggestions
            pump_suggestions.sort(key=lambda x: x['score'], reverse=True)
            suggestions.extend(pump_suggestions[:3])  # Top 3 per pump

        # Sort all suggestions by score
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:max_suggestions]

    def get_assignment_reason(self, employee, pump, score):
        """Get human-readable reason for assignment suggestion"""
        reasons = []

        if employee[1] == pump[1]:  # Same station
            reasons.append("نفس المحطة")

        if employee[4] == "مدير محطة":
            reasons.append("صلاحية إدارية")
        elif employee[4] == "مشرف":
            reasons.append("خبرة إشرافية")

        if score >= 80:
            reasons.append("توافق ممتاز")
        elif score >= 60:
            reasons.append("توافق جيد")
        elif score >= 40:
            reasons.append("توافق مقبول")

        return " • ".join(reasons) if reasons else "توافق أساسي"


def smart_employee_pump_assignment(assignment_logic):
    """Smart assignment with AI-powered suggestions"""
    st.markdown("### 🧠 التعيين الذكي بالذكاء الاصطناعي")

    # Get smart suggestions
    suggestions = assignment_logic.suggest_assignments()

    if not suggestions:
        safe_html.display_info_alert("لا توجد اقتراحات متاحة حالياً", "info", "🤖")
        return

    st.markdown("#### 💡 أفضل الاقتراحات:")

    for i, suggestion in enumerate(suggestions):
        employee = suggestion['employee']
        pump = suggestion['pump']
        score = suggestion['score']

        # Enhanced suggestion card
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

        with col1:
            st.markdown(f"**👤 {employee[2]}**")  # Employee name
            st.caption(f"منصب: {employee[4]}")

        with col2:
            st.markdown(f"**⛽ {pump[2]}**")  # Pump name
            st.caption(f"محطة: {pump[14]}")

        with col3:
            # Score indicator
            if score >= 80:
                st.success(f"🎯 {score}%")
            elif score >= 60:
                st.warning(f"👍 {score}%")
            else:
                st.info(f"📊 {score}%")

        with col4:
            if st.button("تعيين", key=f"smart_assign_{i}", use_container_width=True):
                if update_pump_assignment(pump[0], employee[0]):
                    safe_html.display_info_alert(
                        f"تم تعيين {employee[2]} للمضخة {pump[2]} بنجاح!",
                        "success",
                        "✅"
                    )
                    st.rerun()
                else:
                    safe_html.display_info_alert("فشل في التعيين", "error", "❌")

        st.caption(f"📋 {suggestion['reason']}")
        st.markdown("---")


def manual_employee_pump_assignment(assignment_logic):
    """Manual assignment with enhanced validation"""
    st.markdown("### 🔧 التعيين اليدوي")

    # Create columns for assign/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### ➕ تعيين موظف لمضخة")

        with st.form("assign_employee_pump_form"):
            # Station filter
            station_options = {f"{s[1]} ({s[6]})": s[0] for s in assignment_logic.stations}
            selected_station = st.selectbox(
                "🏭 اختر المحطة أولاً",
                [""] + list(station_options.keys()),
                help="تصفية المضخات والموظفين حسب المحطة"
            )

            station_id = station_options.get(selected_station, None) if selected_station else None

            # Get available pumps for selected station
            available_pumps = assignment_logic.get_available_pumps()
            if station_id:
                available_pumps = [p for p in available_pumps if p[1] == station_id]

            if available_pumps:
                pump_options = {f"{p[2]} (رقم: {p[3]})": p[0] for p in available_pumps}
                selected_pump = st.selectbox(
                    "⛽ اختر المضخة",
                    list(pump_options.keys()),
                    help="اختر المضخة التي تريد تعيين موظف لها"
                )

                # Get available employees for selected station
                available_employees = assignment_logic.get_available_employees(station_id)

                if available_employees:
                    employee_options = {f"{e[2]} ({e[4]})": e[0] for e in available_employees}

                    selected_employee = st.selectbox(
                        "👤 اختر الموظف",
                        list(employee_options.keys()),
                        help="اختر الموظف الذي سيعمل على هذه المضخة"
                    )

                    # Show compatibility score
                    pump_id = pump_options[selected_pump]
                    employee_id = employee_options[selected_employee]

                    pump_data = next(p for p in available_pumps if p[0] == pump_id)
                    employee_data = next(e for e in available_employees if e[0] == employee_id)

                    compatibility = assignment_logic.get_compatibility_score(employee_data, pump_data)

                    if compatibility >= 70:
                        st.success(f"🎯 توافق ممتاز: {compatibility}%")
                    elif compatibility >= 50:
                        st.warning(f"👍 توافق جيد: {compatibility}%")
                    else:
                        st.info(f"📊 توافق أساسي: {compatibility}%")

                    if st.form_submit_button("✅ تأكيد التعيين", use_container_width=True):
                        if update_pump_assignment(pump_id, employee_id):
                            safe_html.display_info_alert(
                                f"تم تعيين {employee_data[2]} للمضخة {pump_data[2]} بنجاح!",
                                "success",
                                "✅"
                            )
                            st.rerun()
                        else:
                            safe_html.display_info_alert("فشل في التعيين", "error", "❌")
                else:
                    st.warning("⚠️ لا يوجد موظفون متاحون في هذه المحطة")
            else:
                safe_html.display_info_alert("جميع المضخات معينة لموظفين بالفعل", "info", "ℹ️")

    with col2:
        st.markdown("#### 📋 المضخات المعينة")

        # Show pumps with assigned employees
        assigned_pumps = [p for p in assignment_logic.pumps if p[17]]  # Has Employee_Name

        if assigned_pumps:
            # Enhanced data display
            assignment_data = []
            for pump in assigned_pumps:
                employee = next((e for e in assignment_logic.employees if e[0] == pump[7]), None)
                station = next((s for s in assignment_logic.stations if s[0] == pump[1]), None)

                assignment_data.append({
                    'المضخة': pump[2],
                    'المحطة': station[1] if station else 'غير محدد',
                    'الموظف': pump[17],
                    'المنصب': employee[4] if employee else 'غير محدد',
                    'نوع الوقود': pump[15],
                    'التوافق': assignment_logic.get_compatibility_score(employee, pump) if employee else 0
                })

            df = pd.DataFrame(assignment_data)
            st.dataframe(df, use_container_width=True)

            # Enhanced summary with metrics
            metrics = [
                {"icon": "⛽", "value": str(len(assigned_pumps)), "label": "المضخات المعينة", "color": "#10b981"},
                {"icon": "👥", "value": str(len(assignment_logic.pumps) - len(assigned_pumps)), "label": "المضخات المتاحة", "color": "#f59e0b"},
                {"icon": "🎯", "value": f"{len(set(p[17] for p in assigned_pumps if p[17]))}", "label": "الموظفون المعينون", "color": "#3b82f6"},
                {"icon": "📊", "value": f"{sum(assignment_logic.get_compatibility_score(next((e for e in assignment_logic.employees if e[0] == p[7]), None), p) for p in assigned_pumps if p[17]) // len([p for p in assigned_pumps if p[17]]):.0f}%", "label": "متوسط التوافق", "color": "#8b5cf6"}
            ]

            safe_html.display_metric_grid(metrics)
        else:
            safe_html.display_info_alert("لا توجد مضخات معينة لموظفين", "info", "📭")


def view_employee_pump_assignments(assignment_logic):
    """View all employee-pump assignments with analytics"""
    st.markdown("### 📊 تحليل التعيينات")

    assigned_pumps = [p for p in assignment_logic.pumps if p[17]]

    if not assigned_pumps:
        safe_html.display_info_alert("لا توجد تعيينات حالياً", "info", "📊")
        return

    # Assignment analytics
    st.markdown("#### 📈 إحصائيات التعيينات")

    # By station
    station_assignments = {}
    for pump in assigned_pumps:
        station_name = pump[14]  # Station_Name
        if station_name:
            station_assignments[station_name] = station_assignments.get(station_name, 0) + 1

    if station_assignments:
        st.subheader("🏭 التعيينات حسب المحطة")
        station_df = pd.DataFrame(list(station_assignments.items()), columns=['المحطة', 'عدد التعيينات'])
        st.bar_chart(station_df.set_index('المحطة'))

    # By employee designation
    designation_assignments = {}
    for pump in assigned_pumps:
        employee_id = pump[7]
        employee = next((e for e in assignment_logic.employees if e[0] == employee_id), None)
        if employee:
            designation = employee[4]
            designation_assignments[designation] = designation_assignments.get(designation, 0) + 1

    if designation_assignments:
        st.subheader("👔 التعيينات حسب المنصب")
        designation_df = pd.DataFrame(list(designation_assignments.items()), columns=['المنصب', 'عدد التعيينات'])
        st.bar_chart(designation_df.set_index('المنصب'))

    # Detailed assignment table
    st.markdown("#### 📋 تفاصيل التعيينات")

    detailed_data = []
    for pump in assigned_pumps:
        employee = next((e for e in assignment_logic.employees if e[0] == pump[7]), None)
        if employee:
            detailed_data.append({
                'المضخة': pump[2],
                'المحطة': pump[14],
                'الموظف': pump[17],
                'المنصب': employee[4],
                'نوع الوقود': pump[15],
                'التوافق': f"{assignment_logic.get_compatibility_score(employee, pump)}%",
                'تاريخ التعيين': pump[13].strftime('%Y-%m-%d') if pump[13] else 'غير محدد'
            })

    if detailed_data:
        df = pd.DataFrame(detailed_data)
        st.dataframe(df, use_container_width=True)

        # Export functionality
        if st.button("📥 تصدير التقرير", key="export_assignments"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="تحميل ملف CSV",
                data=csv,
                file_name="employee_pump_assignments.csv",
                mime="text/csv",
                key="download_assignments"
            )

def pump_tank_assignments():
    """Manage pump to tank assignments with intelligent compatibility logic"""
    safe_html = get_safe_html()

    # Enhanced header
    safe_html.display_section_header(
        "ربط المضخات بالخزانات",
        "ربط ذكي وآمن بين المضخات والخزانات مع ضمان التوافق والسلامة",
        "🗂️"
    )

    # Get data
    pumps = get_all_pumps()
    tanks = get_all_tanks()
    stations = get_all_stations()

    if not pumps or not tanks:
        safe_html.display_info_alert("يرجى إضافة مضخات وخزانات أولاً", "warning", "⚠️")
        return

    # Smart assignment logic for pumps and tanks
    smart_logic = SmartPumpTankLogic(pumps, tanks, stations)

    # Create tabs for different assignment approaches
    tab1, tab2, tab3 = st.tabs([
        "🎯 الربط الذكي",
        "🔧 الربط اليدوي",
        "📊 عرض الربط"
    ])

    with tab1:
        smart_pump_tank_assignment(smart_logic)

    with tab2:
        manual_pump_tank_assignment(smart_logic)

    with tab3:
        view_pump_tank_assignments(smart_logic)


class SmartPumpTankLogic:
    """Smart logic for pump-tank assignments"""

    def __init__(self, pumps, tanks, stations):
        self.pumps = pumps
        self.tanks = tanks
        self.stations = stations

    def get_available_pumps(self):
        """Get pumps without assigned tanks"""
        return [p for p in self.pumps if not p[16]]  # Tank_Name is None

    def get_compatible_tanks(self, pump):
        """Get tanks compatible with a specific pump"""
        pump_fuel_type = pump[15]  # FuelType_Name
        pump_station = pump[1]     # Station_ID

        # Primary: Same station and fuel type
        primary_compatible = [t for t in self.tanks if t[1] == pump_station and t[14] == pump_fuel_type]

        # Secondary: Same fuel type, different station (emergency backup)
        secondary_compatible = [t for t in self.tanks if t[1] != pump_station and t[14] == pump_fuel_type]

        return primary_compatible + secondary_compatible

    def calculate_compatibility_score(self, pump, tank):
        """Calculate compatibility score between pump and tank"""
        score = 0
        reasons = []

        # Same station (highest priority)
        if pump[1] == tank[1]:  # Station_ID match
            score += 50
            reasons.append("نفس المحطة")
        else:
            score += 10
            reasons.append("محطة مختلفة (احتياطي)")

        # Fuel type match (critical)
        if pump[15] == tank[14]:  # FuelType_Name match
            score += 40
            reasons.append("نوع وقود متطابق")
        else:
            return 0, ["نوع وقود غير متطابق"]  # Incompatible

        # Capacity consideration
        tank_capacity = float(tank[4]) if tank[4] else 0
        if tank_capacity > 20000:  # Large capacity
            score += 10
            reasons.append("سعة كبيرة")

        # Tank status
        if tank[9]:  # Is_Active
            score += 5
            reasons.append("خزان نشط")

        return score, reasons

    def suggest_assignments(self, max_suggestions=5):
        """Suggest optimal pump-tank assignments"""
        available_pumps = self.get_available_pumps()
        suggestions = []

        for pump in available_pumps:
            compatible_tanks = self.get_compatible_tanks(pump)

            for tank in compatible_tanks:
                score, reasons = self.calculate_compatibility_score(pump, tank)

                if score > 0:  # Only include compatible assignments
                    suggestions.append({
                        'pump': pump,
                        'tank': tank,
                        'score': score,
                        'reasons': reasons,
                        'priority': 'عالية' if score >= 90 else 'متوسطة' if score >= 70 else 'منخفضة'
                    })

        # Sort by score (descending)
        suggestions.sort(key=lambda x: x['score'], reverse=True)
        return suggestions[:max_suggestions]

    def get_assignment_warnings(self, pump, tank):
        """Get warnings for potential assignment issues"""
        warnings = []

        # Different stations
        if pump[1] != tank[1]:
            warnings.append("⚠️ محطة مختلفة - قد يؤثر على الكفاءة")

        # Tank capacity check
        tank_capacity = float(tank[4]) if tank[4] else 0
        if tank_capacity < 10000:
            warnings.append("⚠️ سعة خزان منخفضة")

        # Tank maintenance check
        if tank[11] and tank[11] <= pd.Timestamp.now().date():  # Next_Maintenance
            warnings.append("⚠️ الخزان يحتاج صيانة")

        return warnings


def smart_pump_tank_assignment(smart_logic):
    """Smart assignment with AI-powered suggestions"""
    st.markdown("### 🧠 الربط الذكي بالذكاء الاصطناعي")

    # Get smart suggestions
    suggestions = smart_logic.suggest_assignments()

    if not suggestions:
        safe_html.display_info_alert("لا توجد اقتراحات متاحة حالياً", "info", "🤖")
        return

    st.markdown("#### 💡 أفضل الاقتراحات:")

    for i, suggestion in enumerate(suggestions):
        pump = suggestion['pump']
        tank = suggestion['tank']
        score = suggestion['score']
        reasons = suggestion['reasons']

        # Enhanced suggestion card
        col1, col2, col3, col4 = st.columns([2, 2, 1, 1])

        with col1:
            st.markdown(f"**⛽ {pump[2]}**")  # Pump name
            st.caption(f"محطة: {pump[14]}")

        with col2:
            st.markdown(f"**🗂️ {tank[3]}**")  # Tank name
            st.caption(f"سعة: {tank[4]:.0f} لتر")

        with col3:
            # Score and priority indicator
            priority_colors = {'عالية': '#10b981', 'متوسطة': '#f59e0b', 'منخفضة': '#6b7280'}
            color = priority_colors.get(suggestion['priority'], '#6b7280')

            st.markdown(f"""
                <div style="text-align: center;">
                    <div style="color: {color}; font-weight: bold;">{score}%</div>
                    <div style="font-size: 0.8em; color: {color};">{suggestion['priority']}</div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            if st.button("ربط", key=f"smart_link_{i}", use_container_width=True):
                if update_pump_assignment(pump[0], None, tank[0]):
                    safe_html.display_info_alert(
                        f"تم ربط المضخة {pump[2]} بالخزان {tank[3]} بنجاح!",
                        "success",
                        "✅"
                    )
                    st.rerun()
                else:
                    safe_html.display_info_alert("فشل في الربط", "error", "❌")

        # Show reasons and warnings
        st.caption(f"📋 {' • '.join(reasons)}")

        warnings = smart_logic.get_assignment_warnings(pump, tank)
        if warnings:
            for warning in warnings:
                st.caption(warning)

        st.markdown("---")


def manual_pump_tank_assignment(smart_logic):
    """Manual assignment with enhanced validation and safety checks"""
    st.markdown("### 🔧 الربط اليدوي")

    # Create columns for assign/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("#### ➕ ربط مضخة بخزان")

        with st.form("assign_pump_tank_form"):
            # Station filter for better UX
            station_options = {f"{s[1]} ({s[6]})": s[0] for s in smart_logic.stations}
            selected_station = st.selectbox(
                "🏭 اختر المحطة أولاً",
                [""] + list(station_options.keys()),
                help="تصفية المضخات والخزانات حسب المحطة"
            )

            station_id = station_options.get(selected_station, None) if selected_station else None

            # Get available pumps for selected station
            available_pumps = smart_logic.get_available_pumps()
            if station_id:
                available_pumps = [p for p in available_pumps if p[1] == station_id]

            if available_pumps:
                pump_options = {f"{p[2]} (رقم: {p[3]}) - {p[15]}": p[0] for p in available_pumps}
                selected_pump = st.selectbox(
                    "⛽ اختر المضخة",
                    list(pump_options.keys()),
                    help="اختر المضخة التي تريد ربطها بخزان"
                )

                # Get compatible tanks
                pump_id = pump_options[selected_pump]
                pump_data = next(p for p in available_pumps if p[0] == pump_id)
                compatible_tanks = smart_logic.get_compatible_tanks(pump_data)

                if compatible_tanks:
                    # Group tanks by compatibility level
                    primary_tanks = [t for t in compatible_tanks if t[1] == pump_data[1]]  # Same station
                    secondary_tanks = [t for t in compatible_tanks if t[1] != pump_data[1]]  # Different station

                    tank_options = {}

                    # Add primary tanks first
                    for tank in primary_tanks:
                        tank_options[f"🏠 {tank[3]} (سعة: {tank[4]:.0f} لتر) - نفس المحطة"] = tank[0]

                    # Add secondary tanks
                    for tank in secondary_tanks:
                        station_name = next((s[1] for s in smart_logic.stations if s[0] == tank[1]), "غير محدد")
                        tank_options[f"🔄 {tank[3]} (سعة: {tank[4]:.0f} لتر) - محطة: {station_name}"] = tank[0]

                    selected_tank = st.selectbox(
                        "🗂️ اختر الخزان المتوافق",
                        list(tank_options.keys()),
                        help="الخزانات مرتبة حسب الأولوية (نفس المحطة أولاً)"
                    )

                    # Show compatibility analysis
                    tank_id = tank_options[selected_tank]
                    tank_data = next(t for t in compatible_tanks if t[0] == tank_id)

                    score, reasons = smart_logic.calculate_compatibility_score(pump_data, tank_data)

                    # Compatibility indicator
                    if score >= 90:
                        st.success(f"🎯 توافق ممتاز: {score}% - {' • '.join(reasons)}")
                    elif score >= 70:
                        st.warning(f"👍 توافق جيد: {score}% - {' • '.join(reasons)}")
                    else:
                        st.info(f"📊 توافق أساسي: {score}% - {' • '.join(reasons)}")

                    # Show warnings
                    warnings = smart_logic.get_assignment_warnings(pump_data, tank_data)
                    if warnings:
                        for warning in warnings:
                            st.warning(warning)

                    # Safety confirmation
                    safety_confirmed = st.checkbox(
                        "✅ أؤكد أن هذا الربط آمن ومتوافق مع إجراءات السلامة",
                        help="يجب التأكد من التوافق قبل الربط"
                    )

                    if st.form_submit_button("🔗 تأكيد الربط", use_container_width=True, disabled=not safety_confirmed):
                        if not safety_confirmed:
                            st.error("❌ يجب تأكيد السلامة أولاً")
                        else:
                            if update_pump_assignment(pump_id, None, tank_id):
                                safe_html.display_info_alert(
                                    f"تم ربط المضخة {pump_data[2]} بالخزان {tank_data[3]} بنجاح!",
                                    "success",
                                    "✅"
                                )
                                st.rerun()
                            else:
                                safe_html.display_info_alert("فشل في الربط", "error", "❌")
                else:
                    pump_fuel_type = pump_data[15]
                    st.warning(f"⚠️ لا توجد خزانات متوافقة مع نوع الوقود: {pump_fuel_type}")
            else:
                safe_html.display_info_alert("جميع المضخات مربوطة بخزانات بالفعل", "info", "ℹ️")

    with col2:
        st.markdown("#### 📋 المضخات المربوطة")

        # Show pumps with assigned tanks
        assigned_pumps = [p for p in smart_logic.pumps if p[16]]  # Has Tank_Name

        if assigned_pumps:
            # Enhanced data display with safety indicators
            assignment_data = []
            for pump in assigned_pumps:
                tank = next((t for t in smart_logic.tanks if t[0] == pump[6]), None)  # Tank_ID match
                station = next((s for s in smart_logic.stations if s[0] == pump[1]), None)

                if tank and station:
                    score, reasons = smart_logic.calculate_compatibility_score(pump, tank)
                    warnings = smart_logic.get_assignment_warnings(pump, tank)

                    assignment_data.append({
                        'المضخة': pump[2],
                        'المحطة': station[1],
                        'الخزان': pump[16],
                        'نوع الوقود': pump[15],
                        'التوافق': f"{score}%" if score >= 70 else f"{score}% ⚠️",
                        'الحالة': 'آمن' if not warnings else 'تحذير',
                        'السعة': f"{tank[4]:.0f} لتر" if tank[4] else 'غير محدد'
                    })

            df = pd.DataFrame(assignment_data)

            # Color coding for status
            def color_status(val):
                if val == 'آمن':
                    return "background-color: #d4edda; color: #155724"
                else:
                    return "background-color: #f8d7da; color: #721c24"

            styled_df = df.style.applymap(color_status, subset=['الحالة'])
            st.dataframe(styled_df, use_container_width=True)

            # Enhanced summary with safety metrics
            safe_assignments = len([a for a in assignment_data if a['الحالة'] == 'آمن'])
            warning_assignments = len([a for a in assignment_data if a['الحالة'] == 'تحذير'])

            metrics = [
                {"icon": "⛽", "value": str(len(assigned_pumps)), "label": "المضخات المربوطة", "color": "#10b981"},
                {"icon": "🗂️", "value": str(len(smart_logic.pumps) - len(assigned_pumps)), "label": "المضخات المتاحة", "color": "#f59e0b"},
                {"icon": "✅", "value": str(safe_assignments), "label": "ربط آمن", "color": "#10b981"},
                {"icon": "⚠️", "value": str(warning_assignments), "label": "ربط يحتاج مراجعة", "color": "#ef4444"}
            ]

            safe_html.display_metric_grid(metrics)

            # Safety alerts
            if warning_assignments > 0:
                safe_html.display_info_alert(
                    f"يوجد {warning_assignments} ربط يحتاج مراجعة للسلامة",
                    "warning",
                    "⚠️"
                )
        else:
            safe_html.display_info_alert("لا توجد مضخات مربوطة بخزانات", "info", "📭")


def view_pump_tank_assignments(smart_logic):
    """View all pump-tank assignments with detailed analytics"""
    st.markdown("### 📊 تحليل الربط والتوافق")

    assigned_pumps = [p for p in smart_logic.pumps if p[16]]

    if not assigned_pumps:
        safe_html.display_info_alert("لا توجد روابط حالياً", "info", "📊")
        return

    # Assignment analytics
    st.markdown("#### 📈 إحصائيات الربط")

    # Compatibility distribution
    compatibility_scores = []
    for pump in assigned_pumps:
        tank = next((t for t in smart_logic.tanks if t[0] == pump[6]), None)
        if tank:
            score, _ = smart_logic.calculate_compatibility_score(pump, tank)
            compatibility_scores.append(score)

    if compatibility_scores:
        # Compatibility score distribution
        score_ranges = {'ممتاز (90-100%)': len([s for s in compatibility_scores if s >= 90]),
                       'جيد (70-89%)': len([s for s in compatibility_scores if 70 <= s < 90]),
                       'مقبول (50-69%)': len([s for s in compatibility_scores if 50 <= s < 70]),
                       'ضعيف (<50%)': len([s for s in compatibility_scores if s < 50])}

        st.subheader("🎯 توزيع مستويات التوافق")
        score_df = pd.DataFrame(list(score_ranges.items()), columns=['المستوى', 'عدد الربط'])
        st.bar_chart(score_df.set_index('المستوى'))

    # Fuel type distribution
    fuel_distribution = {}
    for pump in assigned_pumps:
        fuel_type = pump[15]
        if fuel_type:
            fuel_distribution[fuel_type] = fuel_distribution.get(fuel_type, 0) + 1

    if fuel_distribution:
        st.subheader("⛽ توزيع الربط حسب نوع الوقود")
        fuel_df = pd.DataFrame(list(fuel_distribution.items()), columns=['نوع الوقود', 'عدد الربط'])
        st.bar_chart(fuel_df.set_index('نوع الوقود'))

    # Station-wise analysis
    station_analysis = {}
    for pump in assigned_pumps:
        station_name = pump[14]
        tank = next((t for t in smart_logic.tanks if t[0] == pump[6]), None)

        if station_name and tank:
            if station_name not in station_analysis:
                station_analysis[station_name] = {'pumps': 0, 'tanks': set(), 'same_station_links': 0}

            station_analysis[station_name]['pumps'] += 1
            station_analysis[station_name]['tanks'].add(tank[0])

            # Check if pump and tank are in same station
            if pump[1] == tank[1]:
                station_analysis[station_name]['same_station_links'] += 1

    if station_analysis:
        st.subheader("🏭 تحليل الربط حسب المحطة")

        station_data = []
        for station, data in station_analysis.items():
            station_data.append({
                'المحطة': station,
                'المضخات المربوطة': data['pumps'],
                'الخزانات المستخدمة': len(data['tanks']),
                'الربط داخل المحطة': data['same_station_links'],
                'نسبة الربط المحلي': f"{(data['same_station_links'] / data['pumps'] * 100):.1f}%" if data['pumps'] > 0 else "0%"
            })

        station_df = pd.DataFrame(station_data)
        st.dataframe(station_df, use_container_width=True)

    # Detailed assignment table with safety indicators
    st.markdown("#### 📋 تفاصيل الربط المفصلة")

    detailed_data = []
    for pump in assigned_pumps:
        tank = next((t for t in smart_logic.tanks if t[0] == pump[6]), None)
        station = next((s for s in smart_logic.stations if s[0] == pump[1]), None)

        if tank and station:
            score, reasons = smart_logic.calculate_compatibility_score(pump, tank)
            warnings = smart_logic.get_assignment_warnings(pump, tank)

            detailed_data.append({
                'المضخة': pump[2],
                'المحطة': station[1],
                'الخزان': pump[16],
                'نوع الوقود': pump[15],
                'السعة': f"{tank[4]:.0f} لتر" if tank[4] else 'غير محدد',
                'التوافق': f"{score}% ({' • '.join(reasons)})",
                'الحالة': 'آمن ✅' if not warnings else f'تحذير ⚠️ ({len(warnings)})',
                'التحذيرات': ' • '.join(warnings) if warnings else 'لا توجد',
                'تاريخ الربط': pump[13].strftime('%Y-%m-%d') if pump[13] else 'غير محدد'
            })

    if detailed_data:
        df = pd.DataFrame(detailed_data)
        st.dataframe(df, use_container_width=True)

        # Export functionality
        if st.button("📥 تصدير تقرير الربط", key="export_links"):
            csv = df.to_csv(index=False, encoding='utf-8-sig')
            st.download_button(
                label="تحميل ملف CSV",
                data=csv,
                file_name="pump_tank_assignments.csv",
                mime="text/csv",
                key="download_links"
            )

def employee_station_assignments():
    """Manage employee to station assignments"""
    st.subheader("🏭 تعيين الموظفين للمحطات")

    # Get data
    employees = get_all_employees()
    stations = get_all_stations()

    if not employees or not stations:
        st.warning("⚠️ يرجى إضافة موظفين ومحطات أولاً")
        return

    # Create columns for assign/view operations
    col1, col2 = st.columns([1, 1])

    with col1:
        st.markdown("### ➕ تعيين موظف لمحطة")

        with st.form("assign_employee_station_form"):
            # Get available employees (without station assignment)
            available_employees = [e for e in employees if not e[14]]  # Station_Name is None

            if available_employees:
                employee_options = {f"{e[2]} ({e[4]})": e[0] for e in available_employees}
                selected_employee = st.selectbox(
                    "اختر الموظف",
                    list(employee_options.keys()),
                    help="اختر الموظف الذي تريد تعيينه لمحطة"
                )

                station_options = {f"{s[1]} ({s[6]})": s[0] for s in stations}
                selected_station = st.selectbox(
                    "اختر المحطة",
                    list(station_options.keys()),
                    help="اختر المحطة التي سيعمل بها الموظف"
                )

                if st.form_submit_button("تعيين الموظف للمحطة", use_container_width=True):
                    employee_id = employee_options[selected_employee]
                    station_id = station_options[selected_station]

                    if update_employee_station(employee_id, station_id):
                        st.success("✅ تم تعيين الموظف للمحطة بنجاح!")
                        st.rerun()
                    else:
                        st.error("❌ خطأ في تعيين الموظف للمحطة")
            else:
                st.info("ℹ️ جميع الموظفين معينين لمحطات بالفعل")

    with col2:
        st.markdown("### 📋 الموظفون المعينون")

        # Show employees with station assignments
        assigned_employees = [e for e in employees if e[14]]  # Has Station_Name

        if assigned_employees:
            df = pd.DataFrame(assigned_employees, columns=[
                'Employee_ID', 'Station_ID', 'Emp_Name', 'Emp_Gender', 'Designation',
                'DOB', 'Salary', 'Emp_Address', 'Email_ID', 'Phone', 'Manager_ID',
                'Hire_Date', 'Is_Active', 'Created_Date', 'Station_Name', 'Manager_Name'
            ])

            st.dataframe(df[['Emp_Name', 'Designation', 'Station_Name', 'Manager_Name', 'Phone']],
                        use_container_width=True)

            # Summary by station
            st.subheader("🏭 توزيع الموظفين حسب المحطة")

            station_counts = {}
            for emp in assigned_employees:
                station = emp[14]  # Station_Name
                if station:
                    station_counts[station] = station_counts.get(station, 0) + 1

            if station_counts:
                station_df = pd.DataFrame(list(station_counts.items()),
                                        columns=['المحطة', 'عدد الموظفين'])
                st.bar_chart(station_df.set_index('المحطة'))
        else:
            st.info("ℹ️ لا يوجد موظفون معينون لمحطات")

def assignments_reports():
    """Reports for all assignments"""
    st.subheader("📊 تقارير التعيينات والربط")

    # Get all data
    pumps = get_all_pumps()
    employees = get_all_employees()
    tanks = get_all_tanks()
    stations = get_all_stations()

    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        assigned_pumps = len([p for p in pumps if p[17]])  # Has Employee_Name
        st.metric("المضخات المعينة", assigned_pumps)

    with col2:
        assigned_tanks = len([p for p in pumps if p[16]])  # Has Tank_Name
        st.metric("المضخات المربوطة", assigned_tanks)

    with col3:
        assigned_employees = len([e for e in employees if e[14]])  # Has Station_Name
        st.metric("الموظفون المعينون", assigned_employees)

    with col4:
        total_assignments = assigned_pumps + assigned_tanks + assigned_employees
        st.metric("إجمالي التعيينات", total_assignments)

    st.markdown("---")

    # Detailed assignments report
    st.subheader("🔗 تقرير مفصل بالتعيينات")

    if pumps:
        # Create comprehensive assignment report
        assignment_data = []

        for pump in pumps:
            assignment_data.append({
                'المضخة': pump[2],
                'المحطة': pump[14],
                'نوع الوقود': pump[15],
                'الخزان المرتبط': pump[16] if pump[16] else "غير مربوط",
                'الموظف المعين': pump[17] if pump[17] else "غير معين",
                'الحالة': "مكتملة" if (pump[16] and pump[17]) else "غير مكتملة"
            })

        if assignment_data:
            df = pd.DataFrame(assignment_data)

            # Color coding for status
            def color_status(val):
                if val == "مكتملة":
                    return "background-color: #d4edda; color: #155724"
                else:
                    return "background-color: #f8d7da; color: #721c24"

            styled_df = df.style.applymap(color_status, subset=['الحالة'])
            st.dataframe(styled_df, use_container_width=True)

            # Assignment completion rate
            completed_assignments = len([a for a in assignment_data if a['الحالة'] == "مكتملة"])
            completion_rate = (completed_assignments / len(assignment_data)) * 100

            st.subheader("📈 معدل إتمام التعيينات")
            st.progress(completion_rate / 100)
            st.write(f"**{completion_rate:.1f}%** من المضخات مكتملة التعيينات")

    # Station-wise summary
    st.subheader("🏭 ملخص حسب المحطة")

    if stations:
        station_summary = []

        for station in stations:
            station_id = station[0]
            station_name = station[1]

            # Count pumps in this station
            station_pumps = [p for p in pumps if p[1] == station_id]  # Station_ID

            # Count assigned pumps
            assigned_pumps = [p for p in station_pumps if p[17]]  # Has Employee_Name

            # Count connected tanks
            connected_pumps = [p for p in station_pumps if p[16]]  # Has Tank_Name

            # Count employees in this station
            station_employees = [e for e in employees if e[1] == station_id]  # Station_ID

            station_summary.append({
                'المحطة': station_name,
                'إجمالي المضخات': len(station_pumps),
                'المضخات المعينة': len(assigned_pumps),
                'المضخات المربوطة': len(connected_pumps),
                'الموظفون': len(station_employees),
                'معدل التعيينات %': round((len(assigned_pumps) / len(station_pumps) * 100), 1) if station_pumps else 0
            })

        if station_summary:
            summary_df = pd.DataFrame(station_summary)
            st.dataframe(summary_df, use_container_width=True)

            # Station performance chart
            st.subheader("📊 أداء المحطات في التعيينات")
            chart_df = summary_df[['المحطة', 'معدل التعيينات %']]
            st.bar_chart(chart_df.set_index('المحطة'))

def update_pump_assignment(pump_id, employee_id=None, tank_id=None):
    """Update pump assignment (employee and/or tank)"""
    conn = get_connection()
    if not conn:
        return False

    c = conn.cursor()

    try:
        if employee_id and tank_id:
            # Update both employee and tank
            c.execute('''UPDATE FuelPumps
                        SET Employee_ID = %s, Tank_ID = %s
                        WHERE Pump_ID = %s''',
                     (employee_id, tank_id, pump_id))
        elif employee_id:
            # Update only employee
            c.execute('''UPDATE FuelPumps
                        SET Employee_ID = %s
                        WHERE Pump_ID = %s''',
                     (employee_id, pump_id))
        elif tank_id:
            # Update only tank
            c.execute('''UPDATE FuelPumps
                        SET Tank_ID = %s
                        WHERE Pump_ID = %s''',
                     (tank_id, pump_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"خطأ في تحديث التعيين: {e}")
        conn.close()
        return False

def update_employee_station(employee_id, station_id):
    """Update employee station assignment"""
    conn = get_connection()
    if not conn:
        return False

    c = conn.cursor()

    try:
        c.execute('''UPDATE Employees
                    SET Station_ID = %s
                    WHERE Employee_ID = %s''',
                 (station_id, employee_id))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        st.error(f"خطأ في تحديث تعيين الموظف: {e}")
        conn.close()
        return False

if __name__ == "__main__":
    main()
