import streamlit as st
import plotly.graph_objects as go
from core import f_w, f_kr, comma_int_input, TaxEngine, html_block, render_title_with_reset, RetirementState, card_header
from core import _run_retirement_mc_3phase, make_sync_callback
from core import solve_monthly_rate

def render_retirement():
    render_title_with_reset("⏳ 은퇴자금 계산", ["ret_", "pay_years_", "life_age_", "inf_", "yield_", "risk_radio_ret", "result_ret"], "reset_retirement", default_states=[RetirementState()])
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
            card_header("👤 고객정보")
            with st.container(border=True):
                c_name, c_age = st.columns([1.5, 1])
                client_name = c_name.text_input("고객 성함", "", key="ret_name")
                current_age = c_age.number_input("현재 나이", min_value=20, max_value=100, value=20, key="ret_age")
                goal_p = comma_int_input("희망 월 생활비 (현재가치/원)", st.session_state.ret_goal_p, "ret_goal_p")
                # 목표 은퇴 자산 표시 placeholder (계산 후 채워짐)
                _ph_target_asset = st.empty()
    else:
        client_name = st.session_state.get('ret_name', "")
        current_age = st.session_state.get('ret_age', 20)
        goal_p = st.session_state.get('ret_goal_p', 3_000_000)
        _ph_target_asset = None

    display_name = client_name.strip() if client_name.strip() else "고객"


    if not st.session_state.presentation_mode:
        with col_input:
            # 2. Timeline
            card_header("📅 은퇴 타임라인")

            # Helper callbacks for sync
            if 'pay_years_sl' not in st.session_state: st.session_state.pay_years_sl = 10
            if 'pay_years_num' not in st.session_state: st.session_state.pay_years_num = 10
            if 'ret_age_sl' not in st.session_state: st.session_state.ret_age_sl = 65
            if 'ret_age_num' not in st.session_state: st.session_state.ret_age_num = 65
            if 'life_age_sl' not in st.session_state: st.session_state.life_age_sl = 100
            if 'life_age_num' not in st.session_state: st.session_state.life_age_num = 100

            # UI Rendering (Reordered)
            y_s_limit = max(1, st.session_state.ret_age_sl - current_age)

            with st.container(border=True):
                c_p1, c_p2 = st.columns([2, 1])
                with c_p1: st.slider("납입 기간 (년)", min_value=1, max_value=max(y_s_limit, 2), key='pay_years_sl', disabled=(y_s_limit <= 1), on_change=make_sync_callback('pay_years_sl', 'pay_years_num'))
                with c_p2:
                    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                    st.number_input("납입 기간 입력", min_value=1, max_value=max(y_s_limit, 1), key='pay_years_num', label_visibility="collapsed", on_change=make_sync_callback('pay_years_num', 'pay_years_sl'))

                c1, c2 = st.columns([2, 1])
                with c1: st.slider("은퇴 목표 나이", min_value=current_age, max_value=max(90, current_age + 1), key='ret_age_sl', on_change=make_sync_callback('ret_age_sl', 'ret_age_num'))
                with c2:
                    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                    st.number_input("은퇴 나이(세)", min_value=current_age, max_value=max(90, current_age), key='ret_age_num', label_visibility="collapsed", on_change=make_sync_callback('ret_age_num', 'ret_age_sl'))

                c3, c4 = st.columns([2, 1])
                with c3: st.slider("기대 수명 (은퇴 종료)", min_value=current_age, max_value=max(110, current_age + 1), key='life_age_sl', on_change=make_sync_callback('life_age_sl', 'life_age_num'))
                with c4:
                    st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)
                    st.number_input("기대 수명(세)", min_value=current_age, max_value=max(110, current_age), key='life_age_num', label_visibility="collapsed", on_change=make_sync_callback('life_age_num', 'life_age_sl'))

            # 3. Financials
            card_header("📊 재무 변수")

            # Sync for Financials
            if 'inf_sl' not in st.session_state: st.session_state.inf_sl = 3.0
            if 'inf_num' not in st.session_state: st.session_state.inf_num = 3.0
            if 'yield_sl' not in st.session_state: st.session_state.yield_sl = 6.0
            if 'yield_num' not in st.session_state: st.session_state.yield_num = 6.0

            with st.container(border=True):
                c_a, c_b = st.columns(2)
                with c_a:
                    st.markdown("물가상승률(%)")
                    c_a1, c_a2 = st.columns([2, 1])
                    inf = c_a1.slider("물가상승률", min_value=0.0, max_value=50.0, step=0.1, label_visibility="collapsed", key='inf_sl', on_change=make_sync_callback('inf_sl', 'inf_num'))
                    inf = c_a2.number_input("물가상승률 입력", min_value=0.0, max_value=50.0, step=0.1, label_visibility="collapsed", key='inf_num', on_change=make_sync_callback('inf_num', 'inf_sl'))

                with c_b:
                    st.markdown("투자수익률(%)")
                    c_b1, c_b2 = st.columns([2, 1])
                    yield_r = c_b1.slider("투자수익률", min_value=0.0, max_value=30.0, step=0.1, label_visibility="collapsed", key='yield_sl', on_change=make_sync_callback('yield_sl', 'yield_num'))
                    yield_r = c_b2.number_input("투자수익률 입력", min_value=0.0, max_value=100.0, step=0.1, label_visibility="collapsed", key='yield_num', on_change=make_sync_callback('yield_num', 'yield_sl'))
                    if yield_r > 20:
                        st.warning(f"⚠️ 연 {yield_r:.1f}%는 매우 높은 수익률입니다. 실제 시장 성과와 일치하는지 확인하세요.")

    # Variables extraction
    retire_age = st.session_state.ret_age_sl if 'ret_age_sl' in st.session_state else 65
    yy_life = st.session_state.life_age_sl if 'life_age_sl' in st.session_state else 100
    inf = st.session_state.inf_sl if 'inf_sl' in st.session_state else 3.0
    yield_r = st.session_state.yield_sl if 'yield_sl' in st.session_state else 6.0

    goal_p = st.session_state.ret_goal_p if 'ret_goal_p' in st.session_state else 3_000_000

    # New Period Variables
    y_s = retire_age - current_age # Total to Retirement
    pay_years = st.session_state.pay_years_sl if 'pay_years_sl' in st.session_state else min(10, y_s)
    y_def = y_s - pay_years         # Deferral Years
    y_d = yy_life - retire_age     # Decumulation Years

    if retire_age <= current_age:
        st.error(f"❌ 은퇴 나이({retire_age}세)가 현재 나이({current_age}세) 이하입니다. 은퇴 나이를 현재 나이보다 높게 설정해주세요.")
        return
    if retire_age >= yy_life:
        st.error(f"❌ 은퇴 나이({retire_age}세)가 기대 수명({yy_life}세) 이상입니다. 기대 수명을 더 높게 설정해주세요.")
        return
    if y_def < 0: y_def = 0
    if pay_years >= y_s and not st.session_state.presentation_mode:
        st.warning(f"⚠️ 납입 기간({pay_years}년)이 은퇴까지 남은 기간({y_s}년)과 같거나 초과합니다. 거치 기간 없이 은퇴 즉시 연금 수령이 시작됩니다.")

    # Message (Only in Design Mode)
    if not st.session_state.presentation_mode:
        st.caption(f"💡 {display_name}님은 **{pay_years}년**간 납입, **{y_def}년** 거치 후 **{y_d}년**간 연금을 수령합니다.")

    actual_yield = yield_r


    # Logic
    goal_f = goal_p * (1 + inf/100)**y_s
    n_months_retire = y_d * 12
    monthly_yield = round(actual_yield / 100 / 12, 10)

    # 1. Lump sum needed at Retirement Age (T=retire_age)
    if monthly_yield == 0:
        lump_sum_need = round(goal_f * n_months_retire)
    else:
        lump_sum_need = round(goal_f * ((1 - (1 + monthly_yield) ** (-n_months_retire)) / monthly_yield))

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
        monthly_save = round(v_pay_end_needed / n_months_pay) if n_months_pay > 0 else 0
    else:
        monthly_save = round(v_pay_end_needed * monthly_yield / ((1 + monthly_yield) ** n_months_pay - 1)) if n_months_pay > 0 else 0

    # 목표 은퇴 자산 표시 (입력 영역 placeholder에 채우기)
    if _ph_target_asset is not None:
        with _ph_target_asset.container():
            st.markdown(f"<div style='background:#f0f9ff;border-left:3px solid #3b82f6;padding:10px 14px;border-radius:6px;margin-top:4px;margin-bottom:8px;'>"
                        f"<span style='font-size:12px;color:#64748b;'>목표 은퇴 자산 (자동 계산)</span><br>"
                        f"<span style='font-size:18px;font-weight:700;color:#1e3a8a;'>{f_w(lump_sum_need)}원</span>"
                        f"<span style='font-size:11px;color:#94a3b8;'> ({retire_age}세~{yy_life}세, {y_d}년간)</span>"
                        f"</div>", unsafe_allow_html=True)


    with col_result:
        st.subheader(f"📊 {display_name}님의 은퇴 설계 분석")

        _ret_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;margin-bottom:12px;'>
        <div style='flex:1;min-width:180px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
            <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>{retire_age}세 시점 월 생활비</div>
            <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(goal_f)} 원</div>
            <div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>물가상승 반영</div>
        </div>
        <div style='flex:1;min-width:180px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
            <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>필요 은퇴 자금 (총액)<br><span style='font-size:0.72rem;'>({retire_age}세 ~ {yy_life}세, {y_d}년간)</span></div>
            <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(lump_sum_need)} 원</div>
        </div></div>
        <div style='background:linear-gradient(135deg,#1e3a8a,#3b82f6);border-radius:10px;padding:16px;color:white;box-shadow:0 2px 6px rgba(30,58,138,0.15);'>
            <div style='font-size:0.85rem;font-weight:600;opacity:0.9;margin-bottom:6px;'>💡 매월 필요 저축액 ({current_age}세 ~ {current_age + pay_years}세, {pay_years}년간)</div>
            <div style='font-size:1.3rem;font-weight:800;word-break:break-all;'>{f_w(monthly_save)} 원</div>
            <div style='font-size:0.78rem;opacity:0.8;margin-top:4px;'>{y_def}년 거치 포함</div>
        </div>"""
        st.markdown(_ret_html, unsafe_allow_html=True)

        # 1. Asset Growth Curve (Main Chart)
        years_v = list(range(current_age, yy_life + 1))
        wealth_v = []
        curr_bal_v = 0

        for age_v in years_v:
            wealth_v.append(curr_bal_v)
            if age_v < current_age + pay_years:
                # 1. Payment Phase (월 복리 + 매월 적립)
                if monthly_yield > 0:
                    curr_bal_v = curr_bal_v * (1 + monthly_yield)**12 + monthly_save * ((1 + monthly_yield)**12 - 1) / monthly_yield
                else:
                    curr_bal_v = curr_bal_v + monthly_save * 12
            elif age_v < retire_age:
                # 2. Deferral Phase (월 복리)
                curr_bal_v = curr_bal_v * (1 + monthly_yield)**12
            else:
                # 3. Withdrawal Phase (월 복리 - 매월 인출)
                if monthly_yield > 0:
                    curr_bal_v = curr_bal_v * (1 + monthly_yield)**12 - goal_f * ((1 + monthly_yield)**12 - 1) / monthly_yield
                else:
                    curr_bal_v = curr_bal_v - goal_f * 12

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
            title=dict(text=f"📈 {display_name}님의 자산 생애 주기", font=dict(size=18, color="#1e293b")),
            xaxis=dict(title="나이 (세)", showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(title="자산 규모 (원)", showgrid=True, gridcolor='#f1f5f9'),
            plot_bgcolor='rgba(255,255,255,0)',
            paper_bgcolor='white',
            height=380,
            margin=dict(l=20,r=20,t=60,b=20),
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )

        st.plotly_chart(fig)

    # --- End of Top Columns ---

    # --- Detailed Report ---
    with st.expander("📝 은퇴 설계 상세 리포트", expanded=False):
        html_block(f"""
        <div class='expert-card'>
            <div class='expert-title'>📑 {display_name}님을 위한 로드맵</div>
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
        """)

    # 결과 저장 (전략 보고서용)
    st.session_state['result_ret_monthly'] = monthly_save
    st.session_state['result_ret_lump'] = lump_sum_need
    st.session_state['result_ret_goal'] = goal_f


