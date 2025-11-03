"""
نظام إدارة العلاقات مع العملاء (CRM) - Petrol Pump Management System
يوفر هذا النظام إدارة شاملة للعملاء مع تحليلات سلوكية وعروض مخصصة
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
    filename='customer_crm.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class CustomerCRM:
    """نظام إدارة علاقات العملاء"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # معايير تصنيف العملاء
        self.customer_segments = {
            'VIP': {'min_spent': 50000, 'min_visits': 50, 'min_loyalty_score': 80},
            'GOLD': {'min_spent': 25000, 'min_visits': 25, 'min_loyalty_score': 60},
            'SILVER': {'min_spent': 10000, 'min_visits': 10, 'min_loyalty_score': 40},
            'BRONZE': {'min_spent': 1000, 'min_visits': 3, 'min_loyalty_score': 20},
            'NEW': {'max_visits': 2, 'max_spent': 500}
        }

        # برامج الولاء
        self.loyalty_programs = {
            'points_per_rial': 0.1,  # نقطة لكل ريال
            'points_per_visit': 5,   # نقاط لكل زيارة
            'redemption_rate': 100,  # 100 نقطة = 1 ريال
            'expiry_months': 12      # انتهاء الصلاحية بعد 12 شهر
        }

    def customer_segmentation(self) -> Dict[str, Any]:
        """
        تصنيف العملاء حسب سلوكهم

        Returns:
            Dict: تصنيف العملاء
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # الحصول على بيانات العملاء مع إحصائياتهم
            c.execute("""
                SELECT
                    cu.Customer_Code,
                    cu.C_Name,
                    cu.Phone_No,
                    cu.Email_ID,
                    cu.City,
                    cu.Age,
                    COUNT(i.Invoice_No) as total_visits,
                    COALESCE(SUM(i.Total_Price), 0) as total_spent,
                    COALESCE(AVG(i.Total_Price), 0) as avg_transaction,
                    MAX(i.Date) as last_visit,
                    MIN(i.Date) as first_visit,
                    DATEDIFF(CURDATE(), MAX(i.Date)) as days_since_last_visit
                FROM Customer cu
                LEFT JOIN Invoice i ON cu.Customer_Code = i.Customer_Code
                GROUP BY cu.Customer_Code, cu.C_Name, cu.Phone_No, cu.Email_ID, cu.City, cu.Age
            """)

            customers_data = c.fetchall()
            conn.close()

            if not customers_data:
                return {'error': 'لا توجد بيانات عملاء'}

            segments = defaultdict(list)
            segment_stats = defaultdict(int)

            for customer in customers_data:
                customer_code, name, phone, email, city, age, visits, total_spent, avg_transaction, last_visit, first_visit, days_since = customer

                # حساب نقاط الولاء
                loyalty_score = self._calculate_loyalty_score(visits, total_spent, days_since, avg_transaction)

                # تصنيف العميل
                segment = self._classify_customer(visits, total_spent, loyalty_score)

                customer_info = {
                    'customer_code': customer_code,
                    'name': name,
                    'phone': phone,
                    'email': email,
                    'city': city,
                    'age': age,
                    'total_visits': visits,
                    'total_spent': total_spent,
                    'avg_transaction': avg_transaction,
                    'last_visit': last_visit,
                    'first_visit': first_visit,
                    'days_since_last_visit': days_since,
                    'loyalty_score': loyalty_score,
                    'segment': segment
                }

                segments[segment].append(customer_info)
                segment_stats[segment] += 1

            # إحصائيات التصنيف
            total_customers = len(customers_data)
            segment_percentages = {
                segment: (count / total_customers * 100) if total_customers > 0 else 0
                for segment, count in segment_stats.items()
            }

            return {
                'segments': dict(segments),
                'segment_stats': dict(segment_stats),
                'segment_percentages': segment_percentages,
                'total_customers': total_customers,
                'segment_insights': self._generate_segment_insights(segments)
            }

        except Exception as e:
            self.logger.error(f"Error in customer segmentation: {str(e)}")
            return {'error': str(e)}

    def _calculate_loyalty_score(self, visits: int, total_spent: float,
                               days_since: Optional[int], avg_transaction: float) -> float:
        """حساب نقاط ولاء العميل"""
        try:
            score = 0

            # نقاط الزيارات (حتى 30 نقطة)
            score += min(visits * 2, 30)

            # نقاط الإنفاق (حتى 40 نقطة)
            score += min(total_spent / 1000, 40)  # 1 نقطة لكل 1000 ريال

            # نقاط الانتظام (حتى 20 نقطة)
            if days_since is not None:
                if days_since <= 7:
                    score += 20
                elif days_since <= 30:
                    score += 15
                elif days_since <= 90:
                    score += 10
                elif days_since <= 180:
                    score += 5

            # نقاط متوسط المعاملات (حتى 10 نقاط)
            score += min(avg_transaction / 100, 10)

            return min(score, 100)  # الحد الأقصى 100 نقطة

        except Exception:
            return 0

    def _classify_customer(self, visits: int, total_spent: float, loyalty_score: float) -> str:
        """تصنيف العميل حسب معايير محددة"""
        try:
            # فحص VIP
            vip_criteria = self.customer_segments['VIP']
            if (total_spent >= vip_criteria['min_spent'] and
                visits >= vip_criteria['min_visits'] and
                loyalty_score >= vip_criteria['min_loyalty_score']):
                return 'VIP'

            # فحص GOLD
            gold_criteria = self.customer_segments['GOLD']
            if (total_spent >= gold_criteria['min_spent'] and
                visits >= gold_criteria['min_visits'] and
                loyalty_score >= gold_criteria['min_loyalty_score']):
                return 'GOLD'

            # فحص SILVER
            silver_criteria = self.customer_segments['SILVER']
            if (total_spent >= silver_criteria['min_spent'] and
                visits >= silver_criteria['min_visits'] and
                loyalty_score >= silver_criteria['min_loyalty_score']):
                return 'SILVER'

            # فحص BRONZE
            bronze_criteria = self.customer_segments['BRONZE']
            if (total_spent >= bronze_criteria['min_spent'] and
                visits >= bronze_criteria['min_visits'] and
                loyalty_score >= bronze_criteria['min_loyalty_score']):
                return 'BRONZE'

            # فحص NEW
            new_criteria = self.customer_segments['NEW']
            if (visits <= new_criteria['max_visits'] and
                total_spent <= new_criteria['max_spent']):
                return 'NEW'

            return 'REGULAR'

        except Exception:
            return 'REGULAR'

    def _generate_segment_insights(self, segments: Dict[str, List]) -> Dict[str, Any]:
        """توليد رؤى حول التصنيفات"""
        insights = {}

        for segment_name, customers in segments.items():
            if not customers:
                continue

            # إحصائيات التصنيف
            total_spent = sum(c['total_spent'] for c in customers)
            total_visits = sum(c['total_visits'] for c in customers)
            avg_loyalty = np.mean([c['loyalty_score'] for c in customers])
            avg_age = np.mean([c['age'] for c in customers if c['age']])

            insights[segment_name] = {
                'customer_count': len(customers),
                'total_revenue': total_spent,
                'total_visits': total_visits,
                'avg_transaction': total_spent / total_visits if total_visits > 0 else 0,
                'avg_loyalty_score': avg_loyalty,
                'avg_age': avg_age,
                'revenue_percentage': 0,  # سيتم حسابه لاحقاً
                'insights': self._generate_segment_specific_insights(segment_name, customers)
            }

        # حساب نسب الإيرادات
        total_revenue = sum(insights[s]['total_revenue'] for s in insights)
        for segment in insights:
            insights[segment]['revenue_percentage'] = (
                insights[segment]['total_revenue'] / total_revenue * 100
                if total_revenue > 0 else 0
            )

        return insights

    def _generate_segment_specific_insights(self, segment: str, customers: List[Dict]) -> List[str]:
        """توليد رؤى محددة لكل تصنيف"""
        insights = []

        if segment == 'VIP':
            insights.extend([
                "عملاء عالي القيمة - يمثلون أكبر مصدر للإيرادات",
                "يحتاجون لخدمة VIP وامتيازات خاصة",
                "مناسبون لبرامج الولاء المتقدمة"
            ])

        elif segment == 'NEW':
            insights.extend([
                "عملاء جدد - فرصة لتحويلهم إلى عملاء دائمين",
                "يحتاجون لتجربة ترحيب وتعليم الخدمات",
                "مناسبون لحملات الترحيب والعروض الخاصة"
            ])

        elif segment == 'REGULAR':
            insights.extend([
                "عملاء عاديون - يحتاجون لتشجيع لزيادة الإنفاق",
                "مناسبون لحملات الاحتفاظ والعروض الموسمية",
                "يمكن تحويلهم لتصنيفات أعلى ببرامج الولاء"
            ])

        return insights

    def loyalty_program(self, customer_code: str) -> Dict[str, Any]:
        """
        إدارة برنامج الولاء لعميل محدد

        Args:
            customer_code: كود العميل

        Returns:
            Dict: حالة برنامج الولاء
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # الحصول على بيانات العميل ونقاطه
            c.execute("""
                SELECT
                    cu.C_Name,
                    COUNT(i.Invoice_No) as total_visits,
                    COALESCE(SUM(i.Total_Price), 0) as total_spent,
                    COALESCE(lp.Current_Points, 0) as current_points,
                    COALESCE(lp.Total_Earned_Points, 0) as total_earned,
                    COALESCE(lp.Total_Redeemed_Points, 0) as total_redeemed,
                    lp.Last_Updated
                FROM Customer cu
                LEFT JOIN Invoice i ON cu.Customer_Code = i.Customer_Code
                LEFT JOIN LoyaltyPoints lp ON cu.Customer_Code = lp.Customer_Code
                WHERE cu.Customer_Code = %s
                GROUP BY cu.Customer_Code, cu.C_Name, lp.Current_Points, lp.Total_Earned_Points, lp.Total_Redeemed_Points, lp.Last_Updated
            """, (customer_code,))

            customer_data = c.fetchone()

            if not customer_data:
                conn.close()
                return {'error': 'العميل غير موجود'}

            name, visits, total_spent, current_points, total_earned, total_redeemed, last_updated = customer_data

            # حساب النقاط المستحقة
            earned_from_spending = total_spent * self.loyalty_programs['points_per_rial']
            earned_from_visits = visits * self.loyalty_programs['points_per_visit']
            total_earned_calculated = earned_from_spending + earned_from_visits

            # تحديث النقاط إذا لزم الأمر
            if total_earned_calculated != total_earned:
                # تحديث أو إدراج نقاط الولاء
                c.execute("""
                    INSERT INTO LoyaltyPoints
                    (Customer_Code, Current_Points, Total_Earned_Points, Total_Redeemed_Points, Last_Updated)
                    VALUES (%s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                    Current_Points = %s,
                    Total_Earned_Points = %s,
                    Last_Updated = %s
                """, (
                    customer_code,
                    total_earned_calculated - total_redeemed,
                    total_earned_calculated,
                    total_redeemed,
                    datetime.now(),
                    total_earned_calculated - total_redeemed,
                    total_earned_calculated,
                    datetime.now()
                ))

                current_points = total_earned_calculated - total_redeemed

            conn.commit()
            conn.close()

            # حساب القيمة المتاحة للاستبدال
            redeemable_value = current_points / self.loyalty_programs['redemption_rate']

            # تحديد مستوى العضوية
            membership_level = self._get_membership_level(current_points)

            return {
                'customer_code': customer_code,
                'customer_name': name,
                'current_points': current_points,
                'total_earned': total_earned_calculated,
                'total_redeemed': total_redeemed,
                'redeemable_value': redeemable_value,
                'membership_level': membership_level,
                'points_to_next_level': self._points_to_next_level(current_points),
                'expiry_date': datetime.now() + timedelta(days=self.loyalty_programs['expiry_months'] * 30),
                'last_updated': last_updated or datetime.now()
            }

        except Exception as e:
            self.logger.error(f"Error in loyalty program: {str(e)}")
            return {'error': str(e)}

    def _get_membership_level(self, points: float) -> str:
        """تحديد مستوى العضوية حسب النقاط"""
        if points >= 10000:
            return 'PLATINUM'
        elif points >= 5000:
            return 'GOLD'
        elif points >= 2000:
            return 'SILVER'
        elif points >= 500:
            return 'BRONZE'
        else:
            return 'BASIC'

    def _points_to_next_level(self, current_points: float) -> int:
        """حساب النقاط المطلوبة للمستوى التالي"""
        levels = [500, 2000, 5000, 10000]
        for level in levels:
            if current_points < level:
                return level - int(current_points)
        return 0  # بلغ أعلى مستوى

    def personalized_offers(self, customer_code: str) -> Dict[str, Any]:
        """
        توليد عروض مخصصة للعميل

        Args:
            customer_code: كود العميل

        Returns:
            Dict: العروض المخصصة
        """
        try:
            conn = get_connection()
            if not conn:
                return {'error': 'فشل في الاتصال بقاعدة البيانات'}

            c = conn.cursor()

            # الحصول على بيانات العميل وسلوكه
            c.execute("""
                SELECT
                    cu.C_Name,
                    COUNT(i.Invoice_No) as total_visits,
                    COALESCE(SUM(i.Total_Price), 0) as total_spent,
                    COALESCE(AVG(i.Total_Price), 0) as avg_transaction,
                    MAX(i.Date) as last_visit,
                    GROUP_CONCAT(DISTINCT i.Fuel_Type_Actual) as fuel_types_used,
                    GROUP_CONCAT(DISTINCT i.Payment_Type) as payment_methods
                FROM Customer cu
                LEFT JOIN Invoice i ON cu.Customer_Code = i.Customer_Code
                WHERE cu.Customer_Code = %s
                GROUP BY cu.Customer_Code, cu.C_Name
            """, (customer_code,))

            customer_data = c.fetchone()
            conn.close()

            if not customer_data:
                return {'error': 'العميل غير موجود'}

            name, visits, total_spent, avg_transaction, last_visit, fuel_types, payment_methods = customer_data

            offers = []
            reasons = []

            # عروض حسب السلوك
            if visits >= 10 and total_spent >= 10000:  # عميل دائم
                offers.append({
                    'type': 'LOYALTY_BONUS',
                    'title': 'مكافأة الولاء',
                    'description': 'خصم 10% على جميع المشتريات لمدة شهر',
                    'value': '10% discount',
                    'validity_days': 30
                })
                reasons.append('عميل دائم مع إنفاق عالي')

            if last_visit and (datetime.now().date() - last_visit).days > 30:  # عميل غائب
                offers.append({
                    'type': 'COME_BACK',
                    'title': 'عرض العودة',
                    'description': 'خصم 15% على أول شراء',
                    'value': '15% discount',
                    'validity_days': 14
                })
                reasons.append('لم يزر منذ أكثر من شهر')

            if avg_transaction < 200:  # متوسط إنفاق منخفض
                offers.append({
                    'type': 'UPGRADE_OFFER',
                    'title': 'عرض الترقية',
                    'description': 'خصم على أنواع الوقود الأعلى جودة',
                    'value': 'خصم على البنزين 95',
                    'validity_days': 21
                })
                reasons.append('متوسط المشتريات منخفض')

            if fuel_types and 'بنزين 91' in str(fuel_types) and 'بنزين 95' not in str(fuel_types):
                offers.append({
                    'type': 'FUEL_UPGRADE',
                    'title': 'ترقية نوع الوقود',
                    'description': 'خصم 5% عند تجربة البنزين 95',
                    'value': '5% discount',
                    'validity_days': 30
                })
                reasons.append('لم يجرب أنواع الوقود الأعلى')

            # عرض افتراضي إذا لم تكن هناك عروض مخصصة
            if not offers:
                offers.append({
                    'type': 'GENERAL',
                    'title': 'عرض ترحيبي',
                    'description': 'خصم 5% على جميع المشتريات',
                    'value': '5% discount',
                    'validity_days': 7
                })
                reasons.append('عرض عام للعملاء')

            return {
                'customer_code': customer_code,
                'customer_name': name,
                'offers': offers,
                'reasons': reasons,
                'generated_at': datetime.now(),
                'total_offers': len(offers)
            }

        except Exception as e:
            self.logger.error(f"Error generating personalized offers: {str(e)}")
            return {'error': str(e)}

# إنشاء instance عالمي
customer_crm = CustomerCRM()

# دوال مساعدة للاستخدام في Streamlit
def display_customer_segmentation():
    """عرض تصنيف العملاء في Streamlit"""
    st.subheader("👥 تصنيف العملاء")

    with st.spinner("جاري تحليل بيانات العملاء..."):
        segmentation = customer_crm.customer_segmentation()

    if 'error' in segmentation:
        st.error(segmentation['error'])
        return

    # إحصائيات عامة
    stats = segmentation['segment_stats']
    percentages = segmentation['segment_percentages']

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("إجمالي العملاء", segmentation['total_customers'])

    with col2:
        vip_count = stats.get('VIP', 0)
        st.metric("عملاء VIP", vip_count, delta=f"👑 {vip_count}")

    with col3:
        new_count = stats.get('NEW', 0)
        st.metric("عملاء جدد", new_count, delta=f"🆕 {new_count}")

    with col4:
        gold_count = stats.get('GOLD', 0)
        st.metric("عملاء ذهبي", gold_count, delta=f"🥇 {gold_count}")

    # عرض التصنيفات
    st.subheader("تفاصيل التصنيفات")

    segment_colors = {
        'VIP': '👑',
        'GOLD': '🥇',
        'SILVER': '🥈',
        'BRONZE': '🥉',
        'NEW': '🆕',
        'REGULAR': '👤'
    }

    for segment_name, customers in segmentation['segments'].items():
        if not customers:
            continue

        with st.expander(f"{segment_colors.get(segment_name, '👤')} {segment_name} ({len(customers)} عميل)"):
            # إحصائيات التصنيف
            insights = segmentation['segment_insights'].get(segment_name, {})

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("إجمالي الإيرادات", f"{insights.get('total_revenue', 0):,.0f} ريال")
                st.metric("متوسط المعاملة", f"{insights.get('avg_transaction', 0):,.0f} ريال")

            with col2:
                st.metric("نسبة الإيرادات", f"{insights.get('revenue_percentage', 0):.1f}%")
                st.metric("متوسط الولاء", f"{insights.get('avg_loyalty_score', 0):.1f}")

            with col3:
                st.metric("متوسط العمر", f"{insights.get('avg_age', 0):.0f} سنة")

            # رؤى التصنيف
            if insights.get('insights'):
                st.subheader("الرؤى والتوصيات")
                for insight in insights['insights']:
                    st.info(f"💡 {insight}")

            # جدول العملاء
            if len(customers) <= 20:  # عرض إذا كان عدد العملاء قليل
                st.subheader("العملاء في هذا التصنيف")
                customer_df = pd.DataFrame([{
                    'الاسم': c['name'],
                    'المدينة': c['city'],
                    'إجمالي الإنفاق': c['total_spent'],
                    'عدد الزيارات': c['total_visits'],
                    'نقاط الولاء': c['loyalty_score']
                } for c in customers[:10]])  # أول 10 عملاء

                st.dataframe(customer_df)

def display_loyalty_program(customer_code: Optional[str] = None):
    """عرض برنامج الولاء في Streamlit"""
    st.subheader("🎁 برنامج الولاء")

    if not customer_code:
        # اختيار العميل
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Customer_Code, C_Name, Phone_No FROM Customer ORDER BY C_Name")
            customers = c.fetchall()
            conn.close()

            if not customers:
                st.info("لا يوجد عملاء مسجلون")
                return

            customer_options = {f"{name} - {phone} ({code})": code for code, name, phone in customers}
            selected_customer = st.selectbox("اختر العميل:", list(customer_options.keys()), key="loyalty_customer")
            customer_code = customer_options[selected_customer]

        except Exception as e:
            st.error(f"خطأ في تحميل العملاء: {str(e)}")
            return

    # عرض برنامج الولاء
    with st.spinner("جاري تحميل بيانات برنامج الولاء..."):
        loyalty_data = customer_crm.loyalty_program(customer_code)

    if 'error' in loyalty_data:
        st.error(loyalty_data['error'])
        return

    # عرض البيانات الأساسية
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("النقاط الحالية", f"{loyalty_data['current_points']:,.0f}")

    with col2:
        level = loyalty_data['membership_level']
        level_colors = {'PLATINUM': '🟣', 'GOLD': '🥇', 'SILVER': '🥈', 'BRONZE': '🥉', 'BASIC': '⚪'}
        st.metric("مستوى العضوية", f"{level_colors.get(level, '⚪')} {level}")

    with col3:
        value = loyalty_data['redeemable_value']
        st.metric("القيمة المتاحة", f"{value:,.0f} ريال")

    with col4:
        points_needed = loyalty_data['points_to_next_level']
        if points_needed > 0:
            st.metric("نقاط للمستوى التالي", points_needed)
        else:
            st.metric("المستوى", "الأعلى 🎉")

    # تفاصيل إضافية
    with st.expander("تفاصيل برنامج الولاء"):
        st.write(f"**إجمالي النقاط المكتسبة:** {loyalty_data['total_earned']:,.0f}")
        st.write(f"**النقاط المستبدلة:** {loyalty_data['total_redeemed']:,.0f}")
        st.write(f"**تاريخ انتهاء الصلاحية:** {loyalty_data['expiry_date'].strftime('%Y-%m-%d')}")
        st.write(f"**آخر تحديث:** {loyalty_data['last_updated'].strftime('%Y-%m-%d %H:%M')}")

        # شرح برنامج الولاء
        st.subheader("كيفية كسب النقاط")
        st.write("• نقطة واحدة لكل ريال يتم إنفاقه")
        st.write("• 5 نقاط لكل زيارة")
        st.write("• 100 نقطة = 1 ريال خصم")

def display_personalized_offers(customer_code: Optional[str] = None):
    """عرض العروض المخصصة في Streamlit"""
    st.subheader("🎯 العروض المخصصة")

    if not customer_code:
        # اختيار العميل
        try:
            conn = get_connection()
            c = conn.cursor()
            c.execute("SELECT Customer_Code, C_Name, Phone_No FROM Customer ORDER BY C_Name")
            customers = c.fetchall()
            conn.close()

            if not customers:
                st.info("لا يوجد عملاء مسجلون")
                return

            customer_options = {f"{name} - {phone} ({code})": code for code, name, phone in customers}
            selected_customer = st.selectbox("اختر العميل:", list(customer_options.keys()), key="offers_customer")
            customer_code = customer_options[selected_customer]

        except Exception as e:
            st.error(f"خطأ في تحميل العملاء: {str(e)}")
            return

    # توليد العروض المخصصة
    with st.spinner("جاري توليد العروض المخصصة..."):
        offers_data = customer_crm.personalized_offers(customer_code)

    if 'error' in offers_data:
        st.error(offers_data['error'])
        return

    # عرض العروض
    st.success(f"تم توليد {offers_data['total_offers']} عرض مخصص للعميل {offers_data['customer_name']}")

    # أسباب العروض
    if offers_data.get('reasons'):
        st.subheader("أسباب العروض")
        for reason in offers_data['reasons']:
            st.info(f"📊 {reason}")

    # عرض العروض
    st.subheader("العروض المتاحة")

    for offer in offers_data['offers']:
        with st.expander(f"🎁 {offer['title']}"):
            st.write(f"**الوصف:** {offer['description']}")
            st.write(f"**القيمة:** {offer['value']}")
            st.write(f"**صلاحية:** {offer['validity_days']} يوم")
            st.write(f"**النوع:** {offer['type']}")

            # زر تطبيق العرض
            if st.button(f"تطبيق العرض", key=f"apply_{offer['type']}"):
                st.success(f"تم تطبيق عرض '{offer['title']}' على العميل")
                # يمكن إضافة منطق حفظ العرض في قاعدة البيانات هنا

    # معلومات إضافية
    with st.expander("معلومات إضافية"):
        st.write(f"**تاريخ التوليد:** {offers_data['generated_at'].strftime('%Y-%m-%d %H:%M')}")
        st.write("العروض المخصصة تعتمد على سلوك العميل وسجل المشتريات")