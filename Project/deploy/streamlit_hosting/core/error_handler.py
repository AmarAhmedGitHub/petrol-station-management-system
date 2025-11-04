"""
نظام إدارة الأخطاء المتقدم مع Logging - Petrol Pump Management System
يوفر هذا النظام إدارة شاملة للأخطاء مع تسجيل مفصل
"""

import logging
import traceback
import sys
from datetime import datetime
from typing import Dict, List, Optional, Any, Callable
from functools import wraps
import streamlit as st

# إعداد نظام التسجيل المتقدم
class AdvancedLogger:
    """نظام تسجيل متقدم"""

    def __init__(self):
        self.setup_loggers()

    def setup_loggers(self):
        """إعداد مختلف أنواع التسجيل"""

        # Logger عام للتطبيق
        self.app_logger = logging.getLogger('petrol_pump_app')
        self.app_logger.setLevel(logging.DEBUG)

        # Logger للأخطاء
        self.error_logger = logging.getLogger('petrol_pump_errors')
        self.error_logger.setLevel(logging.ERROR)

        # Logger لقاعدة البيانات
        self.db_logger = logging.getLogger('petrol_pump_db')
        self.db_logger.setLevel(logging.INFO)

        # Logger للأمان
        self.security_logger = logging.getLogger('petrol_pump_security')
        self.security_logger.setLevel(logging.WARNING)

        # إعداد formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )

        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )

        # إعداد handlers
        # File handlers
        app_handler = logging.FileHandler('app.log', encoding='utf-8')
        app_handler.setLevel(logging.DEBUG)
        app_handler.setFormatter(detailed_formatter)

        error_handler = logging.FileHandler('errors.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(detailed_formatter)

        db_handler = logging.FileHandler('database.log', encoding='utf-8')
        db_handler.setLevel(logging.INFO)
        db_handler.setFormatter(simple_formatter)

        security_handler = logging.FileHandler('security.log', encoding='utf-8')
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(detailed_formatter)

        # Console handler للتطوير
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)

        # إضافة handlers للloggers
        self.app_logger.addHandler(app_handler)
        self.app_logger.addHandler(console_handler)

        self.error_logger.addHandler(error_handler)
        self.error_logger.addHandler(console_handler)

        self.db_logger.addHandler(db_handler)
        self.db_logger.addHandler(console_handler)

        self.security_logger.addHandler(security_handler)
        self.security_logger.addHandler(console_handler)

    def log_app_event(self, level: str, message: str, extra: Optional[Dict[str, Any]] = None):
        """تسجيل حدث في التطبيق"""
        log_method = getattr(self.app_logger, level.lower(), self.app_logger.info)
        log_method(message, extra=extra)

    def log_error(self, error: Exception, context: Optional[str] = None, user_info: Optional[Dict[str, Any]] = None):
        """تسجيل خطأ مفصل"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
            'context': context or 'Unknown',
            'timestamp': datetime.now().isoformat(),
            'user_info': user_info or {}
        }

        error_message = f"خطأ في {context}: {type(error).__name__}: {str(error)}"
        self.error_logger.error(error_message, extra=error_details)

    def log_db_operation(self, operation: str, table: str, success: bool, duration: Optional[float] = None, error: Optional[str] = None):
        """تسجيل عملية قاعدة بيانات"""
        message = f"DB {operation} on {table}"
        if duration:
            message += f" - Duration: {duration:.3f}s"
        if error:
            message += f" - Error: {error}"

        if success:
            self.db_logger.info(message)
        else:
            self.db_logger.error(message)

    def log_security_event(self, event_type: str, user: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """تسجيل حدث أمني"""
        message = f"Security event: {event_type}"
        if user:
            message += f" - User: {user}"

        extra = {'event_type': event_type, 'user': user, 'details': details or {}}
        self.security_logger.warning(message, extra=extra)

# إنشاء instance عالمي
advanced_logger = AdvancedLogger()

class ErrorHandler:
    """مدير الأخطاء المتقدم"""

    def __init__(self):
        self.logger = advanced_logger
        self.error_counts = {}
        self.max_retries = 3

    def handle_error(self, error: Exception, context: str = "Unknown", show_user_message: bool = True,
                    log_error: bool = True, user_info: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        معالجة الخطأ وإرجاع معلومات مفصلة

        Args:
            error: الخطأ المحدث
            context: سياق الخطأ
            show_user_message: عرض رسالة للمستخدم
            log_error: تسجيل الخطأ
            user_info: معلومات المستخدم

        Returns:
            Dict: معلومات الخطأ
        """
        error_info = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context,
            'timestamp': datetime.now(),
            'traceback': traceback.format_exc(),
            'user_friendly_message': self.get_user_friendly_message(error, context)
        }

        # تسجيل الخطأ
        if log_error:
            self.logger.log_error(error, context, user_info)

        # زيادة عداد الأخطاء
        error_key = f"{context}:{type(error).__name__}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1

        # عرض رسالة للمستخدم
        if show_user_message and hasattr(st, 'error'):
            st.error(error_info['user_friendly_message'])

        return error_info

    def get_user_friendly_message(self, error: Exception, context: str) -> str:
        """
        الحصول على رسالة خطأ ودية للمستخدم

        Args:
            error: الخطأ
            context: السياق

        Returns:
            str: الرسالة الودية
        """
        error_messages = {
            'ConnectionError': "فشل في الاتصال بالخادم. يرجى المحاولة لاحقاً.",
            'TimeoutError': "انتهت مهلة العملية. يرجى المحاولة مرة أخرى.",
            'ValueError': "البيانات المدخلة غير صحيحة. يرجى التحقق من القيم.",
            'IntegrityError': "البيانات تتعارض مع قواعد النظام. يرجى مراجعة المدخلات.",
            'OperationalError': "خطأ في قاعدة البيانات. يرجى المحاولة لاحقاً.",
            'PermissionError': "ليس لديك صلاحية لتنفيذ هذه العملية.",
            'FileNotFoundError': "الملف المطلوب غير موجود.",
            'KeyError': "بيانات مطلوبة مفقودة.",
            'TypeError': "نوع البيانات غير صحيح.",
            'AttributeError': "خطأ في النظام. يرجى الاتصال بالدعم الفني."
        }

        # رسائل محددة حسب السياق
        context_messages = {
            'database_connection': "فشل في الاتصال بقاعدة البيانات. تحقق من الاتصال بالإنترنت.",
            'user_authentication': "فشل في تسجيل الدخول. تحقق من اسم المستخدم وكلمة المرور.",
            'data_validation': "البيانات المدخلة غير صحيحة. يرجى مراجعة جميع الحقول.",
            'permission_check': "ليس لديك الصلاحيات المطلوبة للوصول لهذه الصفحة.",
            'file_operation': "فشل في عملية الملف. تحقق من صلاحيات الملف.",
            'inventory_update': "فشل في تحديث المخزون. قد تكون الكمية غير متاحة."
        }

        # البحث عن رسالة محددة للسياق
        if context in context_messages:
            return context_messages[context]

        # البحث عن رسالة عامة لنوع الخطأ
        error_type = type(error).__name__
        if error_type in error_messages:
            return error_messages[error_type]

        # رسالة افتراضية
        return "حدث خطأ غير متوقع. يرجى المحاولة مرة أخرى أو الاتصال بالدعم الفني."

    def retry_operation(self, operation: Callable, max_retries: Optional[int] = None,
                       context: str = "Unknown", *args, **kwargs) -> Any:
        """
        إعادة محاولة العملية في حالة فشلها

        Args:
            operation: العملية المراد إعادة محاولتها
            max_retries: عدد المحاولات القصوى
            context: سياق العملية
            *args, **kwargs: معاملات العملية

        Returns:
            Any: نتيجة العملية أو None في حالة الفشل
        """
        retries = max_retries or self.max_retries

        for attempt in range(retries + 1):
            try:
                result = operation(*args, **kwargs)
                if attempt > 0:
                    self.logger.log_app_event('info', f"العملية نجحت في المحاولة {attempt + 1}: {context}")
                return result
            except Exception as e:
                if attempt < retries:
                    self.logger.log_app_event('warning', f"فشلت المحاولة {attempt + 1} للعملية {context}: {str(e)}")
                    continue
                else:
                    self.handle_error(e, context)
                    return None

    def validate_and_execute(self, validation_func: Callable, execution_func: Callable,
                           validation_context: str = "validation",
                           execution_context: str = "execution",
                           *args, **kwargs) -> Tuple[bool, Any]:
        """
        التحقق من الصحة ثم تنفيذ العملية

        Args:
            validation_func: دالة التحقق
            execution_func: دالة التنفيذ
            validation_context: سياق التحقق
            execution_context: سياق التنفيذ

        Returns:
            Tuple[bool, Any]: (نجح/فشل, النتيجة)
        """
        try:
            # التحقق من الصحة
            is_valid, validation_message = validation_func(*args, **kwargs)
            if not is_valid:
                st.error(validation_message)
                return False, None

            # تنفيذ العملية
            result = execution_func(*args, **kwargs)
            return True, result

        except Exception as e:
            self.handle_error(e, execution_context)
            return False, None

    def get_error_statistics(self) -> Dict[str, Any]:
        """
        الحصول على إحصائيات الأخطاء

        Returns:
            Dict: إحصائيات الأخطاء
        """
        return {
            'error_counts': self.error_counts.copy(),
            'total_errors': sum(self.error_counts.values()),
            'unique_error_types': len(self.error_counts),
            'most_common_error': max(self.error_counts.items(), key=lambda x: x[1]) if self.error_counts else None
        }

# إنشاء instance عالمي
error_handler = ErrorHandler()

# Decorators لمعالجة الأخطاء
def handle_errors(context: str = "Unknown", show_user_message: bool = True, log_error: bool = True):
    """
    Decorator لمعالجة الأخطاء في الدوال

    Args:
        context: سياق الدالة
        show_user_message: عرض رسالة للمستخدم
        log_error: تسجيل الخطأ
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error_handler.handle_error(e, context, show_user_message, log_error)
                return None
        return wrapper
    return decorator

def require_permission(permission: str, message: str = "ليس لديك صلاحية للوصول لهذه الصفحة"):
    """
    Decorator للتحقق من الصلاحيات

    Args:
        permission: الصلاحية المطلوبة
        message: رسالة الخطأ
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            from core.permission_manager import check_permission
            if not check_permission(permission):
                st.error(message)
                st.stop()
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_operation(operation_name: str, log_level: str = "info"):
    """
    Decorator لتسجيل العمليات

    Args:
        operation_name: اسم العملية
        log_level: مستوى التسجيل
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                advanced_logger.log_app_event(log_level, f"تم تنفيذ {operation_name} بنجاح في {duration:.3f} ثانية")
                return result
            except Exception as e:
                duration = (datetime.now() - start_time).total_seconds()
                advanced_logger.log_app_event('error', f"فشل في تنفيذ {operation_name} بعد {duration:.3f} ثانية: {str(e)}")
                raise
        return wrapper
    return decorator

# دوال مساعدة للاستخدام في Streamlit
def display_error_page(error_message: str = "حدث خطأ غير متوقع"):
    """عرض صفحة خطأ في Streamlit"""
    st.error("🚨 " + error_message)
    st.info("يرجى المحاولة مرة أخرى أو الاتصال بالدعم الفني إذا استمر الخطأ.")

    with st.expander("تفاصيل إضافية"):
        st.code(traceback.format_exc())

    if st.button("🔄 إعادة تحميل الصفحة"):
        st.rerun()

def display_error_statistics():
    """عرض إحصائيات الأخطاء في Streamlit"""
    st.subheader("📊 إحصائيات الأخطاء")

    stats = error_handler.get_error_statistics()

    if not stats['error_counts']:
        st.success("لا توجد أخطاء مسجلة")
        return

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("إجمالي الأخطاء", stats['total_errors'])

    with col2:
        st.metric("أنواع الأخطاء المختلفة", stats['unique_error_types'])

    with col3:
        if stats['most_common_error']:
            error_type, count = stats['most_common_error']
            st.metric("الخطأ الأكثر شيوعاً", f"{error_type} ({count})")

    with col4:
        st.metric("معدل الأخطاء", f"{stats['total_errors']/max(stats['unique_error_types'], 1):.1f}")

    # عرض تفصيلي للأخطاء
    st.subheader("تفاصيل الأخطاء")

    error_data = []
    for error_key, count in stats['error_counts'].items():
        context, error_type = error_key.split(':', 1)
        error_data.append({
            'السياق': context,
            'نوع الخطأ': error_type,
            'العدد': count
        })

    if error_data:
        import pandas as pd
        df = pd.DataFrame(error_data)
        st.dataframe(df, use_container_width=True)

        # رسم بياني
        st.bar_chart(df.set_index('السياق')['العدد'])

def safe_execute(func: Callable, *args, context: str = "Unknown", **kwargs) -> Any:
    """
    تنفيذ دالة بأمان مع معالجة الأخطاء

    Args:
        func: الدالة المراد تنفيذها
        context: سياق التنفيذ

    Returns:
        Any: نتيجة الدالة أو None
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        error_handler.handle_error(e, context)
        return None