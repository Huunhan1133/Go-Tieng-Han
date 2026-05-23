import streamlit as st
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image
import cv2
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

def enhanced_image_processing(pil_image):
    # Bộ lọc nội suy làm nét ảnh vỡ hạt
    opencv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    width, height = pil_image.size
    enhanced_img = cv2.resize(opencv_img, (width * 2, height * 2), interpolation=cv2.INTER_LANCZOS4)
    gray_img = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    final_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(final_img)

# --- GIAO DIỆN WEB ---
st.set_page_config(page_title="Công Cụ Dịch Thuật Đa Năng", layout="wide") 

st.title("🇰🇷 Công Cụ Dịch Đa Năng PRO (Bản Ổn Định)")
st.write("Sử dụng mã nguồn mở 100%, không lo API limit, không giới hạn số lần dịch!")

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

# ... (Giữ nguyên các hàm CHOSEONG_MAP, JUNGSEONG_MAP, JONGSEONG_MAP, hangul_to_qwerty và enhanced_image_processing ở trên đầu)

# --- SỬA LẠI ĐOẠN DỊCH TỪ ẢNH TRONG CỘT 2 ---
with col2:
    st.subheader("🖼️ Dịch từ Hình ảnh")
    st.info("💡 Mẹo: Cắt thật sát vào chữ để máy đọc chuẩn nhất.")
    
    paste_result = paste_image_button(label="📋 Bấm để Dán ảnh (Paste)", background_color="#FF4B4B")
    image_data = paste_result.image_data

    if image_data is not None:
        st.image(image_data, caption="Ảnh bạn vừa dán lên", use_container_width=True)
        
        if st.button("Quét & Dịch qua Ảnh", type="primary"):
            with st.spinner('Đang quét chữ...'):
                try:
                    processed_image = enhanced_image_processing(image_data)
                    
                    if "Lấy cách gõ phím" in che_do:
                        ngon_ngu = 'vie'
                        config = '--psm 6'
                    else:
                        ngon_ngu = 'kor'
                        config = '--psm 6'
                    
                    extracted_text = pytesseract.image_to_string(processed_image, lang=ngon_ngu, config=config).strip()
                    
                    if extracted_text:
                        st.write("**Văn bản máy đọc được:**")
                        st.success(extracted_text)
                        
                        if "Lấy cách gõ phím" in che_do:
                            # Dịch từ Việt sang Hàn
                            ket_qua = GoogleTranslator(source='vi', target='ko').translate(extracted_text)
                            st.write("**Tiếng Hàn:**")
                            st.info(ket_qua)
                            # THÊM ĐOẠN NÀY ĐỂ HIỂN THỊ CÁCH GÕ
                            st.write("**Cách gõ:**")
                            st.code(hangul_to_qwerty(ket_qua))
                        else:
                            # Dịch từ Hàn sang Việt
                            ket_qua = GoogleTranslator(source='ko', target='vi').translate(extracted_text)
                            st.write("**Nghĩa Việt:**")
                            st.info(ket_qua)
                            # Nếu bạn muốn hiển thị cách gõ cả khi dịch ngược:
                            st.write("**Cách gõ của từ tiếng Hàn vừa dịch:**")
                            st.code(hangul_to_qwerty(extracted_text))
                    else:
                        st.warning("Máy không đọc được chữ, hình như ảnh bị dính nền phức tạp hoặc quá mờ!")
                except Exception as e:
                    st.error(f"Lỗi: {e}. Vui lòng thử Reboot lại App!")
