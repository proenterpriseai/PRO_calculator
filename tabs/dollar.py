import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from core import f_w, comma_int_input, html_block


def render_dollar_insurance():
    st.title("💵 달러 설계")
    st.markdown("사망 보장 종신보험에 확정 금리와 환율 변동성을 활용한 해약환급금을 통해 전략적인 달러 마련의 기능까지 갖춘 보장성 플랜입니다.")
    
    # Data: Refund Rate Table (메트라이프 백만종 실제 보너스 구조 기반)
    # 납입기간에 따른 환급률 차이 (나이/성별과 무관)
    def get_refund_curve(ptype, period):
        rates = []
        
        # Logic for MetLife (백만인을 위한 달러종신)
        if "메트라이프" in ptype:
            if period == 5:
                # 5년납: 5년 완납 시 1차 보너스(22.5%) → 10년 시점 2차 보너스(11.0%) 합산 → 10년 약 124.9%
                # 1~4년: 납입 중 (해약환급금 낮음)
                # 5년차: 완납 + 1차 보너스(22.5%) 가산으로 점프
                # 6~9년: 복리 적립 + 2차 보너스 점진 반영
                # 10년: 2차 보너스(11.0%) 합산 → 124.9%
                base = [0, 35, 60, 78, 102.5, 106, 110, 114, 119, 124.9]
                last = 124.9
                for _ in range(11):
                    last *= 1.025
                    base.append(last)
                rates = base
            elif period == 7:
                # 7년납: 7년 완납 시 1차 보너스(22.2%) → 10년 시점 2차 보너스(15.9%) 합산 → 10년 약 124.8%
                # 1~6년: 납입 중 (해약환급금 낮음)
                # 7년차: 완납 + 1차 보너스(22.2%) 가산으로 점프
                # 8~9년: 복리 적립 + 2차 보너스 점진 반영
                # 10년: 2차 보너스(15.9%) 합산 → 124.8%
                base = [0, 25, 45, 62, 73, 82, 104.2, 110, 117, 124.8]
                last = 124.8
                for _ in range(11):
                    last *= 1.025
                    base.append(last)
                rates = base
            elif period == 10:
                # 10년납: 10년 완납과 동시에 대규모 유지보너스(약 39.7%) 한 번에 가산 → 10년 약 124.0%
                # 1~9년: 납입 중 (보너스 없이 적립만)
                # 10년차: 완납 + 유지보너스(39.7%) 대규모 점프 → 124.0%
                base = [0, 18, 34, 48, 58, 66, 72, 77, 84.3, 124.0]
                last = 124.0
                for _ in range(11):
                    last *= 1.025
                    base.append(last)
                rates = base
            else:  # 20년납
                # 20년납: 10년 시점은 아직 납입 중, 유지보너스가 20년 시점에 발생 → 10년 약 50~60%
                # 1~10년: 납입 중 (보너스 없음, 환급률 매우 낮음)
                # 11~19년: 계속 납입 중, 서서히 상승
                # 20년: 완납 + 유지보너스 가산
                base = [0, 8, 15, 22, 28, 34, 39, 44, 49, 55]
                last = 55
                for i in range(11):
                    if i < 9:
                        # 11~19년: 납입 중 점진 상승
                        last += 5
                    else:
                        # 20년차: 완납 + 유지보너스로 대폭 점프
                        last = 125.0 if i == 9 else last * 1.025
                    base.append(last)
                rates = base
        else: # Competitors (Generic)
            if period == 5:
                rates = [0, 40, 70, 90, 98, 100, 103, 106, 110, 115.0]
            else:
                rates = [0, 20, 50, 70, 80, 90, 95, 98, 100, 103.0]
            
            last = rates[-1]
            for _ in range(11):
                last *= 1.02
                rates.append(last)
        
        # 납입기간별 확정 환급률 그대로 반환 (나이/성별 보정 없음)
        return [round(r, 1) for r in rates[:20]]

    # 1. Inputs
    if st.session_state.presentation_mode:
        col_input = st.empty()
        col_result = st.container()
    else:
        col_input, col_result = st.columns([1, 1.3], gap="large")
    
    if not st.session_state.presentation_mode:
        with col_input:
            st.subheader("📋 달러 설계 입력")
            
            # Product & Client
            with st.container():
                st.markdown("##### 1. 기본 정보")
                
                prod_type = st.selectbox("상품 선택", ["메트라이프 (백만인을 위한 달러종신)", "타사 달러보험 (일반형)"], key="di_prod")
                
                c_pay1, c_pay2 = st.columns(2)
                pay_period = c_pay1.selectbox("납입 기간", [5, 7, 10, 20], index=0, key="di_period") # Default 5
                
                premium_usd = c_pay2.number_input("월 납입 보험료 ($)", value=0, step=100, format="%d", key="di_prem")
                
                # Custom Additional Payment Logic
                is_add_pay = st.toggle("추가납입 활용 (유니버셜 기능)", value=False, key="di_add_toggle")
                if is_add_pay:
                    add_premium_usd = st.number_input("월 추가납입 보험료 ($)", value=premium_usd, step=100, format="%d", help="기본 보험료의 100% 이내(최대 200%) 권장. 추가납입 시 사업비가 적어 환급률이 대폭 상승합니다.", key="di_add_prem")
                else:
                    add_premium_usd = 0
                
                total_premium_monthly = premium_usd + add_premium_usd
                
                 # Exchange Rate Specs
                st.markdown("##### 2. 환율 시나리오 (원/달러)")
                
                # Real-time Fetch Logic (Robust Requests)
                r_c1, r_c2 = st.columns([2.5, 1])
                with r_c1:
                    # Use session state for rate to update it via button
                    if 'curr_rate_val' not in st.session_state:
                        st.session_state.curr_rate_val = 1430.0 # Default conservative
                    
                    current_rate = st.number_input("현재 환율 (가입 시점)", min_value=500.0, max_value=3000.0, value=st.session_state.curr_rate_val, step=1.0, format="%.1f", key="input_curr_rate")
                
                with r_c2:
                    st.write("") # Spacer
                    st.write("")
                    
                    # Callback Function for Button On_Click (Prevents Widget Key Conflict)
                    def update_exchange_rate():
                        try:
                            import requests
                            import time
                            
                            fetched_val = None
                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
                                
                            # 1. Try Naver Mobile API (JSON) - Standard & Very Stable
                            try:
                                url = "https://m.stock.naver.com/front-api/marketIndex/productDetail?category=exchange&reutersCode=FX_USDKRW"
                                r = requests.get(url, headers=headers, timeout=5)
                                r.raise_for_status()
                                data = r.json()
                                if 'result' in data and 'closePrice' in data['result']:
                                    fetched_val = float(data['result']['closePrice'].replace(',', ''))
                            except Exception:
                                pass # Fail silently, try next
                                
                            # 2. Try Yahoo Finance (HTML Scraping) - Fallback
                            if fetched_val is None:
                                try:
                                    url = "https://finance.yahoo.com/quote/KRW=X"
                                    r = requests.get(url, headers=headers, timeout=5)
                                    if "PRE_CHECK" not in r.text:
                                        import re
                                        match = re.search(r'regularMarketPrice.*?fmt":"([\d,]+)', r.text)
                                        if match:
                                            fetched_val = float(match.group(1).replace(',', ''))
                                except Exception:
                                    pass
    
                            if fetched_val:
                                # Update Session State Keys for Widgets
                                # IMPORTANT: Modifying keys directly in callback is allowed
                                st.session_state.curr_rate_val = fetched_val
                                st.session_state['input_curr_rate'] = fetched_val # Force widget update
                                
                                # Auto-Sync Scenarios
                                st.session_state.rate_mid_val = fetched_val
                                st.session_state['rate_mid_val'] = fetched_val
                                
                                low_val = round(fetched_val * 0.9, -1)
                                st.session_state.rate_low_val = low_val
                                st.session_state['rate_low_val'] = low_val
                                
                                high_val = round(fetched_val * 1.1, -1)
                                st.session_state.rate_high_val = high_val
                                st.session_state['rate_high_val'] = high_val
                                
                                # Auto-calc average rate based on fetched rate
                                current_pay_period = st.session_state.get('di_period', 5)
                                weight_curr = max(0, (20 - current_pay_period) / 20)
                                est_avg = (fetched_val * weight_curr) + (1250.0 * (1 - weight_curr))
                                st.session_state.avg_rate_val = round(est_avg, 1)
                                
                                st.session_state['exchange_rate_fetched_at'] = time.strftime('%H:%M:%S')
                                st.toast(f"✅ 환율 정보 갱신 완료: {fetched_val:,.2f}원", icon="💱")
                            else:
                                st.toast("⚠️ 환율 정보를 가져오는데 실패했습니다. 직접 입력해 주세요.", icon="🚫")
                        except Exception as e:
                            st.toast(f"❌ 시스템 오류 발생: {str(e)}", icon="🚨")
    
                    st.button("🔄 실시간 수신", help="네이버/야후 금융 등 다중 소스를 통해 환율을 조회합니다.", on_click=update_exchange_rate)
                    if 'exchange_rate_fetched_at' in st.session_state:
                        st.caption(f"마지막 수신: {st.session_state['exchange_rate_fetched_at']}")
                    else:
                        st.caption("환율 미수신 — 수동 입력값 사용 중")
    
                # Average Rate Logic
                long_term_mean = 1250.0
                
                # Auto Calc Button Removed (Now synced with Real-time Fetch)
                
                if 'avg_rate_val' not in st.session_state:
                    st.session_state.avg_rate_val = 1300.0
    
                avg_pay_rate = st.number_input(
                    "🤖 AI 예측 납입 기간 평균 환율", 
                    value=st.session_state.avg_rate_val, 
                    step=1.0, format="%.1f", 
                    help=f"매월 적립식 납입 시 '코스트 에버리지' 효과가 발생합니다. 실시간 수신 시 AI가 (장기 평균 {long_term_mean}원과 현재 환율을 납입 기간에 비례해 가중 평균하여) 현실적인 평단가를 자동 산출합니다."
                )
                
                # Initialize Scenario Session States if not valid
                if 'rate_low_val' not in st.session_state: st.session_state.rate_low_val = 1100.0
                if 'rate_mid_val' not in st.session_state: st.session_state.rate_mid_val = 1350.0
                if 'rate_high_val' not in st.session_state: st.session_state.rate_high_val = 1550.0
    
                st.caption("인출(해지) 시점 예상 환율 범위")
                c_r1, c_r2, c_r3 = st.columns(3)
                rate_low = c_r1.number_input("하락(비관)", min_value=500.0, max_value=3000.0, value=st.session_state.rate_low_val, step=10.0, key="rate_low_val")
                rate_mid = c_r2.number_input("보합(중립)", min_value=500.0, max_value=3000.0, value=st.session_state.rate_mid_val, step=10.0, key="rate_mid_val")
                rate_high = c_r3.number_input("상승(낙관)", min_value=500.0, max_value=3000.0, value=st.session_state.rate_high_val, step=10.0, key="rate_high_val")
                
                commission_rate = 0.0
    else:
        # Presentation Mode: Load from State
        prod_type = st.session_state.di_prod if 'di_prod' in st.session_state else "메트라이프 (백만인을 위한 달러종신)"
        
        pay_period = st.session_state.di_period if 'di_period' in st.session_state else 5
        premium_usd = st.session_state.di_prem if 'di_prem' in st.session_state else 1000
        is_add_pay = st.session_state.di_add_toggle if 'di_add_toggle' in st.session_state else True
        if is_add_pay:
            add_premium_usd = st.session_state.di_add_prem if 'di_add_prem' in st.session_state else premium_usd
        else:
            add_premium_usd = 0
            
        total_premium_monthly = premium_usd + add_premium_usd
        
        # Rate Variables
        current_rate = st.session_state.get('input_curr_rate', 1430.0)
        avg_pay_rate = st.session_state.avg_rate_val if 'avg_rate_val' in st.session_state else 1300.0
        rate_low = st.session_state.rate_low_val if 'rate_low_val' in st.session_state else 1100.0
        rate_mid = st.session_state.rate_mid_val if 'rate_mid_val' in st.session_state else 1350.0
        rate_high = st.session_state.rate_high_val if 'rate_high_val' in st.session_state else 1550.0
        commission_rate = 0.004

    # Logic Calculation
    # 1. Curve (납입기간별 환급률)
    csv_rates = get_refund_curve(prod_type, pay_period)
    
    # 2. Payments
    months_paid = pay_period * 12
    total_usd_paid_principal = total_premium_monthly * months_paid
    
    # KRW Paid = USD * Average Rate * Fee
    total_krw_paid = total_usd_paid_principal * avg_pay_rate * (1 + commission_rate)
    
    # 3. 10th Year Status
    idx_10 = 9
    rate_10_pet = csv_rates[idx_10] # %
    
    # Value in USD @ 10y
    # Standard CSV logic relies on "accumulated premium" base for rate application generally,
    # or specific Cash Value table. Here we use % of Total Premium Paid assumption for simplicity 
    # as defined in '124.9% of paid premiums'.
    
    # Correction: If pay_period is 5, at 10y we have fully paid 5y ago.
    # Base: Total Premium Paid
    usd_val_10 = total_usd_paid_principal * (rate_10_pet / 100)
    
    # KRW Returns
    krw_ret_low = usd_val_10 * rate_low
    krw_ret_mid = usd_val_10 * rate_mid
    krw_ret_high = usd_val_10 * rate_high
    
    # BEP Calculation
    # BEP Rate = Total KRW Paid / USD Value
    bep_rate = total_krw_paid / usd_val_10 if usd_val_10 > 0 else 0
    
    # Tax Equivalent Calc based on Mid Scenario
    try:
        total_profit = krw_ret_mid - total_krw_paid
        
        # 평가 기준 시점 = 10년 고정 (환급률 자체가 10년 시점 확정값이므로)
        # CAGR = (10년 환급금 / 총납입금)^(1/10) - 1
        avg_years_invested = 10.0

        # 실질 연평균 복리 수익률 (CAGR)
        cagr = (krw_ret_mid / total_krw_paid) ** (1 / avg_years_invested) - 1
        
        # 비과세 역산 (은행 예적금 명목 금리로 환산)
        tax_equiv_yield_10y = (cagr / (1 - 0.154)) * 100
    except:
        tax_equiv_yield_10y = 0

    with col_result:
        st.subheader("📊 10년 시점 분석")
        
        # Improved Layout for Metrics using Custom HTML
        # Added min-width and flex-basis to ensure content fits
        # Improved Layout for Metrics using Custom HTML
        # Added min-width and flex-basis to ensure content fits
        html_block(f"""
        <div style="display: flex; gap: 10px; margin-bottom: 20px; flex-wrap: wrap;">
            <div style="flex: 1; min-width: 140px; padding: 15px; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">총 납입 원금<br>(KRW)</div>
                <div style="color: #1e3a8a; font-size: 1.1rem; font-weight: 800;">{f_w(total_krw_paid/10000)}만원</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 8px;">평단 @{avg_pay_rate}원</div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; line-height: 1.4;">
                    월 ${f_w(total_premium_monthly)} × {months_paid}회<br>× 평균 환율 {avg_pay_rate}원
                </div>
            </div>
            <div style="flex: 1; min-width: 140px; padding: 15px; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">10년 시점 환급률<br>($)</div>
                <div style="color: #1e3a8a; font-size: 1.1rem; font-weight: 800;">{rate_10_pet:.1f}%</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 8px;">USD {f_w(usd_val_10)}</div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; line-height: 1.4;">
                    총 납입 달러 원금 대비<br>10년 시점 확정 환급금 비율
                </div>
            </div>
            <div style="flex: 1; min-width: 140px; padding: 15px; background: white; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e2e8f0; text-align: center;">
                <div style="color: #64748b; font-size: 0.85rem; margin-bottom: 5px;">세전 환산 수익률</div>
                <div style="color: #22c55e; font-size: 1.1rem; font-weight: 800;">{tax_equiv_yield_10y:.2f}%</div>
                <div style="color: #94a3b8; font-size: 0.75rem; margin-bottom: 8px;">비과세 혜택 적용</div>
                <div style="margin-top:8px; padding-top:8px; border-top:1px dashed #cbd5e1; font-size:0.75rem; color:#64748b; line-height: 1.4;">
                    이자소득세(15.4%) 면제 효과를<br>반영한 은행 예금 환산 금리
                </div>
            </div>
        </div>
        """)
        
        # --- [추가 기획 1] 비과세 폭발력 시각화 배너 (은행 비교) ---
        bank_rate = st.number_input("비교 기준 은행 적금 금리(%)", min_value=0.1, max_value=15.0, value=st.session_state.get('di_bank_rate', 3.5), step=0.1, key="di_bank_rate", help="비교할 시중은행 정기적금 금리를 입력하세요.")
        display_yield = max(0, tax_equiv_yield_10y)
        yield_diff = display_yield - bank_rate
        
        # 차트 그리기용 막대 비율 (Max 10~15% 수준으로 스케일링)
        bar_max = max(10.0, display_yield + 2.0)
        bank_width = min(100, (bank_rate / bar_max) * 100)
        ins_width = min(100, (display_yield / bar_max) * 100)
        
        # +차이 라벨 처리
        diff_label = f"+{yield_diff:.2f}% 유리!" if yield_diff > 0 else f"{yield_diff:.2f}%"
        
        html_block(f"""
<div style="background: linear-gradient(135deg, #1e3a8a, #27398c); padding: 25px 30px; border-radius: 16px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); margin-top: 15px; margin-bottom: 25px; color: white;">
    <div style="text-align: center; margin-bottom: 22px;">
        <p style="color: white; font-size: 0.95rem; margin-top: 8px; margin-bottom: 0;">10년 뒤 동일한 달러(현금)를 만들기 위해, <b>이자소득세 15.4%를 떼는 시중은행 적금에 가입한다면 필요한 연 이율(실질 세전 금리)</b>입니다.</p>
    </div>
    <div style="margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 700; align-items: flex-end;">
            <span style="color: #cbd5e1; font-size: 1.05rem;">일반 시중은행 적금</span>
            <span style="color: #cbd5e1; font-size: 1.1rem; white-space: nowrap; margin-left: 10px;">연 {bank_rate:.2f}%</span>
        </div>
        <div style="width: 100%; background-color: rgba(255,255,255,0.1); border-radius: 20px; height: 32px; overflow: hidden; position: relative;">
            <div style="width: {bank_width}%; background: #94a3b8; height: 100%; border-radius: 20px;"></div>
        </div>
    </div>
    <div>
        <div style="display: flex; justify-content: space-between; margin-bottom: 8px; font-weight: 800; align-items: flex-end;">
            <span style="color: white; font-size: 1.25rem;">✨ 메트라이프 달러 종신 금리</span>
            <span style="color: white; font-size: 1.25rem; white-space: nowrap; margin-left: 10px;">연 {display_yield:.2f}%</span>
        </div>
        <div style="width: 100%; background-color: rgba(255,255,255,0.15); border-radius: 20px; height: 42px; overflow: hidden; position: relative; box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);">
            <div style="width: {ins_width}%; background: linear-gradient(90deg, #3b82f6, #1d4ed8); height: 100%; border-radius: 20px; box-shadow: 0 0 15px rgba(39,57,140,0.3); display: flex; align-items: center; justify-content: flex-end; padding-right: 15px; color: white; font-weight: 800; font-size: 1rem; text-shadow: 1px 1px 2px rgba(0,0,0,0.2);">
                {diff_label}
            </div>
        </div>
    </div>
</div>
""")
        
        st.divider()
        st.markdown("<br>", unsafe_allow_html=True) # Add spacing as requested
        st.subheader("💱 환율 시나리오별 예상 환급금 (10년 시점)")
        
        p_low = krw_ret_low - total_krw_paid
        p_mid = krw_ret_mid - total_krw_paid
        p_high = krw_ret_high - total_krw_paid
        
        # HTML 렌더링 (문자열 연결 연산자 사용으로 따옴표 충돌 원천 방지)
        
        # 1. 데이터 준비
        rate_low_str = f"{int(rate_low):,}"
        val_low_str = f_w(krw_ret_low/10000)
        profit_low_num = (p_low/total_krw_paid*100) if total_krw_paid > 0 else 0
        profit_low_str = f"{profit_low_num:+.1f}% ({f_w(p_low/10000)}만)"
        color_low = "#ef4444" if p_low < 0 else "#16a34a"

        rate_mid_str = f"{int(rate_mid):,}"
        val_mid_str = f_w(krw_ret_mid/10000)
        profit_mid_num = (p_mid/total_krw_paid*100) if total_krw_paid > 0 else 0
        profit_mid_str = f"{profit_mid_num:+.1f}% ({f_w(p_mid/10000)}만)"
        color_mid = "#ef4444" if p_mid < 0 else "#16a34a"

        rate_high_str = f"{int(rate_high):,}"
        val_high_str = f_w(krw_ret_high/10000)
        profit_high_num = (p_high/total_krw_paid*100) if total_krw_paid > 0 else 0
        profit_high_str = f"{profit_high_num:+.1f}% ({f_w(p_high/10000)}만)"
        color_high = "#ef4444" if p_high < 0 else "#be123c"

        # 2. HTML 조립
        html = "<div style='display:flex; gap:12px; margin-bottom:24px; flex-wrap: wrap;'>"
        
        # 하락(비관) 카드
        html += "<div style='flex:1; min-width: 150px; padding:16px; border-radius:16px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); background: linear-gradient(to bottom right, #f1f5f9, #e2e8f0); border: 1px solid #cbd5e1;'>"
        html += "<div style='font-size:2rem; margin-bottom:8px;'>📉</div>"
        html += "<div style='font-size:0.95rem; font-weight:bold; color:#475569; margin-bottom:2px;'>하락(비관)</div>"
        html += "<div style='font-size:0.8rem; color:#64748b; margin-bottom:12px; font-family:Consolas, monospace;'>@" + rate_low_str + "원/$</div>"
        html += "<div style='font-size:1.25rem; font-weight:800; color:#334155; margin-bottom:6px; letter-spacing:-0.5px;'>" + val_low_str + "만원</div>"
        html += "<div style='font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:6px; display:inline-block; border:1px solid rgba(0,0,0,0.05); color:" + color_low + ";'>" + profit_low_str + "</div>"
        html += "</div>"

        # 보합(중립) 카드
        html += "<div style='flex:1; min-width: 150px; padding:16px; border-radius:16px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); background: linear-gradient(to bottom right, #eff6ff, #dbeafe); border: 1px solid #60a5fa;'>"
        html += "<div style='font-size:2rem; margin-bottom:8px;'>☁️</div>"
        html += "<div style='font-size:0.95rem; font-weight:bold; color:#1d4ed8; margin-bottom:2px;'>보합(중립)</div>"
        html += "<div style='font-size:0.8rem; color:#3b82f6; margin-bottom:12px; font-family:Consolas, monospace;'>@" + rate_mid_str + "원/$</div>"
        html += "<div style='font-size:1.25rem; font-weight:800; color:#1e40af; margin-bottom:6px; letter-spacing:-0.5px;'>" + val_mid_str + "만원</div>"
        html += "<div style='font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:6px; display:inline-block; border:1px solid rgba(37, 99, 235, 0.1); color:" + color_mid + ";'>" + profit_mid_str + "</div>"
        html += "</div>"

        # 상승(낙관) 카드
        html += "<div style='flex:1; min-width: 150px; padding:16px; border-radius:16px; text-align:center; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05); background: linear-gradient(to bottom right, #fff1f2, #fecdd3); border: 1px solid #f43f5e;'>"
        html += "<div style='font-size:2rem; margin-bottom:8px;'>☀️</div>"
        html += "<div style='font-size:0.95rem; font-weight:bold; color:#be123c; margin-bottom:2px;'>상승(낙관)</div>"
        html += "<div style='font-size:0.8rem; color:#e11d48; margin-bottom:12px; font-family:Consolas, monospace;'>@" + rate_high_str + "원/$</div>"
        html += "<div style='font-size:1.25rem; font-weight:800; color:#9f1239; margin-bottom:6px; letter-spacing:-0.5px;'>" + val_high_str + "만원</div>"
        html += "<div style='font-size:0.85rem; font-weight:700; background:rgba(255,255,255,0.8); padding:4px 8px; border-radius:6px; display:inline-block; border:1px solid rgba(225, 29, 72, 0.1); color:" + color_high + ";'>" + profit_high_str + "</div>"
        html += "</div>"

        html += "</div>"
        
        st.markdown(html, unsafe_allow_html=True)
        
        # Detailed BEP Explanation
        with st.expander("💡 손익분기 환율(BEP) 산출 근거 보기"):
            html_block(f"""
            <div class='logic-annotation'>
                <b>🧮 산출 공식:</b> 총 납입 원화 ÷ 10년 시점 달러 해지환급금<br>
                <br>
                1. <b>총 납입 원화:</b> {f_w(total_krw_paid)}원 (월 ${f_w(total_premium_monthly)} × {months_paid}개월 × 평단 {avg_pay_rate}원)<br>
                2. <b>달러 환급금:</b> ${f_w(usd_val_10)} (원금 ${f_w(total_usd_paid_principal)} × 환급률 {rate_10_pet:.1f}%)<br>
                3. <b>손익분기 환율:</b> <span style='color:#e11d48; font-weight:bold;'>{bep_rate:.1f}원</span><br>
                4. <b>참고:</b> 메트라이프 백만종 상품은 나이/성별과 무관하게 납입기간에 따른 확정 환급률이 적용됩니다.<br>
                <br>
                👉 환율이 {bep_rate:.1f}원 이상이면 원화 기준으로도 원금 이상입니다.
            </div>
            """)

    st.divider()
    
    # Chart Preparation
    years_x = list(range(1, 21)) # 1 to 20
    # ensure years_x matches rates length
    rates_chart = get_refund_curve(prod_type, pay_period)
    rates_comp = get_refund_curve("타사", pay_period)
    
    c_chart1, c_chart2 = st.columns(2, gap="large")
    
    with c_chart1:
        st.subheader("📈 해약환급률 추이 비교")
        fig_csv = go.Figure()
        fig_csv.add_trace(go.Scatter(x=years_x, y=rates_chart, mode='lines+markers', name='선택 상품',
                                     line=dict(color='#1e3a8a', width=3)))
        fig_csv.add_trace(go.Scatter(x=years_x, y=rates_comp, mode='lines', name='타사 평균',
                                     line=dict(color='#94a3b8', width=2, dash='dot')))
        
        # Annotation for 10y
        fig_csv.add_annotation(x=10, y=rates_chart[9], text=f"10년 {rates_chart[9]}%", showarrow=True, arrowhead=1, yshift=10)
        
        fig_csv.update_layout(title="경과 기간별 환급률 (%)", template="plotly_white", height=300, hovermode="x unified", plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_csv)
        st.caption("📌 타사 평균은 10년 이후 연 2% 복리 추정값이며, 실제 계약 조건에 따라 상이할 수 있습니다.")
        
    with c_chart2:
        st.subheader("💰 환율 시나리오별 자산 가치")
        st.caption("10년 시점, 환율 변동에 따른 원화 환산 자산 가치 (환차익 시뮬레이션)")
        
        # 10년 시점 총 환급금($) 예측
        usd_cash_value_10y = total_usd_paid_principal * (rate_10_pet / 100)
        
        scenarios = ['하락(비관)', '보합(중립)', '상승(낙관)'] 
        rates = [rate_low, rate_mid, rate_high]
        colors = ['#94a3b8', '#3b82f6', '#ef4444'] 
        
        krw_values = [usd_cash_value_10y * r for r in rates]
        
        fig_sens = go.Figure()
        fig_sens.add_trace(go.Bar(
            x=scenarios, y=krw_values,
            text=[f"{f_w(v)}" for v in krw_values],
            textposition='auto',
            marker_color=colors
        ))
        
        # 기준선 (원화 납입 원금) 추가
        fig_sens.add_hline(y=total_krw_paid, line_dash="dash", line_color="#334155", annotation_text="원화 납입 원금")
        
        # 최대 이익 계산
        max_profit = max(krw_values) - total_krw_paid
        
        fig_sens.update_layout(title=f"최대 환차익 +{f_w(max_profit)}원 예상", template="plotly_white", height=300, plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_sens)

    # 환율 추이 차트
    with st.expander("📈 USD/KRW 환율 흐름 한눈에 보기 (최근 10년)", expanded=False):
        # 시뮬레이션 데이터 (최근 순 정렬: 2026 -> 2016)
        years_hist = [2026, 2025, 2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016]
        # 데이터도 최근 순으로 (2026이 첫번째)
        avg_rates = [int(current_rate), 1390, 1364, 1306, 1292, 1144, 1180, 1166, 1100, 1131, 1161]
        
        rate_max = max(avg_rates)
        rate_min = min(avg_rates)
        rate_avg = int(sum(avg_rates) / len(avg_rates))
        rate_now = int(current_rate)
        max_year = years_hist[avg_rates.index(rate_max)]
        min_year = years_hist[avg_rates.index(rate_min)]
        
        # 핵심 요약 카드
        st.markdown("##### 💡 10년 환율 핵심 요약")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("📉 최저 환율", f"{rate_min:,}원", f"{min_year}년")
        m2.metric("📈 최고 환율", f"{rate_max:,}원", f"{max_year}년")
        m3.metric("📊 10년 평균", f"{rate_avg:,}원", f"{len(avg_rates)}년 평균")
        m4.metric("📍 현재 기준", f"{rate_now:,}원", f"평균 대비 {'+' if rate_now > rate_avg else ''}{rate_now - rate_avg:,}원")
        
        st.divider()
        
        # 흐름 해석 메시지
        if rate_now > rate_avg:
            trend_msg = f"현재 환율({rate_now:,}원)은 10년 평균({rate_avg:,}원)보다 **{rate_now - rate_avg:,}원 높은 수준**입니다. 달러 자산의 원화 환산 가치가 높아 **환차익이 유리**한 시점입니다."
        else:
            trend_msg = f"현재 환율({rate_now:,}원)은 10년 평균({rate_avg:,}원)보다 **{rate_avg - rate_now:,}원 낮은 수준**입니다. 달러 매입 단가를 낮출 수 있는 저점 구간이므로 **적립 확대를 고려**해볼 만합니다."
        
        st.info(f"💡 {trend_msg}")
        
        # 깔끔한 트렌드 차트
        fig_rate = go.Figure()
        
        # 10년 평균 영역
        fig_rate.add_hrect(y0=rate_avg - 50, y1=rate_avg + 50,
                          fillcolor="rgba(59, 130, 246, 0.08)", line_width=0,
                          annotation_text=f"평균 구간 ({rate_avg-50:,}~{rate_avg+50:,})")
        
        # 메인 라인 (Plotly는 X축 기준 정렬하므로 데이터 순서 상관없이 시계열 좌->우로 그려짐. 표와 일치시키기 위해 데이터는 역순 유지)
        fig_rate.add_trace(go.Scatter(
            x=years_hist, y=avg_rates,
            mode='lines+markers+text',
            line=dict(color='#1e3a8a', width=3),
            marker=dict(size=10, color='#3b82f6', line=dict(width=2, color='white')),
            text=[f"{r:,}" for r in avg_rates],
            textposition='top center',
            textfont=dict(size=10, color='#334155'),
            name='연평균 환율'
        ))
        
        # 현재 시점 강조
        fig_rate.add_trace(go.Scatter(
            x=[2026], y=[rate_now],
            mode='markers',
            marker=dict(size=16, color='#ef4444', symbol='star', line=dict(width=2, color='white')),
            name=f'현재 ({rate_now:,}원)',
            showlegend=True
        ))
        
        fig_rate.update_layout(
            title=dict(text="연도별 USD/KRW 연평균 환율 추이", font=dict(size=16, color='#1e293b')),
            xaxis=dict(title="연도", dtick=1, showgrid=True, gridcolor='#f1f5f9'),
            yaxis=dict(title="환율 (원/USD)", showgrid=True, gridcolor='#f1f5f9',
                      range=[min(avg_rates) - 80, max(avg_rates) + 80]),
            template="plotly_white",
            height=380,
            plot_bgcolor='rgba(255,255,255,0)',
            margin=dict(l=20, r=20, t=60, b=20),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_rate)
        
        # 연도별 표 (역순 데이터 -> 전년 대비 계산 주의)
        import pandas as pd
        diff_list = []
        for i in range(len(avg_rates)):
            if i == len(avg_rates) - 1: # 마지막 요소 (2016)
                diff_list.append("-")
            else:
                diff = avg_rates[i] - avg_rates[i+1] # 현재 - 과거
                # HTML Color Tag 적용
                if diff > 0:
                    diff_str = f"<span style='color:#ef4444; font-weight:bold;'>▲ {abs(diff):,}원</span>"
                elif diff < 0:
                    diff_str = f"<span style='color:#3b82f6; font-weight:bold;'>▼ {abs(diff):,}원</span>"
                else:
                    diff_str = "-"
                diff_list.append(diff_str)

        df_rate = pd.DataFrame({
            "연도": years_hist,
            "연평균 환율(원)": [f"{r:,}" for r in avg_rates],
            "전년 대비": diff_list
        })
        
        # HTML Table 렌더링 (style 적용 위해)
        st.markdown(df_rate.to_html(escape=False, index=False, classes="table-custom"), unsafe_allow_html=True)
        # CSS for better table look
        html_block("""
        <style>
        .table-custom { width: 100%; border-collapse: collapse; font-size: 0.9rem; margin-top: 10px; }
        .table-custom th { background-color: #f8fafc; border-bottom: 2px solid #e2e8f0; padding: 8px; text-align: center; color: #64748b; font-weight: 600; }
        .table-custom td { border-bottom: 1px solid #f1f5f9; padding: 8px; text-align: center; color: #334155; }
        .table-custom tr:hover { background-color: #f1f5f9; }
        </style>
        """)
        
        st.caption("※ 연평균 환율은 한국은행 기준환율 참고 시뮬레이션이며, 정확한 시세는 금융 포털을 참조하세요.")

    with st.expander("📝 AI 분석 리포트", expanded=True):
         html_block(f"""
        <div class='expert-card'>
            <div class='expert-title'>🏆 {prod_type} 핵심 경쟁력</div>
            <div class='step-box'>
                <div class='step-title'>1. 확정 금리와 환차익의 Dual Effect</div>
                <div class='step-content'>
                    10년 시점 확정 환급률 <span class='highlight'>{rate_10_pet}%</span>에 달러 강세 시 추가 환차익을 누릴 수 있습니다.
                    현재 구조상 손익분기 환율(BEP)은 <span class='highlight'>{bep_rate:.1f}원</span>으로, 장기적 관점에서 안정성이 뛰어납니다.
                </div>
            </div>
            <div class='step-box'>
                <div class='step-title'>2. 비과세 혜택의 실질 가치</div>
                <div class='step-content'>
                    관련 세법 충족 시 15.4% 이자소득세가 면제되므로, 은행 예금으로 환산 시 연 <span class='highlight'>{tax_equiv_yield_10y:.2f}%</span>의 수익 상품과 동일한 세후 효과를 가집니다.
                </div>
            </div>
        </div>
        """)

