import streamlit as st
import numpy as np
from dataclasses import dataclass, fields, field

# ============================================================
# 3. Utility Functions
# ============================================================

def f_w(val):
    """Format number with commas"""
    if val is None: return "0"
    return f"{int(val):,}"

def html_block(content):
    """Render HTML block via st.markdown, stripping all leading whitespace
    per line to prevent Markdown code-block interpretation."""
    lines = content.split('\n')
    stripped = '\n'.join(line.lstrip() for line in lines)
    st.markdown(stripped, unsafe_allow_html=True)

def make_sync_callback(source_key, target_key):
    """슬라이더-숫자입력 양방향 동기화 콜백 헬퍼"""
    def _sync():
        st.session_state[target_key] = st.session_state[source_key]
    return _sync

@st.cache_data(show_spinner=False)
def _run_retirement_mc(years, annual_savings, expected_return, volatility):
    """은퇴자금 몬테카를로 시뮬레이션 캐싱 래퍼 (동일 파라미터 재계산 방지)"""
    return TaxEngine.run_monte_carlo(years, 0, annual_savings, expected_return, volatility=volatility)

@st.cache_data(show_spinner=False)
def _run_retirement_mc_3phase(pay_years, defer_years, withdraw_years,
                               annual_savings, annual_withdrawal,
                               expected_return, volatility):
    """은퇴자금 3단계(납입/거치/인출) 몬테카를로 시뮬레이션 캐싱 래퍼"""
    return TaxEngine.run_monte_carlo_3phase(
        pay_years, defer_years, withdraw_years,
        annual_savings, annual_withdrawal,
        expected_return, volatility=volatility)

@st.cache_data(show_spinner=False)
def _run_tf_mc(period, annual_save, req_monthly, tf_add_prem, savings_rate, fund_rate, etf_rate, trials=200):
    """목적자금 3종 상품 몬테카를로 시뮬레이션 캐싱 래퍼"""
    fund_vol, fund_tax, fund_fee_rate = 0.15, 0.154, 0.012
    etf_vol, etf_management_fee_rate = 0.12, 0.00755
    savings_tax = 0.154
    long_periods = [3, 5, 10, 15]
    monthly_deposit = req_monthly + tf_add_prem

    savings_long, fund_long, etf_long = [], [], []
    for lp in long_periods:
        months = lp * 12
        principal = monthly_deposit * months
        pre_tax_interest = monthly_deposit * (savings_rate / 100) * months * (months + 1) / 24
        savings_long.append(principal + pre_tax_interest * (1 - savings_tax))

        f_results = []
        for _ in range(500):
            f_val = 0
            for yr in range(lp):
                ret = np.random.normal(fund_rate / 100, fund_vol)
                gain = f_val * ret
                f_val = max(0, f_val + gain - max(0, gain) * fund_tax - f_val * fund_fee_rate + annual_save)
            f_results.append(f_val)
        fund_long.append(float(np.median(f_results)))

        e_results = []
        for _ in range(500):
            e_val = 0
            for yr in range(lp):
                fee_rate = 0.075 if yr < 10 else 0.0264
                total_injected = req_monthly * (1 - fee_rate) * 12 + tf_add_prem * 12
                ret = np.random.normal(etf_rate / 100, etf_vol)
                e_val = max(0, e_val + e_val * ret - e_val * etf_management_fee_rate + total_injected)
            e_results.append(e_val)
        etf_long.append(float(np.median(e_results)))

    savings_balances = [0]
    for yr in range(period):
        months = (yr + 1) * 12
        principal = monthly_deposit * months
        pre_tax_interest = monthly_deposit * (savings_rate / 100) * months * (months + 1) / 24
        savings_balances.append(principal + pre_tax_interest * (1 - savings_tax))

    fund_scenarios, etf_scenarios = [], []
    for _ in range(trials):
        bal_f, curr_f = [0], 0
        for yr in range(period):
            ret = np.random.normal(fund_rate / 100, fund_vol)
            gain = curr_f * ret
            curr_f = max(0, curr_f + gain - max(0, gain) * fund_tax - curr_f * fund_fee_rate + annual_save)
            bal_f.append(curr_f)
        fund_scenarios.append(bal_f)

        bal_e, curr_e = [0], 0
        for yr in range(period):
            fee_rate = 0.075 if yr < 10 else 0.0264
            total_injected = req_monthly * (1 - fee_rate) * 12 + tf_add_prem * 12
            ret = np.random.normal(etf_rate / 100, etf_vol)
            curr_e = max(0, curr_e + curr_e * ret - curr_e * etf_management_fee_rate + total_injected)
            bal_e.append(curr_e)
        etf_scenarios.append(bal_e)

    fund_np = np.array(fund_scenarios)
    etf_np = np.array(etf_scenarios)
    return (
        savings_long, fund_long, etf_long, savings_balances,
        np.percentile(fund_np, 10, axis=0).tolist(),
        np.percentile(fund_np, 50, axis=0).tolist(),
        np.percentile(fund_np, 90, axis=0).tolist(),
        np.percentile(etf_np, 10, axis=0).tolist(),
        np.percentile(etf_np, 50, axis=0).tolist(),
        np.percentile(etf_np, 90, axis=0).tolist(),
    )

def solve_monthly_rate(monthly_pmt, n_pay, n_defer, target_fv):
    """이진탐색으로 목표 FV를 달성하는 월수익률 산출 (적립식+거치 정확 계산)
    - monthly_pmt: 월 납입액
    - n_pay: 납입 개월 수
    - n_defer: 거치(납입 종료 후 은퇴까지) 개월 수
    - target_fv: 목표 미래가치
    - returns: 월수익률 (float)
    """
    if monthly_pmt <= 0 or n_pay <= 0 or target_fv <= 0:
        return 0.0
    if monthly_pmt * n_pay >= target_fv:  # 0% 수익률로도 목표 달성
        return 0.0
    lo, hi = 0.0, 0.2  # 월 0~20% (연 최대 240%, 현실 범위 충분)
    for _ in range(80):  # 이진탐색 80회 → 소수점 24자리 정밀도
        r = (lo + hi) / 2
        if r < 1e-12:
            fv = monthly_pmt * n_pay
        else:
            fv_pay_end = monthly_pmt * ((1 + r) ** n_pay - 1) / r
            fv = fv_pay_end * (1 + r) ** n_defer
        if fv < target_fv:
            lo = r
        else:
            hi = r
    return (lo + hi) / 2

def get_tax_rate_5steps(base):
    """Standard 5-step detailed tax rate calculation"""
    if base <= 100_000_000: return 0.1, 0, "10% (1억원 이하)"
    elif base <= 500_000_000: return 0.2, 10_000_000, "20% (5억원 이하)"
    elif base <= 1_000_000_000: return 0.3, 60_000_000, "30% (10억원 이하)"
    elif base <= 3_000_000_000: return 0.4, 160_000_000, "40% (30억원 이하)"
    else: return 0.5, 460_000_000, "50% (30억원 초과)"

def get_capital_gains_tax_rate(base):
    """양도소득세 기본세율 (소득세법 8단계 누진세율, 6%~45%)
    주의: 상속/증여세(10~50%)와 다른 세율표입니다."""
    if base <= 0: return 0, 0, "과세표준 없음"
    brackets = [
        (14_000_000, 0.06, 0, "6% (1,400만원 이하)"),
        (50_000_000, 0.15, 1_260_000, "15% (5,000만원 이하)"),
        (88_000_000, 0.24, 5_760_000, "24% (8,800만원 이하)"),
        (150_000_000, 0.35, 15_440_000, "35% (1.5억원 이하)"),
        (300_000_000, 0.38, 19_940_000, "38% (3억원 이하)"),
        (500_000_000, 0.40, 25_940_000, "40% (5억원 이하)"),
        (1_000_000_000, 0.42, 35_940_000, "42% (10억원 이하)"),
        (float('inf'), 0.45, 65_940_000, "45% (10억원 초과)")
    ]
    for limit, rate, prog_ded, desc in brackets:
        if base <= limit:
            return rate, prog_ded, desc
    return 0.45, 65_940_000, "45% (10억원 초과)"

def f_kr(val):
    """Converts a number to Korean reading format (e.g., 12억 5,000만원)"""
    if val is None or val == 0: return "0원"
    val = int(val)
    sign = ""
    if val < 0:
        sign = "-"
        val = abs(val)
    eok = val // 100_000_000
    man = (val % 100_000_000) // 10_000
    won = val % 10_000

    res = ""
    if eok > 0: res += f"{eok}억 "
    if man > 0: res += f"{man:,.0f}만"
    if eok == 0 and man == 0:
        res = f"{val:,}원"
    elif man > 0 and won > 0:
        res += f" {won:,}원"
    else:
        res += "원"
    return (sign + res).strip()

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
            new_num = max(0, int(str(user_str).replace(",", "").strip()))
            st.session_state[num_key] = new_num
            # 다시 쉼표 포맷팅하여 표시값 업데이트
            st.session_state[str_key] = f"{new_num:,}"
        except:
            if st.session_state[num_key] == 0:
                st.session_state[str_key] = ""
            else:
                st.session_state[str_key] = f"{st.session_state[num_key]:,}"
            st.toast("⚠️ 숫자만 입력 가능합니다. 이전 값으로 복원되었습니다.", icon="⚠️")

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

# ============================================================
# Data Classes & State Management
# ============================================================

@dataclass
class RealEstateState:
    acq_area: float = 84.0
    acq_p: int = 500_000_000
    acq_h: str = "1주택"
    acq_type: str = "아파트"
    hold_p: int = 500_000_000
    hold_h: str = "1주택"
    hold_age: int = 60
    hold_y: int = 10
    yang_s: int = 600_000_000
    yang_b: int = 400_000_000
    yang_1h: bool = True
    yang_h_y: int = 1
    yang_r_y: int = 1

@dataclass
class InheritanceState:
    gif_c: int = 100_000_000
    gif_p: int = 0
    gif_d: int = 0
    gif_r: int = 0
    gif_skip: bool = False
    gif_minor: bool = False
    inh_ev: int = 1_000_000_000
    inh_d: int = 0
    inh_sp: int = 0
    inh_type: str = "일반"
    inh_f: float = 0.0

@dataclass
class RetirementState:
    ret_goal_p: int = 3_000_000
    ret_is_net: bool = False
    ret_is_mc: bool = False
    ret_is_compare: bool = False
    ret_risk_level: int = 3
    ret_age_sl: int = 60
    ret_age_num: int = 60
    life_age_sl: int = 90
    life_age_num: int = 90
    pay_years_sl: int = 10
    pay_years_num: int = 10
    ret_stress_yield_val: float = 4.0
    ret_stress_inf_val: float = 4.0
    risk_radio_ret_opt: str = "위험중립형"

@dataclass
class TargetFundState:
    tf_name: str = "자녀 대학자금"
    tf_age: int = 40
    tf_b: int = 50_000_000
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
class IncomeTaxState:
    it_salary: int = 0
    it_interest: int = 0
    it_dividend: int = 0
    it_biz: int = 0
    it_pension: int = 0
    it_other: int = 0
    it_deduction: int = 0

@dataclass
class JeonwolseState:
    jw_jeonse: int = 0
    jw_deposit: int = 0
    jw_wolse: int = 0

@dataclass
class LoanState:
    loan_amt: int = 0
    loan_rate: float = 4.0
    loan_years: int = 30

@dataclass
class SavingsState:
    dep_amount: int = 10_000_000
    dep_rate: float = 3.5
    dep_months: int = 12
    dep_tax: str = "일반과세"
    sav_amount: int = 300_000
    sav_rate: float = 3.5
    sav_months: int = 12
    sav_tax: str = "일반과세"
    sav_goal_amount: int = 0

@dataclass
class AppConfig:
    """통합 세션 상태 관리 모델 (도메인별 분리)"""
    real_estate: RealEstateState = field(default_factory=RealEstateState)
    inheritance: InheritanceState = field(default_factory=InheritanceState)
    retirement: RetirementState = field(default_factory=RetirementState)
    target_fund: TargetFundState = field(default_factory=TargetFundState)
    dollar_insurance: DollarInsuranceState = field(default_factory=DollarInsuranceState)
    income_tax: IncomeTaxState = field(default_factory=IncomeTaxState)
    jeonwolse: JeonwolseState = field(default_factory=JeonwolseState)
    loan: LoanState = field(default_factory=LoanState)
    savings: SavingsState = field(default_factory=SavingsState)
    presentation_mode: bool = False

def init_session_state():
    """객체 지향 모델을 이용한 세션 복원 및 동기화 엔진"""
    # 1. 통합 상태 모델(AppConfig) 초기화
    if 'app_state' not in st.session_state:
        st.session_state.app_state = AppConfig()

    app_state = st.session_state.app_state

    # 2. 로드 (Restore): 모든 도메인별 Dataclass 필드를 st.session_state로 매핑
    def sync_to_session(model_obj):
        for f in fields(model_obj):
            if f.name not in st.session_state:
                st.session_state[f.name] = getattr(model_obj, f.name)

    sync_to_session(app_state.real_estate)
    sync_to_session(app_state.inheritance)
    sync_to_session(app_state.retirement)
    sync_to_session(app_state.target_fund)
    sync_to_session(app_state.dollar_insurance)
    sync_to_session(app_state.savings)

    if 'presentation_mode' not in st.session_state:
        st.session_state.presentation_mode = app_state.presentation_mode

    # 특수 키 디폴트 방어 (레거시 코드 대응)
    if 'acq_p' not in st.session_state: st.session_state.acq_p = 500_000_000
    if 'hold_p' not in st.session_state: st.session_state.hold_p = 500_000_000
    if 'yang_s' not in st.session_state: st.session_state.yang_s = 600_000_000
    if 'yang_b' not in st.session_state: st.session_state.yang_b = 400_000_000
    if 'gif_c' not in st.session_state: st.session_state.gif_c = 100_000_000
    if 'inh_ev' not in st.session_state: st.session_state.inh_ev = 1_000_000_000
    if 'ret_goal_p' not in st.session_state: st.session_state.ret_goal_p = 3_000_000
    if 'tf_b' not in st.session_state: st.session_state.tf_b = 50_000_000

    # 3. 캡처 (Capture): UI에서 변경된 상태를 다시 AppConfig 객체로 동기화
    def sync_from_session(model_obj):
        for f in fields(model_obj):
            if f.name in st.session_state:
                setattr(model_obj, f.name, st.session_state[f.name])

    sync_from_session(app_state.real_estate)
    sync_from_session(app_state.inheritance)
    sync_from_session(app_state.retirement)
    sync_from_session(app_state.target_fund)
    sync_from_session(app_state.dollar_insurance)

    if 'presentation_mode' in st.session_state:
        app_state.presentation_mode = st.session_state.presentation_mode

def card_header(title):
    """카드 섹션 헤더를 렌더링합니다."""
    st.markdown(f"<div class='input-card-header'>{title}</div>", unsafe_allow_html=True)

def render_title_with_reset(title, reset_prefixes, btn_key, default_states=None):
    """탭 제목 + 초기화 버튼을 렌더링합니다.
    - title: 제목 텍스트 (예: "🏠 부동산 통합 시뮬레이터")
    - reset_prefixes: 초기화할 세션 키의 접두사 리스트 (예: ["acq_", "hold_", "yang_"])
    - btn_key: 버튼의 고유 키 (예: "reset_real_estate")
    - default_states: 기본값을 가진 dataclass 인스턴스 리스트 (예: [RealEstateState()])
    """
    col_title, col_btn = st.columns([5, 1])
    with col_title:
        # h1의 기본 border-bottom을 제거 (아래에서 전체 너비 선으로 대체)
        st.markdown(
            f"<h1 style='border-bottom:none; padding-bottom:0; margin-bottom:0;'>{title}</h1>",
            unsafe_allow_html=True
        )
    with col_btn:
        st.markdown("<div style='height: 12px'></div>", unsafe_allow_html=True)
        if st.button("🔄 초기화", key=btn_key, help="이 탭의 입력값을 초기화합니다."):
            # 1. DataClass 기반 기본값 복원
            if default_states:
                for default_obj in default_states:
                    for f in fields(default_obj):
                        default_val = getattr(default_obj, f.name)
                        st.session_state[f.name] = default_val
                        # comma_int_input이 생성하는 _str 접미사 키도 초기화
                        str_key = f"{f.name}_str"
                        if str_key in st.session_state:
                            if isinstance(default_val, int):
                                st.session_state[str_key] = "" if default_val == 0 else f"{default_val:,}"
                            else:
                                del st.session_state[str_key]

            # 2. 접두사 매칭으로 추가 키 삭제 (위젯 키, 결과 키 등)
            _system_keys = {'app_state', 'presentation_mode'}
            keys_to_delete = []
            # DataClass 필드 이름 수집 (이미 복원됐으므로 삭제 대상에서 제외)
            restored_keys = set()
            if default_states:
                for default_obj in default_states:
                    for f in fields(default_obj):
                        restored_keys.add(f.name)
                        restored_keys.add(f"{f.name}_str")

            for key in list(st.session_state.keys()):
                if key in _system_keys or key in restored_keys:
                    continue
                if key.startswith('reset_') or key.startswith('FormSubmitter:'):
                    continue
                for prefix in reset_prefixes:
                    if key.startswith(prefix):
                        keys_to_delete.append(key)
                        break

            for key in keys_to_delete:
                if key in st.session_state:
                    del st.session_state[key]

            # 3. AppConfig 동기화
            if 'app_state' in st.session_state:
                app_state = st.session_state.app_state
                if default_states:
                    for default_obj in default_states:
                        cls_name = type(default_obj).__name__
                        for attr_name in ['real_estate', 'inheritance', 'retirement', 'target_fund', 'dollar_insurance']:
                            if type(getattr(app_state, attr_name)).__name__ == cls_name:
                                setattr(app_state, attr_name, type(default_obj)())
                                break

            st.toast("🔄 초기화되었습니다.", icon="✅")
            st.rerun()
    # 전체 너비 구분선 (h1 대체)
    st.markdown(
        "<hr style='border:none; border-top:3px solid #1e3a8a; margin-top:0; margin-bottom:30px;'>",
        unsafe_allow_html=True
    )

init_session_state()

# ============================================================
# TaxEngine Class
# ============================================================

class TaxEngine:
    """Advanced Tax Logic Engine"""

    @staticmethod
    def get_acquisition_tax(price, area, method, is_adjustment):
        # 1. 법인 취득: 모든 부동산 12% 중과
        if "법인" in method:
            return 0.12, "법인 취득 중과세율 (12%)"

        # 2. 상속 취득
        if "상속" in method:
            if "농지" in method:
                return 0.023, "농지 상속 세율 (2.3%)"
            else:
                return 0.028, "상속 취득세율 (2.8%)"

        # 3. 증여 취득
        if "증여" in method:
            if "농지" in method:
                return 0.028, "농지 증여 세율 (2.8%)"
            # 주택 증여: 조정대상지역 다주택 중과 적용
            if "2주택" in method and is_adjustment:
                return 0.08, "조정지역 2주택 증여 중과 (8%)"
            if ("3주택" in method or "4주택" in method) and is_adjustment:
                return 0.12, "조정지역 3주택+ 증여 중과 (12%)"
            return 0.035, "주택 증여 취득세율 (3.5%)"

        # 4. 농지 매매
        if "농지" in method:
            if "자경" in method:
                return 0.015, "농지 자경 세율 (1.5%)"
            else:
                return 0.03, "농지 비자경 세율 (3%)"

        # 5. 주택 매매
        if "주택" in method:
            if price <= 600_000_000:
                base_rate = 0.01
                desc = "1주택 기본세율 (1%)"
            elif price <= 900_000_000:
                base_rate = (price * 2 / 300_000_000 - 3) / 100
                desc = f"1주택 구간세율 ({base_rate*100:.2f}%)"
            else:
                base_rate = 0.03
                desc = "1주택 기본세율 (3%)"

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

        # 6. 기타 (토지/상가 등)
        return 0.04, "기본세율 (4%)"

    @staticmethod
    def get_long_term_deduction(holding_years, residence_years, is_1house_1family):
        # Table 1: General (Max 30% / 15Y) - 2% per year
        # Table 2: 1-House + Residence 2Y+ (Max 80% / 10Y) - 4% + 4%

        rate = 0
        desc = "미적용"

        if holding_years < 3:
            return 0, "보유 3년 미만 (0%)"

        if is_1house_1family and residence_years >= 2:
            # Table 2: 보유 연 4% + 거주 연 4%, 각 최대 40% (10년 상한)
            # 거주기간은 보유기간을 초과할 수 없음
            residence_years = min(residence_years, holding_years)
            h_rate = min(0.4, holding_years * 0.04)
            r_rate = min(0.4, residence_years * 0.04)
            rate = h_rate + r_rate
            desc = f"1세대 1주택 특례 ({int(rate*100)}% = 보유{int(h_rate*100)}% + 거주{int(r_rate*100)}%) / 보유·거주 각 10년 이상 시 최대 80%"
        else:
            # Table 1
            rate = min(0.3, holding_years * 0.02)
            desc = f"일반 공제 ({int(rate*100)}% / 년 2%)"

        return rate, desc

    @staticmethod
    def get_generation_skipping_surcharge(tax, is_skipping, is_minor_and_high_val, tax_base=0):
        """
        世代省略 (Generation Skipping)
        30% Surcharge, 40% if minor and > 2B KRW
        """
        if not is_skipping:
            return 0, "미부과"

        surcharge_rate = 0.3
        desc = "세대생략 할증 (30%)"

        # 미성년자가 20억원 초과 증여/상속 시에만 40% 할증 적용
        if is_minor_and_high_val and tax_base > 2_000_000_000:
            surcharge_rate = 0.4
            desc = "세대생략 할증 (40%, 미성년+20억 초과)"

        return tax * surcharge_rate, desc

    @staticmethod
    def run_monte_carlo(years, initial_capital, annual_savings, expected_return, volatility=0.10, trials=200):
        """
        Monte Carlo Simulation for Asset Projection
        volatility: standard deviation of annual returns (e.g. 10%)
        """
        all_scenarios = []
        for _ in range(trials):
            balances = [initial_capital]
            for _ in range(years):
                # Using normal distribution for returns
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
    def run_monte_carlo_3phase(pay_years, defer_years, withdraw_years,
                                annual_savings, annual_withdrawal,
                                expected_return, volatility=0.10, trials=200):
        """3단계(납입/거치/인출) 몬테카를로 시뮬레이션
        - pay_years: 납입기 (매년 annual_savings 적립)
        - defer_years: 거치기 (운용만, 납입/인출 없음)
        - withdraw_years: 인출기 (매년 annual_withdrawal 인출)
        """
        total_years = pay_years + defer_years + withdraw_years
        if total_years <= 0:
            return np.array([0]), np.array([0]), np.array([0])
        all_scenarios = []
        for _ in range(trials):
            balances = [0]
            for yr in range(total_years):
                actual_return = np.random.normal(expected_return / 100, volatility)
                prev = balances[-1]
                if yr < pay_years:
                    new_bal = prev * (1 + actual_return) + annual_savings
                elif yr < pay_years + defer_years:
                    new_bal = prev * (1 + actual_return)
                else:
                    new_bal = prev * (1 + actual_return) - annual_withdrawal
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
    def get_jongbu_tax(base, is_multi_home=False):
        """종합부동산세 누진세율 계산 (2025 기준)
        Returns: (종부세, 세율_desc, 농어촌특별세)
        농어촌특별세 = 종부세의 20%
        is_multi_home: True → 3주택 이상 중과세율 적용
        """
        if base <= 0:
            return 0, "과세표준 없음", 0
        if is_multi_home:
            # 3주택 이상 중과세율 (2025 기준)
            brackets = [
                (300_000_000, 0.005, 0),
                (600_000_000, 0.007, 600_000),
                (1_200_000_000, 0.010, 2_400_000),
                (2_500_000_000, 0.014, 7_200_000),
                (5_000_000_000, 0.015, 9_700_000),
                (9_400_000_000, 0.020, 34_700_000),
                (float('inf'), 0.027, 100_500_000)
            ]
        else:
            # 일반세율 (2주택 이하)
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
                tax = max(0, base * rate - prog_ded)
                suffix = " (다주택 중과)" if is_multi_home else ""
                return tax, f"{rate*100:.1f}%{suffix}", tax * 0.20
        rate = brackets[-1][1]
        prog_ded = brackets[-1][2]
        tax = max(0, base * rate - prog_ded)
        suffix = " (다주택 중과)" if is_multi_home else ""
        return tax, f"{rate*100:.1f}%{suffix}", tax * 0.20

    @staticmethod
    def get_property_tax(off_price, is_single_home=False):
        """재산세 간이 계산 (주택분)
        Returns: (base_tax, edu_tax, city_tax, total_tax)
        - base_tax: 재산세 본세
        - edu_tax: 지방교육세 (20%)
        - city_tax: 도시지역분 (0.14%)
        - total_tax: 합계
        - is_single_home: True면 1세대1주택 특례세율 적용 (공시가 9억 이하)
        """
        # 과세표준 = 공시가격 × 공정시장가액비율(60%)
        tax_base = off_price * 0.6
        if is_single_home and off_price <= 900_000_000:
            # 1세대 1주택 특례세율 (공시가 9억 이하)
            if tax_base <= 60_000_000:
                base_tax = tax_base * 0.0005
            elif tax_base <= 150_000_000:
                base_tax = 30_000 + (tax_base - 60_000_000) * 0.001
            elif tax_base <= 300_000_000:
                base_tax = 120_000 + (tax_base - 150_000_000) * 0.002
            else:
                base_tax = 420_000 + (tax_base - 300_000_000) * 0.0035
        else:
            # 일반 세율
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



