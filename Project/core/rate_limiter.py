"""
نظام Rate Limiting متقدم لحماية تسجيل الدخول - Petrol Pump Management System
يوفر هذا النظام حماية متقدمة من محاولات تسجيل الدخول المتكررة
"""

import time
import logging
from datetime import datetime, timedelta
from collections import defaultdict, deque
from typing import Dict, List, Optional, Any, Tuple
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='rate_limiter.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class RateLimiter:
    """مدير تحديد معدل الطلبات"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)

        # إعدادات الحدود
        self.login_limits = {
            'max_attempts': 5,  # الحد الأقصى للمحاولات
            'window_seconds': 300,  # النافذة الزمنية (5 دقائق)
            'block_duration': 600,  # مدة الحظر (10 دقائق)
            'progressive_delay': True  # تأخير تصاعدي
        }

        self.api_limits = {
            'max_requests': 100,  # الحد الأقصى للطلبات
            'window_seconds': 60,  # في الدقيقة الواحدة
            'block_duration': 300  # مدة الحظر (5 دقائق)
        }

        # تخزين محاولات تسجيل الدخول
        self.login_attempts: Dict[str, deque] = defaultdict(deque)
        self.blocked_users: Dict[str, datetime] = {}

        # تخزين طلبات API
        self.api_requests: Dict[str, deque] = defaultdict(deque)
        self.blocked_ips: Dict[str, datetime] = {}

        # إعدادات التأخير التصاعدي
        self.delay_multipliers = [1, 2, 4, 8, 16]  # مضاعفات التأخير

    def _cleanup_old_attempts(self, attempts_dict: Dict[str, deque], window_seconds: int):
        """
        تنظيف المحاولات القديمة

        Args:
            attempts_dict: قاموس المحاولات
            window_seconds: النافذة الزمنية
        """
        current_time = time.time()
        cutoff_time = current_time - window_seconds

        for user_ip, attempts in attempts_dict.items():
            # إزالة المحاولات القديمة
            while attempts and attempts[0] < cutoff_time:
                attempts.popleft()

            # إزالة المستخدمين بدون محاولات
            if not attempts:
                del attempts_dict[user_ip]

    def _get_client_ip(self) -> str:
        """
        الحصول على عنوان IP للعميل

        Returns:
            str: عنوان IP
        """
        # في بيئة Streamlit، قد لا نتمكن من الحصول على IP الحقيقي
        # سنستخدم session_id كبديل
        if hasattr(st, 'session_state') and 'session_id' in st.session_state:
            return st.session_state.session_id
        else:
            # IP وهمي للاختبار
            return "127.0.0.1"

    def check_login_attempts(self, username: str) -> Tuple[bool, Optional[float]]:
        """
        التحقق من محاولات تسجيل الدخول

        Args:
            username: اسم المستخدم

        Returns:
            Tuple[bool, Optional[float]]: (مسموح/محظور, وقت الانتظار)
        """
        client_ip = self._get_client_ip()
        user_key = f"{username}:{client_ip}"

        # تنظيف المحاولات القديمة
        self._cleanup_old_attempts(self.login_attempts, self.login_limits['window_seconds'])

        # التحقق من الحظر
        if user_key in self.blocked_users:
            if datetime.now() < self.blocked_users[user_key]:
                remaining_time = (self.blocked_users[user_key] - datetime.now()).total_seconds()
                return False, remaining_time
            else:
                # انتهى وقت الحظر
                del self.blocked_users[user_key]

        # عد المحاولات في النافذة الزمنية
        attempts_in_window = len(self.login_attempts[user_key])

        if attempts_in_window >= self.login_limits['max_attempts']:
            # حظر المستخدم
            block_until = datetime.now() + timedelta(seconds=self.login_limits['block_duration'])
            self.blocked_users[user_key] = block_until

            self.logger.warning(f"User {username} blocked due to too many login attempts")
            return False, self.login_limits['block_duration']

        return True, None

    def record_login_attempt(self, username: str, success: bool):
        """
        تسجيل محاولة تسجيل دخول

        Args:
            username: اسم المستخدم
            success: نجحت المحاولة أم لا
        """
        client_ip = self._get_client_ip()
        user_key = f"{username}:{client_ip}"
        current_time = time.time()

        # إضافة المحاولة
        self.login_attempts[user_key].append(current_time)

        if success:
            # في حالة النجاح، ننظف محاولات المستخدم
            self.login_attempts[user_key].clear()
            if user_key in self.blocked_users:
                del self.blocked_users[user_key]
            self.logger.info(f"Successful login for user {username}")
        else:
            attempts_count = len(self.login_attempts[user_key])
            self.logger.warning(f"Failed login attempt {attempts_count} for user {username}")

    def get_login_delay(self, username: str) -> float:
        """
        الحصول على التأخير المطلوب قبل المحاولة التالية

        Args:
            username: اسم المستخدم

        Returns:
            float: التأخير بالثواني
        """
        if not self.login_limits['progressive_delay']:
            return 0

        client_ip = self._get_client_ip()
        user_key = f"{username}:{client_ip}"

        attempts_count = len(self.login_attempts[user_key])

        if attempts_count <= 1:
            return 0

        # حساب التأخير التصاعدي
        delay_index = min(attempts_count - 2, len(self.delay_multipliers) - 1)
        base_delay = 2  # تأخير أساسي بالثواني
        delay = base_delay * self.delay_multipliers[delay_index]

        return min(delay, 30)  # الحد الأقصى 30 ثانية

    def check_api_rate_limit(self, endpoint: str = "general") -> Tuple[bool, Optional[float]]:
        """
        التحقق من حد معدل طلبات API

        Args:
            endpoint: نقطة النهاية

        Returns:
            Tuple[bool, Optional[float]]: (مسموح/محظور, وقت الانتظار)
        """
        client_ip = self._get_client_ip()
        request_key = f"{client_ip}:{endpoint}"

        # تنظيف الطلبات القديمة
        self._cleanup_old_attempts(self.api_requests, self.api_limits['window_seconds'])

        # التحقق من الحظر
        if request_key in self.blocked_ips:
            if datetime.now() < self.blocked_ips[request_key]:
                remaining_time = (self.blocked_ips[request_key] - datetime.now()).total_seconds()
                return False, remaining_time
            else:
                del self.blocked_ips[request_key]

        # عد الطلبات في النافذة الزمنية
        requests_in_window = len(self.api_requests[request_key])

        if requests_in_window >= self.api_limits['max_requests']:
            # حظر IP
            block_until = datetime.now() + timedelta(seconds=self.api_limits['block_duration'])
            self.blocked_ips[request_key] = block_until

            self.logger.warning(f"IP {client_ip} blocked due to too many API requests to {endpoint}")
            return False, self.api_limits['block_duration']

        return True, None

    def record_api_request(self, endpoint: str = "general"):
        """
        تسجيل طلب API

        Args:
            endpoint: نقطة النهاية
        """
        client_ip = self._get_client_ip()
        request_key = f"{client_ip}:{endpoint}"
        current_time = time.time()

        self.api_requests[request_key].append(current_time)

    def get_rate_limit_status(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        الحصول على حالة حدود المعدل

        Args:
            username: اسم المستخدم (اختياري)

        Returns:
            Dict: حالة حدود المعدل
        """
        client_ip = self._get_client_ip()

        status = {
            'login_attempts': {},
            'blocked_users': {},
            'api_requests': {},
            'blocked_ips': {}
        }

        # حالة محاولات تسجيل الدخول
        if username:
            user_key = f"{username}:{client_ip}"
            status['login_attempts'][user_key] = {
                'attempts': len(self.login_attempts[user_key]),
                'max_attempts': self.login_limits['max_attempts'],
                'blocked_until': self.blocked_users.get(user_key)
            }

        # المستخدمون المحظورون
        status['blocked_users'] = {
            user: blocked_until.isoformat()
            for user, blocked_until in self.blocked_users.items()
        }

        # طلبات API
        ip_key = f"{client_ip}:general"
        status['api_requests'][ip_key] = {
            'requests': len(self.api_requests[ip_key]),
            'max_requests': self.api_limits['max_requests'],
            'blocked_until': self.blocked_ips.get(ip_key)
        }

        # IPs المحظورة
        status['blocked_ips'] = {
            ip: blocked_until.isoformat()
            for ip, blocked_until in self.blocked_ips.items()
        }

        return status

    def reset_user_limits(self, username: str):
        """
        إعادة تعيين حدود المستخدم

        Args:
            username: اسم المستخدم
        """
        client_ip = self._get_client_ip()
        user_key = f"{username}:{client_ip}"

        if user_key in self.login_attempts:
            self.login_attempts[user_key].clear()

        if user_key in self.blocked_users:
            del self.blocked_users[user_key]

        self.logger.info(f"Rate limits reset for user {username}")

    def reset_ip_limits(self, ip_address: str = None):
        """
        إعادة تعيين حدود IP

        Args:
            ip_address: عنوان IP (اختياري، سيستخدم IP الحالي)
        """
        if not ip_address:
            ip_address = self._get_client_ip()

        # إزالة جميع مفاتيح API المتعلقة بهذا IP
        keys_to_remove = [key for key in self.api_requests.keys() if key.startswith(f"{ip_address}:")]
        for key in keys_to_remove:
            del self.api_requests[key]

        keys_to_remove = [key for key in self.blocked_ips.keys() if key.startswith(f"{ip_address}:")]
        for key in keys_to_remove:
            del self.blocked_ips[key]

        self.logger.info(f"Rate limits reset for IP {ip_address}")

# إنشاء instance عالمي
rate_limiter = RateLimiter()

# دوال مساعدة للاستخدام في Streamlit
def secure_login_form():
    """نموذج تسجيل دخول آمن مع rate limiting"""
    st.subheader("🔐 تسجيل الدخول الآمن")

    # الحصول على معلومات المستخدم من session
    username = st.session_state.get('login_username', '')
    user_type = st.session_state.get('login_user_type', 'Employee')

    # التحقق من الحدود
    can_login, wait_time = rate_limiter.check_login_attempts(username)

    if not can_login:
        if wait_time:
            minutes = int(wait_time // 60)
            seconds = int(wait_time % 60)
            st.error(f"🚫 تم حظر الحساب مؤقتاً بسبب تكرار المحاولات الخاطئة")
            st.error(f"الرجاء الانتظار {minutes} دقيقة و {seconds} ثانية قبل المحاولة مرة أخرى")

            # عرض شريط التقدم للوقت المتبقي
            progress = min(wait_time / rate_limiter.login_limits['block_duration'], 1.0)
            st.progress(1.0 - progress)

            return False

    # حساب التأخير المطلوب
    delay = rate_limiter.get_login_delay(username)
    if delay > 0:
        st.warning(f"⏱️ يرجى الانتظار {delay} ثانية قبل المحاولة التالية")
        time.sleep(delay)

    # نموذج تسجيل الدخول
    with st.form("secure_login_form"):
        username = st.text_input("اسم المستخدم", value=username, key="secure_username")
        password = st.text_input("كلمة المرور", type="password", key="secure_password")
        user_type = st.selectbox("نوع المستخدم", ["Employee", "Owner"], index=0 if user_type == "Employee" else 1, key="secure_user_type")

        submitted = st.form_submit_button("تسجيل الدخول", use_container_width=True)

        if submitted:
            if not username or not password:
                st.error("يرجى إدخال اسم المستخدم وكلمة المرور")
                rate_limiter.record_login_attempt(username, False)
                return False

            # محاولة المصادقة
            from core.secure_auth_manager import secure_authenticate_user
            success = secure_authenticate_user(user_type, username, password)

            # تسجيل المحاولة
            rate_limiter.record_login_attempt(username, success)

            if success:
                st.success("تم تسجيل الدخول بنجاح!")
                return True
            else:
                attempts_left = rate_limiter.login_limits['max_attempts'] - len(rate_limiter.login_attempts[f"{username}:{rate_limiter._get_client_ip()}"])
                if attempts_left > 0:
                    st.error(f"بيانات الدخول غير صحيحة. تبقى {attempts_left} محاولة")
                else:
                    st.error("تم حظر الحساب مؤقتاً بسبب تكرار المحاولات الخاطئة")
                return False

    return False

def display_rate_limit_status():
    """عرض حالة حدود المعدل في Streamlit"""
    st.subheader("📊 حالة حدود المعدل")

    # التحقق من الصلاحية
    from core.permission_manager import check_permission
    if not check_permission('ADMIN'):
        st.error("يجب أن تكون مديراً لعرض حالة حدود المعدل")
        return

    status = rate_limiter.get_rate_limit_status()

    # المستخدمون المحظورون
    if status['blocked_users']:
        st.subheader("🚫 المستخدمون المحظورون")
        for user_key, blocked_until in status['blocked_users'].items():
            username, ip = user_key.split(':', 1)
            st.error(f"المستخدم: {username} | محظور حتى: {blocked_until}")
    else:
        st.success("✅ لا يوجد مستخدمون محظورون")

    # IPs المحظورة
    if status['blocked_ips']:
        st.subheader("🚫 عناوين IP المحظورة")
        for ip_key, blocked_until in status['blocked_ips'].items():
            ip, endpoint = ip_key.split(':', 1)
            st.error(f"IP: {ip} | النقطة: {endpoint} | محظور حتى: {blocked_until}")
    else:
        st.success("✅ لا توجد عناوين IP محظورة")

    # إحصائيات مفصلة
    with st.expander("إحصائيات مفصلة"):
        st.json(status)

def reset_rate_limits_ui():
    """واجهة إعادة تعيين حدود المعدل"""
    st.subheader("🔄 إعادة تعيين حدود المعدل")

    # التحقق من الصلاحية
    from core.permission_manager import check_permission
    if not check_permission('ADMIN'):
        st.error("يجب أن تكون مديراً لإعادة تعيين حدود المعدل")
        return

    st.warning("⚠️ هذه العملية ستزيل جميع القيود المفروضة على المستخدمين")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("إعادة تعيين جميع حدود تسجيل الدخول", use_container_width=True):
            rate_limiter.login_attempts.clear()
            rate_limiter.blocked_users.clear()
            st.success("تم إعادة تعيين حدود تسجيل الدخول")

            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'System',
                'RATE_LIMIT_RESET',
                'UPDATE',
                new_values={'type': 'login_limits'}
            )

    with col2:
        if st.button("إعادة تعيين جميع حدود API", use_container_width=True):
            rate_limiter.api_requests.clear()
            rate_limiter.blocked_ips.clear()
            st.success("تم إعادة تعيين حدود API")

            # تسجيل في audit trail
            from core.audit_trail import log_user_action
            log_user_action(
                'System',
                'RATE_LIMIT_RESET',
                'UPDATE',
                new_values={'type': 'api_limits'}
            )

def api_rate_limit_decorator(endpoint: str = "general"):
    """
    Decorator لتطبيق rate limiting على دوال API

    Args:
        endpoint: نقطة النهاية
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # التحقق من الحدود
            allowed, wait_time = rate_limiter.check_api_rate_limit(endpoint)

            if not allowed:
                if wait_time:
                    st.error(f"تم تجاوز حد الطلبات. الرجاء الانتظار {int(wait_time)} ثانية")
                return None

            # تسجيل الطلب
            rate_limiter.record_api_request(endpoint)

            # تنفيذ الدالة
            return func(*args, **kwargs)

        return wrapper
    return decorator