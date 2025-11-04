import streamlit as st
from core.database_enhanced import get_connection
import bcrypt

def show_password_reset():
    """Display password reset interface"""
    st.markdown("""
        <style>
        .reset-container {
            max-width: 500px;
            margin: 2rem auto;
            padding: 2rem;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            color: white;
        }
        .reset-header {
            text-align: center;
            margin-bottom: 2rem;
        }
        .reset-form {
            background: rgba(255,255,255,0.1);
            padding: 2rem;
            border-radius: 15px;
            backdrop-filter: blur(10px);
        }
        .stTextInput input, .stSelectbox select {
            background: rgba(255,255,255,0.2) !important;
            border: 2px solid rgba(255,255,255,0.3) !important;
            border-radius: 10px !important;
            color: white !important;
            padding: 0.75rem 1rem !important;
        }
        .reset-button {
            background: linear-gradient(45deg, #48bb78, #38a169) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-size: 1.1rem !important;
            font-weight: bold !important;
            width: 100% !important;
            margin-top: 1rem !important;
        }
        .back-button {
            background: linear-gradient(45deg, #ed8936, #dd6b20) !important;
            border: none !important;
            border-radius: 25px !important;
            padding: 0.75rem 2rem !important;
            font-size: 1rem !important;
            width: 100% !important;
            margin-top: 0.5rem !important;
        }
        .success-message {
            background: rgba(72,187,120,0.2);
            border: 1px solid #48bb78;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: #48bb78;
        }
        .error-message {
            background: rgba(255,107,107,0.2);
            border: 1px solid #ff6b6b;
            border-radius: 10px;
            padding: 1rem;
            margin: 1rem 0;
            color: #ff6b6b;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="reset-container">
            <div class="reset-header">
                <h2>🔓 إعادة تعيين كلمة المرور</h2>
                <p>أدخل بياناتك لإعادة تعيين كلمة المرور</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    with st.form("reset_form"):
        st.markdown('<div class="reset-form">', unsafe_allow_html=True)

        reset_user = st.text_input("👤 اسم المستخدم")
        reset_type = st.selectbox("🏢 نوع الحساب", ["Owner", "Employee"])
        security_answer = st.text_input("🏙️ ما هو اسم مدينتك؟ (سؤال أمان)")
        new_pw = st.text_input("🔒 كلمة المرور الجديدة", type="password")
        confirm_pw = st.text_input("🔒 تأكيد كلمة المرور الجديدة", type="password")

        col1, col2 = st.columns(2)
        with col1:
            reset_btn = st.form_submit_button("🔄 تغيير كلمة المرور", use_container_width=True)
        with col2:
            back_btn = st.form_submit_button("⬅️ رجوع", use_container_width=True)

        st.markdown('</div>', unsafe_allow_html=True)

    if reset_btn:
        if not all([reset_user, security_answer, new_pw, confirm_pw]):
            st.markdown('<div class="error-message">⚠️ يرجى ملء جميع الحقول</div>', unsafe_allow_html=True)
        elif new_pw != confirm_pw:
            st.markdown('<div class="error-message">❌ كلمتا المرور غير متطابقتين</div>', unsafe_allow_html=True)
        else:
            success, message = reset_password(reset_user, reset_type, security_answer, new_pw)
            if success:
                st.markdown(f'<div class="success-message">✅ {message}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-message">❌ {message}</div>', unsafe_allow_html=True)

    if back_btn:
        st.session_state.show_password_reset = False
        st.rerun()

def reset_password(username, user_type, security_answer, new_password):
    """Reset user password"""
    conn = get_connection()
    if not conn:
        return False, "خطأ في الاتصال بقاعدة البيانات"

    c = conn.cursor()

    try:
        if user_type == "Owner":
            c.execute("SELECT City FROM Owners WHERE Owner_Name=%s", (username,))
            row = c.fetchone()
            city = None
            if row:
                # handle dict or tuple cursor
                city = row.get('City') if isinstance(row, dict) else row[0]
            if city and security_answer.strip().lower() == str(city).strip().lower():
                # store hashed password
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                c.execute("UPDATE Owners SET hashed_password=%s WHERE Owner_Name=%s", (hashed, username))
                conn.commit()
                conn.close()
                return True, "تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول."
            else:
                conn.close()
                return False, "إجابة سؤال الأمان غير صحيحة أو المستخدم غير موجود."
        else:  # Employee
            c.execute("SELECT City FROM Employees WHERE Emp_Name=%s", (username,))
            row = c.fetchone()
            city = None
            if row:
                city = row.get('City') if isinstance(row, dict) else row[0]
            if city and security_answer.strip().lower() == str(city).strip().lower():
                hashed = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
                c.execute("UPDATE Employees SET hashed_password=%s WHERE Emp_Name=%s", (hashed, username))
                conn.commit()
                conn.close()
                return True, "تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول."
            else:
                conn.close()
                return False, "إجابة سؤال الأمان غير صحيحة أو المستخدم غير موجود."
    except Exception as e:
        conn.close()
        return False, f"حدث خطأ أثناء إعادة تعيين كلمة المرور: {str(e)}"

def main():
    """Main password reset function"""
    show_password_reset()

if __name__ == "__main__":
    main()
