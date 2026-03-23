import streamlit as st
import plotly.graph_objects as go
from core import f_w, f_kr, comma_int_input, make_sync_callback, TaxEngine, _run_tf_mc, html_block, render_title_with_reset, TargetFundState, card_header


def render_target_fund():
    render_title_with_reset("🎯 목적자금 계산", ["tf_"], "reset_target_fund", default_states=[TargetFundState()])
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
            card_header("👤 고객정보")
            with st.container(border=True):
                c_name, c_age = st.columns([1.5, 1])
                client_name = c_name.text_input("고객 성함", "", key="tf_name")
                current_age = c_age.number_input("현재 나이", min_value=20, max_value=100, value=40, key="tf_age")

            card_header("🎯 목표 설정")
            with st.container(border=True):
                calc_type = st.radio("계산 방식 선택", ["목표 필요 자금", "매월 저축(투자) 금액"], key="tf_calc_type", horizontal=True)
                if calc_type == "목표 필요 자금":
                    target_amt = comma_int_input("목표 금액(원)", st.session_state.tf_b, "tf_b")
                    input_monthly = st.session_state.get('tf_monthly_input', 0)
                else:
                    input_monthly = comma_int_input("매월 저축(투자) 금액(원)", st.session_state.get('tf_monthly_input', 1000000), "tf_monthly_input")
                    target_amt = st.session_state.get('tf_b', 0)
    else:
        client_name = st.session_state.get('tf_name', "")
        current_age = st.session_state.get('tf_age', 40)
        calc_type = st.session_state.get('tf_calc_type', "목표 필요 자금")
        target_amt = st.session_state.get('tf_b', 100_000_000)
        input_monthly = st.session_state.get('tf_monthly_input', 1000000)

    display_name = client_name.strip() if client_name.strip() else "고객"
    
    # Sync for Target Fund
    if 'tf_period_sl' not in st.session_state: st.session_state.tf_period_sl = 5
    if 'tf_period_num' not in st.session_state: st.session_state.tf_period_num = 5
    if 'tf_sav_rate_sl' not in st.session_state: st.session_state.tf_sav_rate_sl = 2.5
    if 'tf_sav_rate_num' not in st.session_state: st.session_state.tf_sav_rate_num = 2.5
    if 'tf_rate_sl' not in st.session_state: st.session_state.tf_rate_sl = 5.0
    if 'tf_rate_num' not in st.session_state: st.session_state.tf_rate_num = 5.0

    if not st.session_state.presentation_mode:
        with col_input:
            card_header("📊 수익률 설정")
            with st.container(border=True):
                st.markdown("준비 기간(년)")
                c1, c2 = st.columns([2, 1])
                with c1: period = st.slider("준비 기간", min_value=1, max_value=30, key='tf_period_sl', label_visibility="collapsed", on_change=make_sync_callback('tf_period_sl', 'tf_period_num'))
                with c2: period = st.number_input("기간 입력", min_value=1, max_value=30, key='tf_period_num', label_visibility="collapsed", on_change=make_sync_callback('tf_period_num', 'tf_period_sl'))

                st.markdown("적금 금리(%)")
                cs1, cs2 = st.columns([2, 1])
                with cs1: top_sav_rate = st.slider("적금 금리", min_value=0.0, max_value=100.0, step=0.1, key='tf_sav_rate_sl', label_visibility="collapsed", on_change=make_sync_callback('tf_sav_rate_sl', 'tf_sav_rate_num'))
                with cs2: top_sav_rate = st.number_input("적금 금리 입력", min_value=0.0, max_value=100.0, step=0.1, key='tf_sav_rate_num', label_visibility="collapsed", on_change=make_sync_callback('tf_sav_rate_num', 'tf_sav_rate_sl'))

                st.markdown("기대 수익률(%)")
                c3, c4 = st.columns([2, 1])
                with c3: rate = st.slider("기대 수익률", min_value=0.0, max_value=100.0, step=0.1, key='tf_rate_sl', label_visibility="collapsed", on_change=make_sync_callback('tf_rate_sl', 'tf_rate_num'))
                with c4: rate = st.number_input("수익률 입력", min_value=0.0, max_value=100.0, step=0.1, key='tf_rate_num', label_visibility="collapsed", on_change=make_sync_callback('tf_rate_num', 'tf_rate_sl'))
            
            st.markdown("---")
            # Removed 세후 수익률 적용
    else:
        # Read from state
        period = st.session_state.get('tf_period_sl', 5)
        top_sav_rate = st.session_state.get('tf_sav_rate_sl', 2.5)
        rate = st.session_state.get('tf_rate_sl', 5.0)

    actual_rate = rate
        
    # Logic
    monthly_rate = round(actual_rate / 100 / 12, 10)
    months = period * 12
    sav_r = top_sav_rate / 100

    if calc_type == "목표 필요 자금":
        if monthly_rate == 0:
            req_monthly = round(target_amt / months)
        else:
            req_monthly = round(target_amt * monthly_rate / ((1 + monthly_rate)**months - 1))
        expected_total = target_amt
        
        if sav_r == 0:
            sav_req_monthly = round(target_amt / months)
        else:
            sav_req_monthly = round(target_amt / (months + sav_r * months * (months + 1) / 24))
        sav_expected_total = target_amt
    else:
        req_monthly = input_monthly
        sav_req_monthly = input_monthly
        if monthly_rate == 0:
            expected_total = round(req_monthly * months)
        else:
            expected_total = round(req_monthly * ((1 + monthly_rate)**months - 1) / monthly_rate)
        target_amt = expected_total  # For chart goal line and monte carlo consistency

        if sav_r == 0:
            sav_expected_total = round(sav_req_monthly * months)
        else:
            sav_expected_total = round(sav_req_monthly * months + sav_req_monthly * sav_r * months * (months + 1) / 24)
            
    total_principal = req_monthly * months
    total_interest = expected_total - total_principal
    
    sav_total_principal = sav_req_monthly * months
    sav_total_interest = sav_expected_total - sav_total_principal


    with col_result:
        st.subheader("📊 자금 달성 분석")
        
        c1, c2 = st.columns(2)
        
        # HTML 카드 스타일을 위한 공통 래퍼 함수
        def draw_kpi_card(title, main_val, sub_label, sub_val, is_result1=True):
            icon = "🎯" if is_result1 else "💰"
            grad = "linear-gradient(135deg, #15803d, #22c55e)" if is_result1 else "linear-gradient(135deg, #1e40af, #3b82f6)"
            shadow = "0 4px 16px rgba(34,197,94,0.3)" if is_result1 else "0 4px 16px rgba(59,130,246,0.3)"
            return f"""
            <div style='background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 22px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%; margin-bottom: 12px;'>
                <div style='color: #64748b; font-size: 0.95rem; font-weight: 600; margin-bottom: 8px;'><span style='margin-right:4px;'>{icon}</span> {title}</div>
                <div style='color: #1e293b; font-size: 1.8rem; font-weight: 800; margin-bottom: 16px; letter-spacing: -0.5px;'>{main_val} <span style='font-size: 1.1rem; color: #475569; font-weight:600;'>원</span></div>
                <div style='background: {grad}; padding: 12px 14px; border-radius: 10px; font-size: 0.92rem; display: flex; justify-content: space-between; align-items: center; box-shadow: {shadow};'>
                    <span style='font-weight: 600; color: rgba(255,255,255,0.85);'>{sub_label}</span>
                    <span style='font-weight: 800; color: #ffffff; font-size: 1rem;'>{sub_val}원</span>
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
                curr_s = sav_req_monthly * m + sav_req_monthly * sav_r * m * (m + 1) / 24
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
        st.plotly_chart(fig_growth)
        
    st.divider()
    
    # ===== 적금 vs 펀드 vs 변액 비교 분석 =====
    st.subheader("🎲 적금 vs 펀드 vs 변액 비교 분석")
    
    col_t1, col_t2 = st.columns([1, 2.5])
    with col_t1:
        st.write("")
        is_mc_tf = st.toggle("3종 상품 비교 시뮬레이션 실행", value=False, key="tf_mc_toggle")
    
    if is_mc_tf:
        with col_t2:
            cc1, cc2, cc3 = st.columns(3)
            savings_rate = cc1.number_input("적금 금리(%)", min_value=0.0, value=2.5, step=0.1, key="tf_sav_rate")
            fund_rate = cc2.number_input("펀드 기대수익률(%)", min_value=0.0, value=7.0, step=0.1, key="tf_fund_rate")
            etf_rate = cc3.number_input("변액 기대수익률(%)", min_value=0.0, value=10.0, step=0.1, key="tf_etf_rate")
            
        # === 상품별 파라미터 설정 ===
        # 적금: 이자소득세 15.4%
        savings_tax = 0.154
        
        # 펀드: 변동성 있음, 배당소득세 15.4%
        fund_vol = 0.15  # 펀드 변동성
        fund_tax = 0.154
        
        # 변액: 변동성 있음, 비과세 (10년 이상 유지 시)
        etf_vol = 0.12  # ETF 추종으로 펀드 대비 낮은 변동성
        etf_tax = 0.0  # 비과세 혜택
        
        # === 추가납입 설정 ===
        if st.toggle("💸 추가납입", value=st.session_state.tf_add_toggle, key="tf_add_toggle"):
            c_add1, c_add2 = st.columns([1, 2])
            with c_add1:
                tf_add_prem = comma_int_input("추가납입액(원)", st.session_state.tf_add_prem, "tf_add_prem")
        else:
            tf_add_prem = 0
            
        mc_years = list(range(period + 1))
        long_periods = [3, 5, 10, 15]
        annual_save = (req_monthly + tf_add_prem) * 12

        if annual_save <= 0:
            st.warning("⚠️ 월 납입액이 0원이므로 시뮬레이션을 건너뜁니다. 목표 금액 또는 기간을 확인하세요.")
            is_mc_tf = False

        # 캐싱된 함수 호출 — 동일 파라미터면 재계산 없이 즉시 반환
        with st.spinner("🔄 시뮬레이션 분석 중..."):
            (savings_long, fund_long, etf_long, savings_balances,
             fund_p10, fund_p50, fund_p90,
             etf_p10, etf_p50, etf_p90) = _run_tf_mc(
                period, annual_save, req_monthly, tf_add_prem,
                savings_rate, fund_rate, etf_rate
            )

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
            name='🚀 변액', x=[f'{p}년' for p in long_periods], y=etf_long,
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
        st.plotly_chart(fig_long)
        
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
                cards_html += f'<div style="flex:1;min-width:200px;background:rgba(255,255,255,0.07);border-radius:14px;padding:18px 14px;border:1px solid rgba(255,255,255,0.12);text-align:center;"><div style="color:#93c5fd;font-size:0.85rem;font-weight:600;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid rgba(255,255,255,0.15);">{lp}년 유지</div><div style="display:flex;flex-direction:column;gap:8px;"><div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(203,213,225,0.1);border-radius:8px;"><span style="color:#94a3b8;font-size:0.75rem;">🏦 적금</span><span style="color:#cbd5e1;font-size:0.9rem;font-weight:700;">{f_w(s_val)}원</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(251,191,36,0.08);border-radius:8px;"><span style="color:#fbbf24;font-size:0.75rem;">📊 펀드</span><span style="color:#fbbf24;font-size:0.9rem;font-weight:700;">{f_w(f_val)}원</span></div><div style="display:flex;justify-content:space-between;align-items:center;padding:6px 10px;background:rgba(37,99,235,0.12);border-radius:8px;"><span style="color:#60a5fa;font-size:0.75rem;">🚀 변액</span><span style="color:#34d399;font-size:0.95rem;font-weight:800;">{f_w(e_val)}원</span></div></div><div style="margin-top:10px;padding-top:8px;border-top:1px solid rgba(255,255,255,0.1);font-size:0.72rem;"><span style="color:#94a3b8;">변액-적금</span> <span style="color:{e_gap_color};font-weight:700;">{e_gap_sign}{f_w(e_gap)}원</span> <span style="color:#475569;margin:0 4px;">|</span> <span style="color:#94a3b8;">변액-펀드</span> <span style="color:#34d399;font-weight:700;">{ef_gap_sign}{f_w(ef_gap)}원</span></div></div>'
            
            st.markdown(f'<div style="background:linear-gradient(135deg,#0f172a 0%,#1e3a8a 50%,#1d4ed8 100%);padding:24px;border-radius:16px;color:white;box-shadow:0 10px 25px -5px rgba(30,58,138,0.4);margin-bottom:40px;"><div style="text-align:center;margin-bottom:18px;"><div style="font-size:1.05rem;font-weight:700;letter-spacing:0.5px;">⚡ 기간별 적금 vs 펀드 vs 변액 차이</div><div style="font-size:0.75rem;color:#94a3b8;margin-top:4px;">동일 금액 적립 시, 상품별 누적 자산 비교</div></div><div style="display:flex;gap:12px;flex-wrap:wrap;justify-content:center;">{cards_html}</div><div style="text-align:center;margin-top:16px;padding-top:12px;border-top:1px solid rgba(255,255,255,0.1);"><div style="font-size:0.78rem;color:#bfdbfe;">💡 기간이 길어질수록 비과세 복리의 격차는 <b style="color:#fbbf24;">기하급수적</b>으로 벌어집니다</div></div></div>', unsafe_allow_html=True)
            

        
        with st.expander("🏢 금융기관별 상품 비교", expanded=False):
            st.markdown('<div style="text-align:center;"><h4 style="margin-bottom:16px;">금융기관별 목적자금 마련 상품 비교</h4><table style="margin:0 auto;border-collapse:collapse;width:95%;max-width:900px;font-size:0.88rem;"><thead><tr style="background:#1e3a8a;color:white;"><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">항목</th><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">🏦 은행 (적금)</th><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">📊 증권사 (펀드)</th><th style="padding:10px 12px;border:1px solid #334155;text-align:center;">🚀 보험사 (변액)</th></tr></thead><tbody><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">대표 상품</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">정기적금, 자유적금</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">주식형/혼합형 펀드</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">변액저축보험</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">수익률</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">확정 3~4%</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">변동 (시장 수익률)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">변동 (시장 수익률)</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">과세</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">이자소득세 15.4%</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">배당소득세 15.4%</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">비과세 (10년 유지 시)</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">변동성 관리</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">없음 (확정)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">직접 관리 필요</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">펀드 무제한 무료 변경</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">사망 보장</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">없음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">없음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">사망보험금 지급</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">최저 보증</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">원금 보장</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">없음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">최저 사망보험금 보증</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">ETF 투자</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">불가</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">가능 (별도 계좌)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">보험 내 ETF 직접 편입</td></tr><tr style="background:#f8fafc;"><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">장기 복리</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">낮은 확정금리</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">세금이 복리를 깎음</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">비과세 복리 극대화</td></tr><tr><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;font-weight:600;">중도 인출</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">해지 시 이자 손실</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">자유 (수수료 有)</td><td style="padding:8px 12px;border:1px solid #e2e8f0;text-align:center;">부분 인출 가능</td></tr></tbody></table><div style="margin-top:14px;padding:10px 16px;background:#eff6ff;border-radius:8px;border-left:4px solid #2563eb;text-align:left;font-size:0.85rem;">💡 <b>핵심 포인트</b>: 동일한 수익률이라도 세금이 매년 깎이는 펀드 대비, 비과세 복리로 굴러가는 변액은 시간이 길어질수록 <b>기하급수적으로</b> 차이가 벌어집니다.</div></div>', unsafe_allow_html=True)
    else:
        st.info("💡 적금·펀드·변액의 수익률 차이를 비교 분석으로 직접 확인해보세요. 비과세의 놀라운 복리 효과를 체감하실 수 있습니다.")

    # === 스마트 자산 증식 전략 비교 리포트 ===
    with st.expander("📊 스마트 자산 증식 전략 비교 리포트", expanded=False):
        # 각 상품별 수익 계산 (월 복리 기준으로 통일)
        _total_months = period * 12

        # 적금: 단리 + 이자소득세 15.4%
        _principal = req_monthly * _total_months
        _pre_tax_interest = req_monthly * (top_sav_rate / 100) * _total_months * (_total_months + 1) / 24
        savings_result = _principal + _pre_tax_interest * (1 - 0.154)

        # 펀드: 월 복리 (세후)
        _net_f_monthly = actual_rate * (1 - 0.154) / 100 / 12
        if _net_f_monthly > 0:
            fund_result_simple = req_monthly * ((1 + _net_f_monthly)**_total_months - 1) / _net_f_monthly
        else:
            fund_result_simple = req_monthly * _total_months

        # ETF: 월 복리 (비과세)
        _net_e_monthly = actual_rate / 100 / 12
        if _net_e_monthly > 0:
            etf_result_simple = req_monthly * ((1 + _net_e_monthly)**_total_months - 1) / _net_e_monthly
        else:
            etf_result_simple = req_monthly * _total_months

        total_input = req_monthly * 12 * period
        
        html_block(f"""
        <div class='expert-card'>
            <div class='expert-title'>📑 {display_name}님을 위한 스마트 자산 증식 전략 비교</div>
            <div class='step-box'>
                <div class='step-title'>1. 📌 목표 분석</div>
                <div class='step-content'>
                    {period}년 후({current_age + period}세) 목표 금액 <span class='highlight'>{f_w(target_amt)}원</span> | 매월 필요 저축액 <span class='highlight'>{f_w(req_monthly)}원</span>
                </div>
            </div>
            <div class='step-box' style="border-left-color: #94a3b8;">
                <div class='step-title'>2. 🏦 적금으로 준비하면?</div>
                <div class='step-content'>
                    연 {top_sav_rate}% 확정금리 (이자소득세 15.4% 차감) → 세후 연 {top_sav_rate*(1-0.154):.2f}%<br>
                    {period}년 후 총 자산: <span class='highlight'>{f_w(savings_result)}원</span> (총 원금 {f_w(total_input)}원, 이자 수익 {f_w(savings_result - total_input)}원)<br>
                    <span style="color: {'#ef4444' if savings_result < target_amt else '#16a34a'}; font-weight: 600;">{'⚠️ 목표 금액 대비 ' + f_w(target_amt - savings_result) + '원 부족 → 실질 인플레이션 반영 시 원금 가치마저 감소' if savings_result < target_amt else '✅ 목표 금액 대비 ' + f_w(savings_result - target_amt) + '원 초과 달성'}</span>
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
                <div class='step-title'>4. 🚀 변액로 준비하면?</div>
                <div class='step-content'>
                    연 {rate}% 기대수익률 (10년 이상 유지 시 <b>비과세</b>) → 실질 연 {rate:.2f}%<br>
                    {period}년 후 예상 자산: <span class='highlight' style="font-size: 1.1em; color: #2563eb;">{f_w(etf_result_simple)}원</span> (이자 수익 {f_w(etf_result_simple - total_input)}원)<br>
                    <span style="color: #2563eb; font-weight: 700;">✅ 비과세 복리 + 낮은 변동성 + 사망보장까지! 펀드 대비 +{f_w(etf_result_simple - fund_result_simple)}원 추가 확보</span>
                </div>
            </div>
        </div>
        """)



