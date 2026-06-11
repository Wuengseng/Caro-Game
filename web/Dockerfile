# === STAGE 1: Xây dựng (Build) ===
# Dùng môi trường Node.js siêu nhẹ để biên dịch code React/Vite
FROM node:22-alpine AS builder

# Tạo thư mục làm việc trong container
WORKDIR /app

# Cài đặt pnpm (vì dự án Caro của bạn đang dùng pnpm)
RUN npm install -g pnpm

# Copy danh sách thư viện vào trước để cài đặt
# (Làm bước này trước để Docker lưu cache, giúp build các lần sau cực nhanh)
COPY package.json pnpm-lock.yaml ./
RUN pnpm install

# Copy toàn bộ code Frontend từ máy tính vào container
COPY . .

# Chạy lệnh Build ra thư mục ./dist (chứa code HTML/JS/CSS đã nén tĩnh)
RUN pnpm build

# === STAGE 2: Triển khai (Deploy) ===
# Sau khi build xong, ta không cần Node.js nữa. Dùng Nginx làm web server cho nhẹ!
FROM nginx:alpine

# Xóa trang web rác mặc định của Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copy DUY NHẤT thư mục "dist" (thành quả build từ Stage 1) sang Nginx
# Việc này làm cho dung lượng Image cuối cùng giảm từ hàng GB xuống chỉ còn vài chục MB
COPY --from=builder /app/dist /usr/share/nginx/html

# Mở cổng 80 (cổng web tiêu chuẩn)
EXPOSE 80

# Khởi động máy chủ Nginx
CMD ["nginx", "-g", "daemon off;"]
