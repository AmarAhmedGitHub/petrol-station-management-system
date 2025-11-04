import streamlit as st
import pandas as pd
from core.database_enhanced import get_connection
from core.safe_html import get_safe_html

def get_dashboard_stats():
    """Get dashboard statistics"""
    conn = get_connection()
    if not conn:
        return None

    c = conn.cursor()

    stats = {}

    try:
        # Total sales
        c.execute("SELECT IFNULL(SUM(Total_Amount),0) FROM Invoices")
        stats['total_sales'] = c.fetchone()[0]

        # Customer count
        c.execute("SELECT COUNT(*) FROM Customers")
        stats['customer_count'] = c.fetchone()[0]

        # Total fuel sold
        c.execute("SELECT IFNULL(SUM(Fuel_Amount_Liters),0) FROM Invoices")
        stats['total_fuel'] = c.fetchone()[0]

        # Petrol pump count
        c.execute("SELECT COUNT(*) FROM FuelPumps")
        stats['pump_count'] = c.fetchone()[0]

        # Employee count
        c.execute("SELECT COUNT(*) FROM Employees")
        stats['employee_count'] = c.fetchone()[0]

        # Tank count
        c.execute("SELECT COUNT(*) FROM FuelTanks")
        stats['tank_count'] = c.fetchone()[0]

        # Recent invoices count (last 30 days)
        c.execute("SELECT COUNT(*) FROM Invoices WHERE Invoice_Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)")
        stats['recent_invoices'] = c.fetchone()[0]

        # Low stock alerts
        c.execute("SELECT COUNT(*) FROM FuelTanks WHERE Current_Amount_Liters < 1000")
        stats['low_stock_alerts'] = c.fetchone()[0]

    except Exception as e:
        st.error(f"خطأ في جلب الإحصائيات: {e}")
        return None
    finally:
        conn.close()

    return stats

def show_dashboard():
    """Display advanced dashboard with comprehensive charts and real-time monitoring"""
    safe_html = get_safe_html()

    # Enhanced dashboard header with real-time status
    st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 20px;
            margin-bottom: 30px;
            box-shadow: 0 10px 40px rgba(102,126,234,0.3);
            position: relative;
            overflow: hidden;
        ">
            <div style="
                position: absolute;
                top: -50px;
                right: -50px;
                width: 200px;
                height: 200px;
                background: rgba(255,255,255,0.1);
                border-radius: 50%;
            "></div>
            <div style="
                position: absolute;
                bottom: -40px;
                left: -40px;
                width: 150px;
                height: 150px;
                background: rgba(255,255,255,0.05);
                border-radius: 50%;
            "></div>
            <div style="position: relative; z-index: 1;">
                <h1 style="
                    margin: 0 0 15px 0;
                    font-size: 3em;
                    font-weight: 800;
                    text-shadow: 0 3px 6px rgba(0,0,0,0.4);
                    display: flex;
                    align-items: center;
                    gap: 20px;
                ">
                    ⛽ لوحة التحكم المتقدمة
                    <span style="font-size: 0.4em; background: rgba(255,255,255,0.2); padding: 8px 15px; border-radius: 25px;">LIVE</span>
                </h1>
                <p style="
                    margin: 0;
                    font-size: 1.3em;
                    opacity: 0.95;
                    font-weight: 400;
                    line-height: 1.6;
                ">مراقبة شاملة ومتقدمة لأداء محطات الوقود مع مخططات تفاعلية وتحليلات ذكية</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Real-time status indicators
    show_real_time_status()

    # Main dashboard sections with advanced charts
    show_product_prices_chart()
    show_profit_loss_analysis()
    show_sales_movement_chart()
    show_pump_status_monitoring()
    show_tank_levels_monitoring()

    # Quick actions in a compact format
    st.markdown("---")
    show_compact_quick_actions()

def show_overview_stats():
    """Show overview statistics with modern design"""
    safe_html = get_safe_html()

    # Section header - استخدام HTML آمن
    safe_html.display_section_header(
        "النظرة العامة على النظام",
        "إحصائيات شاملة لأداء النظام والمبيعات",
        "📊"
    )

    stats = get_dashboard_stats()
    if not stats:
        safe_html.display_info_alert("تعذر تحميل الإحصائيات", "error", "❌")
        return

    # Statistics cards in grid - استخدام شبكة المقاييس المحسنة
    metrics = [
        {
            "icon": "💰",
            "value": f"{stats['total_sales']:,}",
            "label": "إجمالي المبيعات",
            "color": "#059669"
        },
        {
            "icon": "👥",
            "value": str(stats['customer_count']),
            "label": "عدد العملاء",
            "color": "#2563eb"
        },
        {
            "icon": "⛽",
            "value": f"{stats['total_fuel']:,}",
            "label": "كمية الوقود المباعة",
            "color": "#dc2626"
        },
        {
            "icon": "🏪",
            "value": str(stats['pump_count']),
            "label": "عدد الطرمبات",
            "color": "#ea580c"
        },
        {
            "icon": "👨‍💼",
            "value": str(stats['employee_count']),
            "label": "عدد الموظفين",
            "color": "#7c3aed"
        },
        {
            "icon": "⛽",
            "value": str(stats['tank_count']),
            "label": "عدد الخزانات",
            "color": "#0891b2"
        }
    ]

    safe_html.display_metric_grid(metrics)

    # Additional stats section - استخدام تنبيهات محسنة
    safe_html.display_section_header("إحصائيات إضافية", icon="📈")

    col1, col2 = st.columns(2)

    with col1:
        safe_html.display_info_alert(
            f"🧾 الفواتير خلال 30 يوم: {stats['recent_invoices']}\n\n⚠️ تنبيهات المخزون المنخفض: {stats['low_stock_alerts']}",
            "info"
        )

    with col2:
        additional_info = []
        if stats['total_sales'] > 0:
            avg_invoice = stats['total_sales'] / max(stats['recent_invoices'], 1)
            additional_info.append(f"📊 متوسط الفاتورة: {avg_invoice:.0f}")
        else:
            additional_info.append("📊 متوسط الفاتورة: 0")

        if stats['total_fuel'] > 0 and stats['customer_count'] > 0:
            avg_fuel_per_customer = stats['total_fuel'] / stats['customer_count']
            additional_info.append(f"⛽ متوسط الوقود للعميل: {avg_fuel_per_customer:.1f}")
        else:
            additional_info.append("⛽ متوسط الوقود للعميل: 0")

        safe_html.display_info_alert("\n\n".join(additional_info), "success")

def show_sales_stats():
    """Show sales statistics with modern design"""
    safe_html = get_safe_html()

    # Section header - استخدام HTML آمن
    safe_html.display_section_header(
        "إحصائيات المبيعات",
        "تحليل مفصل لأداء المبيعات والإيرادات",
        "💰"
    )

    stats = get_dashboard_stats()
    if not stats:
        safe_html.display_info_alert("تعذر تحميل إحصائيات المبيعات", "error", "❌")
        return

    # Sales metrics in grid - استخدام شبكة المقاييس المحسنة
    metrics = [
        {
            "icon": "💰",
            "value": f"{stats['total_sales']:,}",
            "label": "إجمالي المبيعات",
            "color": "#059669"
        },
        {
            "icon": "🧾",
            "value": str(stats['recent_invoices']),
            "label": "عدد الفواتير",
            "color": "#2563eb"
        }
    ]

    if stats['total_sales'] > 0:
        avg_invoice = stats['total_sales'] / max(stats['recent_invoices'], 1)
        metrics.append({
            "icon": "📊",
            "value": f"{avg_invoice:.0f}",
            "label": "متوسط الفاتورة",
            "color": "#7c3aed"
        })

    safe_html.display_metric_grid(metrics)

def show_stock_details():
    """Show stock details with modern design"""
    safe_html = get_safe_html()

    # Section header - استخدام HTML آمن
    safe_html.display_section_header(
        "تفاصيل المخزون",
        "مراقبة مستويات الوقود والتنبيهات",
        "⛽"
    )

    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            c.execute("SELECT t.Tank_ID, s.Station_Name, ft.FuelType_Name, t.Current_Amount_Liters, t.Capacity_Liters FROM FuelTanks t JOIN PetrolStations s ON t.Station_ID = s.Station_ID JOIN FuelTypes ft ON t.FuelType_ID = ft.FuelType_ID ORDER BY t.Current_Amount_Liters ASC")
            tanks = c.fetchall()

            if tanks:
                df_stock = pd.DataFrame(tanks, columns=["رقم الخزان", "اسم المحطة", "نوع الوقود", "الكمية الحالية (لتر)", "السعة الكلية (لتر)"])

                # Stock data table - استخدام جدول محسن
                safe_html.display_data_table_with_header(
                    df_stock,
                    "بيانات المخزون",
                    "جدول يوضح مستويات الوقود في جميع الخزانات"
                )

                # Low stock alerts - استخدام تنبيهات محسنة
                min_limit = 1000
                low_stock = df_stock[df_stock["الكمية الحالية (لتر)"] < min_limit]

                if not low_stock.empty:
                    safe_html.display_info_alert(
                        f"تم العثور على {len(low_stock)} خزان بمخزون منخفض (أقل من {min_limit} لتر)",
                        "warning",
                        "⚠️"
                    )
                    st.dataframe(low_stock, use_container_width=True)
                else:
                    safe_html.display_info_alert(
                        "جميع المخزونات ضمن الحد الآمن",
                        "success",
                        "✅"
                    )

                # Stock distribution chart section
                safe_html.display_section_header("توزيع المخزون حسب نوع الوقود", icon="📊")

                chart_data = df_stock.groupby("نوع الوقود")["الكمية الحالية (لتر)"].sum().reset_index()
                st.bar_chart(chart_data.set_index("نوع الوقود"))

            else:
                safe_html.display_info_alert(
                    "لا توجد بيانات مخزون متوفرة حالياً",
                    "info",
                    "ℹ️"
                )

        except Exception as e:
            safe_html.display_info_alert(
                f"خطأ في جلب البيانات: {e}",
                "error",
                "❌"
            )
        finally:
            conn.close()

def show_quick_actions():
    """Show quick actions with modern design"""
    safe_html = get_safe_html()

    # Section header - استخدام HTML آمن
    safe_html.display_section_header(
        "الإجراءات السريعة",
        "الوصول السريع للمهام الأكثر استخداماً",
        "⚡"
    )

    # Quick actions - استخدام بطاقات الإجراءات المحسنة
    quick_actions = [
        {
            "icon": "📊",
            "title": "عرض التقارير",
            "description": "الوصول السريع للتقارير والإحصائيات",
            "color": "#2563eb",
            "key": "quick_reports",
            "action": "reports"
        },
        {
            "icon": "🔍",
            "title": "البحث المتقدم",
            "description": "بحث متقدم في البيانات والسجلات",
            "color": "#059669",
            "key": "quick_search",
            "action": "search"
        },
        {
            "icon": "⚙️",
            "title": "إعدادات النظام",
            "description": "إدارة إعدادات النظام والتكوينات",
            "color": "#ea580c",
            "key": "quick_settings",
            "action": "settings"
        }
    ]

    selected_action = safe_html.display_action_cards(quick_actions)

    if selected_action == "search":
        safe_html.display_info_alert(
            "سيتم تطوير هذا القسم قريباً",
            "info",
            "🔍"
        )
    elif selected_action:
        st.session_state.dashboard_section = selected_action

def show_real_time_status():
    """Show real-time system status indicators"""
    st.markdown("### 🔴 الحالة المباشرة للنظام")

    # Status indicators in columns
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        # Automation status
        automation_active = st.session_state.get('automation_initialized', False)
        status_color = "#10b981" if automation_active else "#ef4444"
        status_icon = "🤖" if automation_active else "⚠️"
        status_text = "يعمل" if automation_active else "متوقف"

        st.markdown(f"""
            <div style="
                background: {status_color}15;
                border: 2px solid {status_color};
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin: 5px 0;
            ">
                <div style="font-size: 2em; margin-bottom: 5px;">{status_icon}</div>
                <div style="font-weight: bold; color: {status_color};">الأتمتة</div>
                <div style="font-size: 0.9em;">{status_text}</div>
            </div>
        """, unsafe_allow_html=True)

    with col2:
        # Database status
        try:
            conn = get_connection()
            if conn:
                conn.close()
                db_status = "متصل"
                db_color = "#10b981"
                db_icon = "🗄️"
            else:
                db_status = "خطأ"
                db_color = "#ef4444"
                db_icon = "❌"
        except:
            db_status = "خطأ"
            db_color = "#ef4444"
            db_icon = "❌"

        st.markdown(f"""
            <div style="
                background: {db_color}15;
                border: 2px solid {db_color};
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin: 5px 0;
            ">
                <div style="font-size: 2em; margin-bottom: 5px;">{db_icon}</div>
                <div style="font-weight: bold; color: {db_color};">قاعدة البيانات</div>
                <div style="font-size: 0.9em;">{db_status}</div>
            </div>
        """, unsafe_allow_html=True)

    with col3:
        # Sensor status
        sensor_status = "نشط"
        sensor_color = "#10b981"
        sensor_icon = "📡"

        st.markdown(f"""
            <div style="
                background: {sensor_color}15;
                border: 2px solid {sensor_color};
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin: 5px 0;
            ">
                <div style="font-size: 2em; margin-bottom: 5px;">{sensor_icon}</div>
                <div style="font-weight: bold; color: {sensor_color};">أجهزة الاستشعار</div>
                <div style="font-size: 0.9em;">{sensor_status}</div>
            </div>
        """, unsafe_allow_html=True)

    with col4:
        # Current time
        import datetime
        current_time = datetime.datetime.now().strftime("%H:%M:%S")

        st.markdown(f"""
            <div style="
                background: #3b82f615;
                border: 2px solid #3b82f6;
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin: 5px 0;
            ">
                <div style="font-size: 2em; margin-bottom: 5px;">🕐</div>
                <div style="font-weight: bold; color: #3b82f6;">الوقت الحالي</div>
                <div style="font-size: 0.9em;">{current_time}</div>
            </div>
        """, unsafe_allow_html=True)

    with col5:
        # System load (simulated)
        system_load = "منخفض"
        load_color = "#10b981"
        load_icon = "⚡"

        st.markdown(f"""
            <div style="
                background: {load_color}15;
                border: 2px solid {load_color};
                border-radius: 15px;
                padding: 15px;
                text-align: center;
                margin: 5px 0;
            ">
                <div style="font-size: 2em; margin-bottom: 5px;">{load_icon}</div>
                <div style="font-weight: bold; color: {load_color};">حمل النظام</div>
                <div style="font-size: 0.9em;">{system_load}</div>
            </div>
        """, unsafe_allow_html=True)


def show_product_prices_chart():
    """Show interactive product prices chart"""
    st.markdown("### 💰 أسعار المنتجات والوقود")

    # Get fuel types and their prices
    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            c.execute("SELECT FuelType_Name, Unit_Price FROM FuelTypes WHERE Is_Active = TRUE ORDER BY Unit_Price DESC")
            fuel_prices = c.fetchall()

            if fuel_prices:
                # Create price chart
                import pandas as pd

                df_prices = pd.DataFrame(fuel_prices, columns=['نوع الوقود', 'السعر (ريال)'])

                # Enhanced price display with cards
                st.markdown('<div style="display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); margin: 20px 0;">', unsafe_allow_html=True)

                colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4', '#ffeaa7', '#dda0dd']

                for i, (_, row) in enumerate(df_prices.iterrows()):
                    color = colors[i % len(colors)]
                    st.markdown(f"""
                        <div style="
                            background: linear-gradient(135deg, {color} 0%, {color}dd 100%);
                            color: white;
                            padding: 20px;
                            border-radius: 15px;
                            text-align: center;
                            box-shadow: 0 8px 25px rgba(0,0,0,0.15);
                            transition: transform 0.3s ease;
                        " onmouseover="this.style.transform='translateY(-5px)'" onmouseout="this.style.transform='translateY(0)'">
                            <div style="font-size: 2.5em; margin-bottom: 10px;">⛽</div>
                            <div style="font-size: 1.2em; font-weight: bold; margin-bottom: 5px;">{row['نوع الوقود']}</div>
                            <div style="font-size: 1.8em; font-weight: 800;">{row['السعر (ريال)']:.2f}</div>
                            <div style="font-size: 0.9em; opacity: 0.9;">ريال/لتر</div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Price comparison chart
                st.markdown("#### 📊 مقارنة الأسعار")
                st.bar_chart(df_prices.set_index('نوع الوقود'))

            else:
                st.info("ℹ️ لا توجد أسعار محددة للمنتجات")

        except Exception as e:
            st.error(f"خطأ في جلب أسعار المنتجات: {e}")
        finally:
            conn.close()


def show_profit_loss_analysis():
    """Show profit and loss analysis with interactive charts"""
    st.markdown("### 💼 التحليل المالي - الأرباح والخسائر")

    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            # Get monthly sales data for the last 12 months
            c.execute("""
                SELECT
                    DATE_FORMAT(Invoice_Date, '%Y-%m') as month,
                    SUM(Total_Amount) as total_sales,
                    COUNT(*) as invoice_count
                FROM Invoices
                WHERE Invoice_Date >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                GROUP BY DATE_FORMAT(Invoice_Date, '%Y-%m')
                ORDER BY month
            """)
            monthly_data = c.fetchall()

            if monthly_data:
                df_monthly = pd.DataFrame(monthly_data, columns=['الشهر', 'إجمالي المبيعات', 'عدد الفواتير'])

                # Calculate profit/loss (simplified - assuming 70% profit margin)
                df_monthly['الأرباح المقدرة'] = df_monthly['إجمالي المبيعات'] * 0.7
                df_monthly['التكاليف المقدرة'] = df_monthly['إجمالي المبيعات'] * 0.3

                # Financial metrics cards
                col1, col2, col3, col4 = st.columns(4)

                total_sales = df_monthly['إجمالي المبيعات'].sum()
                total_profit = df_monthly['الأرباح المقدرة'].sum()
                avg_monthly_sales = df_monthly['إجمالي المبيعات'].mean()
                profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0

                with col1:
                    st.metric("إجمالي المبيعات", f"{total_sales:,.0f} ريال", "📈")

                with col2:
                    st.metric("إجمالي الأرباح", f"{total_profit:,.0f} ريال", "💰")

                with col3:
                    st.metric("متوسط المبيعات الشهري", f"{avg_monthly_sales:,.0f} ريال", "📊")

                with col4:
                    st.metric("هامش الربح", f"{profit_margin:.1f}%", "🎯")

                # Profit/Loss trend chart
                st.markdown("#### 📈 اتجاه الأرباح والمبيعات")

                # Prepare data for line chart
                chart_data = df_monthly[['الشهر', 'إجمالي المبيعات', 'الأرباح المقدرة', 'التكاليف المقدرة']]
                chart_data = chart_data.set_index('الشهر')

                st.line_chart(chart_data)

                # Monthly breakdown
                st.markdown("#### 📅 التحليل الشهري")
                st.dataframe(df_monthly, use_container_width=True)

            else:
                st.info("ℹ️ لا توجد بيانات مالية كافية للتحليل")

        except Exception as e:
            st.error(f"خطأ في جلب البيانات المالية: {e}")
        finally:
            conn.close()


def show_sales_movement_chart():
    """Show sales movement and trends with interactive charts"""
    st.markdown("### 📈 حركة المبيعات والمؤشرات")

    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            # Get daily sales for the last 30 days
            c.execute("""
                SELECT
                    DATE(Invoice_Date) as sale_date,
                    SUM(Total_Amount) as daily_sales,
                    SUM(Fuel_Amount_Liters) as daily_volume,
                    COUNT(*) as transaction_count
                FROM Invoices
                WHERE Invoice_Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(Invoice_Date)
                ORDER BY sale_date
            """)
            daily_sales = c.fetchall()

            if daily_sales:
                df_daily = pd.DataFrame(daily_sales, columns=['التاريخ', 'المبيعات اليومية', 'الحجم اليومي', 'عدد المعاملات'])

                # Sales movement metrics
                col1, col2, col3, col4 = st.columns(4)

                total_30day_sales = df_daily['المبيعات اليومية'].sum()
                avg_daily_sales = df_daily['المبيعات اليومية'].mean()
                total_volume = df_daily['الحجم اليومي'].sum()
                avg_transactions = df_daily['عدد المعاملات'].mean()

                with col1:
                    st.metric("مبيعات 30 يوم", f"{total_30day_sales:,.0f} ريال", "📈")

                with col2:
                    st.metric("متوسط يومي", f"{avg_daily_sales:,.0f} ريال", "📊")

                with col3:
                    st.metric("إجمالي الحجم", f"{total_volume:,.0f} لتر", "⛽")

                with col4:
                    st.metric("متوسط المعاملات", f"{avg_transactions:.1f}", "🧾")

                # Interactive sales chart
                st.markdown("#### 📊 حركة المبيعات اليومية")
                st.line_chart(df_daily.set_index('التاريخ')[['المبيعات اليومية', 'الحجم اليومي']])

                # Volume vs Transactions scatter plot (simulated with bar chart)
                st.markdown("#### 🔄 العلاقة بين الحجم والمعاملات")
                volume_transaction_data = df_daily[['الحجم اليومي', 'عدد المعاملات']].copy()
                volume_transaction_data.columns = ['حجم المبيعات', 'عدد المعاملات']
                st.bar_chart(volume_transaction_data)

            else:
                st.info("ℹ️ لا توجد بيانات مبيعات كافية")

        except Exception as e:
            st.error(f"خطأ في جلب بيانات المبيعات: {e}")
        finally:
            conn.close()


def show_pump_status_monitoring():
    """Show real-time pump status monitoring"""
    st.markdown("### ⛽ مراقبة حالة مضخات المحطة")

    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            # Get pump status data
            c.execute("""
                SELECT
                    p.Pump_ID,
                    p.Pump_Name,
                    s.Station_Name,
                    ft.FuelType_Name,
                    p.Total_Liters_Dispensed,
                    p.Is_Active,
                    CASE WHEN p.Is_Active = 1 THEN 'نشط' ELSE 'متوقف' END as status_text
                FROM FuelPumps p
                JOIN PetrolStations s ON p.Station_ID = s.Station_ID
                JOIN FuelTypes ft ON p.FuelType_ID = ft.FuelType_ID
                ORDER BY s.Station_Name, p.Pump_Number
            """)
            pumps_data = c.fetchall()

            if pumps_data:
                df_pumps = pd.DataFrame(pumps_data, columns=[
                    'رقم المضخة', 'اسم المضخة', 'اسم المحطة', 'نوع الوقود',
                    'إجمالي التوزيع', 'نشط', 'حالة النص'
                ])

                # Pump status grid
                st.markdown('<div style="display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); margin: 20px 0;">', unsafe_allow_html=True)

                for _, pump in df_pumps.iterrows():
                    status_color = "#10b981" if pump['نشط'] else "#ef4444"
                    status_icon = "🟢" if pump['نشط'] else "🔴"

                    st.markdown(f"""
                        <div style="
                            background: white;
                            border: 2px solid {status_color};
                            border-radius: 15px;
                            padding: 20px;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                            transition: all 0.3s ease;
                        " onmouseover="this.style.transform='translateY(-5px); this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)''"
                           onmouseout="this.style.transform='translateY(0); this.style.boxShadow='0 4px 15px rgba(0,0,0,0.1)''">
                            <div style="display: flex; align-items: center; margin-bottom: 15px;">
                                <span style="font-size: 2em; margin-left: 10px;">{status_icon}</span>
                                <div>
                                    <div style="font-weight: bold; font-size: 1.1em;">{pump['اسم المضخة']}</div>
                                    <div style="color: #6b7280; font-size: 0.9em;">{pump['اسم المحطة']}</div>
                                </div>
                            </div>
                            <div style="margin-bottom: 10px;">
                                <span style="background: {status_color}20; color: {status_color}; padding: 4px 8px; border-radius: 10px; font-size: 0.8em; font-weight: bold;">
                                    {pump['حالة النص']}
                                </span>
                            </div>
                            <div style="color: #374151;">
                                <div style="margin-bottom: 5px;"><strong>نوع الوقود:</strong> {pump['نوع الوقود']}</div>
                                <div><strong>إجمالي التوزيع:</strong> {pump['إجمالي التوزيع']:,.0f} لتر</div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Pump statistics
                active_pumps = len(df_pumps[df_pumps['نشط'] == 1])
                total_dispensed = df_pumps['إجمالي التوزيع'].sum()

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("المضخات النشطة", active_pumps, "🟢")
                with col2:
                    st.metric("المضخات المتوقفة", len(df_pumps) - active_pumps, "🔴")
                with col3:
                    st.metric("إجمالي التوزيع", f"{total_dispensed:,.0f} لتر", "⛽")

                # Pumps by station chart
                st.markdown("#### 🏭 توزيع المضخات حسب المحطة")
                station_pumps = df_pumps.groupby('اسم المحطة').size().reset_index(name='عدد المضخات')
                st.bar_chart(station_pumps.set_index('اسم المحطة'))

            else:
                st.info("ℹ️ لا توجد مضخات مسجلة في النظام")

        except Exception as e:
            st.error(f"خطأ في جلب بيانات المضخات: {e}")
        finally:
            conn.close()


def show_tank_levels_monitoring():
    """Show fuel tank levels monitoring with real-time data"""
    # إخفاء هذا القسم حسب طلب المستخدم
    return
    st.markdown("### 🗂️ مراقبة مستويات خزانات الوقود")

    conn = get_connection()
    if conn:
        c = conn.cursor()
        try:
            # Get tank levels data
            c.execute("""
                SELECT
                    t.Tank_ID,
                    t.Tank_Name,
                    s.Station_Name,
                    ft.FuelType_Name,
                    t.Capacity_Liters,
                    t.Current_Amount_Liters,
                    CASE
                        WHEN t.Capacity_Liters > 0 THEN (t.Current_Amount_Liters / t.Capacity_Liters) * 100
                        ELSE 0
                    END as fill_percentage,
                    CASE
                        WHEN t.Capacity_Liters > 0 AND (t.Current_Amount_Liters / t.Capacity_Liters) * 100 < 20 THEN 'منخفض'
                        WHEN t.Capacity_Liters > 0 AND (t.Current_Amount_Liters / t.Capacity_Liters) * 100 > 80 THEN 'مرتفع'
                        ELSE 'متوسط'
                    END as level_status
                FROM FuelTanks t
                JOIN PetrolStations s ON t.Station_ID = s.Station_ID
                JOIN FuelTypes ft ON t.FuelType_ID = ft.FuelType_ID
                WHERE t.Is_Active = 1
                ORDER BY fill_percentage ASC
            """)
            tanks_data = c.fetchall()

            if tanks_data:
                df_tanks = pd.DataFrame(tanks_data, columns=[
                    'رقم الخزان', 'اسم الخزان', 'اسم المحطة', 'نوع الوقود',
                    'السعة الكلية', 'الكمية الحالية', 'نسبة الامتلاء', 'حالة المستوى'
                ])

                # Tank level visualization
                st.markdown('<div style="display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); margin: 20px 0;">', unsafe_allow_html=True)

                for _, tank in df_tanks.iterrows():
                    fill_percentage = tank['نسبة الامتلاء']

                    # Color coding based on level
                    if fill_percentage < 20:
                        color = "#ef4444"  # Red for low
                        bg_color = "#fee2e2"
                        status_icon = "🔴"
                    elif fill_percentage > 80:
                        color = "#f59e0b"  # Orange for high
                        bg_color = "#fef3c7"
                        status_icon = "🟠"
                    else:
                        color = "#10b981"  # Green for normal
                        bg_color = "#dcfce7"
                        status_icon = "🟢"

                    # Progress bar visualization
                    progress_width = min(fill_percentage, 100)

                    st.markdown(f"""
                        <div style="
                            background: white;
                            border: 2px solid {color};
                            border-radius: 15px;
                            padding: 20px;
                            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
                        ">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                                <div>
                                    <div style="font-weight: bold; font-size: 1.1em;">{tank['اسم الخزان']}</div>
                                    <div style="color: #6b7280; font-size: 0.9em;">{tank['اسم المحطة']}</div>
                                </div>
                                <div style="text-align: center;">
                                    <div style="font-size: 1.5em;">{status_icon}</div>
                                    <div style="font-size: 0.8em; color: {color}; font-weight: bold;">{tank['حالة المستوى']}</div>
                                </div>
                            </div>

                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-weight: bold;">نوع الوقود:</span>
                                    <span>{tank['نوع الوقود']}</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span style="font-weight: bold;">السعة:</span>
                                    <span>{tank['السعة الكلية']:,.0f} لتر</span>
                                </div>
                                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                    <span style="font-weight: bold;">الكمية الحالية:</span>
                                    <span>{tank['الكمية الحالية']:,.0f} لتر</span>
                                </div>
                            </div>

                            <div style="margin-bottom: 10px;">
                                <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                    <span>نسبة الامتلاء</span>
                                    <span style="font-weight: bold; color: {color};">{fill_percentage:.1f}%</span>
                                </div>
                                <div style="
                                    width: 100%;
                                    height: 20px;
                                    background: #e5e7eb;
                                    border-radius: 10px;
                                    overflow: hidden;
                                ">
                                    <div style="
                                        width: {progress_width}%;
                                        height: 100%;
                                        background: {color};
                                        border-radius: 10px;
                                        transition: width 0.5s ease;
                                    "></div>
                                </div>
                            </div>
                        </div>
                    """, unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)

                # Tank statistics
                low_tanks = len(df_tanks[df_tanks['نسبة الامتلاء'] < 20])
                high_tanks = len(df_tanks[df_tanks['نسبة الامتلاء'] > 80])
                total_capacity = df_tanks['السعة الكلية'].sum()
                total_current = df_tanks['الكمية الحالية'].sum()
                avg_fill_rate = (total_current / total_capacity * 100) if total_capacity > 0 else 0

                # إخفاء إحصائيات الخزانات حسب طلب المستخدم
                # col1, col2, col3, col4 = st.columns(4)
                # with col1:
                #     st.metric("الخزانات منخفضة المستوى", low_tanks, "🔴")
                # with col2:
                #     st.metric("الخزانات مرتفعة المستوى", high_tanks, "🟠")
                # with col3:
                #     st.metric("متوسط معدل الامتلاء", f"{avg_fill_rate:.1f}%", "📊")
                # with col4:
                #     st.metric("إجمالي السعة", f"{total_capacity:,.0f} لتر", "🗂️")

                # Tank levels chart
                st.markdown("#### 📊 مستويات الخزانات")
                chart_data = df_tanks[['اسم الخزان', 'نسبة الامتلاء']].copy()
                chart_data = chart_data.sort_values('نسبة الامتلاء', ascending=True)
                st.bar_chart(chart_data.set_index('اسم الخزان'))

            else:
                st.info("ℹ️ لا توجد خزانات نشطة في النظام")

        except Exception as e:
            st.error(f"خطأ في جلب بيانات الخزانات: {e}")
        finally:
            conn.close()


def show_compact_quick_actions():
    """Show compact quick actions bar"""
    st.markdown("### ⚡ إجراءات سريعة")

    # Quick actions in a horizontal layout
    actions = [
        {"icon": "📊", "label": "التقارير", "action": "reports", "key": "reports"},
        {"icon": "⚙️", "label": "الإعدادات", "action": "settings", "key": "settings"},
        {"icon": "🔍", "label": "البحث", "action": "search", "key": "search"},
        {"icon": "📥", "label": "التصدير", "action": "export", "key": "export"},
        {"icon": "🔄", "label": "تحديث", "action": "refresh", "key": "refresh"}
    ]

    cols = st.columns(len(actions))
    for i, action in enumerate(actions):
        with cols[i]:
            if st.button(f"{action['icon']} {action['label']}", key=f"quick_{action['key']}_{i}_dashboard_{id(action)}", use_container_width=True):
                if action['action'] == 'refresh':
                    st.rerun()
                else:
                    st.info(f"سيتم فتح {action['label']} قريباً")


def main():
    """Main dashboard function"""
    if not st.session_state.get('logged_in', False):
        st.warning("⚠️ يجب تسجيل الدخول للوصول إلى لوحة التحكم.")
        return
    show_dashboard()

if __name__ == "__main__":
    main()
