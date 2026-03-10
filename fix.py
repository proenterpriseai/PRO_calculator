import re

with open('app.py', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. 10년 뒤 동일한 달러(현금)를 쥐기 위해 -> 10년 뒤 동일한 달러(현금)를 만들기 위해,
text = text.replace('10년 뒤 동일한 달러(현금)를 쥐기 위해,', '10년 뒤 동일한 달러(현금)를 만들기 위해,')
# (Just in case there's no comma)
text = text.replace('10년 뒤 동일한 달러(현금)를 쥐기 위해', '10년 뒤 동일한 달러(현금)를 만들기 위해,')

# 2. 환율 변동성과 확정 금리를 결합하여 안정적인 달러 자산을 확보하는 플랜입니다. 삭제
text = text.replace('st.markdown("환율 변동성과 확정 금리를 결합하여 안정적인 달러 자산을 확보하는 플랜입니다.")\n', '')

# 3. 일반 시중은행 특판 예적금 -> 일반 시중은행 예적금
text = text.replace('일반 시중은행 특판 예적금', '일반 시중은행 예적금')

# 4. +X%p 압도적! -> +X% 유리! 
# (using regex for flexibility)
text = re.sub(r'\+?\{yield_diff:\.2f\}%p 압도적!', r'+{yield_diff:.2f}% 유리!', text)
text = re.sub(r'\{yield_diff:\.2f\}%p', r'{yield_diff:.2f}%', text)

# 5. 환전수수료율 내용 삭제
# "commission_rate = st.slider..." 
slider_pattern = re.compile(r'commission_rate\s*=\s*st\.slider\([\s\S]*?\)\s*/\s*100')
text = slider_pattern.sub('commission_rate = 0.0', text)

# 6. 10년 시점 플랜 분석 -> 10년 시점 예상 분석
text = text.replace('10년 시점 플랜 분석', '10년 시점 예상 분석')

# 7. 10년 확정 환급률 ($) -> 10년 시점 환급률 ($)
text = text.replace('10년 확정 환급률 ($)', '10년 시점 환급률 ($)')

# 8. All initial values to 0 / empty.
# In `comma_int_input` function update the formatting so 0 is empty.
comma_func = '''def comma_int_input(label, value, key):
    """3자리 콤마 포맷팅을 지원하는 텍스트 기반 정수 입력 위젯"""
    num_key = key
    str_key = f"{key}_str"
    
    # 초기값 설정
    if num_key not in st.session_state:
        st.session_state[num_key] = value
    
    current_num = st.session_state[num_key]
    
    # Callback: 문자열 입력 -> 숫자 변환 및 포맷팅
    def on_change_callback():
        user_str = st.session_state[str_key]
        if not user_str.strip():
            st.session_state[num_key] = 0
            st.session_state[str_key] = ""
            return
        try:
            # 쉼표 제거 후 정수 변환
            new_num = int(str(user_str).replace(",", "").strip())
            st.session_state[num_key] = new_num
            # 다시 쉼표 포맷팅하여 표시값 업데이트
            st.session_state[str_key] = f"{new_num:,}"
        except:
            if st.session_state[num_key] == 0:
                st.session_state[str_key] = ""
            else:
                st.session_state[str_key] = f"{st.session_state[num_key]:,}"
            
    # 위젯 상태 초기화 및 동기화 (외부 변수 변경 대응)
    formatted_val = "" if current_num == 0 else f"{current_num:,}"
    
    if str_key not in st.session_state:
        st.session_state[str_key] = formatted_val
    else:
        # 외부에서 값이 변경되었을 경우를 대비해 동기화 점검
        try:
            current_str_val = int(str(st.session_state[str_key]).replace(",", "").strip()) if st.session_state[str_key].strip() else 0
            if current_str_val != current_num:
                st.session_state[str_key] = formatted_val
        except:
            st.session_state[str_key] = formatted_val
        
    st.text_input(
        label,
        key=str_key,
        on_change=on_change_callback
    )
    
    return st.session_state[num_key]'''

text = re.sub(r'def comma_int_input\(label, value, key\):(.*?)return st\.session_state\[num_key\]', 
              comma_func.replace('\\', '\\\\'), text, flags=re.DOTALL)

# Set the 2nd argument of all comma_int_input to 0
text = re.sub(r'(comma_int_input\(".*?", )([0-9_]+)(, ".*?"\))', r'\g<1>0\g<3>', text)

# Set all value=... in number_inputs to value=None if they are numbers. (But Streamlit 1.28 supports it only. Let's just set them to value=0 to be safe with all math)
# E.g., `value=1000,` -> `value=0,`
# Wait, let's only do it for these ones:
text = re.sub(r'value=1000,\s*step=100', r'value=0, step=100', text)
text = re.sub(r'value=500_000_000', r'value=0', text)
text = re.sub(r'value=200_000_000', r'value=0', text)

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(text)
