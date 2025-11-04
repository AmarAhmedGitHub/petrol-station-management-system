def get_full_css(theme='light', rtl=True):
    """Return the complete CSS for the modern design system with theme and RTL support"""

    # Google Fonts Import with additional weights
    font_import = "@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@200..1000&display=swap');"

    # Define font variable
    font_family = "'Cairo', sans-serif"

    # Enhanced CSS Variables for theming with better colors and gradients
    css_vars = """
    :root {
        /* Light Theme Variables - Enhanced */
        --font-family: 'Cairo', sans-serif;
        --primary-color: #2563eb;
        --secondary-color: #06b6d4;
        --accent-color: #8b5cf6;
        --gradient-start: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-end: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --bg-main: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        --bg-content: #ffffff;
        --bg-sidebar: #ffffff;
        --bg-card: rgba(255, 255, 255, 0.95);
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --text-accent: #2563eb;
        --text-muted: #94a3b8;
        --border-color: #e2e8f0;
        --border-light: #f1f5f9;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        --shadow-color: rgba(0, 0, 0, 0.1);
        --shadow-hover-color: rgba(0, 0, 0, 0.15);
        --button-text-color: #ffffff;
        --success-bg: #dcfce7;
        --success-text: #166534;
        --success-border: #bbf7d0;
        --warning-bg: #fef3c7;
        --warning-text: #92400e;
        --warning-border: #fde68a;
        --error-bg: #fee2e2;
        --error-text: #991b1b;
        --error-border: #fecaca;
        --info-bg: #dbeafe;
        --info-text: #1e40af;
        --info-border: #bfdbfe;

        /* Fuel Station Specific Colors */
        --fuel-primary: #ea580c;
        --fuel-secondary: #dc2626;
        --fuel-accent: #f59e0b;
        --tank-bg: linear-gradient(145deg, #1f2937, #374151);
        --pump-bg: linear-gradient(145deg, #1f2937, #374151);

        /* Animation Variables */
        --transition-fast: 0.15s ease;
        --transition-normal: 0.3s ease;
        --transition-slow: 0.5s ease;
    }

    [data-theme="dark"] {
        /* Dark Theme Variables - Enhanced */
        --primary-color: #3b82f6;
        --secondary-color: #06b6d4;
        --accent-color: #a78bfa;
        --gradient-start: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        --gradient-end: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        --bg-main: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        --bg-content: #1e293b;
        --bg-sidebar: #1e293b;
        --bg-card: rgba(30, 41, 59, 0.95);
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --text-accent: #3b82f6;
        --text-muted: #64748b;
        --border-color: #334155;
        --border-light: #1e293b;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.3);
        --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.4), 0 2px 4px -1px rgba(0, 0, 0, 0.3);
        --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.4);
        --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.6), 0 10px 10px -5px rgba(0, 0, 0, 0.5);
        --shadow-color: rgba(0, 0, 0, 0.4);
        --shadow-hover-color: rgba(0, 0, 0, 0.6);
        --button-text-color: #0f172a;
        --success-bg: #14532d;
        --success-text: #4ade80;
        --success-border: #166534;
        --warning-bg: #451a03;
        --warning-text: #fbbf24;
        --warning-border: #92400e;
        --error-bg: #450a0a;
        --error-text: #f87171;
        --error-border: #991b1b;
        --info-bg: #1e3a8a;
        --info-text: #60a5fa;
        --info-border: #1e40af;

        /* Fuel Station Specific Colors - Dark */
        --fuel-primary: #ea580c;
        --fuel-secondary: #dc2626;
        --fuel-accent: #f59e0b;
        --tank-bg: linear-gradient(145deg, #111827, #1f2937);
        --pump-bg: linear-gradient(145deg, #111827, #1f2937);
    }
    """

    # Apply theme and RTL attributes
    theme_attr = f' data-theme="{theme}"' if theme == 'dark' else ''
    rtl_attr = ' dir="rtl"' if rtl else ''

    css = f"{font_import}\n{css_vars}\n{theme_attr}{rtl_attr}\n"

    css += """
/* --- Base & Global Styles --- */
* {{
    box-sizing: border-box;
}}

body {{
    font-family: var(--font-family);
    background: var(--bg-main);
    color: var(--text-primary);
    direction: {'rtl' if rtl else 'ltr'};
    line-height: 1.6;
    margin: 0;
    padding: 0;
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}}

/* Hide Streamlit's default elements */
#MainMenu, header, footer {{
    visibility: hidden;
}}

/* --- Main Layout --- */
.main-header {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    text-align: center;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-lg);
    position: relative;
    overflow: hidden;
}}

.main-header::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--gradient-start);
}}

.main-header h1 {{
    color: var(--text-primary);
    font-size: 2.5rem;
    font-weight: 800;
    margin-bottom: 0.75rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}

.main-header p {{
    color: var(--text-secondary);
    font-size: 1.2rem;
    margin: 0;
    font-weight: 500;
}}

.content-area {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 2.5rem;
    margin-bottom: 2rem;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-xl);
    min-height: 60vh;
    position: relative;
    overflow: hidden;
}}

.content-area::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-end);
}}

/* --- Sidebar --- */
[data-testid="stSidebar"] {{
    background: var(--bg-sidebar);
    border-left: 1px solid var(--border-color);
    box-shadow: var(--shadow-lg);
}}

.sidebar-header {{
    text-align: center;
    padding: 2rem 1.5rem;
    margin-bottom: 1.5rem;
    border-bottom: 2px solid var(--border-color);
    background: var(--bg-card);
    border-radius: 0 0 15px 15px;
}}

.sidebar-header h2 {{
    font-size: 1.6rem;
    font-weight: 700;
    color: var(--text-accent);
    margin: 0;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}}

/* --- User Info Card in Sidebar --- */
.user-info-card {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 15px;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-md);
    transition: var(--transition-normal);
}}

.user-info-card:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}}

.user-info-card p {{
    margin: 0.75rem 0;
    font-size: 0.95rem;
    line-height: 1.5;
}}

.user-info-card strong {{
    color: var(--text-primary);
    font-weight: 600;
}}

/* --- Navigation Buttons --- */
.stButton button {{
    background: var(--bg-card) !important;
    color: var(--text-secondary) !important;
    border: 2px solid var(--border-light) !important;
    border-radius: 12px !important;
    padding: 1rem 1.25rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    transition: var(--transition-normal) !important;
    width: 100% !important;
    text-align: right !important;
    display: flex !important;
    align-items: center !important;
    justify-content: flex-start !important;
    box-shadow: var(--shadow-sm) !important;
    position: relative !important;
    overflow: hidden !important;
}}

.stButton button::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: var(--transition-slow);
}}

.stButton button:hover {{
    background: var(--bg-content) !important;
    color: var(--text-accent) !important;
    border-color: var(--text-accent) !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--shadow-md) !important;
}}

.stButton button:hover::before {{
    left: 100%;
}}

.stButton button:active {{
    transform: translateY(0) !important;
    box-shadow: var(--shadow-sm) !important;
}}

/* --- Sidebar Radio Navigation --- */
[data-testid="stSidebar"] .stRadio > div {{
    gap: 1rem;
}}

[data-testid="stSidebar"] .stRadio [role="radiogroup"] {{
    display: grid;
    gap: 0.75rem;
}}

[data-testid="stSidebar"] .stRadio input[type="radio"] {{
    display: none;
}}

[data-testid="stSidebar"] .stRadio [role="radio"] {{
    background: var(--bg-card);
    border: 2px solid var(--border-light);
    border-radius: 15px;
    padding: 1.2rem 1.5rem;
    width: 100%;
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 1rem;
    transition: var(--transition-normal);
    box-shadow: var(--shadow-sm);
    cursor: pointer;
    position: relative;
    overflow: hidden;
}}

[data-testid="stSidebar"] .stRadio [role="radio"]::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
    transition: var(--transition-slow);
}}

[data-testid="stSidebar"] .stRadio [role="radio"]:hover {{
    color: var(--text-accent);
    border-color: var(--text-accent);
    box-shadow: var(--shadow-md);
    transform: translateX(-3px);
}}

[data-testid="stSidebar"] .stRadio [role="radio"]:hover::before {{
    left: 100%;
}}

[data-testid="stSidebar"] .stRadio [role="radio"] > div:first-child {{
    display: none;
}}

[data-testid="stSidebar"] .stRadio [role="radio"] > div:nth-child(2) {{
    width: 100%;
    text-align: right;
    font-size: 1.1rem;
}}

[data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] {{
    background: var(--gradient-start);
    color: var(--button-text-color);
    border-color: transparent;
    box-shadow: var(--shadow-lg);
    transform: translateX(-5px);
}}

[data-testid="stSidebar"] .stRadio [role="radio"][aria-checked="true"] > div:nth-child(2) {{
    color: var(--button-text-color);
    font-weight: 700;
}}

/* --- Special Buttons (Logout) --- */
.logout-container .stButton button {{
    background: var(--error-bg) !important;
    color: var(--error-text) !important;
    border: 2px solid var(--error-border) !important;
    box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2) !important;
}}

.logout-container .stButton button:hover {{
    background: var(--error-text) !important;
    color: var(--button-text-color) !important;
    border-color: var(--error-text) !important;
    box-shadow: 0 6px 16px rgba(239, 68, 68, 0.3) !important;
    transform: translateY(-2px) !important;
}}

/* --- Status Indicators --- */
.automation-status {{
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    background: var(--success-bg);
    color: var(--success-text);
    padding: 1rem 1.5rem;
    border-radius: 15px;
    margin-bottom: 2rem;
    border: 2px solid var(--success-border);
    font-weight: 600;
    font-size: 1rem;
    box-shadow: var(--shadow-md);
    animation: pulse 2s infinite;
}}

@keyframes pulse {{
    0%, 100% {{ opacity: 1; }}
    50% {{ opacity: 0.8; }}
}}

.permission-warning {{
    background: var(--warning-bg);
    color: var(--warning-text);
    padding: 1.25rem;
    border-radius: 15px;
    margin: 1rem 0;
    border: 2px solid var(--warning-border);
    font-size: 0.95rem;
    line-height: 1.6;
    text-align: center;
    box-shadow: var(--shadow-md);
    position: relative;
}}

.permission-warning::before {{
    content: '⚠️';
    font-size: 1.5rem;
    display: block;
    margin-bottom: 0.5rem;
}}

/* --- Login Page --- */
.login-container {{
    max-width: 500px;
    margin: 3rem auto;
    padding: 3rem;
    background: var(--bg-card);
    backdrop-filter: blur(15px);
    border-radius: 25px;
    box-shadow: var(--shadow-xl);
    border: 1px solid var(--border-light);
    position: relative;
    overflow: hidden;
}}

.login-container::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 5px;
    background: var(--gradient-start);
}}

.login-header {{
    text-align: center;
    margin-bottom: 2.5rem;
    position: relative;
}}

.login-header h1 {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}

.login-header p {{
    font-size: 1.15rem;
    color: var(--text-secondary);
    font-weight: 500;
}}

/* --- Footer --- */
.footer {{
    text-align: center;
    padding: 2.5rem;
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    margin-top: 2rem;
    color: var(--text-secondary);
    border: 1px solid var(--border-light);
    box-shadow: var(--shadow-lg);
}}

.footer p {{
    margin: 0.75rem 0;
    font-size: 0.95rem;
    font-weight: 500;
}}

/* --- Enhanced User Experience --- */
.stButton button {{
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    transform-origin: center !important;
}}

.stButton button:hover {{
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(0,0,0,0.15) !important;
}}

.stButton button:active {{
    transform: translateY(0) !important;
    transition-duration: 0.1s !important;
}}

/* Smooth transitions for all interactive elements */
.stRadio, .stSelectbox, .stMultiselect, .stTextInput, .stNumberInput, .stTextArea {{
    transition: all 0.3s ease !important;
}}

/* Enhanced form elements */
.stTextInput input, .stNumberInput input, .stTextArea textarea {{
    border-radius: 12px !important;
    border: 2px solid #e5e7eb !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    transition: all 0.3s ease !important;
    background: white !important;
}}

.stTextInput input:focus, .stNumberInput input:focus, .stTextArea textarea:focus {{
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    outline: none !important;
}}

/* Enhanced select elements */
.stSelectbox select {{
    border-radius: 12px !important;
    border: 2px solid #e5e7eb !important;
    padding: 12px 16px !important;
    font-size: 16px !important;
    background: white !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
}}

.stSelectbox select:focus {{
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1) !important;
    outline: none !important;
}}

/* Enhanced dataframes */
.stDataFrame {{
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07) !important;
    border: 1px solid #e5e7eb !important;
    transition: all 0.3s ease !important;
}}

.stDataFrame:hover {{
    box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    transform: translateY(-2px) !important;
}}

/* Enhanced charts */
.stPlotlyChart {{
    border-radius: 16px !important;
    overflow: hidden !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07) !important;
    border: 1px solid #e5e7eb !important;
    transition: all 0.3s ease !important;
    background: white !important;
}}

.stPlotlyChart:hover {{
    box-shadow: 0 8px 25px rgba(0,0,0,0.1) !important;
    transform: translateY(-2px) !important;
}}

/* Loading states */
.stSpinner {{
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    padding: 2rem !important;
}}

.stSpinner > div {{
    border: 4px solid #f3f4f6 !important;
    border-top: 4px solid #2563eb !important;
    border-radius: 50% !important;
    width: 40px !important;
    height: 40px !important;
    animation: spin 1s linear infinite !important;
}}

@keyframes spin {{
    0% {{ transform: rotate(0deg); }}
    100% {{ transform: rotate(360deg); }}
}}

/* Enhanced alerts */
.stAlert {{
    border-radius: 12px !important;
    border-width: 2px !important;
    border-style: solid !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07) !important;
    padding: 1rem 1.25rem !important;
    margin: 1rem 0 !important;
    transition: all 0.3s ease !important;
}}

.stAlert:hover {{
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 12px rgba(0,0,0,0.1) !important;
}}

/* Enhanced metric containers */
[data-testid="metric-container"] {{
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    border: 2px solid #e5e7eb !important;
    border-radius: 16px !important;
    padding: 1.5rem 2rem !important;
    box-shadow: 0 4px 6px rgba(0,0,0,0.07) !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
    position: relative !important;
    overflow: hidden !important;
}}

[data-testid="metric-container"]::before {{
    content: '' !important;
    position: absolute !important;
    top: 0 !important;
    left: 0 !important;
    right: 0 !important;
    height: 3px !important;
    background: linear-gradient(90deg, #2563eb, #3b82f6, #60a5fa) !important;
    transition: all 0.3s ease !important;
}}

[data-testid="metric-container"]:hover {{
    transform: translateY(-4px) !important;
    box-shadow: 0 12px 25px rgba(0,0,0,0.15) !important;
}}

[data-testid="metric-container"]:hover::before {{
    height: 4px !important;
    box-shadow: 0 0 10px rgba(37, 99, 235, 0.3) !important;
}}

/* Enhanced sidebar */
[data-testid="stSidebar"] {{
    background: linear-gradient(180deg, #f8fafc 0%, #f1f5f9 100%) !important;
    border-right: 2px solid #e5e7eb !important;
    box-shadow: 2px 0 10px rgba(0,0,0,0.1) !important;
    backdrop-filter: blur(10px) !important;
}}

/* Enhanced main content area */
.main {{
    background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%) !important;
    min-height: 100vh !important;
}}

/* Responsive design improvements */
@media (max-width: 768px) {{
    .main-header h1 {{
        font-size: 1.8rem !important;
    }}

    .content-area {{
        padding: 1.5rem !important;
        margin-bottom: 1rem !important;
    }}

    [data-testid="metric-container"] {{
        padding: 1rem 1.5rem !important;
    }}

    .stDataFrame, .stPlotlyChart {{
        border-radius: 12px !important;
    }}
}}

/* Focus states for accessibility */
.stButton button:focus,
.stTextInput input:focus,
.stNumberInput input:focus,
.stTextArea textarea:focus,
.stSelectbox select:focus {{
    outline: 2px solid #2563eb !important;
    outline-offset: 2px !important;
}}

/* --- General Component Styling --- */

.stAlert {{
    border-radius: 12px !important;
    border-width: 2px !important;
    border-style: solid !important;
    box-shadow: var(--shadow-md) !important;
    padding: 1rem 1.25rem !important;
}}

[data-testid="metric-container"] {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border: 2px solid var(--border-light);
    border-radius: 20px;
    padding: 1.5rem 2rem;
    box-shadow: var(--shadow-lg);
    transition: var(--transition-normal);
    position: relative;
    overflow: hidden;
}}

[data-testid="metric-container"]::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-start);
}}

[data-testid="metric-container"]:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-xl);
}}

[data-testid="metric-container"] label {{
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 0.9rem;
}}

[data-testid="metric-container"] [data-testid="stMetricValue"] {{
    color: var(--text-primary);
    font-size: 2.1rem;
    font-weight: 800;
    margin: 0.5rem 0;
}}

[data-testid="metric-container"] [data-testid="stMetricDelta"] {{
    font-weight: 600;
    font-size: 0.9rem;
}}

/* --- Section Headers --- */
.section-header h2 {{
    color: var(--text-primary);
    font-size: 2rem;
    font-weight: 800;
    margin-bottom: 0.5rem;
    text-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}}

.section-header p {{
    color: var(--text-secondary);
    margin: 0;
    font-size: 1.1rem;
    font-weight: 500;
}}

/* --- Cards --- */
.section-card {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border: 2px solid var(--border-light);
    border-radius: 20px;
    padding: 2rem;
    box-shadow: var(--shadow-lg);
    margin-bottom: 2rem;
    transition: var(--transition-normal);
    position: relative;
    overflow: hidden;
}}

.section-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--gradient-end);
}}

.section-card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-xl);
}}

/* --- Grids --- */
.section-grid {{
    display: grid;
    gap: 2rem;
}}

.section-grid.three {{
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}}

.section-grid.two {{
    grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
}}

.metric-grid {{
    display: grid;
    gap: 1.5rem;
    grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
}}

.metric-card {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border: 2px solid var(--border-light);
    border-radius: 18px;
    padding: 1.75rem;
    box-shadow: var(--shadow-md);
    text-align: center;
    transition: var(--transition-normal);
    position: relative;
    overflow: hidden;
}}

.metric-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 3px;
    background: var(--gradient-start);
}}

.metric-card:hover {{
    transform: translateY(-3px);
    box-shadow: var(--shadow-lg);
}}

.metric-card .metric-icon {{
    font-size: 2.5rem;
    margin-bottom: 1rem;
    display: block;
}}

.metric-card .metric-value {{
    font-size: 2.2rem;
    font-weight: 800;
    color: var(--text-primary);
    margin: 0.5rem 0;
}}

.metric-card .metric-label {{
    color: var(--text-secondary);
    font-weight: 600;
    font-size: 1rem;
}}

.dashboard-card {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border: 2px solid var(--border-light);
    border-radius: 18px;
    padding: 2rem;
    box-shadow: var(--shadow-lg);
    transition: var(--transition-normal);
    position: relative;
    overflow: hidden;
    cursor: pointer;
}}

.dashboard-card::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: var(--gradient-end);
    transition: var(--transition-normal);
}}

.dashboard-card:hover {{
    transform: translateY(-5px);
    box-shadow: var(--shadow-xl);
}}

.dashboard-card:hover::before {{
    height: 6px;
}}

.dashboard-card .dashboard-icon {{
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
    display: block;
    transition: var(--transition-normal);
}}

.dashboard-card:hover .dashboard-icon {{
    transform: scale(1.1);
}}

.dashboard-card .dashboard-title {{
    font-weight: 700;
    font-size: 1.3rem;
    color: var(--text-primary);
    margin-bottom: 0.75rem;
}}

.dashboard-card .dashboard-description {{
    color: var(--text-secondary);
    font-size: 1rem;
    line-height: 1.5;
}}

.quick-actions {{
    background: var(--bg-card);
    backdrop-filter: blur(10px);
    border: 2px solid var(--border-light);
    border-radius: 18px;
    padding: 1.75rem;
    box-shadow: var(--shadow-lg);
    margin-top: 2rem;
    transition: var(--transition-normal);
}}

.quick-actions:hover {{
    transform: translateY(-2px);
    box-shadow: var(--shadow-xl);
}}

/* --- Fuel Station Specific Components --- */
/* Tank Components */
.tank-container {{
    position: relative;
    width: 100%;
    height: 200px;
    background: var(--tank-bg);
    border: 4px solid var(--fuel-primary);
    border-radius: 100px;
    overflow: hidden;
    box-shadow: var(--shadow-xl);
    margin: 20px 0;
    transition: var(--transition-normal);
}}

.tank-container:hover {{
    transform: scale(1.02);
    box-shadow: 0 15px 35px rgba(234, 88, 12, 0.3);
}}

.tank-container::before {{
    content: '';
    position: absolute;
    top: -18px;
    left: 50%;
    transform: translateX(-50%);
    width: 90px;
    height: 28px;
    background: linear-gradient(45deg, #9ca3af, #6b7280);
    border-radius: 50%;
    border: 3px solid #374151;
    z-index: 2;
}}

.tank-container::after {{
    content: '';
    position: absolute;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    width: 55px;
    height: 12px;
    background: #6b7280;
    border-radius: 6px;
    z-index: 2;
}}

.fuel-fill {{
    position: absolute;
    top: 0;
    left: 0;
    height: 100%;
    transition: width 1.2s cubic-bezier(0.4, 0, 0.2, 1);
    background: linear-gradient(90deg,
        rgba(239, 68, 68, 0.95) 0%,
        rgba(245, 101, 101, 0.95) 30%,
        rgba(34, 197, 94, 0.95) 70%,
        rgba(59, 130, 246, 0.95) 100%);
    box-shadow: inset 0 0 25px rgba(255,255,255,0.4);
}}

.fuel-fill::before {{
    content: '';
    position: absolute;
    top: 0;
    right: 0;
    width: 4px;
    height: 100%;
    background: linear-gradient(to bottom,
        rgba(255,255,255,0.9) 0%,
        rgba(255,255,255,0.5) 50%,
        rgba(255,255,255,0.9) 100%);
}}

/* Pump Components */
.pump-station {{
    background: var(--pump-bg);
    border: 4px solid var(--fuel-secondary);
    border-radius: 25px;
    padding: 30px;
    margin: 20px 0;
    box-shadow: var(--shadow-xl);
    position: relative;
    overflow: hidden;
    transition: var(--transition-normal);
}}

.pump-station::before {{
    content: '';
    position: absolute;
    top: -12px;
    right: -12px;
    width: 35px;
    height: 35px;
    background: var(--fuel-secondary);
    border-radius: 50%;
    box-shadow: 0 0 20px rgba(220, 38, 38, 0.8);
}}

.pump-station:hover {{
    transform: translateY(-3px);
    box-shadow: 0 20px 40px rgba(220, 38, 38, 0.3);
}}

.pump-station.active {{
    border-color: var(--success-text);
    box-shadow: 0 15px 35px rgba(34, 197, 94, 0.4);
}}

.pump-station.active::before {{
    background: var(--success-text);
    box-shadow: 0 0 20px rgba(34, 197, 94, 0.8);
    animation: pulse 1.5s infinite;
}}

.pump-title {{
    font-size: 1.8rem;
    font-weight: bold;
    color: #f9fafb;
    margin-bottom: 18px;
    text-shadow: 0 2px 4px rgba(0,0,0,0.5);
}}

.pump-info {{
    display: flex;
    justify-content: space-between;
    margin-bottom: 18px;
    color: #d1d5db;
    font-size: 1rem;
}}

/* Digital Meter */
.digital-meter {{
    background: linear-gradient(145deg, #0f0f0f, #1a1a1a);
    border: 4px solid #00ff00;
    border-radius: 18px;
    padding: 25px;
    text-align: center;
    box-shadow: 0 0 25px rgba(0, 255, 0, 0.6), inset 0 0 25px rgba(0, 255, 0, 0.1);
    position: relative;
    overflow: hidden;
    margin: 20px 0;
}}

.digital-meter::before {{
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
    background: linear-gradient(90deg, #ff0000, #ffff00, #00ff00);
    animation: shimmer 2s infinite;
}}

@keyframes shimmer {{
    0% {{ left: -100%; }}
    100% {{ left: 100%; }}
}}

.meter-display {{
    font-family: 'Courier New', monospace;
    font-size: 3.5rem;
    font-weight: bold;
    color: #00ff00;
    text-shadow: 0 0 15px rgba(0, 255, 0, 0.9);
    margin: 12px 0;
    letter-spacing: 3px;
    animation: glow 2s ease-in-out infinite alternate;
}}

@keyframes glow {{
    from {{ text-shadow: 0 0 15px rgba(0, 255, 0, 0.9); }}
    to {{ text-shadow: 0 0 25px rgba(0, 255, 0, 1), 0 0 35px rgba(0, 255, 0, 0.8); }}
}}

.meter-label {{
    font-size: 1rem;
    color: #cccccc;
    margin-bottom: 12px;
    font-weight: 500;
}}

/* Control Buttons */
.control-button {{
    background: linear-gradient(45deg, var(--fuel-secondary), #b91c1c);
    border: 3px solid #b91c1c;
    border-radius: 30px;
    padding: 14px 30px;
    font-size: 1.1rem;
    font-weight: bold;
    color: white;
    cursor: pointer;
    transition: var(--transition-normal);
    text-transform: uppercase;
    letter-spacing: 1px;
    box-shadow: 0 6px 18px rgba(220, 38, 38, 0.3);
    position: relative;
    overflow: hidden;
}}

.control-button::before {{
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
    transition: var(--transition-slow);
}}

.control-button:hover {{
    transform: translateY(-2px);
    box-shadow: 0 8px 22px rgba(220, 38, 38, 0.4);
}}

.control-button:hover::before {{
    left: 100%;
}}
"""

    return css
