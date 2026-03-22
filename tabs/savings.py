import streamlit as st
import plotly.graph_objects as go
from core import f_w, f_kr, comma_int_input, html_block, render_title_with_reset, SavingsState, card_header, make_sync_callback


TAX_RATES = {"일반과세": 0.154, "세금우대": 0.095, "비과세": 0.0}
TAX_LABELS = {
    "일반과세": ("15.4%", "이자소득세 14% + 지방소득세 1.4%", "#ef4444"),
    "세금우대": ("9.5%", "조합 등 세금우대 저축 (농협·수협·신협·새마을금고 등)", "#f59e0b"),
    "비과세": ("0%", "비과세종합저축 (만 65세 이상, 장애인 등 대상)", "#22c55e"),
}


def render_savings():
    render_title_with_reset(
        "💰 예적금 계산기",
        ["dep_", "sav_"],
        "reset_savings",
        default_states=[SavingsState()],
    )
    st.markdown("예금과 적금의 **이자를 계산**하고, 만기 수령액을 통해 **목적 자금 계획**을 수립합니다.")

    tab1, tab2 = st.tabs(["🏦 예금 계산기", "💰 적금 계산기"])

    with tab1:
        _render_deposit()
    with tab2:
        _render_installment()


def _render_tax_info_cards():
    """과세 구분 안내 카드 3열 (공용)"""
    cards = ""
    for name, (rate, desc, color) in TAX_LABELS.items():
        cards += f"""
        <div style="flex:1; min-width:140px; background:white; border-radius:10px; padding:14px; border-left:4px solid {color};">
            <div style="font-size:14px; font-weight:700; color:#1e293b; margin-bottom:4px;">{name}</div>
            <div style="font-size:20px; font-weight:800; color:{color}; margin-bottom:6px;">{rate}</div>
            <div style="font-size:11px; color:#64748b; line-height:1.4;">{desc}</div>
        </div>"""
    return f'<div style="display:flex; gap:10px; flex-wrap:wrap;">{cards}</div>'


# ──────────────────────────────────────────────
# 예금 (정기예금) 탭
# ──────────────────────────────────────────────
def _render_deposit():
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")

    # ── 입력 ──
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 예금 정보 입력")

            card_header("💵 예금 정보")
            with st.container(border=True):
                dep_amount = comma_int_input(
                    "예치 금액 (원)",
                    st.session_state.get("dep_amount", 10_000_000),
                    "dep_amount",
                )
                dep_rate = st.number_input(
                    "연 이율 (%)",
                    min_value=0.01,
                    max_value=100.0,
                    value=st.session_state.get("dep_rate", 3.5),
                    step=0.01,
                    format="%.2f",
                    key="dep_rate",
                )

                if "dep_years_sl" not in st.session_state:
                    st.session_state.dep_years_sl = 1
                if "dep_years_num" not in st.session_state:
                    st.session_state.dep_years_num = 1

                st.markdown("예치 기간 (년)")
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.slider(
                        "예치 기간",
                        min_value=1,
                        max_value=10,
                        key="dep_years_sl",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("dep_years_sl", "dep_years_num"),
                    )
                with c2:
                    st.number_input(
                        "예치 기간 입력",
                        min_value=1,
                        max_value=10,
                        key="dep_years_num",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("dep_years_num", "dep_years_sl"),
                    )

                dep_tax_type = st.radio(
                    "과세 구분",
                    list(TAX_RATES.keys()),
                    horizontal=True,
                    key="dep_tax",
                )
    else:
        dep_amount = st.session_state.get("dep_amount", 10_000_000)
        dep_rate = st.session_state.get("dep_rate", 3.5)
        dep_tax_type = st.session_state.get("dep_tax", "일반과세")

    dep_years = st.session_state.get("dep_years_sl", 1)
    tax_rate = TAX_RATES.get(dep_tax_type if not st.session_state.presentation_mode else st.session_state.get("dep_tax", "일반과세"), 0.154)

    # ── 계산 ──
    pre_tax_interest = dep_amount * (dep_rate / 100) * dep_years
    tax_amount = pre_tax_interest * tax_rate
    post_tax_interest = pre_tax_interest - tax_amount
    maturity = dep_amount + post_tax_interest

    # ── 결과 ──
    with col_result:
        st.subheader("📊 예금 계산 결과")

        # KPI 카드
        html_block(f"""
        <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:18px;">
            <div style="background:#f0f9ff; border-radius:12px; padding:14px 18px; border:1px solid #bae6fd;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#0369a1; font-weight:600;">세전 이자</span>
                    <span style="font-size:20px; font-weight:700; color:#0c4a6e;">{f_w(round(pre_tax_interest))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">{f_w(dep_amount)} x {dep_rate}% x {dep_years}년</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:14px 18px; border:1px solid #bbf7d0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#15803d; font-weight:600;">세후 이자</span>
                    <span style="font-size:20px; font-weight:700; color:#14532d;">{f_w(round(post_tax_interest))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">{f_w(round(pre_tax_interest))} - 세금 {f_w(round(tax_amount))} ({tax_rate*100:.1f}%)</div>
            </div>
            <div style="background:#fefce8; border-radius:12px; padding:14px 18px; border:1px solid #fde68a;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#a16207; font-weight:600;">만기 수령액</span>
                    <span style="font-size:22px; font-weight:800; color:#78350f;">{f_w(round(maturity))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">원금 {f_w(dep_amount)} + 세후이자 {f_w(round(post_tax_interest))}</div>
            </div>
        </div>
        """)

        # 워터폴 차트
        y_max = maturity * 1.15
        fig = go.Figure(
            go.Waterfall(
                x=["원금", "세전 이자", "세금", "만기 수령액"],
                measure=["absolute", "relative", "relative", "total"],
                y=[dep_amount, round(pre_tax_interest), -round(tax_amount), 0],
                text=[f"{f_w(dep_amount)}", f"+{f_w(round(pre_tax_interest))}", f"-{f_w(round(tax_amount))}", f"{f_w(round(maturity))}"],
                textposition="outside",
                textfont=dict(size=12),
                connector=dict(line=dict(color="#cbd5e1", width=1, dash="dot")),
                increasing=dict(marker=dict(color="#22c55e")),
                decreasing=dict(marker=dict(color="#ef4444")),
                totals=dict(marker=dict(color="#f59e0b")),
                hovertemplate="%{x}: %{y:,.0f}원<extra></extra>",
            )
        )
        fig.update_layout(
            yaxis=dict(tickformat=",", title="금액 (원)", range=[0, y_max]),
            margin=dict(t=60, b=30, l=60, r=20),
            height=380,
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

        # 계산 방법 안내
        with st.expander("📋 예금 계산 방법 안내"):
            _render_deposit_guide(dep_amount, dep_rate, dep_years, pre_tax_interest, tax_amount, post_tax_interest, maturity, tax_rate)


def _render_deposit_guide(dep_amount, dep_rate, dep_years, pre_tax, tax_amt, post_tax, maturity, tax_rate):
    """예금 계산 방법 안내 — 전문 디자인"""
    html_block(f"""
    <div style="font-family:sans-serif;">
        <div style="background:#f8fafc; border-radius:10px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">📐 정기예금 단리 계산 공식</div>
            <div style="background:white; border-radius:8px; padding:14px; border:1px solid #e2e8f0;">
                <div style="font-size:13px; color:#334155; line-height:2;">
                    <div><b>세전 이자</b> = 원금 x 연이율 x 예치기간(년)</div>
                    <div style="color:#64748b; padding-left:20px;">= {f_w(dep_amount)}원 x {dep_rate}% x {dep_years}년 = <b style="color:#0369a1;">{f_w(round(pre_tax))}원</b></div>
                    <div style="margin-top:6px;"><b>세후 이자</b> = 세전 이자 - (세전 이자 x 세율(이자소득세 15.4%))</div>
                    <div style="color:#64748b; padding-left:20px;">= {f_w(round(pre_tax))}원 - {f_w(round(tax_amt))}원 = <b style="color:#15803d;">{f_w(round(post_tax))}원</b></div>
                    <div style="margin-top:6px;"><b>만기 수령액</b> = 원금 + 세후 이자</div>
                    <div style="color:#64748b; padding-left:20px;">= {f_w(dep_amount)}원 + {f_w(round(post_tax))}원 = <b style="color:#78350f;">{f_w(round(maturity))}원</b></div>
                </div>
            </div>
        </div>

        <div style="background:#f8fafc; border-radius:10px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">📊 상세 내역</div>
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">예치 원금</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1e293b;">{f_w(dep_amount)}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">연 이율</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1e293b;">{dep_rate}%</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">예치 기간</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1e293b;">{dep_years}년 ({dep_years * 12}개월)</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">세전 이자</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#0369a1;">{f_w(round(pre_tax))}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">이자 과세 ({tax_rate*100:.1f}%)</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#ef4444;">-{f_w(round(tax_amt))}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">세후 이자</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#15803d;">{f_w(round(post_tax))}원</td>
                </tr>
                <tr style="background:#fefce8;">
                    <td style="padding:12px 8px; font-weight:700; color:#78350f;">만기 수령액</td>
                    <td style="padding:12px 8px; text-align:right; font-weight:800; font-size:15px; color:#78350f;">{f_w(round(maturity))}원</td>
                </tr>
            </table>
        </div>

        <div style="background:#f8fafc; border-radius:10px; padding:16px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">💡 과세 구분 안내</div>
            {_render_tax_info_cards()}
            <div style="margin-top:10px; font-size:11px; color:#94a3b8; line-height:1.5;">
                * 이자소득이 연 2,000만원을 초과하면 금융소득종합과세 대상이 될 수 있습니다.<br>
                * 세금우대 저축은 조합원 가입이 필요하며, 1인 최대 3,000만원 한도입니다.<br>
                * 비과세종합저축은 만 65세 이상·장애인 등 대상이며, 1인 최대 5,000만원 한도입니다.
            </div>
        </div>
    </div>
    """)


# ──────────────────────────────────────────────
# 적금 (정기적금) 탭
# ──────────────────────────────────────────────
def _render_installment():
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")

    # ── 입력 ──
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 적금 정보 입력")

            card_header("💵 적금 정보")
            with st.container(border=True):
                sav_amount = comma_int_input(
                    "월 납입액 (원)",
                    st.session_state.get("sav_amount", 300_000),
                    "sav_amount",
                )
                sav_rate = st.number_input(
                    "연 이율 (%)",
                    min_value=0.01,
                    max_value=100.0,
                    value=st.session_state.get("sav_rate", 3.5),
                    step=0.01,
                    format="%.2f",
                    key="sav_rate",
                )

                if "sav_years_sl" not in st.session_state:
                    st.session_state.sav_years_sl = 1
                if "sav_years_num" not in st.session_state:
                    st.session_state.sav_years_num = 1

                st.markdown("납입 기간 (년)")
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.slider(
                        "납입 기간",
                        min_value=1,
                        max_value=10,
                        key="sav_years_sl",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("sav_years_sl", "sav_years_num"),
                    )
                with c2:
                    st.number_input(
                        "납입 기간 입력",
                        min_value=1,
                        max_value=10,
                        key="sav_years_num",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("sav_years_num", "sav_years_sl"),
                    )

                sav_tax_type = st.radio(
                    "과세 구분",
                    list(TAX_RATES.keys()),
                    horizontal=True,
                    key="sav_tax",
                )

    else:
        sav_amount = st.session_state.get("sav_amount", 300_000)
        sav_rate = st.session_state.get("sav_rate", 3.5)
        sav_tax_type = st.session_state.get("sav_tax", "일반과세")

    sav_years = st.session_state.get("sav_years_sl", 1)
    n = sav_years * 12  # 총 개월수
    tax_rate = TAX_RATES.get(sav_tax_type if not st.session_state.presentation_mode else st.session_state.get("sav_tax", "일반과세"), 0.154)

    # ── 계산 ──
    monthly_rate = sav_rate / 100 / 12
    pre_tax_interest = sav_amount * monthly_rate * (n * (n + 1)) / 2
    tax_amount = pre_tax_interest * tax_rate
    post_tax_interest = pre_tax_interest - tax_amount
    total_paid = sav_amount * n
    maturity = total_paid + post_tax_interest

    # ── 결과 ──
    with col_result:
        st.subheader("📊 적금 계산 결과")

        # KPI 카드
        html_block(f"""
        <div style="display:flex; flex-direction:column; gap:10px; margin-bottom:18px;">
            <div style="background:#eff6ff; border-radius:12px; padding:14px 18px; border:1px solid #bfdbfe;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#1d4ed8; font-weight:600;">총 납입액</span>
                    <span style="font-size:20px; font-weight:700; color:#1e3a5f;">{f_w(round(total_paid))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">월 {f_w(sav_amount)} x {n}개월 ({sav_years}년)</div>
            </div>
            <div style="background:#f0f9ff; border-radius:12px; padding:14px 18px; border:1px solid #bae6fd;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#0369a1; font-weight:600;">세전 이자</span>
                    <span style="font-size:20px; font-weight:700; color:#0c4a6e;">{f_w(round(pre_tax_interest))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">{f_w(sav_amount)} x ({sav_rate}%/12) x {n}x{n+1}/2</div>
            </div>
            <div style="background:#f0fdf4; border-radius:12px; padding:14px 18px; border:1px solid #bbf7d0;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#15803d; font-weight:600;">세후 이자</span>
                    <span style="font-size:20px; font-weight:700; color:#14532d;">{f_w(round(post_tax_interest))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">{f_w(round(pre_tax_interest))} - 세금 {f_w(round(tax_amount))} ({tax_rate*100:.1f}%)</div>
            </div>
            <div style="background:#fefce8; border-radius:12px; padding:14px 18px; border:1px solid #fde68a;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span style="font-size:14px; color:#a16207; font-weight:600;">만기 수령액</span>
                    <span style="font-size:22px; font-weight:800; color:#78350f;">{f_w(round(maturity))}원</span>
                </div>
                <div style="font-size:11px; color:#64748b; margin-top:4px;">납입 {f_w(round(total_paid))} + 세후이자 {f_w(round(post_tax_interest))}</div>
            </div>
        </div>
        """)

        # 월별 이자 내역표 (KPI 바로 아래)
        with st.expander("📋 월별 이자 내역표", expanded=True):
            table_rows = ""
            running_paid = 0
            running_interest = 0
            for m in range(1, n + 1):
                running_paid += sav_amount
                month_interest = sav_amount * monthly_rate * (n - m + 1)
                running_interest += month_interest
                post_running = running_interest * (1 - tax_rate)
                balance = running_paid + post_running
                table_rows += f"<tr style='border-bottom:1px solid #f1f5f9;'><td style='text-align:center;'>{m}</td><td style='text-align:center;'>{f_w(sav_amount)}</td><td style='text-align:center;'>{f_w(running_paid)}</td><td style='text-align:center;'>{f_w(round(month_interest))}</td><td style='text-align:center;'>{f_w(round(running_interest))}</td><td style='text-align:center;'>{f_w(round(balance))}</td></tr>"

            html_block(f"""
            <div style="max-height:400px; overflow-y:auto;">
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <thead style="position:sticky; top:0; background:#f1f5f9;">
                    <tr style="border-bottom:2px solid #cbd5e1;">
                        <th style="padding:8px 4px; text-align:center;">월</th>
                        <th style="padding:8px 4px; text-align:center;">월 저축액</th>
                        <th style="padding:8px 4px; text-align:center;">누적 저축액</th>
                        <th style="padding:8px 4px; text-align:center;">월 이자</th>
                        <th style="padding:8px 4px; text-align:center;">누적 이자</th>
                        <th style="padding:8px 4px; text-align:center;">예상 수령액</th>
                    </tr>
                    <tr><td colspan="6" style="text-align:right; font-size:10px; color:#94a3b8; padding:2px 4px;">단위: 원</td></tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            </div>
            """)

        # 계산 방법 안내
        with st.expander("📋 적금 계산 방법 안내"):
            _render_installment_guide(sav_amount, sav_rate, sav_years, n, pre_tax_interest, tax_amount, post_tax_interest, total_paid, maturity, tax_rate)


def _render_installment_guide(sav_amount, sav_rate, sav_years, n, pre_tax, tax_amt, post_tax, total_paid, maturity, tax_rate):
    """적금 계산 방법 안내 — 전문 디자인"""
    html_block(f"""
    <div style="font-family:sans-serif;">
        <div style="background:#f8fafc; border-radius:10px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">📐 정기적금 단리 계산 공식</div>
            <div style="background:white; border-radius:8px; padding:14px; border:1px solid #e2e8f0;">
                <div style="font-size:13px; color:#334155; line-height:2;">
                    <div><b>세전 이자</b> = 월납입액 x (연이율 / 12) x 개월수 x (개월수 + 1) / 2</div>
                    <div style="color:#64748b; padding-left:20px;">= {f_w(sav_amount)}원 x ({sav_rate}% / 12) x {n} x {n+1} / 2 = <b style="color:#0369a1;">{f_w(round(pre_tax))}원</b></div>
                    <div style="margin-top:6px;"><b>세후 이자</b> = 세전 이자 - (세전 이자 x 세율(이자소득세 15.4%))</div>
                    <div style="color:#64748b; padding-left:20px;">= {f_w(round(pre_tax))}원 - {f_w(round(tax_amt))}원 = <b style="color:#15803d;">{f_w(round(post_tax))}원</b></div>
                    <div style="margin-top:6px;"><b>만기 수령액</b> = 총 납입액 + 세후 이자</div>
                    <div style="color:#64748b; padding-left:20px;">= {f_w(round(total_paid))}원 + {f_w(round(post_tax))}원 = <b style="color:#78350f;">{f_w(round(maturity))}원</b></div>
                </div>
            </div>
        </div>

        <div style="background:#f8fafc; border-radius:10px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">💡 월별 이자 적용 원리</div>
            <div style="background:white; border-radius:8px; padding:14px; border:1px solid #e2e8f0; font-size:13px; color:#334155; line-height:1.8;">
                적금은 매월 납입하므로, <b>각 회차 납입금마다 남은 기간에 비례</b>하여 이자가 발생합니다.
                <div style="margin-top:10px; padding:10px; background:#f0f9ff; border-radius:6px; font-size:12px;">
                    <div>1회차 납입금 → <b>{n}개월</b>간 이자 발생</div>
                    <div>2회차 납입금 → <b>{n-1}개월</b>간 이자 발생</div>
                    <div style="color:#94a3b8;">...</div>
                    <div>{n}회차 납입금 → <b>1개월</b>간 이자 발생</div>
                </div>
                <div style="margin-top:8px; color:#64748b; font-size:11px;">
                    먼저 납입한 금액일수록 더 많은 이자를 받게 되며, 이를 모두 합산한 것이 세전 이자입니다.
                </div>
            </div>
        </div>

        <div style="background:#f8fafc; border-radius:10px; padding:16px; margin-bottom:14px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">📊 상세 내역</div>
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">월 납입액</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1e293b;">{f_w(sav_amount)}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">연 이율</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1e293b;">{sav_rate}%</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">납입 기간</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1e293b;">{sav_years}년 ({n}개월)</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">총 납입액</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#1d4ed8;">{f_w(round(total_paid))}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">세전 이자</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#0369a1;">{f_w(round(pre_tax))}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">이자 과세 ({tax_rate*100:.1f}%)</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#ef4444;">-{f_w(round(tax_amt))}원</td>
                </tr>
                <tr style="border-bottom:1px solid #e2e8f0;">
                    <td style="padding:10px 8px; color:#64748b;">세후 이자</td>
                    <td style="padding:10px 8px; text-align:right; font-weight:600; color:#15803d;">{f_w(round(post_tax))}원</td>
                </tr>
                <tr style="background:#fefce8;">
                    <td style="padding:12px 8px; font-weight:700; color:#78350f;">만기 수령액</td>
                    <td style="padding:12px 8px; text-align:right; font-weight:800; font-size:15px; color:#78350f;">{f_w(round(maturity))}원</td>
                </tr>
            </table>
        </div>

        <div style="background:#f8fafc; border-radius:10px; padding:16px; border:1px solid #e2e8f0;">
            <div style="font-size:14px; font-weight:700; color:#0f172a; margin-bottom:10px;">💡 과세 구분 안내</div>
            {_render_tax_info_cards()}
            <div style="margin-top:10px; font-size:11px; color:#94a3b8; line-height:1.5;">
                * 이자소득이 연 2,000만원을 초과하면 금융소득종합과세 대상이 될 수 있습니다.<br>
                * 세금우대 저축은 조합원 가입이 필요하며, 1인 최대 3,000만원 한도입니다.<br>
                * 비과세종합저축은 만 65세 이상·장애인 등 대상이며, 1인 최대 5,000만원 한도입니다.
            </div>
        </div>
    </div>
    """)
