import streamlit as st
import plotly.graph_objects as go
from core import f_w, f_kr, comma_int_input, html_block, render_title_with_reset, SavingsState, card_header, make_sync_callback


TAX_RATES = {"일반과세": 0.154, "세금우대": 0.095, "비과세": 0.0}


def render_savings():
    render_title_with_reset(
        "💰 예적금 계산기",
        ["dep_", "sav_"],
        "reset_savings",
        default_states=[SavingsState()],
    )
    st.markdown("예금과 적금의 **단리 이자**를 계산하고, 만기 수령액을 확인하세요.")

    tab1, tab2 = st.tabs(["🏦 예금 계산기", "💰 적금 계산기"])

    with tab1:
        _render_deposit()
    with tab2:
        _render_installment()


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
                    max_value=20.0,
                    value=st.session_state.get("dep_rate", 3.5),
                    step=0.01,
                    format="%.2f",
                    key="dep_rate",
                )

                # 슬라이더 + 숫자입력 동기화
                if "dep_months_sl" not in st.session_state:
                    st.session_state.dep_months_sl = 12
                if "dep_months_num" not in st.session_state:
                    st.session_state.dep_months_num = 12

                st.markdown("예치 기간 (개월)")
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.slider(
                        "예치 기간",
                        min_value=1,
                        max_value=60,
                        key="dep_months_sl",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("dep_months_sl", "dep_months_num"),
                    )
                with c2:
                    st.number_input(
                        "예치 기간 입력",
                        min_value=1,
                        max_value=60,
                        key="dep_months_num",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("dep_months_num", "dep_months_sl"),
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

    dep_months = st.session_state.get("dep_months_sl", 12)
    tax_rate = TAX_RATES.get(dep_tax_type if not st.session_state.presentation_mode else st.session_state.get("dep_tax", "일반과세"), 0.154)

    # ── 계산 ──
    pre_tax_interest = dep_amount * (dep_rate / 100) * (dep_months / 12)
    tax_amount = pre_tax_interest * tax_rate
    post_tax_interest = pre_tax_interest - tax_amount
    maturity = dep_amount + post_tax_interest

    # ── 결과 ──
    with col_result:
        st.subheader("📊 예금 계산 결과")

        # KPI 카드
        html_block(f"""
        <div style="display:flex; gap:12px; flex-wrap:wrap; margin-bottom:18px;">
            <div style="flex:1; min-width:140px; background:#f0f9ff; border-radius:12px; padding:16px; text-align:center; border:1px solid #bae6fd;">
                <div style="font-size:13px; color:#0369a1;">세전 이자</div>
                <div style="font-size:22px; font-weight:700; color:#0c4a6e;">{f_w(round(pre_tax_interest))}원</div>
            </div>
            <div style="flex:1; min-width:140px; background:#f0fdf4; border-radius:12px; padding:16px; text-align:center; border:1px solid #bbf7d0;">
                <div style="font-size:13px; color:#15803d;">세후 이자</div>
                <div style="font-size:22px; font-weight:700; color:#14532d;">{f_w(round(post_tax_interest))}원</div>
            </div>
            <div style="flex:1; min-width:140px; background:#fefce8; border-radius:12px; padding:16px; text-align:center; border:1px solid #fde68a;">
                <div style="font-size:13px; color:#a16207;">만기 수령액</div>
                <div style="font-size:24px; font-weight:800; color:#78350f;">{f_w(round(maturity))}원</div>
            </div>
        </div>
        """)

        # 도넛 차트
        fig = go.Figure(
            data=[
                go.Pie(
                    labels=["원금", "세후 이자"],
                    values=[dep_amount, max(0, round(post_tax_interest))],
                    hole=0.55,
                    marker=dict(colors=["#3b82f6", "#22c55e"]),
                    textinfo="label+percent",
                    textfont=dict(size=14),
                    hovertemplate="%{label}: %{value:,.0f}원<extra></extra>",
                )
            ]
        )
        fig.update_layout(
            showlegend=False,
            margin=dict(t=30, b=20, l=20, r=20),
            height=320,
            annotations=[
                dict(
                    text=f"<b>만기<br>{f_w(round(maturity))}원</b>",
                    x=0.5,
                    y=0.5,
                    font_size=15,
                    showarrow=False,
                )
            ],
        )
        st.plotly_chart(fig, use_container_width=True)

        # 세금 상세
        if tax_rate > 0:
            html_block(f"""
            <div style="background:#fef2f2; border-radius:10px; padding:12px 16px; margin-bottom:12px; border:1px solid #fecaca;">
                <span style="font-size:13px; color:#991b1b;">💸 세금: <b>{f_w(round(tax_amount))}원</b> (세율 {tax_rate*100:.1f}%)</span>
            </div>
            """)

        # 설명
        with st.expander("📋 예금 계산 방법 안내"):
            st.markdown(f"""
**정기예금 단리 계산 공식**

```
세전 이자 = 원금 × 연이율 × (기간 ÷ 12)
         = {f_w(dep_amount)} × {dep_rate}% × ({dep_months} ÷ 12)
         = {f_w(round(pre_tax_interest))}원
```

| 구분 | 금액 |
|------|------|
| 예치 원금 | {f_w(dep_amount)}원 |
| 세전 이자 | {f_w(round(pre_tax_interest))}원 |
| 이자 세금 ({tax_rate*100:.1f}%) | {f_w(round(tax_amount))}원 |
| **세후 이자** | **{f_w(round(post_tax_interest))}원** |
| **만기 수령액** | **{f_w(round(maturity))}원** |

**과세 구분 안내**
- **일반과세 (15.4%)**: 이자소득세 14% + 지방소득세 1.4%
- **세금우대 (9.5%)**: 조합 등 세금우대 저축 (농협, 수협, 신협, 새마을금고 등)
- **비과세 (0%)**: 비과세종합저축 (만 65세 이상, 장애인 등 대상)
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
                    max_value=20.0,
                    value=st.session_state.get("sav_rate", 3.5),
                    step=0.01,
                    format="%.2f",
                    key="sav_rate",
                )

                if "sav_months_sl" not in st.session_state:
                    st.session_state.sav_months_sl = 12
                if "sav_months_num" not in st.session_state:
                    st.session_state.sav_months_num = 12

                st.markdown("납입 기간 (개월)")
                c1, c2 = st.columns([2, 1])
                with c1:
                    st.slider(
                        "납입 기간",
                        min_value=1,
                        max_value=60,
                        key="sav_months_sl",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("sav_months_sl", "sav_months_num"),
                    )
                with c2:
                    st.number_input(
                        "납입 기간 입력",
                        min_value=1,
                        max_value=60,
                        key="sav_months_num",
                        label_visibility="collapsed",
                        on_change=make_sync_callback("sav_months_num", "sav_months_sl"),
                    )

                sav_tax_type = st.radio(
                    "과세 구분",
                    list(TAX_RATES.keys()),
                    horizontal=True,
                    key="sav_tax",
                )

            # 목표 금액 역산
            card_header("🎯 목표 금액 역산")
            with st.container(border=True):
                use_goal = st.checkbox("목표 금액 역산 사용", key="sav_use_goal")
                if use_goal:
                    sav_goal = comma_int_input(
                        "목표 금액 (원)",
                        st.session_state.get("sav_goal_amount", 5_000_000),
                        "sav_goal_amount",
                    )
    else:
        sav_amount = st.session_state.get("sav_amount", 300_000)
        sav_rate = st.session_state.get("sav_rate", 3.5)
        sav_tax_type = st.session_state.get("sav_tax", "일반과세")
        use_goal = st.session_state.get("sav_use_goal", False)

    sav_months = st.session_state.get("sav_months_sl", 12)
    tax_rate = TAX_RATES.get(sav_tax_type if not st.session_state.presentation_mode else st.session_state.get("sav_tax", "일반과세"), 0.154)

    # ── 계산 ──
    monthly_rate = sav_rate / 100 / 12
    n = sav_months
    pre_tax_interest = sav_amount * monthly_rate * (n * (n + 1)) / 2
    tax_amount = pre_tax_interest * tax_rate
    post_tax_interest = pre_tax_interest - tax_amount
    total_paid = sav_amount * n
    maturity = total_paid + post_tax_interest

    # 목표 금액 역산
    goal_monthly = None
    if use_goal:
        sav_goal = st.session_state.get("sav_goal_amount", 5_000_000)
        if sav_goal > 0 and n > 0:
            denom = n + monthly_rate * (n * (n + 1)) / 2 * (1 - tax_rate)
            if denom > 0:
                goal_monthly = sav_goal / denom

    # ── 결과 ──
    with col_result:
        st.subheader("📊 적금 계산 결과")

        # KPI 카드
        html_block(f"""
        <div style="display:flex; gap:10px; flex-wrap:wrap; margin-bottom:18px;">
            <div style="flex:1; min-width:120px; background:#eff6ff; border-radius:12px; padding:14px; text-align:center; border:1px solid #bfdbfe;">
                <div style="font-size:12px; color:#1d4ed8;">총 납입액</div>
                <div style="font-size:20px; font-weight:700; color:#1e3a5f;">{f_w(round(total_paid))}원</div>
            </div>
            <div style="flex:1; min-width:120px; background:#f0f9ff; border-radius:12px; padding:14px; text-align:center; border:1px solid #bae6fd;">
                <div style="font-size:12px; color:#0369a1;">세전 이자</div>
                <div style="font-size:20px; font-weight:700; color:#0c4a6e;">{f_w(round(pre_tax_interest))}원</div>
            </div>
            <div style="flex:1; min-width:120px; background:#f0fdf4; border-radius:12px; padding:14px; text-align:center; border:1px solid #bbf7d0;">
                <div style="font-size:12px; color:#15803d;">세후 이자</div>
                <div style="font-size:20px; font-weight:700; color:#14532d;">{f_w(round(post_tax_interest))}원</div>
            </div>
            <div style="flex:1; min-width:120px; background:#fefce8; border-radius:12px; padding:14px; text-align:center; border:1px solid #fde68a;">
                <div style="font-size:12px; color:#a16207;">만기 수령액</div>
                <div style="font-size:22px; font-weight:800; color:#78350f;">{f_w(round(maturity))}원</div>
            </div>
        </div>
        """)

        # 목표 금액 역산 결과
        if use_goal and goal_monthly is not None:
            sav_goal = st.session_state.get("sav_goal_amount", 5_000_000)
            html_block(f"""
            <div style="background:#faf5ff; border-radius:12px; padding:16px; margin-bottom:16px; border:1px solid #e9d5ff;">
                <div style="font-size:14px; font-weight:600; color:#7c3aed; margin-bottom:8px;">🎯 목표 금액 역산 결과</div>
                <div style="font-size:13px; color:#6b21a8; line-height:1.8;">
                    목표 금액 <b>{f_w(sav_goal)}원</b>을 달성하려면<br>
                    연 {sav_rate}% · {n}개월 · {sav_tax_type} 기준<br>
                    매월 <span style="font-size:20px; font-weight:800; color:#7c3aed;">{f_w(round(goal_monthly))}원</span>을 납입해야 합니다.
                </div>
            </div>
            """)

        # 누적 영역 차트
        months_list = list(range(1, n + 1))
        cum_paid = [sav_amount * m for m in months_list]
        cum_interest = []
        for m in months_list:
            int_m = sav_amount * monthly_rate * (m * (m + 1)) / 2
            cum_interest.append(int_m * (1 - tax_rate))

        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=months_list,
                y=cum_paid,
                name="납입 원금",
                fill="tozeroy",
                mode="lines",
                line=dict(color="#3b82f6", width=2),
                fillcolor="rgba(59,130,246,0.3)",
                hovertemplate="%{x}개월<br>납입원금: %{y:,.0f}원<extra></extra>",
            )
        )
        fig.add_trace(
            go.Scatter(
                x=months_list,
                y=[p + i for p, i in zip(cum_paid, cum_interest)],
                name="납입 + 세후이자",
                fill="tonexty",
                mode="lines",
                line=dict(color="#22c55e", width=2),
                fillcolor="rgba(34,197,94,0.3)",
                hovertemplate="%{x}개월<br>납입+이자: %{y:,.0f}원<extra></extra>",
            )
        )
        fig.update_layout(
            xaxis_title="경과 개월",
            yaxis_title="금액 (원)",
            yaxis=dict(tickformat=","),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            margin=dict(t=30, b=40, l=60, r=20),
            height=340,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

        # 세금 상세
        if tax_rate > 0:
            html_block(f"""
            <div style="background:#fef2f2; border-radius:10px; padding:12px 16px; margin-bottom:12px; border:1px solid #fecaca;">
                <span style="font-size:13px; color:#991b1b;">💸 세금: <b>{f_w(round(tax_amount))}원</b> (세율 {tax_rate*100:.1f}%)</span>
            </div>
            """)

        # 월별 이자 내역표
        with st.expander("📋 월별 이자 내역표"):
            table_rows = ""
            running_paid = 0
            running_interest = 0
            for m in range(1, n + 1):
                running_paid += sav_amount
                # m번째 달에 납입한 금액의 이자 = 남은 개월수에 대한 이자
                month_interest = sav_amount * monthly_rate * (n - m + 1)
                running_interest += month_interest
                post_running = running_interest * (1 - tax_rate)
                balance = running_paid + post_running
                table_rows += f"<tr><td>{m}</td><td>{f_w(sav_amount)}</td><td>{f_w(running_paid)}</td><td>{f_w(round(month_interest))}</td><td>{f_w(round(running_interest))}</td><td>{f_w(round(balance))}</td></tr>"

            html_block(f"""
            <div style="max-height:400px; overflow-y:auto;">
            <table style="width:100%; border-collapse:collapse; font-size:13px;">
                <thead style="position:sticky; top:0; background:#f1f5f9;">
                    <tr style="border-bottom:2px solid #cbd5e1;">
                        <th style="padding:8px 4px; text-align:center;">월</th>
                        <th style="padding:8px 4px; text-align:right;">납입액</th>
                        <th style="padding:8px 4px; text-align:right;">누적납입</th>
                        <th style="padding:8px 4px; text-align:right;">월이자</th>
                        <th style="padding:8px 4px; text-align:right;">누적이자</th>
                        <th style="padding:8px 4px; text-align:right;">잔액</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
            </div>
            """)

        # 설명
        with st.expander("📋 적금 계산 방법 안내"):
            st.markdown(f"""
**정기적금 단리 계산 공식**

적금은 매월 납입하므로, 각 회차 납입금에 대해 남은 기간만큼 이자가 발생합니다.

```
세전 이자 = 월납입액 × (연이율/12) × (개월수 × (개월수+1)) / 2
         = {f_w(sav_amount)} × ({sav_rate}%/12) × ({n} × {n+1}) / 2
         = {f_w(round(pre_tax_interest))}원
```

| 구분 | 금액 |
|------|------|
| 월 납입액 | {f_w(sav_amount)}원 |
| 총 납입액 ({n}개월) | {f_w(total_paid)}원 |
| 세전 이자 | {f_w(round(pre_tax_interest))}원 |
| 이자 세금 ({tax_rate*100:.1f}%) | {f_w(round(tax_amount))}원 |
| **세후 이자** | **{f_w(round(post_tax_interest))}원** |
| **만기 수령액** | **{f_w(round(maturity))}원** |

**월별 이자 적용 원리**
- 1회차 납입금: {n}개월간 이자 발생
- 2회차 납입금: {n-1}개월간 이자 발생
- ...
- {n}회차 납입금: 1개월간 이자 발생

**과세 구분 안내**
- **일반과세 (15.4%)**: 이자소득세 14% + 지방소득세 1.4%
- **세금우대 (9.5%)**: 조합 등 세금우대 저축
- **비과세 (0%)**: 비과세종합저축 대상자
""")
