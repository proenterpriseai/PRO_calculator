import streamlit as st

# 1. Page Configuration
st.set_page_config(
    page_title="Incar Pro Asset Management Lab",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. Google Analytics 4 (GA4)
st.markdown("""
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-NV114K1SQY"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-NV114K1SQY');
    </script>
""", unsafe_allow_html=True)

# 3. Global Styling (CSS)


st.markdown('<link rel="stylesheet" href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css" media="print" onload="this.media=\'all\'">', unsafe_allow_html=True)
st.markdown("""
    <style>
    /* Global Font & Background */
    html, body, .stApp { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; }
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stButton, .stTextInput, .stNumberInput, .stSelectbox { font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif !important; }
    /* Exclude Material Icons/Symbols from font override */
    [class^="material-"], [class*=" material-"], .material-icons { font-family: 'Material Icons' !important; }
    .stApp { background-color: #f8fafc; }

    /* Input field borders — 입력 영역 명확화 */
    .stNumberInput input, .stTextInput input, .stTextArea textarea {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        padding: 8px 12px !important;
        background: #ffffff !important;
    }
    .stNumberInput input:focus, .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.15) !important;
    }
    .stSelectbox > div > div {
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px !important;
        background: #ffffff !important;
    }
    
    /* Sidebar */
    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #27398c !important;
        border-right: 1px solid #1e3a8a;
    }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    [data-testid="stSidebar"] label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio div[role='radiogroup'] > label {
        color: white !important;
    }
    [data-testid="stSidebar"] .stRadio label p {
        color: white !important;
        font-weight: 500;
        font-size: 1.0rem !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        background-color: rgba(255,255,255,0.05) !important;
        color: white !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        padding: 0.5rem 0.75rem !important;
        margin-top: -5px !important;
        margin-bottom: -5px !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] p {
        color: #cbd5e1 !important;
        font-size: 0.85rem !important;
    }
    
    /* Reduce Sidebar Widget Spacing */
    [data-testid="stSidebar"] .stVerticalBlock {
        gap: 0.5rem !important;
    }
    [data-testid="stSidebar"] hr {
        margin: 0.5rem 0 !important;
    }
    
    /* Center Sidebar Content */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        text-align: center;
    }
    
    /* Radio Button: full width matching header */
    [data-testid="stSidebar"] .stRadio,
    [data-testid="stSidebar"] .stRadio:has([role="radiogroup"]) {
        width: 100% !important;
        max-width: 100% !important;
    }
    [data-testid="stSidebar"] .stElementContainer:has(.stRadio) {
        width: 100% !important;
        max-width: 100% !important;
    }
    [data-testid="stSidebar"] [role="radiogroup"] {
        width: 100% !important;
        display: flex;
        flex-direction: column;
        align-items: stretch;
    }
    [data-testid="stSidebar"] .stRadio label {
        width: 100% !important;
        justify-content: flex-start !important;
        text-align: left;
        box-sizing: border-box !important;
    }
    /* 사이드바 카테고리 카드 스타일 */
    [data-testid="stSidebar"] .stRadio label {
        background: rgba(255,255,255,0.06) !important;
        border-radius: 10px !important;
        padding: 8px 12px !important;
        margin-bottom: 3px !important;
        border-left: 3px solid transparent !important;
        transition: all 0.2s ease !important;
    }
    [data-testid="stSidebar"] .stRadio label:hover {
        background: rgba(255,255,255,0.12) !important;
        border-left-color: #60a5fa !important;
        transform: translateX(2px);
    }
    [data-testid="stSidebar"] .stRadio label[data-checked="true"],
    [data-testid="stSidebar"] .stRadio label:has(input:checked) {
        background: rgba(96,165,250,0.2) !important;
        border-left-color: #3b82f6 !important;
    }
    
    /* Button Centering */
    [data-testid="stSidebar"] .stButton button {
        width: 100%;
        margin: 0 auto;
        display: block;
        background-color: #3b82f6 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
        color: white !important;
        transition: all 0.2s ease;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: #2563eb !important;
        border-color: white !important;
        transform: translateY(-1px);
    }
    
    /* Alert/Tip Box in Sidebar */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        text-align: center;
        background-color: rgba(255,255,255,0.08) !important;
        color: #cbd5e1 !important;
        border-color: rgba(255,255,255,0.2) !important;
    }
    [data-testid="stSidebar"] [data-testid="stAlert"] p,
    [data-testid="stSidebar"] [data-testid="stAlert"] span {
        color: #cbd5e1 !important;
    }
    
    /* Toggle Centering */
    [data-testid="stSidebar"] .stCheckbox {
        display: flex;
        justify-content: center;
    }
    [data-testid="stSidebar"] .stCheckbox label {
        width: auto;
    }
    
    /* Label Centering */
    [data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p {
        width: 100%;
        text-align: center;
        display: block;
    }

    /* Headers */
    h1, h2, h3 { color: #1e3a8a; font-weight: 700; letter-spacing: -0.5px; }
    h1 { border-bottom: 3px solid #1e3a8a; padding-bottom: 15px; margin-bottom: 30px; font-size: 2.2rem; }
    h2 { font-size: 1.6rem; margin-top: 25px; margin-bottom: 15px; }
    h3 { font-size: 1.3rem; margin-top: 20px; color: #1e40af; }
    
    /* Metrics */
    .stMetric {
        background-color: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        border: 1px solid #e2e8f0;
        transition: all 0.2s ease;
        height: 100%; /* Ensure full height */
        min-height: 140px; /* Minimum height for consistency */
        display: flex;
        flex-direction: column;
        justify-content: flex-start; /* Unified top alignment for titles */
        gap: 4px;
        overflow: visible !important; /* Allow content to overflow if necessary */
    }
    .stMetric:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    [data-testid="stMetricValue"] { 
        font-size: 1.25rem !important; /* Smaller size to force single line */
        color: #1e3a8a; 
        font-weight: 800; 
        word-wrap: normal !important; 
        white-space: nowrap !important;   /* Force single line */
        overflow: hidden !important;   /* Prevent wrapping to new line */
        text-overflow: ellipsis !important; /* Ellipsis for overly long (though reduced font helps) */
        line-height: 1.2 !important;
    }
    [data-testid="stMetricValue"] > div {
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }
    [data-testid="stMetricLabel"] { 
        font-size: 0.92rem !important; 
        color: #64748b; 
        font-weight: 600;
        white-space: pre-line !important;  /* Support \n for explicit line breaks */
        line-height: 1.2 !important;
        min-height: 2.8rem;               /* Secure space for 2 lines to keep alignment */
        display: block !important;
        overflow: visible !important;
    }
    [data-testid="stMetricLabel"] > div {
        white-space: pre-line !important; /* Override Streamlit's internal nowrap */
        overflow: visible !important;
        text-overflow: unset !important;
        word-break: keep-all !important;
    }

    /* Expert Card (Custom Component Style) */
    .expert-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 20px;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
        margin-top: 10px;
    }
    .expert-title {
        color: #1e3a8a;
        font-size: 1.05rem; /* Reduced for single line */
        font-weight: 700;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        gap: 6px;
        white-space: nowrap; /* Prevent wrapping */
        overflow: hidden;
        text-overflow: ellipsis;
    }
    
    /* Step Box */
    .step-box {
        background-color: white;
        border-radius: 10px;
        padding: 15px 20px;
        margin-bottom: 12px;
        border-left: 5px solid #3b82f6;
        border-top: 1px solid #f1f5f9;
        border-right: 1px solid #f1f5f9;
        border-bottom: 1px solid #f1f5f9;
    }
    /* Fix overlap in steps by ensuring block formatting context */
    .step-box > div { display: block; width: 100%; }
    
    /* Metric Delta Truncation Fix */
    [data-testid="stMetricDelta"] > div {
        white-space: pre-wrap !important;
        overflow: visible !important;
        text-overflow: clip !important;
        word-break: keep-all !important;
        font-size: 0.82rem !important;
        line-height: 1.3 !important;
    }
    
    .step-title { color: #1e3a8a; font-weight: 700; font-size: 0.95rem; margin-bottom: 5px; line-height: 1.4; }
    .step-content { color: #475569; font-size: 0.9rem; line-height: 1.6; }
    .highlight { color: #2563eb; font-weight: 700; background-color: #eff6ff; padding: 2px 6px; border-radius: 4px; }
    
    /* Logic Annotation Box */
    .logic-annotation {
        background-color: #f1f5f9;
        border-left: 3px solid #64748b;
        padding: 10px 15px;
        margin-top: 8px;
        border-radius: 4px;
        font-size: 0.85rem;
        color: #475569;
        line-height: 1.5;
    }
    
    /* Tabs */
    .stTabs [data-baseline-toggle="true"] {
        font-weight: 600;
        color: #64748b;
    }
    .stTabs [aria-selected="true"] {
        color: #1e3a8a !important;
        border-bottom-color: #1e3a8a !important;
        font-weight: 800 !important;
    }
    
    /* Buttons */
    .stButton button {
        background-color: #1e3a8a;
        color: white;
        font-weight: 600;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        border: none;
        transition: background-color 0.2s;
    }
    .stButton button:hover {
        background-color: #1e40af;
    }
    
    /* Expander Fix - More specific targeting */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #475569;
        background-color: #f8fafc;
        border-radius: 8px;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
        margin-bottom: 10px !important; /* Push content down */
    }
    
    [data-testid="stExpander"] details > summary {
        padding-left: 20px !important;
        position: relative !important;
    }
    [data-testid="stExpander"] details > summary > svg {
        position: absolute !important;
        left: 0 !important;
        top: 50% !important;
        transform: translateY(-50%) !important;
        margin-left: 0 !important;
    }
    
    /* Ensure content inside expander has breathing room */
    div[data-testid="stExpander"] > div[role="group"] {
        padding-top: 15px !important;
    }
    
    /* Presentation Mode Toggle Label & Icon Color - Robust Selector */
    div[data-testid="stSidebar"] label[data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stCheckbox"] label p,
    [data-testid="stSidebar"] .stSwitch label p {
        color: white !important;
        font-weight: 600 !important;
    }
    
    /* Force Sidebar Widget Icons (Help, SVGs) to White */
    [data-testid="stSidebar"] svg {
        fill: white !important;
    }
    [data-testid="stSidebar"] [data-testid="stHelpIcon"] {
        color: white !important;
    }
    
    /* === Mobile Responsive === */
    @media (max-width: 768px) {
        .main .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            padding-top: 1rem !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            min-width: 100% !important;
        }
        .expert-card {
            padding: 12px !important;
        }
        h1 { font-size: 1.4rem !important; padding-bottom: 8px !important; margin-bottom: 16px !important; }
        h2 { font-size: 1.15rem !important; }
        h3 { font-size: 1.05rem !important; }
        /* Metric cards: reduce min-height on mobile, prevent overflow */
        .stMetric { min-height: 80px !important; padding: 10px 8px !important; }
        [data-testid="stMetricValue"] { font-size: 0.95rem !important; word-break: break-all !important; }
        [data-testid="stMetricLabel"] { font-size: 0.75rem !important; line-height: 1.2 !important; }
        [data-testid="stMetricDelta"] { font-size: 0.7rem !important; }
        /* Force 2-col max on mobile for metric rows */
        [data-testid="column"]:nth-child(n+3) { margin-top: 8px !important; }
        /* Expander: full width, no overflow */
        .stExpander { overflow-x: hidden !important; }
        .stExpander [data-testid="stExpanderDetails"] { padding: 8px !important; }
        /* Number inputs: larger touch targets */
        input[type="number"] { font-size: 1rem !important; }
        /* Sidebar radio: bigger tap area */
        [data-testid="stSidebar"] .stRadio label p { font-size: 1rem !important; }
        /* Tabs: allow horizontal scroll */
        [data-testid="stTabs"] { overflow-x: auto !important; }
        /* Plotly charts: touch-friendly */
        .js-plotly-plot .plotly { touch-action: pan-x pan-y !important; }
    }
    
    /* === Print Styles === */
    @media print {
        [data-testid="stSidebar"] { display: none !important; }
        [data-testid="stHeader"] { display: none !important; }
        .stDeployButton { display: none !important; }
        button { display: none !important; }
        .stSlider, .stTextInput, .stSelectbox, .stCheckbox, .stRadio, .stNumberInput { display: none !important; }
        .stExpander [data-testid="stExpanderDetails"] { display: block !important; }
        .main .block-container { padding: 0 !important; max-width: 100% !important; }
        .expert-card { break-inside: avoid; page-break-inside: avoid; }
        .step-box { break-inside: avoid; }
        h1, h2, h3 { page-break-after: avoid; }
    }

    /* === Dark Mode Support === */
    @media (prefers-color-scheme: dark) {
        .expert-card {
            background: #1e293b !important;
            border-color: #334155 !important;
        }
        .step-box {
            background: #0f172a !important;
            border-color: #334155 !important;
        }
        .step-title {
            color: #93c5fd !important;
        }
        .step-content {
            color: #e2e8f0 !important;
        }
        .logic-annotation {
            background: #1e293b !important;
            color: #cbd5e1 !important;
        }
    }

    /* Streamlit Cloud "Manage app" 버튼 및 footer 숨김 */
    .stDeployButton,
    [data-testid="manage-app-button"],
    [data-testid="stStatusWidget"],
    div[class*="stAppDeployButton"],
    div[class*="StatusWidget"],
    div[class*="profileContainer"],
    div[class*="viewerBadge"],
    .viewerBadge_container__r5tak,
    .stBottom > div,
    #stDecoration,
    section[data-testid="stSidebarUserContent"] ~ div,
    footer,
    header[data-testid="stHeader"] button[kind="header"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        position: fixed !important;
        bottom: -100px !important;
    }

    /* ============================================ */
    /* === Card-Based Input UI Styles ===          */
    /* ============================================ */
    
    /* Card header label */
    .input-card-header {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 0.95rem;
        font-weight: 700;
        color: #1e3a8a;
        margin-bottom: 2px;
        margin-top: 16px;
        padding-left: 4px;
        letter-spacing: -0.3px;
    }
    .input-card-header:first-child {
        margin-top: 0;
    }
    
    /* Override st.container(border=True) for card style */
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"] {
        background: white !important;
        border: 1px solid #e2e8f0 !important;
        border-left: 4px solid #3b82f6 !important;
        border-radius: 12px !important;
        padding: 4px 8px !important;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 1px 2px rgba(0,0,0,0.03) !important;
        transition: box-shadow 0.25s ease, border-color 0.25s ease !important;
        margin-bottom: 12px !important;
    }
    div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: 0 4px 12px rgba(30,58,138,0.08), 0 2px 4px rgba(0,0,0,0.04) !important;
        border-color: #cbd5e1 !important;
        border-left-color: #1e3a8a !important;
    }
    
    /* === Input Widget Polish (최소한) === */

    /* Labels: Better typography */
    label[data-testid="stWidgetLabel"] p {
        font-weight: 600 !important;
        color: #334155 !important;
        font-size: 0.88rem !important;
    }
    
    </style>
    """, unsafe_allow_html=True)

# ============================================================
# Module Imports (core utilities + tab renderers)
# ============================================================
from core import init_session_state
init_session_state()  # 매 rerun마다 실행 (모듈 캐싱과 무관하게)

# ============================================================
# Sidebar
# ============================================================
# 4. Sidebar Profile
with st.sidebar:
    st.markdown("""
        <div style='padding:10px 14px; background:#27398c; border-radius:8px; border:1px solid rgba(255,255,255,0.3); margin-bottom:22px; margin-top:-60px;'>
            <h3 style='color:white; margin:0; font-size:1.1rem; border-bottom:1px solid rgba(255,255,255,0.15); padding-bottom:6px; margin-bottom:6px;'>🧮 PRO Calculator</h3>
            <p style='font-size:0.9rem; color:#e2e8f0; margin:0;'><b style='color:white; font-size:0.95rem;'>AI 실시간 시뮬레이션</b></p>
            <p style='font-size:0.78rem; color:#cbd5e1; margin-top:3px;'>프리미엄 자산관리 솔루션</p>
        </div>
    """, unsafe_allow_html=True)
    
    _MENU_ICONS = {
        "부동산 통합": "🏠", "상속 및 증여세": "🎁", "예적금 계산기": "💰",
        "은퇴자금 설계": "🏖️", "목적자금 설계": "🎯", "달러 설계": "💵",
        "전월세 전환 설계": "🏘️", "대출 상환 설계": "🏦", "종합소득세 계산": "📊",
    }
    _menu_items = list(_MENU_ICONS.keys())

    st.markdown("""
        <div style='background: linear-gradient(135deg, #f59e0b, #d97706); border-radius:10px; padding:9px 16px; margin-bottom:10px; box-shadow: 0 4px 12px rgba(245,158,11,0.3); position:relative; overflow:hidden;'>
            <div style='position:absolute; top:-8px; right:-8px; width:40px; height:40px; background:rgba(255,255,255,0.15); border-radius:50%;'></div>
            <span style='color:#fff; font-size:0.88rem; font-weight:800; letter-spacing:0.5px; text-shadow:0 1px 2px rgba(0,0,0,0.2);'>⚡ 금융 솔루션 카테고리</span>
        </div>
    """, unsafe_allow_html=True)
    st.radio(
        "금융 솔루션 카테고리",
        _menu_items,
        format_func=lambda x: f"{_MENU_ICONS.get(x, '')}  {x}",
        key="main_menu",
        label_visibility="collapsed"
    )

    main_menu = st.session_state.get("main_menu", "부동산 통합")

    # ---------------------------------------------------------
    # Bottom Utility Section
    st.markdown("<div style='height: 30px'></div>", unsafe_allow_html=True)

    st.info("💡 **Tip**: 각 시뮬레이터는 최신 세법 및 금융 공학 모델을 기반으로 정밀하게 설계되었습니다.")

    st.markdown("---")
    st.session_state.presentation_mode = st.toggle("🖥️ 프레젠테이션 모드", value=st.session_state.get("presentation_mode", False), help="고객 상담 시 입력창을 숨기고 결과 중심으로 화면을 구성합니다.")

    st.markdown("---")
    st.markdown("""
        <div style='font-size:0.72rem; color:#94a3b8; line-height:1.5;'>
            📋 <b style='color:#64748b;'>개인정보 · 면책 고지</b><br>
            본 데이터는 상담용으로만 활용됩니다.<br><br>
            본 시뮬레이션 결과는 참고용이며, 실제 세금·투자 결과와 다를 수 있습니다. 정확한 판단은 전문가 상담을 권장합니다.
        </div>
    """, unsafe_allow_html=True)


# ============================================================
# Main Routing
# ============================================================
# 메뉴 전환 시 스크롤 맨 위로 이동
_prev_menu = st.session_state.get('_prev_main_menu', None)
if _prev_menu != main_menu:
    st.session_state['_prev_main_menu'] = main_menu
    import streamlit.components.v1 as components
    components.html("""
    <script>
        var mainContent = window.parent.document.querySelector('section.main');
        if (mainContent) { mainContent.scrollTo(0, 0); }
    </script>
    """, height=0)

# 6. Main Routing (Lazy Import — 선택된 탭 모듈만 import하여 초기 로딩 최적화)
if "부동산" in main_menu:
    from tabs.real_estate import render_real_estate
    render_real_estate()
elif "상속" in main_menu:
    from tabs.inheritance import render_inheritance
    render_inheritance()
elif "예적금" in main_menu:
    from tabs.savings import render_savings
    render_savings()
elif "은퇴" in main_menu:
    from tabs.retirement import render_retirement
    render_retirement()
elif "목적" in main_menu:
    from tabs.target_fund import render_target_fund
    render_target_fund()
elif "달러" in main_menu:
    from tabs.dollar import render_dollar_insurance
    render_dollar_insurance()
elif "전월세" in main_menu:
    from tabs.jeonwolse import render_jeonwolse
    render_jeonwolse()
elif "대출" in main_menu:
    from tabs.loan import render_loan_planner
    render_loan_planner()
elif "종합소득세" in main_menu:
    from tabs.income_tax import render_income_tax
    render_income_tax()
else:
    st.info("메뉴를 선택해 주세요.")

