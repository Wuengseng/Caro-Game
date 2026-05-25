import pygame
import sys
from board import Board
from ai_easy import AIEasy
from ai_medium import AIMedium
from ai_hard import AIHard

# Configuration
WIDTH, HEIGHT = 800, 800
GRID_SIZE = 15
CELL_SIZE = WIDTH // (GRID_SIZE + 1)
MARGIN = CELL_SIZE

# Colors
BG_COLOR = (222, 184, 135) # Burlywood color for wooden board
LINE_COLOR = (0, 0, 0)
BLACK_COLOR = (20, 20, 20)
WHITE_COLOR = (245, 245, 245)
TEXT_COLOR = (0, 0, 0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Caro AI (Gomoku) - 3 Levels")
font = pygame.font.SysFont(None, 40)
big_font = pygame.font.SysFont(None, 60)

def draw_board(board):
    screen.fill(BG_COLOR)
    # Draw grid
    for i in range(GRID_SIZE):
        # Vertical lines
        pygame.draw.line(screen, LINE_COLOR, (MARGIN + i * CELL_SIZE, MARGIN), (MARGIN + i * CELL_SIZE, HEIGHT - MARGIN), 2)
        # Horizontal lines
        pygame.draw.line(screen, LINE_COLOR, (MARGIN, MARGIN + i * CELL_SIZE), (WIDTH - MARGIN, MARGIN + i * CELL_SIZE), 2)
        
    # Draw stones
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if board.grid[r][c] == 1:
                pygame.draw.circle(screen, BLACK_COLOR, (MARGIN + c * CELL_SIZE, MARGIN + r * CELL_SIZE), CELL_SIZE // 2 - 2)
            elif board.grid[r][c] == 2:
                pygame.draw.circle(screen, WHITE_COLOR, (MARGIN + c * CELL_SIZE, MARGIN + r * CELL_SIZE), CELL_SIZE // 2 - 2)
                pygame.draw.circle(screen, LINE_COLOR, (MARGIN + c * CELL_SIZE, MARGIN + r * CELL_SIZE), CELL_SIZE // 2 - 2, 1)

def main_menu():
    while True:
        screen.fill(BG_COLOR)
        title_text = big_font.render("CARO AI (GOMOKU)", True, TEXT_COLOR)
        screen.blit(title_text, (WIDTH//2 - title_text.get_width()//2, HEIGHT//4))

        easy_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 - 40, 200, 50)
        med_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 30, 200, 50)
        hard_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)

        pygame.draw.rect(screen, (150, 220, 150), easy_btn)
        pygame.draw.rect(screen, (220, 220, 150), med_btn)
        pygame.draw.rect(screen, (220, 150, 150), hard_btn)

        screen.blit(font.render("Easy", True, BLACK_COLOR), (easy_btn.x + 65, easy_btn.y + 12))
        screen.blit(font.render("Medium", True, BLACK_COLOR), (med_btn.x + 45, med_btn.y + 12))
        screen.blit(font.render("Hard", True, BLACK_COLOR), (hard_btn.x + 65, hard_btn.y + 12))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                if easy_btn.collidepoint(pos):
                    return "easy"
                if med_btn.collidepoint(pos):
                    return "medium"
                if hard_btn.collidepoint(pos):
                    return "hard"

def game_loop(difficulty):
    board = Board(GRID_SIZE)
    player = 1 # Human (Black)
    ai_player = 2 # AI (White)
    
    if difficulty == "easy":
        ai = AIEasy(ai_player, player)
    elif difficulty == "medium":
        ai = AIMedium(ai_player, player, depth=5) # Limit depth to 5 in Python for responsiveness
    else:
        ai = AIHard(ai_player, player)

    turn = player
    game_over = False
    winner = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            if event.type == pygame.MOUSEBUTTONDOWN and not game_over and turn == player:
                x, y = pygame.mouse.get_pos()
                c = round((x - MARGIN) / CELL_SIZE)
                r = round((y - MARGIN) / CELL_SIZE)
                
                if board.is_valid_move(r, c):
                    board.make_move(r, c, player)
                    if board.check_win(player):
                        game_over = True
                        winner = player
                    elif board.is_full():
                        game_over = True
                    else:
                        turn = ai_player

        if not game_over and turn == ai_player:
            draw_board(board)
            pygame.display.flip()
            
            pygame.display.set_caption(f"Caro AI - {difficulty.capitalize()} - AI is thinking...")
            ai_move = ai.get_best_move(board)
            if ai_move:
                board.make_move(ai_move[0], ai_move[1], ai_player)
                if board.check_win(ai_player):
                    game_over = True
                    winner = ai_player
                elif board.is_full():
                    game_over = True
            pygame.display.set_caption(f"Caro AI - {difficulty.capitalize()}")
            turn = player

        draw_board(board)
        
        if game_over:
            msg = "Draw!" if winner == 0 else f"{'Player' if winner == 1 else 'AI'} wins!"
            text = big_font.render(msg, True, (255, 0, 0))
            screen.blit(text, (WIDTH//2 - text.get_width()//2, HEIGHT//2 - text.get_height()//2 - 50))
            
            restart_btn = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 20, 200, 50)
            pygame.draw.rect(screen, (200, 200, 200), restart_btn)
            screen.blit(font.render("Main Menu", True, BLACK_COLOR), (restart_btn.x + 30, restart_btn.y + 12))
            
            pygame.display.flip()
            
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        if restart_btn.collidepoint(event.pos):
                            return
        
        pygame.display.flip()

if __name__ == "__main__":
    while True:
        diff = main_menu()
        game_loop(diff)
