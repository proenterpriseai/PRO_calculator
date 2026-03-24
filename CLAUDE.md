# CLAUDE.md — 계산기 앱 핵심 규칙

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

### 2. 대출 상환 (tabs/loan.py)
- **3가지 방식**: 원리금균등, 원금균등, **만기일시상환**
- 만기일시상환 = 매월 이자만 납부, 만기에 원금 전액 상환
- **거치식(grace period) 방식은 제거됨** — 절대 복원 금지

### 3. 전월세 전환 (tabs/jeonwolse.py)
- **법정상한 전환율**: 기준금리(2.50%) + 2.0% = **4.50%**
- **투자 기대수익률**: 별도 입력 (기본 3.5%) — 전환율과 분리
- **절대 금지**: 전환율과 투자수익률을 동일 변수로 사용 (항등식 버그 발생)

### 4. 상속세 (tabs/inheritance.py + app.py)
- **장례비용**: `max(500만, min(입력값, 1,500만))` — 최소 500만 보장
- **배우자공제**: `max(5억, min(입력값, 법정상속분, 30억))`
- **기초+인적공제**: 일괄공제(5억)보다 작으면 자동 5억 적용

### 5. 부동산 양도세 (tabs/real_estate.py)
- **분양권(2021년 이후 취득)**: 1년 미만 70%, 1~2년 60%, **2년 이상 일반 누진세율**
- **지방교육세**: 주택만 가격대별 표준세율 적용 (6억↓1%, 6~9억 슬라이딩, 9억↑3%). 비주거는 `tax × 0.10`

### 6. 달러 적립 (tabs/dollar.py)
- **수수료율**: presentation_mode와 일반 모드 모두 `0.0` (일치 필수)

### 7. 목표자금 (tabs/target_fund.py)
- **전략리포트 적금 금리**: 사용자 입력값 `top_sav_rate` 사용 (3.5% 하드코딩 금지)
- **몬테카를로 시뮬레이션 200회 차트**: 삭제됨 — 복원 금지

---

## Streamlit 위젯 규칙
- `st.slider`, `st.number_input`의 `value=`는 첫 렌더링만 적용 → **고정 기본값 사용**
- 슬라이더↔숫자입력 연동: `make_sync_callback()` 사용
- presentation_mode: `st.session_state.get()` 으로 값 읽기

## 빌드 & 검증
```bash
python -m py_compile app.py && python -m py_compile core.py
python -m py_compile tabs/loan.py && python -m py_compile tabs/jeonwolse.py
python -m py_compile tabs/inheritance.py && python -m py_compile tabs/real_estate.py
python -m py_compile tabs/dollar.py && python -m py_compile tabs/target_fund.py
python -m py_compile tabs/retirement.py && python -m py_compile tabs/income_tax.py
```

## ⚠️ Vercel 프로젝트 동기화 (반드시 준수)
- **Vercel 코드**: 바탕화면 `calculator-vercel/` 폴더 (GitHub: `proenterpriseai/Procalculator`)
- **Streamlit 코드**: 바탕화면 `계산기/` 폴더 (GitHub: `proenterpriseai/PRO_calculator`)
- **제목/문구 변경 시 양쪽 동기화 필수** (Vercel index.html ↔ Streamlit tabs/*.py)

## ⚠️ 배포 순서 (반드시 준수)
1. **`.vercel.app` (pro-financecalculator.vercel.app) 먼저**: `calculator-vercel/` 수정 → git push → Vercel 배포 완료 확인
2. **Streamlit 후속**: `계산기/` 수정 → git push → Streamlit 배포 완료 확인
- 수정 작업 시 `.vercel.app` 배포를 건너뛰고 Streamlit만 배포하지 않는다
- 코드 수정 후 반드시 push/배포까지 완료한 뒤 사용자에게 테스트 안내한다

## 수정 이력
총 51건 수정 완료 (2025-03 15건 + 2026-03 36건). 상세 → memory `claudemd-calculator-history.md` 참조
