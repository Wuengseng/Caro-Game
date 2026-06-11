import os
import torch
import numpy as np
import torch.nn as nn
import torch.nn.functional as F

# =========================================================
# CONFIG
# =========================================================

BOARD_SIZE = 15
INPUT_CHANNELS = 4
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# =========================================================
# RESIDUAL BLOCK
# =========================================================

class ResidualBlock(nn.Module):
    """
    Khối thặng dư (Residual Block):
    Lõi của mạng, giúp AI 'nhìn' ra các mẫu hình cờ (ví dụ: cờ bí, cờ mở, nước đôi).
    Sử dụng Skip Connection (x = x + residual) để tránh hiện tượng quên kiến thức
    khi mạng học quá sâu (Vanishing Gradient).
    """
    def __init__(self, channels):
        super().__init__()
        self.conv1 = nn.Conv2d(
            channels,
            channels,
            kernel_size=3,
            padding=1,
            bias=False
        )
        self.bn1 = nn.BatchNorm2d(channels)
        self.conv2 = nn.Conv2d(
            channels,
            channels,
            kernel_size=3,
            padding=1,
            bias=False
        )
        self.bn2 = nn.BatchNorm2d(channels)

    def forward(self, x):
        # 1. Lưu lại bản gốc của dữ liệu (Skip Connection)
        # Giống như việc ghi nhớ 'kiến thức nền' trước khi học kiến thức mới
        residual = x
        
        # 2. Xử lý qua lớp bộ lọc thứ nhất (conv1)
        x = self.conv1(x)
        x = self.bn1(x)        # Chuẩn hóa dữ liệu
        x = F.relu(x)          # Lọc bỏ số âm (chỉ giữ lại tín hiệu tích cực)
        
        # 3. Xử lý qua lớp bộ lọc thứ hai (conv2)
        x = self.conv2(x)
        x = self.bn2(x)
        
        # 4. TRỌNG TÂM: Cộng gộp kiến thức cũ và mới (Residual Addition)
        # AI không vứt bỏ dữ liệu gốc đi, mà lấy cái mới phân tích được (+) cộng chồng lên cái cũ.
        # Nhờ vậy, AI có tư duy sâu đến mấy cũng không bị 'mất gốc' (Vanishing Gradient)
        x = x + residual
        
        # 5. Kích hoạt bước cuối
        x = F.relu(x)
        return x

# =========================================================
# NETWORK
# =========================================================

class ImitationNet(nn.Module):
    """
    Mạng Neural học bắt chước (Imitation Learning).
    Mục tiêu: Nhìn vào bàn cờ (đầu vào) và chỉ ra nước đi tốt nhất y hệt như AI chuyên gia.
    """
    def __init__(self):
        super().__init__()
        channels = 256 # Số kênh (bộ lọc) để quét bàn cờ

        # 1. KHỐI ĐẦU VÀO (Input Block): Giống như 'võng mạc' của mắt
        # Nhận ma trận 4 lớp (channels) của bàn cờ và phân tích các đặc điểm thô ban đầu
        self.input_conv = nn.Conv2d(
            INPUT_CHANNELS,
            channels,
            kernel_size=3, # Quét từng vùng 3x3 ô cờ
            padding=1,     # Giữ nguyên kích thước bàn cờ
            bias=False
        )
        self.input_bn = nn.BatchNorm2d(channels) # Chuẩn hóa để mạng học nhanh hơn

        # 2. KHỐI TƯ DUY (Body - Residual Blocks): Giống như 'não bộ'
        # 6 khối nối tiếp nhau giúp AI hiểu được các thế trận phức tạp từ đơn giản
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

        # 3. KHỐI ĐẦU RA (Policy Head): 'Người ra quyết định'
        # Nén kết quả tư duy từ 128 kênh xuống còn 2 kênh, sau đó dũi phẳng ra (flatten)
        # để biến thành 225 điểm số tương ứng với 225 ô (15x15) trên bàn cờ.
        self.policy_conv = nn.Conv2d(
            channels,
            2,
            kernel_size=1,
            bias=False
        )
        self.policy_bn = nn.BatchNorm2d(2)
        self.policy_fc = nn.Linear(
            2 * BOARD_SIZE * BOARD_SIZE, # 2 kênh * 15 * 15
            BOARD_SIZE * BOARD_SIZE      # Đầu ra: 225 giá trị (xác suất đi vào ô)
        )

    def forward(self, x):
        x = self.input_conv(x)
        x = self.input_bn(x)
        x = F.relu(x)

        x = self.res_blocks(x)

        # POLICY
        p = self.policy_conv(x)
        p = self.policy_bn(p)
        p = F.relu(p)
        p = p.view(p.size(0), -1)
        p = self.policy_fc(p)

        return p

# =========================================================
# ENCODE BOARD: Chuyển đổi bàn cờ thành đầu vào cho mạng Neural
# =========================================================

def encode_board(grid, current_player):
    """
    AI không nhìn bàn cờ như con người. Ta phải tách bàn cờ thành 4 'bản đồ' (planes):
    1. Bản đồ quân ta (player_plane): Ô nào có quân ta thì bằng 1, còn lại 0.
    2. Bản đồ quân địch (opponent_plane): Ô nào có quân địch thì bằng 1, còn lại 0.
    3. Bản đồ lượt đi (turn_plane): Toàn số 1 hoặc 0 để AI biết màu quân mình đang cầm.
    4. Bản đồ ô trống (legal_plane): Ô nào trống thì bằng 1 (cho AI biết các nước hợp lệ).
    """
    player_plane = (grid == current_player).astype(np.float32)
    opponent_plane = (grid == (3 - current_player)).astype(np.float32)
    turn_plane = np.full(
        (BOARD_SIZE, BOARD_SIZE),
        current_player - 1,
        dtype=np.float32
    )
    legal_plane = (grid == 0).astype(np.float32)

    return np.stack([
        player_plane,
        opponent_plane,
        turn_plane,
        legal_plane
    ])

# =========================================================
# AI CLASS TO IMPORT
# =========================================================

class AIHard:
    def __init__(self, player, opponent=None, time_limit=3.0, model_path="alphazero_gomoku_imitation.pth"):
        """
        Khởi tạo AI
        :param player: Người chơi của AI (vd: 1 hoặc 2)
        :param opponent: Đối thủ của AI
        :param time_limit: Giới hạn thời gian (không dùng trong pure policy, nhưng giữ lại cho tương thích)
        :param model_path: Đường dẫn tới file model trained (.pth)
        """
        self.player = player
        self.opponent = opponent if opponent is not None else (3 - player)
        self.time_limit = time_limit
        
        self.model = ImitationNet().to(DEVICE)
        
        # Thử tìm file imitation trước, nếu không có thì dùng file best cũ
        dir_path = os.path.dirname(os.path.abspath(__file__))
        
        if not os.path.exists(model_path):
            paths_to_check = [
                os.path.join(dir_path, "models", "alphazero_gomoku_imitation.pth"),
                os.path.join(dir_path, "models", "alphazero_gomoku_best.pth"),
                os.path.join(dir_path, "models", "alphazero_gomoku_best (1).pth"),
                os.path.join(dir_path, "alphazero_gomoku_imitation.pth"),
                os.path.join(dir_path, "alphazero_gomoku_best.pth")
            ]
            for p in paths_to_check:
                if os.path.exists(p):
                    model_path = p
                    break

        # Tải mô hình
        if os.path.exists(model_path):
            checkpoint = torch.load(model_path, map_location=DEVICE)
            if "model_state_dict" in checkpoint:
                self.model.load_state_dict(checkpoint["model_state_dict"])
            else:
                self.model.load_state_dict(checkpoint)
            print(f"[AIHard] AlphaZero model loaded from {model_path}")
        else:
            print(f"[AIHard] Warning: Model file {model_path} not found. Using untrained model.")

        self.model.eval()

    def get_best_move(self, board):
        """
        Tính toán nước đi tốt nhất dựa trên policy network
        :param board: Object board từ game chính (cần có thuộc tính grid hoặc là mảng 2 chiều)
        """
        # Lấy mảng 2D từ board
        if hasattr(board, 'grid'):
            grid = np.array(board.grid)
        else:
            grid = np.array(board)

        state = encode_board(grid, self.player)

        state = torch.tensor(
            state,
            dtype=torch.float32
        ).unsqueeze(0).to(DEVICE)

        with torch.inference_mode():
            policy_logits = self.model(state)

        policy_logits = policy_logits[0]

        # MASK ILLEGAL MOVES
        legal_mask = (grid.flatten() == 0)
        
        if not np.any(legal_mask):
            return None # Không còn nước đi

        policy_logits = policy_logits.masked_fill(
            torch.tensor(~legal_mask, device=DEVICE),
            -1e9
        )

        probs = F.softmax(policy_logits, dim=0).cpu().numpy()

        move_idx = np.argmax(probs)

        r = int(move_idx // BOARD_SIZE)
        c = int(move_idx % BOARD_SIZE)

        return r, c