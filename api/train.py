import torch
import torch.optim as optim
import numpy as np
import random
import os
from board import Board
from ai_hard import Net, Node, MCTS, encode_board

# ================= SELF PLAY =================
def self_play(board, net, sims=40):
    data = []
    player = 1

    while True:
        root = Node(board.copy(), player)
        mcts = MCTS(net, sims)
        mcts.search(root)

        moves, probs = mcts.get_policy(root)

        # Build full policy vector
        full_policy = np.zeros(board.size * board.size)
        for (r, c), p in zip(moves, probs):
            full_policy[r * board.size + c] = p

        state = encode_board(board, player)
        data.append((state, full_policy, player))

        # Chọn nước đi cho game
        move = random.choices(moves, weights=probs)[0]
        board.make_move(move[0], move[1], player)

        if board.check_win(player):
            winner = player
            break
        if board.is_full():
            winner = 0
            break

        player = 3 - player

    # Gán giá trị thưởng (Reward)
    result = []
    for state, policy, p in data:
        value = 1 if p == winner else -1 if winner != 0 else 0
        result.append((state, policy, value))

    return result

# ================= TRAIN =================
def train(net, data, epochs=80, batch_size=64):
    optimizer = optim.Adam(net.parameters(), lr=1e-3)

    for _ in range(epochs):
        random.shuffle(data)

        for i in range(0, len(data), batch_size):
            batch = data[i:i+batch_size]

            states = torch.cat([s for s,_,_ in batch])
            # Bọc numpy array bên trong list
            policies = torch.tensor(np.array([p for _,p,_ in batch]), dtype=torch.float32)
            values = torch.tensor(np.array([v for _,_,v in batch]), dtype=torch.float32).unsqueeze(1)

            pred_policy, pred_value = net(states)

            # Tính Loss
            loss_policy = -torch.mean(torch.sum(policies * torch.log_softmax(pred_policy, dim=1), dim=1))
            loss_value = torch.mean((pred_value - values)**2)

            loss = loss_policy + loss_value

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

# ================= RUN PIPELINE =================
def run_alphazero_training():
    BOARD_SIZE = 19
    net = Net(BOARD_SIZE)
    
    if os.path.exists("model.pth"):
        net.load_state_dict(torch.load("model.pth", map_location='cpu'))
        print("[+] Đã load trọng số từ model.pth")

    print(f"[*] Bắt đầu huấn luyện AlphaZero trên bàn cờ {BOARD_SIZE}x{BOARD_SIZE} bằng CPU")

    for iteration in range(50):
        dataset = []
        print(f"\n--- Vòng (Iteration) {iteration+1}/50 ---")
        
        # Để chạy CPU nhanh hơn, giảm số game xuống 3 ván mỗi vòng
        # Nếu muốn train thực tế có thể tăng lên 20 - 50 ván
        for game_idx in range(3):  
            board = Board(BOARD_SIZE)
            dataset += self_play(board, net, sims=30)
            print(f"   - Đã chơi xong game mô phỏng {game_idx+1}")

        print("[*] Đang huấn luyện Neural Network...")
        train(net, dataset)

        torch.save(net.state_dict(), "model.pth")
        print(f"[+] Đã lưu file model.pth cho vòng {iteration+1}")

if __name__ == "__main__":
    run_alphazero_training()
