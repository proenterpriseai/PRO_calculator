import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from core import f_w, f_kr, show_kr_label, comma_int_input, TaxEngine, render_ai_doctor, html_block, make_sync_callback


def render_jeonwolse():
    """전월세 전환율 계산기"""
    st.title("🏠 전월세 전환율 계산기")
    st.markdown("전세와 월세를 **전환율 기반**으로 상호 변환하고, 유불리를 분석합니다.")

    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")

    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 전월세 조건 입력")

            mode = st.radio("변환 방향", ["전세 → 월세", "월세 → 전세"], horizontal=True, key="jw_mode")

            if "전세 → 월세" in mode:
                jeonse = comma_int_input("전세 보증금 (원)", 0, "jw_jeonse")
                wolse_deposit = comma_int_input("월세 전환 시 보증금 (원)", 0, "jw_deposit")
            else:
                wolse_deposit = comma_int_input("월세 보증금 (원)", 0, "jw_deposit")
                monthly_wolse = comma_int_input("월세 (원/월)", 0, "jw_wolse")

            if 'jw_rate_sl' not in st.session_state: st.session_state.jw_rate_sl = 5.0
            if 'jw_rate_num' not in st.session_state: st.session_state.jw_rate_num = 5.0
            st.markdown("전월세 전환율 (%)")
            _cr1, _cr2 = st.columns([2, 1])
            _cr1.slider("전환율", 2.0, 12.0, step=0.5, key="jw_rate_sl", label_visibility="collapsed",
                        on_change=make_sync_callback('jw_rate_sl', 'jw_rate_num'),
                        help="전세보증금을 월세로 (또는 그 반대로) 전환할 때 적용되는 이율입니다. (2025년 법정 상한선: 4.75%)")
            _cr2.number_input("전환율 입력", 2.0, 12.0, step=0.5, key="jw_rate_num", label_visibility="collapsed",
                              on_change=make_sync_callback('jw_rate_num', 'jw_rate_sl'))
            conversion_rate = st.session_state.jw_rate_sl
            if conversion_rate > 4.75:
                _has_jw_input = (st.session_state.get('jw_jeonse', 0) > 0 or
                                 st.session_state.get('jw_deposit', 0) > 0 or
                                 st.session_state.get('jw_wolse', 0) > 0)
                if _has_jw_input:
                    st.warning(f"⚠️ 입력한 전환율 **{conversion_rate}%** 는 2025년 법정 상한선 **4.75%** 를 초과합니다. 임대차 계약에 적용 시 법적 분쟁이 발생할 수 있습니다.", icon="⚠️")
    else:
        mode = st.session_state.get('jw_mode', "전세 → 월세")
        jeonse = st.session_state.get('jw_jeonse', 300_000_000)
        wolse_deposit = st.session_state.get('jw_deposit', 50_000_000)
        monthly_wolse = st.session_state.get('jw_wolse', 1_000_000)
        conversion_rate = st.session_state.get('jw_rate_sl', 5.0)

    # 계산
    with col_result:
        st.subheader("📊 전환 결과")

        if "전세 → 월세" in mode:
            diff = max(0, jeonse - wolse_deposit)
            monthly_wolse_calc = int(diff * (conversion_rate / 100) / 12)
            annual_wolse = monthly_wolse_calc * 12

            _jw1_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;'>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>산출 월세</div>
                <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(monthly_wolse_calc)} 원/월</div>
            </div>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>연간 월세 합계</div>
                <div style='font-size:1.15rem;font-weight:800;color:#ef4444;word-break:break-all;'>{f_w(annual_wolse)} 원/년</div>
            </div></div>"""
            st.markdown(_jw1_html, unsafe_allow_html=True)

            html_block(f"""
            <div class='logic-annotation'>
                <b>🧮 산출 근거:</b><br>
                (전세 {f_w(jeonse)}원 - 보증금 {f_w(wolse_deposit)}원) × 전환율 {conversion_rate}% ÷ 12<br>
                = {f_w(diff)}원 × {conversion_rate}% ÷ 12 = <b>{f_w(monthly_wolse_calc)}원/월</b>
            </div>
            """)

            # 비교 차트
            fig = go.Figure(data=[
                go.Bar(name='전세 기회비용', x=['연간 비용'], y=[int(jeonse * conversion_rate / 100)], marker_color='#1e3a8a'),
                go.Bar(name='월세 합계', x=['연간 비용'], y=[annual_wolse], marker_color='#ef4444')
            ])
            fig.update_layout(barmode='group', template='plotly_white', height=300, title="전세 기회비용 vs 월세 비교")
            st.plotly_chart(fig)



        else:
            # 월세 → 전세
            jeonse_calc = wolse_deposit + int(monthly_wolse * 12 / (conversion_rate / 100))

            _jw2_html = f"""<div style='display:flex;flex-wrap:wrap;gap:10px;'>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>환산 전세금</div>
                <div style='font-size:1.15rem;font-weight:800;color:#1e3a8a;word-break:break-all;'>{f_w(jeonse_calc)} 원</div>
            </div>
            <div style='flex:1;min-width:160px;background:white;border-radius:10px;padding:14px 12px;border:1px solid #e2e8f0;box-shadow:0 1px 3px rgba(0,0,0,0.06);'>
                <div style='font-size:0.82rem;font-weight:600;color:#475569;margin-bottom:6px;'>연간 월세 합계</div>
                <div style='font-size:1.15rem;font-weight:800;color:#ef4444;word-break:break-all;'>{f_w(monthly_wolse * 12)} 원/년</div>
            </div></div>"""
            st.markdown(_jw2_html, unsafe_allow_html=True)

            html_block(f"""
            <div class='logic-annotation'>
                <b>🧮 산출 근거:</b><br>
                보증금 {f_w(wolse_deposit)}원 + (월세 {f_w(monthly_wolse)}원 × 12 ÷ 전환율 {conversion_rate}%)<br>
                = {f_w(wolse_deposit)} + {f_w(int(monthly_wolse * 12 / (conversion_rate / 100)))} = <b>{f_w(jeonse_calc)}원</b>
            </div>
            """)



        # 전환율 민감도 분석
        st.divider()
        st.subheader("📈 전환율 민감도 분석")
        rates = [r/10 for r in range(20, 121, 5)]
        if "전세 → 월세" in mode:
            diff = max(0, jeonse - wolse_deposit)
            wolse_values = [int(diff * (r/100) / 12) for r in rates]
            fig2 = go.Figure(data=[go.Scatter(x=rates, y=wolse_values, mode='lines+markers',
                                              line=dict(color='#1e3a8a', width=3))])
            fig2.add_vline(x=conversion_rate, line_dash="dash", line_color="#ef4444",
                          annotation_text=f"현재 {conversion_rate}%")
            fig2.update_layout(title="전환율별 예상 월세", xaxis_title="전환율 (%)", yaxis_title="월세 (원)",
                                  template='plotly_white', height=300)
        else:
            jeonse_values = [wolse_deposit + int(monthly_wolse * 12 / (r/100)) for r in rates]
            fig2 = go.Figure(data=[go.Scatter(x=rates, y=jeonse_values, mode='lines+markers',
                                              line=dict(color='#1e3a8a', width=3))])
            fig2.add_vline(x=conversion_rate, line_dash="dash", line_color="#ef4444",
                          annotation_text=f"현재 {conversion_rate}%")
            fig2.update_layout(title="전환율별 환산 전세금", xaxis_title="전환율 (%)", yaxis_title="전세금 (원)",
                                  template='plotly_white', height=300)
        st.plotly_chart(fig2)

    # 유불리 판정 (Input Column으로 이동)
    with col_input:
        st.write("") # Spacer
        st.markdown("<div style='margin-top:20px;'></div>", unsafe_allow_html=True)
        if "전세 → 월세" in mode:
            opp_cost = int(jeonse * conversion_rate / 100)
            if opp_cost > annual_wolse:
                verdict_icon = "✅"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "월세가 유리합니다"
                verdict_desc = f"전세 기회비용({f_w(opp_cost)}원/년)이 월세({f_w(annual_wolse)}원/년)보다 <b>{f_w(opp_cost - annual_wolse)}원 더 비쌉니다.</b><br>전세 보증금을 투자하면 월세보다 높은 수익을 기대할 수 있습니다."
            elif opp_cost < annual_wolse:
                verdict_icon = "🏠"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "전세가 유리합니다"
                verdict_desc = f"월세({f_w(annual_wolse)}원/년)가 전세 기회비용({f_w(opp_cost)}원/년)보다 <b>{f_w(annual_wolse - opp_cost)}원 더 비쌉니다.</b><br>전세를 유지하는 것이 경제적으로 유리합니다."
            else:
                verdict_icon = "⚖️"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "비용이 동일합니다"
                verdict_desc = "전세 기회비용과 월세 부담이 같습니다. 주거 안정성, 자금 유동성 등을 고려하여 선택하세요."

            html_block(f"""
            <div style='padding:20px; border:1px solid rgba(255,255,255,0.1); border-radius:12px; text-align:center; background:{verdict_bg}; margin-top:10px; color:white;'>
                <div style='font-size:2rem; margin-bottom:8px;'>{verdict_icon}</div>
                <div style='font-size:1.3rem; font-weight:800; color:{verdict_color}; margin-bottom:10px;'>{verdict_title}</div>
                <div style='font-size:0.9rem; color:#cbd5e1; line-height:1.6;'>{verdict_desc}</div>
                <div style='margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.2); font-size:0.8rem; color:#94a3b8;'>
                    ※ 기회비용 = 전세 보증금 × 전환율({conversion_rate}%). 실제 투자수익률에 따라 달라질 수 있습니다.
                </div>
            </div>
            """)

        else:
            annual_wolse_pay = monthly_wolse * 12
            opp_cost_jeonse = int(jeonse_calc * conversion_rate / 100)
            if annual_wolse_pay > opp_cost_jeonse:
                verdict_icon = "🏠"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "전세 전환이 유리합니다"
                verdict_desc = f"현재 월세 부담({f_w(annual_wolse_pay)}원/년)이 전세 기회비용({f_w(opp_cost_jeonse)}원/년)보다 <b>{f_w(annual_wolse_pay - opp_cost_jeonse)}원 더 비쌉니다.</b><br>전세 자금이 있다면 전세로 전환하는 것이 유리합니다."
            elif annual_wolse_pay < opp_cost_jeonse:
                verdict_icon = "✅"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "현재 월세가 유리합니다"
                verdict_desc = f"전세 기회비용({f_w(opp_cost_jeonse)}원/년)이 월세 부담({f_w(annual_wolse_pay)}원/년)보다 <b>{f_w(opp_cost_jeonse - annual_wolse_pay)}원 더 비쌉니다.</b><br>여유 자금을 투자에 활용하는 것이 더 효율적입니다."
            else:
                verdict_icon = "⚖️"
                verdict_color = "white"
                verdict_bg = "linear-gradient(135deg, #1e3a8a, #27398c)"
                verdict_title = "비용이 동일합니다"
                verdict_desc = "월세 부담과 전세 기회비용이 같습니다. 주거 안정성, 자금 유동성 등을 고려하여 선택하세요."

            html_block(f"""
            <div style='padding:20px; border:1px solid rgba(255,255,255,0.1); border-radius:12px; text-align:center; background:{verdict_bg}; margin-top:10px; color:white;'>
                <div style='font-size:2rem; margin-bottom:8px;'>{verdict_icon}</div>
                <div style='font-size:1.3rem; font-weight:800; color:{verdict_color}; margin-bottom:10px;'>{verdict_title}</div>
                <div style='font-size:0.9rem; color:#cbd5e1; line-height:1.6;'>{verdict_desc}</div>
                <div style='margin-top:12px; padding-top:12px; border-top:1px solid rgba(255,255,255,0.2); font-size:0.8rem; color:#94a3b8;'>
                    ※ 기회비용 = 환산 전세금 × 전환율({conversion_rate}%). 실제 투자수익률에 따라 달라질 수 있습니다.
                </div>
            </div>
            """)
