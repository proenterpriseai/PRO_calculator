import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from core import f_w, f_kr, show_kr_label, comma_int_input, TaxEngine, html_block, render_title_with_reset, InheritanceState, card_header
from core import get_tax_rate_5steps

def render_inheritance():
    render_title_with_reset("🎁 상속 및 증여세 시뮬레이터", ["gif_", "inh_", "result_gift", "result_inh"], "reset_inheritance", default_states=[InheritanceState()])
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
                card_header("💰 증여 금액")
                with st.container(border=True):
                    curr = comma_int_input("증여 가액 (원)", st.session_state.gif_c, "gif_c", help="이번에 배우자나 자녀에게 증여하고자 하는 재산(현금, 부동산 등)의 총 평가액입니다.")
                    prev = comma_int_input("10년 내 사전증여액(원)", 0, "gif_p", help="과거 10년 이내에 같은 사람(동일인)에게 이미 증여했던 재산가액의 합계입니다. 누진과세를 위해 합산됩니다.")
                    prev_tax = comma_int_input("기납부 증여세액(원)", 0, "gif_p_tax", help="과거 사전증여 당시 이미 납부했던 증여세액입니다. (이중과세 방지를 위해 기납부세액으로 공제됩니다.)")
                    debt = comma_int_input("부담부 채무액(원)", 0, "gif_d", help="부동산 증여 시 함께 넘겨주는 전세보증금이나 담보대출액 등 수증자(받는사람)가 대신 갚기로 한 채무액입니다.")
                    if st.session_state.get('gif_d', 0) > 0:
                        st.warning(f"⚠️ 부담부 증여: 채무 부분({f_w(st.session_state.get('gif_d',0))}원)은 **증여자에게 양도소득세**가 과세됩니다. 채무액이 증여자의 취득가를 초과하는 경우 양도차익에 대해 별도 양도소득세가 발생하므로 반드시 확인하십시오.")
                card_header("👤 수증자 정보")
                with st.container(border=True):
                    rel = st.selectbox("수증자 관계", ["배우자(6억)", "성년 자녀(5천만)", "미성년 자녀(2천만)", "직계존속(5천만)", "기타친족(1천만)", "형제자매(1천만)"], key="gif_r")
                    prev_used_ded = comma_int_input("10년 내 이미 사용한 공제액(원)", 0, "gif_prev_ded",
                        help="과거 10년 이내 동일인에게 증여 시 이미 공제받은 금액. 공제한도는 10년 누적 관리되므로 잔여 공제액만 적용됩니다.")
                    is_startup = st.checkbox("창업자금 증여 과세특례 적용 (5억 한도, 10% 단일세율)",
                        key="gif_startup",
                        help="60세 이상 부모가 18세 이상 자녀에게 창업 목적으로 증여 시 최대 5억원 한도로 10% 단일세율 적용 (일반 누진세율 대신). 요건: 창업일로부터 3년 이내 증여.")
                    is_overseas = st.checkbox("국외 재산 증여 여부 (신고기한 6개월 적용)", key="gif_overseas",
                        help="국외에 소재하는 재산을 증여하는 경우 신고·납부 기한이 6개월로 연장됩니다.")
                    c1, c2 = st.columns(2)
                    is_gen_skip = c1.checkbox("세대생략 증여 (할증부과)", value=False, key="gif_skip")
                    is_minor_high = c2.checkbox("수증자 미성년 (20억 초과 시 40% 적용)", value=False, key="gif_minor", disabled=not is_gen_skip)
        else:
            curr = st.session_state.get('gif_c', 300_000_000)
            prev = st.session_state.get('gif_p', 0)
            prev_tax = st.session_state.get('gif_p_tax', 0)
            debt = st.session_state.get('gif_d', 0)
            rel = st.session_state.get('gif_r', "성년 자녀(5천만)")
            prev_used_ded = st.session_state.get('gif_prev_ded', 0)
            is_startup = st.session_state.get('gif_startup', False)
            is_overseas = st.session_state.get('gif_overseas', False)
            is_gen_skip = st.session_state.get('gif_skip', False)
            is_minor_high = st.session_state.get('gif_minor', False)

        # Logic
        ded_map = {"배우자": 6e8, "성년": 5e7, "미성년": 2e7, "직계존속": 5e7, "형제자매": 1e7, "기타": 1e7}
        ded_full = 0
        for k, v in ded_map.items():
            if k in rel: ded_full = v; break
        ded = max(0, ded_full - prev_used_ded)  # 잔여 공제액

        tax_base = max(0, (curr + prev - debt) - ded)
        r, p, r_desc = get_tax_rate_5steps(tax_base)
        if is_startup:
            startup_limit = 500_000_000
            if tax_base <= startup_limit:
                calc_tax = tax_base * 0.10
                r_desc = "창업자금 과세특례 (10% 단일세율)"
            else:
                startup_tax = startup_limit * 0.10
                excess = tax_base - startup_limit
                r_ex, p_ex, _ = get_tax_rate_5steps(excess)
                calc_tax = startup_tax + (excess * r_ex - p_ex)
                r_desc = f"창업자금 특례 5억(10%) + 초과분({int(r_ex*100)}%)"
        else:
            calc_tax = tax_base * r - p

        # Surcharge (tax_base 전달하여 20억 초과 자동 검증)
        surcharge_amt, surcharge_desc = TaxEngine.get_generation_skipping_surcharge(calc_tax, is_gen_skip, is_minor_high, tax_base)

        # Credit for previously paid tax (기납부세액공제) - Cannot exceed calculated tax + surcharge
        max_credit = calc_tax + surcharge_amt
        applied_prev_tax = min(prev_tax, max_credit)

        tax_after_prepaid = calc_tax + surcharge_amt - applied_prev_tax
        final_tax = max(0, tax_after_prepaid * 0.97) # 신고세액공제 3%, 음수 방지

        net_gift = curr - debt - final_tax

        # Logic Breakdown Steps (Moved to Result Column)

        with col_result:
            st.subheader("📊 증여 플랜 분석")
            _gif_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;'>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>산출세액 (신고공제 후)</div>
                <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(final_tax)} 원</div>
            </div>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>실질 수령액</div>
                <div style='font-size:1.15rem;font-weight:800;color:#16a34a;word-break:break-all;'>{f_w(net_gift)} 원</div>
                <div style='font-size:0.78rem;color:#64748b;margin-top:4px;'>채무/세금 차감 후</div>
            </div></div>"""
            st.markdown(_gif_html, unsafe_allow_html=True)

            # Pie Chart (음수 값 필터링)
            _pie_names, _pie_vals = [], []
            if net_gift > 0: _pie_names.append('실 수령액'); _pie_vals.append(net_gift)
            if final_tax > 0: _pie_names.append('납부 세액'); _pie_vals.append(final_tax)
            if debt > 0: _pie_names.append('채무 승계액'); _pie_vals.append(debt)
            fig = px.pie(
                names=_pie_names if _pie_vals else ['데이터 없음'],
                values=_pie_vals if _pie_vals else [1],
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
            st.plotly_chart(fig)

            st.divider()

            # Detail Side-by-Side with Logic (Logic moved to Input bottom, so here just Detail)
            with st.expander("🔍 증여세 상세 분석 보기", expanded=True):
                    html_block(f"""
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
                                {rel} 기준 공제한도 <span class='highlight'>{f_w(ded_full)}원</span>{'에서 기사용공제 <span class="highlight">'+f_w(prev_used_ded)+'원</span>을 차감하여' if prev_used_ded > 0 else '을'} 잔여 공제액 <span class='highlight'>{f_w(ded)}원</span>을 적용하여 과세표준 <span class='highlight'>{f_w(tax_base)}원</span>을 확정했습니다.
                                <div class='logic-annotation'>
                                    💡 <b>공제 한도(10년 누적):</b><br>
                                    - 배우자: 6억 / 직계존비속: 5천만원(미성년 2천만원)<br>
                                    - 직계존속: 5천만원 / 기타친족·형제자매: 1천만원
                                </div>
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>3. 최종 세액 산출 ({r_desc})</div>
                            <div class='step-content'>
                                {'창업자금 과세특례: 과세표준(최대 5억) × 10% 단일세율 적용. ' if is_startup else f'과세표준에 누진세율({int(r*100)}%)을 적용하여 산출세액 {f_w(calc_tax)}원을 계산한 뒤, '}{'기납부세액공제 <span class="highlight">' + f_w(applied_prev_tax) + '원</span> 및 ' if applied_prev_tax > 0 else ''}신고세액공제(3%)를 차감하여 최종 납부 세액을 산출합니다.
                            </div>
                        </div>
                    </div>
                    """)

        # Logic Breakdown Steps (Moved to Input Bottom)
        # However, col_input is hidden in presentation mode so this stays in Design Mode context effectively
        if not st.session_state.presentation_mode:
             with col_input:
                html_block(f"""
                <div class='step-box' style='margin-top:20px; border-left:5px solid #22c55e;'>
                <div class='step-title'>📝 단계별 산출 로직</div>
                <div class='step-content'>
                <b>1. 증여세 과세가액 ({f_w(curr+prev-debt)}원)</b><br>
                = (증여재산 {f_w(curr)} + 사전증여 {f_w(prev)}) - 채무 승계 {f_w(debt)}<br>
                <br>
                <b>2. 과세표준 ({f_w(tax_base)}원)</b><br>
                = 과세가액 {f_w(curr+prev-debt)} - 잔여공제({rel}: {f_w(ded_full)}{f' - 기사용 {f_w(prev_used_ded)}' if prev_used_ded > 0 else ''} = {f_w(ded)})<br>
                <br>
                <b>3. 산출세액 ({f_w(calc_tax)}원)</b><br>
                {'= 창업자금 특례: min(과세표준, 5억) × 10% 단일세율' if is_startup else f'= 과세표준 {f_w(tax_base)} × 세율({int(r*100)}%) - 누진공제 {f_w(p)}'}<br>
                <br>
                {'<b>4. 세대생략 할증세액 ('+f_w(surcharge_amt)+'원)</b><br>= 산출세액 '+f_w(calc_tax)+' × 할증률 ('+('40%' if is_minor_high else '30%')+')<br><br>' if is_gen_skip else ''}
                {f'<b>{5 if is_gen_skip else 4}. 기납부세액공제 ({f_w(applied_prev_tax)}원)</b><br>= 사전증여에 대해 이미 납부한 세액 차감<br><br>' if prev_tax > 0 else ''}
                <b>{6 if is_gen_skip and prev_tax > 0 else (5 if is_gen_skip or prev_tax > 0 else 4)}. 최종납부세액 ({f_w(final_tax)}원)</b><br>
                = (산출세액 {f_w(calc_tax)} {f'+ 할증 {f_w(surcharge_amt)}' if is_gen_skip else ''} {f'- 기납부세액 {f_w(applied_prev_tax)}' if prev_tax > 0 else ''}) - 신고세액공제 {f_w(tax_after_prepaid * 0.03)} (3%)
                </div>
                </div>
                """)

        # 결과 저장 (전략 보고서용)
        st.session_state['result_gift_tax'] = final_tax
        st.session_state['result_gift_net'] = net_gift

        # 신고기한 및 납부방법 안내
        if final_tax > 0:
            _deadline = "6개월" if is_overseas else "3개월"
            st.info(f"📅 **증여세 신고 기한**: 증여일이 속하는 달의 말일부터 **{_deadline}** 이내에 관할 세무서에 신고·납부하셔야 합니다. 기한 내 신고 시 신고세액공제(3%)가 적용됩니다.")
            if final_tax > 20_000_000:
                st.info("💡 **연부연납**: 납부세액 2천만원 초과 시 최대 **5년간 분할 납부** 가능합니다. 관할 세무서에 연부연납 허가 신청이 필요하며, 이자율(현행 2.9%)이 적용됩니다.")
            elif final_tax > 10_000_000:
                st.info("💡 **분납**: 납부세액 1천만원 초과 시 **2개월 이내 분납** 가능합니다. 신고 시 분납을 선택하면 별도 신청 없이 적용됩니다.")

        # AI Doctor Call

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
                card_header("💰 상속 재산")
                with st.container(border=True):
                    estate_val = comma_int_input("상속 재산 총액 (원)", st.session_state.inh_ev, "inh_ev", help="고인(피상속인)이 남긴 예금, 주식, 부동산(평가액 기준) 등 모든 재산의 총합입니다.")
                    nontax_estate = comma_int_input("비과세 재산 (원)", 0, "inh_nontax",
                        help="국가·지방자치단체·공익법인에 상속·출연하는 재산은 상속세 과세가액에 산입하지 않습니다.")
                    prev_gift_heir = comma_int_input("상속인(배우자·자녀 등) 10년 내 사전증여재산(원)", 0, "inh_prev_gift_heir",
                        help="배우자·자녀 등 법정상속인에게 사망 전 10년 이내에 증여한 재산 가액 (증여 당시 평가액 기준).")
                    prev_gift_nonheir = comma_int_input("상속인 외(손자·며느리 등) 5년 내 사전증여재산(원)", 0, "inh_prev_gift_nonheir",
                        help="며느리·사위·손자 등 법정상속인이 아닌 자에게 사망 전 5년 이내에 증여한 재산 가액.")
                    prev_gift_inh = prev_gift_heir + prev_gift_nonheir
                    prev_tax_inh = comma_int_input("기납부 증여세액 (원)", 0, "inh_prev_tax", help="합산된 사전증여재산에 대해 과거에 이미 납부했던 증여세액 합계입니다.")
                    debt_inh = comma_int_input("공제 대상 채무액 (원)", 0, "inh_d", help="고인이 남긴 대출금, 미납세금, 반환해야 할 임대보증금 등 상속재산에서 차감될 부채입니다.")
                    funeral = comma_int_input("장례비용(원)", 0, "inh_f", help="장례를 치르는 데 사용된 비용입니다. (기본 500만원 ~ 최대 1,000만원 한도 내 공제, 봉안시설 500만원 별도 추가 가능)")

                card_header("⚙️ 상속 공제 설정")
                with st.container(border=True):
                    has_spouse = st.checkbox("배우자 생존", value=True if 'inh_sp' not in st.session_state else st.session_state.inh_sp, key="inh_sp")

                    # Spouse Deduction Logic
                    spouse_ded_val = 0  # 배우자 미생존 시 공제 없음
                    if has_spouse:
                        spouse_ded_val = st.number_input("배우자 상속공제액(원)", value=0 if 'inh_sp_ded' not in st.session_state else st.session_state.inh_sp_ded, min_value=0, max_value=3_000_000_000, step=10_000_000, format="%d", key="inh_sp_ded", help="배우자가 실제 상속받는 금액을 입력하세요 (법정 최대 30억). 배우자 몫이 없으면 0원.")
                        show_kr_label(st.session_state.get('inh_sp_ded', 0))
                        _sp_input = st.session_state.get('inh_sp_ded', 0)
                        _num_ch_ref = st.session_state.get('inh_children', 2)
                        _legal_sp = int(estate_val * 1.5 / (1.5 + _num_ch_ref)) if (1.5 + _num_ch_ref) > 0 else estate_val
                        st.caption(f"📌 배우자 법정상속분 참고: 약 {f_kr(_legal_sp)} (공제한도 = 실제상속액 vs 법정상속분 중 작은 금액, 최대 30억)")
                        if _sp_input < 500_000_000:
                            st.info("💡 배우자 생존 시 최소 **5억원 공제 보장** (상속세법 제19조). 실제 상속분이 5억 미만이더라도 5억 공제가 적용됩니다.")
                            spouse_ded_val = 500_000_000

                    # Lump-sum vs Itemized
                    ded_type = st.radio("공제 방식", ["일괄공제 (5억)", "기초+인적공제"], horizontal=True, key="inh_type")
                    if "기초" in ded_type:
                        num_children = st.number_input("자녀 수 (5천만원/인)", min_value=0, max_value=20, value=st.session_state.get('inh_children', 2), step=1, format="%d", key="inh_children", help="기초공제 2억 + 자녀 1인당 5천만원 공제")
                        _max_minors = max(0, num_children)
                        num_minors = st.number_input("미성년 자녀 수 (19세 미만, 별도 공제)", min_value=0, max_value=max(1, _max_minors), value=min(st.session_state.get('inh_minors', 0), _max_minors), step=1, format="%d", key="inh_minors", help="미성년 자녀: (19세 - 나이) × 1천만원 추가 공제. 총 자녀 수를 초과할 수 없습니다.")
                        avg_minor_age = 0
                        if num_minors > 0:
                            avg_minor_age = st.number_input("미성년 자녀 평균 나이(세)", min_value=0, max_value=18, value=st.session_state.get('inh_minor_age', 10), step=1, format="%d", key="inh_minor_age")
                        num_elderly = st.number_input("65세 이상 피부양자 수 (5천만원/인)", min_value=0, max_value=20, value=st.session_state.get('inh_elderly', 0), step=1, format="%d", key="inh_elderly")
                        num_disabled = st.number_input("장애인 수 (기대여명×1천만원)", min_value=0, max_value=20, value=st.session_state.get('inh_disabled', 0), step=1, format="%d", key="inh_disabled")
                        avg_disabled_life = 0
                        if num_disabled > 0:
                            avg_disabled_life = st.number_input("장애인 평균 기대여명(년)", min_value=1, max_value=80, value=st.session_state.get('inh_disabled_life', 30), step=1, format="%d", key="inh_disabled_life")

                    # Financial Asset Deduction
                    fin_asset = st.number_input("순금융재산가액(원)", value=0, step=10_000_000, format="%d", key="inh_fin", help="순금융재산의 20%, 최대 2억원 공제 / 2천만원 이하는 전액")
                    show_kr_label(st.session_state.get('inh_fin', 200_000_000), has_help=True)

                with st.container():
                    st.markdown("##### 3. 특별 상속공제")
                    has_coresidence = st.checkbox("동거주택 상속공제",
                        key="inh_coresidence",
                        help="피상속인과 10년 이상 동거한 1세대 1주택 주택 상속 시 주택 가액의 100% (최대 6억원) 공제. 상속 개시 전 10년 이상 무주택자이어야 합니다.")
                    coresidence_ded = 0
                    if has_coresidence:
                        _core_val = comma_int_input("동거 주택 가액(원)", 0, "inh_core_val", help="상속받는 동거 주택의 평가액")
                        coresidence_ded = min(_core_val, 600_000_000)
                        st.caption(f"적용 공제액: {f_kr(coresidence_ded)} (최대 6억)")

                    has_business = st.checkbox("가업상속공제",
                        key="inh_business",
                        help="중소·중견기업 가업을 상속받는 경우 가업상속재산가액의 최대 100% (최대 600억원) 공제. 피상속인이 10년 이상 가업을 경영해야 합니다.")
                    business_ded = 0
                    if has_business:
                        _biz_val = comma_int_input("가업상속재산 가액(원)", 0, "inh_biz_val", help="가업에 해당하는 상속재산 가액")
                        business_ded = min(_biz_val, 60_000_000_000)
                        st.caption(f"적용 공제액: {f_kr(business_ded)} (최대 600억)")

                    has_farming = st.checkbox("영농상속공제",
                        key="inh_farming",
                        help="피상속인이 영농에 종사한 경우 농지·초지·산림지 등 영농재산 최대 30억원 공제.")
                    farming_ded = 0
                    if has_farming:
                        _farm_val = comma_int_input("영농재산 가액(원)", 0, "inh_farm_val", help="공제 대상 농지·어장 등 영농 재산 가액")
                        farming_ded = min(_farm_val, 3_000_000_000)
                        st.caption(f"적용 공제액: {f_kr(farming_ded)} (최대 30억)")

                is_gen_skip_inh = st.checkbox("세대생략 상속 (손주 등)", value=False, key="inh_skip")
        else:
            estate_val = st.session_state.get('inh_ev', 1_500_000_000)
            nontax_estate = st.session_state.get('inh_nontax', 0)
            prev_gift_heir = st.session_state.get('inh_prev_gift_heir', 0)
            prev_gift_nonheir = st.session_state.get('inh_prev_gift_nonheir', 0)
            prev_gift_inh = prev_gift_heir + prev_gift_nonheir
            prev_tax_inh = st.session_state.get('inh_prev_tax', 0)
            debt_inh = st.session_state.get('inh_d', 100_000_000)
            funeral = st.session_state.get('inh_f', 10_000_000)
            has_spouse = st.session_state.get('inh_sp', True)
            spouse_ded_val = st.session_state.get('inh_sp_ded', 0) if has_spouse else 0
            if has_spouse and spouse_ded_val < 500_000_000:
                spouse_ded_val = 500_000_000  # 배우자 생존 시 최소 5억 공제 보장
            ded_type = st.session_state.get('inh_type', "일괄공제 (5억)")
            num_children = st.session_state.get('inh_children', 2)
            num_minors = st.session_state.get('inh_minors', 0)
            avg_minor_age = st.session_state.get('inh_minor_age', 10)
            num_elderly = st.session_state.get('inh_elderly', 0)
            num_disabled = st.session_state.get('inh_disabled', 0)
            avg_disabled_life = st.session_state.get('inh_disabled_life', 30)
            fin_asset = st.session_state.get('inh_fin', 200_000_000)
            coresidence_ded = min(st.session_state.get('inh_core_val', 0), 600_000_000) if st.session_state.get('inh_coresidence', False) else 0
            business_ded = min(st.session_state.get('inh_biz_val', 0), 60_000_000_000) if st.session_state.get('inh_business', False) else 0
            farming_ded = min(st.session_state.get('inh_farm_val', 0), 3_000_000_000) if st.session_state.get('inh_farming', False) else 0
            is_gen_skip_inh = st.session_state.get('inh_skip', False)

        # Logic
        # 배우자공제 법정상속분 한도 적용 (상속세법 제19조)
        if has_spouse and spouse_ded_val > 0:
            _num_ch_calc = st.session_state.get('inh_children', 2)
            _legal_sp_calc = int(estate_val * 1.5 / (1.5 + _num_ch_calc)) if (1.5 + _num_ch_calc) > 0 else estate_val
            spouse_ded_val = max(500_000_000, min(spouse_ded_val, _legal_sp_calc, 3_000_000_000))

        basic_ded = 200_000_000
        if "일괄" in ded_type:
            final_other_ded = 500_000_000
        else:
            num_children_calc = st.session_state.get('inh_children', 2)
            num_minors_calc = st.session_state.get('inh_minors', 0)
            avg_minor_age_calc = st.session_state.get('inh_minor_age', 10)
            num_elderly_calc = st.session_state.get('inh_elderly', 0)
            num_disabled_calc = st.session_state.get('inh_disabled', 0)
            avg_disabled_life_calc = st.session_state.get('inh_disabled_life', 30)
            child_ded = num_children_calc * 50_000_000
            minor_ded = num_minors_calc * max(0, 19 - avg_minor_age_calc) * 10_000_000
            elderly_ded = num_elderly_calc * 50_000_000
            disabled_ded = num_disabled_calc * avg_disabled_life_calc * 10_000_000
            final_other_ded = basic_ded + child_ded + minor_ded + elderly_ded + disabled_ded
            # 기초+인적공제 합계가 일괄공제(5억)보다 작으면 일괄공제 적용 (납세자 유리 원칙)
            if final_other_ded < 500_000_000:
                final_other_ded = 500_000_000

        fin_ded = 0
        if fin_asset <= 20_000_000: fin_ded = fin_asset
        else: fin_ded = min(200_000_000, max(20_000_000, fin_asset * 0.2))

        # Calculation
        funeral = max(5_000_000, min(funeral, 15_000_000))  # 장례비용 공제: 최소 500만원 보장, 최대 1,500만원
        net_estate = estate_val + prev_gift_inh - debt_inh - funeral - nontax_estate
        total_deduction = final_other_ded + spouse_ded_val + fin_ded + coresidence_ded + business_ded + farming_ded
        # 공제적용한도액: 상속공제 합계는 (과세가액 - 사전증여 합산액)을 초과할 수 없음
        deduction_limit = max(0, net_estate - prev_gift_inh)
        total_deduction = min(total_deduction, deduction_limit)
        tax_base = max(0, net_estate - total_deduction)

        r_i, p_i, r_desc = get_tax_rate_5steps(tax_base)
        calc_tax_i = tax_base * r_i - p_i

        # Surcharge
        surcharge_inh, surcharge_inh_desc = TaxEngine.get_generation_skipping_surcharge(calc_tax_i, is_gen_skip_inh, False)

        # Credit for previously paid gift tax
        max_credit_inh = calc_tax_i + surcharge_inh
        applied_prev_tax_inh = min(prev_tax_inh, max_credit_inh)

        tax_after_prepaid_inh = calc_tax_i + surcharge_inh - applied_prev_tax_inh
        final_tax_i = max(0, tax_after_prepaid_inh * 0.97) # Declaration Credit, 음수 방지

        with col_result:
            st.subheader("📊 상속세 분석 결과")
            _inh_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;'>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>과세표준</div>
                <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(tax_base)} 원</div>
            </div>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>최종 예상 납부액</div>
                <div style='font-size:1.15rem;font-weight:800;color:#ef4444;word-break:break-all;'>{f_w(final_tax_i)} 원</div>
            </div></div>"""
            st.markdown(_inh_html, unsafe_allow_html=True)

            # Waterfall Chart for Tax Logic
            fig = go.Figure(go.Waterfall(
                name = "20", orientation = "v",
                measure = ["relative", "relative", "relative", "relative", "total", "total"],
                x = ["상속재산", "사전증여합산", "채무·비과세", "상속공제", "과세표준", "예상 세액"],
                textposition = "outside",
                text = [f"{f_w(estate_val/1e8)}억", f"{f_w(prev_gift_inh/1e8)}억", f"-{f_w((debt_inh+funeral+nontax_estate)/1e8)}억",
                        f"-{f_w(total_deduction/1e8)}억", f"{f_w(tax_base/1e8)}억", f"-{f_w(final_tax_i/1e8)}억"],
                y = [estate_val, prev_gift_inh, -(debt_inh+funeral+nontax_estate), -total_deduction, tax_base, -final_tax_i],
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
            st.plotly_chart(fig)

            st.divider()

            # Logic & Detail Side-by-Side
            # Logic & Detail Side-by-Side (Refactored)
            c_detail = st.container()


            with c_detail:
                with st.expander("🔍 상속세 상세 분석 보기", expanded=True):
                    html_block(f"""
                    <div class='expert-card'>
                        <div class='expert-title'>📑 상속세 산출 리포트</div>
                        <div class='step-box'>
                            <div class='step-title'>STEP 1. 과세가액 파악 ({'합산없음' if prev_gift_inh==0 else '사전증여 합산'})</div>
                            <div class='step-content'>
                                총 상속재산 <span class='highlight'>{f_w(estate_val)}원</span>{'에서 ' if prev_gift_inh == 0 else f'과 사전증여재산 <span class="highlight">{f_w(prev_gift_inh)}원</span>(상속인 10년 + 비상속인 5년)을 합산한 뒤, '}채무·장례비 <span class='highlight'>{f_w(debt_inh+funeral)}원</span>{f'과 비과세재산 <span class="highlight">{f_w(nontax_estate)}원</span>' if nontax_estate > 0 else ''}을 차감합니다.
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>STEP 2. 상속공제 적용 ({'일괄' if '일괄' in ded_type else '기초+인적'})</div>
                            <div class='step-content'>
                                배우자공제 <span class='highlight'>{f_w(spouse_ded_val)}원</span>,
                                {ded_type} <span class='highlight'>{f_w(final_other_ded)}원</span>,
                                금융재산공제 <span class='highlight'>{f_w(fin_ded)}원</span>
                                {f', 동거주택공제 <span class="highlight">{f_w(coresidence_ded)}원</span>' if coresidence_ded > 0 else ''}
                                {f', 가업상속공제 <span class="highlight">{f_w(business_ded)}원</span>' if business_ded > 0 else ''}
                                {f', 영농상속공제 <span class="highlight">{f_w(farming_ded)}원</span>' if farming_ded > 0 else ''}을 적용했습니다.
                                <br>👉 <b>총 공제액: {f_w(total_deduction)}원</b>
                                <div class='logic-annotation'>
                                    💡 <b>주요 공제 한도:</b><br>
                                    금융재산공제: 20% (최대 2억) / 동거주택: 최대 6억 / 가업상속: 최대 600억 / 영농: 최대 30억
                                </div>
                            </div>
                        </div>
                        <div class='step-box'>
                            <div class='step-title'>STEP 3. 과세표준 및 세액 - {r_desc}</div>
                            <div class='step-content'>
                                과세표준 {f_w(tax_base)}원에 대해 세율 {int(r_i*100)}%가 적용되며, {'기납부증여세액공제 <span class="highlight">' + f_w(applied_prev_tax_inh) + '원</span> 및 ' if applied_prev_tax_inh > 0 else ''}신고세액공제를 차감하여 최종 세액을 산출합니다.
                                <div class='logic-annotation'>
                                    💡 <b>상속세율 구간:</b><br>
                                    - 1억 이하: 10% / 5억 이하: 20% (누진공제 1천만원)<br>
                                    - 10억 이하: 30% (6천만) / 30억 이하: 40% (1.6억) / 30억 초과: 50% (4.6억)
                                </div>
                            </div>
                        </div>
                    </div>
                    """)

        # Logic Breakdown Steps (Moved to Input Bottom)
        if not st.session_state.presentation_mode:
            with col_input:
                html_block(f"""
                <div class='step-box' style='margin-top:20px; border-left:5px solid #a855f7;'>
                <div class='step-title'>📝 단계별 산출 로직</div>
                <div class='step-content'>
                <b>1. 상속세 과세가액 ({f_w(net_estate)}원)</b><br>
                = (상속재산 {f_w(estate_val)} + 사전증여 {f_w(prev_gift_inh)}) - (채무/장례 {f_w(debt_inh+funeral)}{f' - 비과세 {f_w(nontax_estate)}' if nontax_estate > 0 else ''})<br>
                <br>
                <b>2. 상속공제 총액 ({f_w(total_deduction)}원)</b><br>
                = 기초/일괄 {f_w(final_other_ded)} + 배우자 {f_w(spouse_ded_val)} + 금융 {f_w(fin_ded)}{f' + 동거주택 {f_w(coresidence_ded)}' if coresidence_ded > 0 else ''}{f' + 가업 {f_w(business_ded)}' if business_ded > 0 else ''}{f' + 영농 {f_w(farming_ded)}' if farming_ded > 0 else ''}<br>
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
                """)

        # 납부방법 안내
        if final_tax_i > 0:
            st.info("📅 **상속세 신고 기한**: 상속개시일(사망일)이 속하는 달의 말일부터 **6개월** 이내 신고·납부. (국외 거주자 9개월)")
            if final_tax_i > 20_000_000:
                st.info("💡 **납부 방법**: ① **분납** — 1천만원 초과 시 2개월 이내 분납 가능  ② **연부연납** — 2천만원 초과 시 최대 **10년 분할 납부** (세무서 허가 필요, 이자율 적용)  ③ **물납** — 현금 납부 곤란 시 부동산·유가증권으로 납부 신청 가능")

        # 결과 저장 (전략 보고서용)
        st.session_state['result_inh_tax'] = final_tax_i
        st.session_state['result_inh_estate'] = estate_val

        # AI Doctor Call

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

        _ins_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;'>
        <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #fecaca;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
            <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>A안 (부모 납입)</div>
            <div style='font-size:1.15rem;font-weight:800;color:#ef4444;word-break:break-all;'>{f_w(final_tax_A)} 원</div>
            <div style='font-size:0.78rem;color:#dc2626;margin-top:4px;'>보험금이 상속재산에 합산 부과</div>
        </div>
        <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #bbf7d0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
            <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>B안 (자녀 납입)</div>
            <div style='font-size:1.15rem;font-weight:800;color:#16a34a;word-break:break-all;'>{f_w(final_tax_B)} 원</div>
            <div style='font-size:0.78rem;color:#16a34a;margin-top:4px;'>{f_w(tax_saving)}원 상속세 절감 효과</div>
        </div></div>"""
        st.markdown(_ins_html, unsafe_allow_html=True)

        st.info("💡 **자녀가 계약자/납입자**가 되고 실질적인 소득증빙이 가능하다면, 종신보험의 사망보험금은 상속재산에 포함되지 않아 **상속세 없이 100% 비과세 현금 수령**이 가능합니다.")

        fig_ins = go.Figure(data=[
            go.Bar(name='예상 상속세', x=['A안 (합산과세)', 'B안 (비과세)'], y=[final_tax_A, final_tax_B], marker_color=['#ef4444', '#3b82f6'], text=[f"{f_w(final_tax_A)}원", f"{f_w(final_tax_B)}원"], textposition='auto')
        ])
        fig_ins.update_layout(title="계약 구조별 상속세액 비교", template="plotly_white", height=300, margin=dict(t=40, b=20, l=20, r=20))
        st.plotly_chart(fig_ins)

