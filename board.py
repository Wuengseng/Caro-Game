import numpy as np

class Board:
    def __init__(self, size=19):
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
        # Return list of empty cells.
        # To optimize, we should probably only return cells that are adjacent to played pieces
        # but for simplicity first, we can return all, or better: return adjacent cells for AI speed.
        
        # Optimization for AI: only consider cells within 2 steps of an existing stone
        rows, cols = np.where(self.grid != 0)
        if len(rows) == 0:
            return [(self.size // 2, self.size // 2)] # Center of the board

        # Create a bounding box with padding
        min_r, max_r = max(0, np.min(rows) - 2), min(self.size - 1, np.max(rows) + 2)
        min_c, max_c = max(0, np.min(cols) - 2), min(self.size - 1, np.max(cols) + 2)
        
        empty_cells = []
        for r in range(min_r, max_r + 1):
            for c in range(min_c, max_c + 1):
                if self.grid[r][c] == 0:
                    empty_cells.append((r, c))
                    
        return empty_cells

    def check_win(self, player):
        """Check if the given player has won (5 in a row)."""
        # Horizontal
        for r in range(self.size):
            for c in range(self.size - 4):
                if np.all(self.grid[r, c:c+5] == player):
                    return True
        # Vertical
        for r in range(self.size - 4):
            for c in range(self.size):
                if np.all(self.grid[r:r+5, c] == player):
                    return True
        # Diagonal (top-left to bottom-right)
        for r in range(self.size - 4):
            for c in range(self.size - 4):
                if all(self.grid[r+i, c+i] == player for i in range(5)):
                    return True
        # Anti-diagonal (bottom-left to top-right)
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
