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
        residual = x
        x = self.conv1(x)
        x = self.bn1(x)
        x = F.relu(x)
        x = self.conv2(x)
        x = self.bn2(x)
        x = x + residual
        x = F.relu(x)
        return x

# =========================================================
# NETWORK
# =========================================================

class AlphaZeroNet(nn.Module):
    def __init__(self):
        super().__init__()
        channels = 128

        self.input_conv = nn.Conv2d(
            INPUT_CHANNELS,
            channels,
            kernel_size=3,
            padding=1,
            bias=False
        )
        self.input_bn = nn.BatchNorm2d(channels)

        self.res_blocks = nn.Sequential(
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels),
            ResidualBlock(channels)
        )

        # POLICY HEAD
        self.policy_conv = nn.Conv2d(
            channels,
            2,
            kernel_size=1,
            bias=False
        )
        self.policy_bn = nn.BatchNorm2d(2)
        self.policy_fc = nn.Linear(
            2 * BOARD_SIZE * BOARD_SIZE,
            BOARD_SIZE * BOARD_SIZE
        )

        # VALUE HEAD
        self.value_conv = nn.Conv2d(
            channels,
            1,
            kernel_size=1,
            bias=False
        )
        self.value_bn = nn.BatchNorm2d(1)
        self.value_fc1 = nn.Linear(
            BOARD_SIZE * BOARD_SIZE,
            256
        )
        self.value_fc2 = nn.Linear(
            256,
            1
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

        # VALUE
        v = self.value_conv(x)
        v = self.value_bn(v)
        v = F.relu(v)
        v = v.view(v.size(0), -1)
        v = self.value_fc1(v)
        v = F.relu(v)
        v = self.value_fc2(v)
        v = torch.tanh(v)

        return p, v.squeeze(1)

# =========================================================
# ENCODE BOARD
# =========================================================

def encode_board(grid, current_player):
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
    def __init__(self, player, opponent=None, time_limit=3.0, model_path="alphazero_gomoku_best.pth"):
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
        
        self.model = AlphaZeroNet().to(DEVICE)
        
        # Tìm đường dẫn tuyệt đối cho model nếu cần
        if not os.path.exists(model_path):
            dir_path = os.path.dirname(os.path.abspath(__file__))
            local_path = os.path.join(dir_path, "alphazero_gomoku_best.pth")
            if os.path.exists(local_path):
                model_path = local_path

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
            policy_logits, _ = self.model(state)

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