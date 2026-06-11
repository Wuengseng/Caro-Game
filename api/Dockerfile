# 1. Khai báo môi trường gốc: Dùng Python 3.11 phiên bản siêu nhẹ (slim)
FROM python:3.11-slim

# Cài đặt một số thư viện hệ thống cần thiết (để chạy numpy/torch nếu cần)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 2. Tạo một thư mục ảo tên là /app bên trong Container để chứa code
WORKDIR /app

# 3. Copy file cấu hình thư viện vào trước
COPY requirements.txt .

# 4. Cài đặt các thư viện (fastapi, uvicorn, numpy, torch...)
# --no-cache-dir giúp file Docker nhẹ hơn vì không lưu cache cài đặt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ mã nguồn API từ máy tính vào thư mục /app trong Container
COPY . .

# 6. Mở cửa số 8000 để Frontend có thể giao tiếp được
EXPOSE 8000

# 7. Lệnh sẽ được tự động chạy khi Container khởi động
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
