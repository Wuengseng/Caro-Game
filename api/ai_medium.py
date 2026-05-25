import math
import random

BOARD_SIZE = 15

class AIMedium:
    def __init__(self, player, opponent, depth=5):
        self.player = player
        self.opponent = opponent
        self.depth = depth

        self.MAX_CANDIDATES = 14
        self.SEARCH_RADIUS = 2

        self.ttable = {}

    # =========================================================
    # HASH
    # =========================================================
    def board_hash(self, board):
        return tuple(map(tuple, board.grid))

    # =========================================================
    # FAST WIN CHECK AROUND LAST MOVE
    # =========================================================
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

    # =========================================================
    # BOARD EVALUATION
    # =========================================================
    def evaluate_board(self, board):
        my_score = self.evaluate_lines(board, self.player)
        opp_score = self.evaluate_lines(board, self.opponent)

        return my_score - opp_score * 1.15

    # =========================================================
    # EVALUATE ALL LINES
    # =========================================================
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

                    # prevent double count
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

    # =========================================================
    # PATTERN SCORE
    # =========================================================
    def pattern_score(self, consecutive, open_ends):

        if consecutive >= 5:
            return 10000000

        if consecutive == 4:
            if open_ends == 2:
                return 1000000
            if open_ends == 1:
                return 100000

        if consecutive == 3:
            if open_ends == 2:
                return 50000
            if open_ends == 1:
                return 5000

        if consecutive == 2:
            if open_ends == 2:
                return 3000
            if open_ends == 1:
                return 300

        return 0

    # =========================================================
    # LOCAL MOVE EVALUATION
    # =========================================================
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

    # =========================================================
    # ONLY SEARCH NEAR EXISTING STONES
    # =========================================================
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

    # =========================================================
    # CANDIDATE MOVES
    # =========================================================
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

            # immediate win
            if attack >= 10000000:
                return [(r, c)]

            defend = self.evaluate_local_move(grid, size, r, c, opponent)

            score = attack + defend * 1.2

            # center bias
            center_dist = abs(r - size//2) + abs(c - size//2)
            score -= center_dist * 2

            scored_moves.append((score, (r, c)))

        scored_moves.sort(reverse=True, key=lambda x: x[0])

        return [move for _, move in scored_moves[:self.MAX_CANDIDATES]]

    # =========================================================
    # MINIMAX
    # =========================================================
    def minimax(self, board, depth, alpha, beta, maximizing, last_move=None):

        board_key = (self.board_hash(board), depth, maximizing)

        if board_key in self.ttable:
            return self.ttable[board_key]

        # terminal check
        if last_move is not None:

            r, c, player = last_move

            if self.check_win_from_move(board, r, c, player):

                if player == self.player:
                    return 10000000 + depth
                else:
                    return -10000000 - depth

        if depth == 0 or board.is_full():
            return self.evaluate_board(board)

        # =====================================================
        # MAX
        # =====================================================
        if maximizing:

            max_eval = -math.inf

            candidates = self.get_candidate_moves(board, self.player)

            for r, c in candidates:

                board.make_move(r, c, self.player)

                value = self.minimax(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    False,
                    (r, c, self.player)
                )

                board.undo_move(r, c)

                max_eval = max(max_eval, value)

                alpha = max(alpha, value)

                if beta <= alpha:
                    break

            self.ttable[board_key] = max_eval
            return max_eval

        # =====================================================
        # MIN
        # =====================================================
        else:

            min_eval = math.inf

            candidates = self.get_candidate_moves(board, self.opponent)

            for r, c in candidates:

                board.make_move(r, c, self.opponent)

                value = self.minimax(
                    board,
                    depth - 1,
                    alpha,
                    beta,
                    True,
                    (r, c, self.opponent)
                )

                board.undo_move(r, c)

                min_eval = min(min_eval, value)

                beta = min(beta, value)

                if beta <= alpha:
                    break

            self.ttable[board_key] = min_eval
            return min_eval

    # =========================================================
    # BEST MOVE
    # =========================================================
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

            score = self.minimax(
                board,
                self.depth - 1,
                -math.inf,
                math.inf,
                False,
                (r, c, self.player)
            )

            board.undo_move(r, c)

            if score > best_score:
                best_score = score
                best_move = (r, c)

        return best_move