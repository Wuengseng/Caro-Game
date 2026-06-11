import sys
import os
import torch
sys.path.append(os.path.abspath('.'))

try:
    from api.generate_dataset import generate_games
    from api.train_imitation import train_imitation

    print('1. Sinh dữ liệu 1 ván cờ (Depth=2 cho nhanh)...')
    generate_games(num_games=1, depth=2, save_path='test_expert_dataset.pt')

    print('\n2. Kiểm tra định dạng dữ liệu...')
    data = torch.load('test_expert_dataset.pt')
    print('States shape:', data['states'].shape)
    print('Policies shape:', data['policies'].shape)

    print('\n3. Chạy thử quy trình Train...')
    train_imitation(dataset_path='test_expert_dataset.pt', epochs=1, batch_size=16, save_path='test_model.pth')
    print('\n[THÀNH CÔNG] Pipeline hoàn toàn hợp lệ!')

except Exception as e:
    print('\n[LỖI]', e)

