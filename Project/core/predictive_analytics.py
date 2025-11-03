"""
نظام الذكاء الاصطناعي للتنبؤات - Petrol Pump Management System
يوفر هذا النظام تنبؤات ذكية للمبيعات والمخزون وكشف الأنشطة الشاذة
"""

import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from collections import defaultdict
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='predictive_analytics.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class PredictiveAnalytics:
    """نظام التنبؤات الذكية"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.min_data_points = 30  # الحد الأدنى لنقاط البيانات للتنبؤ

    def predict_sales_demand(self, station_id: str, fuel_type: str,
                           days_ahead: int = 30) -> Dict[str, Any]:
        """
        التنبؤ بالطلب على المبيعات

        Args:
            station_id: معرف المحطة
            fuel_type: نوع الوقود
            days_ahead: عدد الأيام المستقبلية

        Returns:
            Dict: نتائج التنبؤ
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # الحصول على بيانات المبيعات التاريخية
            c.execute("""
                SELECT DATE(i.Date) as sale_date, SUM(i.Fuel_Amount) as daily_sales
                FROM Invoice i
                WHERE i.Petrolpump_No = %s AND i.Fuel_Type_Actual = %s
                      AND i.Date >= DATE_SUB(CURDATE(), INTERVAL 90 DAY)
                GROUP BY DATE(i.Date)
                ORDER BY sale_date
            """, (station_id, fuel_type))

            sales_data = c.fetchall()
            conn.close()

            if len(sales_data) < self.min_data_points:
                return {
                    'error': f'بيانات غير كافية. مطلوب {self.min_data_points} نقطة بيانات على الأقل',
                    'available_data_points': len(sales_data)
                }

            # تحويل البيانات إلى DataFrame
            df = pd.DataFrame(sales_data, columns=['date', 'sales'])
            df['date'] = pd.to_datetime(df['date'])
            df = df.set_index('date')

            # حساب المتوسطات المتحركة والإحصائيات
            df['ma_7'] = df['sales'].rolling(window=7).mean()
            df['ma_30'] = df['sales'].rolling(window=30).mean()
            df['std_30'] = df['sales'].rolling(window=30).std()

            # التنبؤ البسيط باستخدام المتوسط المتحرك
            last_30_avg = df['sales'].tail(30).mean()
            last_7_avg = df['sales'].tail(7).mean()

            # اتجاه التغيير
            trend = (last_7_avg - last_30_avg) / last_30_avg if last_30_avg > 0 else 0

            # التنبؤ للأيام القادمة
            predictions = []
            current_avg = last_7_avg

            for i in range(days_ahead):
                # تطبيق الاتجاه تدريجياً
                adjustment = 1 + (trend * (i + 1) / days_ahead)
                predicted_sales = current_avg * adjustment

                # إضافة تغيير عشوائي بسيط (±10%)
                variation = np.random.normal(0, 0.1)
                predicted_sales *= (1 + variation)

                # التأكد من عدم التنبؤ بقيم سلبية
                predicted_sales = max(predicted_sales, 0)

                predictions.append({
                    'date': (datetime.now() + timedelta(days=i+1)).date(),
                    'predicted_sales': round(predicted_sales, 2),
                    'confidence_level': max(0.5, 1 - abs(trend) - 0.2)  # مستوى الثقة
                })

            # تحليل الموسمية
            seasonality = self._analyze_seasonality(df)

            return {
                'station_id': station_id,
                'fuel_type': fuel_type,
                'historical_avg': round(last_30_avg, 2),
                'recent_avg': round(last_7_avg, 2),
                'trend_percentage': round(trend * 100, 2),
                'predictions': predictions,
                'seasonality': seasonality,
                'data_points': len(sales_data),
                'prediction_accuracy': self._estimate_accuracy(df)
            }

        except Exception as e:
            self.logger.error(f"Error predicting sales demand: {str(e)}")
            return {'error': str(e)}

    def optimize_inventory_levels(self, station_id: str) -> Dict[str, Any]:
        """
        تحسين مستويات المخزون

        Args:
            station_id: معرف المحطة

        Returns:
            Dict: توصيات تحسين المخزون
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # الحصول على معلومات الخزانات والمبيعات
            c.execute("""
                SELECT
                    ft.FuelTank_ID,
                    ft.Fuel_Type,
                    ft.Capacity,
                    ft.Current_Amount,
                    AVG(i.Fuel_Amount) as avg_daily_sales,
                    STD(i.Fuel_Amount) as std_daily_sales,
                    MAX(i.Fuel_Amount) as max_daily_sales
                FROM FuelTank ft
                LEFT JOIN Petrolpump p ON ft.FuelTank_ID = p.FuelTank_ID
                LEFT JOIN Invoice i ON p.Registration_No = i.Petrolpump_No
                    AND i.Fuel_Type_Actual = ft.Fuel_Type
                    AND i.Date >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                WHERE p.Registration_No = %s
                GROUP BY ft.FuelTank_ID, ft.Fuel_Type, ft.Capacity, ft.Current_Amount
            """, (station_id,))

            tank_data = c.fetchall()
            conn.close()

            if not tank_data:
                return {'error': 'لا توجد بيانات خزانات متاحة'}

            recommendations = []

            for tank in tank_data:
                tank_id, fuel_type, capacity, current_amount, avg_sales, std_sales, max_sales = tank

                if not avg_sales:
                    continue

                # حساب مستوى المخزون المثالي
                # مخزون أمان = انحراف معياري × 2
                safety_stock = (std_sales or 0) * 2

                # الطلب المتوقع للأيام القادمة (7 أيام)
                expected_demand = avg_sales * 7

                # المستوى المثالي = الطلب المتوقع + مخزون الأمان
                optimal_level = expected_demand + safety_stock

                # الحد الأدنى = 15% من السعة
                min_level = capacity * 0.15

                # الحد الأقصى = 90% من السعة
                max_level = capacity * 0.90

                # تحديد التوصية
                if current_amount < min_level:
                    recommendation = {
                        'tank_id': tank_id,
                        'fuel_type': fuel_type,
                        'current_level': current_amount,
                        'optimal_level': min(optimal_level, max_level),
                        'min_level': min_level,
                        'max_level': max_level,
                        'action': 'REFILL_URGENT',
                        'priority': 'HIGH',
                        'reason': f'المستوى الحالي ({current_amount}) أقل من الحد الأدنى ({min_level})'
                    }
                elif current_amount < optimal_level:
                    recommendation = {
                        'tank_id': tank_id,
                        'fuel_type': fuel_type,
                        'current_level': current_amount,
                        'optimal_level': min(optimal_level, max_level),
                        'min_level': min_level,
                        'max_level': max_level,
                        'action': 'REFILL_SOON',
                        'priority': 'MEDIUM',
                        'reason': f'المستوى الحالي ({current_amount}) أقل من المستوى المثالي ({optimal_level:.1f})'
                    }
                elif current_amount > max_level:
                    recommendation = {
                        'tank_id': tank_id,
                        'fuel_type': fuel_type,
                        'current_level': current_amount,
                        'optimal_level': min(optimal_level, max_level),
                        'min_level': min_level,
                        'max_level': max_level,
                        'action': 'REDUCE_STOCK',
                        'priority': 'LOW',
                        'reason': f'المستوى الحالي ({current_amount}) أعلى من الحد الأقصى ({max_level})'
                    }
                else:
                    recommendation = {
                        'tank_id': tank_id,
                        'fuel_type': fuel_type,
                        'current_level': current_amount,
                        'optimal_level': min(optimal_level, max_level),
                        'min_level': min_level,
                        'max_level': max_level,
                        'action': 'OPTIMAL',
                        'priority': 'NONE',
                        'reason': 'المستوى الحالي مثالي'
                    }

                recommendations.append(recommendation)

            return {
                'station_id': station_id,
                'recommendations': recommendations,
                'summary': {
                    'total_tanks': len(recommendations),
                    'urgent_refills': len([r for r in recommendations if r['action'] == 'REFILL_URGENT']),
                    'planned_refills': len([r for r in recommendations if r['action'] == 'REFILL_SOON']),
                    'optimal_tanks': len([r for r in recommendations if r['action'] == 'OPTIMAL'])
                }
            }

        except Exception as e:
            self.logger.error(f"Error optimizing inventory levels: {str(e)}")
            return {'error': str(e)}

    def detect_anomalies(self, data_stream: str, station_id: Optional[str] = None,
                        hours_back: int = 24) -> Dict[str, Any]:
        """
        كشف الأنشطة الشاذة والاحتيال

        Args:
            data_stream: نوع البيانات (sales, inventory, login_attempts)
            station_id: معرف المحطة (اختياري)
            hours_back: عدد الساعات الماضية للفحص

        Returns:
            Dict: الأنشطة الشاذة المكتشفة
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            anomalies = []

            if data_stream == 'sales':
                # كشف مبيعات شاذة
                query = """
                    SELECT
                        i.Invoice_No,
                        i.Date,
                        i.Fuel_Amount,
                        i.Total_Price,
                        i.Employee_ID,
                        e.Emp_Name,
                        AVG(i2.Fuel_Amount) as station_avg,
                        STD(i2.Fuel_Amount) as station_std
                    FROM Invoice i
                    JOIN Employee e ON i.Employee_ID = e.Employee_ID
                    JOIN (
                        SELECT AVG(Fuel_Amount) as avg_amount, STD(Fuel_Amount) as std_amount
                        FROM Invoice
                        WHERE Date >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                        {}
                    ) i2 ON 1=1
                    WHERE i.Date >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                    {}
                    HAVING ABS(i.Fuel_Amount - station_avg) > (2 * station_std)
                    ORDER BY i.Date DESC
                """.format(
                    "AND Petrolpump_No = %s" if station_id else "",
                    "AND i.Petrolpump_No = %s" if station_id else ""
                )

                params = [hours_back]
                if station_id:
                    params.extend([station_id, station_id])

                c.execute(query, params)
                sales_anomalies = c.fetchall()

                for anomaly in sales_anomalies:
                    anomalies.append({
                        'type': 'UNUSUAL_SALES_VOLUME',
                        'invoice_no': anomaly[0],
                        'date': anomaly[1],
                        'amount': anomaly[2],
                        'total_price': anomaly[3],
                        'employee': anomaly[5],
                        'station_avg': anomaly[6],
                        'deviation': abs(anomaly[2] - anomaly[6]),
                        'severity': 'HIGH' if abs(anomaly[2] - anomaly[6]) > 3 * anomaly[7] else 'MEDIUM'
                    })

            elif data_stream == 'inventory':
                # كشف تغييرات شاذة في المخزون
                c.execute("""
                    SELECT
                        it.Transaction_ID,
                        it.Tank_ID,
                        it.Amount,
                        it.Transaction_Date,
                        it.Employee_ID,
                        e.Emp_Name,
                        AVG(it2.Amount) as avg_transaction,
                        STD(it2.Amount) as std_transaction
                    FROM InventoryTransactions it
                    JOIN Employee e ON it.Employee_ID = e.Employee_ID
                    JOIN (
                        SELECT AVG(ABS(Amount)) as avg_amount, STD(ABS(Amount)) as std_amount
                        FROM InventoryTransactions
                        WHERE Transaction_Date >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                        AND Transaction_Type = 'SALE'
                    ) it2 ON 1=1
                    WHERE it.Transaction_Date >= DATE_SUB(NOW(), INTERVAL %s HOUR)
                    AND it.Transaction_Type = 'SALE'
                    HAVING ABS(it.Amount) > (it2.avg_amount + 3 * it2.std_amount)
                    ORDER BY it.Transaction_Date DESC
                """, (hours_back, hours_back))

                inventory_anomalies = c.fetchall()

                for anomaly in inventory_anomalies:
                    anomalies.append({
                        'type': 'UNUSUAL_INVENTORY_CHANGE',
                        'transaction_id': anomaly[0],
                        'tank_id': anomaly[1],
                        'amount': anomaly[2],
                        'date': anomaly[3],
                        'employee': anomaly[5],
                        'avg_transaction': anomaly[6],
                        'severity': 'HIGH'
                    })

            conn.close()

            return {
                'data_stream': data_stream,
                'station_id': station_id,
                'time_period_hours': hours_back,
                'anomalies_detected': len(anomalies),
                'anomalies': anomalies,
                'risk_level': 'HIGH' if len(anomalies) > 5 else 'MEDIUM' if len(anomalies) > 2 else 'LOW'
            }

        except Exception as e:
            self.logger.error(f"Error detecting anomalies: {str(e)}")
            return {'error': str(e)}

    def _analyze_seasonality(self, df: pd.DataFrame) -> Dict[str, Any]:
        """تحليل الموسمية في البيانات"""
        try:
            # تحليل اليوم من الأسبوع
            df['day_of_week'] = df.index.dayofweek
            weekly_pattern = df.groupby('day_of_week')['sales'].mean()

            # تحليل الشهر
            df['month'] = df.index.month
            monthly_pattern = df.groupby('month')['sales'].mean()

            # تحليل الساعة (إذا كانت متوفرة)
            hourly_pattern = None
            if 'hour' in df.columns:
                hourly_pattern = df.groupby('hour')['sales'].mean()

            return {
                'weekly_pattern': weekly_pattern.to_dict(),
                'monthly_pattern': monthly_pattern.to_dict(),
                'hourly_pattern': hourly_pattern.to_dict() if hourly_pattern is not None else None,
                'best_day': weekly_pattern.idxmax(),
                'worst_day': weekly_pattern.idxmin(),
                'best_month': monthly_pattern.idxmax(),
                'seasonal_strength': self._calculate_seasonal_strength(weekly_pattern)
            }

        except Exception as e:
            self.logger.error(f"Error analyzing seasonality: {str(e)}")
            return {}

    def _calculate_seasonal_strength(self, pattern) -> float:
        """حساب قوة الموسمية"""
        try:
            mean_value = pattern.mean()
            if mean_value == 0:
                return 0

            variation = ((pattern - mean_value) ** 2).mean() ** 0.5
            return min(variation / mean_value, 1.0)  # تطبيع إلى 0-1
        except:
            return 0

    def _estimate_accuracy(self, df: pd.DataFrame) -> float:
        """تقدير دقة التنبؤ"""
        try:
            # حساب دقة بسيطة باستخدام cross-validation بسيط
            if len(df) < 20:
                return 0.5  # دقة افتراضية

            # تقسيم البيانات
            train_size = int(len(df) * 0.8)
            train_data = df[:train_size]
            test_data = df[train_size:]

            # تنبؤ بسيط
            ma_predictions = train_data['sales'].rolling(window=7).mean().iloc[-len(test_data):]

            # حساب MAPE
            mape = np.mean(np.abs((test_data['sales'].values - ma_predictions.values) / test_data['sales'].values)) * 100

            # تحويل إلى دقة (0-1)
            accuracy = max(0, 1 - mape / 100)
            return round(accuracy, 2)

        except Exception as e:
            self.logger.error(f"Error estimating accuracy: {str(e)}")
            return 0.5

# إنشاء instance عالمي
predictive_analytics = PredictiveAnalytics()

# دوال مساعدة للاستخدام في Streamlit
def display_sales_predictions(station_id: Optional[str] = None, fuel_type: Optional[str] = None, days_ahead: int = 30):
    """عرض تنبؤات المبيعات في Streamlit"""
    st.subheader("🔮 تنبؤات المبيعات")

    if not station_id:
        # اختيار المحطة
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Registration_No, Petrolpump_Name, City FROM Petrolpump ORDER BY Petrolpump_Name")
            stations = c.fetchall()
            conn.close()

            if not stations:
                st.info("لا توجد محطات مسجلة")
                return

            station_options = {f"{name} - {city} ({reg_no})": reg_no for reg_no, name, city in stations}
            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="predict_station")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    if not fuel_type:
        # اختيار نوع الوقود
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT DISTINCT Fuel_Type_Actual FROM Invoice WHERE Fuel_Type_Actual IS NOT NULL ORDER BY Fuel_Type_Actual")
            fuel_types = [row[0] for row in c.fetchall()]
            conn.close()

            if not fuel_types:
                st.info("لا توجد أنواع وقود متاحة")
                return

            fuel_type = st.selectbox("اختر نوع الوقود:", fuel_types, key="predict_fuel")

        except Exception as e:
            st.error(f"خطأ في تحميل أنواع الوقود: {str(e)}")
            return

    # إجراء التنبؤ
    with st.spinner("جاري إجراء التنبؤ..."):
        prediction = predictive_analytics.predict_sales_demand(station_id, fuel_type, days_ahead)

    if 'error' in prediction:
        st.error(prediction['error'])
        return

    # عرض النتائج
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("متوسط المبيعات (30 يوم)", f"{prediction['historical_avg']:.1f} لتر")

    with col2:
        st.metric("متوسط المبيعات (7 أيام)", f"{prediction['recent_avg']:.1f} لتر")

    with col3:
        trend = prediction['trend_percentage']
        st.metric("اتجاه التغيير", f"{trend:+.1f}%",
                 delta=f"{trend:+.1f}%" if abs(trend) > 1 else "مستقر")

    # عرض التنبؤات
    st.subheader("التنبؤات للأيام القادمة")

    pred_df = pd.DataFrame(prediction['predictions'])
    pred_df['date'] = pd.to_datetime(pred_df['date'])

    # رسم التنبؤات
    st.line_chart(pred_df.set_index('date')['predicted_sales'])

    # جدول التفاصيل
    st.dataframe(pred_df)

    # معلومات إضافية
    with st.expander("معلومات إضافية"):
        st.write(f"**عدد نقاط البيانات:** {prediction['data_points']}")
        st.write(f"**دقة التنبؤ المقدرة:** {prediction['prediction_accuracy']:.1%}")

        if prediction.get('seasonality'):
            season = prediction['seasonality']
            st.write(f"**أفضل يوم في الأسبوع:** {season.get('best_day', 'غير محدد')}")
            st.write(f"**أسوأ يوم في الأسبوع:** {season.get('worst_day', 'غير محدد')}")

def display_inventory_optimization(station_id: Optional[str] = None):
    """عرض تحسين المخزون في Streamlit"""
    st.subheader("📦 تحسين مستويات المخزون")

    if not station_id:
        # اختيار المحطة
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Registration_No, Petrolpump_Name, City FROM Petrolpump ORDER BY Petrolpump_Name")
            stations = c.fetchall()
            conn.close()

            if not stations:
                st.info("لا توجد محطات مسجلة")
                return

            station_options = {f"{name} - {city} ({reg_no})": reg_no for reg_no, name, city in stations}
            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="optimize_station")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    # إجراء التحسين
    with st.spinner("جاري تحليل المخزون..."):
        optimization = predictive_analytics.optimize_inventory_levels(station_id)

    if 'error' in optimization:
        st.error(optimization['error'])
        return

    # ملخص النتائج
    summary = optimization['summary']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("إجمالي الخزانات", summary['total_tanks'])

    with col2:
        urgent = summary['urgent_refills']
        st.metric("خزانات تحتاج تعبئة عاجلة", urgent, delta=f"🚨 {urgent}" if urgent > 0 else "✅")

    with col3:
        planned = summary['planned_refills']
        st.metric("خزانات تحتاج تعبئة قريباً", planned, delta=f"⚠️ {planned}" if planned > 0 else "✅")

    with col4:
        optimal = summary['optimal_tanks']
        st.metric("خزانات في المستوى المثالي", optimal, delta=f"✅ {optimal}")

    # تفاصيل كل خزان
    st.subheader("توصيات مفصلة لكل خزان")

    for rec in optimization['recommendations']:
        status_colors = {
            'REFILL_URGENT': '🔴',
            'REFILL_SOON': '🟠',
            'OPTIMAL': '🟢',
            'REDUCE_STOCK': '🔵'
        }

        with st.expander(f"{status_colors.get(rec['action'], '⚪')} خزان {rec['tank_id']} - {rec['fuel_type']}"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**المستوى الحالي:** {rec['current_level']} لتر")
                st.write(f"**المستوى المثالي:** {rec['optimal_level']:.1f} لتر")

            with col2:
                st.write(f"**الحد الأدنى:** {rec['min_level']:.1f} لتر")
                st.write(f"**الحد الأقصى:** {rec['max_level']:.1f} لتر")

            with col3:
                priority_colors = {'HIGH': '🔴', 'MEDIUM': '🟠', 'LOW': '🟢', 'NONE': '⚪'}
                st.write(f"**الأولوية:** {priority_colors.get(rec['priority'], '⚪')} {rec['priority']}")
                st.write(f"**الإجراء المطلوب:** {rec['action'].replace('_', ' ')}")

            st.info(rec['reason'])

def display_anomaly_detection(data_stream: str = 'sales', station_id: Optional[str] = None, hours_back: int = 24):
    """عرض كشف الأنشطة الشاذة في Streamlit"""
    st.subheader("🚨 كشف الأنشطة الشاذة")

    # اختيار نوع البيانات
    stream_options = {
        'sales': 'مبيعات',
        'inventory': 'مخزون',
        'login_attempts': 'محاولات تسجيل الدخول'
    }

    selected_stream = st.selectbox("اختر نوع البيانات:", list(stream_options.keys()),
                                  format_func=lambda x: stream_options[x], key="anomaly_stream")

    if selected_stream == 'sales' and not station_id:
        # اختيار المحطة للمبيعات
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Registration_No, Petrolpump_Name, City FROM Petrolpump ORDER BY Petrolpump_Name")
            stations = c.fetchall()
            conn.close()

            station_options = {f"{name} - {city} ({reg_no})": reg_no for reg_no, name, city in stations}
            station_options["جميع المحطات"] = None

            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="anomaly_station")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    # إجراء الكشف
    with st.spinner("جاري فحص الأنشطة الشاذة..."):
        anomalies = predictive_analytics.detect_anomalies(selected_stream, station_id, hours_back)

    if 'error' in anomalies:
        st.error(anomalies['error'])
        return

    # عرض النتائج
    risk_colors = {'HIGH': '🔴', 'MEDIUM': '🟠', 'LOW': '🟢'}

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("نوع البيانات", stream_options[selected_stream])

    with col2:
        detected = anomalies['anomalies_detected']
        st.metric("الأنشطة الشاذة المكتشفة", detected, delta=f"{risk_colors.get(anomalies['risk_level'], '⚪')} {detected}")

    with col3:
        st.metric("مستوى المخاطر", f"{risk_colors.get(anomalies['risk_level'], '⚪')} {anomalies['risk_level']}")

    # عرض التفاصيل
    if anomalies['anomalies']:
        st.subheader("تفاصيل الأنشطة الشاذة")

        for anomaly in anomalies['anomalies'][:10]:  # عرض أول 10 فقط
            severity_color = '🔴' if anomaly.get('severity') == 'HIGH' else '🟠' if anomaly.get('severity') == 'MEDIUM' else '🟢'

            with st.expander(f"{severity_color} {anomaly['type']} - {anomaly.get('date', 'غير محدد')}"):
                if anomaly['type'] == 'UNUSUAL_SALES_VOLUME':
                    st.write(f"**رقم الفاتورة:** {anomaly['invoice_no']}")
                    st.write(f"**الكمية:** {anomaly['amount']} لتر")
                    st.write(f"**الإجمالي:** {anomaly['total_price']} ريال")
                    st.write(f"**الموظف:** {anomaly['employee']}")
                    st.write(f"**متوسط المحطة:** {anomaly['station_avg']:.1f} لتر")
                    st.write(f"**الانحراف:** {anomaly['deviation']:.1f} لتر")

                elif anomaly['type'] == 'UNUSUAL_INVENTORY_CHANGE':
                    st.write(f"**رقم الحركة:** {anomaly['transaction_id']}")
                    st.write(f"**الخزان:** {anomaly['tank_id']}")
                    st.write(f"**الكمية:** {anomaly['amount']} لتر")
                    st.write(f"**الموظف:** {anomaly['employee']}")
                    st.write(f"**متوسط الحركات:** {anomaly['avg_transaction']:.1f} لتر")

                st.write(f"**مستوى الخطورة:** {severity_color} {anomaly.get('severity', 'غير محدد')}")
    else:
        st.success("✅ لم يتم اكتشاف أي أنشطة شاذة في الفترة المحددة")