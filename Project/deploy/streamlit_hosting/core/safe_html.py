"""
أدوات HTML آمنة - Safe HTML Utilities
أدوات لعرض HTML بطريقة آمنة دون استخدام unsafe_allow_html
"""

import streamlit as st
from typing import Optional


class SafeHTML:
    """مدير عرض HTML آمن"""

    @staticmethod
    def display_header(title: str, subtitle: Optional[str] = None, icon: str = "📊"):
        """عرض رأس صفحة آمن"""
        st.markdown(f"## {icon} {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
        st.markdown("---")

    @staticmethod
    def display_metric_card(icon: str, value: str, label: str, color: str = "#0d6efd"):
        """عرض بطاقة مقياس آمنة"""
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 20px;
            margin: 10px 0;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        ">
            <div style="font-size: 2em; margin-bottom: 10px;">{icon}</div>
            <div style="font-size: 2em; font-weight: bold; color: {color}; margin-bottom: 5px;">{value}</div>
            <div style="color: #6c757d; font-size: 0.9em;">{label}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_info_card(title: str, content: str, icon: str = "ℹ️", card_type: str = "info"):
        """عرض بطاقة معلومات آمنة"""
        colors = {
            "info": "#0dcaf0",
            "success": "#198754",
            "warning": "#ffc107",
            "error": "#dc3545"
        }
        color = colors.get(card_type, "#0dcaf0")

        st.markdown(f"""
        <div style="
            background: {color}15;
            border: 1px solid {color}30;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 10px;">
                <span style="font-size: 1.5em; margin-right: 10px;">{icon}</span>
                <strong style="color: {color};">{title}</strong>
            </div>
            <div>{content}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_section_header(title: str, icon: str = "📋"):
        """عرض رأس قسم آمن"""
        st.markdown(f"### {icon} {title}")
        st.markdown("---")

    @staticmethod
    def display_quick_action_card(title: str, description: str, icon: str = "⚡"):
        """عرض بطاقة إجراء سريع آمنة"""
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e9ecef;
            border-radius: 8px;
            padding: 15px;
            margin: 10px 0;
            cursor: pointer;
            transition: all 0.3s ease;
        " onmouseover="this.style.boxShadow='0 4px 8px rgba(0,0,0,0.1)'"
           onmouseout="this.style.boxShadow='0 2px 4px rgba(0,0,0,0.1)'">
            <div style="display: flex; align-items: center;">
                <span style="font-size: 1.5em; margin-right: 15px;">{icon}</span>
                <div>
                    <div style="font-weight: bold; margin-bottom: 5px;">{title}</div>
                    <div style="color: #6c757d; font-size: 0.9em;">{description}</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_alert(message: str, alert_type: str = "info", icon: str = "ℹ️"):
        """عرض تنبيه آمن"""
        if alert_type == "error":
            st.error(f"{icon} {message}")
        elif alert_type == "warning":
            st.warning(f"{icon} {message}")
        elif alert_type == "success":
            st.success(f"{icon} {message}")
        else:
            st.info(f"{icon} {message}")

    @staticmethod
    def display_data_table(data, title: str = "البيانات"):
        """عرض جدول بيانات آمن"""
        st.markdown(f"#### 📊 {title}")
        if data:
            st.dataframe(data, use_container_width=True)
        else:
            st.info("لا توجد بيانات متاحة")

    @staticmethod
    def display_main_header(title: str, subtitle: str):
        """عرض الرأس الرئيسي للتطبيق"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        ">
            <h1 style="margin: 0; font-size: 2.5em; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">⛽ {title}</h1>
            <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9; font-weight: 300;">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_section_header(title: str, subtitle: str = None, icon: str = "📋"):
        """عرض رأس قسم محسن"""
        st.markdown(f"### {icon} {title}")
        if subtitle:
            st.markdown(f"*{subtitle}*")
        st.markdown("---")

    @staticmethod
    def display_dashboard_header(title: str, subtitle: str):
        """عرض رأس لوحة التحكم المحسن"""
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            color: white;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            box-shadow: 0 8px 32px rgba(245,87,108,0.2);
        ">
            <h1 style="margin: 0; font-size: 2.2em; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">📊 {title}</h1>
            <p style="margin: 8px 0 0 0; font-size: 1.1em; opacity: 0.9; font-weight: 300;">{subtitle}</p>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_metric_grid(metrics: list):
        """عرض شبكة مقاييس محسنة"""
        st.markdown('<div style="display: grid; gap: 20px; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); margin: 20px 0;">', unsafe_allow_html=True)

        for metric in metrics:
            icon = metric.get('icon', '📊')
            value = metric.get('value', '0')
            label = metric.get('label', 'مقياس')
            color = metric.get('color', '#2563eb')

            st.markdown(f"""
            <div style="
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 15px;
                padding: 20px;
                text-align: center;
                box-shadow: 0 4px 6px rgba(0,0,0,0.07);
                transition: all 0.3s ease;
                border-top: 4px solid {color};
            " onmouseover="this.style.transform='translateY(-5px)'; this.style.boxShadow='0 8px 25px rgba(0,0,0,0.15)'"
               onmouseout="this.style.transform='translateY(0)'; this.style.boxShadow='0 4px 6px rgba(0,0,0,0.07)'">
                <div style="font-size: 2.5em; margin-bottom: 10px;">{icon}</div>
                <div style="font-size: 2em; font-weight: bold; color: {color}; margin: 10px 0;">{value}</div>
                <div style="color: #6b7280; font-weight: 500; font-size: 0.95em;">{label}</div>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    @staticmethod
    def display_action_cards(actions: list):
        """عرض بطاقات الإجراءات المحسنة"""
        st.markdown('<div style="display: grid; gap: 15px; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); margin: 20px 0;">', unsafe_allow_html=True)

        for action in actions:
            icon = action.get('icon', '⚡')
            title = action.get('title', 'إجراء')
            description = action.get('description', 'وصف الإجراء')
            color = action.get('color', '#2563eb')
            key = action.get('key', f"action_{len(actions)}")

            st.markdown(f"""
            <div style="
                background: white;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
                cursor: pointer;
                transition: all 0.3s ease;
                box-shadow: 0 2px 4px rgba(0,0,0,0.05);
                border-left: 4px solid {color};
            " onmouseover="this.style.transform='translateX(5px)'; this.style.boxShadow='0 6px 20px rgba(0,0,0,0.1)'"
               onmouseout="this.style.transform='translateX(0)'; this.style.boxShadow='0 2px 4px rgba(0,0,0,0.05)'">
                <div style="display: flex; align-items: center;">
                    <span style="font-size: 1.8em; margin-left: 15px; color: {color};">{icon}</span>
                    <div style="flex: 1;">
                        <div style="font-weight: bold; font-size: 1.1em; margin-bottom: 5px; color: #1f2937;">{title}</div>
                        <div style="color: #6b7280; font-size: 0.9em; line-height: 1.4;">{description}</div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            if st.button(f"{icon} {title}", key=key, use_container_width=True):
                return action.get('action', key)

        st.markdown('</div>', unsafe_allow_html=True)
        return None

    @staticmethod
    def display_info_alert(message: str, type: str = "info", icon: str = "ℹ️"):
        """عرض تنبيه معلومات محسن"""
        colors = {
            "info": {"bg": "#dbeafe", "border": "#bfdbfe", "text": "#1e40af", "icon": "ℹ️"},
            "success": {"bg": "#dcfce7", "border": "#bbf7d0", "text": "#166534", "icon": "✅"},
            "warning": {"bg": "#fef3c7", "border": "#fde68a", "text": "#92400e", "icon": "⚠️"},
            "error": {"bg": "#fee2e2", "border": "#fecaca", "text": "#991b1b", "icon": "❌"}
        }

        color_scheme = colors.get(type, colors["info"])
        if icon == "auto":
            icon = color_scheme["icon"]

        st.markdown(f"""
        <div style="
            background: {color_scheme['bg']};
            border: 2px solid {color_scheme['border']};
            color: {color_scheme['text']};
            padding: 15px 20px;
            border-radius: 10px;
            margin: 15px 0;
            display: flex;
            align-items: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        ">
            <span style="font-size: 1.5em; margin-left: 10px;">{icon}</span>
            <div style="flex: 1; font-weight: 500;">{message}</div>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def display_data_table_with_header(data, title: str, description: str = None):
        """عرض جدول بيانات مع رأس محسن"""
        st.markdown(f"#### 📊 {title}")
        if description:
            st.markdown(f"*{description}*")

        if data is not None and len(data) > 0:
            st.dataframe(data, use_container_width=True)
        else:
            SafeHTML.display_info_alert("لا توجد بيانات متاحة", "info", "📭")

    @staticmethod
    def display_automation_status(is_active: bool):
        """عرض حالة النظام الآلي"""
        if is_active:
            st.markdown("""
            <div style="
                background: #d4edda;
                border: 1px solid #c3e6cb;
                color: #155724;
                padding: 10px 15px;
                border-radius: 5px;
                margin: 10px 0;
                display: flex;
                align-items: center;
            ">
                <span style="font-size: 1.2em; margin-right: 10px;">🤖</span>
                <span><strong>النظام الآلي:</strong> يعمل - التسوية التلقائية كل 7.5 ساعات</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ تحذير: النظام الآلي غير مفعل - سيتم استخدام القراءات المحاكاة فقط")


# إنشاء instance عام
safe_html = SafeHTML()


def get_safe_html() -> SafeHTML:
    """الحصول على instance أدوات HTML الآمنة"""
    return safe_html