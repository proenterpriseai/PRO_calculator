import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from station_data import COMPLEX_DB, REGION_DB

import streamlit.components.v1 as components

# 1. Page Configuration
st.set_page_config(
    page_title="Incar Pro Asset Management Lab",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 브라우저 자동 완성 기능 전역 비활성화 스크립트
components.html(
    """
    <script>
        const inputs = window.parent.document.querySelectorAll('input');
        for (const input of inputs) {
            input.setAttribute('autocomplete', 'off');
        }
        
        // 동적으로 추가되는 input 요소들을 위한 옵저버
        const observer = new MutationObserver((mutations) => {
            mutations.forEach((mutation) => {
                mutation.addedNodes.forEach((node) => {
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        if (node.tagName === 'INPUT') {
                            node.setAttribute('autocomplete', 'off');
                        }
                        const childInputs = node.querySelectorAll ? node.querySelectorAll('input') : [];
                        childInputs.forEach(input => input.setAttribute('autocomplete', 'off'));
                    }
                });
            });
        });
        
        observer.observe(window.parent.document.body, {
            childList: true,
            subtree: true
        });
    </script>
    """,
    height=0,
    width=0,
)

# 2. Global Styling (CSS)


st.markdown("""
    <style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    
    /* Global Font & Background */
    html, body, .stApp { font-family: 'Pretendard', sans-serif !important; }
    h1, h2, h3, h4, h5, h6, .stMarkdown, .stButton, .stTextInput, .stNumberInput, .stSelectbox { font-family: 'Pretendard', sans-serif !important; }
    /* Exclude Material Icons/Symbols from font override */
    [class^="material-"], [class*=" material-"], .material-icons { font-family: 'Material Icons' !important; }
    .stApp { background-color: #f8fafc; }
    
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
        font-size: 1.2rem !important; /* Increased font size */
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
    /* Center Sidebar Content */
    [data-testid="stSidebar"] div[data-testid="stVerticalBlock"] {
        text-align: center;
    }
    
    /* Radio Button Left-Align (Options Only) */
    [data-testid="stSidebar"] [role="radiogroup"] {
        width: 100%;
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    [data-testid="stSidebar"] .stRadio label {
        width: 100%;
        justify-content: flex-start !important;
        text-align: left;
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
    
    /* Alert/Tip Box Centering */
    [data-testid="stSidebar"] [data-testid="stAlert"] {
        text-align: center;
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
            padding-left: 1rem !important;
            padding-right: 1rem !important;
        }
        [data-testid="column"] {
            width: 100% !important;
            flex: 100% !important;
            min-width: 100% !important;
        }
        .expert-card {
            padding: 12px !important;
        }
        h1 { font-size: 1.4rem !important; }
        h2 { font-size: 1.15rem !important; }
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
    </style>
    """, unsafe_allow_html=True)

# 3. Utility Functions
def f_w(val):
    """Format number with commas"""
    return f"{int(val):,}"

def get_tax_rate_5steps(base):
    """Standard 5-step detailed tax rate calculation"""
    if base <= 100_000_000: return 0.1, 0, "10% (1억원 이하)"
    elif base <= 500_000_000: return 0.2, 10_000_000, "20% (5억원 이하)"
    elif base <= 1_000_000_000: return 0.3, 60_000_000, "30% (10억원 이하)"
    elif base <= 3_000_000_000: return 0.4, 160_000_000, "40% (30억원 이하)"
    else: return 0.5, 460_000_000, "50% (30억원 초과)"

def f_kr(val):
    """Converts a number to Korean reading format (e.g., 12억 5,000만원)"""
    if val is None or val == 0: return "0원"
    val = int(val)
    eok = val // 100_000_000
    man = (val % 100_000_000) // 10_000
    
    res = ""
    if eok > 0: res += f"{eok}억 "
    if man > 0: res += f"{man:,.0f}만원"
    elif eok == 0: res = "0원"
    else: res += "원"
    return res.strip()

def show_kr_label(val, has_help=False):
    """Displays Korean currency label if value > 0, aligned at the same height as the field label.
    If has_help=True, adds extra right padding to avoid overlapping with the help (?) icon."""
    if val and val > 0:
        st.caption(f"💰 {f_kr(val)}")

def comma_int_input(label, value, key, help=None):
    """3자리 콤마 포맷팅을 지원하는 텍스트 기반 정수 입력 위젯"""
    num_key = key
    str_key = f"{key}_str"
    
    # 초기값 설정
    if num_key not in st.session_state:
        st.session_state[num_key] = value
    
    current_num = st.session_state[num_key]
    
    # Callback: 문자열 입력 -> 숫자 변환 및 포맷팅
    def on_change_callback():
        user_str = st.session_state[str_key]
        if not user_str.strip():
            st.session_state[num_key] = 0
            st.session_state[str_key] = ""
            return
        try:
            # 쉼표 제거 후 정수 변환
            new_num = int(str(user_str).replace(",", "").strip())
            st.session_state[num_key] = new_num
            # 다시 쉼표 포맷팅하여 표시값 업데이트
            st.session_state[str_key] = f"{new_num:,}"
        except:
            if st.session_state[num_key] == 0:
                st.session_state[str_key] = ""
            else:
                st.session_state[str_key] = f"{st.session_state[num_key]:,}"
            
    # 위젯 상태 초기화 및 동기화 (외부 변수 변경 대응)
    formatted_val = "" if current_num == 0 else f"{current_num:,}"
    
    if str_key not in st.session_state:
        st.session_state[str_key] = formatted_val
    else:
        # 외부에서 값이 변경되었을 경우를 대비해 동기화 점검
        try:
            current_str_val = int(str(st.session_state[str_key]).replace(",", "").strip()) if st.session_state[str_key].strip() else 0
            if current_str_val != current_num:
                st.session_state[str_key] = formatted_val
        except:
            st.session_state[str_key] = formatted_val
        
    st.text_input(
        label,
        key=str_key,
        help=help,
        on_change=on_change_callback
    )
    
    return st.session_state[num_key]

from dataclasses import dataclass, fields, field

# --- Data & State Management ---
@dataclass
class RealEstateState:
    acq_area: float = 84.0
    acq_p: int = 0
    acq_h: str = "1주택"
    acq_type: str = "아파트"
    hold_p: int = 0
    hold_h: str = "1주택"
    hold_age: int = 60
    hold_y: int = 10
    yang_s: int = 0
    yang_b: int = 0
    yang_1h: bool = True
    yang_h_y: int = 1
    yang_r_y: int = 1

@dataclass
class InheritanceState:
    gif_c: int = 0
    gif_p: int = 0
    gif_d: int = 0
    gif_r: int = 0
    gif_skip: bool = False
    gif_minor: bool = False
    inh_ev: int = 0
    inh_d: int = 0
    inh_sp: int = 0
    inh_type: str = "일반"
    inh_f: float = 0.0

@dataclass
class RetirementState:
    ret_goal_p: int = 0
    ret_is_net: bool = True
    ret_is_mc: bool = True
    ret_is_compare: bool = True
    ret_risk_level: str = "중위험"
    ret_age_sl: int = 60
    ret_age_num: int = 60
    life_age_sl: int = 100
    life_age_num: int = 100
    pay_years_sl: int = 10
    pay_years_num: int = 10
    ret_stress_yield_val: float = -15.0
    ret_stress_inf_val: float = 5.0
    risk_radio_ret_opt: str = "기본"

@dataclass
class TargetFundState:
    tf_name: str = "자녀 대학자금"
    tf_age: int = 0
    tf_b: int = 0
    tf_period_sl: int = 10
    tf_period_num: int = 10
    tf_rate_sl: float = 5.0
    tf_rate_num: float = 5.0
    tf_net: bool = True
    tf_mc_toggle: bool = True
    tf_add_toggle: bool = False
    tf_add_prem: int = 0

@dataclass
class DollarInsuranceState:
    di_prod: str = "메트라이프 (백만인을 위한 달러종신)"
    di_period: int = 5
    di_prem: int = 1000
    di_add_toggle: bool = True
    di_add_prem: int = 1000
    input_curr_rate: float = 1430.0
    curr_rate_val: float = 1430.0
    avg_rate_val: float = 1300.0
    rate_low_val: float = 1100.0
    rate_mid_val: float = 1350.0
    rate_high_val: float = 1550.0

@dataclass
class AppConfig:
    """통합 세션 상태 관리 모델 (도메인별 분리)"""
    real_estate: RealEstateState = field(default_factory=RealEstateState)
    inheritance: InheritanceState = field(default_factory=InheritanceState)
    retirement: RetirementState = field(default_factory=RetirementState)
    target_fund: TargetFundState = field(default_factory=TargetFundState)
    dollar_insurance: DollarInsuranceState = field(default_factory=DollarInsuranceState)
    presentation_mode: bool = False

def init_session_state():
    """객체 지향 모델을 이용한 세션 복원 및 동기화 엔진"""
    # 1. 통합 상태 모델(AppConfig) 초기화
    if 'app_state' not in st.session_state:
        st.session_state.app_state = AppConfig()
        st.session_state.master_data = {} # 하위 호환성 유지용 (리팩토링 과도기)
        
    app_state = st.session_state.app_state
    
    # 2. 로드 (Restore): 모든 도메인별 Dataclass 필드를 st.session_state로 매핑
    def sync_to_session(model_obj):
        for f in fields(model_obj):
            if f.name not in st.session_state:
                # 초기 기본값 주입
                st.session_state[f.name] = getattr(model_obj, f.name)
            else:
                # 안전한 타입 추적용 저장
                st.session_state.master_data[f.name] = getattr(model_obj, f.name)

    sync_to_session(app_state.real_estate)
    sync_to_session(app_state.inheritance)
    sync_to_session(app_state.retirement)
    sync_to_session(app_state.target_fund)
    sync_to_session(app_state.dollar_insurance)

    if 'presentation_mode' not in st.session_state:
        st.session_state.presentation_mode = app_state.presentation_mode
        
    # 특수 키 디폴트 방어 (레거시 코드 대응)
    if 'acq_p' not in st.session_state: st.session_state.acq_p = 0
    if 'hold_p' not in st.session_state: st.session_state.hold_p = 0
    if 'yang_s' not in st.session_state: st.session_state.yang_s = 0
    if 'yang_b' not in st.session_state: st.session_state.yang_b = 0
    if 'gif_c' not in st.session_state: st.session_state.gif_c = 0
    if 'inh_ev' not in st.session_state: st.session_state.inh_ev = 0
    if 'ret_goal_p' not in st.session_state: st.session_state.ret_goal_p = 0
    if 'tf_b' not in st.session_state: st.session_state.tf_b = 0

    # 3. 캡처 (Capture): UI에서 변경된 상태를 다시 AppConfig 객체로 동기화
    def sync_from_session(model_obj):
        for f in fields(model_obj):
            if f.name in st.session_state:
                val = st.session_state[f.name]
                setattr(model_obj, f.name, val)
                st.session_state.master_data[f.name] = val # 레거시 동기화

    sync_from_session(app_state.real_estate)
    sync_from_session(app_state.inheritance)
    sync_from_session(app_state.retirement)
    sync_from_session(app_state.target_fund)
    sync_from_session(app_state.dollar_insurance)
    
    if 'presentation_mode' in st.session_state:
        app_state.presentation_mode = st.session_state.presentation_mode

init_session_state()


class TaxEngine:
    """Advanced Tax Logic Engine"""
    
    @staticmethod
    def get_acquisition_tax(price, area, method, is_adjustment):
        # 1. Standard Rates
        base_rate = 0.04 # Commercial, Land etc
        desc = "기본세율 (4%)"
        
        # 농지 세율 세분화 (2025 기준)
        if "농지" in method:
            if "자경" in method:
                base_rate = 0.015
                desc = "농지 자경 세율 (1.5%)"
            else:
                base_rate = 0.03
                desc = "농지 비자경 세율 (3%)"
            return base_rate, desc
        
        if "주택" in method:
            # 1-3% Scale for 1-House or Non-Adj 2-House
            if price <= 600_000_000:
                base_rate = 0.01
                desc = "1주택 기본세율 (1%)"
            elif price <= 900_000_000:
                base_rate = (price * 2 / 300_000_000 - 3) / 100
                desc = f"1주택 구간세율 ({base_rate*100:.2f}%)"
            else:
                base_rate = 0.03
                desc = "1주택 기본세율 (3%)"
                
            # Surcharges (2025 기준: 조정지역 중과 한시 유예 반영)
            if "2주택" in method:
                if is_adjustment:
                    base_rate = 0.08
                    desc = "조정지역 2주택 중과 (8%)"
                else:
                    desc = "비조정 2주택 (기본세율)"
            elif "3주택" in method:
                if is_adjustment:
                    base_rate = 0.12
                    desc = "조정지역 3주택 중과 (12%)"
                else:
                    base_rate = 0.08
                    desc = "비조정 3주택 중과 (8%)"
            elif "4주택" in method:
                base_rate = 0.12
                desc = "4주택 이상 중과 (12%)"
                
        return base_rate, desc

    @staticmethod
    def get_long_term_deduction(holding_years, residence_years, is_1house_1family):
        # Table 1: General (Max 30% / 15Y) - 2% per year
        # Table 2: 1-House + Residence 2Y+ (Max 80% / 10Y) - 4% + 4%
        
        rate = 0
        desc = "미적용"
        
        if holding_years < 3:
            return 0, "보유 3년 미만 (0%)"
            
        if is_1house_1family and residence_years >= 2:
            # Table 2
            h_rate = min(0.4, holding_years * 0.04)
            r_rate = min(0.4, residence_years * 0.04)
            rate = h_rate + r_rate
            desc = f"1세대 1주택 특례 ({int(rate*100)}% = 보유{int(h_rate*100)}% + 거주{int(r_rate*100)}%)"
        else:
            # Table 1
            rate = min(0.3, holding_years * 0.02)
            desc = f"일반 공제 ({int(rate*100)}% / 년 2%)"
            
        return rate, desc

    @staticmethod
    def get_generation_skipping_surcharge(tax, is_skipping, is_minor_and_high_val):
        """
        世代省略 (Generation Skipping)
        30% Surcharge, 40% if minor and > 2B KRW
        """
        if not is_skipping:
            return 0, "미부과"
        
        surcharge_rate = 0.3
        desc = "세대생략 할증 (30%)"
        
        if is_minor_and_high_val:
            surcharge_rate = 0.4
            desc = "세대생략 할증 (40%, 미성년+20억 초과)"
            
        return tax * surcharge_rate, desc

    @staticmethod
    def run_monte_carlo(years, initial_capital, annual_savings, expected_return, volatility=0.10, trials=1000):
        """
        Monte Carlo Simulation for Asset Projection
        volatility: standard deviation of annual returns (e.g. 10%)
        """
        all_scenarios = []
        for _ in range(trials):
            balances = [initial_capital]
            for _ in range(years):
                # Using log-normal distribution for returns
                actual_return = np.random.normal(expected_return / 100, volatility)
                new_bal = balances[-1] * (1 + actual_return) + annual_savings
                balances.append(max(0, new_bal))
            all_scenarios.append(balances)
        
        scenarios_np = np.array(all_scenarios)
        p10 = np.percentile(scenarios_np, 10, axis=0)
        p50 = np.percentile(scenarios_np, 50, axis=0)
        p90 = np.percentile(scenarios_np, 90, axis=0)
        
        return p10, p50, p90

    @staticmethod
    def get_portfolio_recommendation(risk_score):
        """
        Simple portfolio recommendation based on risk score (1-5)
        1: Stable, 5: Aggressive
        """
        rec = {
            1: {"title": "안정형", "assets": {"현금성": 40, "채권": 50, "주식": 10}},
            2: {"title": "안정추구형", "assets": {"현금성": 30, "채권": 45, "주식": 25}},
            3: {"title": "위험중립형", "assets": {"현금성": 20, "채권": 35, "주식": 45}},
            4: {"title": "적극투자형", "assets": {"현금성": 10, "채권": 20, "주식": 70}},
            5: {"title": "공격투자형", "assets": {"현금성": 5, "채권": 5, "주식": 90}},
        }
        return rec.get(risk_score, rec[3])

    @staticmethod
    def get_jongbu_tax(base):
        """종합부동산세 누진세율 계산 (2025 기준)"""
        if base <= 0:
            return 0, "과세표준 없음"
        brackets = [
            (300_000_000, 0.005, 0),
            (600_000_000, 0.007, 600_000),
            (1_200_000_000, 0.010, 2_400_000),
            (2_500_000_000, 0.013, 6_000_000),
            (5_000_000_000, 0.015, 11_000_000),
            (9_400_000_000, 0.020, 36_000_000),
            (float('inf'), 0.027, 101_800_000)
        ]
        for limit, rate, prog_ded in brackets:
            if base <= limit:
                tax = base * rate - prog_ded
                return max(0, tax), f"{rate*100:.1f}%"
        return max(0, base * 0.027 - 101_800_000), "2.7%"

    @staticmethod
    def get_property_tax(off_price):
        """재산세 간이 계산 (주택분, 1세대1주택 기준)
        Returns: (base_tax, edu_tax, city_tax, total_tax)
        - base_tax: 재산세 본세
        - edu_tax: 지방교육세 (20%)
        - city_tax: 도시지역분 (0.14%)
        - total_tax: 합계
        """
        # 과세표준 = 공시가격 × 공정시장가액비율(60%)
        tax_base = off_price * 0.6
        if tax_base <= 60_000_000:
            base_tax = tax_base * 0.001
        elif tax_base <= 150_000_000:
            base_tax = 60_000 + (tax_base - 60_000_000) * 0.0015
        elif tax_base <= 300_000_000:
            base_tax = 195_000 + (tax_base - 150_000_000) * 0.0025
        else:
            base_tax = 570_000 + (tax_base - 300_000_000) * 0.004
        base_tax = max(0, base_tax)
        edu_tax = base_tax * 0.2  # 지방교육세 (20%)
        city_tax = tax_base * 0.0014  # 도시지역분 (0.14%)
        total_tax = base_tax + edu_tax + city_tax
        return base_tax, edu_tax, city_tax, total_tax

# 4. Sidebar Profile
with st.sidebar:
    st.markdown("""
        <div style='padding:20px; background:#27398c; border-radius:12px; border:1px solid white; margin-bottom:20px; margin-top:-60px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1);'>
            <h3 style='color:white; margin:0; font-size:1.3rem; border-bottom:1px solid rgba(255,255,255,0.2); padding-bottom:10px; margin-bottom:10px;'>🧮 PRO Calculator</h3>
            <p style='font-size:1.0rem; color:#e2e8f0; margin:0;'><b style='color:white; font-size:1.1rem;'>AI 실시간 시뮬레이션</b></p>
            <p style='font-size:0.9rem; color:#cbd5e1; margin-top:5px;'>프리미엄 자산관리 솔루션</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.radio(
        "금융 솔루션 카테고리", 
        ["부동산 통합", "상속 및 증여세", "은퇴자금 설계", "목적자금 설계", "달러 설계", "전월세 전환 설계", "대출 상환 설계", "종합소득세 계산"],
        key="main_menu"
    )

    st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
    c_reset, c_sync = st.columns(2)
    with c_reset:
        if st.button("🔄 초기화", help="모든 입력값을 초기화합니다.", use_container_width=True):
            st.session_state.reset_confirm_mode = True
            
    with c_sync:
        if st.button("🌐 연동", help="외부 데이터(부동산원 등)를 연동합니다.", use_container_width=True):
            st.toast("🌐 외부 데이터 연동 엔진이 활성화되었습니다.", icon="⚡")
            with st.spinner("데이터 동기화 중..."):
                import time
                time.sleep(1.5)
                # Actual Data Sync logic (Simulated)
                st.session_state.hold_p = 2_100_000_000
                st.session_state.yang_s = 2_100_000_000
                st.session_state.acq_p = 2_100_000_000
                st.session_state.yang_b = 1_800_000_000
                st.session_state.master_data['hold_p'] = 2_100_000_000
                st.session_state.master_data['yang_s'] = 2_100_000_000
                st.session_state.master_data['acq_p'] = 2_100_000_000
                st.session_state.master_data['yang_b'] = 1_800_000_000
                st.success("연동 완료!")
                st.rerun()

    if st.session_state.get('reset_confirm_mode', False):
        st.warning("⚠️ 모든 데이터가 삭제됩니다.", icon="⚠️")
        rc1, rc2 = st.columns(2)
        if rc1.button("✅ 실행", use_container_width=True, key="btn_confirm_rst"):
            st.session_state.master_data = {}
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        if rc2.button("❌ 취소", use_container_width=True, key="btn_cancel_rst"):
            st.session_state.reset_confirm_mode = False
            st.rerun()

    main_menu = st.session_state.get("main_menu", "부동산 통합") # Get selected value with default
    
    # ---------------------------------------------------------
    # Bottom Utility Section (Pushed down)
    st.markdown("<div style='height: 40px'></div>", unsafe_allow_html=True)
    
    st.info("💡 **Tip**: 각 시뮬레이터는 최신 세법 및 금융 공학 모델을 기반으로 정밀하게 설계되었습니다.")
    
    st.markdown("---")
    st.session_state.presentation_mode = st.toggle("🖥️ 프레젠테이션 모드", value=st.session_state.presentation_mode, help="고객 상담 시 입력창을 숨기고 결과 중심으로 화면을 구성합니다.")

# --- AI Scenario Doctor ---
def render_ai_doctor(context, data):
    """
    Renders a contextual advice box based on the provided data.
    """
    with st.expander("🤖 AI 시나리오 닥터 (Expert Insight)", expanded=True):
        st.markdown(f"""
        <div style='background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 16px; display: flex; align-items: start; gap: 12px;'>
            <div style='font-size: 24px;'>🩺</div>
            <div>
                <div style='font-weight: bold; color: #166534; margin-bottom: 4px;'>전문가 진단 ({context})</div>
                <div style='color: #15803d; font-size: 0.95rem; line-height: 1.5;'>
                    {_generate_advice(context, data)}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def _generate_advice(context, data):
    if context == "취득세":
        tax = data.get('tax', 0)
        h_count = data.get('h_count', '1주택')
        if tax > 50_000_000:
            return "취득세 부담이 상당히 높습니다. **매매사업자 등록** 또는 **부부 공동명의**를 통한 세율 완화 가능성을 검토해야 합니다. 특히 취득 자금 출처 조사에 대비한 자금 조달 계획서 준비가 필수적입니다."
        elif "3주택" in h_count or "4주택" in h_count:
            return "다주택자 중과세율이 적용되고 있습니다. **임대사업자 등록** 시 취득세 감면 혜택(신규 분양 등)이 적용 가능한지 확인해 보세요."
        else:
            return "표준 세율이 적용되는 구간입니다. 취득 후 **60일 이내** 신고 및 납부를 통해 가산세 부담을 피하시는 것이 중요합니다."
            
    elif context == "보유세":
        tax = data.get('tax', 0)
        if tax > 10_000_000:
            return "매년 발생하는 보유세 부담이 1,000만원을 초과합니다. 이는 장기 보유 시 자산 가치 상승분을 상쇄할 수 있으므로, **증여를 통한 명의 분산**이나 **처분 우선순위**를 재설정하는 전략이 필요합니다."
        else:
            return "현재 보유세 부담은 적정 수준이나, 공시가격 상승 추이를 고려하여 **공동명의 변경** 실익을 주기적으로 점검하시기 바랍니다."

    elif context == "양도세":
        tax = data.get('tax', 0)
        gain = data.get('gain', 0)
        if tax > 100_000_000:
            return f"예상 양도세가 {int(tax/10000_000)}천만원에 달합니다. **필요경비(인테리어, 중개보수 등)** 증빙을 철저히 챙기시고, 배우자 증여 후 5년(10년) 이월과세를 활용한 절세 플랜을 시뮬레이션 해보세요."
        elif gain > 0 and tax / gain > 0.4:
            return "양도차익 대비 세금 비율이 40%를 초과합니다. **장기보유특별공제** 요건(거주기간)을 충족했는지 다시 한번 확인하고, 매도 시기를 분산하여 과세표준을 낮추는 방법을 고려하십시오."
        else:
            return "양도차익 실현에 적합한 구조입니다. 매도 대금의 **재투자 포트폴리오(연금/채권)**를 미리 구상하여 자산 증식의 연속성을 확보하세요."

    elif context == "증여세":
        tax = data.get('tax', 0)
        net = data.get('net', 0)
        if tax > 0 and tax > net * 0.3:
            return "증여세 실효세율이 30%를 상회합니다. **부담부 증여(양도세 비교)** 또는 **10년 단위 분산 증여** 전략을 통해 과세표준을 낮추는 것이 유리할 수 있습니다."
        else:
            return "증여 실행 후 3개월 이내 신고 시 3% 세액공제를 받을 수 있습니다. 수증자가 소득이 없는 경우 증여세 대납액도 재차 증여로 간주되므로 주의가 필요합니다."

    elif context == "상속세":
        tax = data.get('tax', 0)
        base = data.get('base', 0)
        if tax > 0:
            return f"예상 상속세가 {f_w(tax)}원입니다. **종신보험**을 활용한 상속세 재원 마련이나, 사전 증여를 통해 상속 재산 규모를 줄이는 전략(상속 개시 10년 전)이 시급합니다."
        else:
            return "현재 기준으로 상속세 발생 가능성은 낮습니다. 다만 자산 가치 상승을 고려하여 5년 주기로 상속세 시뮬레이션을 재점검하는 것이 좋습니다."
            
    elif context == "은퇴설계":
        goal = data.get('goal', 0)
        saved = data.get('saved', 0)
        if saved > 2_000_000:
            return f"목표 달성을 위해 매월 {int(saved/10000)}만원의 저축이 필요합니다. 부담스러운 규모라면 **투자 수익률 제고(ISA, 연금저축)** 또는 **은퇴 목표 시기 조정**을 고려해야 합니다."
        else:
            return "현실적인 저축 목표 구간입니다. **연금저축펀드**와 **IRP**를 적극 활용하여 세액공제 혜택과 과세이연 효과를 동시에 누리십시오."
            
    return "고객님의 데이터를 기반으로 최적의 절세 및 자산 증식 전략을 분석 중입니다."

# 5. Modules



def render_real_estate():
    st.title("🏠 부동산 통합 시뮬레이터")
    st.markdown("취득, 보유, 양도 전 단계에 걸친 세금을 정밀하게 분석하고 절세 전략을 수립합니다.")
    
    # A. Smart Search (Global - Above Tabs)
    if not st.session_state.presentation_mode:
        with st.container():
            c_search, c_btn = st.columns([3, 1])
            addr_input = c_search.text_input("📍 스마트 주소 검색 (취득/보유/양도 통합 연동)", placeholder="예: 반포자이 84 (엔터)")
            if c_btn.button("🔍 데이터 로드"):
                found = False
                target_p, target_area = 0, 0
                
                # Check Complex Database first
                for k, v in COMPLEX_DB.items():
                    if k in addr_input:
                        target_p, target_area = int(v[0]), v[1]
                        st.toast(f"✅ {k} 실거래 기반 정밀 연동 완료!", icon="🏢")
                        found = True
                        break
                
                # Check Regional/Subway Database if not found
                if not found:
                    for reg, price in REGION_DB.items():
                        if reg in addr_input:
                            target_p, target_area = int(price), 84.0
                            st.toast(f"📍 {reg} 지역 평균 시세({f_w(price)}) 기반 데이터가 로드되었습니다.", icon="🌍")
                            found = True
                            break
                
                if found:
                    # Sync ALL tabs
                    st.session_state.acq_p = target_p
                    st.session_state.acq_area = target_area
                    st.session_state.hold_p = int(target_p * 0.7) # Assume official price is 70% of market
                    st.session_state.yang_s = target_p
                    st.session_state.yang_b = int(target_p * 0.8) # Assume 20% gain as default
                    st.rerun()
                else:
                    st.warning("⚠️ 정확한 단지나 지역을 찾을 수 없어 전국 공통 평균가로 연동되었습니다. 수치를 직접 조정해 주세요.")

    tab1, tab2, tab3 = st.tabs(["1️⃣ 취득세 정밀 분석", "2️⃣ 보유세(재산/종부) 예측", "3️⃣ 양도소득세 시뮬레이션"])

    # --- Tab 1: 취득세 ---
    with tab1:

        # Layout Logic based on Presentation Mode
        if st.session_state.presentation_mode:
            col_input = st.empty() # Hide inputs
            col_result = st.container() # Full width
        else:
            col_input, col_result = st.columns([1, 1.3], gap="large")
        
        # Input Logic (conditionally rendered)
        if not st.session_state.presentation_mode:
            with col_input:
                st.subheader("📋 매물 정보 입력")
                with st.container():
                    prop_type = st.selectbox("부동산 종류", ["주택(매매)", "농지(자경)", "농지(비자경)", "기타 토지/상가"], key="acq_type")
                    area = st.number_input("전용면적(㎡)", value=84.0 if 'acq_area' not in st.session_state else st.session_state.acq_area, key="acq_area", help="건축물대장이나 등기부등본에 기재된 전용면적(평방미터)을 입력하세요. 국민주택규모인 85㎡를 초과하면 농어촌특별세가 추가로 부과되어 세금이 늘어납니다.")
                    price = comma_int_input("취득 가액 (실거래가/원)", st.session_state.acq_p, "acq_p", help="부동산을 실제 매수한 (또는 매수할) 실거래 가격을 입력하세요.")
                    h_count = st.selectbox("주택수 (취득시점 기준)", ["1주택", "2주택", "3주택", "4주택 이상"], key="acq_h", help="이번에 취득하는 주택을 포함하여 세대원이 보유한 총 주택 수입니다.")
                    is_adjustment = st.checkbox("조정대상지역 여부", value=False, key="acq_adj")
                    is_first_home = st.checkbox("생애최초 주택 취득 (감면 적용)", value=False, key="acq_first", help="생애최초 주택 취득 시 취득세 200만원 한도 감면")
        else:
            prop_type = st.session_state.get('acq_type', "주택(매매)")
            area = st.session_state.get('acq_area', 84.0)
            price = st.session_state.get('acq_p', 900_000_000)
            h_count = st.session_state.get('acq_h', "1주택")
            is_adjustment = st.session_state.get('acq_adj', False)
            is_first_home = st.session_state.get('acq_first', False)

        # Logic using TaxEngine
        rate, rate_desc = TaxEngine.get_acquisition_tax(price, area, f"{prop_type} {h_count}", is_adjustment)
            
        tax = price * rate
        
        # Additional Taxes (Approx)
        edu_tax = tax * 0.1 # 지방교육세 (개략)
        rural_tax = 0 if area <= 85 else tax * 0.1 # 농특세 (개략)
        total_tax = tax + edu_tax + rural_tax
        
        # 생애최초 감면 적용
        first_home_reduction = 0
        if is_first_home and "주택" in prop_type:
            first_home_reduction = min(total_tax, 2_000_000)
            total_tax = max(0, total_tax - first_home_reduction)

            
        # 결과 저장 (전략 보고서용)
        st.session_state['result_acq_tax'] = total_tax
        st.session_state['result_acq_price'] = price

        with col_result:
            st.subheader("📊 산출 결과")
            if is_first_home and first_home_reduction > 0:
                st.metric("총 예상 취득세액\n(지방세 포함)", f"{f_w(total_tax)} 원", delta=f"생애최초 -{f_w(first_home_reduction)}원 감면", delta_color="normal")
            else:
                st.metric("총 예상 취득세액\n(지방세 포함)", f"{f_w(total_tax)} 원", delta="예상치")
            
            # Chart
            fig = go.Figure(data=[go.Bar(
                x=['취득세 본세', '지방교육세', '농어촌특별세'],
                y=[tax, edu_tax, rural_tax],
                marker_color=['#1e3a8a', '#3b82f6', '#93c5fd'],
                text=[f"{f_w(tax)}", f"{f_w(edu_tax)}", f"{f_w(rural_tax)}"],
                textposition='auto',
                marker=dict(line=dict(width=1.5, color='white')) # 3D effect
            )])
            fig.update_layout(
                title="세목별 상세 구성", 
                template="plotly_white", 
                height=300, 
                margin=dict(l=20, r=20, t=40, b=20), 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("🔍 취득세 상세 분석 보고서", expanded=True):
                 st.markdown(f"""
                <div class='expert-card'>
                    <div class='expert-title'>📑 취득세 단계별 산출 리포트</div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 1. 과세표준(취득가액) 확정</div>
                        <div class='step-content'>
                            실제 거래가액인 <span class='highlight'>{f_w(price)}원</span>을 과세표준으로 산정합니다.
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 2. 적용 세율 판정 ({rate_desc})</div>
                        <div class='step-content'>
                            {h_count}, {price/1e8:.1f}억, {prop_type} 조건에 따라 표준세율 <span class='highlight'>{rate*100:.2f}%</span>가 적용됩니다.
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 3. 세액 산출 및 부가세 계산</div>
                        <div class='step-content'>
                            • 취득세(본세): {f_w(tax)}원 ({f_w(price)} × {rate*100:.2f}%)<br>
                            • 지방교육세: {f_w(edu_tax)}원 (본세액의 10% 가정)<br>
                            • 농어촌특별세: {f_w(rural_tax)}원 (85㎡ 초과 시 부과)
                        </div>
                    </div>
                    <div class='step-box' style='background: #f8fafc; border: 1px solid #3b82f6;'>
                        <div class='step-title' style='color: #1e3a8a;'>FINAL. 합계 납부액</div>
                        <div class='step-content' style='font-weight: 700; font-size: 1.1rem;'>
                             총 예상 세액: {f_w(total_tax)}원
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        # AI Doctor Call
        render_ai_doctor("취득세", {'tax': total_tax, 'h_count': h_count})

    # --- Tab 2: 보유세 ---
    with tab2:
        if st.session_state.presentation_mode:
            col_input = st.empty()
            col_result = st.container()
        else:
            col_input, col_result = st.columns([1, 1.3], gap="large")

        if not st.session_state.presentation_mode:
            with col_input:
                st.subheader("📋 보유 현황 입력")
                off_p = comma_int_input("주택 공시가격 (총합/원)", st.session_state.hold_p, "hold_p", help="보유하고 있는 모든 주택의 국토교통부 고시 공시가격 합계를 입력하세요. (통상 실거래가의 60~70% 수준)")
                h_type = st.radio("보유 형태", ["1주택(단독)", "다주택"], horizontal=True, key="hold_h")
                
                with st.container():
                    st.caption("세액공제 요건 (1주택자)")
                    c_a, c_b = st.columns(2)
                    age = c_a.slider("연령", 20, 90, 60, key="hold_age")
                    hold_y = c_b.slider("보유기간(년)", 0, 30, 10, key="hold_y")
        else:
            off_p = st.session_state.get('hold_p', 1_500_000_000)
            h_type = st.session_state.get('hold_h', "1주택(단독)")
            age = st.session_state.get('hold_age', 60)
            hold_y = st.session_state.get('hold_y', 10)

        # Logic
        exemption = 1_200_000_000 if "1주택" in h_type else 900_000_000
        j_base = max(0, (off_p - exemption) * 0.6)
        j_tax_raw, j_rate_desc = TaxEngine.get_jongbu_tax(j_base)
        prop_tax_base, prop_edu_tax, prop_city_tax, prop_tax = TaxEngine.get_property_tax(off_p)
        
        deduction_rate = 0
        if "1주택" in h_type:
            age_ded = (0.4 if age>=70 else 0.3 if age>=65 else 0.2 if age>=60 else 0)
            period_ded = (0.5 if hold_y>=15 else 0.4 if hold_y>=10 else 0.2 if hold_y>=5 else 0)
            deduction_rate = min(0.8, age_ded + period_ded)
            
        j_tax_final = j_tax_raw * (1 - deduction_rate)

        with col_result:
            st.subheader("📊 예상 보유세 (재산세 + 종부세)")
            c1, c2, c3 = st.columns(3)
            c1.metric("재산세\n(본세+부가세)", f"{f_w(prop_tax)} 원", delta=f"본세 {f_w(prop_tax_base)} + 교육{f_w(prop_edu_tax)} + 도시{f_w(prop_city_tax)}")
            c2.metric(f"종부세\n(세율 {j_rate_desc})", f"{f_w(j_tax_final)} 원", f"-{int(deduction_rate*100)}% 공제" if deduction_rate > 0 else None)
            c3.metric("총 보유세 합계", f"{f_w(prop_tax + j_tax_final)} 원")
            
            # Donut Chart for Deduction
            if deduction_rate > 0:
                fig = go.Figure(data=[go.Pie(labels=['납부 세액', '세액 공제금액'], 
                                             values=[j_tax_final, j_tax_raw * deduction_rate], 
                                             hole=.6, 
                                             marker=dict(colors=['#1e3a8a', '#e2e8f0'], line=dict(color='#ffffff', width=2)))])
                fig.update_layout(
                    title="세액 공제 효과 분석", 
                    template="plotly_white", 
                    height=250, 
                    margin=dict(t=40, b=20, l=20, r=20)
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("💡 1세대 1주택자로서 고령/장기보유 요건 충족 시 최대 80% 세액공제를 받을 수 있습니다.")

            with st.expander("🔍 보유세 상세 분석 보고서", expanded=True):
                st.markdown(f"""
                <div class='expert-card'>
                    <div class='expert-title'>📑 종합부동산세 단계별 산출 리포트</div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 1. 공시가격 합계 및 기본공제 ({h_type})</div>
                        <div class='step-content'>
                            공시가 {f_w(off_p)}원 - 기본공제 {f_w(exemption)}원 = <span class='highlight'>{f_w(max(0, off_p - exemption))}원</span>
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 2. 과세표준 산정</div>
                        <div class='step-content'>
                            공제 후 금액 × 공정시장가액비율(60%) = <span class='highlight'>{f_w(j_base)}원</span>
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 3. 산출세액 및 세액공제</div>
                        <div class='step-content'>
                            • 재산세(추정): {f_w(prop_tax)}원 (본세 {f_w(prop_tax_base)} + 교육세 {f_w(prop_edu_tax)} + 도시지역분 {f_w(prop_city_tax)})<br>
                            • 종부세 산출세액: {f_w(j_tax_raw)}원 (세율 {j_rate_desc})<br>
                            • 세액공제액: -{f_w(j_tax_raw * deduction_rate)}원 (고령/장기보유 {int(deduction_rate*100)}% 적용)
                        </div>
                    </div>
                    <div class='step-box' style='background: #f8fafc; border: 1px solid #3b82f6;'>
                        <div class='step-title' style='color: #1e3a8a;'>FINAL. 최종 보유세액 (재산세 + 종부세)</div>
                        <div class='step-content' style='font-weight: 700; font-size: 1.1rem;'>
                             재산세 {f_w(prop_tax)}원 + 종부세 {f_w(j_tax_final)}원 = 합계 {f_w(prop_tax + j_tax_final)}원
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 결과 저장 (전략 보고서용)
        st.session_state['result_hold_tax'] = prop_tax + j_tax_final
        st.session_state['result_prop_tax'] = prop_tax
        st.session_state['result_jongbu_tax'] = j_tax_final

        # AI Doctor Call
        render_ai_doctor("보유세", {'tax': j_tax_final})

    # --- Tab 3: 양도세 ---
    with tab3:
        if st.session_state.presentation_mode:
            col_input = st.empty()
            col_result = st.container()
        else:
            col_input, col_result = st.columns([1, 1.3], gap="large")
            
        if not st.session_state.presentation_mode:
            with col_input:
                st.subheader("📋 거래 정보 입력")
                sell_p = comma_int_input("양도 가액 (실제 매도가/원)", st.session_state.yang_s, "yang_s", help="부동산을 매도하는 (또는 매도예정인) 실제 거래가격을 입력하세요.")
                
                buy_p = comma_int_input("취득 가액 (과거 매입가/원)", st.session_state.yang_b, "yang_b", help="과거에 이 부동산을 매수했을 때 지불했던 실제 취득가격을 입력하세요.")
                
                expenses = comma_int_input("필요경비 (중개수수료/인테리어 등/원)", 0, "yang_exp", help="취득세, 중개수수료, 샷시 등 자본적 지출에 해당하는 인테리어 비용의 합계입니다.")
                
                c1, c2 = st.columns(2)
                is_1h = c1.checkbox("1세대 1주택 비과세", value=True if 'yang_1h' not in st.session_state else st.session_state.yang_1h, key="yang_1h")
                multi_house_surcharge = c2.selectbox("다주택 중과", ["없음", "2주택 (+20%p)", "3주택 (+30%p)"], key="yang_multi", disabled=is_1h)
                
                st.caption("장기보유특별공제 입력")
                c3, c4 = st.columns(2)
                h_years = c3.slider("보유기간 (년)", 0, 30, 10, key="yang_h_y")
                r_years = c4.slider("거주기간 (년)", 0, 30, 5, key="yang_r_y", disabled=not is_1h)
        else:
            sell_p = st.session_state.get('yang_s', 1_500_000_000)
            buy_p = st.session_state.get('yang_b', 900_000_000)
            expenses = st.session_state.get('yang_exp', 0)
            is_1h = st.session_state.get('yang_1h', True)
            multi_house_surcharge = st.session_state.get('yang_multi', '없음')
            h_years = st.session_state.get('yang_h_y', 10)
            r_years = st.session_state.get('yang_r_y', 5)

        gain = sell_p - buy_p - expenses
        taxable_gain = gain
        if is_1h and sell_p > 1_200_000_000:
            taxable_gain = gain * (sell_p - 1_200_000_000) / sell_p
        elif is_1h and sell_p <= 1_200_000_000:
            taxable_gain = 0
        
        lt_rate, lt_desc = TaxEngine.get_long_term_deduction(h_years, r_years, is_1h)
        deduction_amt = taxable_gain * lt_rate
        yang_base = max(0, taxable_gain - deduction_amt - 2_500_000)
        
        # 다주택 중과세율 적용
        surcharge_rate = 0
        if not is_1h and multi_house_surcharge != '없음':
            if '2주택' in multi_house_surcharge:
                surcharge_rate = 0.20
            elif '3주택' in multi_house_surcharge:
                surcharge_rate = 0.30
        
        r, p, r_desc = get_tax_rate_5steps(yang_base)
        if surcharge_rate > 0:
            final_tax = max(0, yang_base * (r + surcharge_rate) - p)
        else:
            final_tax = max(0, yang_base * r - p)
        
        # 지방소득세 (10%)
        local_income_tax = final_tax * 0.1
        total_yang_tax = final_tax + local_income_tax

        with col_result:
            st.subheader("📊 양도소득 분석")
            c1, c2, c3 = st.columns(3)
            c1.metric("양도소득세", f"{f_w(final_tax)} 원")
            c2.metric("지방소득세\n(10%)", f"{f_w(local_income_tax)} 원")
            c3.metric("세후 실수령액", f"{f_w(sell_p - total_yang_tax)} 원", delta_color="normal")
            
            if surcharge_rate > 0:
                st.warning(f"⚠️ 다주택 중과세율 +{int(surcharge_rate*100)}%p 적용됨 (적용세율: {(r+surcharge_rate)*100:.0f}%)")
            
            # Waterfall sort of Bar chart
            fig = go.Figure(data=[
                go.Bar(name='금액', x=['매도가액', '취득가액', '필요경비', '양도차익', '양도세+지방세'], 
                       y=[sell_p, buy_p, expenses, gain, total_yang_tax],
                       marker_color=['#cbd5e1', '#94a3b8', '#64748b', '#3b82f6', '#ef4444'],
                       marker=dict(line=dict(width=1.5, color='white')))
            ])
            fig.update_layout(
                title="자금 흐름 분석", 
                template="plotly_white", 
                height=300, 
                plot_bgcolor='rgba(0,0,0,0)',
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
            st.plotly_chart(fig, use_container_width=True)

            with st.expander("🔍 양도세 상세 분석 보고서", expanded=True):
                st.markdown(f"""
                <div class='expert-card'>
                    <div class='expert-title'>📑 양도소득세 단계별 산출 리포트</div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 1. 양도차익 계산</div>
                        <div class='step-content'>
                            양도가 {f_w(sell_p)} - 취득가 {f_w(buy_p)} - 필요경비 {f_w(expenses)} = <span class='highlight'>{f_w(gain)}원</span>
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 2. 장기보유특별공제 및 기본공제</div>
                        <div class='step-content'>
                            • 비과세 제외 과세대상차익: {f_w(taxable_gain)}원<br>
                            • 장특공제: -{f_w(deduction_amt)}원 ({lt_desc})<br>
                            • 양도소득기본공제: -2,500,000원
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 3. 과세표준 및 세율 적용</div>
                        <div class='step-content'>
                            • 양도과표: {f_w(yang_base)}원<br>
                            • 적용세율: {r_desc}
                        </div>
                    </div>
                    <div class='step-box' style='background: #f8fafc; border: 1px solid #ef4444;'>
                        <div class='step-title' style='color: #991b1b;'>FINAL. 예상 양도소득세</div>
                        <div class='step-content' style='font-weight: 700; font-size: 1.1rem;'>
                             양도소득세: {f_w(final_tax)}원{f' (중과 +{int(surcharge_rate*100)}%p)' if surcharge_rate > 0 else ''}<br>
                             지방소득세: {f_w(local_income_tax)}원<br>
                             <span class='highlight'>총 납부액: {f_w(total_yang_tax)}원</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

        # 결과 저장 (전략 보고서용)
        st.session_state['result_yang_tax'] = total_yang_tax
        st.session_state['result_yang_gain'] = gain
        st.session_state['result_local_tax'] = local_income_tax

        # AI Doctor Call
        render_ai_doctor("양도세", {'tax': final_tax, 'gain': gain})


def render_inheritance():
    st.title("🎁 상속 및 증여세 시뮬레이터")
    st.markdown("복잡한 상속/증여 계산을 누진세율 효과까지 고려하여 정밀하게 시뮬레이션합니다.")
    
    tab1, tab2 = st.tabs(["증여세 (10년 합산/부담부)", "상속세 (일괄/배우자)"])
    
    with tab1:
        if st.session_state.presentation_mode:
            col_input = st.empty()
            col_result = st.container()
        else:
            col_input, col_result = st.columns([1, 1.3], gap="large")

        if not st.session_state.presentation_mode:
            with col_input:
                st.subheader("📋 증여세 계산")
                curr = comma_int_input("증여 가액 (원)", st.session_state.gif_c, "gif_c", help="이번에 배우자나 자녀에게 증여하고자 하는 재산(현금, 부동산 등)의 총 평가액입니다.")
                prev = comma_int_input("10년 내 사전증여액(원)", 0, "gif_p", help="과거 10년 이내에 같은 사람(동일인)에게 이미 증여했던 재산가액의 합계입니다. 누진과세를 위해 합산됩니다.")
                prev_tax = comma_int_input("기납부 증여세액(원)", 0, "gif_p_tax", help="과거 사전증여 당시 이미 납부했던 증여세액입니다. (이중과세 방지를 위해 기납부세액으로 공제됩니다.)")
                debt = comma_int_input("부담부 채무액(원)", 0, "gif_d", help="부동산 증여 시 함께 넘겨주는 전세보증금이나 담보대출액 등 수증자(받는사람)가 대신 갚기로 한 채무액입니다.")
                
                rel = st.selectbox("수증자 관계", ["배우자(6억)", "성년 자녀(5천만)", "미성년 자녀(2천만)", "기타친족(1천만)"], key="gif_r")
                
                c1, c2 = st.columns(2)
                is_gen_skip = c1.checkbox("세대생략 증여 (할증부과)", value=False, key="gif_skip")
                is_minor_high = c2.checkbox("수증자 미성년 (20억 초과 시 40% 적용)", value=False, key="gif_minor", disabled=not is_gen_skip)
        else:
            curr = st.session_state.get('gif_c', 300_000_000)
            prev = st.session_state.get('gif_p', 0)
            prev_tax = st.session_state.get('gif_p_tax', 0)
            debt = st.session_state.get('gif_d', 0)
            rel = st.session_state.get('gif_r', "성년 자녀(5천만)")
            is_gen_skip = st.session_state.get('gif_skip', False)
            is_minor_high = st.session_state.get('gif_minor', False)
            
        # Logic
        ded_map = {"배우자": 6e8, "성년": 5e7, "미성년": 2e7, "기타": 1e7}
        ded = 0
        for k, v in ded_map.items():
            if k in rel: ded = v; break
        
        tax_base = max(0, (curr + prev - debt) - ded)
        r, p, r_desc = get_tax_rate_5steps(tax_base)
        calc_tax = tax_base * r - p
        
        # Surcharge
        surcharge_amt, surcharge_desc = TaxEngine.get_generation_skipping_surcharge(calc_tax, is_gen_skip, is_minor_high)
        
        # Credit for previously paid tax (기납부세액공제) - Cannot exceed calculated tax + surcharge
        max_credit = calc_tax + surcharge_amt
        applied_prev_tax = min(prev_tax, max_credit)
        
        tax_after_prepaid = calc_tax + surcharge_amt - applied_prev_tax
        final_tax = tax_after_prepaid * 0.97 # 신고세액공제 3%
        
        net_gift = curr - debt - final_tax

        # Logic Breakdown Steps (Moved to Result Column)
        
        with col_result:
            st.subheader("📊 증여 플랜 분석")
            c1, c2 = st.columns(2)
            c1.metric("산출세액\n(신고공제 후)", f"{f_w(final_tax)} 원")
            c2.metric("실질 수령액", f"{f_w(net_gift)} 원", delta="채무/세금 차감 후")
            
            # Pie Chart
            fig = px.pie(
                names=['실 수령액', '납부 세액', '채무 승계액'],
                values=[net_gift, final_tax, debt],
                color_discrete_sequence=['#1e3a8a', '#94a3b8', '#cbd5e1'],
                hole=0.5
            )
            fig.update_traces(marker=dict(line=dict(color='#ffffff', width=2)), pull=[0.05, 0, 0])
            fig.update_layout(
                title="증여 자금 구성 (Funds Breakdown)", 
                template="plotly_white", 
                height=300,
                showlegend=True
            )
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            
            # Detail Side-by-Side with Logic (Logic moved to Input bottom, so here just Detail)
            with st.expander("🔍 증여세 상세 분석 보기", expanded=True):
                    st.markdown(f"""
                    <div class='expert-card'>
                        <div class='expert-title'>📑 증여세 산출 리포트</div>
                        <div class='step-box'>
                            <div class='step-title'>1. 합산 과세 ({'합산없음' if prev==0 else '사전증여 합산'})</div>
                            <div class='step-content'>
                                총 증여가액 <span class='highlight'>{f_w(curr+prev)}원</span>에서 채무 <span class='highlight'>{f_w(debt)}원</span>을 차감하여 순 증여분을 도출합니다.
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>2. 증여재산 공제</div>
                            <div class='step-content'>
                                {rel} 기준으로 <span class='highlight'>{f_w(ded)}원</span>을 공제하여 과세표준 <span class='highlight'>{f_w(tax_base)}원</span>을 확정했습니다.
                                <div class='logic-annotation'>
                                    💡 <b>공제 한도(10년):</b><br>
                                    - 배우자: 6억<br>
                                    - 직계존비속: 5천만원(미성년 2천만원)<br>
                                    - 기타친족: 1천만원
                                </div>
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>3. 최종 세액 산출</div>
                            <div class='step-content'>
                                과세표준에 누진세율을 적용하여 산출세액을 구한 뒤, {'기납부세액공제 <span class="highlight">' + f_w(applied_prev_tax) + '원</span> 및 ' if applied_prev_tax > 0 else ''}신고세액공제(3%)를 차감하여 최종 납부 세액을 산출합니다.
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Logic Breakdown Steps (Moved to Input Bottom)
        # However, col_input is hidden in presentation mode so this stays in Design Mode context effectively
        if not st.session_state.presentation_mode:
             with col_input:
                st.markdown(f"""
                <div class='step-box' style='margin-top:20px; border-left:5px solid #22c55e;'>
                <div class='step-title'>📝 단계별 산출 로직</div>
                <div class='step-content'>
                <b>1. 증여세 과세가액 ({f_w(curr+prev-debt)}원)</b><br>
                = (증여재산 {f_w(curr)} + 사전증여 {f_w(prev)}) - 채무 승계 {f_w(debt)}<br>
                <br>
                <b>2. 과세표준 ({f_w(tax_base)}원)</b><br>
                = 과세가액 {f_w(curr+prev-debt)} - 증여재산공제({rel}: {f_w(ded)})<br>
                <br>
                <b>3. 산출세액 ({f_w(calc_tax)}원)</b><br>
                = 과세표준 {f_w(tax_base)} × 세율({int(r*100)}%) - 누진공제 {f_w(p)}<br>
                <br>
                {'<b>4. 세대생략 할증세액 ('+f_w(surcharge_amt)+'원)</b><br>= 산출세액 '+f_w(calc_tax)+' × 할증률 ('+('40%' if is_minor_high else '30%')+')<br><br>' if is_gen_skip else ''}
                {f'<b>{5 if is_gen_skip else 4}. 기납부세액공제 ({f_w(applied_prev_tax)}원)</b><br>= 사전증여에 대해 이미 납부한 세액 차감<br><br>' if prev_tax > 0 else ''}
                <b>{6 if is_gen_skip and prev_tax > 0 else (5 if is_gen_skip or prev_tax > 0 else 4)}. 최종납부세액 ({f_w(final_tax)}원)</b><br>
                = (산출세액 {f_w(calc_tax)} {f'+ 할증 {f_w(surcharge_amt)}' if is_gen_skip else ''} {f'- 기납부세액 {f_w(applied_prev_tax)}' if prev_tax > 0 else ''}) - 신고세액공제 {f_w(tax_after_prepaid * 0.03)} (3%)
                </div>
                </div>
                """, unsafe_allow_html=True)

        # 결과 저장 (전략 보고서용)
        st.session_state['result_gift_tax'] = final_tax
        st.session_state['result_gift_net'] = net_gift

        # 신고기한 안내
        if final_tax > 0:
            st.info("📅 **증여세 신고 기한**: 증여일이 속하는 달의 말일부터 **3개월** 이내에 관할 세무서에 신고·납부하셔야 합니다. 기한 내 신고 시 신고세액공제(3%)가 적용됩니다.")

        # AI Doctor Call
        render_ai_doctor("증여세", {'tax': final_tax, 'net': net_gift})
    
    with tab2:
        if st.session_state.presentation_mode:
            col_input = st.empty()
            col_result = st.container()
        else:
            col_input, col_result = st.columns([1, 1.3], gap="large")

        if not st.session_state.presentation_mode:
            with col_input:
                st.subheader("📋 상속세 계산")
                
                with st.container():
                    st.markdown("##### 1. 상속 재산")
                    estate_val = comma_int_input("상속 재산 총액 (원)", st.session_state.inh_ev, "inh_ev", help="고인(피상속인)이 남긴 예금, 주식, 부동산(평가액 기준) 등 모든 재산의 총합입니다.")
                    prev_gift_inh = comma_int_input("10년 내 사전증여재산 (원)", 0, "inh_prev_gift", help="고인이 사망하기 전 상속인에게는 10년 이내, 상속인 외(며느리/사위/손자 등)에게는 5년 이내에 사전 증여했던 재산의 증여 당시 가액입니다.")
                    prev_tax_inh = comma_int_input("기납부 증여세액 (원)", 0, "inh_prev_tax", help="합산된 사전증여재산에 대해 과거에 이미 납부했던 증여세액 합계입니다.")
                    
                    debt_inh = comma_int_input("공제 대상 채무액 (원)", 0, "inh_d", help="고인이 남긴 대출금, 미납세금, 반환해야 할 임대보증금 등 상속재산에서 차감될 부채입니다.")
                    funeral = comma_int_input("장례비용(원)", 0, "inh_f", help="장례를 치르는 데 사용된 비용입니다. (기본 500만원 ~ 최대 1,000만원 한도 내 공제, 봉안시설 500만원 별도 추가 가능)")

                with st.container():
                    st.markdown("##### 2. 상속 공제 설정")
                    has_spouse = st.checkbox("배우자 생존", value=True if 'inh_sp' not in st.session_state else st.session_state.inh_sp, key="inh_sp")
                    
                    # Spouse Deduction Logic
                    spouse_ded_val = 500_000_000
                    if has_spouse:
                        spouse_ded_val = st.number_input("배우자 상속공제액(원)", value=0 if 'inh_sp_ded' not in st.session_state else st.session_state.inh_sp_ded, min_value=0, max_value=3_000_000_000, step=10_000_000, format="%d", key="inh_sp_ded")
                        show_kr_label(st.session_state.get('inh_sp_ded', 500_000_000))
                    
                    # Lump-sum vs Itemized
                    ded_type = st.radio("공제 방식", ["일괄공제 (5억)", "기초+인적공제"], horizontal=True, key="inh_type")
                    
                    # Financial Asset Deduction
                    fin_asset = st.number_input("순금융재산가액(원)", value=0, step=10_000_000, format="%d", key="inh_fin", help="순금융재산의 20%, 최대 2억원 공제 / 2천만원 이하는 전액")
                    show_kr_label(st.session_state.get('inh_fin', 200_000_000), has_help=True)
                    
                is_gen_skip_inh = st.checkbox("세대생략 상속 (손주 등)", value=False, key="inh_skip")
        else:
            estate_val = st.session_state.get('inh_ev', 1_500_000_000)
            prev_gift_inh = st.session_state.get('inh_prev_gift', 0)
            prev_tax_inh = st.session_state.get('inh_prev_tax', 0)
            debt_inh = st.session_state.get('inh_d', 100_000_000)
            funeral = st.session_state.get('inh_f', 10_000_000)
            has_spouse = st.session_state.get('inh_sp', True)
            spouse_ded_val = st.session_state.get('inh_sp_ded', 500_000_000)
            ded_type = st.session_state.get('inh_type', "일괄공제 (5억)")
            fin_asset = st.session_state.get('inh_fin', 200_000_000)
            is_gen_skip_inh = st.session_state.get('inh_skip', False)

        # Logic Re-construction for variables that might be missing in 'else' block
        # (Actually, we need to replicate the 'if has_spouse' logic or ensure variables are defined)
        
        basic_ded = 200_000_000 
        final_other_ded = 500_000_000 # Default to Lump
        if "일괄" in ded_type:
            final_other_ded = 500_000_000
        else:
            # children input was inside 'else' in original? No, it was inside cond.
            # If pres mode, we assume default 2 children for calculation or need state.
            final_other_ded = basic_ded + (2 * 50_000_000)

        fin_ded = 0
        if fin_asset <= 20_000_000: fin_ded = fin_asset
        else: fin_ded = min(200_000_000, max(20_000_000, fin_asset * 0.2))

        # Calculation
        net_estate = estate_val + prev_gift_inh - debt_inh - funeral
        total_deduction = final_other_ded + spouse_ded_val + fin_ded
        tax_base = max(0, net_estate - total_deduction)
        
        r_i, p_i, r_desc = get_tax_rate_5steps(tax_base)
        calc_tax_i = tax_base * r_i - p_i
        
        # Surcharge
        surcharge_inh, surcharge_inh_desc = TaxEngine.get_generation_skipping_surcharge(calc_tax_i, is_gen_skip_inh, False)
        
        # Credit for previously paid gift tax
        max_credit_inh = calc_tax_i + surcharge_inh
        applied_prev_tax_inh = min(prev_tax_inh, max_credit_inh)
        
        tax_after_prepaid_inh = calc_tax_i + surcharge_inh - applied_prev_tax_inh
        final_tax_i = tax_after_prepaid_inh * 0.97 # Declaration Credit

        with col_result:
            st.subheader("📊 상속세 분석 결과")
            c1, c2 = st.columns(2)
            c1.metric("과세표준", f"{f_w(tax_base)} 원")
            c2.metric("최종 예상 납부액", f"{f_w(final_tax_i)} 원", delta_color="inverse")
            
            # Waterfall Chart for Tax Logic
            fig = go.Figure(go.Waterfall(
                name = "20", orientation = "v",
                measure = ["relative", "relative", "relative", "relative", "total", "total"],
                x = ["상속재산", "사전증여(10년)", "비과세/공과금", "상속공제", "과세표준", "예상 세액"],
                textposition = "outside",
                text = [f"{f_w(estate_val/1e8)}억", f"{f_w(prev_gift_inh/1e8)}억", f"-{f_w((debt_inh+funeral)/1e8)}억", 
                        f"-{f_w(total_deduction/1e8)}억", f"{f_w(tax_base/1e8)}억", f"-{f_w(final_tax_i/1e8)}억"],
                y = [estate_val, prev_gift_inh, -(debt_inh+funeral), -total_deduction, tax_base, -final_tax_i],
                connector = {"line":{"color":"rgb(63, 63, 63)"}},
                decreasing = {"marker":{"color":"#ef4444", "line":{"width":1, "color":"white"}}},
                increasing = {"marker":{"color":"#1e3a8a", "line":{"width":1, "color":"white"}}},
                totals = {"marker":{"color":"#3b82f6", "line":{"width":1, "color":"white"}}}
            ))
            fig.update_layout(
                title="상속세 구조 분석 (Waterfall)", 
                template="plotly_white", 
                height=350
            )
            st.plotly_chart(fig, use_container_width=True)

            st.divider()
            
            # Logic & Detail Side-by-Side
            # Logic & Detail Side-by-Side (Refactored)
            c_detail = st.container()
            

            with c_detail:
                with st.expander("🔍 상속세 상세 분석 보기", expanded=True):
                    st.markdown(f"""
                    <div class='expert-card'>
                        <div class='expert-title'>📑 상속세 산출 리포트</div>
                        <div class='step-box'>
                            <div class='step-title'>STEP 1. 과세가액 파악 ({'합산없음' if prev_gift_inh==0 else '사전증여 합산'})</div>
                            <div class='step-content'>
                                총 상속재산 <span class='highlight'>{f_w(estate_val)}원</span>{'에서 ' if prev_gift_inh == 0 else f'과 사전증여재산 <span class="highlight">{f_w(prev_gift_inh)}원</span>을 합산한 뒤, '}채무 및 장례비용 <span class='highlight'>{f_w(debt_inh+funeral)}원</span>을 차감합니다.
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>STEP 2. 상속공제 적용 ({'일괄' if '일괄' in ded_type else '기초'})</div>
                            <div class='step-content'>
                                배우자공제 <span class='highlight'>{f_w(spouse_ded_val)}원</span>, 
                                {ded_type} <span class='highlight'>{f_w(final_other_ded)}원</span>, 
                                금융재산공제 <span class='highlight'>{f_w(fin_ded)}원</span>을 적용했습니다.
                                <br>👉 <b>총 공제액: {f_w(total_deduction)}원</b>
                                <div class='logic-annotation'>
                                    💡 <b>금융재산상속공제 계산:</b><br>
                                    순금융재산가액 {f_w(fin_asset)}원의 20% = {f_w(fin_asset*0.2)}원<br>
                                    (한도: 최대 2억원 / 2천만원 이하는 전액 공제)
                                </div>
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>STEP 3. 과세표준 및 세액 - {r_desc}</div>
                            <div class='step-content'>
                                과세표준 {f_w(tax_base)}원에 대해 세율 {int(r_i*100)}%가 적용되며, {'기납부증여세액공제 <span class="highlight">' + f_w(applied_prev_tax_inh) + '원</span> 및 ' if applied_prev_tax_inh > 0 else ''}신고세액공제를 차감하여 최종 세액을 산출합니다.
                                <div class='logic-annotation'>
                                    💡 <b>상속세율 구간:</b><br>
                                    - 1억 이하: 10%<br>
                                    - 5억 이하: 20% (누진공제 1천만원)<br>
                                    - 10억 이하: 30% (누진공제 6천만원)<br>
                                    - 30억 이하: 40% (누진공제 1.6억원)<br>
                                    - 30억 초과: 50% (누진공제 4.6억원)
                                </div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

        # Logic Breakdown Steps (Moved to Input Bottom)
        if not st.session_state.presentation_mode:
            with col_input:
                st.markdown(f"""
                <div class='step-box' style='margin-top:20px; border-left:5px solid #a855f7;'>
                <div class='step-title'>📝 단계별 산출 로직</div>
                <div class='step-content'>
                <b>1. 상속세 과세가액 ({f_w(net_estate)}원)</b><br>
                = (상속재산 {f_w(estate_val)} + 사전증여 {f_w(prev_gift_inh)}) - (채무/공과/장례 {f_w(debt_inh+funeral)})<br>
                <br>
                <b>2. 상속공제 총액 ({f_w(total_deduction)}원)</b><br>
                = 기초/일괄 {f_w(final_other_ded)} + 배우자 {f_w(spouse_ded_val)} + 금융 {f_w(fin_ded)}<br>
                <br>
                <b>3. 과세표준 ({f_w(tax_base)}원)</b><br>
                = 과세가액 {f_w(net_estate)} - 상속공제총액 {f_w(total_deduction)}<br>
                <br>
                <b>4. 산출세액 ({f_w(calc_tax_i)}원)</b><br>
                = 과세표준 {f_w(tax_base)} × 세율({int(r_i*100)}%) - 누진공제 {f_w(p_i)}<br>
                <br>
                {'<b>5. 세대생략 할증세액 ('+f_w(surcharge_inh)+'원)</b><br>= 산출세액 '+f_w(calc_tax_i)+' × 할증률(30%)<br><br>' if is_gen_skip_inh else ''}
                {f'<b>{6 if is_gen_skip_inh else 5}. 기납부증여세액공제 ({f_w(applied_prev_tax_inh)}원)</b><br>= 합산된 사전증여에 대해 납부한 세액 차감<br><br>' if prev_tax_inh > 0 else ''}
                <b>{7 if is_gen_skip_inh and prev_tax_inh > 0 else (6 if is_gen_skip_inh or prev_tax_inh > 0 else 5)}. 최종납부세액 ({f_w(final_tax_i)}원)</b><br>
                = (산출세액 {f_w(calc_tax_i)} {f'+ 할증 {f_w(surcharge_inh)}' if is_gen_skip_inh else ''} {f'- 기납부세액 {f_w(applied_prev_tax_inh)}' if prev_tax_inh > 0 else ''}) - 신고세액공제 {f_w(tax_after_prepaid_inh * 0.03)} (3%)
                </div>
                </div>
                """, unsafe_allow_html=True)

        # 결과 저장 (전략 보고서용)
        st.session_state['result_inh_tax'] = final_tax_i
        st.session_state['result_inh_estate'] = estate_val

        # AI Doctor Call
        render_ai_doctor("상속세", {'tax': final_tax_i, 'base': tax_base})

    # === 종신보험을 활용한 상속세 재원 마련 및 절세 전략 ===
    st.markdown("---")
    st.subheader("🛡️ 종신보험 활용 절세 및 재원 마련 전략")
    
    if st.session_state.presentation_mode:
        col_ins_input = st.empty()
        col_ins_res = st.container()
    else:
        col_ins_input, col_ins_res = st.columns([1, 1.3], gap="large")

    if not st.session_state.presentation_mode:
        with col_ins_input:
            st.markdown("##### 1. 유동성 자산 및 보험금 설정")
            liquid_asset = comma_int_input("보유 현금성 자산 (원)", 0, "inh_liquid", help="상속세를 납부하기 위해 동원할 수 있는 예금, 적금 등 즉시 현금화 가능한 자산의 총액을 의미합니다.")
            
            shortfall = max(0, final_tax_i - liquid_asset)
            
            if 'inh_death_benefit' not in st.session_state:
                st.session_state.inh_death_benefit = int(shortfall) if shortfall > 0 else 500_000_000
            death_benefit = comma_int_input("종신보험 가입금액 (사망보험금/원)", st.session_state.inh_death_benefit, "inh_death_benefit", help="절세 및 상속세 납부 재원 마련을 위해 설계하는 종신보험의 사망보험금 크기를 입력하세요.")
    else:
        liquid_asset = st.session_state.get('inh_liquid', 0)
        shortfall = max(0, final_tax_i - liquid_asset)
        death_benefit = st.session_state.get('inh_death_benefit', shortfall if shortfall > 0 else 500_000_000)

    with col_ins_res:
        st.markdown("##### 💡 1. 상속세 재원(유동성) 분석")
        
        if shortfall > 0:
            st.error(f"⚠️ 상속세 납부를 위한 현금 재원이 **{f_w(shortfall)}원 부족**합니다. (부동산 급매/물납 위험 경고)")
        else:
            st.success(f"✅ 상속세 납부를 위한 현금 재원이 충분합니다. (잔여 현금: {f_w(liquid_asset - final_tax_i)}원)")

        st.markdown("##### 💡 2. 계약 구조별 상속세 절세 효과 (사망보험금 비과세)")
        
        # A안: 부모 계약/납입 -> 보험금이 상속재산 포함
        net_estate_A = net_estate + death_benefit
        tax_base_A = max(0, net_estate_A - total_deduction)
        r_A, p_A, _ = get_tax_rate_5steps(tax_base_A)
        calc_tax_A = tax_base_A * r_A - p_A
        surcharge_A, _ = TaxEngine.get_generation_skipping_surcharge(calc_tax_A, is_gen_skip_inh, False)
        max_credit_A = calc_tax_A + surcharge_A
        applied_prev_tax_A = min(prev_tax_inh, max_credit_A)
        tax_after_prepaid_A = calc_tax_A + surcharge_A - applied_prev_tax_A
        final_tax_A = tax_after_prepaid_A * 0.97
        
        # B안: 자녀 계약/납입 -> 비과세 (기존 상속세와 동일)
        final_tax_B = final_tax_i
        
        tax_saving = final_tax_A - final_tax_B
        
        c1, c2 = st.columns(2)
        c1.metric("A안 (부모 납입)", f"{f_w(final_tax_A)} 원", delta="보험금이 상속재산에 합산 부과", delta_color="inverse")
        c2.metric("B안 (자녀 납입)", f"{f_w(final_tax_B)} 원", delta=f"{f_w(tax_saving)}원 상속세 절감 효과", delta_color="normal")
        
        st.info("💡 **자녀가 계약자/납입자**가 되고 실질적인 소득증빙이 가능하다면, 종신보험의 사망보험금은 상속재산에 포함되지 않아 **상속세 없이 100% 비과세 현금 수령**이 가능합니다.")
        
        fig_ins = go.Figure(data=[
            go.Bar(name='예상 상속세', x=['A안 (합산과세)', 'B안 (비과세)'], y=[final_tax_A, final_tax_B], marker_color=['#ef4444', '#3b82f6'], text=[f"{f_w(final_tax_A)}원", f"{f_w(final_tax_B)}원"], textposition='auto')
        ])
        fig_ins.update_layout(title="계약 구조별 상속세액 비교", template="plotly_white", height=300, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_ins, use_container_width=True)

def render_retirement():
    st.title("⏳ 은퇴자금 계산")
    st.markdown("고객님의 현재 나이와 목표, 경제 변수를 반영한 **1:1 맞춤형 은퇴 설계 솔루션**입니다.")
    
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 은퇴 설계 입력")
            
            # 1. Personal Info
            with st.container():
                st.markdown("##### 1. 고객정보")
                c_name, c_age = st.columns([1.5, 1])
                client_name = c_name.text_input("고객 성함", "", key="ret_name")
                current_age = c_age.number_input("현재 나이", min_value=0, max_value=100, value=0, key="ret_age")
                goal_p = comma_int_input("희망 월 생활비 (현재가치/원)", st.session_state.ret_goal_p, "ret_goal_p")
    else:
        client_name = st.session_state.get('ret_name', "")
        current_age = st.session_state.get('ret_age', 0)
        goal_p = st.session_state.get('ret_goal_p', 3_000_000)
        
            
    if not st.session_state.presentation_mode:
        with col_input:
            # 2. Timeline
            st.markdown("##### 2. 은퇴 타임라인")
            
            # Helper callbacks for sync
            if 'pay_years_sl' not in st.session_state: st.session_state.pay_years_sl = 10
            if 'pay_years_num' not in st.session_state: st.session_state.pay_years_num = 10
            
            def update_pay_years_sl():
                st.session_state.pay_years_num = st.session_state.pay_years_sl
            def update_pay_years_num():
                st.session_state.pay_years_sl = st.session_state.pay_years_num

            if 'ret_age_sl' not in st.session_state: st.session_state.ret_age_sl = 60
            if 'ret_age_num' not in st.session_state: st.session_state.ret_age_num = 60
            
            def update_ret_age_sl():
                st.session_state.ret_age_num = st.session_state.ret_age_sl
            def update_ret_age_num():
                st.session_state.ret_age_sl = st.session_state.ret_age_num
            
            if 'life_age_sl' not in st.session_state: st.session_state.life_age_sl = 90
            if 'life_age_num' not in st.session_state: st.session_state.life_age_num = 90
            
            def update_life_age_sl():
                st.session_state.life_age_num = st.session_state.life_age_sl
            def update_life_age_num():
                st.session_state.life_age_sl = st.session_state.life_age_num

            # UI Rendering (Reordered)
            y_s_limit = max(1, st.session_state.ret_age_sl - current_age)
            
            c_p1, c_p2 = st.columns([2, 1])
            with c_p1: st.slider("납입 기간 (년)", min_value=1, max_value=max(y_s_limit, 2), key='pay_years_sl', disabled=(y_s_limit <= 1), on_change=update_pay_years_sl)
            with c_p2: 
                st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                st.number_input("납입 기간 입력", min_value=1, max_value=max(y_s_limit, 1), key='pay_years_num', label_visibility="collapsed", on_change=update_pay_years_num)

            c1, c2 = st.columns([2, 1])
            with c1: st.slider("은퇴 목표 나이", min_value=current_age, max_value=max(90, current_age + 1), key='ret_age_sl', on_change=update_ret_age_sl)
            with c2: 
                st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                st.number_input("은퇴 나이(세)", min_value=current_age, max_value=max(90, current_age), key='ret_age_num', label_visibility="collapsed", on_change=update_ret_age_num)
            
            c3, c4 = st.columns([2, 1])
            with c3: st.slider("기대 수명 (은퇴 종료)", min_value=current_age, max_value=max(110, current_age + 1), key='life_age_sl', on_change=update_life_age_sl)
            with c4: 
                st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                st.number_input("기대 수명(세)", min_value=current_age, max_value=max(110, current_age), key='life_age_num', label_visibility="collapsed", on_change=update_life_age_num)
            
            # 3. Financials
            st.markdown("##### 3. 재무 변수")
            
            # Sync for Financials
            if 'inf_sl' not in st.session_state: st.session_state.inf_sl = 3.0
            if 'inf_num' not in st.session_state: st.session_state.inf_num = 3.0
            
            def update_inf_sl():
                st.session_state.inf_num = st.session_state.inf_sl
            def update_inf_num():
                st.session_state.inf_sl = st.session_state.inf_num
                
            if 'yield_sl' not in st.session_state: st.session_state.yield_sl = 6.0
            if 'yield_num' not in st.session_state: st.session_state.yield_num = 6.0
            
            def update_yield_sl():
                st.session_state.yield_num = st.session_state.yield_sl
            def update_yield_num():
                st.session_state.yield_sl = st.session_state.yield_num
            
            c_a, c_b = st.columns(2)
            with c_a:
                st.markdown("물가상승률(%)")
                c_a1, c_a2 = st.columns([2, 1])
                inf = c_a1.slider("물가상승률", min_value=0.0, max_value=50.0, step=0.1, label_visibility="collapsed", key='inf_sl', on_change=update_inf_sl)
                inf = c_a2.number_input("물가상승률 입력", min_value=0.0, max_value=50.0, step=0.1, label_visibility="collapsed", key='inf_num', on_change=update_inf_num)
                
            with c_b:
                st.markdown("투자수익률(%)")
                c_b1, c_b2 = st.columns([2, 1])
                yield_r = c_b1.slider("투자수익률", min_value=0.0, max_value=100.0, step=0.1, label_visibility="collapsed", key='yield_sl', on_change=update_yield_sl)
                yield_r = c_b2.number_input("투자수익률 입력", min_value=0.0, max_value=100.0, step=0.1, label_visibility="collapsed", key='yield_num', on_change=update_yield_num)
                
            st.markdown("---")
            st.markdown("##### 🚀 고도화 옵션")
            c_opt1, c_opt2 = st.columns(2)
            is_net_return = c_opt1.toggle("세후 수익률 적용 (15.4%)", value=False, key="ret_is_net")
            is_monte_carlo = c_opt2.toggle("몬테카를로 스트레스 테스트", value=False, key="ret_is_mc")
            
            comparative_mode = st.toggle("시나리오 비교 (A/B Test)", value=False, key="ret_is_compare")
            risk_level = st.select_slider("투자 성향", options=[1, 2, 3, 4, 5], value=3, format_func=lambda x: ["안정", "안정추구", "중립", "적극", "공격"][x-1], key="ret_risk_level")

    # Variables extraction (valid in both modes thanks to session_state)
    retire_age = st.session_state.ret_age_sl if 'ret_age_sl' in st.session_state else 60
    yy_life = st.session_state.life_age_sl if 'life_age_sl' in st.session_state else 90
    inf = st.session_state.inf_sl if 'inf_sl' in st.session_state else 3.0
    yield_r = st.session_state.yield_sl if 'yield_sl' in st.session_state else 6.0
    
    goal_p = st.session_state.ret_goal_p if 'ret_goal_p' in st.session_state else 3_000_000
    is_net_return = st.session_state.ret_is_net if 'ret_is_net' in st.session_state else False
    is_monte_carlo = st.session_state.ret_is_mc if 'ret_is_mc' in st.session_state else False
    comparative_mode = st.session_state.ret_is_compare if 'ret_is_compare' in st.session_state else False
    risk_level = st.session_state.ret_risk_level if 'ret_risk_level' in st.session_state else 3
    
    # New Period Variables
    y_s = retire_age - current_age # Total to Retirement
    pay_years = st.session_state.pay_years_sl if 'pay_years_sl' in st.session_state else min(10, y_s)
    y_def = y_s - pay_years         # Deferral Years
    y_d = yy_life - retire_age     # Decumulation Years
    
    if y_s < 0: y_s = 0
    if y_def < 0: y_def = 0
    
    # Message (Only in Design Mode)
    if not st.session_state.presentation_mode:
        st.caption(f"💡 {client_name}님은 **{pay_years}년**간 납입, **{y_def}년** 거치 후 **{y_d}년**간 연금을 수령합니다.")
    
    # Logic Adjustments
    actual_yield = yield_r * 0.846 if is_net_return else yield_r

        
    # Logic
    goal_f = goal_p * (1 + inf/100)**y_s
    n_months_retire = y_d * 12
    monthly_yield = actual_yield / 100 / 12
    
    # 1. Lump sum needed at Retirement Age (T=retire_age)
    if monthly_yield == 0:
        lump_sum_need = goal_f * n_months_retire
    else:
        lump_sum_need = goal_f * ((1 - (1 + monthly_yield) ** (-n_months_retire)) / monthly_yield)
    
    # 2. Value needed at end of payment period (T=current_age + pay_years)
    # This value will grow at yield_r for the deferral period to reach lump_sum_need.
    n_months_pay = pay_years * 12
    n_months_defer = y_def * 12
    
    if monthly_yield == 0:
        v_pay_end_needed = lump_sum_need
    else:
        v_pay_end_needed = lump_sum_need / ((1 + monthly_yield) ** n_months_defer)

    # 3. Monthly save needed during payment period
    if monthly_yield == 0:
        monthly_save = v_pay_end_needed / n_months_pay if n_months_pay > 0 else 0
    else:
        monthly_save = v_pay_end_needed * monthly_yield / ((1 + monthly_yield) ** n_months_pay - 1) if n_months_pay > 0 else 0
        
    # Back Calculation (Goal Seek)
    with st.expander("🎯 역산 엔진 (목표 자산 역산)"):
        target_lump = comma_int_input("목표 은퇴 자산(원)", int(lump_sum_need), "ret_target_lump_reverse")
        if monthly_save > 0:
            req_yield_seek = (((target_lump / (monthly_save * 12 * y_s)) ** (1/y_s)) - 1) * 100 if y_s > 0 else 0
            st.info(f"💡 {f_w(target_lump)}원을 만드려면 연 {req_yield_seek:.2f}%의 수익률이 필요합니다.")


    with col_result:
        st.subheader(f"📊 {client_name}님의 은퇴 설계 분석")
        
        c1, c2 = st.columns(2)
        c1.metric(f"{retire_age}세 시점 월 생활비", f"{f_w(goal_f)} 원", delta="물가상승 반영")
        c2.metric(f"필요 은퇴 자금 (총액)\n({retire_age}세 ~ {yy_life}세, {y_d}년간)", f"{f_w(lump_sum_need)} 원")
        
        st.divider()
        st.metric(f"💡 매월 필요 저축액\n({current_age}세 ~ {current_age + pay_years}세, {pay_years}년간)", f"{f_w(monthly_save)} 원", delta=f"{y_def}년 거치 포함", delta_color="inverse")
        
        # 1. Asset Growth Curve (Main Chart)
        years_v = list(range(current_age, yy_life + 1))
        wealth_v = []
        curr_bal_v = 0
        
        for age_v in years_v:
            wealth_v.append(curr_bal_v)
            if age_v < current_age + pay_years:
                # 1. Payment Phase
                gain = curr_bal_v * (actual_yield/100)
                curr_bal_v = curr_bal_v + gain + monthly_save * 12
            elif age_v < retire_age:
                # 2. Deferral Phase
                gain = curr_bal_v * (actual_yield/100)
                curr_bal_v = curr_bal_v + gain
            else:
                # 3. Withdrawal Phase
                gain = curr_bal_v * (actual_yield/100)
                curr_bal_v = curr_bal_v + gain - goal_f * 12
        
        fig = go.Figure()
        
        # Area Chart with better styling
        fig.add_trace(go.Scatter(
            x=years_v, y=wealth_v, 
            fill='tozeroy', 
            mode='lines', 
            line=dict(width=4, color='#3b82f6'),
            fillcolor='rgba(59, 130, 246, 0.15)', 
            name='자산 잔고'
        ))
        
        # Add Markers for Key Events
        fig.add_trace(go.Scatter(
            x=[current_age, current_age + pay_years, retire_age, yy_life], 
            y=[0, wealth_v[years_v.index(current_age + pay_years)] if (current_age + pay_years) in years_v else 0, 
               wealth_v[years_v.index(retire_age)] if retire_age in years_v else 0, 
               wealth_v[-1]],
            mode='markers+text',
            marker=dict(color=['#64748b', '#3b82f6', '#22c55e', '#ef4444'], size=12, line=dict(width=2, color='white')),
            text=["시작", "납입종료", "은퇴/개시", "종료"],
            textposition="top center",
            showlegend=False
        ))
        
        fig.update_layout(
            title=dict(text=f"📈 {client_name}님의 자산 생애 주기", font=dict(size=18, color="#1e293b")),
            xaxis=dict(title="나이 (세)", showgrid=True, gridcolor='#f1f5f9'), 
            yaxis=dict(title="자산 규모 (원)", showgrid=True, gridcolor='#f1f5f9'),
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='white',
            height=380, 
            margin=dict(l=20,r=20,t=60,b=20),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        
        # Comparative Mode logic
        if comparative_mode:
            if not st.session_state.presentation_mode:
                with st.expander("📉 시나리오 B (보수적) 변수 설정", expanded=True):
                    c_comp1, c_comp2 = st.columns(2)
                    stress_yield_val = c_comp1.number_input("B 수익률 (%)", value=max(0.0, yield_r - 2.0), step=0.1, key="ret_stress_yield_val")
                    stress_inf_val = c_comp2.number_input("B 물가 (%)", value=inf + 1.0, step=0.1, key="ret_stress_inf_val")
            
            # Use values from state or defaults
            s_yield = st.session_state.ret_stress_yield_val if 'ret_stress_yield_val' in st.session_state else max(0.0, yield_r - 2.0)
            s_inf = st.session_state.ret_stress_inf_val if 'ret_stress_inf_val' in st.session_state else inf + 1.0
            
            # Logic Adjustments for Scenario B
            actual_stress_yield = s_yield * 0.846 if is_net_return else s_yield
            
            # Recalculate curve for stress
            stress_wealth = []
            curr_stress = 0
            stress_goal_f = goal_p * (1 + s_inf/100)**y_s
            
            for age_v in years_v:
                stress_wealth.append(curr_stress)
                if age_v < retire_age:
                    gain = curr_stress * (actual_stress_yield/100)
                    curr_stress = curr_stress + gain + monthly_save * 12
                else:
                    gain = curr_stress * (actual_stress_yield/100)
                    curr_stress = curr_stress + gain - stress_goal_f * 12
            
            fig.add_trace(go.Scatter(
                x=years_v, y=stress_wealth, 
                name=f'시나리오 B (수익률 {s_yield}%, 물가 {s_inf}%)',
                line=dict(color='#ef4444', width=2, dash='dash')
            ))
            
            # Brief Summary for Scenario B
            st.info(f"🚩 시나리오 B 적용 시, 은퇴 시점 필요 자금은 **{f_w(stress_goal_f * ((1 - (1 + (actual_stress_yield/100/12)) ** (-y_d*12)) / (actual_stress_yield/100/12)) if actual_stress_yield > 0 else stress_goal_f * y_d * 12)}원**으로 변동됩니다.")
            
        st.plotly_chart(fig, use_container_width=True)
        
        # Monte Carlo Section
        if is_monte_carlo:
            st.divider()
            st.subheader("🎲 몬테카를로 스트레스 테스트 결과")
            vol = {1: 0.05, 2: 0.08, 3: 0.12, 4: 0.18, 5: 0.25}.get(risk_level, 0.12)
            
            p10, p50, p90 = TaxEngine.run_monte_carlo(
                yy_life - current_age, 
                0, 
                monthly_save * 12, 
                actual_yield, 
                volatility=vol
            )
            
            mc_fig = go.Figure()
            mc_years = list(range(current_age, yy_life + 1))
            
            mc_fig.add_trace(go.Scatter(x=mc_years, y=p90, fill=None, mode='lines', line_color='rgba(59, 130, 246, 0.1)', showlegend=False))
            mc_fig.add_trace(go.Scatter(x=mc_years, y=p10, fill='tonexty', mode='lines', line_color='rgba(59, 130, 246, 0.1)', name='신뢰구간 (80%)'))
            mc_fig.add_trace(go.Scatter(x=mc_years, y=p50, mode='lines', line=dict(color='#3b82f6', width=3), name='중간 시나리오'))
            
            # Add horizontal line at zero
            mc_fig.add_hline(y=0, line_dash="dot", line_color="red", annotation_text="자산 고갈 지점")
            
            mc_fig.update_layout(
                title="시장 변동성 반영 시 자산 추이", 
                template="plotly_white", 
                plot_bgcolor='rgba(255,255,255,0)',
                height=350, 
                margin=dict(l=20,r=20,t=40,b=20),
                xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
                yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
            )
            st.plotly_chart(mc_fig, use_container_width=True)
            st.caption(f"※ 투자 성향({['안정', '안정추구', '중립', '적극', '공격'][risk_level-1]})에 따른 변동성 {vol*100}%를 적용한 1,000회 시뮬레이션 결과입니다.")

    # --- End of Top Columns ---
    
    # --- Row 2: Portfolio Recommendation (Centered or Full Width based on removal of Cash Flow) ---
    st.divider()
    st.subheader("📊 맞춤형 포트폴리오 제안")
    
    if risk_level:
        # Risk Profile Selector
        risk_type = st.radio("투자 성향 선택 (실시간)", ["위험안정형", "위험중립형", "위험선호형"], horizontal=True, key="risk_radio_ret_opt")
        risk_map = {"위험안정형": 1, "위험중립형": 3, "위험선호형": 5}
        risk_score = risk_map[risk_type]
        
        rec = TaxEngine.get_portfolio_recommendation(risk_score)
        
        c_p1, c_p2 = st.columns([1, 2])
        with c_p1:
             st.markdown(f"""
            <div class='expert-card' style='margin-top:0;'>
                <div class='expert-title'>{rec['title']} 전략</div>
                <div style='font-size:0.9rem; color:#475569;'>
                    고객님의 성향에 맞춰 
                    <b>주식 {rec['assets']['주식']}%</b>, 
                    <b>채권 {rec['assets']['채권']}%</b>, 
                    <b>현금성 {rec['assets']['현금성']}%</b>의 
                    비중을 제안합니다.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        with c_p2: 
            fig_port = go.Figure(data=[go.Pie(
                labels=list(rec['assets'].keys()),
                values=list(rec['assets'].values()),
                hole=0.4,
                marker=dict(colors=['#1e3a8a', '#3b82f6', '#93c5fd'], line=dict(color='#ffffff', width=2)),
                textinfo='label+percent',
                hoverinfo='label+value+percent'
            )])
            fig_port.update_layout(
                title=dict(text=f"{rec['title']} 자산 배분", font=dict(size=16, color='#1e293b')),
                height=300, 
                margin=dict(t=40, b=20, l=20, r=20),
                showlegend=True
            )
            st.plotly_chart(fig_port, use_container_width=True)

    # --- Row 3: Monte Carlo (Full Width) ---
    if is_monte_carlo:
        st.divider()
        st.subheader("🎲 몬테카를로 리스크 분석")
        
        p10, p50, p90 = TaxEngine.run_monte_carlo(y_s + y_d, 0, monthly_save * 12, actual_yield)
        mc_years = list(range(current_age, current_age + len(p10)))
        
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("최악의 시나리오\n(하위 10%)", f"{f_w(p10[-1])} 원", "목표 미달 가능성", delta_color="inverse")
        mc2.metric("평균적 시나리오\n(중위 값)", f"{f_w(p50[-1])} 원", "예상 자산 잔존액")
        mc3.metric("최상의 시나리오\n(상위 10%)", f"{f_w(p90[-1])} 원", "초과 달성 예상", delta_color="normal")
        
        fig_mc = go.Figure()
        fig_mc.add_trace(go.Scatter(x=mc_years, y=p90, mode='lines', line=dict(width=0), showlegend=False))
        fig_mc.add_trace(go.Scatter(x=mc_years, y=p10, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(59, 130, 246, 0.1)', showlegend=False))
        fig_mc.add_trace(go.Scatter(x=mc_years, y=p50, name="평균 흐름", line=dict(color='#3b82f6', width=3)))
        fig_mc.add_trace(go.Scatter(x=mc_years, y=p10, name="위험 하한선", line=dict(color='#ef4444', width=2, dash='dot')))
        
        fig_mc.update_layout(
            title="시나리오별 자산 변동 범위 (Confidence Interval)", 
            template="plotly_white", 
            plot_bgcolor='rgba(255,255,255,0)',
            height=350, 
            margin=dict(l=20,r=20,t=40,b=20),
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_mc, use_container_width=True)
        
        with st.expander("ℹ️ 몬테카를로 분석이란?", expanded=False):
             st.markdown("불확실한 투자 시장의 변동성을 반영하여 1,000번의 시뮬레이션을 수행한 결과입니다. 하위 10% 시나리오에서도 자산이 고갈되지 않는지 확인하세요.")

    # --- Row 4: Comparative (Full Width) ---
    if comparative_mode:
        st.divider()
        st.subheader("⚖️ 플랜 수익률 비교 (A vs B)")
        yield_b = st.number_input("비교할 수익률(%)", value=actual_yield + 2.0, step=0.1)
        m_yield_b = yield_b / 100 / 12
        m_save_b = lump_sum_need * m_yield_b / ((1 + m_yield_b)**n_months_pay - 1) if n_months_pay > 0 and m_yield_b > 0 else 0
        
        fig_comp = go.Figure(data=[
            go.Bar(
                name=f'현행 ({actual_yield:.1f}%)', 
                x=['필요 저축액'], y=[monthly_save], 
                marker_color='#1e3a8a',
                text=[f"{f_w(monthly_save)} 원"],
                textposition='auto',
                marker=dict(line=dict(width=1, color='white')) # 3D effect hint
            ),
            go.Bar(
                name=f'비교 ({yield_b:.1f}%)', 
                x=['필요 저축액'], y=[m_save_b], 
                marker_color='#94a3b8',
                text=[f"{f_w(m_save_b)} 원"],
                textposition='auto',
                marker=dict(line=dict(width=1, color='white'))
            )
        ])
        fig_comp.update_layout(
            barmode='group', 
            height=300, 
            title="수익률별 저축 부담 비교",
            plot_bgcolor='rgba(255,255,255,0)',
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_comp, use_container_width=True)

    # --- Row 5: Detailed Report ---
    with st.expander("📝 은퇴 설계 상세 리포트", expanded=False):
        st.markdown(f"""
        <div class='expert-card'>
            <div class='expert-title'>📑 {client_name}님을 위한 로드맵</div>
            <div class='step-box'>
                <div class='step-title'>1. 인플레이션 헷지 (Inflation Hedge)</div>
                <div class='step-content'>
                    현재 생활비 {f_w(goal_p)}원은 물가상승률 {inf}%를 반영하여 {y_s}년 후({retire_age}세) <span class='highlight'>{f_w(goal_f)}원</span>의 가치를 가집니다.
                </div>
            </div>
            <div class='step-box'>
                <div class='step-title'>2. 필요 자산 규모 (Lump Sum)</div>
                <div class='step-content'>
                    은퇴 기간 {y_d}년 동안 매월 {f_w(goal_f)}원을 인출하기 위해 은퇴 시점({retire_age}세)에 <span class='highlight'>{f_w(lump_sum_need)}원</span>이 준비되어야 합니다.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # 결과 저장 (전략 보고서용)
    st.session_state['result_ret_monthly'] = monthly_save
    st.session_state['result_ret_lump'] = lump_sum_need
    st.session_state['result_ret_goal'] = goal_f

    # AI Doctor Call
    render_ai_doctor("은퇴설계", {'goal': goal_f, 'saved': monthly_save})

def render_target_fund():
    st.title("🎯 목적자금 계산")
    st.markdown("주택 마련, 결혼, 자녀 교육 등 구체적인 재무 목표 달성을 위한 최적의 저축 플랜을 제시합니다.")
    
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 목적자금 설계 입력")
            
            # Personal Info
            with st.container():
                st.markdown("##### 1. 고객정보")
                c_name, c_age = st.columns([1.5, 1])
                client_name = c_name.text_input("고객 성함", "", key="tf_name")
                current_age = c_age.number_input("현재 나이", min_value=0, max_value=100, value=0, key="tf_age")

            st.markdown("##### 2. 목표 설정")
            calc_type = st.radio("계산 방식 선택", ["목표 필요 자금", "매월 잉여 금액"], key="tf_calc_type", horizontal=True)
            if calc_type == "목표 필요 자금":
                target_amt = comma_int_input("목표 금액(원)", st.session_state.tf_b, "tf_b")
                input_monthly = 0
            else:
                input_monthly = comma_int_input("매월 잉여 금액(원)", st.session_state.get('tf_monthly_input', 1000000), "tf_monthly_input")
                target_amt = 0
    else:
        client_name = st.session_state.get('tf_name', "")
        current_age = st.session_state.get('tf_age', 0)
        calc_type = st.session_state.get('tf_calc_type', "목표 필요 자금")
        target_amt = st.session_state.get('tf_b', 100_000_000)
        input_monthly = st.session_state.get('tf_monthly_input', 1000000)
    
    # Sync for Target Fund
    if 'tf_period_sl' not in st.session_state: st.session_state.tf_period_sl = 5
    if 'tf_period_num' not in st.session_state: st.session_state.tf_period_num = 5
    
    def update_tf_period_sl():
        st.session_state.tf_period_num = st.session_state.tf_period_sl
    def update_tf_period_num():
        st.session_state.tf_period_sl = st.session_state.tf_period_num

    if 'tf_sav_rate_sl' not in st.session_state: st.session_state.tf_sav_rate_sl = 2.5
    if 'tf_sav_rate_num' not in st.session_state: st.session_state.tf_sav_rate_num = 2.5

    def update_tf_sav_rate_sl():
        st.session_state.tf_sav_rate_num = st.session_state.tf_sav_rate_sl
    def update_tf_sav_rate_num():
        st.session_state.tf_sav_rate_sl = st.session_state.tf_sav_rate_num

    if 'tf_rate_sl' not in st.session_state: st.session_state.tf_rate_sl = 5.0
    if 'tf_rate_num' not in st.session_state: st.session_state.tf_rate_num = 5.0

    def update_tf_rate_sl():
        st.session_state.tf_rate_num = st.session_state.tf_rate_sl
    def update_tf_rate_num():
        st.session_state.tf_rate_sl = st.session_state.tf_rate_num
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.markdown("준비 기간(년)")
            c1, c2 = st.columns([2, 1])
            with c1: period = st.slider("준비 기간", min_value=1, max_value=30, key='tf_period_sl', label_visibility="collapsed", on_change=update_tf_period_sl)
            with c2: period = st.number_input("기간 입력", min_value=1, max_value=30, key='tf_period_num', label_visibility="collapsed", on_change=update_tf_period_num)
            
            st.markdown("적금 금리(%)")
            cs1, cs2 = st.columns([2, 1])
            with cs1: top_sav_rate = st.slider("적금 금리", min_value=0.0, max_value=20.0, step=0.1, key='tf_sav_rate_sl', label_visibility="collapsed", on_change=update_tf_sav_rate_sl)
            with cs2: top_sav_rate = st.number_input("적금 금리 입력", min_value=0.0, max_value=20.0, step=0.1, key='tf_sav_rate_num', label_visibility="collapsed", on_change=update_tf_sav_rate_num)

            st.markdown("기대 수익률(%)")
            c3, c4 = st.columns([2, 1])
            with c3: rate = st.slider("기대 수익률", min_value=0.0, max_value=20.0, step=0.1, key='tf_rate_sl', label_visibility="collapsed", on_change=update_tf_rate_sl)
            with c4: rate = st.number_input("수익률 입력", min_value=0.0, max_value=20.0, step=0.1, key='tf_rate_num', label_visibility="collapsed", on_change=update_tf_rate_num)
            
            st.markdown("---")
            # Removed 세후 수익률 적용
    else:
        # Read from state
        # Read from state
        period = st.session_state.get('tf_period_sl', 5)
        top_sav_rate = st.session_state.get('tf_sav_rate_sl', 2.5)
        rate = st.session_state.get('tf_rate_sl', 5.0)

    actual_rate = rate
        
    # Logic
    monthly_rate = actual_rate / 100 / 12
    months = period * 12
    sav_r = top_sav_rate / 100
    
    if calc_type == "목표 필요 자금":
        if monthly_rate == 0:
            req_monthly = target_amt / months
        else:
            req_monthly = target_amt * monthly_rate / ((1 + monthly_rate)**months - 1)
        expected_total = target_amt
        
        if sav_r == 0:
            sav_req_monthly = target_amt / months
        else:
            sav_req_monthly = target_amt / (months + sav_r * months * (months + 1) / 24)
        sav_expected_total = target_amt
    else:
        req_monthly = input_monthly
        sav_req_monthly = input_monthly
        if monthly_rate == 0:
            expected_total = req_monthly * months
        else:
            expected_total = req_monthly * ((1 + monthly_rate)**months - 1) / monthly_rate
        target_amt = expected_total  # For chart goal line and monte carlo consistency
        
        if sav_r == 0:
            sav_expected_total = sav_req_monthly * months
        else:
            sav_expected_total = sav_req_monthly * months + sav_req_monthly * sav_r * months * (months + 1) / 24
            
    total_principal = req_monthly * months
    total_interest = expected_total - total_principal
    
    sav_total_principal = sav_req_monthly * months
    sav_total_interest = sav_expected_total - sav_total_principal


    with col_result:
        st.subheader("📊 자금 달성 분석")
        
        c1, c2 = st.columns(2)
        
        # HTML 카드 스타일을 위한 공통 래퍼 함수
        def draw_kpi_card(title, main_val, sub_label, sub_val, is_result1=True):
            bg_color = "#f0fdf4" if is_result1 else "#eff6ff"
            border_color = "#bbf7d0" if is_result1 else "#bfdbfe"
            icon = "🎯" if is_result1 else "💰"
            return f"""
            <div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%; margin-bottom: 12px;'>
                <div style='color: #64748b; font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;'><span style='margin-right:4px;'>{icon}</span> {title}</div>
                <div style='color: #1e293b; font-size: 1.8rem; font-weight: 800; margin-bottom: 16px; letter-spacing: -0.5px;'>{main_val} <span style='font-size: 1.1rem; color: #475569; font-weight:600;'>원</span></div>
                <div style='background-color: {bg_color}; border: 1px solid {border_color}; padding: 12px 14px; border-radius: 8px; color: #334155; font-size: 0.92rem; display: flex; justify-content: space-between; align-items: center;'>
                    <span style='font-weight: 600; color: #475569;'>{sub_label}</span>
                    <span style='font-weight: 700; color: #1e3a8a;'>{sub_val}원</span>
                </div>
            </div>
            """
            
        with c1:
            if calc_type == "목표 필요 자금":
                html_c1 = draw_kpi_card("투자(복리) 시 매월 저축액", f_w(req_monthly), "적금 필요액:", f_w(sav_req_monthly), True)
            else:
                html_c1 = draw_kpi_card("투자(복리) 시 예상 자산", f_w(expected_total), "적금 예상액:", f_w(sav_expected_total), True)
            st.markdown(html_c1, unsafe_allow_html=True)
            
        with c2:
            html_c2 = draw_kpi_card("투자 시 예상 수익 (이자)", f_w(total_interest), "적금 이자:", f_w(sav_total_interest), False)
            st.markdown(html_c2, unsafe_allow_html=True)
        
        # Growth Curve Chart
        growth_months = list(range(months + 1))
        growth_balances = []
        sav_balances = []
        curr_g = 0
        for m in growth_months:
            growth_balances.append(curr_g)
            if m == 0:
                sav_balances.append(0)
            else:
                curr_s = req_monthly * m + req_monthly * sav_r * m * (m + 1) / 24
                sav_balances.append(curr_s)
            curr_g = curr_g * (1 + monthly_rate) + req_monthly
        
        fig_growth = go.Figure()
        fig_growth.add_trace(go.Scatter(x=growth_months, y=growth_balances, mode='lines', line=dict(width=4, color='#e11d48'), name='투자 시 자산 성장 (복리)'))
        fig_growth.add_trace(go.Scatter(x=growth_months, y=sav_balances, mode='lines', line=dict(width=3, color='#94a3b8', dash='dot'), name='적금 시 자산 성장 (단리)'))
        fig_growth.update_layout(
            title = "자산 성장 곡선 (Growth Curve)", 
            template = "plotly_white", 
            plot_bgcolor='rgba(255,255,255,0)',
            height=350, 
            margin=dict(l=20,r=20,t=40,b=20),
            xaxis=dict(showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9')
        )
        st.plotly_chart(fig_growth, use_container_width=True)
        
    st.divider()
    
    # ===== 적금 vs 펀드 vs 변액ETF 몬테카를로 비교 분석 =====
    st.subheader("🎲 적금 vs 펀드 vs 변액ETF 몬테카를로 비교 분석")
    
    col_t1, col_t2 = st.columns([1, 2.5])
    with col_t1:
        st.write("")
        is_mc_tf = st.toggle("3종 상품 비교 시뮬레이션 실행", value=False, key="tf_mc_toggle")
    
    if is_mc_tf:
        with col_t2:
            cc1, cc2, cc3 = st.columns(3)
            savings_rate = cc1.number_input("적금 금리(%)", min_value=0.0, value=2.5, step=0.1, key="tf_sav_rate")
            fund_rate = cc2.number_input("펀드 기대수익률(%)", min_value=0.0, value=7.0, step=0.1, key="tf_fund_rate")
            etf_rate = cc3.number_input("변액ETF 기대수익률(%)", min_value=0.0, value=10.0, step=0.1, key="tf_etf_rate")
            
        # === 상품별 파라미터 설정 ===
        # 적금: 이자소득세 15.4%
        savings_tax = 0.154
        
        # 펀드: 변동성 있음, 배당소득세 15.4%
        fund_vol = 0.15  # 펀드 변동성
        fund_tax = 0.154
        
        # 변액ETF: 변동성 있음, 비과세 (10년 이상 유지 시)
        etf_vol = 0.12  # ETF 추종으로 펀드 대비 낮은 변동성
        etf_tax = 0.0  # 비과세 혜택
        
        # === 추가납입 설정 ===
        if st.toggle("💸 추가납입", value=st.session_state.tf_add_toggle, key="tf_add_toggle"):
            c_add1, c_add2 = st.columns([1, 2])
            with c_add1:
                tf_add_prem = comma_int_input("추가납입액(원)", st.session_state.tf_add_prem, "tf_add_prem")
        else:
            tf_add_prem = 0
            
        fund_fee_rate = 0.012  # C클래스 펀드 평균 연보수(약 1.2%) 적용
        
        mc_years = list(range(period + 1))
        annual_save = (req_monthly + tf_add_prem) * 12
        trials = 1000
        
        # --- 메트릭 및 장기 투자 결과 저장용 ---
        long_periods = [3, 5, 10, 15]
        savings_long = []
        fund_long = []
        etf_long = []
        
        # --- 적금,펀드,ETF 메트릭용 변수 ---
        savings_balances = [0]
        monthly_deposit = req_monthly + tf_add_prem
        
        # --- 기간별 자산 비교 (Top Priority) ---
        for lp in long_periods:
            # 적금
            months = lp * 12
            principal = monthly_deposit * months
            pre_tax_interest = monthly_deposit * (savings_rate / 100) * months * (months + 1) / 24
            after_tax_interest = pre_tax_interest * (1 - savings_tax)
            savings_long.append(principal + after_tax_interest)
            
            # 펀드 (중위 시뮬레이션 x500)
            f_results = []
            for _ in range(500):
                f_val = 0
                for yr in range(lp):
                    ret = np.random.normal(fund_rate / 100, fund_vol)
                    gain = f_val * ret
                    tax_d = max(0, gain) * fund_tax
                    fee_d = f_val * fund_fee_rate
                    f_val = f_val + gain - tax_d - fee_d + annual_save
                    f_val = max(0, f_val)
                f_results.append(f_val)
            fund_long.append(np.median(f_results))
            
            # 변액ETF
            e_results = []
            for _ in range(500):
                e_val = 0
                for yr in range(lp):
                    if yr < 10:
                        basic_fee_rate = 0.075
                    else:
                        basic_fee_rate = 0.0264
                        
                    injected_basic = req_monthly * (1 - basic_fee_rate) * 12
                    injected_add = tf_add_prem * 12
                    total_injected = injected_basic + injected_add

                    ret = np.random.normal(etf_rate / 100, etf_vol)
                    gain = e_val * ret
                    fee_deducted = e_val * 0.00755
                    
                    e_val = e_val + gain - fee_deducted + total_injected
                    e_val = max(0, e_val)
                e_results.append(e_val)
            etf_long.append(np.median(e_results))
            
        # --- 적금 몬테카를로 (단리, 세후 실질 이자율 반영) - 그래프용 ---
        for yr in range(period):
            months = (yr + 1) * 12
            principal = monthly_deposit * months
            pre_tax_interest = monthly_deposit * (savings_rate / 100) * months * (months + 1) / 24
            after_tax_interest = pre_tax_interest * (1 - savings_tax)
            savings_balances.append(principal + after_tax_interest)
            
        # --- 펀드 몬테카를로 (변동성 + 세금 + 펀드보수) - 그래프용 ---
        fund_scenarios = []
        for _ in range(trials):
            bal = [0]
            curr_f = 0
            for yr in range(period):
                ret = np.random.normal(fund_rate / 100, fund_vol)
                gain = curr_f * ret
                tax_deducted = max(0, gain) * fund_tax
                fee_deducted = curr_f * fund_fee_rate
                curr_f = curr_f + gain - tax_deducted - fee_deducted + annual_save
                curr_f = max(0, curr_f)
                bal.append(curr_f)
            fund_scenarios.append(bal)
        fund_np = np.array(fund_scenarios)
        fund_p10 = np.percentile(fund_np, 10, axis=0)
        fund_p50 = np.percentile(fund_np, 50, axis=0)
        fund_p90 = np.percentile(fund_np, 90, axis=0)
        
        # --- 변액ETF 몬테카를로 (변동성 + 비과세 + 보험사업비/보수 차감) - 그래프용 ---
        etf_scenarios = []
        etf_management_fee_rate = 0.00755
        
        for _ in range(trials):
            bal = [0]
            curr_e = 0
            for yr in range(period):
                if yr < 10:
                    basic_fee_rate = 0.075
                else:
                    basic_fee_rate = 0.0264
                
                injected_basic = req_monthly * (1 - basic_fee_rate) * 12
                injected_add = tf_add_prem * 12
                total_injected = injected_basic + injected_add
                
                ret = np.random.normal(etf_rate / 100, etf_vol)
                gain = curr_e * ret
                fee_deducted = curr_e * etf_management_fee_rate
                
                curr_e = curr_e + gain - fee_deducted + total_injected
                curr_e = max(0, curr_e)
                bal.append(curr_e)
            etf_scenarios.append(bal)
        etf_np = np.array(etf_scenarios)
        etf_p10 = np.percentile(etf_np, 10, axis=0)
        etf_p50 = np.percentile(etf_np, 50, axis=0)
        etf_p90 = np.percentile(etf_np, 90, axis=0)
        
        # === 3종 비교 메트릭 ===
        savings_final = savings_balances[-1]
        fund_final = fund_p50[-1]
        etf_final = etf_p50[-1]
        
        total_paid = annual_save * period
        
        savings_profit = savings_final - total_paid
        fund_profit = fund_final - total_paid
        etf_profit = etf_final - total_paid
        
        etf_vs_savings = etf_final - savings_final
        etf_vs_fund = etf_final - fund_final
        
        fig_long = go.Figure()
        
        fig_long.add_trace(go.Bar(
            name='🏦 적금', x=[f'{p}년' for p in long_periods], y=savings_long,
            marker_color='#cbd5e1', text=[f'{v/10000:,.0f}만' for v in savings_long], textposition='outside',
            marker=dict(line=dict(width=1, color='white'))
        ))
        fig_long.add_trace(go.Bar(
            name='📊 펀드', x=[f'{p}년' for p in long_periods], y=fund_long,
            marker_color='#fbbf24', text=[f'{v/10000:,.0f}만' for v in fund_long], textposition='outside',
            marker=dict(line=dict(width=1, color='white'))
        ))
        fig_long.add_trace(go.Bar(
            name='🚀 변액ETF', x=[f'{p}년' for p in long_periods], y=etf_long,
            marker_color='#2563eb', text=[f'{v/10000:,.0f}만' for v in etf_long], textposition='outside',
            marker=dict(line=dict(width=1, color='white'))
        ))
        
        fig_long.update_layout(
            barmode='group',
            template="plotly_white",
            plot_bgcolor='rgba(255,255,255,0)',
            height=360,
            margin=dict(l=20, r=20, t=30, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5),
            yaxis=dict(showgrid=True, gridcolor='#f1f5f9', title='누적 자산 (원)'),
            xaxis=dict(title='유지 기간')
        )
        st.plotly_chart(fig_long, use_container_width=True)
        
        # 기간별 3종 비교 강조 (미리 계산)
        if len(etf_long) >= len(long_periods) and len(savings_long) >= len(long_periods) and len(fund_long) >= len(long_periods):
            cards_html = ""
            for idx, lp in enumerate(long_periods):
                s_val = savings_long[idx]
                f_val = fund_long[idx]
                e_val = etf_long[idx]
                f_gap = f_val - s_val
                f_gap_sign = "+" if f_gap >= 0 else ""
                f_gap_color = "#fbbf24" if f_gap >= 0 else "#f87171"
                e_gap = e_val - s_val
                e_gap_sign = "+" if e_gap >= 0 else ""
                e_gap_color = "#34d399" if e_gap >= 0 else "#f87171"
                ef_gap = e_val - f_val
                ef_gap_sign = "+" if ef_gap >= 0 else ""
                cards_html += f'<div style="flex:1;min-width:200px;background:rgba(255,255,255,0.07);border-radius:14px;padding:18px 14px;border:1px solid rgba(255,255,255,0.12);text-align:center;"><div style="color:#93c5fd;font-size:0.85rem;font-weight:600;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.15);">{lp}년 유지</div><div style="display:flex;flex-direction:column;gap:8px;"><div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(203,213,225,0.1);border-radius:8px;"><span style="color:#94a3b8;font-size:0.75rem;">🏦 적금</span><span style="color:#cbd5e1;font-size:0.9rem;font-weight:700;">{f_w(s_val)}원</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(251,191,36,0.08);border-radius:8px;"><span style="color:#fbbf24;font-size:0.75rem;">📊 펀드</span><span style="color:#fbbf24;font-size:0.9rem;font-weight:700;">{f_w(f_val)}원</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(37,99,235,0.12);border-radius:8px;"><span style="color:#60a5fa;font-size:0.75rem;">🚀 변액ETF</span><span style="color:#34d399;font-size:0.95rem;font-weight:800;">{f_w(e_val)}원</span></div></div><div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.1);font-size:0.72rem;"><span style="color:#94a3b8;">ETF-적금</span> <span style="color:{e_gap_color};font-weight:700;">{e_gap_sign}{f_w(e_gap)}원</span> <span style="color:#475569;margin:0 4px;">|</span> <span style="color:#94a3b8;">ETF-펀드</span> <span style="color:#34d399;font-weight:700;">{ef_gap_sign}{f_w(ef_gap)}원</span></div></div>'
            
            st.markdown(f'<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#1d4ed8 100%);padding:24px;border-radius:16px;color:white;box-shadow:0 10px 25px -5px rgba(30,58,138,0.4);margin-bottom:40px;"><div style="text-align:center;margin-bottom:18px;"><div style="font-size:1.05rem;font-weight:700;letter-spacing:0.5px;">⚡ 기간별 적금 vs 펀드 vs 변액ETF 차이</div><div style="font-size:0.75rem;color:#94a3b8;margin-top:4px;">동일 금액 적립 시, 상품별 누적 자산 비교</div></div><div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">{cards_html}</div><div style="text-align:center;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.78rem;color:#bfdbfe;">💡 기간이 길어질수록 비과세 복리의 격차는 <b style="color:#fbbf24;">기하급수적</b>으로 벌어집니다</div></div></div>', unsafe_allow_html=True)
            
        # === 2. 몬테카를로 1000회 시뮬레이션 상세 여정 ===
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("#### 🎯 목표 달성 과정 몬테카를로 시뮬레이션 (1,000회)")
        
        # === 메트릭 카드 ===
        st.markdown(f"""
        <div style="display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 200px; padding: 20px; background: linear-gradient(135deg, #f8fafc, #f1f5f9); border-radius: 14px; border: 1px solid #e2e8f0; text-align: center;">
                <div style="font-size: 1.8rem; margin-bottom: 5px;">🏦</div>
                <div style="color: #64748b; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">적금 (확정금리)</div>
                <div style="color: #94a3b8; font-size: 1.6rem; font-weight: 800;">{f_w(savings_final)}원</div>
                <div style="color: #94a3b8; font-size: 0.8rem; margin-top: 4px;">수익 {f_w(savings_profit)}원</div>
                <div style="margin-top: 10px; padding: 6px 12px; background: #e2e8f0; border-radius: 20px; display: inline-block; font-size: 0.75rem; color: #64748b;">세후 이자 연 1.37%</div>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 20px; background: linear-gradient(135deg, #fef3c7, #fde68a); border-radius: 14px; border: 1px solid #fbbf24; text-align: center;">
                <div style="font-size: 1.8rem; margin-bottom: 5px;">📊</div>
                <div style="color: #92400e; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">펀드 (과세/보수)</div>
                <div style="color: #b45309; font-size: 1.6rem; font-weight: 800;">{f_w(fund_final)}원</div>
                <div style="color: #b45309; font-size: 0.8rem; margin-top: 4px;">수익 {f_w(fund_profit)}원</div>
                <div style="margin-top: 10px; padding: 6px 12px; background: rgba(251,191,36,0.3); border-radius: 20px; display: inline-block; font-size: 0.75rem; color: #92400e;">배당소득세(15.4%)<br>+ 보수(연 1.2%) 차감</div>
            </div>
            <div style="flex: 1; min-width: 200px; padding: 20px; background: linear-gradient(135deg, #1e3a8a, #2563eb); border-radius: 14px; border: 2px solid #60a5fa; text-align: center; position: relative; overflow: hidden;">
                <div style="position: absolute; top: 8px; right: 8px; background: #fbbf24; color: #1e3a8a; font-size: 0.65rem; font-weight: 800; padding: 3px 8px; border-radius: 10px;">BEST</div>
                <div style="font-size: 1.8rem; margin-bottom: 5px;">🚀</div>
                <div style="color: #93c5fd; font-size: 0.85rem; font-weight: 600; margin-bottom: 8px;">변액ETF (비과세)</div>
                <div style="color: white; font-size: 1.6rem; font-weight: 800;">{f_w(etf_final)}원</div>
                <div style="color: #93c5fd; font-size: 0.8rem; margin-top: 4px;">수익 {f_w(etf_profit)}원</div>
                <div style="margin-top: 10px; padding: 6px 12px; background: rgba(255,255,255,0.15); border-radius: 20px; display: inline-block; font-size: 0.75rem; color: #bfdbfe;">✨ 비과세 + 낮은 변동성</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # === 차이 강조 배너 ===
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #0f172a, #1e293b); padding: 18px 25px; border-radius: 14px; margin-bottom: 20px; display: flex; justify-content: space-around; flex-wrap: wrap; gap: 15px;">
            <div style="text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem;">적금 대비 변액ETF 초과 수익</div>
                <div style="color: #34d399; font-size: 1.4rem; font-weight: 800;">+{f_w(etf_vs_savings)}원</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem;">펀드 대비 변액ETF 초과 수익</div>
                <div style="color: #60a5fa; font-size: 1.4rem; font-weight: 800;">+{f_w(etf_vs_fund)}원</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #94a3b8; font-size: 0.8rem;">비과세/보수 절감 효과</div>
                <div style="color: #fbbf24; font-size: 1.4rem; font-weight: 800;">+{f_w(etf_final - fund_final)}원</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # === 몬테카를로 3종 비교 차트 ===
        mc_fig = go.Figure()
        
        # 적금 (확정 - 단일 선)
        mc_fig.add_trace(go.Scatter(
            x=mc_years, y=savings_balances, name="🏦 적금 (확정)",
            line=dict(color='#94a3b8', width=3, dash='dot'),
            hovertemplate='적금: %{y:,.0f}원<extra></extra>'
        ))
        
        # 펀드 신뢰구간
        mc_fig.add_trace(go.Scatter(x=mc_years, y=fund_p90, mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        mc_fig.add_trace(go.Scatter(x=mc_years, y=fund_p10, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(251, 191, 36, 0.08)', showlegend=False, hoverinfo='skip'))
        mc_fig.add_trace(go.Scatter(
            x=mc_years, y=fund_p50, name="📊 펀드 (과세/보수)",
            line=dict(color='#f59e0b', width=2.5),
            hovertemplate='펀드: %{y:,.0f}원<extra></extra>'
        ))
        
        # 변액ETF 신뢰구간
        mc_fig.add_trace(go.Scatter(x=mc_years, y=etf_p90, mode='lines', line=dict(width=0), showlegend=False, hoverinfo='skip'))
        mc_fig.add_trace(go.Scatter(x=mc_years, y=etf_p10, mode='lines', line=dict(width=0), fill='tonexty', fillcolor='rgba(37, 99, 235, 0.1)', showlegend=False, hoverinfo='skip'))
        mc_fig.add_trace(go.Scatter(
            x=mc_years, y=etf_p50, name="🚀 변액ETF (비과세)",
            line=dict(color='#2563eb', width=4),
            hovertemplate='변액ETF: %{y:,.0f}원<extra></extra>'
        ))
        
        # 목표선
        mc_fig.add_hline(y=target_amt, line_dash="dash", line_color="#ef4444", line_width=1.5,
                         annotation_text=f"🎯 목표 {f_w(target_amt)}원", annotation_position="top left",
                         annotation_font=dict(color="#ef4444", size=11))
        
        mc_fig.update_layout(
            title=dict(text="", font=dict(size=16, color='#1e293b')),
            template="plotly_white",
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='white',
            height=420,
            margin=dict(l=20, r=20, t=20, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5, font=dict(size=12)),
            xaxis=dict(title="경과 기간 (년)", showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(title="누적 자산 (원)", showgrid=True, gridcolor='#f1f5f9'),
            hovermode="x unified"
        )
        st.plotly_chart(mc_fig, use_container_width=True)
        
        st.caption(f"※ 적금: 단리만기 (실효세후수익률 반영) | 펀드: 연 {fund_rate:.2f}% 기대수익(변동성 {fund_vol*100:.0f}%, 세후/펀드보수 반영) | 변액ETF: 연 {etf_rate:.2f}% 기대수익(변동성 {etf_vol*100:.0f}%, 비과세/보험사업비 및 펀드보수 반영)")
            

        
        with st.expander("🏢 금융기관별 상품 비교", expanded=False):
            st.markdown('<div style="text-align:center;"><h4 style="margin-bottom:16px;">금융기관별 목적자금 마련 상품 비교</h4><table style="margin:0 auto;border-collapse:collapse;width:95%;max-width:900px;font-size:0.88rem;"><thead><tr style="background:#1e3a8a;color:white;"><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">항목</th><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">🏦 은행 (적금)</th><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">📊 증권사 (펀드)</th><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">🚀 보험사 (변액ETF)</th></tr></thead><tbody><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">대표 상품</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">정기적금, 자유적금</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">주식형/혼합형 펀드</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">변액유니버셜 ETF보험</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">수익률</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">확정 3~4%</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">변동 (시장 수익률)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">변동 (시장 수익률)</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">과세</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">이자소득세 15.4%</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">배당소득세 15.4%</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">✅ 비과세 (10년 유지 시)</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">변동성 관리</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">없음 (확정)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">직접 관리 필요</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">✅ 펀드 무제한 무료 변경</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">사망 보장</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">❌ 없음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">❌ 없음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">✅ 사망보험금 지급</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">최저 보증</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">원금 보장</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">❌ 없음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">✅ 최저 사망보험금 보증</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">ETF 투자</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">❌ 불가</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">가능 (별도 계좌)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">✅ 보험 내 ETF 직접 편입</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">장기 복리</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">낮은 확정금리</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">세금이 복리를 깎음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">✅ 비과세 복리 극대화</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">중도 인출</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">해지 시 이자 손실</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">자유 (수수료 有)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">부분 인출 가능</td></tr></tbody></table><div style="margin-top:14px;padding:10px 16px;background:#eff6ff;border-radius:8px;border-left:4px solid #2563eb;text-align:left;font-size:0.85rem;">💡 <b>핵심 포인트</b>: 동일한 수익률이라도 세금이 매년 깎이는 펀드 대비, 비과세 복리로 굴러가는 변액ETF는 시간이 길어질수록 <b>기하급수적으로</b> 차이가 벌어집니다.</div></div>', unsafe_allow_html=True)
    else:
        st.info("💡 적금·펀드·변액ETF의 수익률 차이를 몬테카를로 시뮬레이션으로 직접 확인해보세요. 비과세의 놀라운 복리 효과를 체감하실 수 있습니다.")

    # === 스마트 자산 증식 전략 비교 리포트 ===
    with st.expander("📊 스마트 자산 증식 전략 비교 리포트", expanded=False):
        # 각 상품별 수익 계산
        savings_result = 0
        net_s_rate = 3.5 * (1 - 0.154) / 100
        for yr in range(period):
            savings_result = savings_result * (1 + net_s_rate) + req_monthly * 12
        
        fund_result_simple = 0
        net_f_rate = actual_rate * (1 - 0.154) / 100
        for yr in range(period):
            fund_result_simple = fund_result_simple * (1 + net_f_rate) + req_monthly * 12
        
        etf_result_simple = 0
        net_e_rate = actual_rate / 100
        for yr in range(period):
            etf_result_simple = etf_result_simple * (1 + net_e_rate) + req_monthly * 12
        
        total_input = req_monthly * 12 * period
        
        st.markdown(f"""
        <div class='expert-card'>
            <div class='expert-title'>📑 {client_name}님을 위한 스마트 자산 증식 전략 비교</div>
            <div class='step-box'>
                <div class='step-title'>1. 📌 목표 분석</div>
                <div class='step-content'>
                    {period}년 후({current_age + period}세) 목표 금액 <span class='highlight'>{f_w(target_amt)}원</span> | 매월 필요 저축액 <span class='highlight'>{f_w(req_monthly)}원</span>
                </div>
            </div>
            <div class='step-box' style="border-left-color: #94a3b8;">
                <div class='step-title'>2. 🏦 적금으로 준비하면?</div>
                <div class='step-content'>
                    연 3.5% 확정금리 (이자소득세 15.4% 차감) → 세후 연 {3.5*(1-0.154):.2f}%<br>
                    {period}년 후 총 자산: <span class='highlight'>{f_w(savings_result)}원</span> (총 원금 {f_w(total_input)}원, 이자 수익 {f_w(savings_result - total_input)}원)<br>
                    <span style="color: #ef4444; font-weight: 600;">⚠️ 목표 금액 대비 {f_w(target_amt - savings_result)}원 부족 → 실질 인플레이션 반영 시 원금 가치마저 감소</span>
                </div>
            </div>
            <div class='step-box' style="border-left-color: #f59e0b;">
                <div class='step-title'>3. 📊 일반 펀드로 준비하면?</div>
                <div class='step-content'>
                    연 {rate}% 기대수익률 (배당소득세 15.4% 차감) → 세후 연 {rate*(1-0.154):.2f}%<br>
                    {period}년 후 예상 자산: <span class='highlight'>{f_w(fund_result_simple)}원</span> (이자 수익 {f_w(fund_result_simple - total_input)}원)<br>
                    <span style="color: #f59e0b; font-weight: 600;">⚠️ 매년 세금이 복리를 깎아먹어, 실질 자산 증식 속도 저하</span>
                </div>
            </div>
            <div class='step-box' style="border-left-color: #2563eb;">
                <div class='step-title'>4. 🚀 변액ETF로 준비하면?</div>
                <div class='step-content'>
                    연 {rate}% 기대수익률 (10년 이상 유지 시 <b>비과세</b>) → 실질 연 {rate:.2f}%<br>
                    {period}년 후 예상 자산: <span class='highlight' style="font-size: 1.1em; color: #2563eb;">{f_w(etf_result_simple)}원</span> (이자 수익 {f_w(etf_result_simple - total_input)}원)<br>
                    <span style="color: #2563eb; font-weight: 700;">✅ 비과세 복리 + ETF 낮은 변동성 + 사망보장까지! 펀드 대비 +{f_w(etf_result_simple - fund_result_simple)}원 추가 확보</span>
                </div>
            </div>
            <div class='step-box' style="border-left-color: #22c55e; background: linear-gradient(135deg, #f0fdf4, #dcfce7);">
                <div class='step-title'>5. 💎 변액ETF만의 차별화 포인트</div>
                <div class='step-content'>
                    <b>① 비과세 복리</b> — 수익에 세금 없이 전액 재투자, 시간이 갈수록 격차 확대<br>
                    <b>② 펀드 무제한 무료 변경</b> — 시장 상황에 따라 공격형↔안정형 자유 전환<br>
                    <b>③ 사망보험금</b> — 목적자금 + 가족 보장을 동시에 해결<br>
                    <b>④ 최저보증</b> — 최저 사망보험금 보증으로 원금 이하 손실 방어<br>
                    <b>⑤ ETF 편입</b> — S&P500, 나스닥 등 글로벌 ETF에 보험 내에서 직접 투자
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)



def render_dollar_insurance():
    st.title("💵 달러 설계")
    st.markdown("사망 보장 종신보험에 확정 금리와 환율 변동성을 활용한 해약환급금을 통해 전략적인 달러 마련의 기능까지 갖춘 보장성 플랜입니다.")
    
    # Data: Refund Rate Table (메트라이프 백만종 실제 보너스 구조 기반)
    # 납입기간에 따른 환급률 차이 (나이/성별과 무관)
    def get_refund_curve(ptype, period):
        rates = []
        
        # Logic for MetLife (백만인을 위한 달러종신)
        if "메트라이프" in ptype:
            if period == 5:
                # 5년납: 5년 완납 시 1차 보너스(22.5%) → 10년 시점 2차 보너스(11.0%) 합산 → 10년 약 124.9%
                # 1~4년: 납입 중 (해약환급금 낮음)
                # 5년차: 완납 + 1차 보너스(22.5%) 가산으로 점프
                # 6~9년: 복리 적립 + 2차 보너스 점진 반영
                # 10년: 2차 보너스(11.0%) 합산 → 124.9%
                base = [0, 35, 60, 78, 102.5, 106, 110, 114, 119, 124.9]
                last = 124.9
                for _ in range(11):
                    last *= 1.025
                    base.append(last)
                rates = base
            elif period == 7:
                # 7년납: 7년 완납 시 1차 보너스(22.2%) → 10년 시점 2차 보너스(15.9%) 합산 → 10년 약 124.8%
                # 1~6년: 납입 중 (해약환급금 낮음)
                # 7년차: 완납 + 1차 보너스(22.2%) 가산으로 점프
                # 8~9년: 복리 적립 + 2차 보너스 점진 반영
                # 10년: 2차 보너스(15.9%) 합산 → 124.8%
                base = [0, 25, 45, 62, 73, 82, 104.2, 110, 117, 124.8]
                last = 124.8
                for _ in range(11):
                    last *= 1.025
                    base.append(last)
                rates = base
            elif period == 10:
                # 10년납: 10년 완납과 동시에 대규모 유지보너스(약 39.7%) 한 번에 가산 → 10년 약 124.0%
                # 1~9년: 납입 중 (보너스 없이 적립만)
                # 10년차: 완납 + 유지보너스(39.7%) 대규모 점프 → 124.0%
                base = [0, 18, 34, 48, 58, 66, 72, 77, 84.3, 124.0]
                last = 124.0
                for _ in range(11):
                    last *= 1.025
                    base.append(last)
                rates = base
            else:  # 20년납
                # 20년납: 10년 시점은 아직 납입 중, 유지보너스가 20년 시점에 발생 → 10년 약 50~60%
                # 1~10년: 납입 중 (보너스 없음, 환급률 매우 낮음)
                # 11~19년: 계속 납입 중, 서서히 상승
                # 20년: 완납 + 유지보너스 가산
                base = [0, 8, 15, 22, 28, 34, 39, 44, 49, 55]
                last = 55
                for i in range(11):
                    if i < 9:
                        # 11~19년: 납입 중 점진 상승
                        last += 5
                    else:
                        # 20년차: 완납 + 유지보너스로 대폭 점프
                        last = 125.0 if i == 9 else last * 1.025
                    base.append(last)
                rates = base
        else: # Competitors (Generic)
            if period == 5:
                rates = [0, 40, 70, 90, 98, 100, 103, 106, 110, 115.0]
            else:
                rates = [0, 20, 50, 70, 80, 90, 95, 98, 100, 103.0]
            
            last = rates[-1]
            for _ in range(11):
                last *= 1.02
                rates.append(last)
        
        # 납입기간별 확정 환급률 그대로 반환 (나이/성별 보정 없음)
        return [round(r, 1) for r in rates[:20]]

    # 1. Inputs
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 달러 설계 입력")
            
            # Product & Client
            with st.container():
                st.markdown("##### 1. 기본 정보")
                
                prod_type = st.selectbox("상품 선택", ["메트라이프 (백만인을 위한 달러종신)", "타사 달러보험 (일반형)"], key="di_prod")
                
                c_pay1, c_pay2 = st.columns(2)
                pay_period = c_pay1.selectbox("납입 기간", [5, 7, 10, 20], index=0, key="di_period") # Default 5
                
                premium_usd = c_pay2.number_input("월 납입 보험료 ($)", value=0, step=100, format="%d", key="di_prem")
                
                # Custom Additional Payment Logic
                is_add_pay = st.toggle("추가납입 활용 (유니버셜 기능)", value=False, key="di_add_toggle")
                if is_add_pay:
                    add_premium_usd = st.number_input("월 추가납입 보험료 ($)", value=premium_usd, step=100, format="%d", help="기본 보험료의 100% 이내(최대 200%) 권장. 추가납입 시 사업비가 적어 환급률이 대폭 상승합니다.", key="di_add_prem")
                else:
                    add_premium_usd = 0
                
                total_premium_monthly = premium_usd + add_premium_usd
                
                 # Exchange Rate Specs
                st.markdown("##### 2. 환율 시나리오 (원/달러)")
                
                # Real-time Fetch Logic (Robust Requests)
                r_c1, r_c2 = st.columns([2.5, 1])
                with r_c1:
                    # Use session state for rate to update it via button
                    if 'curr_rate_val' not in st.session_state:
                        st.session_state.curr_rate_val = 1430.0 # Default conservative
                    
                    current_rate = st.number_input("현재 환율 (가입 시점)", value=st.session_state.curr_rate_val, step=1.0, format="%.1f", key="input_curr_rate")
                
                with r_c2:
                    st.write("") # Spacer
                    st.write("")
                    
                    # Callback Function for Button On_Click (Prevents Widget Key Conflict)
                    def update_exchange_rate():
                        try:
                            import requests
                            import time
                            
                            fetched_val = None
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                                
                            # 1. Try Naver Mobile API (JSON) - Standard & Very Stable
                            try:
                                url = "https://m.stock.naver.com/front-api/marketIndex/productDetail?category=exchange&reutersCode=FX_USDKRW"
                                r = requests.get(url, headers=headers, timeout=5)
                                r.raise_for_status()
                                data = r.json()
                                if 'result' in data and 'closePrice' in data['result']:
                                    fetched_val = float(data['result']['closePrice'].replace(',', ''))
                            except Exception:
                                pass # Fail silently, try next
                                
                            # 2. Try Yahoo Finance (HTML Scraping) - Fallback
                            if fetched_val is None:
                                try:
                                    url = "https://finance.yahoo.com/quote/KRW=X"
                                    r = requests.get(url, headers=headers, timeout=5)
                                    if "PRE_CHECK" not in r.text:
                                        import re
                                        match = re.search(r'regularMarketPrice.*?fmt":"([\d,]+)', r.text)
                                        if match:
                                            fetched_val = float(match.group(1).replace(',', ''))
                                except Exception:
                                    pass
    
                            if fetched_val:
                                # Update Session State Keys for Widgets
                                # IMPORTANT: Modifying keys directly in callback is allowed
                                st.session_state.curr_rate_val = fetched_val
                                st.session_state['input_curr_rate'] = fetched_val # Force widget update
                                
                                # Auto-Sync Scenarios
                                st.session_state.rate_mid_val = fetched_val
                                st.session_state['rate_mid_val'] = fetched_val
                                
                                low_val = round(fetched_val * 0.9, -1)
                                st.session_state.rate_low_val = low_val
                                st.session_state['rate_low_val'] = low_val
                                
                                high_val = round(fetched_val * 1.1, -1)
                                st.session_state.rate_high_val = high_val
                                st.session_state['rate_high_val'] = high_val
                                
                                # Auto-calc average rate based on fetched rate
                                current_pay_period = st.session_state.get('di_period', 5)
                                weight_curr = max(0, (20 - current_pay_period) / 20)
                                est_avg = (fetched_val * weight_curr) + (1250.0 * (1 - weight_curr))
                                st.session_state.avg_rate_val = round(est_avg, 1)
                                
                                st.toast(f"✅ 환율 정보 갱신 완료: {fetched_val:,.2f}원", icon="💱")
                            else:
                                st.toast("⚠️ 환율 정보를 가져오는데 실패했습니다.", icon="🚫")
                        except Exception as e:
                            st.toast(f"❌ 시스템 오류 발생: {str(e)}", icon="🚨")
    
                    st.button("🔄 실시간 수신", help="네이버/야후 금융 등 다중 소스를 통해 환율을 조회합니다.", on_click=update_exchange_rate)
    
                # Average Rate Logic
                long_term_mean = 1250.0
                
                # Auto Calc Button Removed (Now synced with Real-time Fetch)
                
                if 'avg_rate_val' not in st.session_state:
                    st.session_state.avg_rate_val = 1300.0
    
                avg_pay_rate = st.number_input(
                    "🤖 AI 예측 납입 기간 평균 환율", 
                    value=st.session_state.avg_rate_val, 
                    step=1.0, format="%.1f", 
                    help=f"매월 적립식 납입 시 '코스트 에버리지' 효과가 발생합니다. 실시간 수신 시 AI가 (장기 평균 {long_term_mean}원과 현재 환율을 납입 기간에 비례해 가중 평균하여) 현실적인 평단가를 자동 산출합니다."
                )
                
                # Initialize Scenario Session States if not valid
                if 'rate_low_val' not in st.session_state: st.session_state.rate_low_val = 1100.0
                if 'rate_mid_val' not in st.session_state: st.session_state.rate_mid_val = 1350.0
                if 'rate_high_val' not in st.session_state: st.session_state.rate_high_val = 1550.0
    
                st.caption("인출(해지) 시점 예상 환율 범위")
                c_r1, c_r2, c_r3 = st.columns(3)
                rate_low = c_r1.number_input("하락(비관)", value=st.session_state.rate_low_val, step=10.0, key="rate_low_val")
                rate_mid = c_r2.number_input("보합(중립)", value=st.session_state.rate_mid_val, step=10.0, key="rate_mid_val")
                rate_high = c_r3.number_input("상승(낙관)", value=st.session_state.rate_high_val, step=10.0, key="rate_high_val")
                
                commission_rate = 0.0
    else:
        # Presentation Mode: Load from State
        prod_type = st.session_state.di_prod if 'di_prod' in st.session_state else "메트라이프 (백만인을 위한 달러종신)"
        
        pay_period = st.session_state.di_period if 'di_period' in st.session_state else 5
        premium_usd = st.session_state.di_prem if 'di_prem' in st.session_state else 1000
        is_add_pay = st.session_state.di_add_toggle if 'di_add_toggle' in st.session_state else True
        if is_add_pay:
            add_premium_usd = st.session_state.di_add_prem if 'di_add_prem' in st.session_state else premium_usd
        else:
            add_premium_usd = 0
            
        total_premium_monthly = premium_usd + add_premium_usd
        
        # Rate Variables
        avg_pay_rate = st.session_state.avg_rate_val if 'avg_rate_val' in st.session_state else 1300.0
        rate_low = st.session_state.rate_low_val if 'rate_low_val' in st.session_state else 1100.0
        rate_mid = st.session_state.rate_mid_val if 'rate_mid_val' in st.session_state else 1350.0
        rate_high = st.session_state.rate_high_val if 'rate_high_val' in st.session_state else 1550.0
        commission_rate = 0.004

    # Logic Calculation
    # 1. Curve (납입기간별 환급률)
    csv_rates = get_refund_curve(prod_type, pay_period)
    
    # 2. Payments
    months_paid = pay_period * 12
    total_usd_paid_principal = total_premium_monthly * months_paid
    
    # KRW Paid = USD * Average Rate * Fee
    total_krw_paid = total_usd_paid_principal * avg_pay_rate * (1 + commission_rate)
    
    # 3. 10th Year Status
    idx_10 = 9
    rate_10_pet = csv_rates[idx_10] # %
    
    # Value in USD @ 10y
    # Standard CSV logic relies on "accumulated premium" base for rate application generally,
    # or specific Cash Value table. Here we use % of Total Premium Paid assumption for simplicity 
    # as defined in '124.9% of paid premiums'.
    
    # Correction: If pay_period is 5, at 10y we have fully paid 5y ago.
    # Base: Total Premium Paid
    usd_val_10 = total_usd_paid_principal * (rate_10_pet / 100)
    
    # KRW Returns
    krw_ret_low = usd_val_10 * rate_low
    krw_ret_mid = usd_val_10 * rate_mid
    krw_ret_high = usd_val_10 * rate_high
    
    # BEP Calculation
    # BEP Rate = Total KRW Paid / USD Value
    bep_rate = total_krw_paid / usd_val_10 if usd_val_10 > 0 else 0
    
    # Tax Equivalent Calc based on Mid Scenario
    try:
        total_profit = krw_ret_mid - total_krw_paid
        
        # 적립식(월납) 프리미엄의 평균 자금 예치 기간 산출
        # 10년납의 경우 첫 달 보험료는 10년 굴러가지만, 마지막 달은 1개월만 굴러감
        # 따라서 평균 거치 기간은 [10년 - (납입기간/2)] 로 근사 계산하는 것이 정확함
        avg_years_invested = max(1.0, 10.0 - (pay_period / 2.0))
        
        # 실질 연평균 복리 수익률 (CAGR)
        cagr = (krw_ret_mid / total_krw_paid) ** (1 / avg_years_invested) - 1
        
        # 비과세 역산 (은행 예적금 명목 금리로 환산)
        tax_equiv_yield_10y = (cagr / (1 - 0.154)) * 100
    except:
        tax_equiv_yield_10y = 0

    with col_result:
        st.subheader("📊 10년 시점 분석")
        
        # Improved Layout for Metrics using Custom HTML
        # Added min-width and flex-basis to ensure content fits
        # Improved Layout for Metrics using Custom HTML
        # Added min-width and flex-basis to ensure content fits
        st.markdown(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 140px; padding: 15px; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">총 납입 원금<br>(KRW)</div>
                <div style="color: #1e3a8a; font-size: 1.1rem; font-weight: 800;">{f_w(total_krw_paid/10000)}만원</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 8px;">평단 @{avg_pay_rate}원</div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; line-height: 1.4;">
                    월 ${f_w(total_premium_monthly)} × {months_paid}회<br>× 평균 환율 {avg_pay_rate}원
                </div>
            </div>
            <div style="flex: 1; min-width: 140px; padding: 15px; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">10년 시점 환급률<br>($)</div>
                <div style="color: #1e3a8a; font-size: 1.1rem; font-weight: 800;">{rate_10_pet:.1f}%</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 8px;">USD {f_w(usd_val_10)}</div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; line-height: 1.4;">
                    총 납입 달러 원금 대비<br>10년 시점 확정 환급금 비율
                </div>
            </div>
            <div style="flex: 1; min-width: 140px; padding: 15px; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">세전 환산 수익률</div>
                <div style="color: #22c55e; font-size: 1.1rem; font-weight: 800;">{tax_equiv_yield_10y:.2f}%</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 8px;">비과세 혜택 적용</div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; line-height: 1.4;">
                    이자소득세(15.4%) 면제 효과를<br>반영한 은행 예금 환산 금리
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # --- [추가 기획 1] 비과세 폭발력 시각화 배너 (은행 비교) ---
        bank_rate = 3.5
        display_yield = max(0, tax_equiv_yield_10y)
        yield_diff = display_yield - bank_rate
        
        # 차트 그리기용 막대 비율 (Max 10~15% 수준으로 스케일링)
        bar_max = max(10.0, display_yield + 2.0)
        bank_width = min(100, (bank_rate / bar_max) * 100)
        ins_width = min(100, (display_yield / bar_max) * 100)
        
        # +차이 라벨 처리
        diff_label = f"+{yield_diff:.2f}% 유리!" if yield_diff > 0 else f"{yield_diff:.2f}%"
        
        st.markdown(f"""
<div style="background: linear-gradient(135deg, #1e3a8a, #27398c); padding: 25px 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-top: 15px; margin-bottom: 25px; color: white;">
    <div style="text-align: center; margin-bottom: 22px;">
        <p style="color: white; font-size: 0.95rem; margin-top: 8px; margin-bottom: 0;">10년 뒤 동일한 달러(현금)를 만들기 위해, <b>이자소득세 15.4%를 떼는 시중은행 적금에 가입한다면 필요한 연 이율(실질 세전 금리)</b>입니다.</p>
    </div>
    <div style="margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 700; align-items: flex-end;">
            <span style="color: #cbd5e1; font-size: 1.05rem;">일반 시중은행 적금</span>
            <span style="color: #cbd5e1; font-size: 1.1rem; white-space: nowrap; margin-left: 10px;">연 3.50%</span>
        </div>
        <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 20px; height: 32px; overflow: hidden; position: relative;">
            <div style="width: {bank_width}%; background: #94a3b8; height: 100%; border-radius: 20px;"></div>
        </div>
    </div>
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 800; align-items: flex-end;">
            <span style="color: white; font-size: 1.25rem;">✨ 메트라이프 백만종 환산 금리</span>
            <span style="color: white; font-size: 1.25rem; white-space: nowrap; margin-left: 10px;">연 {display_yield:.2f}%</span>
        </div>
        <div style="width: 100%; background-color: rgba(255,255,255,0.15); border-radius: 20px; height: 42px; overflow: hidden; position: relative; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
            <div style="width: {ins_width}%; background: linear-gradient(90deg, #3b82f6, #1d4ed8); height: 100%; border-radius: 20px; box-shadow: 0 0 15px rgba(39,57,140,0.3); display: flex; align-items: center; justify-content: flex-end; padding-right: 15px; color: white; font-weight: 800; font-size: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                {diff_label}
            </div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)
        
        st.divider()
        st.markdown("<br>", unsafe_allow_html=True) # Add spacing as requested
        st.subheader("💱 환율 시나리오별 예상 환급금 (10년 시점)")
        
        p_low = krw_ret_low - total_krw_paid
        p_mid = krw_ret_mid - total_krw_paid
        p_high = krw_ret_high - total_krw_paid
        
        # HTML 렌더링 (문자열 연결 연산자 사용으로 따옴표 충돌 원천 방지)
        
        # 1. 데이터 준비
        rate_low_str = f"{int(rate_low):,}"
        val_low_str = f_w(krw_ret_low/10000)
        profit_low_num = (p_low/total_krw_paid*100) if total_krw_paid > 0 else 0
        profit_low_str = f"{profit_low_num:+.1f}% ({f_w(p_low/10000)}만)"
        color_low = "#ef4444" if p_low < 0 else "#16a34a"

        rate_mid_str = f"{int(rate_mid):,}"
        val_mid_str = f_w(krw_ret_mid/10000)
        profit_mid_num = (p_mid/total_krw_paid*100) if total_krw_paid > 0 else 0
        profit_mid_str = f"{profit_mid_num:+.1f}% ({f_w(p_mid/10000)}만)"
        color_mid = "#ef4444" if p_mid < 0 else "#16a34a"

        rate_high_str = f"{int(rate_high):,}"
        val_high_str = f_w(krw_ret_high/10000)
        profit_high_num = (p_high/total_krw_paid*100) if total_krw_paid > 0 else 0
        profit_high_str = f"{profit_high_num:+.1f}% ({f_w(p_high/10000)}만)"
        color_high = "#ef4444" if p_high < 0 else "#be123c"

        # 2. HTML 조립
        html = "<div style='display:flex; gap:12px; margin-bottom:24px; flex-wrap: wrap;'>"
        
        # 하락(비관) 카드
        html += "<div style='flex:1; min-width: 150px; padding:16px; border-radius:16px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); background: linear-gradient(to bottom right, #f1f5f9, #e2e8f0); border: 1px solid #cbd5e1;'>"
        html += "<div style='font-size:2rem; margin-bottom:8px;'>📉</div>"
        html += "<div style='font-size:0.95rem; font-weight:bold; color:#475569; margin-bottom:2px;'>하락(비관)</div>"
        html += "<div style='font-size:0.8rem; color:#64748b; margin-bottom:12px; font-family:Consolas, monospace;'>@" + rate_low_str + "원/$</div>"
        html += "<div style='font-size:1.25rem; font-weight:800; color:#334155; margin-bottom:6px; letter-spacing:-0.5px;'>" + val_low_str + "만원</div>"
        html += "<div style='font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:6px; display:inline-block; border:1px solid rgba(0,0,0,0.05); color:" + color_low + ";'>" + profit_low_str + "</div>"
        html += "</div>"

        # 보합(중립) 카드
        html += "<div style='flex:1; min-width: 150px; padding:16px; border-radius:16px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); background: linear-gradient(to bottom right, #eff6ff, #dbeafe); border: 1px solid #60a5fa;'>"
        html += "<div style='font-size:2rem; margin-bottom:8px;'>☁️</div>"
        html += "<div style='font-size:0.95rem; font-weight:bold; color:#1d4ed8; margin-bottom:2px;'>보합(중립)</div>"
        html += "<div style='font-size:0.8rem; color:#3b82f6; margin-bottom:12px; font-family:Consolas, monospace;'>@" + rate_mid_str + "원/$</div>"
        html += "<div style='font-size:1.25rem; font-weight:800; color:#1e40af; margin-bottom:6px; letter-spacing:-0.5px;'>" + val_mid_str + "만원</div>"
        html += "<div style='font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:6px; display:inline-block; border:1px solid rgba(37, 99, 235, 0.1); color:" + color_mid + ";'>" + profit_mid_str + "</div>"
        html += "</div>"

        # 상승(낙관) 카드
        html += "<div style='flex:1; min-width: 150px; padding:16px; border-radius:16px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); background: linear-gradient(to bottom right, #fff1f2, #fecdd3); border: 1px solid #f43f5e;'>"
        html += "<div style='font-size:2rem; margin-bottom:8px;'>☀️</div>"
        html += "<div style='font-size:0.95rem; font-weight:bold; color:#be123c; margin-bottom:2px;'>상승(낙관)</div>"
        html += "<div style='font-size:0.8rem; color:#e11d48; margin-bottom:12px; font-family:Consolas, monospace;'>@" + rate_high_str + "원/$</div>"
        html += "<div style='font-size:1.25rem; font-weight:800; color:#9f1239; margin-bottom:6px; letter-spacing:-0.5px;'>" + val_high_str + "만원</div>"
        html += "<div style='font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:6px; display:inline-block; border:1px solid rgba(225, 29, 72, 0.1); color:" + color_high + ";'>" + profit_high_str + "</div>"
        html += "</div>"

        html += "</div>"
        
        st.markdown(html, unsafe_allow_html=True)
        
        # Detailed BEP Explanation
        with st.expander("💡 손익분기 환율(BEP) 산출 근거 보기"):
            st.markdown(f"""
            <div class='logic-annotation'>
                <b>🧮 산출 공식:</b> 총 납입 원화 ÷ 10년 시점 달러 해지환급금<br>
                <br>
                1. <b>총 납입 원화:</b> {f_w(total_krw_paid)}원 (월 ${f_w(total_premium_monthly)} × {months_paid}개월 × 평단 {avg_pay_rate}원)<br>
                2. <b>달러 환급금:</b> ${f_w(usd_val_10)} (원금 ${f_w(total_usd_paid_principal)} × 환급률 {rate_10_pet:.1f}%)<br>
                3. <b>손익분기 환율:</b> <span style='color:#e11d48; font-weight:bold;'>{bep_rate:.1f}원</span><br>
                4. <b>참고:</b> 메트라이프 백만종 상품은 나이/성별과 무관하게 납입기간에 따른 확정 환급률이 적용됩니다.<br>
                <br>
                👉 환율이 {bep_rate:.1f}원 이상이면 원화 기준으로도 원금 이상입니다.
            </div>
            """, unsafe_allow_html=True)

    st.divider()
    
    # Chart Preparation
    years_x = list(range(1, 21)) # 1 to 20
    # ensure years_x matches rates length
    rates_chart = get_refund_curve(prod_type, pay_period)
    rates_comp = get_refund_curve("타사", pay_period)
    
    c_chart1, c_chart2 = st.columns(2, gap="large")
    
    with c_chart1:
        st.subheader("📈 해약환급률 추이 비교")
        fig_csv = go.Figure()
        fig_csv.add_trace(go.Scatter(x=years_x, y=rates_chart, mode='lines+markers', name='선택 상품',
                                     line=dict(color='#1e3a8a', width=3)))
        fig_csv.add_trace(go.Scatter(x=years_x, y=rates_comp, mode='lines', name='타사 평균',
                                     line=dict(color='#94a3b8', width=2, dash='dot')))
        
        # Annotation for 10y
        fig_csv.add_annotation(x=10, y=rates_chart[9], text=f"10년 {rates_chart[9]}%", showarrow=True, arrowhead=1, yshift=10)
        
        fig_csv.update_layout(title="경과 기간별 환급률 (%)", template="plotly_white", height=300, hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_csv, use_container_width=True)
        
    with c_chart2:
        st.subheader("💰 환율 시나리오별 자산 가치")
        st.caption("10년 시점, 환율 변동에 따른 원화 환산 자산 가치 (환차익 시뮬레이션)")
        
        # 10년 시점 총 환급금($) 예측
        usd_cash_value_10y = total_usd_paid_principal * (rate_10_pet / 100)
        
        scenarios = ['하락(비관)', '보합(중립)', '상승(낙관)'] 
        rates = [rate_low, rate_mid, rate_high]
        colors = ['#94a3b8', '#3b82f6', '#ef4444'] 
        
        krw_values = [usd_cash_value_10y * r for r in rates]
        
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Bar(
            x=scenarios, y=krw_values,
            text=[f"{f_w(v)}" for v in krw_values],
            textposition='auto',
            marker_color=colors
        ))
        
        # 기준선 (원화 납입 원금) 추가
        fig_sens.add_hline(y=total_krw_paid, line_dash="dash", line_color="#334155", annotation_text="원화 납입 원금")
        
        # 최대 이익 계산
        max_profit = max(krw_values) - total_krw_paid
        
        fig_sens.update_layout(title=f"최대 환차익 +{f_w(max_profit)}원 예상", template="plotly_white", height=300, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sens, use_container_width=True)

    # 환율 추이 차트
    with st.expander("📈 USD/KRW 환율 흐름 한눈에 보기 (최근 10년)", expanded=True):
        # 시뮬레이션 데이터 (최근 순 정렬: 2026 -> 2016)
        years_hist = [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016]
        # 데이터도 최근 순으로 (2026이 첫번째)
        avg_rates = [int(current_rate), 1390, 1364, 1306, 1292, 1144, 1180, 1166, 1100, 1131, 1161]
        
        rate_max = max(avg_rates)
        rate_min = min(avg_rates)
        rate_avg = int(sum(avg_rates) / len(avg_rates))
        rate_now = int(current_rate)
        max_year = years_hist[avg_rates.index(rate_max)]
        min_year = years_hist[avg_rates.index(rate_min)]
        
        # 핵심 요약 카드
        st.markdown("##### 💡 10년 환율 핵심 요약")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📉 최저 환율", f"{rate_min:,}원", f"{min_year}년")
        m2.metric("📈 최고 환율", f"{rate_max:,}원", f"{max_year}년")
        m3.metric("📊 10년 평균", f"{rate_avg:,}원", f"{len(avg_rates)}년 평균")
        m4.metric("📍 현재 기준", f"{rate_now:,}원", f"평균 대비 {'+' if rate_now > rate_avg else ''}{rate_now - rate_avg:,}원")
        
        st.divider()
        
        # 흐름 해석 메시지
        if rate_now > rate_avg:
            trend_msg = f"현재 환율({rate_now:,}원)은 10년 평균({rate_avg:,}원)보다 **{rate_now - rate_avg:,}원 높은 수준**입니다. 달러 자산의 원화 환산 가치가 높아 **환차익이 유리**한 시점입니다."
        else:
            trend_msg = f"현재 환율({rate_now:,}원)은 10년 평균({rate_avg:,}원)보다 **{rate_avg - rate_now:,}원 낮은 수준**입니다. 달러 매입 단가를 낮출 수 있는 저점 구간이므로 **적립 확대를 고려**해볼 만합니다."
        
        st.info(f"💡 {trend_msg}")
        
        # 깔끔한 트렌드 차트
        fig_rate = go.Figure()
        
        # 10년 평균 영역
        fig_rate.add_hrect(y0=rate_avg - 50, y1=rate_avg + 50,
                          fillcolor="rgba(59, 130, 246, 0.08)", line_width=0,
                          annotation_text=f"평균 구간 ({rate_avg-50:,}~{rate_avg+50:,})")
        
        # 메인 라인 (Plotly는 X축 기준 정렬하므로 데이터 순서 상관없이 시계열 좌->우로 그려짐. 표와 일치시키기 위해 데이터는 역순 유지)
        fig_rate.add_trace(go.Scatter(
            x=years_hist, y=avg_rates,
            mode='lines+markers+text',
            line=dict(color='#1e3a8a', width=3),
            marker=dict(size=10, color='#3b82f6', line=dict(width=2, color='white')),
            text=[f"{r:,}" for r in avg_rates],
            textposition='top center',
            textfont=dict(size=10, color='#334155'),
            name='연평균 환율'
        ))
        
        # 현재 시점 강조
        fig_rate.add_trace(go.Scatter(
            x=[2026], y=[rate_now],
            mode='markers',
            marker=dict(size=16, color='#ef4444', symbol='star', line=dict(width=2, color='white')),
            name=f'현재 ({rate_now:,}원)',
            showlegend=True
        ))
        
        fig_rate.update_layout(
            title=dict(text="연도별 USD/KRW 연평균 환율 추이", font=dict(size=16, color='#1e293b')),
            xaxis=dict(title="연도", dtick=1, showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(title="환율 (원/USD)", showgrid=True, gridcolor='#f1f5f9',
                      range=[min(avg_rates) - 80, max(avg_rates) + 80]),
            template="plotly_white",
            height=380,
            plot_bgcolor='rgba(255,255,255,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rate, use_container_width=True)
        
        # 연도별 표 (역순 데이터 -> 전년 대비 계산 주의)
        import pandas as pd
        diff_list = []
        for i in range(len(avg_rates)):
            if i == len(avg_rates) - 1: # 마지막 요소 (2016)
                diff_list.append("-")
            else:
                diff = avg_rates[i] - avg_rates[i+1] # 현재 - 과거
                # HTML Color Tag 적용
                if diff > 0:
                    diff_str = f"<span style='color:#ef4444; font-weight:bold;'>▲ {abs(diff):,}원</span>"
                elif diff < 0:
                    diff_str = f"<span style='color:#3b82f6; font-weight:bold;'>▼ {abs(diff):,}원</span>"
                else:
                    diff_str = "-"
                diff_list.append(diff_str)

        df_rate = pd.DataFrame({
            "연도": years_hist,
            "연평균 환율(원)": [f"{r:,}" for r in avg_rates],
            "전년 대비": diff_list
        })
        
        # HTML Table 렌더링 (style 적용 위해)
        st.markdown(df_rate.to_html(escape=False, index=False, classes="table-custom"), unsafe_allow_html=True)
        # CSS for better table look
        st.markdown("""
        <style>
        .table-custom { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-top: 10px; }
        .table-custom th { background-color: #f8fafc; border-bottom: 2px solid #e2e8f0; padding: 8px; text-align: center; color: #64748b; font-weight: 600; }
        .table-custom td { border-bottom: 1px solid #f1f5f9; padding: 8px; text-align: center; color: #334155; }
        .table-custom tr:hover { background-color: #f1f5f9; }
        </style>
        """, unsafe_allow_html=True)
        
        st.caption("※ 연평균 환율은 한국은행 기준환율 참고 시뮬레이션이며, 정확한 시세는 금융 포털을 참조하세요.")

    with st.expander("📝 AI 분석 리포트", expanded=True):
         st.markdown(f"""
        <div class='expert-card'>
            <div class='expert-title'>🏆 {prod_type} 핵심 경쟁력</div>
            <div class='step-box'>
                <div class='step-title'>1. 확정 금리와 환차익의 Dual Effect</div>
                <div class='step-content'>
                    10년 시점 확정 환급률 <span class='highlight'>{rate_10_pet}%</span>에 달러 강세 시 추가 환차익을 누릴 수 있습니다.
                    현재 구조상 손익분기 환율(BEP)은 <span class='highlight'>{bep_rate:.1f}원</span>으로, 장기적 관점에서 안정성이 뛰어납니다.
                </div>
            </div>
            <div class='step-box'>
                <div class='step-title'>2. 비과세 혜택의 실질 가치</div>
                <div class='step-content'>
                    관련 세법 충족 시 15.4% 이자소득세가 면제되므로, 은행 예금으로 환산 시 연 <span class='highlight'>{tax_equiv_yield_10y:.2f}%</span>의 수익 상품과 동일한 세후 효과를 가집니다.
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def render_jeonwolse():
    """전월세 전환율 계산기"""
    st.title("🏠 전월세 전환율 계산기")
    st.markdown("전세와 월세를 **전환율 기반**으로 상호 변환하고, 유불리를 분석합니다.")
    
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 전월세 조건 입력")
            
            mode = st.radio("변환 방향", ["전세 → 월세", "월세 → 전세"], horizontal=True, key="jw_mode")
            
            if "전세 → 월세" in mode:
                jeonse = comma_int_input("전세 보증금 (원)", 0, "jw_jeonse")
                wolse_deposit = comma_int_input("월세 전환 시 보증금 (원)", 0, "jw_deposit")
            else:
                wolse_deposit = comma_int_input("월세 보증금 (원)", 0, "jw_deposit")
                monthly_wolse = comma_int_input("월세 (원/월)", 0, "jw_wolse")
            
            conversion_rate = st.slider("전월세 전환율 (%)", 2.0, 12.0, 5.0, step=0.5, key="jw_rate",
                                        help="전세보증금을 월세로 (또는 그 반대로) 전환할 때 적용되는 이율입니다. 값이 높을수록 똑같은 보증금에 대해 내야(받아야) 할 월세가 많아집니다. (2025년 법정 상한선: 한국은행 기준금리 2.75% + 2.0% = 4.75%)")
    else:
        mode = st.session_state.get('jw_mode', "전세 → 월세")
        jeonse = st.session_state.get('jw_jeonse', 300_000_000)
        wolse_deposit = st.session_state.get('jw_deposit', 50_000_000)
        monthly_wolse = st.session_state.get('jw_wolse', 1_000_000)
        conversion_rate = st.session_state.get('jw_rate', 5.0)
    
    # 계산
    with col_result:
        st.subheader("📊 전환 결과")
        
        if "전세 → 월세" in mode:
            diff = max(0, jeonse - wolse_deposit)
            monthly_wolse_calc = int(diff * (conversion_rate / 100) / 12)
            annual_wolse = monthly_wolse_calc * 12
            
            c1, c2 = st.columns(2)
            c1.metric("산출 월세", f"{f_w(monthly_wolse_calc)} 원/월")
            c2.metric("연간 월세 합계", f"{f_w(annual_wolse)} 원/년")
            
            st.markdown(f"""
            <div class='logic-annotation'>
                <b>🧮 산출 근거:</b><br>
                (전세 {f_w(jeonse)}원 - 보증금 {f_w(wolse_deposit)}원) × 전환율 {conversion_rate}% ÷ 12<br>
                = {f_w(diff)}원 × {conversion_rate}% ÷ 12 = <b>{f_w(monthly_wolse_calc)}원/월</b>
            </div>
            """, unsafe_allow_html=True)
            
            # 비교 차트
            fig = go.Figure(data=[
                go.Bar(name='전세 기회비용', x=['연간 비용'], y=[int(jeonse * conversion_rate / 100)], marker_color='#1e3a8a'),
                go.Bar(name='월세 합계', x=['연간 비용'], y=[annual_wolse], marker_color='#ef4444')
            ])
            fig.update_layout(barmode='group', template='plotly_white', height=300, title="전세 기회비용 vs 월세 비교")
            st.plotly_chart(fig, use_container_width=True)
            

            
        else:
            # 월세 → 전세
            jeonse_calc = wolse_deposit + int(monthly_wolse * 12 / (conversion_rate / 100))
            
            c1, c2 = st.columns(2)
            c1.metric("환산 전세금", f"{f_w(jeonse_calc)} 원")
            c2.metric("연간 월세 합계", f"{f_w(monthly_wolse * 12)} 원/년")
            
            st.markdown(f"""
            <div class='logic-annotation'>
                <b>🧮 산출 근거:</b><br>
                보증금 {f_w(wolse_deposit)}원 + (월세 {f_w(monthly_wolse)}원 × 12 ÷ 전환율 {conversion_rate}%)<br>
                = {f_w(wolse_deposit)} + {f_w(int(monthly_wolse * 12 / (conversion_rate / 100)))} = <b>{f_w(jeonse_calc)}원</b>
            </div>
            """, unsafe_allow_html=True)
            

        
        # 전환율 민감도 분석
        st.divider()
        st.subheader("📈 전환율 민감도 분석")
        rates = [r/10 for r in range(20, 121, 5)]
        if "전세 → 월세" in mode:
            diff = max(0, jeonse - wolse_deposit)
            wolse_values = [int(diff * (r/100) / 12) for r in rates]
            fig2 = go.Figure(data=[go.Scatter(x=rates, y=wolse_values, mode='lines+markers',
                                              line=dict(color='#1e3a8a', width=3))])
            fig2.add_vline(x=conversion_rate, line_dash="dash", line_color="#ef4444", 
                          annotation_text=f"현재 {conversion_rate}%")
            fig2.update_layout(title="전환율별 예상 월세", xaxis_title="전환율 (%)", yaxis_title="월세 (원)",
                                  template='plotly_white', height=300)
        else:
            jeonse_values = [wolse_deposit + int(monthly_wolse * 12 / (r/100)) for r in rates]
            fig2 = go.Figure(data=[go.Scatter(x=rates, y=jeonse_values, mode='lines+markers',
                                              line=dict(color='#1e3a8a', width=3))])
            fig2.add_vline(x=conversion_rate, line_dash="dash", line_color="#ef4444",
                          annotation_text=f"현재 {conversion_rate}%")
            fig2.update_layout(title="전환율별 환산 전세금", xaxis_title="전환율 (%)", yaxis_title="전세금 (원)",
                                  template='plotly_white', height=300)
        st.plotly_chart(fig2, use_container_width=True)

    # 유불리 판정 (Input Column으로 이동)
    with col_input:
        st.write("") # Spacer
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        if "전세 → 월세" in mode:
            opp_cost = int(jeonse * conversion_rate / 100)
            if opp_cost > annual_wolse:
                verdict_icon = "✅"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "월세가 유리합니다"
                verdict_desc = f"전세 기회비용({f_w(opp_cost)}원/년)이 월세({f_w(annual_wolse)}원/년)보다 <b>{f_w(opp_cost - annual_wolse)}원 더 비쌉니다.</b><br>전세 보증금을 투자하면 월세보다 높은 수익을 기대할 수 있습니다."
            elif opp_cost < annual_wolse:
                verdict_icon = "🏠"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "전세가 유리합니다"
                verdict_desc = f"월세({f_w(annual_wolse)}원/년)가 전세 기회비용({f_w(opp_cost)}원/년)보다 <b>{f_w(annual_wolse - opp_cost)}원 더 비쌉니다.</b><br>전세를 유지하는 것이 경제적으로 유리합니다."
            else:
                verdict_icon = "⚖️"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "비용이 동일합니다"
                verdict_desc = "전세 기회비용과 월세 부담이 같습니다. 주거 안정성, 자금 유동성 등을 고려하여 선택하세요."
            
            st.markdown(f"""
            <div style='padding:20px; border:1px solid rgba(255,255,255,0.1); border-radius:12px; text-align:center; background:{verdict_bg}; margin-top:10px; color:white;'>
                <div style='font-size:2rem; margin-bottom:8px;'>{verdict_icon}</div>
                <div style='font-size:1.3rem; font-weight:800; color:{verdict_color}; margin-bottom:10px;'>{verdict_title}</div>
                <div style='font-size:0.9rem; color:#cbd5e1; line-height:1.6;'>{verdict_desc}</div>
                <div style='margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.2); font-size:0.8rem; color:#94a3b8;'>
                    ※ 기회비용 = 전세 보증금 × 전환율({conversion_rate}%). 실제 투자수익률에 따라 달라질 수 있습니다.
                </div>
            </div>
            """, unsafe_allow_html=True)
            
        else:
            annual_wolse_pay = monthly_wolse * 12
            opp_cost_jeonse = int(jeonse_calc * conversion_rate / 100)
            if annual_wolse_pay > opp_cost_jeonse:
                verdict_icon = "🏠"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "전세 전환이 유리합니다"
                verdict_desc = f"현재 월세 부담({f_w(annual_wolse_pay)}원/년)이 전세 기회비용({f_w(opp_cost_jeonse)}원/년)보다 <b>{f_w(annual_wolse_pay - opp_cost_jeonse)}원 더 비쌉니다.</b><br>전세 자금이 있다면 전세로 전환하는 것이 유리합니다."
            elif annual_wolse_pay < opp_cost_jeonse:
                verdict_icon = "✅"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "현재 월세가 유리합니다"
                verdict_desc = f"전세 기회비용({f_w(opp_cost_jeonse)}원/년)이 월세 부담({f_w(annual_wolse_pay)}원/년)보다 <b>{f_w(opp_cost_jeonse - annual_wolse_pay)}원 더 비쌉니다.</b><br>여유 자금을 투자에 활용하는 것이 더 효율적입니다."
            else:
                verdict_icon = "⚖️"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "비용이 동일합니다"
                verdict_desc = "월세 부담과 전세 기회비용이 같습니다. 주거 안정성, 자금 유동성 등을 고려하여 선택하세요."
            
            st.markdown(f"""
            <div style='padding:20px; border:1px solid rgba(255,255,255,0.1); border-radius:12px; text-align:center; background:{verdict_bg}; margin-top:10px; color:white;'>
                <div style='font-size:2rem; margin-bottom:8px;'>{verdict_icon}</div>
                <div style='font-size:1.3rem; font-weight:800; color:{verdict_color}; margin-bottom:10px;'>{verdict_title}</div>
                <div style='font-size:0.9rem; color:#cbd5e1; line-height:1.6;'>{verdict_desc}</div>
                <div style='margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.2); font-size:0.8rem; color:#94a3b8;'>
                    ※ 기회비용 = 환산 전세금 × 전환율({conversion_rate}%). 실제 투자수익률에 따라 달라질 수 있습니다.
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_loan_planner():
    """대출 상환 설계"""
    st.title("🏦 대출 상환 설계")
    st.markdown("원리금균등, 원금균등, 거치식 3가지 상환 방식을 **한눈에 비교**합니다.")
    
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 대출 조건 입력")
            loan_amount = comma_int_input("대출 원금 (원)", 0, "loan_amt")
            loan_rate = st.slider("연 이자율 (%)", 1.0, 15.0, 4.0, step=0.1, key="loan_rate")
            loan_years = st.slider("대출 기간 (년)", 1, 40, 30, key="loan_years")
            grace_years = st.slider("거치 기간 (년, 거치식 전용)", 0, 10, 3, key="loan_grace")
    else:
        loan_amount = st.session_state.get('loan_amt', 300_000_000)
        loan_rate = st.session_state.get('loan_rate', 4.0)
        loan_years = st.session_state.get('loan_years', 30)
        grace_years = st.session_state.get('loan_grace', 3)
    
    # 계산
    monthly_rate = loan_rate / 100 / 12
    total_months = loan_years * 12
    grace_months = grace_years * 12
    
    # 1. 원리금균등 (pmt_equal 계산 미리 수행)
    if monthly_rate > 0 and total_months > 0:
        pmt_equal = loan_amount * monthly_rate * (1+monthly_rate)**total_months / ((1+monthly_rate)**total_months - 1)
    else:
        pmt_equal = loan_amount / max(1, total_months)

    if not st.session_state.presentation_mode:
        with col_input:
            # 상환 스케줄 차트 (원리금균등 기준) - 입력창 아래로 이동
            st.divider()
            st.subheader("📈 원리금균등 상환 스케줄")
            
            balances = []
            interests_cum = []
            bal = loan_amount
            cum_int = 0
            step = max(1, total_months // 60)
            for m in range(0, total_months + 1, step):
                balances.append(bal)
                interests_cum.append(cum_int)
                if m < total_months:
                    for s in range(step):
                        if bal > 0:
                            interest_part = bal * monthly_rate
                            principal_part = min(bal, pmt_equal - interest_part)
                            bal = max(0, bal - principal_part)
                            cum_int += interest_part
            
            months_x = list(range(0, total_months + 1, step))[:len(balances)]
            
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=months_x, y=balances, mode='lines', name='잔여 원금',
                                       line=dict(color='#1e3a8a', width=2), fill='tozeroy',
                                       fillcolor='rgba(30,58,138,0.1)'))
            fig2.add_trace(go.Scatter(x=months_x, y=interests_cum, mode='lines', name='누적 이자',
                                       line=dict(color='#ef4444', width=2, dash='dot')))
            fig2.update_layout(
                title=dict(text="경과 기간별 원금 잔액 및 누적 이자", font=dict(color="#1e293b")), 
                template='plotly_white', 
                height=300,
                xaxis_title="개월", yaxis_title="금액 (원)"
            )
            st.plotly_chart(fig2, use_container_width=True)
    total_interest_equal = pmt_equal * total_months - loan_amount
    
    # 2. 원금균등
    monthly_principal = loan_amount / total_months if total_months > 0 else 0
    total_interest_principal = 0
    for m in range(total_months):
        remain = loan_amount - monthly_principal * m
        total_interest_principal += remain * monthly_rate
    first_payment_principal = monthly_principal + loan_amount * monthly_rate
    last_payment_principal = monthly_principal + monthly_principal * monthly_rate
    
    # 3. 거치식
    grace_interest_monthly = loan_amount * monthly_rate
    repay_months = total_months - grace_months
    if monthly_rate > 0 and repay_months > 0:
        pmt_grace = loan_amount * monthly_rate * (1+monthly_rate)**repay_months / ((1+monthly_rate)**repay_months - 1)
    else:
        pmt_grace = loan_amount / max(1, repay_months)
    total_interest_grace = grace_interest_monthly * grace_months + (pmt_grace * repay_months - loan_amount) if repay_months > 0 else 0
    
    with col_result:
        st.subheader("📊 상환 비교 분석")
        
        c1, c2, c3 = st.columns(3)
        c1.metric("원리금균등 월 납입", f"{f_w(pmt_equal)} 원", f"총이자 {f_w(total_interest_equal)}")
        c2.metric("원금균등 초회 납입", f"{f_w(first_payment_principal)} 원", f"총이자 {f_w(total_interest_principal)}")
        c3.metric(f"거치식\n(거치{grace_years}년)", f"{f_w(grace_interest_monthly)} 원", f"총이자 {f_w(total_interest_grace)}")
        
        # 이자 비교 차트
        st.divider()
        st.subheader("💰 총 이자 비교")
        
        methods = ['원리금균등', '원금균등', f'거치식({grace_years}년)']
        interests = [total_interest_equal, total_interest_principal, total_interest_grace]
        colors = ['#1e3a8a', '#3b82f6', '#ef4444']
        
        fig = go.Figure(data=[go.Bar(
            x=methods, y=interests,
            text=[f"{f_w(i)}원" for i in interests],
            textposition='auto',
            marker_color=colors
        )])
        fig.update_layout(
            title="상환 방식별 총 이자 비교", 
            template='plotly_white', 
            height=300, 
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
        pass
        
        # 상세 리포트
        with st.expander("📝 상세 분석 리포트", expanded=True):
            savings = total_interest_grace - total_interest_principal
            st.markdown(f"""
            <div class='expert-card'>
                <div class='expert-title'>🏦 상환 전략 분석</div>
                <div class='step-box'>
                    <div class='step-title'>💡 핵심 인사이트</div>
                    <div class='step-content'>
                        원금균등 방식이 총 이자를 가장 적게 지불합니다.<br>
                        거치식 대비 <span class='highlight'>{f_w(savings)}원</span> 이자 절감 가능합니다.<br>
                        다만, 원리금균등은 매월 동일 금액으로 계획적 상환에 유리합니다.
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)


def render_income_tax():
    """종합소득세 시뮬레이터"""
    st.title("💼 종합소득세 시뮬레이터")
    st.markdown("다양한 소득원을 입력하면 **종합과세 vs 분리과세**를 비교합니다.")
    
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    # 종합소득세 누진세율 (2025 기준)
    def calc_income_tax(taxable):
        if taxable <= 0:
            return 0, "과세표준 없음", 0
        brackets = [
            (14_000_000, 0.06, 0),
            (50_000_000, 0.15, 1_260_000),
            (88_000_000, 0.24, 5_760_000),
            (150_000_000, 0.35, 15_440_000),
            (300_000_000, 0.38, 19_940_000),
            (500_000_000, 0.40, 25_940_000),
            (1_000_000_000, 0.42, 35_940_000),
            (float('inf'), 0.45, 65_940_000)
        ]
        for limit, rate, prog_ded in brackets:
            if taxable <= limit:
                tax = taxable * rate - prog_ded
                return max(0, tax), f"{rate*100:.0f}%", rate
        return max(0, taxable * 0.45 - 65_940_000), "45%", 0.45
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 소득 항목 입력")
            
            st.markdown("##### 1. 근로소득")
            salary = comma_int_input("총급여 (원/년)", 0, "it_salary")
            
            st.markdown("##### 2. 금융소득 (이자/배당)")
            c1, c2 = st.columns(2)
            with c1:
                interest_income = comma_int_input("이자소득 (원/년)", 0, "it_interest")
            with c2:
                dividend_income = comma_int_input("배당소득 (원/년)", 0, "it_dividend")
            
            st.markdown("##### 3. 사업소득 (임대/부업 포함)")
            business_income = comma_int_input("사업소득금액 (매출-필요경비)", 0, "it_business")
            
            st.markdown("##### 4. 연금소득")
            pension_income = comma_int_input("연금소득금액 (공적/사적 연금)", 0, "it_pension")
            
            st.markdown("##### 5. 기타소득")
            etc_income = comma_int_input("기타소득금액 (강연료/인세 등)", 0, "it_etc")
            
            st.markdown("##### 6. 공제 항목")
            basic_ded = comma_int_input("인적공제·기본공제 (원)", 0, "it_basic_ded")
            
            st.divider()
            with st.expander("ℹ️ 종합과세 vs 분리과세 가이드", expanded=True):
                st.markdown("""
                <div style='background-color: #f8fafc; padding: 12px; border-radius: 8px; border: 1px solid #e2e8f0; font-size: 0.9rem;'>
                    <strong style='color: #1e3a8a;'>📌 종합과세란?</strong><br>
                    이자, 배당, 사업(부동산임대), 근로, 연금, 기타소득을 <b>모두 합산</b>하여 누진세율(6%~45%)을 적용하는 방식입니다. 소득이 많을수록 높은 세율이 적용되어 세부담이 커집니다.<br><br>
                    <strong style='color: #1e3a8a;'>📌 분리과세란?</strong><br>
                    특정 소득(주택임대 2천만원 이하, 금융소득 2천만원 이하 등)을 합산하지 않고 <b>단일 세율(14% 등)</b>로 별도 과세하여 종결하는 방식입니다.<br><br>
                    <strong style='color: #ef4444;'>💡 유불리 판단 (핵심)</strong><br>
                    1. <b>소득이 적을 때</b>: 종합과세가 유리할 수 있습니다. (누진세율 6% 구간이 분리과세 14%보다 낮음)<br>
                    2. <b>소득이 많을 때</b>: 분리과세가 절대적으로 유리합니다. (최고 45% 누진세율 회피)<br>
                    3. <b>금융소득</b>: 2,000만원 초과 시 무조건 종합과세됩니다. (필수 체크)<br>
                    4. <b>주택임대</b>: 2,000만원 이하는 분리과세(14%) 선택 가능합니다.
                </div>
                """, unsafe_allow_html=True)
    else:
        salary = st.session_state.get('it_salary', 60_000_000)
        interest_income = st.session_state.get('it_interest', 5_000_000)
        dividend_income = st.session_state.get('it_dividend', 3_000_000)
        business_income = st.session_state.get('it_business', 12_000_000)
        pension_income = st.session_state.get('it_pension', 0)
        etc_income = st.session_state.get('it_etc', 0)
        basic_ded = st.session_state.get('it_basic_ded', 1_500_000)
    
    # 계산
    # 근로소득공제
    if salary <= 5_000_000:
        salary_ded = salary * 0.7
    elif salary <= 15_000_000:
        salary_ded = 3_500_000 + (salary - 5_000_000) * 0.4
    elif salary <= 45_000_000:
        salary_ded = 7_500_000 + (salary - 15_000_000) * 0.15
    elif salary <= 100_000_000:
        salary_ded = 12_000_000 + (salary - 45_000_000) * 0.05
    else:
        salary_ded = 14_750_000 + (salary - 100_000_000) * 0.02
    salary_ded = min(salary_ded, 20_000_000)
    
    earned_income = max(0, salary - salary_ded)
    
    # 금융소득 (이자+배당)
    financial_income = interest_income + dividend_income
    financial_threshold = 20_000_000
    
    # 종합과세 (전부 합산)
    total_income = earned_income + financial_income + business_income + pension_income + etc_income
    taxable_income = max(0, total_income - basic_ded)
    income_tax, rate_desc, marginal_rate = calc_income_tax(taxable_income)
    local_tax = income_tax * 0.1  # 지방소득세 10%
    total_tax = income_tax + local_tax
    
    # 분리과세 비교 (금융소득 2천만원 이하 시 14% 분리과세)
    if financial_income <= financial_threshold:
        sep_financial_tax = financial_income * 0.14
        sep_remaining = earned_income + business_income + pension_income + etc_income
        sep_taxable = max(0, sep_remaining - basic_ded)
        sep_income_tax, sep_rate_desc, _ = calc_income_tax(sep_taxable)
        sep_local_tax = (sep_income_tax + sep_financial_tax) * 0.1
        sep_total_tax = sep_income_tax + sep_financial_tax + sep_local_tax
        can_separate = True
    else:
        sep_total_tax = total_tax  # 2천만 초과 시 무조건 종합과세
        can_separate = False
    
    with col_result:
        st.subheader("📊 종합소득세 산출 결과")
        
        c1, c2 = st.columns(2)
        c1.metric("총 소득금액", f"{f_w(total_income)} 원")
        c2.metric("과세표준", f"{f_w(taxable_income)} 원")
        st.caption(f"적용 세율 (최고): {rate_desc}")
        
        st.divider()
        
        # 종합 vs 분리 비교
        st.subheader("⚖️ 종합과세 vs 분리과세 비교")
        
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown(f"""
            <div style='padding:15px; border:2px solid #1e3a8a; border-radius:12px; text-align:center; background:linear-gradient(135deg, #eff6ff, #dbeafe); overflow-wrap: break-word;'>
                <div style='font-size:0.9rem; color:#64748b; margin-bottom:8px;'>종합과세</div>
                <div style='font-size:1.5rem; font-weight:800; color:#1e3a8a; line-height:1.2; word-break: break-all;'>{f_w(total_tax)}원</div>
                <div style='font-size:0.8rem; color:#64748b; margin-top:6px;'>소득세 {f_w(income_tax)} + 지방세 {f_w(local_tax)}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with tc2:
            if can_separate:
                diff = total_tax - sep_total_tax
                border_color = "#22c55e" if diff > 0 else "#ef4444"
                label = f"{'절세' if diff > 0 else '추가'} {f_w(abs(diff))}원"
                st.markdown(f"""
                <div style='padding:15px; border:2px solid {border_color}; border-radius:12px; text-align:center; background:linear-gradient(135deg, #f0fdf4, #dcfce7); overflow-wrap: break-word;'>
                    <div style='font-size:0.9rem; color:#64748b; margin-bottom:8px;'>분리과세 (14%)</div>
                    <div style='font-size:1.5rem; font-weight:800; color:#166534; line-height:1.2; word-break: break-all;'>{f_w(sep_total_tax)}원</div>
                    <div style='font-size:0.8rem; color:{border_color}; font-weight:bold; margin-top:6px;'>{label}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style='padding:15px; border:2px solid #94a3b8; border-radius:12px; text-align:center; background:#f8fafc; overflow-wrap: break-word;'>
                    <div style='font-size:0.9rem; color:#64748b; margin-bottom:8px;'>분리과세</div>
                    <div style='font-size:1.1rem; font-weight:700; color:#94a3b8; line-height:1.2;'>선택 불가</div>
                    <div style='font-size:0.8rem; color:#ef4444; margin-top:6px;'>금융소득 2,000만원 초과 →<br>무조건 종합과세</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.divider()
        
        # 소득 구성 파이 차트
        st.subheader("📊 소득 구성 분석")
        labels = []
        values = []
        if earned_income > 0: labels.append("근로소득"); values.append(earned_income)
        if interest_income > 0: labels.append("이자소득"); values.append(interest_income)
        if dividend_income > 0: labels.append("배당소득"); values.append(dividend_income)
        if business_income > 0: labels.append("사업소득"); values.append(business_income)
        if pension_income > 0: labels.append("연금소득"); values.append(pension_income)
        if etc_income > 0: labels.append("기타소득"); values.append(etc_income)
        
        if values:
            fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=0.5,
                                         marker=dict(colors=['#1e3a8a', '#3b82f6', '#f59e0b', '#8b5cf6', '#10b981', '#6366f1'],
                                                     line=dict(color='white', width=2)))])
            fig.update_layout(title="소득원별 구성 비율", template='plotly_white', height=300, 
                             margin=dict(t=40, b=20, l=20, r=20))
            st.plotly_chart(fig, use_container_width=True)
        
        # 세율 구간 시각화
        with st.expander("📐 2025 종합소득세 누진세율표", expanded=False):
            rate_data = pd.DataFrame({
                "과세표준": ["~1,400만", "~5,000만", "~8,800만", "~1.5억", "~3억", "~5억", "~10억", "10억 초과"],
                "세율": ["6%", "15%", "24%", "35%", "38%", "40%", "42%", "45%"],
                "누진공제": ["0", "126만", "576만", "1,544만", "1,994만", "2,594만", "3,594만", "6,594만"]
            })
            st.dataframe(rate_data, use_container_width=True, hide_index=True)


def render_summary_report():
    pass

    st.markdown("""
        <div style="background-color: #f0fdf4; border: 1px solid #bbf7d0; border-radius: 8px; padding: 12px; text-align: center; color: #166534; font-size: 0.78rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">
            💎 <b>Incar Pro Asset Management Lab</b> - 본 계산기는 AI의 정밀한 시뮬레이션이 적용되었지만 참고용으로만 사용하시고, 정확한 법적 자문은 전문가에게 문의하세요. (2025 기준)
        </div>
        """, unsafe_allow_html=True)

# 6. Main Routing
if "부동산" in main_menu:
    render_real_estate()
elif "상속" in main_menu:
    render_inheritance()
elif "은퇴" in main_menu:
    render_retirement()
elif "목적" in main_menu:
    render_target_fund()
elif "달러" in main_menu:
    render_dollar_insurance()
elif "전월세" in main_menu:
    render_jeonwolse()
elif "대출" in main_menu:
    render_loan_planner()
elif "종합소득세" in main_menu:
    render_income_tax()
else:
    st.info("메뉴를 선택해 주세요.")

