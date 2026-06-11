import torch
import numpy as np
import os
import sys
import random

# Fix encoding for Windows console
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# Ensure api module can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.board import Board
from api.ai_medium import AIMedium
from api.ai_hard import encode_board, BOARD_SIZE

# =========================================================
# RANDOM OPENING
# =========================================================
def random_opening(board):
    """
    Đi ngẫu nhiên 3-5 nước đầu tiên xung quanh tâm (bán kính <= 2).
    Điều này ép AI gặp nhiều thế cờ khởi đầu đa dạng.
    """
    num_moves = random.randint(3, 5)
    current_player = 1
    center = BOARD_SIZE // 2
    
    moves_made = 0
    while moves_made < num_moves:
        r = center + random.randint(-2, 2)
        c = center + random.randint(-2, 2)
        
        if board.is_valid_move(r, c):
            board.make_move(r, c, current_player)
            current_player = 3 - current_player
            moves_made += 1
            
    return current_player

# =========================================================
# DATA AUGMENTATION
# =========================================================
def augment_data(state, policy):
    """
    Nhân bản dữ liệu bằng cách xoay (90, 180, 270) và lật gương.
    1 ván cờ -> 8 ván cờ hợp lệ.
    """
    augmented = []
    
    for k in range(4):
        # 1. Xoay k * 90 độ
        # Xoay state trên trục 1 và 2 (Bỏ qua trục 0 là channel)
        s = np.rot90(state, k=k, axes=(1, 2)).copy()
        
        # Xoay policy
        board_policy = policy.reshape(BOARD_SIZE, BOARD_SIZE)
        p = np.rot90(board_policy, k=k).flatten().copy()
        
        augmented.append((s, p))
        
        # 2. Lật gương theo chiều dọc (cột)
        fs = np.flip(s, axis=2).copy()
        
        # Lật policy tương ứng
        board_p = p.reshape(BOARD_SIZE, BOARD_SIZE)
        fp = np.fliplr(board_p).flatten().copy()
        
        augmented.append((fs, fp))
        
    return augmented

# =========================================================
# GENERATOR
# =========================================================
def generate_games(num_games=100, depth=3, save_path="expert_dataset.pt"):
    print(f"Bắt đầu tạo dataset với {num_games} ván cờ, độ sâu AI={depth}...")
    
    dataset = [] # List of tuples: (state, policy)
    
    for i in range(num_games):
        board = Board(BOARD_SIZE)
        ai1 = AIMedium(player=1, opponent=2, depth=depth)
        ai2 = AIMedium(player=2, opponent=1, depth=depth)
        
        # 1. KHAI CUỘC NGẪU NHIÊN
        current_player = random_opening(board)
        
        print(f"Đang chơi ván {i+1}/{num_games}...", end="", flush=True)
        
        moves_count = 0
        while not board.is_full():
            ai = ai1 if current_player == 1 else ai2
            
            # Lấy state
            grid = np.array(board.grid)
            state = encode_board(grid, current_player)
            
            # Lấy nước đi tốt nhất từ Expert
            best_move = ai.get_best_move(board)
            if best_move is None:
                break # Không còn nước đi
                
            r, c = best_move
            
            # Tạo target policy (One-hot vector)
            policy = np.zeros(BOARD_SIZE * BOARD_SIZE, dtype=np.float32)
            policy[r * BOARD_SIZE + c] = 1.0
            
            # 2. NHÂN BẢN DỮ LIỆU (DATA AUGMENTATION)
            # Tạo ra 8 state-policy từ 1 bước đi gốc
            augmented = augment_data(state, policy)
            dataset.extend(augmented)
            
            # Thực hiện nước đi
            board.make_move(r, c, current_player)
            moves_count += 1
            
            # Kiểm tra kết thúc
            if board.check_win(current_player) or board.is_full():
                break
                
            current_player = 3 - current_player
            
        print(f" Xong ({moves_count} nước chuyên gia -> {moves_count * 8} mẫu data).")
            
    # Convert sang PyTorch tensors
    states = torch.tensor(np.array([item[0] for item in dataset]), dtype=torch.float32)
    policies = torch.tensor(np.array([item[1] for item in dataset]), dtype=torch.float32)
    
    print(f"\nTổng số mẫu data (states) thu thập được: {len(dataset)}")
    
    # Lưu file dataset
    torch.save({
        'states': states,
        'policies': policies
    }, save_path)
    print(f"Đã lưu dataset thành công vào {save_path}")

if __name__ == "__main__":
    # Để sử dụng thực tế, hãy chỉnh num_games=100
    generate_games(num_games=100, depth=3, save_path="expert_dataset.pt")
