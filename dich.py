import streamlit as st
from deep_translator import GoogleTranslator
from PIL import Image
import easyocr
import numpy as np

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
st.set_page_config(page_title="Công Cụ Dịch Thuật Siêu Cấp 2.0")
st.title("🇰🇷 Công Cụ Dịch Đa Năng PRO 2.0")
st.write("Phiên bản **SIÊU CẤP 2.0** chuyên trị chữ trong Game/Phim/Ảnh phức tạp!")

che_do = st.radio(
    "⚙️ Bạn muốn làm gì?",
    ("🇻🇳 Việt ➡️ 🇰🇷 Hàn (Lấy cách gõ phím)", "🇰🇷 Hàn/🇯🇵 Nhật ➡️ 🇻🇳 Việt (Tra nghĩa từ ảnh Game/Phim)")
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
                except Exception as e: st.error(f"Lỗi dịch: {e}")
        else: st.warning("Nhập từ.")

from streamlit_paste_button import paste_image_button
with tab2:
    st.info("💡 Copy vùng ảnh chứa chữ (mờ/rõ/trong game đều được), bấm nút đỏ để Dán (Paste). Hệ thống sẽ tự xử lý.")
    
    paste_result = paste_image_button(label="📋 Bấm để Dán ảnh (Paste)", background_color="#FF4B4B")
    image_data = paste_result.image_data

    if image_data is not None:
        # Hiển thị ảnh gốc
        st.image(image_data, caption="Ảnh bạn vừa dán lên", use_container_width=True)
        
        if st.button("Quét & Dịch SIÊU CẤP 2.0", type="primary"):
            with st.spinner('Đang kích hoạt bộ não AI Siêu Cấp...'):
                try:
                    # 1. Chuyển PIL Image sang numpy array (Cần cho EasyOCR)
                    img_np = np.array(image_data)
                    
                    # 2. Khởi tạo reader SIÊU CẤP (chọn Ja+En cho ảnh game của bạn, Ko+Vi cho ảnh thường)
                    # Chúng ta cho phép nó đọc cả 4 ngôn ngữ một lúc
                    reader = easyocr.Reader(['ja', 'ko', 'vi', 'en'], gpu=False) # GPU=False để chạy trên Streamlit Cloud miễn phí
                    
                    # 3. Quét chữ SIÊU CẤP 2.0 (detail=0 để lấy text gọn)
                    extracted_texts = reader.readtext(img_np, detail=0)
                    
                    # 4. Ghép toàn bộ chữ quét được thành 1 câu
                    final_extracted_text = " ".join(extracted_texts).strip()
                    
                    if final_extracted_text:
                        st.write("**Văn bản đọc được:**")
                        st.success(final_extracted_text)
                        
                        # 5. Dịch theo chế độ bạn chọn
                        if "Việt ➡️ Hàn" in che_do:
                            # Quét được tiếng Việt (ví dụ từ file config), dịch sang Hàn
                            ket_qua = GoogleTranslator(source='vi', target='ko').translate(final_extracted_text)
                            st.subheader(f"Tiếng Hàn: {ket_qua}")
                            st.subheader(f"Cách gõ: {hangul_to_qwerty(ket_qua)}")
                        else:
                            # Quét được Nhật/Hàn/En (trong game), dịch sang Việt
                            # Tự động phát hiện nguồn ngôn ngữ là 'auto' cho an toàn
                            ket_qua = GoogleTranslator(source='auto', target='vi').translate(final_extracted_text)
                            st.subheader(f"Nghĩa Việt: {ket_qua}")
                    else:
                        st.warning("Hệ thống đã cố hết sức nhưng không nhận diện được chữ nào trong bức ảnh này. Bạn thử ảnh khác nét hơn nhé!")
                except Exception as e:
                    st.error(f"Lỗi: {e}")