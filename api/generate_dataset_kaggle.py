import os
import sys
import math
import random
import numpy as np
import torch

BOARD_SIZE = 15

# =========================================================
# BOARD CLASS (Trích từ api/board.py)
# =========================================================
class Board:
    def __init__(self, size=BOARD_SIZE):
        self.size = size
        # 0: Empty, 1: Player 1 (X), 2: Player 2 (O)
        self.grid = np.zeros((self.size, self.size), dtype=int)
        self.last_move = None

    def is_valid_move(self, r, c):
        return 0 <= r < self.size and 0 <= c < self.size and self.grid[r][c] == 0

    def make_move(self, r, c, player):
        if self.is_valid_move(r, c):
            self.grid[r][c] = player
            self.last_move = (r, c)
            return True
        return False

    def undo_move(self, r, c):
        self.grid[r][c] = 0

    def get_empty_cells(self):
        rows, cols = np.where(self.grid != 0)
        if len(rows) == 0:
            return [(self.size // 2, self.size // 2)]

        min_r, max_r = max(0, np.min(rows) - 2), min(self.size - 1, np.max(rows) + 2)
        min_c, max_c = max(0, np.min(cols) - 2), min(self.size - 1, np.max(cols) + 2)
        
        empty_cells = []
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.grid[r][c] == 0:
                    empty_cells.append((r, c))
                    
        return empty_cells

    def check_win(self, player):
        for r in range(self.size):
            for c in range(self.size - 4):
                if np.all(self.grid[r, c:c+5] == player):
                    return True
        for r in range(self.size - 4):
            for c in range(self.size):
                if np.all(self.grid[r:r+5, c] == player):
                    return True
        for r in range(self.size - 4):
            for c in range(self.size - 4):
                if all(self.grid[r+i, c+i] == player for i in range(5)):
                    return True
        for r in range(4, self.size):
            for c in range(self.size - 4):
                if all(self.grid[r-i, c+i] == player for i in range(5)):
                    return True
        return False

    def is_full(self):
        return not np.any(self.grid == 0)

    def copy(self):
        new_board = Board(self.size)
        new_board.grid = np.copy(self.grid)
        new_board.last_move = self.last_move
        return new_board

# =========================================================
# AI MEDIUM CLASS (Trích từ api/ai_medium.py)
# =========================================================
class AIMedium:
    def __init__(self, player, opponent, depth=5):
        self.player = player
        self.opponent = opponent
        self.depth = depth

        self.MAX_CANDIDATES = 14
        self.SEARCH_RADIUS = 2

        self.ttable = {}

    def board_hash(self, board):
        return tuple(map(tuple, board.grid))

    def check_win_from_move(self, board, r, c, player):
        directions = [(1,0), (0,1), (1,1), (1,-1)]
        for dr, dc in directions:
            count = 1
            nr, nc = r + dr, c + dc
            while 0 <= nr < board.size and 0 <= nc < board.size and board.grid[nr][nc] == player:
                count += 1
                nr += dr
                nc += dc
            nr, nc = r - dr, c - dc
            while 0 <= nr < board.size and 0 <= nc < board.size and board.grid[nr][nc] == player:
                count += 1
                nr -= dr
                nc -= dc
            if count >= 5:
                return True
        return False

    def evaluate_board(self, board):
        my_score = self.evaluate_lines(board, self.player)
        opp_score = self.evaluate_lines(board, self.opponent)
        return my_score - opp_score * 1.15

    def evaluate_lines(self, board, player):
        score = 0
        grid = board.grid
        size = board.size
        directions = [(0,1), (1,0), (1,1), (1,-1)]

        for r in range(size):
            for c in range(size):
                if grid[r][c] != player:
                    continue
                for dr, dc in directions:
                    pr, pc = r - dr, c - dc
                    if 0 <= pr < size and 0 <= pc < size:
                        if grid[pr][pc] == player:
                            continue
                    consecutive = 1
                    open_ends = 0
                    nr, nc = r + dr, c + dc
                    while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
                        consecutive += 1
                        nr += dr
                        nc += dc
                    if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                        open_ends += 1
                    if 0 <= pr < size and 0 <= pc < size and grid[pr][pc] == 0:
                        open_ends += 1
                    score += self.pattern_score(consecutive, open_ends)
        return score

    def pattern_score(self, consecutive, open_ends):
        if consecutive >= 5: return 10000000
        if consecutive == 4:
            if open_ends == 2: return 1000000
            if open_ends == 1: return 100000
        if consecutive == 3:
            if open_ends == 2: return 50000
            if open_ends == 1: return 5000
        if consecutive == 2:
            if open_ends == 2: return 3000
            if open_ends == 1: return 300
        return 0

    def evaluate_local_move(self, grid, size, r, c, player):
        grid[r][c] = player
        score = 0
        directions = [(0,1), (1,0), (1,1), (1,-1)]
        for dr, dc in directions:
            consecutive = 1
            open_ends = 0
            nr, nc = r + dr, c + dc
            while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
                consecutive += 1
                nr += dr
                nc += dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                open_ends += 1
            nr, nc = r - dr, c - dc
            while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
                consecutive += 1
                nr -= dr
                nc -= dc
            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                open_ends += 1
            score += self.pattern_score(consecutive, open_ends)
        grid[r][c] = 0
        return score

    def get_nearby_moves(self, board):
        grid = board.grid
        size = board.size
        moves = set()
        has_stone = False
        for r in range(size):
            for c in range(size):
                if grid[r][c] != 0:
                    has_stone = True
                    for dr in range(-self.SEARCH_RADIUS, self.SEARCH_RADIUS + 1):
                        for dc in range(-self.SEARCH_RADIUS, self.SEARCH_RADIUS + 1):
                            nr = r + dr
                            nc = c + dc
                            if 0 <= nr < size and 0 <= nc < size:
                                if grid[nr][nc] == 0:
                                    moves.add((nr, nc))
        if not has_stone:
            center = size // 2
            return [(center, center)]
        return list(moves)

    def get_candidate_moves(self, board, player):
        moves = self.get_nearby_moves(board)
        if not moves:
            return []
        grid = board.grid
        size = board.size
        scored_moves = []
        opponent = self.opponent if player == self.player else self.player
        for r, c in moves:
            attack = self.evaluate_local_move(grid, size, r, c, player)
            if attack >= 10000000:
                return [(r, c)]
            defend = self.evaluate_local_move(grid, size, r, c, opponent)
            score = attack + defend * 1.2
            center_dist = abs(r - size//2) + abs(c - size//2)
            score -= center_dist * 2
            scored_moves.append((score, (r, c)))
        scored_moves.sort(reverse=True, key=lambda x: x[0])
        return [move for _, move in scored_moves[:self.MAX_CANDIDATES]]

    def minimax(self, board, depth, alpha, beta, maximizing, last_move=None):
        board_key = (self.board_hash(board), depth, maximizing)
        if board_key in self.ttable:
            return self.ttable[board_key]

        if last_move is not None:
            r, c, player = last_move
            if self.check_win_from_move(board, r, c, player):
                if player == self.player:
                    return 10000000 + depth
                else:
                    return -10000000 - depth

        if depth == 0 or board.is_full():
            return self.evaluate_board(board)

        if maximizing:
            max_eval = -math.inf
            candidates = self.get_candidate_moves(board, self.player)
            for r, c in candidates:
                board.make_move(r, c, self.player)
                value = self.minimax(board, depth - 1, alpha, beta, False, (r, c, self.player))
                board.undo_move(r, c)
                max_eval = max(max_eval, value)
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            self.ttable[board_key] = max_eval
            return max_eval
        else:
            min_eval = math.inf
            candidates = self.get_candidate_moves(board, self.opponent)
            for r, c in candidates:
                board.make_move(r, c, self.opponent)
                value = self.minimax(board, depth - 1, alpha, beta, True, (r, c, self.opponent))
                board.undo_move(r, c)
                min_eval = min(min_eval, value)
                beta = min(beta, value)
                if beta <= alpha:
                    break
            self.ttable[board_key] = min_eval
            return min_eval

    def get_best_move(self, board):
        self.ttable.clear()
        best_score = -math.inf
        best_move = None
        candidates = self.get_candidate_moves(board, self.player)
        if not candidates:
            return None
        random.shuffle(candidates)
        for r, c in candidates:
            board.make_move(r, c, self.player)
            score = self.minimax(board, self.depth - 1, -math.inf, math.inf, False, (r, c, self.player))
            board.undo_move(r, c)
            if score > best_score:
                best_score = score
                best_move = (r, c)
        return best_move

# =========================================================
# ENCODE BOARD (Trích từ api/ai_hard.py)
# =========================================================
def encode_board(grid, current_player):
    player_plane = (grid == current_player).astype(np.float32)
    opponent_plane = (grid == (3 - current_player)).astype(np.float32)
    turn_plane = np.full((BOARD_SIZE, BOARD_SIZE), current_player - 1, dtype=np.float32)
    legal_plane = (grid == 0).astype(np.float32)
    return np.stack([player_plane, opponent_plane, turn_plane, legal_plane])

# =========================================================
# DATASET GENERATION LOGIC (Tối ưu cho Kaggle / RAM lớn)
# =========================================================
def random_opening(board):
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

def augment_data(state, policy):
    augmented = []
    for k in range(4):
        # 1. Rotate
        s = np.rot90(state, k=k, axes=(1, 2)).copy()
        board_policy = policy.reshape(BOARD_SIZE, BOARD_SIZE)
        p = np.rot90(board_policy, k=k).flatten().copy()
        augmented.append((s, p))
        
        # 2. Flip
        fs = np.flip(s, axis=2).copy()
        board_p = p.reshape(BOARD_SIZE, BOARD_SIZE)
        fp = np.fliplr(board_p).flatten().copy()
        augmented.append((fs, fp))
        
    return augmented

def generate_games(num_games=1000, depth=4, chunk_size=200, save_dir="."):
    """
    Hàm sinh dataset, chia thành nhiều chunks để tránh lỗi Out-Of-Memory (OOM) trên Kaggle
    """
    print(f"Bắt đầu tạo dataset với {num_games} ván cờ, độ sâu AI={depth}...")
    
    dataset = [] 
    chunk_index = 1
    total_samples = 0
    
    for i in range(num_games):
        board = Board(BOARD_SIZE)
        ai1 = AIMedium(player=1, opponent=2, depth=depth)
        ai2 = AIMedium(player=2, opponent=1, depth=depth)
        
        current_player = random_opening(board)
        
        print(f"Đang chơi ván {i+1}/{num_games}...", end="", flush=True)
        
        moves_count = 0
        while not board.is_full():
            ai = ai1 if current_player == 1 else ai2
            grid = np.array(board.grid)
            state = encode_board(grid, current_player)
            
            best_move = ai.get_best_move(board)
            if best_move is None:
                break
                
            r, c = best_move
            
            policy = np.zeros(BOARD_SIZE * BOARD_SIZE, dtype=np.float32)
            policy[r * BOARD_SIZE + c] = 1.0
            
            augmented = augment_data(state, policy)
            dataset.extend(augmented)
            
            board.make_move(r, c, current_player)
            moves_count += 1
            
            if board.check_win(current_player) or board.is_full():
                break
                
            current_player = 3 - current_player
            
        print(f" Xong ({moves_count} nước chuyên gia -> {moves_count * 8} mẫu data).")
        
        # LƯU CHUNKS ĐỂ TRÁNH TRÀN RAM
        if (i + 1) % chunk_size == 0 or (i + 1) == num_games:
            if len(dataset) > 0:
                states = torch.tensor(np.array([item[0] for item in dataset]), dtype=torch.float32)
                policies = torch.tensor(np.array([item[1] for item in dataset]), dtype=torch.float32)
                
                save_path = os.path.join(save_dir, f"expert_dataset_chunk_{chunk_index}.pt")
                torch.save({
                    'states': states,
                    'policies': policies
                }, save_path)
                
                print(f"\n--- Đã lưu {len(dataset)} mẫu (Chunk {chunk_index}) vào {save_path} ---")
                total_samples += len(dataset)
                
                # Reset dataset để giải phóng bộ nhớ RAM
                dataset = []
                chunk_index += 1

    print(f"\nHoàn thành! Tổng số mẫu (samples) thu thập được: {total_samples}")

if __name__ == "__main__":
    # Trên Kaggle, bạn có thể chạy bằng lệnh: python generate_dataset_kaggle.py
    # Bạn có thể tăng num_games lên (vd: 5000, 10000). 
    # Mỗi chunk_size=200 ván sẽ tạo ra 1 file dataset (đỡ lo mất dữ liệu nếu bị đứt mạng hoặc timeout)
    generate_games(num_games=2000, depth=4, chunk_size=500, save_dir=".")
