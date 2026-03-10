import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core import f_w, f_kr, show_kr_label, comma_int_input, TaxEngine, render_ai_doctor, html_block
from core import _run_retirement_mc, make_sync_callback
from core import solve_monthly_rate

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
                current_age = c_age.number_input("현재 나이", min_value=20, max_value=100, value=40, key="ret_age")
                goal_p = comma_int_input("희망 월 생활비 (현재가치/원)", st.session_state.ret_goal_p, "ret_goal_p")
    else:
        client_name = st.session_state.get('ret_name', "")
        current_age = st.session_state.get('ret_age', 40)
        goal_p = st.session_state.get('ret_goal_p', 3_000_000)

    display_name = client_name.strip() if client_name.strip() else "고객"


    if not st.session_state.presentation_mode:
        with col_input:
            # 2. Timeline
            st.markdown("##### 2. 은퇴 타임라인")

            # Helper callbacks for sync
            if 'pay_years_sl' not in st.session_state: st.session_state.pay_years_sl = 10
            if 'pay_years_num' not in st.session_state: st.session_state.pay_years_num = 10
            if 'ret_age_sl' not in st.session_state: st.session_state.ret_age_sl = 60
            if 'ret_age_num' not in st.session_state: st.session_state.ret_age_num = 60
            if 'life_age_sl' not in st.session_state: st.session_state.life_age_sl = 90
            if 'life_age_num' not in st.session_state: st.session_state.life_age_num = 90

            # UI Rendering (Reordered)
            y_s_limit = max(1, st.session_state.ret_age_sl - current_age)

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
            st.markdown("##### 3. 재무 변수")

            # Sync for Financials
            if 'inf_sl' not in st.session_state: st.session_state.inf_sl = 3.0
            if 'inf_num' not in st.session_state: st.session_state.inf_num = 3.0
            if 'yield_sl' not in st.session_state: st.session_state.yield_sl = 6.0
            if 'yield_num' not in st.session_state: st.session_state.yield_num = 6.0

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

    if retire_age <= current_age:
        st.error(f"❌ 은퇴 나이({retire_age}세)가 현재 나이({current_age}세) 이하입니다. 은퇴 나이를 현재 나이보다 높게 설정해주세요.")
        return
    if retire_age >= yy_life:
        st.error(f"❌ 은퇴 나이({retire_age}세)가 기대 수명({yy_life}세) 이상입니다. 기대 수명을 더 높게 설정해주세요.")
        return
    if y_def < 0: y_def = 0

    # Message (Only in Design Mode)
    if not st.session_state.presentation_mode:
        st.caption(f"💡 {display_name}님은 **{pay_years}년**간 납입, **{y_def}년** 거치 후 **{y_d}년**간 연금을 수령합니다.")

    # Logic Adjustments
    actual_yield = yield_r * 0.846 if is_net_return else yield_r


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

    # Back Calculation (Goal Seek)
    with st.expander("🎯 역산 엔진 (목표 자산 역산)"):
        target_lump = comma_int_input("목표 은퇴 자산(원)", int(lump_sum_need), "ret_target_lump_reverse")
        if monthly_save > 0 and n_months_pay > 0:
            _r_monthly = solve_monthly_rate(monthly_save, n_months_pay, n_months_defer, target_lump)
            req_yield_seek = _r_monthly * 12 * 100
            st.info(f"💡 {f_w(target_lump)}원을 만드려면 연 {req_yield_seek:.2f}%의 수익률이 필요합니다.")


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
                gain = curr_stress * (actual_stress_yield/100)
                if age_v < current_age + pay_years:
                    curr_stress = curr_stress + gain + monthly_save * 12
                elif age_v < retire_age:
                    curr_stress = curr_stress + gain  # 거치기간: 복리만
                else:
                    curr_stress = curr_stress + gain - stress_goal_f * 12

            fig.add_trace(go.Scatter(
                x=years_v, y=stress_wealth,
                name=f'시나리오 B (수익률 {s_yield}%, 물가 {s_inf}%)',
                line=dict(color='#ef4444', width=2, dash='dash')
            ))

            # Brief Summary for Scenario B
            st.info(f"🚩 시나리오 B 적용 시, 은퇴 시점 필요 자금은 **{f_w(stress_goal_f * ((1 - (1 + (actual_stress_yield/100/12)) ** (-y_d*12)) / (actual_stress_yield/100/12)) if actual_stress_yield > 0 else stress_goal_f * y_d * 12)}원**으로 변동됩니다.")

        st.plotly_chart(fig)

        # Monte Carlo Section
        if is_monte_carlo:
            st.divider()
            st.subheader("🎲 몬테카를로 스트레스 테스트 결과")
            vol = {1: 0.05, 2: 0.08, 3: 0.12, 4: 0.18, 5: 0.25}.get(risk_level, 0.12)

            p10, p50, p90 = _run_retirement_mc(
                yy_life - current_age,
                monthly_save * 12,
                actual_yield,
                vol
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
            st.plotly_chart(mc_fig)
            st.caption(f"※ 투자 성향({['안정', '안정추구', '중립', '적극', '공격'][risk_level-1]})에 따른 변동성 {vol*100}%를 적용한 200회 시뮬레이션 결과입니다.")

    # --- End of Top Columns ---

    # --- Row 2: Portfolio Recommendation ---
    st.divider()
    with st.expander("📊 맞춤형 포트폴리오 제안", expanded=False):
        if risk_level:
            risk_type = st.radio("투자 성향 선택 (실시간)", ["위험안정형", "위험중립형", "위험선호형"], horizontal=True, key="risk_radio_ret_opt")
            risk_map = {"위험안정형": 1, "위험중립형": 3, "위험선호형": 5}
            risk_score = risk_map[risk_type]

            rec = TaxEngine.get_portfolio_recommendation(risk_score)

            c_p1, c_p2 = st.columns([1, 2])
            with c_p1:
                html_block(f"""
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
                """)

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
                st.plotly_chart(fig_port)

    # --- Row 3: Monte Carlo (Full Width) ---
    if is_monte_carlo:
        st.divider()
        st.subheader("🎲 몬테카를로 리스크 분석")

        _vol = {1: 0.05, 2: 0.08, 3: 0.12, 4: 0.18, 5: 0.25}.get(risk_level, 0.12)
        p10, p50, p90 = _run_retirement_mc(y_s + y_d, monthly_save * 12, actual_yield, _vol)
        mc_years = list(range(current_age, current_age + len(p10)))

        _mc_cards = [
            ("최악의 시나리오<br><span style='font-size:0.7rem;color:#64748b;'>(하위 10%)</span>", f"{f_w(p10[-1])} 원", "목표 미달 가능성", "#ef4444", "#fef2f2", "#fecaca"),
            ("평균적 시나리오<br><span style='font-size:0.7rem;color:#64748b;'>(중위 값)</span>", f"{f_w(p50[-1])} 원", "예상 자산 잔존액", "#1e3a8a", "#f8fafc", "#e2e8f0"),
            ("최상의 시나리오<br><span style='font-size:0.7rem;color:#64748b;'>(상위 10%)</span>", f"{f_w(p90[-1])} 원", "초과 달성 예상", "#16a34a", "#f0fdf4", "#bbf7d0"),
        ]
        _mc_html = "<div style='display:flex;flex-wrap:wrap;gap:10px;'>"
        for _lbl, _val, _delta, _color, _bg, _border in _mc_cards:
            _mc_html += f"""
            <div style='flex:1;min-width:150px;background:{_bg};border-radius:10px;padding:14px 12px;border:1px solid {_border};box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;line-height:1.4;'>{_lbl}</div>
                <div style='font-size:1.1rem;font-weight:800;color:{_color};word-break:break-all;'>{_val}</div>
                <div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>{_delta}</div>
            </div>"""
        _mc_html += "</div>"
        st.markdown(_mc_html, unsafe_allow_html=True)

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
        st.plotly_chart(fig_mc)

        with st.expander("ℹ️ 몬테카를로 분석이란?", expanded=False):
             st.markdown("불확실한 투자 시장의 변동성을 반영하여 200번의 시뮬레이션을 수행한 결과입니다. 하위 10% 시나리오에서도 자산이 고갈되지 않는지 확인하세요.")

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
        st.plotly_chart(fig_comp)

    # --- Row 5: Detailed Report ---
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

    # AI Doctor Call
    render_ai_doctor("은퇴설계", {'goal': goal_f, 'saved': monthly_save})
