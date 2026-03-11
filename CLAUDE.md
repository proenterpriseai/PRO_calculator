# CLAUDE.md — 계산기 앱 핵심 규칙 & 수정 이력

> **이 파일은 계산 로직의 정확성을 보장하기 위한 규칙 문서입니다.**
> **절대로 아래 규칙을 위반하거나 되돌리지 마세요.**

## 프로젝트 개요
- Streamlit 기반 한국 재무 계산기 앱 (8개 탭)
- 100명 대상 프레젠테이션 + 700명 사용자 배포
- 핵심 원칙: **기존 기능/UI/CSS가 삭제·오류·누락되지 않도록 할 것**
- 안전 백업: `git reset --hard fc60ef1` (1단계 버그수정 전 백업)

## 프로젝트 구조
```
app.py          — 메인 앱 (증여세 Tab1, 상속세 Tab2 포함)
core.py         — 세율 테이블, TaxEngine, 공통 유틸리티
tabs/
  income_tax.py — 종합소득세
  real_estate.py— 부동산(취득세·양도세·종부세)
  loan.py       — 대출 상환 설계
  jeonwolse.py  — 전월세 전환
  dollar.py     — 달러 적립
  target_fund.py— 목표자금
  retirement.py — 은퇴설계
```

---

## 절대 규칙 (DO NOT CHANGE)

### 1. 세율 테이블 (core.py)

#### 양도소득세 8단계 (get_capital_gains_tax_rate)
| 과세표준 | 세율 | 누진공제 |
|---------|------|---------|
| ~1,400만 | 6% | 0 |
| ~5,000만 | 15% | 126만 |
| ~8,800만 | 24% | 576만 |
| ~1.5억 | 35% | 1,544만 |
| ~3억 | 38% | 1,994만 |
| ~5억 | 40% | 2,594만 |
| ~10억 | 42% | 3,594만 |
| 10억 초과 | 45% | 6,594만 |

#### 상속·증여세 5단계 (get_tax_rate_5steps)
| 과세표준 | 세율 | 누진공제 |
|---------|------|---------|
| ~1억 | 10% | 0 |
| ~5억 | 20% | 1,000만 |
| ~10억 | 30% | 6,000만 |
| ~30억 | 40% | 1.6억 |
| 30억 초과 | 50% | 4.6억 |

#### 종부세 — 일반 (get_jongbu_tax, is_multi_home=False)
| 과세표준 | 세율 | 누진공제 |
|---------|------|---------|
| ~3억 | 0.5% | 0 |
| ~6억 | 0.7% | 60만 |
| ~12억 | 1.0% | 240만 |
| ~25억 | 1.3% | 600만 |
| ~50억 | 1.5% | 1,100만 |
| ~94억 | 2.0% | 3,600만 |
| 94억 초과 | 2.7% | 10,180만 |

#### 종부세 — 다주택 (is_multi_home=True) ✅ 수정완료
| 과세표준 | 세율 | 누진공제 |
|---------|------|---------|
| ~3억 | 0.5% | 0 |
| ~6억 | 0.7% | 60만 |
| ~12억 | 1.0% | 240만 |
| ~25억 | 1.4% | **720만** |
| ~50억 | 1.5% | **970만** |
| ~94억 | 2.0% | **3,470만** |
| 94억 초과 | 2.7% | **10,050만** |

> **주의**: 다주택 25억 이상 4개 구간의 누진공제액은 경계값 연속성 검증 완료.
> 이전 오류: 10,800/13,300/38,300/104,100 → 수정: 7,200/9,700/34,700/100,500

### 2. 대출 상환 (tabs/loan.py)

- **3가지 방식**: 원리금균등, 원금균등, **만기일시상환**
- 만기일시상환 = 매월 이자만 납부, 만기에 원금 전액 상환
  ```python
  bullet_monthly = loan_amount * monthly_rate
  total_interest_bullet = bullet_monthly * total_months
  ```
- **거치식(grace period) 방식은 제거됨** — 절대 복원하지 말 것

### 3. 전월세 전환 (tabs/jeonwolse.py)

- **법정상한 전환율**: 기준금리(2.50%) + 2.0% = **4.50%**
- **투자 기대수익률**: 별도 입력 (기본 3.5%) — 전환율과 분리
- **전세→월세 판정**: `freed_capital × invest_rate` vs `annual_wolse`
- **월세→전세 판정**: `annual_wolse_pay` vs `extra_capital × invest_rate`
- **절대 금지**: 전환율과 투자수익률을 동일 변수로 사용 (항등식 버그 발생)

### 4. 상속세 (tabs/inheritance.py + app.py)

- **장례비용**: `max(500만, min(입력값, 1,500만))` — 최소 500만 보장
- **배우자공제**: `max(5억, min(입력값, 법정상속분, 30억))`
  - 법정상속분 = `estate_val × 1.5 / (1.5 + 자녀수)`
- **기초+인적공제**: 일괄공제(5억)보다 작으면 자동으로 5억 적용
  ```python
  if final_other_ded < 500_000_000:
      final_other_ded = 500_000_000
  ```

### 5. 부동산 양도세 (tabs/real_estate.py)

- **분양권(2021년 이후 취득)** 보유기간별 세율:
  - 1년 미만: 70%
  - 1~2년 미만: 60%
  - **2년 이상: 일반 누진세율(6~45%)** ← 60% 적용 금지

- **지방교육세 표준세율** (취득세 중과 시 — **주택에만 적용**):
  - 6억 이하: 표준세율 1%
  - 6~9억: 슬라이딩 `(price×2/3억 - 3)/100`
  - 9억 초과: 표준세율 3%
  - 교육세 = 표준세율 기준 취득세 × 10%
  - **비주거(기타 토지/상가/법인)**: `tax × 0.10` 단순 적용 (가격대별 표준세율 미적용)

### 6. 달러 적립 (tabs/dollar.py)

- **수수료율**: presentation_mode와 일반 모드 모두 `0.0` (일치 필수)

### 7. 목표자금 (tabs/target_fund.py)

- **전략리포트 적금 금리**: 사용자 입력값 `top_sav_rate` 사용 (3.5% 하드코딩 금지)
- **몬테카를로 시뮬레이션 200회 차트**: 삭제됨 — 복원 금지

---

## Streamlit 위젯 규칙

- `st.slider`, `st.number_input` 등의 `value=` 파라미터는 **첫 렌더링 시만 적용**
- 동적 값을 `value=`에 넣으면 위젯 재생성 시 무시됨 → **고정 기본값 사용**
- 슬라이더↔숫자입력 양방향 연동: `make_sync_callback()` 사용
- presentation_mode에서는 `st.session_state.get()` 으로 값 읽기

## 빌드 & 검증
```bash
python -m py_compile app.py
python -m py_compile core.py
python -m py_compile tabs/loan.py
python -m py_compile tabs/jeonwolse.py
python -m py_compile tabs/inheritance.py
python -m py_compile tabs/real_estate.py
python -m py_compile tabs/dollar.py
python -m py_compile tabs/target_fund.py
python -m py_compile tabs/retirement.py
python -m py_compile tabs/income_tax.py
```

---

## 수정 이력 (날짜순)

### 2025-03 수정 완료 항목
1. ✅ 종부세 다주택 누진공제액 4개 구간 수정 (core.py)
2. ✅ 대출 거치식 → 만기일시상환 변경 (loan.py)
3. ✅ 전월세 판정 항등식 버그 수정 + 투자수익률 분리 (jeonwolse.py)
4. ✅ 전월세 법정상한 4.75% → 4.50% (jeonwolse.py)
5. ✅ 장례비용 최소 500만원 보장 (inheritance.py)
6. ✅ 배우자공제 법정상속분 한도 적용 (inheritance.py)
7. ✅ 기초+인적공제 5억 최소 보장 (inheritance.py)
8. ✅ 분양권 2년↑ 일반세율 적용 (real_estate.py)
9. ✅ 지방교육세 표준세율 가격대별 분리 (real_estate.py)
10. ✅ 달러 수수료율 presentation_mode 일치 (dollar.py)
11. ✅ 목표자금 적금금리 하드코딩 제거 (target_fund.py)
12. ✅ 몬테카를로 시뮬레이션 200회 차트 삭제 (target_fund.py)
13. ✅ 양도소득세 8단계 세율 검증 완료 (core.py)
14. ✅ 종합소득세 비교산출세액 구현 (income_tax.py)
15. ✅ 은퇴설계 동적 기본값 고정 (retirement.py)

### 2026-03 종합 수정 (36건 일괄)
**CRITICAL (3건)**
16. ✅ 세대생략 증여 40% 할증 — tax_base > 20억 조건 검증 추가 (core.py)
17. ✅ 달러 적립 CAGR 0나누기 방어 + bare except 제거 (dollar.py)
18. ✅ 전월세 전환율 0 나누기 방어 (jeonwolse.py)

**HIGH (8건)**
19. ✅ 증여세·상속세 음수 세액 방지 `max(0, ...)` (inheritance.py)
20. ✅ 증여세 파이차트 음수 값 필터링 (inheritance.py)
21. ✅ 목표자금 적금 차트 변수명 `sav_req_monthly` 수정 (target_fund.py)
22. ✅ 목표자금 전략리포트 적금=단리, 펀드/ETF=월복리 공식 수정 (target_fund.py)
23. ✅ 목표자금 "부족/초과 달성" 메시지 조건 분기 (target_fund.py)
24. ✅ 은퇴설계 자산 성장 차트 월복리 annuity 공식 적용 (retirement.py)
25. ✅ 은퇴설계 yield_b=0 시 m_save_b 올바른 계산 (retirement.py)
26. ✅ 은퇴설계 중복 MC 섹션 제거 (retirement.py)

**MEDIUM (14건)**
27. ✅ 비주거(기타 토지/상가) 교육세 — 주택 가격대별 표준세율 조건 분리 (real_estate.py)
28. ✅ 은퇴설계 pay_years >= y_s 경고 추가 (retirement.py)
29. ✅ 달러 적립 수익 색상 녹색(#16a34a) 수정 (dollar.py)
30. ✅ 장기보유특별공제 거주기간 > 보유기간 검증 추가 (core.py)
31. ✅ MC 시뮬레이션 주석 log-normal → normal 수정 (core.py)

**LOW (11건)**
32. ✅ 미사용 import 제거 — core.py (textwrap)
33. ✅ 미사용 import 제거 — inheritance.py (pandas, numpy)
34. ✅ 미사용 import 제거 — jeonwolse.py (pandas, numpy, px 등)
35. ✅ 미사용 import 제거 — retirement.py (pandas, numpy, px 등)
36. ✅ 미사용 import 제거 — income_tax.py (numpy, px, 미사용 core 함수들)
37. ✅ 미사용 import 제거 — loan.py (pandas, numpy, px, solve_monthly_rate)
38. ✅ loan.py 불필요한 pass 제거
