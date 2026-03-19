import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core import f_w, f_kr, show_kr_label, comma_int_input, TaxEngine, html_block, render_title_with_reset, RealEstateState, card_header
from station_data import COMPLEX_DB, REGION_DB
from core import get_capital_gains_tax_rate

def render_real_estate():
    # Fragment 내 세션 상태 방어 초기화 (fragment는 독립 실행되므로 core.init 이전에 호출될 수 있음)
    _defaults = {
        'presentation_mode': False,
        'acq_p': 500_000_000, 'acq_area': 84.0, 'acq_h': '1주택', 'acq_type': '주택(매매)',
        'hold_p': 500_000_000, 'hold_h': '1주택(단독)', 'hold_age': 60, 'hold_y': 10,
        'yang_s': 600_000_000, 'yang_b': 400_000_000, 'yang_1h': True, 'yang_h_y': 1, 'yang_r_y': 1,
    }
    for k, v in _defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

    render_title_with_reset("🏠 부동산 통합 시뮬레이터", ["acq_", "hold_", "yang_", "result_acq", "result_hold", "result_yang", "result_prop", "result_jongbu", "result_local"], "reset_real_estate", default_states=[RealEstateState()])
    st.markdown("취득, 보유, 양도 전 단계에 걸친 세금을 정밀하게 분석하고 절세 전략을 수립합니다.")

    # A. Smart Search (Global - Above Tabs)
    if not st.session_state.presentation_mode:
        with st.container():
            c_search, c_btn = st.columns([3, 1])
            addr_input = c_search.text_input("📍 스마트 주소 검색 (취득/보유/양도 통합 연동)", placeholder="예: 반포자이 84 (엔터)")
            if c_btn.button("🔍 데이터 로드"):
                if not addr_input or not addr_input.strip():
                    st.error("❌ 주소 또는 단지명을 입력해주세요. (예: 반포자이 84)")
                else:
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
                        # 기존 입력값이 있으면 덮어쓰기 경고
                        existing = [st.session_state.get('acq_p', 0), st.session_state.get('hold_p', 0), st.session_state.get('yang_s', 0)]
                        if any(v > 0 for v in existing):
                            st.toast("⚠️ 기존 입력값이 검색 결과로 대체됩니다.", icon="⚠️")
                        # Sync ALL tabs
                        st.session_state.acq_p = target_p
                        st.session_state.acq_area = target_area
                        st.session_state.hold_p = int(target_p * 0.7) # 공시가격 = 시세의 약 70%
                        st.session_state.yang_s = target_p
                        st.session_state.yang_b = int(target_p * 0.8) # 취득가 = 시세의 80% 가정
                        st.rerun()
                    else:
                        st.warning(f"⚠️ '{addr_input}'에 일치하는 데이터를 찾을 수 없습니다. 단지명 또는 지역명을 확인해주세요.")

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
                card_header("🏠 매물 기본정보")
                with st.container(border=True):
                    prop_type = st.selectbox("부동산 종류",
                        ["주택(매매)", "주택(증여)", "주택(상속)", "농지(자경)", "농지(비자경)", "농지(증여)", "농지(상속)", "법인(취득)", "기타 토지/상가"],
                        key="acq_type")
                    area = st.number_input("전용면적(㎡)", value=84.0 if 'acq_area' not in st.session_state else st.session_state.acq_area, key="acq_area", help="건축물대장이나 등기부등본에 기재된 전용면적(평방미터)을 입력하세요. 국민주택규모인 85㎡를 초과하면 농어촌특별세가 추가로 부과되어 세금이 늘어납니다.")
                    price = comma_int_input("취득 가액 (실거래가/원)", st.session_state.acq_p, "acq_p", help="부동산을 실제 매수한 (또는 매수할) 실거래 가격을 입력하세요.")
                card_header("💰 세율 조건")
                with st.container(border=True):
                    _lock_hcount = "상속" in prop_type or "법인" in prop_type
                    h_count = st.selectbox("주택수 (취득시점 기준)", ["1주택", "2주택", "3주택", "4주택 이상"], key="acq_h",
                        help="이번에 취득하는 주택을 포함하여 세대원이 보유한 총 주택 수입니다.",
                        disabled=_lock_hcount)
                    _lock_adj = "상속" in prop_type or "법인" in prop_type or "농지" in prop_type
                    is_adjustment = st.checkbox("조정대상지역 여부", value=False, key="acq_adj",
                        help="2025년 기준 서울 전역이 조정대상지역입니다. 수도권·지방은 대부분 해제된 상태입니다.",
                        disabled=_lock_adj)
                    is_first_home = st.checkbox("생애최초 주택 취득 (감면 적용)", value=False, key="acq_first",
                        help="생애최초 주택 취득 시 취득세 200만원 한도 감면 (매매 취득에만 해당)",
                        disabled=("증여" in prop_type or "상속" in prop_type or "법인" in prop_type))
                    if "법인" in prop_type:
                        st.info("💡 법인은 취득유형에 관계없이 12% 중과세율이 적용됩니다.")
                    elif "상속" in prop_type:
                        st.info("💡 상속 취득은 단일세율(주택 2.8%, 농지 2.3%)이 적용됩니다.")
                    elif "증여" in prop_type:
                        st.info("💡 증여 취득: 주택 3.5% (조정지역 다주택 시 8~12% 중과)")
        else:
            prop_type = st.session_state.get('acq_type', "주택(매매)")
            area = st.session_state.get('acq_area', 84.0)
            price = st.session_state.get('acq_p', 900_000_000)
            h_count = st.session_state.get('acq_h', "1주택")
            is_adjustment = st.session_state.get('acq_adj', False)
            is_first_home = st.session_state.get('acq_first', False)
            _lock_hcount = "상속" in prop_type or "법인" in prop_type
            _lock_adj = "상속" in prop_type or "법인" in prop_type or "농지" in prop_type

        # Logic using TaxEngine
        _method_str = f"{prop_type} {h_count}" if not ("상속" in prop_type or "법인" in prop_type) else prop_type
        rate, rate_desc = TaxEngine.get_acquisition_tax(price, area, _method_str, is_adjustment)

        tax = price * rate

        # Additional Taxes
        # 지방교육세: 표준세율(1~3%) 취득세의 10%, 중과세율 시 표준세율 부분만 10% 적용
        if rate > 0.03 and "주택" in prop_type:
            # 주택 중과세율: 해당 가격대의 실제 표준세율 기준 교육세 적용
            if price <= 600_000_000:
                _std_rate = 0.01
            elif price <= 900_000_000:
                _std_rate = (price * 2 / 300_000_000 - 3) / 100
            else:
                _std_rate = 0.03
            _std_tax = price * _std_rate
            edu_tax = _std_tax * 0.10
        else:
            edu_tax = tax * 0.10
        # 농어촌특별세: 85㎡ 초과 주택에 취득세의 10% (비과세·감면 대상 외)
        rural_tax = 0 if area <= 85 else tax * 0.10
        # 증여·상속·농지·기타는 농특세 미적용 (간이 처리)
        if "농지" in prop_type or "상속" in prop_type or "증여" in prop_type or "법인" in prop_type or "기타" in prop_type:
            rural_tax = 0
        total_tax = tax + edu_tax + rural_tax

        # 생애최초 감면 적용 (매매 주택에만 적용)
        first_home_reduction = 0
        if is_first_home and "주택(매매)" in prop_type:
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
            st.plotly_chart(fig)
            if area > 85:
                st.caption("📌 농어촌특별세: 전용면적 85㎡ 초과 주택에 취득세의 약 10% 추가 부과 (개략값). 정확한 세액은 관할 지자체에 확인하세요.")

            with st.expander("🔍 취득세 상세 분석 보고서", expanded=True):
                _acq_type_note = {
                    "주택(매매)": "유상거래(매매) 취득 — 실거래가 기준 과세",
                    "주택(증여)": "증여 취득 — 시가인정액(감정가 등) 기준 과세. 조정지역 다주택 시 중과",
                    "주택(상속)": "상속 취득 — 취득 원인 불문 2.8% 단일세율 적용",
                    "농지(자경)": "농지 자경 취득 — 1.5% 감면세율 (실경작 증명 필요)",
                    "농지(비자경)": "농지 비자경 취득 — 3% 일반세율",
                    "농지(증여)": "농지 증여 취득 — 2.8% 세율",
                    "농지(상속)": "농지 상속 취득 — 2.3% 단일세율",
                    "법인(취득)": "법인 취득 — 취득 유형·주택수에 관계없이 12% 중과",
                    "기타 토지/상가": "비주거용 부동산 — 4% 기본세율",
                }.get(prop_type, "")
                html_block(f"""
                <div class='expert-card'>
                    <div class='expert-title'>📑 취득세 단계별 산출 리포트</div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 1. 취득 유형 및 과세표준 확정</div>
                        <div class='step-content'>
                            <b>{prop_type}</b> — {_acq_type_note}<br>
                            과세표준: <span class='highlight'>{f_w(price)}원</span>
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 2. 적용 세율 판정 ({rate_desc})</div>
                        <div class='step-content'>
                            {'' if _lock_hcount else h_count + ', '}{price/1e8:.1f}억, {prop_type} 조건 → 세율 <span class='highlight'>{rate*100:.2f}%</span>
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 3. 세액 산출 및 부가세 계산</div>
                        <div class='step-content'>
                            • 취득세(본세): {f_w(tax)}원 ({f_w(price)} × {rate*100:.2f}%)<br>
                            • 지방교육세: {f_w(edu_tax)}원 (표준세율 기준 10%)<br>
                            • 농어촌특별세: {f_w(rural_tax)}원 {'(85㎡ 초과 주택 취득세의 10%)' if rural_tax > 0 else '(해당없음)'}
                        </div>
                    </div>
                    {f"<div class='step-box' style='background:#fef9c3; border:1px solid #fbbf24;'><div class='step-title'>생애최초 감면</div><div class='step-content'>감면액: -{f_w(first_home_reduction)}원 (최대 200만원 한도)</div></div>" if first_home_reduction > 0 else ""}
                    <div class='step-box' style='background: #f8fafc; border: 1px solid #3b82f6;'>
                        <div class='step-title' style='color: #1e3a8a;'>FINAL. 합계 납부액</div>
                        <div class='step-content' style='font-weight: 700; font-size: 1.1rem;'>
                             총 예상 세액: {f_w(total_tax)}원
                        </div>
                    </div>
                </div>
                """)

        # AI Doctor Call

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
                card_header("🏠 보유 조건")
                with st.container(border=True):
                    off_p = comma_int_input("주택 공시가격 (총합/원)", st.session_state.hold_p, "hold_p", help="보유하고 있는 모든 주택의 국토교통부 고시 공시가격 합계를 입력하세요. (통상 실거래가의 60~70% 수준)")
                    h_type = st.radio("보유 형태", ["1주택(단독)", "1주택(공동명의)", "다주택"], horizontal=True, key="hold_h")
                    if h_type == "1주택(공동명의)":
                        st.caption("💡 공동명의: 1세대 1주택 특례 적용 시 12억 공제 + 세액공제. (특례 미적용 시 각 9억, 합산 18억 가능하나 세액공제 없음)")
                card_header("📋 세액공제 요건")
                with st.container(border=True):
                    c_a, c_b = st.columns(2)
                    age = c_a.slider("연령", 20, 90, 60, key="hold_age")
                    hold_y = c_b.slider("보유기간(년)", 0, 30, 10, key="hold_y")
        else:
            off_p = st.session_state.get('hold_p', 1_500_000_000)
            h_type = st.session_state.get('hold_h', "1주택(단독)")
            age = st.session_state.get('hold_age', 60)
            hold_y = st.session_state.get('hold_y', 10)

        # Logic
        if "다주택" in h_type:
            exemption = 900_000_000
        else:
            exemption = 1_200_000_000  # 1주택(단독) 및 1주택(공동명의) 모두 12억 공제

        j_base = max(0, (off_p - exemption) * 0.6)
        j_tax_raw, j_rate_desc, jongbu_rural_tax_raw = TaxEngine.get_jongbu_tax(j_base, is_multi_home=("다주택" in h_type))
        prop_tax_base, prop_edu_tax, prop_city_tax, prop_tax = TaxEngine.get_property_tax(off_p, is_single_home=("1주택" in h_type))

        deduction_rate = 0
        if "1주택" in h_type:
            age_ded = (0.4 if age>=70 else 0.3 if age>=65 else 0.2 if age>=60 else 0)
            period_ded = (0.5 if hold_y>=15 else 0.4 if hold_y>=10 else 0.2 if hold_y>=5 else 0)
            deduction_rate = min(0.8, age_ded + period_ded)

        j_tax_final = j_tax_raw * (1 - deduction_rate)
        jongbu_rural_tax_final = jongbu_rural_tax_raw * (1 - deduction_rate)
        total_hold_tax = prop_tax + j_tax_final + jongbu_rural_tax_final

        with col_result:
            st.subheader("📊 예상 보유세 (재산세 + 종부세)")
            st.caption("📌 재산세는 공정시장가액비율 60% 기준. 종부세 농어촌특별세(20%) 포함.")
            _hold_cards = [
                (f"재산세 (본세+부가세)", f"{f_w(prop_tax)} 원", f"본세 {f_w(prop_tax_base)}", "#3b82f6"),
                (f"종부세 (세율 {j_rate_desc})", f"{f_w(j_tax_final)} 원", f"-{int(deduction_rate*100)}% 공제" if deduction_rate > 0 else "", "#1e3a8a"),
                ("종부 농어촌특별세 (종부세의 20%)", f"{f_w(jongbu_rural_tax_final)} 원", "", "#6366f1"),
                ("총 보유세 합계", f"{f_w(total_hold_tax)} 원", "", "#ef4444"),
            ]
            _hold_html = "<div style='display:flex;flex-wrap:wrap;gap:10px;'>"
            for _lbl, _val, _delta, _color in _hold_cards:
                _delta_html = f"<div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>{_delta}</div>" if _delta else ""
                _hold_html += f"<div style='flex:1;min-width:140px;background:white;border-radius:10px;padding:12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'><div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>{_lbl}</div><div style='font-size:1.15rem;font-weight:800;color:{_color};word-break:break-all;'>{_val}</div>{_delta_html}</div>"
            _hold_html += "</div>"
            st.markdown(_hold_html, unsafe_allow_html=True)

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
                st.plotly_chart(fig)
            else:
                st.info("💡 1세대 1주택자로서 고령/장기보유 요건 충족 시 최대 80% 세액공제를 받을 수 있습니다.")

            with st.expander("🔍 보유세 상세 분석 보고서", expanded=True):
                html_block(f"""
                <div class='expert-card'>
                    <div class='expert-title'>📑 종합부동산세 단계별 산출 리포트</div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 1. 공시가격 합계 및 기본공제 ({h_type})</div>
                        <div class='step-content'>
                            공시가 {f_w(off_p)}원 - 기본공제 {f_w(exemption)}원 = <span class='highlight'>{f_w(max(0, off_p - exemption))}원</span>
                            {'<br>※ 공동명의: 부부 합산 12억 공제 (인당 6억 × 2)' if h_type == '1주택(공동명의)' else ''}
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
                            • 세액공제액: -{f_w(j_tax_raw * deduction_rate)}원 (고령/장기보유 {int(deduction_rate*100)}% 적용)<br>
                            • 종부 농어촌특별세: {f_w(jongbu_rural_tax_final)}원 (납부 종부세의 20%)
                        </div>
                    </div>
                    <div class='step-box' style='background: #f8fafc; border: 1px solid #3b82f6;'>
                        <div class='step-title' style='color: #1e3a8a;'>FINAL. 최종 보유세액 합계</div>
                        <div class='step-content' style='font-weight: 700; font-size: 1.1rem;'>
                             재산세 {f_w(prop_tax)}원 + 종부세 {f_w(j_tax_final)}원 + 농특세 {f_w(jongbu_rural_tax_final)}원 = <span class='highlight'>합계 {f_w(total_hold_tax)}원</span>
                        </div>
                    </div>
                </div>
                """)

        # 결과 저장
        st.session_state['result_hold_tax'] = total_hold_tax
        st.session_state['result_prop_tax'] = prop_tax
        st.session_state['result_jongbu_tax'] = j_tax_final

        # AI Doctor Call

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
                if st.button("🔗 취득세 입력값 동기화", help="취득세 탭에 입력한 가격·면적 정보를 양도세 취득가로 가져옵니다."):
                    _acq = st.session_state.get('acq_p', 0)
                    if _acq > 0:
                        st.session_state.yang_b = _acq
                        st.toast(f"✅ 취득가 {f_w(_acq)}원 동기화 완료", icon="🔗")
                        st.rerun()
                    else:
                        st.toast("⚠️ 취득세 탭에 가격을 먼저 입력해주세요.", icon="⚠️")
                card_header("💰 거래 금액")
                with st.container(border=True):
                    asset_type = st.selectbox("자산 유형",
                        ["주택", "분양권(2021년 이후 취득)", "비사업용 토지", "일반 건물/상가", "토지(일반)"],
                        key="yang_asset",
                        help="자산 유형에 따라 단기보유 중과세율, 비사업용 토지 중과 등이 달리 적용됩니다.")
                    sell_p = comma_int_input("양도 가액 (실제 매도가/원)", st.session_state.yang_s, "yang_s", help="부동산을 매도하는 (또는 매도예정인) 실제 거래가격을 입력하세요.")

                    # 이월과세 체크박스
                    is_rollover = st.checkbox("이월과세 적용 (배우자·직계존비속 증여 후 5년 이내 양도)", value=False, key="yang_rollover",
                        help="증여받은 자산을 5년 이내 양도 시, 증여자의 원래 취득가액으로 양도차익을 계산합니다.")
                    if is_rollover:
                        st.warning("⚠️ 이월과세: '취득 가액' 란에 증여자(배우자 등)의 최초 취득가액을 입력하세요.")

                    buy_p = comma_int_input("취득 가액 (과거 매입가/원)", st.session_state.yang_b, "yang_b",
                        help="과거 매수 시 취득가격. 이월과세 적용 시 증여자의 최초 취득가액을 입력하세요.")
                    expenses = comma_int_input("필요경비 (중개수수료/인테리어 등/원)", 0, "yang_exp",
                        help="인정 필요경비: 취득세, 법무사 비용, 중개수수료, 자본적 지출(샷시·보일러 등 내구성 개량비). 단순 수리비·도배·청소는 불인정.")
                card_header("⚙️ 과세 옵션")
                with st.container(border=True):
                    _is_housing = asset_type == "주택"
                    c1, c2 = st.columns(2)
                    is_1h = c1.checkbox("1세대 1주택 비과세", value=True if 'yang_1h' not in st.session_state else st.session_state.yang_1h, key="yang_1h", disabled=not _is_housing)
                    multi_house_surcharge = c2.selectbox("다주택 중과", ["없음", "2주택 (+20%p)", "3주택 이상 (+30%p)", "4주택 이상 (+30%p)"], key="yang_multi", disabled=(is_1h and _is_housing))

                    st.caption("장기보유특별공제 입력")
                    c3, c4 = st.columns(2)
                    h_years = c3.slider("보유기간 (년)", 0, 30, 10, key="yang_h_y")
                    r_years = c4.slider("거주기간 (년)", 0, 30, 5, key="yang_r_y", disabled=not (is_1h and _is_housing))

                # 거주요건 검증
                if _is_housing and is_1h and r_years < 2:
                    st.warning("⚠️ 거주기간 2년 미충족 — 1세대 1주택 비과세가 적용되지 않으며, 아래 결과는 **일반과세** 기준으로 계산됩니다.")
        else:
            asset_type = st.session_state.get('yang_asset', "주택")
            sell_p = st.session_state.get('yang_s', 1_500_000_000)
            buy_p = st.session_state.get('yang_b', 900_000_000)
            expenses = st.session_state.get('yang_exp', 0)
            is_1h = st.session_state.get('yang_1h', True)
            multi_house_surcharge = st.session_state.get('yang_multi', '없음')
            h_years = st.session_state.get('yang_h_y', 10)
            r_years = st.session_state.get('yang_r_y', 5)
            is_rollover = st.session_state.get('yang_rollover', False)
            _is_housing = asset_type == "주택"

        # --- 계산 로직 ---
        gain = sell_p - buy_p - expenses
        taxable_gain = gain

        # 1세대 1주택 비과세 (주택에만 적용, 거주 2년 이상일 때)
        _1h_applicable = _is_housing and is_1h and r_years >= 2
        if _1h_applicable and sell_p > 1_200_000_000 and sell_p > 0:
            taxable_gain = gain * (sell_p - 1_200_000_000) / sell_p
        elif _1h_applicable and sell_p <= 1_200_000_000:
            taxable_gain = 0

        # 단기보유 중과세율 판단
        _short_rate = None
        _short_desc = ""
        if asset_type == "분양권(2021년 이후 취득)":
            if h_years < 1:
                _short_rate, _short_desc = 0.70, "단기보유 중과 70% (분양권 1년 미만)"
            elif h_years < 2:
                _short_rate, _short_desc = 0.60, "단기보유 중과 60% (분양권 1~2년 미만)"
            # 2년 이상: _short_rate = None → 일반 누진세율(6~45%) 적용
        elif asset_type in ["주택", "비사업용 토지"]:
            if h_years < 1:
                _short_rate, _short_desc = 0.70, "단기보유 중과 70% (1년 미만 보유)"
            elif h_years < 2:
                _short_rate, _short_desc = 0.60, "단기보유 중과 60% (1~2년 미만 보유)"

        # 장기보유특별공제 (단기 중과 시 미적용)
        if _short_rate is None:
            lt_rate, lt_desc = TaxEngine.get_long_term_deduction(h_years, r_years, _1h_applicable)
        else:
            lt_rate, lt_desc = 0, "단기보유 — 장특공제 미적용"
        deduction_amt = taxable_gain * lt_rate
        yang_base = max(0, taxable_gain - deduction_amt - 2_500_000)

        # 세율 적용
        surcharge_rate = 0
        _nonbusiness_land = False
        if _short_rate is not None:
            final_tax = max(0, yang_base * _short_rate)
            r_desc = _short_desc
        else:
            # 비사업용 토지 중과 (+10%p)
            if asset_type == "비사업용 토지":
                _nonbusiness_land = True
            # 다주택 중과
            if not (is_1h and _is_housing) and multi_house_surcharge != '없음':
                if '2주택' in multi_house_surcharge:
                    surcharge_rate = 0.20
                elif '3주택' in multi_house_surcharge or '4주택' in multi_house_surcharge:
                    surcharge_rate = 0.30
            r, p, r_desc = get_capital_gains_tax_rate(yang_base)
            _extra = surcharge_rate + (0.10 if _nonbusiness_land else 0)
            if _extra > 0:
                final_tax = max(0, yang_base * (r + _extra) - p)
            else:
                final_tax = max(0, yang_base * r - p)

        # 지방소득세 (10%)
        local_income_tax = final_tax * 0.1
        total_yang_tax = final_tax + local_income_tax

        with col_result:
            st.subheader("📊 양도소득 분석")
            _yang_cards = [
                ("양도소득세", f"{f_w(final_tax)} 원", "#1e3a8a"),
                ("지방소득세 (10%)", f"{f_w(local_income_tax)} 원", "#3b82f6"),
                ("세후 실수령액", f"{f_w(max(0, sell_p - total_yang_tax))} 원", "#16a34a"),
            ]
            _yang_html = "<div style='display:flex;flex-wrap:wrap;gap:10px;'>"
            for _lbl, _val, _color in _yang_cards:
                _yang_html += f"<div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'><div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>{_lbl}</div><div style='font-size:1.15rem;font-weight:800;color:{_color};word-break:break-all;'>{_val}</div></div>"
            _yang_html += "</div>"
            st.markdown(_yang_html, unsafe_allow_html=True)

            if _short_rate is not None:
                st.info(f"🚨 {_short_desc} — 보유기간 {h_years}년 미만으로 중과세율 적용!")
            if surcharge_rate > 0:
                st.warning(f"⚠️ 다주택 중과세율 +{int(surcharge_rate*100)}%p 적용됨")
            if _nonbusiness_land and _short_rate is None:
                st.warning("⚠️ 비사업용 토지 중과 +10%p 적용됨")
            if is_rollover:
                st.info("ℹ️ 이월과세 적용: 증여자의 원래 취득가 기준으로 양도차익이 계산되었습니다.")
            if _is_housing and is_1h and r_years < 2:
                st.caption("ℹ️ 거주기간 2년 미충족으로 비과세 미적용 → 일반과세 적용됨")

            # 자금 흐름 차트
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
            st.plotly_chart(fig)

            with st.expander("🔍 양도세 상세 분석 보고서", expanded=True):
                _exemption_note = ""
                if _1h_applicable and sell_p <= 1_200_000_000:
                    _exemption_note = "<br>✅ 1세대 1주택 비과세 (12억 이하 전액 면세)"
                elif _1h_applicable and sell_p > 1_200_000_000:
                    _exemption_note = f"<br>✅ 1세대 1주택 부분 비과세 (12억 초과분 {f_w(taxable_gain)}원에 대해 과세)"
                elif _is_housing and is_1h and r_years < 2:
                    _exemption_note = "<br>⚠️ 거주기간 2년 미충족 — 비과세 요건 불충족"

                html_block(f"""
                <div class='expert-card'>
                    <div class='expert-title'>📑 양도소득세 단계별 산출 리포트</div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 1. 양도차익 계산</div>
                        <div class='step-content'>
                            자산유형: <b>{asset_type}</b> | 보유기간: {h_years}년{'(이월과세 적용)' if is_rollover else ''}<br>
                            양도가 {f_w(sell_p)} - 취득가 {f_w(buy_p)} - 필요경비 {f_w(expenses)} = <span class='highlight'>{f_w(gain)}원</span>
                            {_exemption_note}
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 2. 장기보유특별공제 및 기본공제</div>
                        <div class='step-content'>
                            • 과세대상 양도차익: {f_w(taxable_gain)}원<br>
                            • 장특공제: -{f_w(deduction_amt)}원 ({lt_desc})<br>
                            • 양도소득기본공제: -2,500,000원
                        </div>
                    </div>
                    <div class='step-box'>
                        <div class='step-title'>STEP 3. 과세표준 및 세율 적용</div>
                        <div class='step-content'>
                            • 양도과표: {f_w(yang_base)}원<br>
                            • 적용세율: <b>{r_desc}</b>
                            {f"<br>• 다주택 중과: +{int(surcharge_rate*100)}%p" if surcharge_rate > 0 else ""}
                            {f"<br>• 비사업용 토지 중과: +10%p" if _nonbusiness_land and _short_rate is None else ""}
                        </div>
                    </div>
                    <div class='step-box' style='background: #f8fafc; border: 1px solid #ef4444;'>
                        <div class='step-title' style='color: #991b1b;'>FINAL. 예상 양도소득세</div>
                        <div class='step-content' style='font-weight: 700; font-size: 1.1rem;'>
                             양도소득세: {f_w(final_tax)}원<br>
                             지방소득세: {f_w(local_income_tax)}원<br>
                             <span class='highlight'>총 납부액: {f_w(total_yang_tax)}원</span>
                        </div>
                    </div>
                </div>
                """)

        # 결과 저장
        st.session_state['result_yang_tax'] = total_yang_tax
        st.session_state['result_yang_gain'] = gain
        st.session_state['result_local_tax'] = local_income_tax

        # AI Doctor Call

