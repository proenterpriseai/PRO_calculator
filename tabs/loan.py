import streamlit as st
import plotly.graph_objects as go
from core import f_w, comma_int_input, html_block, render_title_with_reset, card_header, LoanState


def render_loan_planner():
    """대출 상환 설계"""
    render_title_with_reset("🏦 대출 상환 설계", ["loan_"], "reset_loan", default_states=[LoanState()])
    st.markdown("원리금균등, 원금균등, 만기일시상환 3가지 상환 방식을 **한눈에 비교**합니다.")

    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")

    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 대출 조건 입력")
            card_header("💰 대출 조건")
            with st.container(border=True):
                loan_amount = comma_int_input("대출 원금 (원)", 0, "loan_amt")
                loan_rate = st.slider("연 이자율 (%)", 1.0, 15.0, 4.0, step=0.1, key="loan_rate")
                loan_years = st.slider("대출 기간 (년)", 1, 40, 30, key="loan_years")
    else:
        loan_amount = st.session_state.get('loan_amt', 300_000_000)
        loan_rate = st.session_state.get('loan_rate', 4.0)
        loan_years = st.session_state.get('loan_years', 30)

    # 계산
    monthly_rate = loan_rate / 100 / 12
    total_months = loan_years * 12

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
            st.plotly_chart(fig2)
    total_interest_equal = pmt_equal * total_months - loan_amount

    # 2. 원금균등
    monthly_principal = loan_amount / total_months if total_months > 0 else 0
    total_interest_principal = 0
    for m in range(total_months):
        remain = loan_amount - monthly_principal * m
        total_interest_principal += remain * monthly_rate
    first_payment_principal = monthly_principal + loan_amount * monthly_rate
    last_payment_principal = monthly_principal + monthly_principal * monthly_rate

    # 3. 만기일시상환: 매월 이자만 납부, 만기에 원금 전액 상환
    bullet_monthly = loan_amount * monthly_rate  # 매월 이자
    total_interest_bullet = bullet_monthly * total_months  # 총 이자

    with col_result:
        st.subheader("📊 상환 비교 분석")

        _loan_cards = [
            ("원리금균등 월 납입", f"{f_w(pmt_equal)} 원", f"총이자 {f_w(total_interest_equal)}", "#1e3a8a"),
            ("원금균등 초회 납입", f"{f_w(first_payment_principal)} 원", f"총이자 {f_w(total_interest_principal)}", "#3b82f6"),
            ("만기일시상환 월 이자", f"{f_w(bullet_monthly)} 원", f"총이자 {f_w(total_interest_bullet)}", "#6366f1"),
        ]
        _loan_html = "<div style='display:flex;flex-wrap:wrap;gap:10px;'>"
        for _lbl, _val, _delta, _color in _loan_cards:
            _loan_html += f"""
            <div style='flex:1;min-width:150px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>{_lbl}</div>
                <div style='font-size:1.1rem;font-weight:800;color:{_color};word-break:break-all;'>{_val}</div>
                <div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>{_delta}</div>
            </div>"""
        _loan_html += "</div>"
        st.markdown(_loan_html, unsafe_allow_html=True)

        # 이자 비교 차트
        st.divider()
        st.subheader("💰 총 이자 비교")

        methods = ['원리금균등', '원금균등', '만기일시상환']
        interests = [total_interest_equal, total_interest_principal, total_interest_bullet]
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
        st.plotly_chart(fig)

        # 상세 리포트
        with st.expander("📝 상세 분석 리포트", expanded=True):
            savings = total_interest_bullet - total_interest_principal
            html_block(f"""
            <div class='expert-card'>
                <div class='expert-title'>🏦 상환 전략 분석</div>
                <div class='step-box'>
                    <div class='step-title'>💡 핵심 인사이트</div>
                    <div class='step-content'>
                        원금균등 방식이 총 이자를 가장 적게 지불합니다.<br>
                        만기일시상환 대비 <span class='highlight'>{f_w(savings)}원</span> 이자 절감 가능합니다.<br>
                        다만, 원리금균등은 매월 동일 금액으로 계획적 상환에 유리합니다.<br>
                        만기일시상환은 매월 이자만 납부하므로 월 부담이 가장 적지만, 만기 시 원금 전액을 상환해야 합니다.
                    </div>
                </div>
            </div>
            """)
