import streamlit as st
from deep_translator import GoogleTranslator

# Bảng ánh xạ Jamo
CHOSEONG_MAP = ['r', 'R', 's', 'e', 'E', 'f', 'a', 'q', 'Q', 't', 'T', 'd', 'w', 'W', 'c', 'z', 'x', 'v', 'g']
JUNGSEONG_MAP = ['k', 'o', 'i', 'O', 'j', 'p', 'u', 'P', 'h', 'hk', 'ho', 'hl', 'y', 'n', 'nj', 'np', 'nl', 'b', 'm', 'ml', 'l']
JONGSEONG_MAP = ['', 'r', 'R', 'rt', 's', 'sw', 'sg', 'e', 'f', 'fr', 'fa', 'fq', 'ft', 'fx', 'fv', 'fg', 'a', 'q', 'qt', 't', 'T', 'd', 'w', 'c', 'z', 'x', 'v', 'g']

def hangul_to_qwerty(korean_text):
    result = ""
    for char in korean_text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            index = code - 0xAC00
            result += CHOSEONG_MAP[index // 588]
            result += JUNGSEONG_MAP[(index % 588) // 28]
            result += JONGSEONG_MAP[index % 28]
        else:
            result += char 
    return result

# Kiểm tra xem ký tự có phải là tiếng Hàn không
def is_korean(text):
    return any('\uac00' <= char <= '\ud7a3' for char in text)

st.title("🇰🇷 Tool Dịch Hàn - Việt")

input_text = st.text_area("Nhập nội dung cần dịch:")

if st.button("Dịch"):
    if input_text:
        # Tự động nhận diện ngôn ngữ
        if is_korean(input_text):
            # Hàn sang Việt
            res = GoogleTranslator(source='ko', target='vi').translate(input_text)
            st.success("Tiếng Việt:")
            st.info(res)
        else:
            # Việt sang Hàn
            res = GoogleTranslator(source='vi', target='ko').translate(input_text)
            st.success("Tiếng Hàn:")
            st.info(res)
            st.write("**Cách gõ phím (QWERTY):**")
            st.code(hangul_to_qwerty(res))
    else:
        st.warning("Vui lòng nhập nội dung!")
