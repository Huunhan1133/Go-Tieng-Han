import streamlit as st
import google.generativeai as genai
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

# --- HÀM TÌM AI THÔNG MINH ---
def get_best_model(api_key):
    genai.configure(api_key=api_key)
    available_models = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
    
    # Ưu tiên bản flash vì tốc độ cao và có gói miễn phí tốt
    for m in available_models:
        if 'flash' in m.lower():
            return m
            
    for m in available_models:
        if 'pro' not in m.lower():
            return m
            
    if available_models:
        return available_models[0]
    return 'models/gemini-1.5-flash'

# --- GIAO DIỆN WEB ---
st.set_page_config(page_title="Công Cụ Dịch Thuật AI", layout="wide") 

try:
    user_api_key = st.secrets["GEMINI_API_KEY"]
except:
    user_api_key = None

st.title("🇰🇷 Công Cụ Dịch Đa Năng Tích Hợp AI")
st.write("Sử dụng não bộ Trí tuệ Nhân tạo Google Gemini để quét ảnh và dịch thuật!")

if not user_api_key:
    st.error("⚠️ Hệ thống chưa tìm thấy API Key! Hãy vào phần Settings -> Secrets trên Streamlit Cloud để cấu hình biến GEMINI_API_KEY nhé.")

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
        if tu_nhap and user_api_key:
            with st.spinner('AI đang suy nghĩ...'):
                try:
                    best_model_name = get_best_model(user_api_key)
                    model = genai.GenerativeModel(best_model_name)
                    
                    if "Lấy cách gõ phím" in che_do:
                        prompt = f"Dịch câu sau sang tiếng Hàn, dùng văn phong game MMORPG cổ điển. Chỉ in kết quả dịch: '{tu_nhap}'"
                        ket_qua = model.generate_content(prompt).text.strip()
                        st.success(f"Dịch thành công! (Model: {best_model_name})")
                        st.info(ket_qua)
                        st.code(hangul_to_qwerty(ket_qua))
                    else:
                        prompt = f"Dịch câu tiếng Hàn sau sang tiếng Việt, chú ý các từ lóng và thuật ngữ. Chỉ in kết quả dịch: '{tu_nhap}'"
                        ket_qua = model.generate_content(prompt).text.strip()
                        st.success(f"Dịch thành công! (Model: {best_model_name})")
                        st.info(ket_qua)
                except Exception as e:
                    st.error(f"Lỗi AI: {e}")
        elif not tu_nhap: 
            st.warning("Bạn chưa nhập từ nào!")

with col2:
    st.subheader("🖼️ Dịch từ Hình ảnh (AI Vision)")
    paste_result = paste_image_button(label="📋 Bấm để Dán ảnh", background_color="#FF4B4B")
    image_data = paste_result.image_data

    if image_data is not None:
        st.image(image_data, caption="Ảnh bạn dán", use_container_width=True)
        
        if st.button("AI Quét Ảnh & Dịch", type="primary"):
            if user_api_key:
                with st.spinner('AI đang dùng MẮT THẦN nhìn vào ảnh...'):
                    try:
                        best_model_name = get_best_model(user_api_key)
                        model = genai.GenerativeModel(best_model_name)
                        
                        # CHUẨN HÓA VÀ NÉN ẢNH ĐỂ TRÁNH LỖI ĐỊNH DẠNG / QUOTA TOKENS
                        img_input = image_data.convert("RGB")
                        img_input.thumbnail((1024, 1024)) # Giới hạn cạnh dài nhất tối đa 1024px để giảm tải tokens
                        
                        if "Lấy cách gõ phím" in che_do:
                            prompt = "Hãy đọc chữ tiếng Việt trong bức ảnh này và dịch nó sang tiếng Hàn. Trình bày làm 2 dòng:\nChữ gốc: [chữ đọc được]\nDịch sang Hàn: [chữ dịch]"
                        else:
                            prompt = "Hãy nhìn vào bức ảnh này, đây là ảnh từ game MMORPG cổ điển với phông chữ dạng pixel vỡ hạt. Hãy đọc chữ tiếng Hàn/Nhật trong ảnh và dịch sang tiếng Việt sát nghĩa nhất. Trình bày làm 2 dòng:\nChữ gốc máy đọc được: [chữ đọc được]\nNghĩa Tiếng Việt: [chữ dịch]"
                        
                        response = model.generate_content([prompt, img_input])
                        
                        st.success(f"Mắt Thần đã phân tích xong! (Model: {best_model_name})")
                        st.write(response.text)
                        
                        if "Lấy cách gõ phím" in che_do:
                            lines = response.text.split('\n')
                            for line in lines:
                                if "Dịch sang Hàn:" in line:
                                    korean_text = line.replace("Dịch sang Hàn:", "").strip()
                                    st.write("**Cách gõ phím:**")
                                    st.code(hangul_to_qwerty(korean_text))
                                    
                    except Exception as e:
                        # Hiện thông báo lỗi chi tiết để dễ debug
                        st.error(f"❌ Lỗi xử lý ảnh từ hệ thống: {e}")