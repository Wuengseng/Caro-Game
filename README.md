# 🎯 Caro (Gomoku) AI Master - Web Application

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
</p>

Dự án này là một hệ thống Web hoàn chỉnh áp dụng **Trí tuệ nhân tạo (AI)** vào trò chơi cờ Caro (Gomoku) kinh điển. Mục tiêu của dự án là xây dựng hệ thống AI từ thuật toán Tìm kiếm đối kháng (Minimax) truyền thống cho đến **Mô hình Học Sâu (Deep Learning)** hiện đại, đồng thời được đóng gói chuyên nghiệp bằng Docker và tích hợp CI/CD chuẩn DevOps.

---

## 🚀 Tính năng & Các cấp độ AI

Hệ thống cung cấp một Giao diện Web mượt mà, trực quan cùng 3 cấp độ khó:

1. 🟢 **Cấp độ Dễ (Easy):**
   - **Thuật toán:** Tìm kiếm tham lam (Greedy Heuristic Search).
   - **Đặc điểm:** Phản xạ nhanh. Ưu tiên chặn người chơi khi sắp thua hoặc đi nước quyết định để thắng. Nếu không, AI đánh ngẫu nhiên xung quanh khu vực có quân cờ.

2. 🟡 **Cấp độ Vừa (Medium):**
   - **Thuật toán:** Minimax kết hợp Cắt tỉa Alpha-Beta (Alpha-Beta Pruning).
   - **Đặc điểm:** AI có thể duyệt cây tìm kiếm để "nhìn xa" trước nhiều nước đi. Phong cách đánh mang thiên hướng tấn công dữ dội, liên tục gài bẫy (chuỗi 3, chuỗi 4) để tạo sức ép.

3. 🔴 **Cấp độ Khó (Hard - Deep Imitation Learning):**
   - **Thuật toán:** Mạng Nơ-ron Tích chập sâu (Deep CNN - ResNet Architecture).
   - **Cấu trúc Não AI:** Siêu khủng với **256 Channels** và **10 Residual Blocks**, sở hữu khoảng 50 triệu thông số (Parameters).
   - **Đặc điểm:** AI được huấn luyện theo phương pháp *Học Bắt chước (Imitation Learning)* từ hàng trăm nghìn ván cờ của Chuyên gia Minimax (Depth 4-5). Mạng Neural không dùng các phép tính heuristic cứng nhắc mà sẽ tự "nhìn" bàn cờ (4-channels input) để ra quyết định chính xác và nhanh chóng.

---

## 🏗 Kiến trúc Hệ thống (System Architecture)

Dự án được cấu trúc theo mô hình Microservices, bao gồm các thành phần:

- **Web Frontend:** Giao diện người dùng chạy trên trình duyệt (Cổng 80).
- **API Backend:** Viết bằng `FastAPI` (Python), chịu trách nhiệm xử lý logic và tính toán nước đi AI bằng `PyTorch` (Cổng 8000).
- **DevOps:** 
  - Đóng gói toàn bộ bằng `docker-compose`.
  - Quy trình tự động hóa (CI/CD) được cấu hình bằng **GitHub Actions**. Tự động Build, Test và Push các Docker Image lên **Docker Hub** mỗi khi có Code mới ở nhánh `main`.
- **Kaggle AI Training:** Toàn bộ quá trình tạo Dataset và Train Neural Network nặng nề được tách biệt sang môi trường GPU của Kaggle.

---

## 📦 Hướng dẫn Cài đặt & Chạy Game (Local)

Vì hệ thống đã được Đóng gói hoàn toàn bằng Docker, bạn không cần phải cài đặt Python hay thư viện lằng nhằng nào trên máy tính.

**Yêu cầu duy nhất:** Máy tính đã cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. **Clone mã nguồn:**
   ```bash
   git clone https://github.com/<your-username>/Caro_Project.git
   cd Caro_Project
   ```

2. **Khởi chạy Hệ thống:**
   Mở Terminal / PowerShell và gõ:
   ```bash
   docker-compose up --build
   ```

3. **Chơi Game:**
   Mở trình duyệt web của bạn và truy cập vào: 👉 **http://localhost**

> **Lưu ý:** Nếu bạn muốn tắt Server, hãy bấm `Ctrl + C` trên Terminal hoặc mở tab Terminal mới gõ lệnh `docker-compose down`.

---

## 🧠 Hướng dẫn Huấn luyện "Não" AI (Kaggle)

Nếu bạn muốn AI ở chế độ Hard mạnh hơn nữa, bạn có thể tự mình huấn luyện lại mô hình thông qua nền tảng Kaggle miễn phí:

1. **Sinh Dữ liệu (Generate Dataset):**
   - Đưa file `api/generate_dataset_kaggle.py` lên Kaggle Notebook.
   - Chạy script để thuật toán Minimax tạo ra hàng trăm ngàn mẫu ván cờ (Nên chia nhỏ thành nhiều Chunk để tránh tràn RAM).
2. **Huấn luyện Mô hình (Train):**
   - Chạy file `api/train_imitation_kaggle.py` trên Notebook có bật GPU (T4 hoặc P100).
   - Đợi quá trình huấn luyện kết thúc, tải file trọng số (`.pth` nặng khoảng ~50MB) về máy.
3. **Cập nhật Não mới cho Web:**
   - Đổi tên file vừa tải về thành `alphazero_gomoku_imitation.pth` (hoặc giữ nguyên tên).
   - Thả file đó vào thư mục `api/models/` trong dự án.
   - Chạy lại lệnh `docker-compose up --build`, web sẽ tự động nhận diện Não mới!

---

_Dự án phục vụ cho Đồ án môn học Trí tuệ Nhân tạo & Thực hành CI/CD DevOps._
