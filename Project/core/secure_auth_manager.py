"""
نظام إعادة تعيين كلمة مرور آمن مع تشفير - Petrol Pump Management System
يوفر هذا النظام إدارة آمنة للمصادقة مع تشفير كامل
"""

import hashlib
import secrets
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import re
from database import get_connection
import streamlit as st

# إعداد نظام التسجيل
logging.basicConfig(
    filename='secure_auth_manager.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class SecureAuthManager:
    """مدير المصادقة الآمن"""

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.salt_length = 32
        self.token_length = 64
        self.reset_token_expiry = 3600  # ساعة واحدة

        # متطلبات كلمة المرور
        self.password_requirements = {
            'min_length': 8,
            'require_uppercase': True,
            'require_lowercase': True,
            'require_digits': True,
            'require_special': True
        }

    def hash_password(self, password: str, salt: Optional[str] = None) -> Tuple[str, str]:
        """
        تشفير كلمة المرور باستخدام SHA-256 مع salt

        Args:
            password: كلمة المرور
            salt: الـ salt (اختياري، سيتم إنشاؤه إذا لم يكن موجوداً)

        Returns:
            Tuple[str, str]: (hash, salt)
        """
        if not salt:
            salt = secrets.token_hex(self.salt_length)

        # إنشاء hash باستخدام SHA-256 مع salt
        password_with_salt = password + salt
        hashed_password = hashlib.sha256(password_with_salt.encode('utf-8')).hexdigest()

        return hashed_password, salt

    def verify_password(self, password: str, hashed_password: str, salt: str) -> bool:
        """
        التحقق من كلمة المرور

        Args:
            password: كلمة المرور المدخلة
            hashed_password: كلمة المرور المشفرة المخزنة
            salt: الـ salt المستخدم

        Returns:
            bool: صحيحة أم لا
        """
        computed_hash, _ = self.hash_password(password, salt)
        return computed_hash == hashed_password

    def validate_password_strength(self, password: str) -> Tuple[bool, str]:
        """
        التحقق من قوة كلمة المرور

        Args:
            password: كلمة المرور

        Returns:
            Tuple[bool, str]: (صالحة/غير صالحة, رسالة)
        """
        if len(password) < self.password_requirements['min_length']:
            return False, f"كلمة المرور يجب أن تكون على الأقل {self.password_requirements['min_length']} أحرف"

        if self.password_requirements['require_uppercase'] and not re.search(r'[A-Z]', password):
            return False, "كلمة المرور يجب أن تحتوي على حرف كبير على الأقل"

        if self.password_requirements['require_lowercase'] and not re.search(r'[a-z]', password):
            return False, "كلمة المرور يجب أن تحتوي على حرف صغير على الأقل"

        if self.password_requirements['require_digits'] and not re.search(r'\d', password):
            return False, "كلمة المرور يجب أن تحتوي على رقم على الأقل"

        if self.password_requirements['require_special'] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "كلمة المرور يجب أن تحتوي على رمز خاص على الأقل"

        return True, "كلمة المرور قوية"

    def generate_reset_token(self) -> str:
        """
        إنشاء رمز إعادة تعيين كلمة المرور

        Returns:
            str: الرمز المولد
        """
        return secrets.token_urlsafe(self.token_length)

    def create_password_reset_request(self, user_type: str, identifier: str) -> Tuple[bool, str]:
        """
        إنشاء طلب إعادة تعيين كلمة المرور

        Args:
            user_type: نوع المستخدم (Owner/Employee)
            identifier: معرف المستخدم (اسم المالك أو اسم الموظف)

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        try:
            conn = get_connection()
            if not conn:
                return False, "فشل في الاتصال بقاعدة البيانات"

            c = conn.cursor()

            # التحقق من وجود المستخدم
            if user_type == 'Owner':
                c.execute("SELECT Owner_Name, City FROM Owners WHERE Owner_Name = %s", (identifier,))
                user_data = c.fetchone()
                if not user_data:
                    conn.close()
                    return False, "المالك غير موجود"
                security_question = f"ما هو اسم مدينتك؟ (الإجابة: {user_data[1]})"
            else:  # Employee
                c.execute("SELECT Employee_ID, Emp_Name, City FROM Employee WHERE Emp_Name = %s", (identifier,))
                user_data = c.fetchone()
                if not user_data:
                    conn.close()
                    return False, "الموظف غير موجود"
                security_question = f"ما هو اسم مدينتك؟ (الإجابة: {user_data[2]})"

            # إنشاء رمز إعادة التعيين
            reset_token = self.generate_reset_token()
            expiry_time = datetime.now() + timedelta(seconds=self.reset_token_expiry)

            # حفظ طلب إعادة التعيين
            c.execute("""
                INSERT INTO PasswordResetTokens
                (User_Type, User_Identifier, Reset_Token, Expiry_Time, Created_At, Used)
                VALUES (%s, %s, %s, %s, %s, FALSE)
            """, (user_type, identifier, reset_token, expiry_time, datetime.now()))

            conn.commit()
            conn.close()

            self.logger.info(f"Password reset request created for {user_type}:{identifier}")

            return True, f"تم إرسال رمز إعادة التعيين. سؤال الأمان: {security_question}"

        except Exception as e:
            self.logger.error(f"Error creating password reset request: {str(e)}")
            return False, f"فشل في إنشاء طلب إعادة التعيين: {str(e)}"

    def verify_security_answer_and_reset(self, user_type: str, identifier: str,
                                       security_answer: str, new_password: str) -> Tuple[bool, str]:
        """
        التحقق من إجابة سؤال الأمان وإعادة تعيين كلمة المرور

        Args:
            user_type: نوع المستخدم
            identifier: معرف المستخدم
            security_answer: إجابة سؤال الأمان
            new_password: كلمة المرور الجديدة

        Returns:
            Tuple[bool, str]: (نجح/فشل, رسالة)
        """
        try:
            # التحقق من قوة كلمة المرور الجديدة
            is_strong, message = self.validate_password_strength(new_password)
            if not is_strong:
                return False, message

            conn = get_connection()
            if not conn:
                return False, "فشل في الاتصال بقاعدة البيانات"

            c = conn.cursor()

            # التحقق من إجابة سؤال الأمان
            if user_type == 'Owner':
                c.execute("SELECT City FROM Owners WHERE Owner_Name = %s", (identifier,))
            else:
                c.execute("SELECT City FROM Employee WHERE Emp_Name = %s", (identifier,))

            user_data = c.fetchone()
            if not user_data or not user_data[0]:
                conn.close()
                return False, "المستخدم غير موجود أو لا يحتوي على معلومات أمان"

            stored_answer = user_data[0].strip().lower()
            provided_answer = security_answer.strip().lower()

            if stored_answer != provided_answer:
                conn.close()
                return False, "إجابة سؤال الأمان غير صحيحة"

            # تشفير كلمة المرور الجديدة
            hashed_password, salt = self.hash_password(new_password)

            # تحديث كلمة المرور
            if user_type == 'Owner':
                c.execute("""
                    UPDATE Owners
                    SET Contact_NO = %s, Password_Salt = %s
                    WHERE Owner_Name = %s
                """, (hashed_password, salt, identifier))
            else:
                c.execute("""
                    UPDATE Employee
                    SET Employee_ID = %s, Password_Salt = %s
                    WHERE Emp_Name = %s
                """, (hashed_password, salt, identifier))

            # تحديث حالة رمز إعادة التعيين إلى مستخدم
            c.execute("""
                UPDATE PasswordResetTokens
                SET Used = TRUE, Used_At = %s
                WHERE User_Type = %s AND User_Identifier = %s AND Used = FALSE
                ORDER BY Created_At DESC LIMIT 1
            """, (datetime.now(), user_type, identifier))

            conn.commit()
            conn.close()

            self.logger.info(f"Password reset successful for {user_type}:{identifier}")
            return True, "تم إعادة تعيين كلمة المرور بنجاح"

        except Exception as e:
            self.logger.error(f"Error resetting password: {str(e)}")
            return False, f"فشل في إعادة تعيين كلمة المرور: {str(e)}"

    def authenticate_user(self, user_type: str, username: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        المصادقة على المستخدم

        Args:
            user_type: نوع المستخدم
            username: اسم المستخدم
            password: كلمة المرور

        Returns:
            Tuple[bool, Optional[Dict]]: (نجح/فشل, بيانات المستخدم)
        """
        try:
            conn = get_connection()
            if not conn:
                return False, None

            c = conn.cursor()

            if user_type == 'Owner':
                c.execute("SELECT Owner_Name, Contact_NO, Password_Salt FROM Owners WHERE Owner_Name = %s", (username,))
            else:
                c.execute("SELECT Emp_Name, Employee_ID, Password_Salt FROM Employee WHERE Emp_Name = %s", (username,))

            user_data = c.fetchone()
            conn.close()

            if not user_data:
                return False, None

            stored_hash = user_data[1]
            stored_salt = user_data[2] if len(user_data) > 2 else None

            # التحقق من كلمة المرور
            if stored_salt and stored_hash:
                # كلمة مرور مشفرة
                if not self.verify_password(password, stored_hash, stored_salt):
                    return False, None
            else:
                # كلمة مرور غير مشفرة (للتوافق مع البيانات القديمة)
                if stored_hash != password:
                    return False, None

            user_info = {
                'username': user_data[0],
                'user_type': user_type,
                'authenticated_at': datetime.now()
            }

            self.logger.info(f"User authenticated: {user_type}:{username}")
            return True, user_info

        except Exception as e:
            self.logger.error(f"Authentication error: {str(e)}")
            return False, None

    def migrate_legacy_passwords(self) -> Tuple[int, int]:
        """
        ترحيل كلمات المرور القديمة غير المشفرة إلى النظام الجديد

        Returns:
            Tuple[int, int]: (عدد المرحلين, إجمالي المستخدمين)
        """
        try:
            conn = get_connection()
            if not conn:
                return 0, 0

            c = conn.cursor()

            total_migrated = 0

            # ترحيل كلمات مرور الملاك
            c.execute("SELECT Owner_Name, Contact_NO FROM Owners WHERE Password_Salt IS NULL OR Password_Salt = ''")
            owners = c.fetchall()

            for owner in owners:
                if owner[1] and len(owner[1]) < 64:  # كلمة مرور غير مشفرة
                    hashed_password, salt = self.hash_password(owner[1])
                    c.execute("""
                        UPDATE Owners
                        SET Contact_NO = %s, Password_Salt = %s
                        WHERE Owner_Name = %s
                    """, (hashed_password, salt, owner[0]))
                    total_migrated += 1

            # ترحيل كلمات مرور الموظفين
            c.execute("SELECT Emp_Name, Employee_ID FROM Employee WHERE Password_Salt IS NULL OR Password_Salt = ''")
            employees = c.fetchall()

            for emp in employees:
                if emp[1] and len(emp[1]) < 64:  # كلمة مرور غير مشفرة
                    hashed_password, salt = self.hash_password(emp[1])
                    c.execute("""
                        UPDATE Employee
                        SET Employee_ID = %s, Password_Salt = %s
                        WHERE Emp_Name = %s
                    """, (hashed_password, salt, emp[0]))
                    total_migrated += 1

            conn.commit()
            conn.close()

            total_users = len(owners) + len(employees)
            self.logger.info(f"Password migration completed: {total_migrated}/{total_users} passwords migrated")

            return total_migrated, total_users

        except Exception as e:
            self.logger.error(f"Error migrating passwords: {str(e)}")
            return 0, 0

# إنشاء instance عالمي
secure_auth_manager = SecureAuthManager()

# دوال مساعدة للاستخدام في Streamlit
def secure_password_reset_ui():
    """واجهة إعادة تعيين كلمة المرور الآمنة في Streamlit"""
    st.subheader("🔐 إعادة تعيين كلمة المرور الآمنة")

    # الخطوة 1: طلب إعادة التعيين
    if 'reset_step' not in st.session_state:
        st.session_state.reset_step = 1

    if st.session_state.reset_step == 1:
        st.write("**الخطوة 1:** طلب إعادة التعيين")

        user_type = st.selectbox("نوع الحساب:", ["Owner", "Employee"], key="reset_user_type")
        identifier = st.text_input("اسم المستخدم:", key="reset_identifier")

        if st.button("طلب إعادة التعيين", use_container_width=True):
            if not identifier:
                st.error("يرجى إدخال اسم المستخدم")
                return

            success, message = secure_auth_manager.create_password_reset_request(user_type, identifier)

            if success:
                st.success(message)
                st.session_state.reset_step = 2
                st.session_state.reset_user_type = user_type
                st.session_state.reset_identifier = identifier
                st.rerun()
            else:
                st.error(message)

    # الخطوة 2: التحقق من سؤال الأمان وإعادة التعيين
    elif st.session_state.reset_step == 2:
        st.write("**الخطوة 2:** التحقق والإعادة التعيين")

        security_answer = st.text_input("إجابة سؤال الأمان (اسم المدينة):", key="security_answer")
        new_password = st.text_input("كلمة المرور الجديدة:", type="password", key="new_password")
        confirm_password = st.text_input("تأكيد كلمة المرور الجديدة:", type="password", key="confirm_password")

        # عرض متطلبات كلمة المرور
        with st.expander("متطلبات كلمة المرور"):
            st.write("• على الأقل 8 أحرف")
            st.write("• حرف كبير واحد على الأقل")
            st.write("• حرف صغير واحد على الأقل")
            st.write("• رقم واحد على الأقل")
            st.write("• رمز خاص واحد على الأقل (!@#$%^&*)")

        col1, col2 = st.columns(2)

        with col1:
            if st.button("إعادة التعيين", use_container_width=True):
                if not security_answer:
                    st.error("يرجى إدخال إجابة سؤال الأمان")
                    return

                if new_password != confirm_password:
                    st.error("كلمات المرور غير متطابقة")
                    return

                success, message = secure_auth_manager.verify_security_answer_and_reset(
                    st.session_state.reset_user_type,
                    st.session_state.reset_identifier,
                    security_answer,
                    new_password
                )

                if success:
                    st.success(message)
                    st.info("يمكنك الآن تسجيل الدخول بكلمة المرور الجديدة")

                    # تنظيف session
                    for key in ['reset_step', 'reset_user_type', 'reset_identifier']:
                        if key in st.session_state:
                            del st.session_state[key]

                    st.rerun()
                else:
                    st.error(message)

        with col2:
            if st.button("العودة", use_container_width=True):
                st.session_state.reset_step = 1
                st.rerun()

def secure_authenticate_user(user_type: str, username: str, password: str) -> bool:
    """مصادقة آمنة للمستخدم"""
    success, user_info = secure_auth_manager.authenticate_user(user_type, username, password)

    if success and user_info:
        # تحديث session state
        st.session_state.logged_in = True
        st.session_state.user_type = user_type
        st.session_state.username = username
        st.session_state.permissions = []  # سيتم تحديثها لاحقاً

        st.success(f"تم تسجيل الدخول بنجاح ك{user_type}")
        return True
    else:
        st.error("بيانات الدخول غير صحيحة")
        return False

def migrate_legacy_passwords_ui():
    """واجهة ترحيل كلمات المرور القديمة"""
    st.subheader("🔄 ترحيل كلمات المرور القديمة")

    # التحقق من الصلاحية
    from core.permission_manager import check_permission
    if not check_permission('ADMIN'):
        st.error("يجب أن تكون مديراً لتنفيذ هذه العملية")
        return

    st.warning("⚠️ هذه العملية ستشفر جميع كلمات المرور غير المشفرة في النظام")
    st.info("تأكد من إخطار جميع المستخدمين قبل تنفيذ هذه العملية")

    if st.button("بدء الترحيل", use_container_width=True):
        with st.spinner("جاري ترحيل كلمات المرور..."):
            migrated, total = secure_auth_manager.migrate_legacy_passwords()

        if migrated > 0:
            st.success(f"تم ترحيل {migrated} من أصل {total} كلمة مرور بنجاح")
        else:
            st.info("لا توجد كلمات مرور تحتاج ترحيل")

        # تسجيل في audit trail
        from core.audit_trail import log_user_action
        log_user_action(
            'System',
            'PASSWORD_MIGRATION',
            'UPDATE',
            new_values={'migrated': migrated, 'total': total}
        )

def display_password_requirements():
    """عرض متطلبات كلمة المرور"""
    st.subheader("📋 متطلبات كلمة المرور")

    requirements = secure_auth_manager.password_requirements

    col1, col2 = st.columns(2)

    with col1:
        st.write(f"• الحد الأدنى للطول: {requirements['min_length']} أحرف")
        st.write("• يجب أن تحتوي على حرف كبير" if requirements['require_uppercase'] else "• لا يشترط حرف كبير")
        st.write("• يجب أن تحتوي على حرف صغير" if requirements['require_lowercase'] else "• لا يشترط حرف صغير")

    with col2:
        st.write("• يجب أن تحتوي على رقم" if requirements['require_digits'] else "• لا يشترط رقم")
        st.write("• يجب أن تحتوي على رمز خاص" if requirements['require_special'] else "• لا يشترط رمز خاص")

    # اختبار قوة كلمة المرور
    st.subheader("اختبار قوة كلمة المرور")
    test_password = st.text_input("اختبر كلمة مرور:", type="password", key="test_password")

    if test_password:
        is_strong, message = secure_auth_manager.validate_password_strength(test_password)
        if is_strong:
            st.success("✅ " + message)
        else:
            st.error("❌ " + message)