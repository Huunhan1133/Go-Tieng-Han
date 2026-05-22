import streamlit as st
from deep_translator import GoogleTranslator
from PIL import Image
import easyocr
import numpy as np
from streamlit_paste_button import paste_image_button

# Bảng ánh xạ Jamo sang QWERTY
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

# --- GIAO DIỆN WEB ---
st.set_page_config(page_title="Công Cụ Dịch Thuật Siêu Cấp 2.0", layout="wide") 

st.title("🇰🇷 Công Cụ Dịch Đa Năng PRO 2.0")
st.write("Phiên bản **SIÊU CẤP 2.0** chuyên trị chữ trong Game/Phim/Ảnh phức tạp!")

# Bạn có thể thoải mái sửa chữ ở đây, miễn là giữ lại chữ "Lấy cách gõ phím"
che_do = st.radio(
    "⚙️ Bạn muốn làm gì hôm nay?",
    ("VN Việt ➡️ KR Hàn (Lấy cách gõ phím)", "KR Hàn ➡️ VN Việt (Tra nghĩa từ ảnh Game/Phim)"),
    horizontal=True
)

st.divider()

col1, col2 = st.columns(2, gap="large")

with col1:
    st.subheader("✍️ Dịch từ Văn bản")
    tu_nhap = st.text_input("Nhập nội dung cần dịch:")
    
    if st.button("Dịch văn bản", type="secondary"):
        if tu_nhap:
            with st.spinner('Đang dịch...'):
                try:
                    # Đã sửa lại điều kiện kiểm tra thông minh hơn
                    if "Lấy cách gõ phím" in che_do:
                        ket_qua = GoogleTranslator(source='vi', target='ko').translate(tu_nhap)
                        st.success("Dịch thành công!")
                        st.write("**Tiếng Hàn:**")
                        st.info(ket_qua)
                        st.write("**Cách gõ:**")
                        st.code(hangul_to_qwerty(ket_qua))
                    else:
                        ket_qua = GoogleTranslator(source='ko', target='vi').translate(tu_nhap)
                        st.success("Dịch thành công!")
                        st.write("**Nghĩa Việt:**")
                        st.info(ket_qua)
                except Exception as e: 
                    st.error(f"Lỗi dịch: {e}")
        else: 
            st.warning("Bạn chưa nhập từ nào!")

with col2:
    st.subheader("🖼️ Dịch từ Hình ảnh")
    st.info("💡 Copy vùng ảnh chứa chữ, bấm nút đỏ bên dưới để Dán (Paste).")
    
    paste_result = paste_image_button(label="📋 Bấm để Dán ảnh (Paste)", background_color="#FF4B4B")
    image_data = paste_result.image_data

    if image_data is not None:
        st.image(image_data, caption="Ảnh bạn vừa dán lên", use_container_width=True)
        
        if st.button("Quét & Dịch SIÊU CẤP 2.0", type="primary"):
            with st.spinner('Đang kích hoạt bộ não AI...'):
                try:
                    img_np = np.array(image_data)
                    
                    # Đã sửa lại điều kiện kiểm tra thông minh hơn
                    if "Lấy cách gõ phím" in che_do:
                        reader = easyocr.Reader(['vi', 'en'], gpu=False)
                    else:
                        reader = easyocr.Reader(['ko', 'en'], gpu=False)
                    
                    extracted_texts = reader.readtext(img_np, detail=0)
                    final_extracted_text = " ".join(extracted_texts).strip()
                    
                    if final_extracted_text:
                        st.write("**Văn bản máy đọc được:**")
                        st.success(final_extracted_text)
                        
                        # Đã sửa lại điều kiện kiểm tra thông minh hơn
                        if "Lấy cách gõ phím" in che_do:
                            ket_qua = GoogleTranslator(source='vi', target='ko').translate(final_extracted_text)
                            st.write("**Tiếng Hàn:**")
                            st.info(ket_qua)
                            st.write("**Cách gõ:**")
                            st.code(hangul_to_qwerty(ket_qua))
                        else:
                            ket_qua = GoogleTranslator(source='auto', target='vi').translate(final_extracted_text)
                            st.write("**Nghĩa Việt:**")
                            st.info(ket_qua)
                    else:
                        st.warning("Hệ thống không nhận diện được chữ nào trong bức ảnh này.")
                except Exception as e:
                    st.error(f"Lỗi: {e}")