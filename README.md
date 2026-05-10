# Đề tài: Xây dựng AI đa cấp độ cho trò chơi Caro sử dụng thuật toán Minimax và Monte Carlo Tree Search kết hợp Mạng Nơ-ron

Dự án này là một ứng dụng Trí tuệ nhân tạo (AI) vào trò chơi cờ Caro (Gomoku) kinh điển. Mục tiêu của dự án là xây dựng hệ thống AI với khả năng chơi cờ ở 3 cấp độ khác nhau, qua đó tìm hiểu và áp dụng từ những thuật toán Tìm kiếm đối kháng (Adversarial Search) cơ bản cho đến các mô hình hiện đại có sử dụng Mạng Nơ-ron (Neural Networks).

## 🚀 Tính năng & Các cấp độ AI

Game cung cấp giao diện đồ họa (GUI) hoàn chỉnh trực quan và 3 cấp độ khó dành cho người chơi:

1. **Cấp độ Dễ (Easy):**
   - **Thuật toán:** Tìm kiếm tham lam (Greedy Heuristic Search).
   - **Đặc điểm:** AI sẽ ưu tiên chặn người chơi nếu sắp thua hoặc giành chiến thắng ngay lập tức nếu có cơ hội. Nếu không, AI sẽ đánh ngẫu nhiên quanh các vùng có quân cờ để tạo cảm giác thực tế.

2. **Cấp độ Vừa (Medium):**
   - **Thuật toán:** Minimax kết hợp Cắt tỉa Alpha-Beta (Alpha-Beta Pruning).
   - **Đặc điểm:** AI có khả năng "nhìn xa" (duyệt cây) trước vài nước đi. Kết hợp với hàm đánh giá (Heuristic) mang thiên hướng tấn công dữ dội, AI sẽ chủ động gài thế cờ (chuỗi 3, chuỗi 4) gây sức ép liên tục lên người chơi.

3. **Cấp độ Khó (Hard - AlphaZero Style):**
   - **Thuật toán:** Monte Carlo Tree Search (MCTS) kết hợp với Mạng Nơ-ron Tích chập (Convolutional Neural Networks - PyTorch).
   - **Đặc điểm:** AI không sử dụng heuristic tĩnh cứng nhắc mà sẽ đánh giá nước đi (Policy) và tỷ lệ thắng (Value) thông qua mạng Deep Learning. Model này cần trải qua quá trình tự chơi (Self-play) để huấn luyện và nâng cao trình độ.

## 🛠 Công nghệ sử dụng

- **Ngôn ngữ:** Python 3
- **Giao diện (GUI):** Pygame
- **Toán học & Ma trận:** Numpy
- **Deep Learning / AI:** PyTorch (Dùng cho MCTS Neural Network)

## 📦 Hướng dẫn cài đặt và chạy game

**1. Cài đặt các thư viện cần thiết:**
Mở Terminal / Command Prompt trong thư mục dự án và chạy lệnh:

```bash
pip install -r requirements.txt
```

**2. Khởi chạy trò chơi:**
Để bắt đầu chơi, chạy lệnh sau:

```bash
python main.py
```

> **Lưu ý:** Khi chọn độ khó **Hard**, nếu máy tính chưa có file trọng số `model.pth` đã được huấn luyện, AI sẽ khởi tạo ngẫu nhiên và suy nghĩ tương đối ngô nghê. Bạn cần thực thi hàm training để AI học cách đánh.

## 🧠 Hướng dẫn huấn luyện AI (Dành cho cấp độ Hard)

Thuật toán ở cấp độ Hard yêu cầu Mạng Nơ-ron phải được huấn luyện. Bạn có thể kích hoạt quá trình tự học (Self-play) thông qua code huấn luyện (`train`). Sau nhiều vòng chơi, AI sẽ lưu trữ lại "kinh nghiệm" vào file `model.pth`. Tốc độ học phụ thuộc vào cấu hình máy tính (khuyến nghị chạy trên thiết bị có GPU).

---

_Dự án phục vụ cho đồ án môn học Trí tuệ nhân tạo._
