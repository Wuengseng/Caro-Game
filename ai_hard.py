import math
import random
import os
import torch
import torch.nn as nn
import numpy as np

# ================= NETWORK =================
class Net(nn.Module):
    def __init__(self, board_size):
        super().__init__()
        self.board_size = board_size

        self.conv = nn.Sequential(
            nn.Conv2d(2, 64, 3, padding=1),
            nn.ReLU(),
            nn.Conv2d(64, 64, 3, padding=1),
            nn.ReLU()
        )

        self.policy_head = nn.Sequential(
            nn.Conv2d(64, 2, 1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(2 * board_size * board_size, board_size * board_size)
        )

        self.value_head = nn.Sequential(
            nn.Conv2d(64, 1, 1),
            nn.ReLU(),
            nn.Flatten(),
            nn.Linear(board_size * board_size, 64),
            nn.ReLU(),
            nn.Linear(64, 1),
            nn.Tanh()
        )

    def forward(self, x):
        x = self.conv(x)
        policy = self.policy_head(x)
        value = self.value_head(x)
        return policy, value

# ================= ENCODE =================
def encode_board(board, player):
    grid = np.array(board.grid)

    state = np.zeros((2, board.size, board.size), dtype=np.float32)
    state[0] = (grid == player)
    state[1] = (grid != 0) & (grid != player)

    return torch.from_numpy(state).unsqueeze(0)

# ================= HELPER =================
def get_nearby_moves(board, radius=1):
    size = board.size
    grid = board.grid
    moves = set()

    for r in range(size):
        for c in range(size):
            if grid[r][c] != 0:
                for dr in range(-radius, radius+1):
                    for dc in range(-radius, radius+1):
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                            moves.add((nr, nc))

    if not moves:
        return [(size//2, size//2)]
    return list(moves)

# ================= NODE =================
class Node:
    def __init__(self, board, player, parent=None, prior=0):
        self.board = board
        self.player = player
        self.parent = parent
        self.prior = prior

        self.children = {}
        self.visits = 0
        self.value_sum = 0

    def value(self):
        return self.value_sum / self.visits if self.visits > 0 else 0

# ================= MCTS =================
class MCTS:
    def __init__(self, net, simulations=40, c_puct=1.2):
        self.net = net
        self.simulations = simulations
        self.c_puct = c_puct

    def search(self, root):
        for _ in range(self.simulations):
            node = root
            path = [node]

            # Selection
            while node.children:
                best_score = -1e9
                best_move = None

                for move, child in node.children.items():
                    u = self.c_puct * child.prior * math.sqrt(node.visits + 1) / (1 + child.visits)
                    score = child.value() + u

                    if score > best_score:
                        best_score = score
                        best_move = move

                node = node.children[best_move]
                path.append(node)

            # Evaluate
            if node.board.check_win(3 - node.player):
                value = -1
            elif node.board.is_full():
                value = 0
            else:
                with torch.no_grad():
                    state = encode_board(node.board, node.player)
                    policy, value = self.net(state)

                policy = torch.softmax(policy, dim=1)[0].cpu().numpy()

                moves = get_nearby_moves(node.board)

                for (r, c) in moves:
                    idx = r * node.board.size + c
                    p = policy[idx]

                    new_board = node.board.copy()
                    new_board.make_move(r, c, node.player)

                    node.children[(r, c)] = Node(
                        new_board,
                        3 - node.player,
                        node,
                        p
                    )

                value = value.item()

            # Backprop
            for n in reversed(path):
                n.visits += 1
                n.value_sum += value
                value = -value

    def get_policy(self, root):
        moves = list(root.children.keys())
        visits = np.array([root.children[m].visits for m in moves], dtype=np.float32)

        probs = visits / (np.sum(visits) + 1e-8)
        return moves, probs

# ================= AI FOR GAME =================
class AIHard:
    def __init__(self, player, opponent, time_limit=3.0):
        self.player = player
        self.opponent = opponent
        self.time_limit = time_limit
        
        self.board_size = 19
        self.net = Net(self.board_size)
        
        if os.path.exists("model.pth"):
            self.net.load_state_dict(torch.load("model.pth", map_location='cpu'))
        self.net.eval()

    def get_best_move(self, board):
        # Tối ưu nước đi đầu tiên để tránh MCTS chạy lâu
        if len(board.get_empty_cells()) == board.size * board.size:
            return (board.size//2, board.size//2)

        root = Node(board.copy(), self.player)
        mcts = MCTS(self.net, simulations=50)

        with torch.no_grad():
            mcts.search(root)

        moves, probs = mcts.get_policy(root)

        if not moves:
            empty = board.get_empty_cells()
            return random.choice(empty) if empty else None

        return moves[np.argmax(probs)]