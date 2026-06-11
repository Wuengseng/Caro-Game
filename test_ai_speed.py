import time
import sys
import os

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.board import Board
from api.ai_medium import AIMedium

def test_speed():
    board = Board(15)
    ai1 = AIMedium(1, 2, depth=2)
    ai2 = AIMedium(2, 1, depth=2)
    
    start_time = time.time()
    
    for i in range(10):
        player = 1 if i % 2 == 0 else 2
        ai = ai1 if player == 1 else ai2
        move = ai.get_best_move(board)
        if move is None:
            break
        board.make_move(move[0], move[1], player)
        print(f"Move {i}: {move}")
        
    print(f"10 moves at depth 2 took: {time.time() - start_time:.2f} seconds")
    
    # Test depth 3
    board = Board(15)
    ai1 = AIMedium(1, 2, depth=3)
    ai2 = AIMedium(2, 1, depth=3)
    
    start_time = time.time()
    for i in range(4):
        player = 1 if i % 2 == 0 else 2
        ai = ai1 if player == 1 else ai2
        move = ai.get_best_move(board)
        board.make_move(move[0], move[1], player)
        print(f"Move {i}: {move}")
    print(f"4 moves at depth 3 took: {time.time() - start_time:.2f} seconds")

if __name__ == '__main__':
    test_speed()
