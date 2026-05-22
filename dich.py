import streamlit as st
from deep_translator import GoogleTranslator
import pytesseract
from PIL import Image

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

# Tạo 2 Tab để giao diện gọn gàng
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
    st.info("💡 Mẹo: Hãy tải lên ảnh chụp màn hình hoặc ảnh có chữ in rõ nét để máy đọc chính xác nhất nhé.")
    uploaded_file = st.file_uploader("Tải ảnh chứa tiếng Việt lên đây", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        # Hiển thị ảnh
        image = Image.open(uploaded_file)
        st.image(image, caption="Ảnh bạn vừa tải lên", use_container_width=True)
        
        if st.button("Quét chữ & Dịch"):
            with st.spinner('Đang dùng AI quét chữ trong ảnh...'):
                try:
                    # Đọc chữ từ ảnh (lang='vie' là tiếng Việt)
                    extracted_text = pytesseract.image_to_string(image, lang='vie').strip()
                    
                    if extracted_text:
                        st.write("**Chữ máy tính đọc được:**")
                        st.info(extracted_text)
                        
                        # Dịch chữ vừa quét được
                        tu_han = translate_vi_to_ko(extracted_text)
                        if tu_han:
                            chuoi_phim = hangul_to_qwerty(tu_han)
                            st.success("Đã dịch thành công!")
                            st.subheader(f"Tiếng Hàn: {tu_han}")
                            st.subheader(f"Cách gõ: {chuoi_phim}")
                    else:
                        st.warning("Máy không tìm thấy chữ nào trong ảnh. Bạn thử dùng ảnh nét hơn xem sao nhé!")
                except Exception as e:
                    st.error("Chưa cài đặt đủ hệ thống quét ảnh trên máy chủ. Bạn nhớ tạo file packages.txt nhé!")