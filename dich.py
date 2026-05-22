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
st.title("🇰🇷 Công Cụ Gõ Tiếng Hàn Siêu Cấp")
st.write("Hỗ trợ dịch từ văn bản và **DÁN ẢNH TRỰC TIẾP** từ bộ nhớ tạm!")

tab1, tab2 = st.tabs(["✍️ Nhập văn bản", "🖼️ Dán ảnh & Dịch (Giống Google)"])

# --- TAB 1: DỊCH CHỮ (CƠ BẢN) ---
with tab1:
    tu_viet = st.text_input("Nhập câu Tiếng Việt vào đây:")
    if st.button("Dịch & Chuyển đổi", type="secondary"):
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

# --- TAB 2: DÁN ẢNH & DỊCH (PRO) ---
with tab2:
    st.info("💡 **HƯỚNG DẪN:** Bạn chỉ cần Copy ảnh chụp màn hình chứa tiếng Việt (ví dụ dùng Print Screen hoặc Snipping Tool), sau đó bấm nút dán màu đỏ ở dưới.")
    
    # Khu vực nút bấm Dán ảnh (Custom màu sắc cho bắt mắt)
    st.write("**Bấm nút dưới đây để đưa ảnh vào:**")
    paste_result = paste_image_button(
        label="📋 Bấm vào đây để Dán ảnh (Paste)",
        background_color="#FF4B4B", # Màu đỏ Streamlit cho nổi bật
        hover_background_color="#FF3333"
    )
    
    # Xử lý nếu đã nhận được ảnh từ nút dán
    image = None
    if paste_result.image_data is not None:
        image = paste_result.image_data

    if image is not None:
        # Hiển thị ảnh
        st.image(image, caption="Ảnh bạn vừa dán lên", use_container_width=True)
        
        # Nút bấm chính thức để xử lý
        if st.button("Quét chữ & Dịch", type="primary"):
            with st.spinner('Đang dùng AI quét chữ tiếng Việt trong ảnh...'):
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
                    st.error(f"Lỗi hệ thống: {e}. Bạn hãy đảm bảo đã Reboot lại app trên Streamlit Cloud nhé.")