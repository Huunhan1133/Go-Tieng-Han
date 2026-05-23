import streamlit as st
import google.generativeai as genai
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
    opencv_img = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)
    width, height = pil_image.size
    enhanced_img = cv2.resize(opencv_img, (width * 2, height * 2), interpolation=cv2.INTER_LANCZOS4)
    gray_img = cv2.cvtColor(enhanced_img, cv2.COLOR_BGR2GRAY)
    blurred_img = cv2.GaussianBlur(gray_img, (5, 5), 0)
    final_img = cv2.adaptiveThreshold(blurred_img, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
    return Image.fromarray(final_img)

# --- HÀM DỊCH THUẬT BẰNG AI ---
def ai_translate(text, direction, api_key):
    try:
        genai.configure(api_key=api_key)
        # Sử dụng model flash siêu tốc của Google
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        if direction == "vi2ko":
            prompt = f"Dịch câu tiếng Việt sau sang tiếng Hàn một cách tự nhiên nhất, dùng văn phong giao tiếp mạng hoặc game. Chỉ in ra kết quả dịch, không giải thích gì thêm: '{text}'"
        else:
            prompt = f"Dịch câu tiếng Hàn/Nhật sau sang tiếng Việt thật mượt mà và dễ hiểu. Đặc biệt chú ý dịch sát nghĩa nếu đây là thuật ngữ, tên vật phẩm (như Tinh thể linh hồn, ngọc...), kỹ năng hoặc đoạn hội thoại trong các tựa game nhập vai MMORPG cổ điển. Chỉ in ra kết quả dịch, tuyệt đối không giải thích thêm: '{text}'"
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Lỗi AI (Có thể do API Key chưa đúng): {e}"

# --- GIAO DIỆN WEB ---
st.set_page_config(page_title="Công Cụ Dịch Thuật AI", layout="wide") 

# Cột bên trái để nhập API Key bảo mật
st.sidebar.header("🔑 Cấu hình Trí tuệ Nhân tạo")
st.sidebar.info("Để AI hoạt động, bạn cần nhập API Key lấy từ Google AI Studio.")
user_api_key = st.sidebar.text_input("Nhập Gemini API Key vào đây:", type="password")

st.title("🇰🇷 Công Cụ Dịch Đa Năng Tích Hợp AI")
st.write("Sử dụng não bộ Trí tuệ Nhân tạo để dịch mượt mà các thuật ngữ và câu lóng!")

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
        if not user_api_key:
            st.error("⚠️ Vui lòng nhập API Key ở thanh menu bên trái trước!")
        elif tu_nhap:
            with st.spinner('AI đang suy nghĩ...'):
                if "Lấy cách gõ phím" in che_do:
                    ket_qua = ai_translate(tu_nhap, "vi2ko", user_api_key)
                    if "Lỗi AI" not in ket_qua:
                        st.success("Dịch thành công!")
                        st.write("**Tiếng Hàn (AI dịch):**")
                        st.info(ket_qua)
                        st.write("**Cách gõ:**")
                        st.code(hangul_to_qwerty(ket_qua))
                    else: st.error(ket_qua)
                else:
                    ket_qua = ai_translate(tu_nhap, "ko2vi", user_api_key)
                    if "Lỗi AI" not in ket_qua:
                        st.success("Dịch thành công!")
                        st.write("**Nghĩa Việt (AI dịch):**")
                        st.info(ket_qua)
                    else: st.error(ket_qua)
        else: 
            st.warning("Bạn chưa nhập từ nào!")

with col2:
    st.subheader("🖼️ Dịch từ Hình ảnh")
    paste_result = paste_image_button(label="📋 Bấm để Dán ảnh (Paste)", background_color="#FF4B4B")
    image_data = paste_result.image_data

    if image_data is not None:
        st.image(image_data, caption="Ảnh bạn vừa dán lên", use_container_width=True)
        
        if st.button("Quét & Dịch bằng AI", type="primary"):
            if not user_api_key:
                st.error("⚠️ Vui lòng nhập API Key ở thanh menu bên trái trước!")
            else:
                with st.spinner('Đang quét chữ và phân tích ngữ cảnh...'):
                    try:
                        processed_image = enhanced_image_processing(image_data)
                        ngon_ngu = 'vie' if "Lấy cách gõ phím" in che_do else 'kor'
                        extracted_text = pytesseract.image_to_string(processed_image, lang=ngon_ngu, config='--psm 6').strip()
                        
                        if extracted_text:
                            st.write("**Văn bản máy đọc được:**")
                            st.success(extracted_text)
                            
                            if "Lấy cách gõ phím" in che_do:
                                ket_qua = ai_translate(extracted_text, "vi2ko", user_api_key)
                                st.write("**Tiếng Hàn:**")
                                st.info(ket_qua)
                                st.write("**Cách gõ:**")
                                st.code(hangul_to_qwerty(ket_qua))
                            else:
                                ket_qua = ai_translate(extracted_text, "ko2vi", user_api_key)
                                st.write("**Nghĩa Việt:**")
                                st.info(ket_qua)
                        else:
                            st.warning("Ảnh quá mờ hoặc dính nền phức tạp, máy không đọc được chữ.")
                    except Exception as e:
                        st.error(f"Lỗi hệ thống: {e}")