# 🎯 Caro (Gomoku) AI Master - Web Application

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/PyTorch-EE4C2C?style=for-the-badge&logo=pytorch&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=FastAPI&logoColor=white" />
  <img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB" />
  <img src="https://img.shields.io/badge/Vite-B73BFE?style=for-the-badge&logo=vite&logoColor=FFD62E" />
  <img src="https://img.shields.io/badge/Docker-2CA5E0?style=for-the-badge&logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white" />
  <img src="https://img.shields.io/badge/Terraform-7B42BC?style=for-the-badge&logo=terraform&logoColor=white" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=github-actions&logoColor=white" />
</p>

Dự án này là một hệ thống Web hoàn chỉnh áp dụng **Trí tuệ nhân tạo (AI)** vào trò chơi cờ Caro (Gomoku) kinh điển. Mục tiêu của dự án là xây dựng một hệ thống từ thuật toán Tìm kiếm đối kháng (Minimax) truyền thống cho đến **Mô hình Học Sâu (Deep Learning)** hiện đại. Đồng thời, toàn bộ ứng dụng được phát triển với tư duy quy mô thực tế: đóng gói bằng Docker, triển khai qua Kubernetes (K8s), quản lý hạ tầng bằng Terraform và CI/CD hoàn chỉnh với GitHub Actions.

---

## 🚀 Tính năng & Các cấp độ AI

Hệ thống cung cấp một Giao diện Web hiện đại, mượt mà (SPA) cùng với 3 cấp độ khó riêng biệt, được thiết kế để bao quát từ các phương pháp AI truyền thống (Heuristic, Search) cho đến hiện đại (Deep Learning):

### 1. 🟢 Cấp độ Dễ (Easy - Greedy Heuristic Search)

- **Mã nguồn:** `api/ai_easy.py`
- **Thuật toán:** Tìm kiếm tham lam (Greedy Search) kết hợp Đánh giá Heuristic cục bộ.
- **Chi tiết hoạt động:**
  - Ở cấp độ này, AI không tính toán trước các nước đi tương lai (Look-ahead = 0). Thay vào đó, nó phản ứng ngay lập tức dựa trên trạng thái hiện tại của bàn cờ.
  - Hàm đánh giá (Heuristic) sẽ quét bàn cờ và gán điểm số cao cho các mẫu hình đe dọa (ví dụ: đối thủ có 3 hoặc 4 quân liên tiếp) để ưu tiên chặn đứng ngay lập tức. Ngược lại, nếu AI phát hiện cơ hội chiến thắng (có 4 quân), nó sẽ ưu tiên đánh nước quyết định.
  - **Đặc điểm:** Tốc độ phản hồi tức thì (`O(N)` với N là số ô trống xung quanh). Nếu không có tình huống nguy cấp, AI sẽ chọn ngẫu nhiên một ô trống lân cận các quân cờ đã có. Điều này mang lại lối chơi mang tính ngẫu hứng, có phần "ngây ngô" nhưng đôi khi cũng tạo ra nước đi khó đoán, dễ bị lừa bởi các bẫy cờ cơ bản.

### 2. 🟡 Cấp độ Vừa (Medium - Minimax & Alpha-Beta Pruning)

- **Mã nguồn:** `api/ai_medium.py`
- **Thuật toán:** Cây Tìm kiếm Đối kháng (Adversarial Search) với thuật toán Minimax, tối ưu hóa bằng Cắt tỉa Alpha-Beta (Alpha-Beta Pruning) với độ sâu là 5.
- **Chi tiết hoạt động:**
  - AI sẽ mô phỏng các diễn biến tiếp theo của trận đấu bằng cách xây dựng một cây trò chơi đa nhánh (độ sâu thường từ 3-5 nước đi tương lai). Nó luân phiên đóng vai trò là "Max" (tìm nước đi tốt nhất cho mình) và "Min" (mô phỏng nước đi tối ưu của người chơi để chống lại).
  - **Hàm đánh giá (Evaluation Function):** Hàm sẽ quét toàn bộ bàn cờ và chấm điểm các cấu trúc (ví dụ: chuỗi 2, chuỗi 3 mở hai đầu, chuỗi 4 bị chặn một đầu) để đánh giá tổng thể "vị thế" của bàn cờ.
  - **Tối ưu Alpha-Beta:** Giúp AI bỏ qua những nhánh tính toán vô ích (những nhánh mà đối thủ chắc chắn sẽ không cho phép xảy ra), từ đó giảm thiểu số lần tính toán theo cấp số nhân và cho phép AI duyệt cây sâu hơn trong thời gian ngắn.
  - **Đặc điểm:** Lối đánh nguy hiểm, chặt chẽ và "thích gài bẫy". Nhờ khả năng nhìn trước nhiều bước, AI thường xuyên tạo ra các đòn tấn công đôi (Fork - ví dụ: tạo ra hai chuỗi 3 cùng lúc hoặc đe dọa chuỗi 4 và chuỗi 3) khiến người chơi không thể phòng thủ một lúc hai đầu.

### 3. 🔴 Cấp độ Khó (Hard - Deep Imitation Learning)

- **Mã nguồn:** `api/ai_hard.py`
- **Thuật toán:** Mạng Nơ-ron Tích chập sâu (Deep Convolutional Neural Networks) với kiến trúc ResNet (Residual Network), huấn luyện bằng Học Bắt Chước (Imitation Learning).
- **Chi tiết hoạt động:**
  - **Biểu diễn Dữ liệu (State Representation):** Bàn cờ Caro được mã hóa dưới dạng một Tensor không gian nhiều kênh (Multi-channel Tensor) – biểu diễn vị trí quân ta, quân địch, và lượt đi hiện tại. Đây đóng vai trò là "hình ảnh" đầu vào để Mạng Nơ-ron phân tích.
  - **Kiến trúc ResNet:** Sử dụng mô hình mạng Nơ-ron sâu với nhiều khối Residual Blocks. Các kết nối "skip-connections" giúp thông tin truyền sâu vào mạng mà không bị lỗi biến mất đạo hàm (vanishing gradient problem). Kiến trúc này giúp AI học được các đặc trưng không gian (spatial features) phức tạp và tương quan trên bàn cờ rộng lớn.
  - **Pipeline Huấn luyện (Training):** Để tránh thời gian học thử-sai quá lâu của Reinforcement Learning truyền thống, AI được train trên một _Dataset Khổng Lồ_ gồm hàng trăm nghìn ván cờ. Tập dữ liệu này được tạo ra bằng cách cho các thuật toán Minimax cấp độ cực cao (độ sâu = 5) tự chơi với nhau. Mạng Neural sẽ học cách "bắt chước" trực giác (Policy) của chuyên gia Minimax.
  - **Đặc điểm:** Do toàn bộ kiến thức đã được nén vào "trọng số" của mô hình trong quá trình Train, quá trình suy luận (Inference) cực kỳ chớp nhoáng vì không cần xây dựng Cây tìm kiếm cồng kềnh. AI mang một tư duy "trực giác" giống con người: có khả năng nhận diện pattern trận địa rộng, chuyển đổi uyển chuyển giữa phòng thủ và tấn công mà không bị gò bó bởi các hệ đếm điểm cứng nhắc do con người lập trình thủ công.

---

## 📂 Cấu trúc dự án (Project Structure)

Dự án được chia thành các phân hệ rõ ràng (Microservices architecture & Infrastructure as Code):

```text
Caro_Project/
├── api/                    # 🧠 Backend API (FastAPI) & Trí tuệ nhân tạo (PyTorch)
│   ├── models/             # Thư mục chứa các file weights của model (.pth)
│   ├── dataset/            # Nơi lưu trữ dữ liệu các ván cờ (logs)
│   ├── ai_easy.py          # Logic AI cấp độ Dễ
│   ├── ai_medium.py        # Logic AI cấp độ Vừa (Minimax)
│   ├── ai_hard.py          # Logic AI cấp độ Khó (ResNet)
│   ├── board.py            # Logic cốt lõi của bàn cờ và trạng thái trò chơi
│   ├── main.py             # Entrypoint của FastAPI
│   ├── generate_dataset*.py# Script tạo dữ liệu huấn luyện (Local & Kaggle)
│   ├── train_imitation*.py # Script huấn luyện mô hình (Local & Kaggle)
│   └── Dockerfile          # Dockerfile cho Backend
├── web/                    # 💻 Frontend UI (React + Vite)
│   ├── src/                # Mã nguồn React UI (Components, Hooks, Services)
│   ├── public/             # Tài nguyên tĩnh
│   ├── package.json        # Dependencies của Frontend
│   └── Dockerfile          # Dockerfile cho Frontend (Nginx)
├── infra/                  # ☁️ Infrastructure as Code (Terraform)
│   ├── modules/            # Các Terraform Modules cấu hình Cloud (VPC, EKS, etc.)
│   ├── main.tf             # Cấu hình chính của Terraform
│   └── provider.tf         # Cấu hình Cloud Provider (AWS/GCP/Azure)
├── k8s/                    # 🚢 Kubernetes Deployment Manifests
│   ├── api/                # Cấu hình Pods/Services/Ingress cho Backend
│   └── web/                # Cấu hình Pods/Services/Ingress cho Frontend
├── .github/                # ⚙️ CI/CD Pipelines (GitHub Actions)
├── DESIGN.md               # Phân tích thiết kế của hệ thống
└── docker-compose.yml      # Cấu hình chạy giả lập toàn bộ hệ thống ở Local
```

---

## 🏗 Kiến trúc Hệ thống & DevOps

- **Web Frontend:** Giao diện SPA hiện đại xây dựng trên nền **React** và build bằng **Vite**, cung cấp UX mượt mà.
- **API Backend:** Dịch vụ API mạnh mẽ viết bằng **FastAPI** (Python), phụ trách giao tiếp với UI và xử lý tính toán mô hình AI (qua **PyTorch**).
- **Hạ tầng (Infrastructure):**
  - Quản lý hạ tầng trên Cloud hoàn toàn tự động thông qua **Terraform** (`infra/`).
  - Triển khai ứng dụng trên cụm Container Orchestration bằng **Kubernetes** (`k8s/`).
- **CI/CD Pipeline:** Tích hợp **GitHub Actions** để tự động:
  - Lint, Test code frontend và backend.
  - Build Docker Images và Push lên Docker Hub/ECR.
  - Tự động Deploy phiên bản mới lên cụm K8s.

---

## 📦 Hướng dẫn Cài đặt & Chạy Game (Local)

Với Docker Compose, bạn có thể chạy toàn bộ Frontend và Backend ở môi trường local cực kì dễ dàng mà không cần cài đặt Python hay Node.js.

**Yêu cầu:** Đã cài đặt [Docker Desktop](https://www.docker.com/products/docker-desktop/).

1. **Clone mã nguồn:**

   ```bash
   git clone https://github.com/<your-username>/Caro_Project.git
   cd Caro_Project
   ```

2. **Khởi chạy Hệ thống:**

   ```bash
   docker-compose up --build
   ```

3. **Trải nghiệm Game:**
   Mở trình duyệt web của bạn và truy cập vào: 👉 **http://localhost** _(Frontend)_
   - API Docs (Swagger) của backend chạy tại: **http://localhost:8000/docs**

> Để tắt Server, ấn `Ctrl + C` trên Terminal hoặc gõ `docker-compose down`.

---

## 🧠 Hướng dẫn Huấn luyện AI (Imitation Learning Pipeline)

Nếu bạn muốn tạo ra một "Não" AI riêng tư mạnh mẽ hơn thông qua nền tảng Kaggle:

1. **Sinh Dữ liệu (Generate Dataset):**
   - Đẩy file `api/generate_dataset_kaggle.py` lên Kaggle Notebook.
   - Script này sẽ cho các AI Minimax tự đánh với nhau để thu thập hàng trăm nghìn dữ liệu mẫu các nước đi tối ưu.
2. **Làm sạch Dữ liệu:**
   - (Tuỳ chọn) Chạy `api/clean_dataset.py` để loại bỏ các ván cờ trùng lặp hoặc nhiễu.
3. **Huấn luyện Mô hình (Train):**
   - Chạy `api/train_imitation_kaggle.py` trên Notebook có GPU. Quá trình huấn luyện sử dụng ResNet và PyTorch để AI học cách "bắt chước" các nước đi khôn ngoan của Minimax.
   - Khi hoàn thành, tải file trọng số (ví dụ: `alphazero_gomoku_imitation.pth`) về.
4. **Tích hợp vào Web:**
   - Thả file `.pth` đó vào thư mục `api/models/`. Cập nhật file cấu hình và chạy lại Docker Compose.

---

## ☁️ Triển khai lên Môi trường Production (Cloud & Kubernetes)

1. **Khởi tạo Hạ tầng (Terraform):**

   ```bash
   cd infra
   terraform init
   terraform apply -auto-approve
   ```

   _(Thao tác này sẽ tạo cụm Kubernetes và các resource liên quan trên Cloud)._

2. **Triển khai Ứng dụng (K8s):**
   ```bash
   cd ../k8s
   kubectl apply -f api/
   kubectl apply -f web/
   ```
   _(Toàn bộ các bản cập nhật sau đó có thể được tự động hoá thông qua cấu hình trong thư mục `.github/workflows`)._

---

_Dự án minh họa cách áp dụng Trí Tuệ Nhân Tạo (AI) vào Game, kết hợp với các tiêu chuẩn thiết kế kiến trúc và tự động hóa cao nhất của DevOps._
