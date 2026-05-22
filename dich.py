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
    """
    Kính hiển vi thông minh: Làm rõ nét chữ bị mờ do thu phóng
    """
    # 1. Chuyển từ Pillow sang OpenCV BGR format
    opencv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    
    # 2. Phóng đại ảnh lên gấp 2 lần bằng thuật toán nội suy Lanzcos (làm mịn hạt)
    # Đây là "Kính hiển vi" của chúng ta
    width, height = pil_image.size
    enhanced_img = cv2.resize(opencv_img, (width * 2, height * 2), interpolation=cv2.INTER_LANCZOS4)
    
    # 3. Chuyển sang ảnh xám
    gray_img = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
    
    # 4. Áp dụng nhị phân hóa cục bộ (sau khi khử nhiễu) để làm nét chữ
    # Xử lý này rất hiệu quả với ảnh mờ vỡ hạt
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    final_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    
    # 5. Chuyển lại về Pillow để Tesseract đọc
    return Image.fromarray(final_img)

# --- GIAO DIỆN WEB ---
st.title("🇰🇷 Công Cụ Gõ Tiếng Hàn Siêu Chống Mờ Pro")
st.write("Hỗ trợ dịch đa năng, đặc biệt được nâng cấp bộ xử lý để đọc chữ bị vỡ hạt!")

che_do = st.radio(
    "⚙️ Chọn chế độ:",
    ("🇻🇳 Việt ➡️ 🇰🇷 Hàn", "🇰🇷 Hàn ➡️ 🇻🇳 Việt")
)

tab1, tab2 = st.tabs(["✍️ Nhập văn bản", "🖼️ Dán ảnh & Chuyển đổi"])

with tab1:
    tu_nhap = st.text_input("Nhập nội dung:")
    if st.button("Dịch", type="secondary"):
        if tu_nhap:
            with st.spinner('Đang dịch...'):
                try:
                    if "Việt ➡️ Hàn" in che_do:
                        ket_qua = GoogleTranslator(source='vi', target='ko').translate(tu_nhap)
                        st.subheader(f"Tiếng Hàn: {ket_qua}")
                        st.subheader(f"Cách gõ: {hangul_to_qwerty(ket_qua)}")
                    else:
                        ket_qua = GoogleTranslator(source='ko', target='vi').translate(tu_nhap)
                        st.subheader(f"Nghĩa Việt: {ket_qua}")
                except: st.error("Lỗi.")
        else: st.warning("Nhập từ.")

with tab2:
    st.info("💡 Copy vùng ảnh chứa chữ, bấm nút đỏ để Dán (Paste). Nếu ảnh quá mờ, hệ thống siêu chống mờ sẽ tự kích hoạt.")
    
    paste_result = paste_image_button(label="📋 Dán ảnh (Paste)", background_color="#FF4B4B")
    image = paste_result.image_data

    if image is not None:
        st.write("---")
        col1, col2 = st.columns(2)
        
        with col1:
            st.image(image, caption="Ảnh mờ gốc (Bị vỡ hạt)", use_container_width=True)
            if st.button("Quét thường", type="secondary"):
                with st.spinner('Đang quét...'):
                    ngon_ngu = 'vie' if "Việt ➡️ Hàn" in che_do else 'kor'
                    text = pytesseract.image_to_string(image, lang=ngon_ngu).strip()
                    if text: st.info(f"Văn bản thường: {text}")
                    else: st.warning("Không đọc được.")

        with col2:
            st.image(enhanced_image_processing(image), caption="Ảnh đã được Siêu Chống Mờ (Làm rõ nét)", use_container_width=True)
            if st.button("Quét SIÊU CẤP", type="primary"):
                with st.spinner('Đang kích hoạt kính hiển vi thông minh...'):
                    try:
                        # Kích hoạt hàm xử lý siêu cấp
                        processed_image = enhanced_image_processing(image)
                        
                        ngon_ngu = 'vie' if "Việt ➡️ Hàn" in che_do else 'kor'
                        
                        # Cấu hình OCR đặc biệt cho chữ bị mờ (psm 10: single character)
                        config = '--psm 10' if "Hàn ➡️ Việt" in che_do else '--psm 7'
                        
                        extracted_text = pytesseract.image_to_string(processed_image, lang=ngon_ngu, config=config).strip()
                        
                        if extracted_text:
                            st.write("**Văn bản đọc được:**")
                            st.success(extracted_text)
                            
                            if "Việt ➡️ Hàn" in che_do:
                                ket_qua = GoogleTranslator(source='vi', target='ko').translate(extracted_text)
                                st.subheader(f"Tiếng Hàn: {ket_qua}")
                                st.subheader(f"Cách gõ: {hangul_to_qwerty(ket_qua)}")
                            else:
                                ket_qua = GoogleTranslator(source='ko', target='vi').translate(extracted_text)
                                st.subheader(f"Nghĩa Việt: {ket_qua}")
                        else:
                            st.warning("Hệ thống đã cố hết sức nhưng không nhận diện được chữ nào. Bạn thử ảnh nét hơn nhé!")
                    except Exception as e: st.error(f"Lỗi: {e}")