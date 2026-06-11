import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader, random_split
import os
import sys
import glob

import torch.nn.functional as F

# Fix encoding for Windows console (bỏ qua nếu chạy trên Kaggle/Jupyter)
if hasattr(sys.stdout, 'reconfigure'):
    if sys.stdout.encoding != 'utf-8':
        sys.stdout.reconfigure(encoding='utf-8')

# =========================================================
# NHÚNG TRỰC TIẾP MODEL ĐỂ TRÁNH LỖI KHI CHẠY KAGGLE
# =========================================================
BOARD_SIZE = 15
INPUT_CHANNELS = 4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class ResidualBlock(nn.Module):
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(channels, channels, kernel_size=3, padding=1, bias=False)
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        residual = x
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = x + residual
        x = F.relu(x)
        return x

class ImitationNet(nn.Module):
    def __init__(self):
        super().__init__()
        channels = 256
        
        self.input_conv = nn.Conv2d(INPUT_CHANNELS, channels, kernel_size=3, padding=1, bias=False)
        self.input_bn = nn.BatchNorm2d(channels)
        
        self.res_blocks = nn.Sequential(
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels)
        )
        self.policy_conv = nn.Conv2d(channels, 2, kernel_size=1, bias=False)
        self.policy_bn = nn.BatchNorm2d(2)
        self.policy_fc = nn.Linear(2 * BOARD_SIZE * BOARD_SIZE, BOARD_SIZE * BOARD_SIZE)

    def forward(self, x):
        x = self.input_conv(x)
        x = self.input_bn(x)
        x = F.relu(x)
        x = self.res_blocks(x)
        p = self.policy_conv(x)
        p = self.policy_bn(p)
        p = F.relu(p)
        p = p.view(p.size(0), -1)
        p = self.policy_fc(p)
        return p

def load_datasets(dataset_dir):
    """Load and concatenate datasets from a directory."""
    if not os.path.exists(dataset_dir):
        print(f"Lỗi: Thư mục '{dataset_dir}' không tồn tại.")
        return None, None
        
    # Tìm tất cả các file trong thư mục (bao gồm các file như 1, 2, 3...)
    files = [os.path.join(dataset_dir, f) for f in os.listdir(dataset_dir) if os.path.isfile(os.path.join(dataset_dir, f))]
    
    if not files:
        print(f"Không tìm thấy file dataset nào trong '{dataset_dir}'.")
        return None, None
        
    print(f"Tìm thấy {len(files)} file: {files}")
    
    all_states = []
    all_policies = []
    
    # Sắp xếp để load theo thứ tự 1, 2, 3...
    for f in sorted(files):
        print(f"Đang load {f}...")
        try:
            # map_location='cpu' khi load ban đầu để tránh tràn VRAM nếu data lớn
            data = torch.load(f, map_location='cpu')
            all_states.append(data['states'])
            all_policies.append(data['policies'])
        except Exception as e:
            print(f"Lỗi khi đọc file {f}: {e}")
            
    if not all_states:
        return None, None
        
    print("Đang gộp các dataset lại...")
    combined_states = torch.cat(all_states, dim=0)
    combined_policies = torch.cat(all_policies, dim=0)
    
    print(f"Kích thước sau khi gộp: States: {combined_states.shape}, Policies: {combined_policies.shape}")
    return combined_states, combined_policies

def train_imitation_kaggle(dataset_dir="/kaggle/input/datasets/wuengsengg/expert-dataset-chunk", epochs=30, batch_size=128, save_path="alphazero_gomoku_best.pth", val_split=0.2, test_split=0.1):
    print(f"Sử dụng thiết bị: {DEVICE}")
    print(f"Đang tìm kiếm dataset tại thư mục: {dataset_dir}")
    states, policies = load_datasets(dataset_dir)
    
    if states is None:
        print("Huấn luyện bị huỷ do không tìm thấy dữ liệu.")
        return

    dataset = TensorDataset(states, policies)
    
    # Chia tập train, validation và test
    total_size = len(dataset)
    val_size = int(total_size * val_split)
    test_size = int(total_size * test_split)
    train_size = total_size - val_size - test_size
    
    train_dataset, val_dataset, test_dataset = random_split(dataset, [train_size, val_size, test_size])
    
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    print(f"Tổng số mẫu: {total_size}")
    print(f"Tập Train: {train_size} mẫu ({len(train_loader)} batches)")
    print(f"Tập Validation: {val_size} mẫu ({len(val_loader)} batches)")
    print(f"Tập Test: {test_size} mẫu ({len(test_loader)} batches)")
    
    # Khởi tạo model
    model = ImitationNet().to(DEVICE)
    
    # Load trọng số cũ nếu muốn tiếp tục train
    if os.path.exists(save_path):
        try:
            model.load_state_dict(torch.load(save_path, map_location=DEVICE))
            print(f"Đã load model cũ từ {save_path} để tiếp tục train.")
        except Exception as e:
            print(f"Không thể load model cũ {save_path}, sẽ train từ đầu. Lỗi: {e}")
            
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    
    best_val_acc = 0.0
    
    print("Bắt đầu huấn luyện...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_states, batch_policies in train_loader:
            batch_states = batch_states.to(DEVICE)
            batch_policies = batch_policies.to(DEVICE)
            
            optimizer.zero_grad()
            
            # Forward pass
            pred_policies = model(batch_states)
            
            # Tính Policy Loss (Cross Entropy)
            log_preds = torch.log_softmax(pred_policies, dim=1)
            loss = -torch.mean(torch.sum(batch_policies * log_preds, dim=1))
            
            # Backward pass
            loss.backward()
            optimizer.step()
            
            total_loss += loss.item()
            
        avg_train_loss = total_loss / len(train_loader)
        
        # ==========================================
        # ĐÁNH GIÁ TRÊN TẬP TEST (VALIDATION)
        # ==========================================
        model.eval()
        val_loss = 0
        correct_preds = 0
        
        with torch.no_grad():
            for batch_states, batch_policies in val_loader:
                batch_states = batch_states.to(DEVICE)
                batch_policies = batch_policies.to(DEVICE)
                
                pred_policies = model(batch_states)
                
                # Tính Loss
                log_preds = torch.log_softmax(pred_policies, dim=1)
                loss = -torch.mean(torch.sum(batch_policies * log_preds, dim=1))
                val_loss += loss.item()
                
                # Tính độ chính xác (Accuracy)
                # Nước đi AI dự đoán (điểm cao nhất) có khớp với chuyên gia không
                pred_moves = torch.argmax(pred_policies, dim=1)
                target_moves = torch.argmax(batch_policies, dim=1)
                correct_preds += (pred_moves == target_moves).sum().item()
                
        avg_val_loss = val_loss / len(val_loader)
        val_accuracy = correct_preds / val_size * 100
        
        print(f"Epoch {epoch+1:02d}/{epochs} | Train Loss: {avg_train_loss:.4f} | Val Loss: {avg_val_loss:.4f} | Val Acc: {val_accuracy:.2f}%")
        
        # ==========================================
        # LƯU MÔ HÌNH TỐT NHẤT (BEST CHECKPOINT)
        # ==========================================
        if val_accuracy > best_val_acc:
            best_val_acc = val_accuracy
            torch.save(model.state_dict(), save_path)
            print(f"    --> Đã lưu mô hình tốt nhất! (Val Acc mới: {best_val_acc:.2f}%)")
            
    print(f"\nHuấn luyện hoàn tất. Đã lưu mô hình xuất sắc nhất tại {save_path} với Val Acc = {best_val_acc:.2f}%.")

    # ==========================================
    # ĐÁNH GIÁ TRÊN TẬP TEST CUỐI CÙNG
    # ==========================================
    if test_size > 0:
        print("\nĐang đánh giá mô hình trên tập Test...")
        model.eval()
        test_loss = 0
        correct_test_preds = 0
        
        with torch.no_grad():
            for batch_states, batch_policies in test_loader:
                batch_states = batch_states.to(DEVICE)
                batch_policies = batch_policies.to(DEVICE)
                
                pred_policies = model(batch_states)
                
                log_preds = torch.log_softmax(pred_policies, dim=1)
                loss = -torch.mean(torch.sum(batch_policies * log_preds, dim=1))
                test_loss += loss.item()
                
                pred_moves = torch.argmax(pred_policies, dim=1)
                target_moves = torch.argmax(batch_policies, dim=1)
                correct_test_preds += (pred_moves == target_moves).sum().item()
                
        avg_test_loss = test_loss / len(test_loader)
        test_accuracy = correct_test_preds / test_size * 100
        print(f"KẾT QUẢ TEST CUỐI CÙNG | Test Loss: {avg_test_loss:.4f} | Test Acc: {test_accuracy:.2f}%\n")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Train Imitation Learning with multiple datasets")
    parser.add_argument("--dir", type=str, default="/kaggle/input/datasets/wuengsengg/expert-dataset-chunk", help="Đường dẫn tới thư mục chứa các file dataset (Vd: /kaggle/input/...)")
    parser.add_argument("--epochs", type=int, default=30, help="Số epochs")
    parser.add_argument("--batch_size", type=int, default=128, help="Kích thước batch")
    parser.add_argument("--val_split", type=float, default=0.2, help="Tỉ lệ tập Validation (ví dụ 0.2 là 20%)")
    parser.add_argument("--test_split", type=float, default=0.1, help="Tỉ lệ tập Test (ví dụ 0.1 là 10%)")
    parser.add_argument("--save", type=str, default="alphazero_gomoku_best.pth", help="Đường dẫn lưu model")
    
    # Dùng parse_known_args để không bị lỗi với các tham số ẩn của Jupyter/Kaggle (như -f)
    args, unknown = parser.parse_known_args()
    
    train_imitation_kaggle(
        dataset_dir=args.dir,
        epochs=args.epochs,
        batch_size=args.batch_size,
        save_path=args.save,
        val_split=args.val_split,
        test_split=args.test_split
    )
