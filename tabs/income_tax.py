import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core import f_w, f_kr, show_kr_label, comma_int_input, TaxEngine, render_ai_doctor, html_block


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
                html_block("""
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
                """)
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

        _it_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;'>
        <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
            <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>총 소득금액</div>
            <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(total_income)} 원</div>
        </div>
        <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
            <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>과세표준</div>
            <div style='font-size:1.15rem;font-weight:800;color:#3b82f6;word-break:break-all;'>{f_w(taxable_income)} 원</div>
        </div></div>"""
        st.markdown(_it_html, unsafe_allow_html=True)
        if taxable_income <= 0:
            st.caption("적용 세율: 과세표준 없음 (소득 입력 후 확인)")
        else:
            st.caption(f"적용 세율 (최고 구간): {rate_desc}")

        st.divider()

        # 종합 vs 분리 비교
        st.subheader("⚖️ 종합과세 vs 분리과세 비교")

        tc1, tc2 = st.columns(2)
        with tc1:
            html_block(f"""
            <div style='padding:15px; border:2px solid #1e3a8a; border-radius:12px; text-align:center; background:linear-gradient(135deg, #eff6ff, #dbeafe); overflow-wrap: break-word;'>
                <div style='font-size:0.9rem; color:#64748b; margin-bottom:8px;'>종합과세</div>
                <div style='font-size:1.5rem; font-weight:800; color:#1e3a8a; line-height:1.2; word-break: break-all;'>{f_w(total_tax)}원</div>
                <div style='font-size:0.8rem; color:#64748b; margin-top:6px;'>소득세 {f_w(income_tax)} + 지방세 {f_w(local_tax)}</div>
            </div>
            """)

        with tc2:
            if can_separate:
                diff = total_tax - sep_total_tax
                border_color = "#22c55e" if diff > 0 else "#ef4444"
                label = f"{'절세' if diff > 0 else '추가'} {f_w(abs(diff))}원"
                html_block(f"""
                <div style='padding:15px; border:2px solid {border_color}; border-radius:12px; text-align:center; background:linear-gradient(135deg, #f0fdf4, #dcfce7); overflow-wrap: break-word;'>
                    <div style='font-size:0.9rem; color:#64748b; margin-bottom:8px;'>분리과세 (14%)</div>
                    <div style='font-size:1.5rem; font-weight:800; color:#166534; line-height:1.2; word-break: break-all;'>{f_w(sep_total_tax)}원</div>
                    <div style='font-size:0.8rem; color:{border_color}; font-weight:bold; margin-top:6px;'>{label}</div>
                </div>
                """)
            else:
                html_block(f"""
                <div style='padding:15px; border:2px solid #94a3b8; border-radius:12px; text-align:center; background:#f8fafc; overflow-wrap: break-word;'>
                    <div style='font-size:0.9rem; color:#64748b; margin-bottom:8px;'>분리과세</div>
                    <div style='font-size:1.1rem; font-weight:700; color:#94a3b8; line-height:1.2;'>선택 불가</div>
                    <div style='font-size:0.8rem; color:#ef4444; margin-top:6px;'>금융소득 2,000만원 초과 →<br>무조건 종합과세</div>
                </div>
                """)

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
            st.plotly_chart(fig)

        # 세율 구간 시각화
        with st.expander("📐 2025 종합소득세 누진세율표", expanded=False):
            rate_data = pd.DataFrame({
                "과세표준": ["~1,400만", "~5,000만", "~8,800만", "~1.5억", "~3억", "~5억", "~10억", "10억 초과"],
                "세율": ["6%", "15%", "24%", "35%", "38%", "40%", "42%", "45%"],
                "누진공제": ["0", "126만", "576만", "1,544만", "1,994만", "2,594만", "3,594만", "6,594만"]
            })
            st.dataframe(rate_data, hide_index=True)
