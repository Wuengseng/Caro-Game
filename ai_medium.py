import math

class AIMedium:
    def __init__(self, player, opponent, depth=5):
        self.player = player
        self.opponent = opponent
        self.depth = depth

    def evaluate_board(self, board):
        # A simple aggressive heuristic: 
        # Evaluate lines for player (positive) and opponent (negative).
        # Aggressive: weight player's attacks slightly more than opponent's.
        score = 0
        score += self.evaluate_lines(board, self.player) * 1.2 # Aggressive factor
        score -= self.evaluate_lines(board, self.opponent)
        return score

    def evaluate_lines(self, board, player):
        score = 0
        grid = board.grid
        size = board.size
        
        # Directions: right, down, diagonal-down-right, diagonal-down-left
        directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        
        for r in range(size):
            for c in range(size):
                if grid[r][c] == player:
                    for dr, dc in directions:
                        consecutive = 1
                        open_ends = 0
                        
                        # Check forward
                        nr, nc = r + dr, c + dc
                        while 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == player:
                            consecutive += 1
                            nr += dr
                            nc += dc
                        if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                            open_ends += 1
                            
                        # Check backward
                        nr, nc = r - dr, c - dc
                        if 0 <= nr < size and 0 <= nc < size and grid[nr][nc] == 0:
                            open_ends += 1
                            
                        # Score patterns
                        if consecutive >= 5:
                            return 1000000
                        elif consecutive == 4:
                            if open_ends == 2:
                                score += 100000
                            elif open_ends == 1:
                                score += 10000
                        elif consecutive == 3:
                            if open_ends == 2:
                                score += 5000
                            elif open_ends == 1:
                                score += 500
                        elif consecutive == 2:
                            if open_ends == 2:
                                score += 100
        return score

    def get_candidate_moves(self, board, player):
        empty_cells = board.get_empty_cells()
        # Sort empty cells based on a shallow evaluation to improve alpha-beta pruning
        # For performance, only keep top N moves
        MAX_CANDIDATES = 20
        
        moves_with_scores = []
        for r, c in empty_cells:
            # Shallow eval
            board.make_move(r, c, player)
            if board.check_win(player):
                board.undo_move(r, c)
                return [(r, c)] # Immediate win
            
            score = self.evaluate_board(board)
            board.undo_move(r, c)
            moves_with_scores.append((score, (r, c)))
            
        # Sort descending for the maximizing player
        moves_with_scores.sort(key=lambda x: x[0], reverse=True)
        return [move for score, move in moves_with_scores[:MAX_CANDIDATES]]

    def minimax(self, board, depth, alpha, beta, is_maximizing):
        if board.check_win(self.player):
            return 1000000 + depth
        if board.check_win(self.opponent):
            return -1000000 - depth
        if depth == 0 or board.is_full():
            return self.evaluate_board(board)

        if is_maximizing:
            max_eval = -math.inf
            candidates = self.get_candidate_moves(board, self.player)
            for r, c in candidates:
                board.make_move(r, c, self.player)
                ev = self.minimax(board, depth - 1, alpha, beta, False)
                board.undo_move(r, c)
                max_eval = max(max_eval, ev)
                alpha = max(alpha, ev)
                if beta <= alpha:
                    break
            return max_eval
        else:
            min_eval = math.inf
            candidates = self.get_candidate_moves(board, self.opponent)
            for r, c in candidates:
                board.make_move(r, c, self.opponent)
                ev = self.minimax(board, depth - 1, alpha, beta, True)
                board.undo_move(r, c)
                min_eval = min(min_eval, ev)
                beta = min(beta, ev)
                if beta <= alpha:
                    break
            return min_eval

    def get_best_move(self, board):
        best_score = -math.inf
        best_move = None
        
        candidates = self.get_candidate_moves(board, self.player)
        if not candidates:
            return None
            
        # Optimization: Check for immediate block
        for r, c in candidates:
            board.make_move(r, c, self.opponent)
            if board.check_win(self.opponent):
                board.undo_move(r, c)
                return (r, c)
            board.undo_move(r, c)

        for r, c in candidates:
            board.make_move(r, c, self.player)
            score = self.minimax(board, self.depth - 1, -math.inf, math.inf, False)
            board.undo_move(r, c)
            
            if score > best_score:
                best_score = score
                best_move = (r, c)
                
        # Fallback if no best move found
        if best_move == None and candidates:
            best_move = candidates[0]
            
        return best_move
