import streamlit as st
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image
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
st.title("🇰🇷 Công Cụ Tiếng Hàn Đa Năng")
st.write("Hỗ trợ lấy cách gõ phím hoặc Dịch trực tiếp từ ảnh trong Game/Phim!")

# Công tắc chọn chế độ
che_do = st.radio(
    "⚙️ Chọn mục đích sử dụng của bạn:",
    ("🇻🇳 Việt ➡️ 🇰🇷 Hàn (Để lấy cách gõ phím)", "🇰🇷 Hàn ➡️ 🇻🇳 Việt (Để tra nghĩa tiếng Việt)")
)

tab1, tab2 = st.tabs(["✍️ Nhập văn bản", "🖼️ Dán ảnh & Dịch"])

# --- TAB 1: NHẬP VĂN BẢN ---
with tab1:
    tu_nhap = st.text_input("Nhập nội dung vào đây:")
    if st.button("Dịch ngay", type="secondary"):
        if tu_nhap:
            with st.spinner('Đang dịch...'):
                try:
                    if "Việt ➡️ Hàn" in che_do:
                        ket_qua = GoogleTranslator(source='vi', target='ko').translate(tu_nhap)
                        st.success("Thành công!")
                        st.subheader(f"Tiếng Hàn: {ket_qua}")
                        st.subheader(f"Cách gõ: {hangul_to_qwerty(ket_qua)}")
                    else:
                        ket_qua = GoogleTranslator(source='ko', target='vi').translate(tu_nhap)
                        st.success("Thành công!")
                        st.subheader(f"Nghĩa Tiếng Việt: {ket_qua}")
                except:
                    st.error("Có lỗi xảy ra. Vui lòng thử lại.")
        else:
            st.warning("Bạn chưa nhập từ nào!")

# --- TAB 2: DÁN ẢNH ---
with tab2:
    st.info("💡 Copy ảnh có chứa chữ và bấm nút đỏ bên dưới để dán.")
    
    paste_result = paste_image_button(
        label="📋 Bấm vào đây để Dán ảnh (Paste)",
        background_color="#FF4B4B",
        hover_background_color="#FF3333"
    )
    
    image = None
    if paste_result.image_data is not None:
        image = paste_result.image_data

    if image is not None:
        st.image(image, caption="Ảnh bạn vừa dán lên", use_container_width=True)
        
        if st.button("Quét chữ & Dịch", type="primary"):
            with st.spinner('Đang dùng AI quét chữ trong ảnh...'):
                try:
                    # Xác định ngôn ngữ quét ảnh dựa theo chế độ
                    ngon_ngu_quet = 'vie' if "Việt ➡️ Hàn" in che_do else 'kor'
                    
                    text_quet = pytesseract.image_to_string(image, lang=ngon_ngu_quet).strip()
                    
                    if text_quet:
                        st.write("**Chữ máy tính đọc được:**")
                        st.info(text_quet)
                        
                        # Dịch theo chế độ
                        if "Việt ➡️ Hàn" in che_do:
                            ket_qua = GoogleTranslator(source='vi', target='ko').translate(text_quet)
                            st.success("Đã dịch thành công!")
                            st.subheader(f"Tiếng Hàn: {ket_qua}")
                            st.subheader(f"Cách gõ: {hangul_to_qwerty(ket_qua)}")
                        else:
                            ket_qua = GoogleTranslator(source='ko', target='vi').translate(text_quet)
                            st.success("Đã dịch thành công!")
                            st.subheader(f"Nghĩa Tiếng Việt: {ket_qua}")
                    else:
                        st.warning("Máy không đọc được chữ nào. Bạn thử ảnh nét hơn nhé!")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")