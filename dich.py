import streamlit as st
from deep_translator import GoogleTranslator

# Các hàm hỗ trợ gõ phím tiếng Hàn
CHOSEONG_MAP = { ... } # (Giữ nguyên các map của bạn ở đây)
def hangul_to_qwerty(text):
    # ... (Giữ nguyên hàm này)
    return result

st.title("Tool Dịch Hàn - Việt")

# Chỉ để lại 1 cột duy nhất cho văn bản
input_text = st.text_area("Nhập văn bản cần dịch:")
che_do = st.selectbox("Chọn chế độ:", ["Hàn sang Việt", "Việt sang Hàn", "Lấy cách gõ phím"])

if st.button("Dịch"):
    if input_text:
        if che_do == "Hàn sang Việt":
            res = GoogleTranslator(source='ko', target='vi').translate(input_text)
            st.success(res)
        elif che_do == "Việt sang Hàn":
            res = GoogleTranslator(source='vi', target='ko').translate(input_text)
            st.info(res)
        elif che_do == "Lấy cách gõ phím":
            st.code(hangul_to_qwerty(input_text))
