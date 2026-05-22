from deep_translator import GoogleTranslator

# 1. Bảng ánh xạ Jamo sang bàn phím QWERTY (kiểu Dubeolsik)
CHOSEONG_MAP = ['r', 'R', 's', 'e', 'E', 'f', 'a', 'q', 'Q', 't', 'T', 'd', 'w', 'W', 'c', 'z', 'x', 'v', 'g']
JUNGSEONG_MAP = ['k', 'o', 'i', 'O', 'j', 'p', 'u', 'P', 'h', 'hk', 'ho', 'hl', 'y', 'n', 'nj', 'np', 'nl', 'b', 'm', 'ml', 'l']
JONGSEONG_MAP = ['', 'r', 'R', 'rt', 's', 'sw', 'sg', 'e', 'f', 'fr', 'fa', 'fq', 'ft', 'fx', 'fv', 'fg', 'a', 'q', 'qt', 't', 'T', 'd', 'w', 'c', 'z', 'x', 'v', 'g']

def translate_vi_to_ko(text):
    """
    Sử dụng deep-translator (nhân Google Translate) để dịch trực tiếp
    """
    try:
        # source='vi' (Tiếng Việt), target='ko' (Tiếng Hàn)
        translator = GoogleTranslator(source='vi', target='ko')
        result = translator.translate(text)
        return result
    except Exception as e:
        print(f"Lỗi khi kết nối với Google Translate: {e}")
        return None

def hangul_to_qwerty(korean_text):
    """
    Tách âm Hangul và chuyển sang phím gõ QWERTY
    """
    result = ""
    for char in korean_text:
        code = ord(char)
        if 0xAC00 <= code <= 0xD7A3:
            index = code - 0xAC00
            cho = index // 588
            jung = (index % 588) // 28
            jong = index % 28

            result += CHOSEONG_MAP[cho]
            result += JUNGSEONG_MAP[jung]
            result += JONGSEONG_MAP[jong]
        else:
            result += char 
    return result

# --- CHƯƠNG TRÌNH CHÍNH ---
print("=== PHẦN MỀM GÕ TIẾNG HÀN TỪ TIẾNG VIỆT (Bản Full Google Translate) ===")
while True:
    tu_viet = input("\nNhập câu tiếng Việt (hoặc gõ 'thoát' để dừng): ")
    
    if tu_viet.lower() == 'thoát':
        print("Cảm ơn bạn đã sử dụng!")
        break
        
    if not tu_viet.strip():
        continue
        
    print("Đang dịch...")
    tu_han = translate_vi_to_ko(tu_viet)

    if tu_han:
        chuoi_phim = hangul_to_qwerty(tu_han)
        print("--- KẾT QUẢ ---")
        print(f"Tiếng Hàn    : {tu_han}")
        print(f"Cách gõ phím : {chuoi_phim}")