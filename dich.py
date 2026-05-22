import streamlit as st
from deep_translator import GoogleTranslator

# Bảng ánh xạ Jamo sang QWERTY
CHOSEONG_MAP = ['r', 'R', 's', 'e', 'E', 'f', 'a', 'q', 'Q', 't', 'T', 'd', 'w', 'W', 'c', 'z', 'x', 'v', 'g']
JUNGSEONG_MAP = ['k', 'o', 'i', 'O', 'j', 'p', 'u', 'P', 'h', 'hk', 'ho', 'hl', 'y', 'n', 'nj', 'np', 'nl', 'b', 'm', 'ml', 'l']
JONGSEONG_MAP = ['', 'r', 'R', 'rt', 's', 'sw', 'sg', 'e', 'f', 'fr', 'fa', 'fq', 'ft', 'fx', 'fv', 'fg', 'a', 'q', 'qt', 't', 'T', 'd', 'w', 'c', 'z', 'x', 'v', 'g']

def translate_vi_to_ko(text):
    try:
        return GoogleTranslator(source='vi', target='ko').translate(text)
    except:
        return None

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

# --- GIAO DIỆN WEB ---
st.title("🇰🇷 Công Cụ Gõ Tiếng Hàn (Telex)")
st.write("Nhập tiếng Việt, hệ thống sẽ dịch sang tiếng Hàn và chỉ cho bạn cách gõ trên bàn phím QWERTY!")

# Ô nhập dữ liệu
tu_viet = st.text_input("Nhập câu Tiếng Việt vào đây:")

# Nút bấm xử lý
if st.button("Dịch & Chuyển đổi"):
    if tu_viet:
        with st.spinner('Đang dịch...'):
            tu_han = translate_vi_to_ko(tu_viet)
            if tu_han:
                chuoi_phim = hangul_to_qwerty(tu_han)
                st.success("Thành công!")
                st.subheader(f"Tiếng Hàn: {tu_han}")
                st.subheader(f"Cách gõ: {chuoi_phim}")
            else:
                st.error("Có lỗi xảy ra khi dịch. Vui lòng thử lại.")
    else:
        st.warning("Bạn chưa nhập từ nào kìa!")