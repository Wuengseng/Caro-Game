import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
import os
import sys

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure api module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.ai_hard import ImitationNet, DEVICE

def train_imitation(dataset_path="expert_dataset.pt", epochs=20, batch_size=64, save_path="alphazero_gomoku_imitation.pth"):
    if not os.path.exists(dataset_path):
        print(f"Lỗi: Không tìm thấy file {dataset_path}. Hãy chạy generate_dataset.py trước.")
        return
        
    print(f"Đang load dataset từ {dataset_path}...")
    data = torch.load(dataset_path)
    
    states = data['states']
    policies = data['policies']
    
    dataset = TensorDataset(states, policies)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=True)
    
    print(f"Số lượng batch: {len(dataloader)}")
    
    # Khởi tạo model
    model = ImitationNet().to(DEVICE)
    
    # Load trọng số cũ nếu muốn fine-tune (tuỳ chọn)
    # old_model_path = "alphazero_gomoku_best.pth"
    # if os.path.exists(old_model_path):
    #     model.load_state_dict(torch.load(old_model_path, map_location=DEVICE))
    #     print(f"Đã load model cũ từ {old_model_path} để tiếp tục train.")
        
    optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)
    
    # Loss functions
    # Policy: Cross Entropy (bản chất là -sum(target * log_softmax(pred)))
    
    print("Bắt đầu huấn luyện...")
    for epoch in range(epochs):
        model.train()
        total_loss = 0
        
        for batch_states, batch_policies in dataloader:
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
            
        avg_loss = total_loss / len(dataloader)
        
        print(f"Epoch {epoch+1}/{epochs} | Loss: {avg_loss:.4f}")
        
    # Lưu model
    torch.save(model.state_dict(), save_path)
    print(f"Đã lưu mô hình huấn luyện vào {save_path}")

if __name__ == "__main__":
    train_imitation(dataset_path="expert_dataset.pt", epochs=20, batch_size=64, save_path="alphazero_gomoku_imitation.pth")
