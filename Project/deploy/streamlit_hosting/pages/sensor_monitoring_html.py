import streamlit as st

def sensor_monitoring_html():
    st.markdown(
        """
        <style>
        .container {
            max-width: 900px;
            margin: auto;
            font-family: Arial, sans-serif;
        }
        header {
            text-align: center;
            margin-bottom: 3rem;
        }
        h1 {
            font-size: 2.5rem;
            font-weight: 800;
            color: #0077cc;
            text-shadow: 0 0.5px 0 #00aaff;
            letter-spacing: 0.05em;
        }
        p {
            font-size: 1.25rem;
            color: #555555;
            margin-top: 0.5rem;
        }
        section {
            margin-bottom: 2rem;
        }
        h2 {
            font-size: 1.75rem;
            font-weight: 700;
            color: #004080;
            border-bottom: 2px solid #0077cc;
            padding-bottom: 0.5rem;
            text-align: center;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 1rem;
            justify-items: center;
        }
        .card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 1rem;
            width: 100%;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            background-color: #f9f9f9;
        }
        </style>

        <div class="container">
            <header>
                <h1>لوحة تحكم خزانات الوقود الذكية</h1>
                <p>نظام مراقبة متقدم للتشغيل والتحكم</p>
            </header>

            <section>
                <h2>بيانات الخزانات (التصميم الأسطواني الأفقي)</h2>
                <div id="tanks-display" class="grid">
                    <div class="card">خزان 1: 75% ممتلئ</div>
                    <div class="card">خزان 2: 50% ممتلئ</div>
                    <div class="card">خزان 3: 90% ممتلئ</div>
                </div>
            </section>

            <hr>

            <section>
                <h2>وحدات التحكم بالمضخات</h2>
                <div id="pumps-display" class="grid">
                    <div class="card">مضخة 1: تعمل</div>
                    <div class="card">مضخة 2: متوقفة</div>
                </div>
            </section>
        </div>
        """,
        unsafe_allow_html=True
    )
