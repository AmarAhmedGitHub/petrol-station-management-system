"""
نظام إدارة الجودة والصيانة التنبؤية - Petrol Pump Management System
يوفر هذا النظام مراقبة المعدات وصيانة تنبؤية وفحص الجودة
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
    filename='predictive_maintenance.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class PredictiveMaintenance:
    """نظام الصيانة التنبؤية"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # معايير الصيانة للمعدات
        self.maintenance_thresholds = {
            'pump': {
                'operating_hours': 2000,  # ساعات التشغيل قبل الصيانة
                'temperature_threshold': 80,  # درجة الحرارة (°C)
                'vibration_threshold': 5.0,  # مستوى الاهتزاز
                'pressure_threshold': 100,  # ضغط غير طبيعي (PSI)
            },
            'tank': {
                'inspection_interval_days': 90,  # فحص كل 90 يوم
                'corrosion_threshold': 2.0,  # سمك التآكل (mm)
                'leakage_threshold': 0.1,  # معدل التسرب (لتر/ساعة)
            },
            'sensor': {
                'calibration_interval_days': 180,  # معايرة كل 180 يوم
                'accuracy_threshold': 0.05,  # دقة القياس (5%)
                'response_time_threshold': 2.0,  # وقت الاستجابة (ثانية)
            }
        }

    def monitor_equipment_health(self, equipment_id: str, equipment_type: str) -> Dict[str, Any]:
        """
        مراقبة حالة المعدات

        Args:
            equipment_id: معرف المعدات
            equipment_type: نوع المعدات (pump, tank, sensor)

        Returns:
            Dict: حالة المعدات
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            health_status = {
                'equipment_id': equipment_id,
                'equipment_type': equipment_type,
                'overall_health': 'UNKNOWN',
                'issues': [],
                'recommendations': [],
                'next_maintenance': None,
                'risk_level': 'LOW'
            }

            if equipment_type == 'pump':
                health_status.update(self._monitor_pump_health(c, equipment_id))
            elif equipment_type == 'tank':
                health_status.update(self._monitor_tank_health(c, equipment_id))
            elif equipment_type == 'sensor':
                health_status.update(self._monitor_sensor_health(c, equipment_id))

            conn.close()

            # تحديد المستوى العام للصحة
            if health_status['issues']:
                critical_issues = len([i for i in health_status['issues'] if i['severity'] == 'CRITICAL'])
                high_issues = len([i for i in health_status['issues'] if i['severity'] == 'HIGH'])

                if critical_issues > 0:
                    health_status['overall_health'] = 'CRITICAL'
                    health_status['risk_level'] = 'CRITICAL'
                elif high_issues > 0:
                    health_status['overall_health'] = 'POOR'
                    health_status['risk_level'] = 'HIGH'
                else:
                    health_status['overall_health'] = 'FAIR'
                    health_status['risk_level'] = 'MEDIUM'
            else:
                health_status['overall_health'] = 'EXCELLENT'
                health_status['risk_level'] = 'LOW'

            return health_status

        except Exception as e:
            self.logger.error(f"Error monitoring equipment health: {str(e)}")
            return {'error': str(e)}

    def _monitor_pump_health(self, cursor, pump_id: str) -> Dict[str, Any]:
        """مراقبة حالة مضخة الوقود"""
        try:
            # الحصول على بيانات التشغيل الأخيرة
            cursor.execute("""
                SELECT
                    Reading_ID,
                    Level,
                    Timestamp,
                    Sensor_Type
                FROM SensorReadings
                WHERE Pump_ID = %s
                ORDER BY Timestamp DESC
                LIMIT 100
            """, (pump_id,))

            readings = cursor.fetchall()

            if not readings:
                return {
                    'issues': [{'description': 'لا توجد بيانات استشعار متاحة', 'severity': 'MEDIUM'}],
                    'recommendations': ['تثبيت أجهزة استشعار للمراقبة المستمرة']
                }

            # تحليل البيانات
            df = pd.DataFrame(readings, columns=['id', 'level', 'timestamp', 'sensor_type'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            issues = []
            recommendations = []

            # فحص درجة الحرارة (إذا كانت متوفرة)
            temp_readings = df[df['sensor_type'] == 'TEMPERATURE']
            if not temp_readings.empty:
                avg_temp = temp_readings['level'].mean()
                max_temp = temp_readings['level'].max()

                if max_temp > self.maintenance_thresholds['pump']['temperature_threshold']:
                    issues.append({
                        'description': f'درجة حرارة عالية: {max_temp}°C (الحد: {self.maintenance_thresholds["pump"]["temperature_threshold"]}°C)',
                        'severity': 'HIGH'
                    })
                    recommendations.append('فحص نظام التبريد واستبدال المراوح إذا لزم الأمر')

            # فحص الاهتزاز (إذا كان متوفراً)
            vibration_readings = df[df['sensor_type'] == 'VIBRATION']
            if not vibration_readings.empty:
                avg_vibration = vibration_readings['level'].mean()

                if avg_vibration > self.maintenance_thresholds['pump']['vibration_threshold']:
                    issues.append({
                        'description': f'اهتزاز عالي: {avg_vibration} (الحد: {self.maintenance_thresholds["pump"]["vibration_threshold"]})',
                        'severity': 'HIGH'
                    })
                    recommendations.append('فحص المحامل والأجزاء المتحركة')

            # حساب ساعات التشغيل التقريبية
            time_span = df['timestamp'].max() - df['timestamp'].min()
            operating_hours = time_span.total_seconds() / 3600

            if operating_hours > self.maintenance_thresholds['pump']['operating_hours']:
                issues.append({
                    'description': f'ساعات التشغيل العالية: {operating_hours:.0f} ساعة',
                    'severity': 'MEDIUM'
                })
                recommendations.append('إجراء صيانة دورية شاملة')

            # تحديد موعد الصيانة التالية
            next_maintenance = datetime.now() + timedelta(days=30)  # صيانة شهرية افتراضية

            return {
                'issues': issues,
                'recommendations': recommendations,
                'next_maintenance': next_maintenance,
                'operating_hours': operating_hours,
                'last_reading': df['timestamp'].max() if not df.empty else None
            }

        except Exception as e:
            self.logger.error(f"Error monitoring pump health: {str(e)}")
            return {'issues': [{'description': f'خطأ في المراقبة: {str(e)}', 'severity': 'CRITICAL'}]}

    def _monitor_tank_health(self, cursor, tank_id: str) -> Dict[str, Any]:
        """مراقبة حالة خزان الوقود"""
        try:
            # الحصول على معلومات الخزان
            cursor.execute("""
                SELECT
                    Fuel_Type,
                    Capacity,
                    Current_Amount,
                    FuelTank_ID
                FROM FuelTank
                WHERE FuelTank_ID = %s
            """, (tank_id,))

            tank_info = cursor.fetchone()

            if not tank_info:
                return {'issues': [{'description': 'الخزان غير موجود', 'severity': 'CRITICAL'}]}

            fuel_type, capacity, current_amount, tank_id = tank_info

            issues = []
            recommendations = []

            # فحص مستوى التعبئة
            fill_percentage = (current_amount / capacity) * 100 if capacity > 0 else 0

            if fill_percentage < 10:
                issues.append({
                    'description': f'مستوى الوقود منخفض جداً: {fill_percentage:.1f}%',
                    'severity': 'HIGH'
                })
                recommendations.append('تعبئة الخزان فوراً')

            # فحص آخر فحص
            cursor.execute("""
                SELECT MAX(Created_Date)
                FROM InventoryAlerts
                WHERE Tank_ID = %s AND Alert_Type = 'TANK_INSPECTION'
            """, (tank_id,))

            last_inspection = cursor.fetchone()[0]

            if last_inspection:
                days_since_inspection = (datetime.now() - last_inspection).days
                inspection_interval = self.maintenance_thresholds['tank']['inspection_interval_days']

                if days_since_inspection > inspection_interval:
                    issues.append({
                        'description': f'تأخر الفحص الدوري: {days_since_inspection} يوم (الفترة: {inspection_interval} يوم)',
                        'severity': 'MEDIUM'
                    })
                    recommendations.append('إجراء فحص دوري شامل للخزان')
            else:
                issues.append({
                    'description': 'لم يتم إجراء فحص دوري للخزان',
                    'severity': 'MEDIUM'
                })
                recommendations.append('إجراء فحص دوري أولي للخزان')

            # تحديد موعد الصيانة التالية
            next_maintenance = datetime.now() + timedelta(days=self.maintenance_thresholds['tank']['inspection_interval_days'])

            return {
                'issues': issues,
                'recommendations': recommendations,
                'next_maintenance': next_maintenance,
                'fill_percentage': fill_percentage,
                'last_inspection': last_inspection
            }

        except Exception as e:
            self.logger.error(f"Error monitoring tank health: {str(e)}")
            return {'issues': [{'description': f'خطأ في المراقبة: {str(e)}', 'severity': 'CRITICAL'}]}

    def _monitor_sensor_health(self, cursor, sensor_id: str) -> Dict[str, Any]:
        """مراقبة حالة أجهزة الاستشعار"""
        try:
            # الحصول على قراءات الاستشعار الأخيرة
            cursor.execute("""
                SELECT
                    Reading_ID,
                    Level,
                    Timestamp,
                    Sensor_Type
                FROM SensorReadings
                WHERE Reading_ID LIKE %s
                ORDER BY Timestamp DESC
                LIMIT 50
            """, (f"{sensor_id}%",))

            readings = cursor.fetchall()

            issues = []
            recommendations = []

            if not readings:
                return {
                    'issues': [{'description': 'لا توجد قراءات متاحة للاستشعار', 'severity': 'HIGH'}],
                    'recommendations': ['فحص اتصال الاستشعار وتشغيله']
                }

            df = pd.DataFrame(readings, columns=['id', 'level', 'timestamp', 'sensor_type'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])

            # فحص استمرارية القراءات
            time_diffs = df['timestamp'].diff().dt.total_seconds()
            avg_interval = time_diffs.mean()

            if avg_interval > 3600:  # أكثر من ساعة بين القراءات
                issues.append({
                    'description': f'انقطاع في القراءات: متوسط الفاصل {avg_interval/60:.1f} دقيقة',
                    'severity': 'MEDIUM'
                })
                recommendations.append('فحص اتصال الاستشعار والبطارية')

            # فحص دقة القراءات (تباين عالي)
            std_dev = df['level'].std()
            mean_val = df['level'].mean()

            if mean_val > 0 and (std_dev / mean_val) > 0.1:  # تباين أكثر من 10%
                issues.append({
                    'description': f'عدم استقرار في القراءات: انحراف معياري {std_dev:.2f}',
                    'severity': 'MEDIUM'
                })
                recommendations.append('معايرة الاستشعار أو استبداله')

            # فحص آخر معايرة
            cursor.execute("""
                SELECT MAX(Created_Date)
                FROM InventoryAlerts
                WHERE Tank_ID = %s AND Alert_Type = 'SENSOR_CALIBRATION'
            """, (sensor_id,))

            last_calibration = cursor.fetchone()[0]

            if last_calibration:
                days_since_calibration = (datetime.now() - last_calibration).days
                calibration_interval = self.maintenance_thresholds['sensor']['calibration_interval_days']

                if days_since_calibration > calibration_interval:
                    issues.append({
                        'description': f'حاجة لمعايرة: مر {days_since_calibration} يوم (الفترة: {calibration_interval} يوم)',
                        'severity': 'LOW'
                    })
                    recommendations.append('إجراء معايرة دورية للاستشعار')
            else:
                issues.append({
                    'description': 'لم يتم معايرة الاستشعار',
                    'severity': 'LOW'
                })
                recommendations.append('إجراء معايرة أولية للاستشعار')

            # تحديد موعد الصيانة التالية
            next_maintenance = datetime.now() + timedelta(days=self.maintenance_thresholds['sensor']['calibration_interval_days'])

            return {
                'issues': issues,
                'recommendations': recommendations,
                'next_maintenance': next_maintenance,
                'last_reading': df['timestamp'].max() if not df.empty else None,
                'readings_count': len(readings),
                'avg_interval_minutes': avg_interval / 60 if avg_interval else None
            }

        except Exception as e:
            self.logger.error(f"Error monitoring sensor health: {str(e)}")
            return {'issues': [{'description': f'خطأ في المراقبة: {str(e)}', 'severity': 'CRITICAL'}]}

    def schedule_maintenance(self, station_id: str) -> Dict[str, Any]:
        """
        جدولة الصيانة للمحطة

        Args:
            station_id: معرف المحطة

        Returns:
            Dict: جدول الصيانة
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # الحصول على جميع المعدات في المحطة
            c.execute("""
                SELECT DISTINCT
                    'pump' as equipment_type,
                    Registration_No as equipment_id,
                    Petrolpump_Name as equipment_name
                FROM Petrolpump
                WHERE Registration_No = %s

                UNION ALL

                SELECT DISTINCT
                    'tank' as equipment_type,
                    FuelTank_ID as equipment_id,
                    CONCAT('خزان ', Fuel_Type) as equipment_name
                FROM FuelTank ft
                JOIN Petrolpump p ON ft.FuelTank_ID = p.FuelTank_ID
                WHERE p.Registration_No = %s

                UNION ALL

                SELECT DISTINCT
                    'sensor' as equipment_type,
                    CONCAT('SENSOR_', Pump_ID) as equipment_id,
                    CONCAT('استشعار ', Pump_ID) as equipment_name
                FROM SensorReadings
                WHERE Pump_ID = %s
                GROUP BY Pump_ID
            """, (station_id, station_id, station_id))

            equipment = c.fetchall()
            conn.close()

            maintenance_schedule = []

            for eq_type, eq_id, eq_name in equipment:
                health = self.monitor_equipment_health(eq_id, eq_type)

                if 'error' not in health:
                    maintenance_item = {
                        'equipment_id': eq_id,
                        'equipment_name': eq_name,
                        'equipment_type': eq_type,
                        'health_status': health.get('overall_health', 'UNKNOWN'),
                        'risk_level': health.get('risk_level', 'UNKNOWN'),
                        'next_maintenance': health.get('next_maintenance'),
                        'issues_count': len(health.get('issues', [])),
                        'recommendations': health.get('recommendations', [])
                    }
                    maintenance_schedule.append(maintenance_item)

            # ترتيب حسب مستوى المخاطر
            risk_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3, 'UNKNOWN': 4}
            maintenance_schedule.sort(key=lambda x: risk_order.get(x['risk_level'], 4))

            return {
                'station_id': station_id,
                'maintenance_schedule': maintenance_schedule,
                'summary': {
                    'total_equipment': len(maintenance_schedule),
                    'critical_risk': len([m for m in maintenance_schedule if m['risk_level'] == 'CRITICAL']),
                    'high_risk': len([m for m in maintenance_schedule if m['risk_level'] == 'HIGH']),
                    'needs_attention': len([m for m in maintenance_schedule if m['risk_level'] in ['CRITICAL', 'HIGH']])
                }
            }

        except Exception as e:
            self.logger.error(f"Error scheduling maintenance: {str(e)}")
            return {'error': str(e)}

    def quality_control_checks(self, fuel_sample: Dict[str, Any]) -> Dict[str, Any]:
        """
        فحص جودة الوقود

        Args:
            fuel_sample: عينة الوقود المراد فحصها

        Returns:
            Dict: نتائج فحص الجودة
        """
        try:
            # معايير جودة الوقود (قيم افتراضية - يمكن تخصيصها)
            quality_standards = {
                'density': {'min': 0.75, 'max': 0.85},  # كجم/لتر
                'viscosity': {'min': 2.0, 'max': 4.5},  # cSt
                'flash_point': {'min': 40, 'max': 60},  # °C
                'water_content': {'max': 0.02},  # %
                'sediment': {'max': 0.005},  # %
                'sulfur_content': {'max': 0.001}  # %
            }

            quality_results = {
                'sample_id': fuel_sample.get('sample_id', 'UNKNOWN'),
                'fuel_type': fuel_sample.get('fuel_type', 'UNKNOWN'),
                'test_date': datetime.now(),
                'overall_quality': 'PASS',
                'tests': [],
                'recommendations': []
            }

            failed_tests = 0

            # إجراء الفحوصات
            for test_name, standards in quality_standards.items():
                if test_name in fuel_sample:
                    measured_value = fuel_sample[test_name]
                    test_result = {'test_name': test_name, 'measured_value': measured_value, 'status': 'PASS'}

                    # فحص الحدود
                    if 'min' in standards and measured_value < standards['min']:
                        test_result['status'] = 'FAIL'
                        test_result['reason'] = f'أقل من الحد الأدنى ({standards["min"]})'
                        failed_tests += 1

                    elif 'max' in standards and measured_value > standards['max']:
                        test_result['status'] = 'FAIL'
                        test_result['reason'] = f'أعلى من الحد الأقصى ({standards["max"]})'
                        failed_tests += 1

                    quality_results['tests'].append(test_result)

            # تحديد الجودة العامة
            if failed_tests == 0:
                quality_results['overall_quality'] = 'EXCELLENT'
            elif failed_tests <= 2:
                quality_results['overall_quality'] = 'GOOD'
                quality_results['recommendations'].append('تحسين طفيف مطلوب')
            else:
                quality_results['overall_quality'] = 'FAIL'
                quality_results['recommendations'].append('الوقود غير مطابق للمواصفات - لا يصلح للاستخدام')

            # توصيات إضافية
            if quality_results['overall_quality'] == 'FAIL':
                quality_results['recommendations'].extend([
                    'إجراء تنقية للوقود',
                    'فحص نظام التخزين',
                    'التحقق من جودة المورد'
                ])

            return quality_results

        except Exception as e:
            self.logger.error(f"Error in quality control checks: {str(e)}")
            return {'error': str(e)}

# إنشاء instance عالمي
predictive_maintenance = PredictiveMaintenance()

# دوال مساعدة للاستخدام في Streamlit
def display_equipment_health(equipment_id: Optional[str] = None, equipment_type: Optional[str] = 'pump'):
    """عرض حالة المعدات في Streamlit"""
    st.subheader("🔧 مراقبة حالة المعدات")

    if not equipment_id:
        # اختيار المعدات
        equipment_types = {
            'pump': 'مضخة وقود',
            'tank': 'خزان وقود',
            'sensor': 'جهاز استشعار'
        }

        selected_type = st.selectbox("اختر نوع المعدات:", list(equipment_types.keys()),
                                    format_func=lambda x: equipment_types[x], key="equipment_type")

        # الحصول على قائمة المعدات المتاحة
        try:
            conn = get_connection()
            c = conn.cursor()

            if selected_type == 'pump':
                c.execute("SELECT Registration_No, Petrolpump_Name FROM Petrolpump ORDER BY Petrolpump_Name")
                equipment_list = [(row[0], f"{row[1]} (مضخة)") for row in c.fetchall()]
            elif selected_type == 'tank':
                c.execute("SELECT FuelTank_ID, Fuel_Type FROM FuelTank ORDER BY FuelTank_ID")
                equipment_list = [(row[0], f"خزان {row[0]} - {row[1]}") for row in c.fetchall()]
            else:  # sensor
                c.execute("SELECT DISTINCT Pump_ID FROM SensorReadings WHERE Pump_ID IS NOT NULL")
                equipment_list = [(row[0], f"استشعار {row[0]}") for row in c.fetchall()]

            conn.close()

            if not equipment_list:
                st.info(f"لا توجد {equipment_types[selected_type]} متاحة")
                return

            equipment_options = {name: id for id, name in equipment_list}
            selected_equipment = st.selectbox("اختر المعدات:", list(equipment_options.keys()), key="equipment_select")
            equipment_id = equipment_options[selected_equipment]
            equipment_type = selected_type

        except Exception as e:
            st.error(f"خطأ في تحميل المعدات: {str(e)}")
            return

    # مراقبة الحالة
    with st.spinner("جاري فحص حالة المعدات..."):
        health_status = predictive_maintenance.monitor_equipment_health(equipment_id, equipment_type)

    if 'error' in health_status:
        st.error(health_status['error'])
        return

    # عرض النتائج
    health_colors = {
        'EXCELLENT': '🟢',
        'GOOD': '🟢',
        'FAIR': '🟡',
        'POOR': '🟠',
        'CRITICAL': '🔴',
        'UNKNOWN': '⚪'
    }

    risk_colors = {
        'CRITICAL': '🔴',
        'HIGH': '🟠',
        'MEDIUM': '🟡',
        'LOW': '🟢',
        'UNKNOWN': '⚪'
    }

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("الحالة العامة", f"{health_colors.get(health_status['overall_health'], '⚪')} {health_status['overall_health']}")

    with col2:
        st.metric("مستوى المخاطر", f"{risk_colors.get(health_status['risk_level'], '⚪')} {health_status['risk_level']}")

    with col3:
        issues_count = len(health_status.get('issues', []))
        st.metric("عدد المشاكل", issues_count, delta=f"⚠️ {issues_count}" if issues_count > 0 else "✅")

    # عرض المشاكل
    if health_status.get('issues'):
        st.subheader("المشاكل المكتشفة")
        for issue in health_status['issues']:
            severity_color = '🔴' if issue['severity'] == 'CRITICAL' else '🟠' if issue['severity'] == 'HIGH' else '🟡'
            st.error(f"{severity_color} {issue['description']}")

    # عرض التوصيات
    if health_status.get('recommendations'):
        st.subheader("التوصيات")
        for rec in health_status['recommendations']:
            st.info(f"💡 {rec}")

    # معلومات إضافية
    with st.expander("معلومات إضافية"):
        if health_status.get('next_maintenance'):
            st.write(f"**موعد الصيانة التالية:** {health_status['next_maintenance'].strftime('%Y-%m-%d %H:%M')}")

        if health_status.get('operating_hours'):
            st.write(f"**ساعات التشغيل:** {health_status['operating_hours']:.0f} ساعة")

        if health_status.get('last_reading'):
            st.write(f"**آخر قراءة:** {health_status['last_reading'].strftime('%Y-%m-%d %H:%M')}")

        if health_status.get('fill_percentage') is not None:
            st.write(f"**نسبة التعبئة:** {health_status['fill_percentage']:.1f}%")

def display_maintenance_schedule(station_id: Optional[str] = None):
    """عرض جدول الصيانة في Streamlit"""
    st.subheader("📅 جدول الصيانة")

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
            selected_station = st.selectbox("اختر المحطة:", list(station_options.keys()), key="maintenance_station")
            station_id = station_options[selected_station]

        except Exception as e:
            st.error(f"خطأ في تحميل المحطات: {str(e)}")
            return

    # إنشاء جدول الصيانة
    with st.spinner("جاري إنشاء جدول الصيانة..."):
        schedule = predictive_maintenance.schedule_maintenance(station_id)

    if 'error' in schedule:
        st.error(schedule['error'])
        return

    # ملخص
    summary = schedule['summary']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("إجمالي المعدات", summary['total_equipment'])

    with col2:
        critical = summary['critical_risk']
        st.metric("مخاطر حرجة", critical, delta=f"🔴 {critical}" if critical > 0 else "✅")

    with col3:
        high = summary['high_risk']
        st.metric("مخاطر عالية", high, delta=f"🟠 {high}" if high > 0 else "✅")

    with col4:
        attention = summary['needs_attention']
        st.metric("يحتاج انتباه", attention, delta=f"⚠️ {attention}" if attention > 0 else "✅")

    # جدول الصيانة التفصيلي
    st.subheader("جدول الصيانة التفصيلي")

    for item in schedule['maintenance_schedule']:
        risk_color = {
            'CRITICAL': '🔴',
            'HIGH': '🟠',
            'MEDIUM': '🟡',
            'LOW': '🟢',
            'UNKNOWN': '⚪'
        }.get(item['risk_level'], '⚪')

        health_color = {
            'EXCELLENT': '🟢',
            'GOOD': '🟢',
            'FAIR': '🟡',
            'POOR': '🟠',
            'CRITICAL': '🔴',
            'UNKNOWN': '⚪'
        }.get(item['health_status'], '⚪')

        with st.expander(f"{risk_color} {item['equipment_name']} ({item['equipment_type']})"):
            col1, col2, col3 = st.columns(3)

            with col1:
                st.write(f"**الحالة:** {health_color} {item['health_status']}")
                st.write(f"**مستوى المخاطر:** {risk_color} {item['risk_level']}")

            with col2:
                st.write(f"**عدد المشاكل:** {item['issues_count']}")
                if item['next_maintenance']:
                    st.write(f"**الصيانة التالية:** {item['next_maintenance'].strftime('%Y-%m-%d')}")

            with col3:
                if item['recommendations']:
                    st.write("**التوصيات:**")
                    for rec in item['recommendations'][:3]:  # أول 3 توصيات
                        st.write(f"• {rec}")
                else:
                    st.write("**التوصيات:** لا توجد توصيات")

def perform_quality_control():
    """إجراء فحص جودة الوقود في Streamlit"""
    st.subheader("🧪 فحص جودة الوقود")

    # نموذج إدخال عينة الوقود
    with st.form("quality_control_form"):
        st.write("أدخل بيانات عينة الوقود:")

        col1, col2 = st.columns(2)

        with col1:
            sample_id = st.text_input("رقم العينة:", key="sample_id")
            fuel_type = st.selectbox("نوع الوقود:", ["بنزين 91", "بنزين 95", "ديزل", "غاز"], key="fuel_type")
            density = st.number_input("الكثافة (كجم/لتر):", min_value=0.0, max_value=2.0, step=0.001, key="density")
            viscosity = st.number_input("اللزوجة (cSt):", min_value=0.0, max_value=10.0, step=0.01, key="viscosity")

        with col2:
            flash_point = st.number_input("نقطة الوميض (°C):", min_value=0, max_value=100, key="flash_point")
            water_content = st.number_input("محتوى الماء (%):", min_value=0.0, max_value=10.0, step=0.001, key="water_content")
            sediment = st.number_input("الرواسب (%):", min_value=0.0, max_value=10.0, step=0.001, key="sediment")
            sulfur_content = st.number_input("محتوى الكبريت (%):", min_value=0.0, max_value=10.0, step=0.0001, key="sulfur_content")

        submitted = st.form_submit_button("إجراء الفحص", use_container_width=True)

        if submitted:
            if not sample_id:
                st.error("يرجى إدخال رقم العينة")
                return

            # إنشاء عينة الوقود
            fuel_sample = {
                'sample_id': sample_id,
                'fuel_type': fuel_type,
                'density': density,
                'viscosity': viscosity,
                'flash_point': flash_point,
                'water_content': water_content,
                'sediment': sediment,
                'sulfur_content': sulfur_content
            }

            # إجراء الفحص
            with st.spinner("جاري إجراء فحص الجودة..."):
                quality_results = predictive_maintenance.quality_control_checks(fuel_sample)

            if 'error' in quality_results:
                st.error(quality_results['error'])
                return

            # عرض النتائج
            quality_colors = {
                'EXCELLENT': '🟢',
                'GOOD': '🟢',
                'PASS': '🟡',
                'FAIL': '🔴'
            }

            st.subheader("نتائج فحص الجودة")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("الجودة العامة", f"{quality_colors.get(quality_results['overall_quality'], '⚪')} {quality_results['overall_quality']}")

            with col2:
                passed_tests = len([t for t in quality_results['tests'] if t['status'] == 'PASS'])
                total_tests = len(quality_results['tests'])
                st.metric("الفحوصات الناجحة", f"{passed_tests}/{total_tests}")

            with col3:
                st.metric("تاريخ الفحص", quality_results['test_date'].strftime('%Y-%m-%d %H:%M'))

            # تفاصيل الفحوصات
            st.subheader("تفاصيل الفحوصات")

            for test in quality_results['tests']:
                status_color = '🟢' if test['status'] == 'PASS' else '🔴'
                with st.expander(f"{status_color} {test['test_name']}"):
                    st.write(f"**القيمة المقاسة:** {test['measured_value']}")
                    st.write(f"**الحالة:** {test['status']}")
                    if 'reason' in test:
                        st.error(f"**السبب:** {test['reason']}")

            # التوصيات
            if quality_results.get('recommendations'):
                st.subheader("التوصيات")
                for rec in quality_results['recommendations']:
                    st.info(f"💡 {rec}")

            # حفظ النتائج في قاعدة البيانات
            try:
                conn = get_connection()
                c = conn.cursor()

                c.execute("""
                    INSERT INTO QualityControlTests
                    (Sample_ID, Fuel_Type, Test_Date, Overall_Quality, Test_Results, Recommendations)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    quality_results['sample_id'],
                    quality_results['fuel_type'],
                    quality_results['test_date'],
                    quality_results['overall_quality'],
                    str(quality_results['tests']),
                    str(quality_results['recommendations'])
                ))

                conn.commit()
                conn.close()

                st.success("تم حفظ نتائج الفحص في قاعدة البيانات")

            except Exception as e:
                st.warning(f"لم يتم حفظ النتائج في قاعدة البيانات: {str(e)}")