# Dùng hệ điều hành Linux siêu nhẹ có sẵn Python 3.10
FROM python:3.10-slim

# Tạo thư mục làm việc
WORKDIR /app

# Cài đặt phần mềm đọc ảnh Tesseract (Hàn, Việt)
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-kor \
    tesseract-ocr-vie \
    && rm -rf /var/lib/apt/lists/*

# Cài đặt các thư viện Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code của bạn vào máy chủ
COPY . .

# Lệnh khởi động trang web với cấu hình nới lỏng bảo mật để hiển thị giao diện
EXPOSE 8501
CMD ["streamlit", "run", "dich.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
