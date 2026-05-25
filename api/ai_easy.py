import math

class AIEasy:
    def __init__(self, player, opponent):
        self.player = player
        self.opponent = opponent

    # ================= HEURISTIC =================
    def evaluate_board(self, board):
        my_score = self.evaluate_player(board, self.player)
        opp_score = self.evaluate_player(board, self.opponent)
        
        # Phòng thủ mạnh hơn chút
        return my_score - opp_score * 1.2

    def evaluate_player(self, board, player):
        score = 0
        grid = board.grid
        size = board.size
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]

        for r in range(size):
            for c in range(size):
                if grid[r][c] != player:
                    continue

                for dr, dc in directions:
                    # Bỏ qua nếu không phải đầu chuỗi (Fix double count)
                    pr, pc = r - dr, c - dc
                    if 0 <= pr < size and 0 <= pc < size and grid[pr][pc] == player:
                        continue

                    consecutive = 0
                    open_ends = 0

                    # Đếm chiều dài chuỗi
                    nr, nc = r, c
                    while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
                        consecutive += 1
                        nr += dr
                        nc += dc

                    # Kiểm tra mở đầu/đuôi
                    if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                        open_ends += 1
                    if 0 <= pr < size and 0 <= pc < size and grid[pr][pc] == 0:
                        open_ends += 1

                    score += self.pattern_score(consecutive, open_ends)

        return score

    def pattern_score(self, consecutive, open_ends):
        if consecutive >= 5:
            return 1000000
            
        if consecutive == 4:
            if open_ends == 2:
                return 120000
            if open_ends == 1:
                return 15000
                
        if consecutive == 3:
            if open_ends == 2:
                return 8000
            if open_ends == 1:
                return 1000
                
        if consecutive == 2:
            if open_ends == 2:
                return 300
                
        return 0

    # ================= MOVE GENERATION =================
    def get_candidate_moves(self, board):
        size = board.size
        grid = board.grid
        moves = set()

        # Chỉ lấy ô gần quân đã đánh
        for r in range(size):
            for c in range(size):
                if grid[r][c] != 0:
                    for dr in range(-2, 3):
                        for dc in range(-2, 3):
                            nr, nc = r + dr, c + dc
                            if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                                moves.add((nr, nc))

        if not moves:
            return [(size // 2, size // 2)]
            
        return list(moves)

    # ================= GREEDY AI =================
    def get_best_move(self, board):
        best_score = -math.inf
        best_move = None
        candidates = self.get_candidate_moves(board)

        # 1. Win Immediately
        for r, c in candidates:
            board.make_move(r, c, self.player)
            if board.check_win(self.player):
                board.undo_move(r, c)
                return (r, c)
            board.undo_move(r, c)

        # 2. Block Opponent Win
        for r, c in candidates:
            board.make_move(r, c, self.opponent)
            if board.check_win(self.opponent):
                board.undo_move(r, c)
                return (r, c)
            board.undo_move(r, c)

        # 3. Greedy Heuristic
        for r, c in candidates:
            board.make_move(r, c, self.player)
            score = self.evaluate_board(board)
            board.undo_move(r, c)

            if score > best_score:
                best_score = score
                best_move = (r, c)

        return best_move