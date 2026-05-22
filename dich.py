import streamlit as st
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image
from streamlit_paste_button import paste_image_button

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
st.title("🇰🇷 Công Cụ Gõ Tiếng Hàn PRO")
st.write("Hỗ trợ dịch từ văn bản và trích xuất chữ tiếng Việt từ hình ảnh!")

tab1, tab2 = st.tabs(["✍️ Nhập văn bản", "🖼️ Dịch từ ảnh"])

# --- TAB 1: DỊCH CHỮ ---
with tab1:
    tu_viet = st.text_input("Nhập câu Tiếng Việt vào đây:")
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
                    st.error("Có lỗi xảy ra. Vui lòng thử lại.")
        else:
            st.warning("Bạn chưa nhập từ nào!")

# --- TAB 2: DỊCH ẢNH ---
with tab2:
    st.info("💡 Mẹo: Bạn có thể tải file ảnh lên HOẶC copy ảnh và bấm nút Dán (Paste) ở bên dưới nhé.")
    
    # 1. Khu vực tải ảnh bình thường
    uploaded_file = st.file_uploader("1. Tải file ảnh từ máy tính", type=["jpg", "jpeg", "png"])
    
    st.write("--- HOẶC ---")
    
    # 2. Khu vực dán ảnh từ Clipboard
    st.write("**2. Dán ảnh vừa Copy**")
    paste_result = paste_image_button(
        label="📋 Bấm vào đây để Dán ảnh",
        background_color="#FF4B4B",
        hover_background_color="#FF6666"
    )
    
    # Xác định nguồn ảnh: Lấy từ Upload hay từ nút Dán?
    image = None
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
    elif paste_result.image_data is not None:
        image = paste_result.image_data

    # Xử lý nếu đã nhận được ảnh
    if image is not None:
        st.image(image, caption="Ảnh bạn vừa đưa lên", use_container_width=True)
        
        if st.button("Quét chữ & Dịch", type="primary"):
            with st.spinner('Đang dùng AI quét chữ trong ảnh...'):
                try:
                    extracted_text = pytesseract.image_to_string(image, lang='vie').strip()
                    
                    if extracted_text:
                        st.write("**Chữ máy tính đọc được:**")
                        st.info(extracted_text)
                        
                        tu_han = translate_vi_to_ko(extracted_text)
                        if tu_han:
                            chuoi_phim = hangul_to_qwerty(tu_han)
                            st.success("Đã dịch thành công!")
                            st.subheader(f"Tiếng Hàn: {tu_han}")
                            st.subheader(f"Cách gõ: {chuoi_phim}")
                    else:
                        st.warning("Máy không tìm thấy chữ nào trong ảnh. Bạn thử dùng ảnh nét hơn xem sao nhé!")
                except Exception as e:
                    st.error(f"Lỗi hệ thống: {e}")