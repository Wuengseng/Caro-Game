import time
import sys
import random
from board import Board
from ai_easy import AIEasy
from ai_medium import AIMedium
from ai_hard import AIHard

# Ép console xuất UTF-8 để in tiếng Việt không lỗi
sys.stdout.reconfigure(encoding='utf-8')

def run_benchmark():
    print("="*70)
    print("KHỞI TẠO CÁC MÔ HÌNH AI...")
    print("="*70)

    player = 1
    opponent = 2

    print("Đang tải AI Easy (Greedy Heuristic)...")
    ai_easy = AIEasy(player, opponent)

    print("Đang tải AI Medium (Minimax Alpha-Beta - Depth 5)...")
    ai_medium = AIMedium(player, opponent, depth=5)

    print("Đang tải AI Hard (Deep Imitation Learning / ResNet)...")
    ai_hard = AIHard(player, model_path="models/alphazero_gomoku_imitation.pth")
    
    # Warm up AI Hard
    board = Board(size=15)
    _ = ai_hard.get_best_move(board)

    print("\n" + "="*70)
    print("BẮT ĐẦU BENCHMARK - TRUNG BÌNH MỘT VÁN GAME (TỪ EARLY ĐẾN LATE GAME)")
    print("="*70)

    total_easy_time = 0
    total_medium_time = 0
    total_hard_time = 0
    num_samples = 0

    # Chơi ngẫu nhiên 15 nước cờ (đủ để mô phỏng từ Early đến Mid game)
    random.seed(42) # Cố định seed để dễ so sánh
    for step in range(1, 16):
        # Chọn đại 1 ô trống lân cận để đánh cho giống thật (không đánh tít ra góc)
        empty_cells = board.get_empty_cells()
        if not empty_cells:
            break
        
        # Nếu là nước đầu, đánh giữa bàn
        if step == 1:
            r, c = 7, 7
        else:
            # Chọn ngẫu nhiên trong các ô hợp lệ
            r, c = random.choice(empty_cells)
            
        current_player = 1 if step % 2 != 0 else 2
        board.make_move(r, c, current_player)

        # Cứ mỗi 5 nước đi, chúng ta sẽ bắt cả 3 AI cùng suy nghĩ để lấy mẫu
        # Giai đoạn: 5 (Mở màn), 10, 15 (Giữa game), 20, 25, 30 (Cuối game)
        if step % 5 == 0:
            print(f"-> Đang lấy mẫu tại nước thứ {step} (Số quân cờ trên bàn: {step})...")
            num_samples += 1
            
            # Đo AI Easy
            t0 = time.time()
            ai_easy.get_best_move(board)
            total_easy_time += (time.time() - t0)

            # Đo AI Medium
            t0 = time.time()
            ai_medium.get_best_move(board)
            total_medium_time += (time.time() - t0)

            # Đo AI Hard
            t0 = time.time()
            ai_hard.get_best_move(board)
            total_hard_time += (time.time() - t0)

    # Tính trung bình
    avg_easy = total_easy_time / num_samples
    avg_medium = total_medium_time / num_samples
    avg_hard = total_hard_time / num_samples

    print("\n" + "="*70)
    print("KẾT QUẢ TỐC ĐỘ TRUNG BÌNH (TIME PER MOVE):")
    print("="*70)
    print(f"[Dễ - Heuristic]       : {avg_easy:.4f} giây / nước đi")
    print(f"[Vừa - Minimax 3 tầng] : {avg_medium:.4f} giây / nước đi")
    print(f"[Khó - ResNet Toàn cục]: {avg_hard:.4f} giây / nước đi")
    
    print("\n" + "="*70)
    print("PHÂN TÍCH KẾT QUẢ THỰC TẾ DỰA TRÊN SỐ LIỆU ĐO ĐẠC:")
    print("="*70)
    
    # Sắp xếp tốc độ từ nhanh nhất đến chậm nhất (thời gian nhỏ nhất xếp trước)
    results = [
        ("Dễ (Heuristic)", avg_easy),
        ("Trung bình (Minimax)", avg_medium),
        ("Khó (ResNet)", avg_hard)
    ]
    results.sort(key=lambda x: x[1])

    print(f"Xếp hạng Tốc độ Phản hồi (Nhanh đến Chậm):")
    for i, (name, time_val) in enumerate(results, 1):
        print(f"{i}. {name:<25}: {time_val:.4f}s")
    
    print("\nNhận xét tự động từ hệ thống:")
    if avg_medium > avg_easy:
        print("- AI Trung bình chậm hơn AI Dễ: Chính xác! Minimax phải tốn thời gian duyệt qua nhiều nhánh của cây trò chơi.")
    else:
        print("- AI Trung bình nhanh hơn AI Dễ: Xảy ra do bàn cờ quá trống, số lượng nhánh Minimax tạo ra ít nên chạy vèo vèo.")

    import torch
    if avg_hard == results[-1][1]: # Nếu Khó chậm nhất
        if not torch.cuda.is_available():
            print("- AI Khó chậm nhất: Rất thực tế! Do bạn đang chạy Deep Learning (ResNet) bằng CPU, hàng tỷ phép nhân ma trận khiến tốc độ bị thắt nút cổ chai.")
        else:
            print("- AI Khó chậm nhất: Model đang chạy quá chậm. Có thể do kích thước mạng 256 channels quá lớn hoặc overhead load vào GPU.")
    elif avg_hard == results[0][1]: # Nếu Khó nhanh nhất
        print("- AI Khó nhanh nhất: Sức mạnh vô đối của GPU CUDA đã được chứng minh. Quá trình feed-forward tensor 1 chiều nhanh hơn hẳn vòng lặp for/while thông thường!")
    else:
        print("- AI Khó đứng ở giữa: Inference của mạng ổn định ở một mức thời gian cố định, không phụ thuộc vào số lượng quân cờ trên bàn như Minimax.")
    print("="*70)

def play_match(name1, ai1, name2, ai2, board_size=15):
    board = Board(size=board_size)
    current_turn = 1 # 1 đi trước
    
    # Cập nhật màu quân cờ cho các AI
    ai1.player = 1
    ai1.opponent = 2
    ai2.player = 2
    ai2.opponent = 1
    
    players = {1: (name1, ai1), 2: (name2, ai2)}
    
    # Giới hạn số nước đi để tránh vô hạn
    for step in range(board_size * board_size):
        _, current_ai = players[current_turn]
        
        move = current_ai.get_best_move(board)
        if move is None:
            break # Hết nước đi
            
        board.make_move(move[0], move[1], current_turn)
        
        if board.check_win(current_turn):
            return current_turn # Trả về 1 hoặc 2 (người thắng)
            
        current_turn = 3 - current_turn
        
    return 0 # Hòa

def run_arena():
    print("\n" + "="*70)
    print("BẮT ĐẦU ARENA - SO SÁNH TỶ LỆ THẮNG (10 TRẬN)")
    print("="*70)
    
    # Khởi tạo AI cho Arena
    # LƯU Ý: Minimax depth 3 để thời gian đấu 10 trận không bị quá lâu (Depth 5 có thể tốn hàng tiếng đồng hồ)
    ai_easy = AIEasy(1, 2)
    ai_medium = AIMedium(1, 2, depth=3) 
    ai_hard = AIHard(1, model_path="models/alphazero_gomoku_imitation.pth")
    
    def simulate_10_matches(name1, ai1, name2, ai2):
        print(f"\n--- Đấu 10 trận: {name1} vs {name2} ---")
        wins1, wins2, draws = 0, 0, 0
        
        for i in range(1, 11):
            # Trận lẻ: ai1 đi trước (player 1)
            # Trận chẵn: ai2 đi trước (player 1)
            if i % 2 != 0:
                winner = play_match(name1, ai1, name2, ai2)
                if winner == 1:
                    wins1 += 1
                    winner_name = name1
                elif winner == 2:
                    wins2 += 1
                    winner_name = name2
                else:
                    draws += 1
                    winner_name = "Hòa"
            else:
                winner = play_match(name2, ai2, name1, ai1)
                if winner == 1:
                    wins2 += 1 # ai2 là player 1
                    winner_name = name2
                elif winner == 2:
                    wins1 += 1 # ai1 là player 2
                    winner_name = name1
                else:
                    draws += 1
                    winner_name = "Hòa"
                    
            print(f"  + Trận {i:<2}: {winner_name}")
            
        print(f"=> Tổng kết: [{name1}] thắng {wins1} | [{name2}] thắng {wins2} | Hòa {draws}")

    simulate_10_matches("Khó (ResNet)", ai_hard, "Trung bình (Minimax)", ai_medium)
    simulate_10_matches("Trung bình (Minimax)", ai_medium, "Dễ (Heuristic)", ai_easy)

if __name__ == "__main__":
    # 1. Đo tốc độ trước
    run_benchmark()
    # 2. Đấu Arena sau
    run_arena()
