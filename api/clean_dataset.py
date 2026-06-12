import os
import glob
import torch
import numpy as np
import argparse

def clean_and_merge_datasets(input_paths, output_file):
    """
    input_paths: danh sách đường dẫn tới các file .pt
    output_file: đường dẫn lưu file kết quả
    """
    if not input_paths:
        print("Không có file dữ liệu nào để xử lý.")
        return

    unique_data = {}
    total_samples_before = 0
    
    for file_path in input_paths:
        print(f"Đang đọc file: {file_path}...")
        try:
            data = torch.load(file_path)
            states = data['states'].numpy()
            policies = data['policies'].numpy()
            
            num_samples = len(states)
            total_samples_before += num_samples
            
            for i in range(num_samples):
                s = states[i]
                p = policies[i]
                
                # Chuyển state array thành bytes để làm key cho Dictionary
                s_bytes = s.tobytes()
                
                if s_bytes in unique_data:
                    unique_data[s_bytes]['policy'] += p
                    unique_data[s_bytes]['count'] += 1
                else:
                    unique_data[s_bytes] = {
                        'state': s,
                        'policy': p.copy(),
                        'count': 1
                    }
        except Exception as e:
            print(f"Lỗi khi đọc file {file_path}: {e}")

    total_samples_after = len(unique_data)
    print(f"\n" + "="*30)
    print(f"        THỐNG KÊ TỔNG KẾT        ")
    print("="*30)
    print(f"Tổng số mẫu trước khi lọc: {total_samples_before}")
    print(f"Tổng số mẫu duy nhất giữ lại: {total_samples_after}")
    
    if total_samples_before > 0:
        print(f"Đã loại bỏ được: {total_samples_before - total_samples_after} mẫu trùng lặp.")
    
    if total_samples_after == 0:
        print("Không có dữ liệu hợp lệ để lưu.")
        return

    print("\nĐang tính trung bình cộng (chuẩn hóa) các policy và tạo file mới...")
    new_states = []
    new_policies = []
    
    for val in unique_data.values():
        new_states.append(val['state'])
        # Tính trung bình cộng policy cho các state bị trùng
        normalized_policy = val['policy'] / val['count']
        new_policies.append(normalized_policy)
        
    states_tensor = torch.tensor(np.array(new_states), dtype=torch.float32)
    policies_tensor = torch.tensor(np.array(new_policies), dtype=torch.float32)
    
    print("Đang lưu xuống ổ cứng...")
    torch.save({
        'states': states_tensor,
        'policies': policies_tensor
    }, output_file)
    print(f"HOÀN TẤT! Đã lưu dataset sạch vào: {output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Làm sạch và gộp các file dataset (.pt) trùng lặp.")
    parser.add_argument("--input_dir", type=str, default=r"C:\CNTT\AI\Caro_Project\api\dataset", help="Đường dẫn tới thư mục chứa các file dataset gốc.")
    parser.add_argument("--output_file", type=str, default=r"C:\CNTT\AI\Caro_Project\api\dataset\expert_dataset_final.pt", help="Đường dẫn file lưu dataset sau khi làm sạch.")
    args = parser.parse_args()

    # Tìm tất cả file .pt trong thư mục đầu vào
    search_pattern = os.path.join(args.input_dir, "*.pt")
    dataset_files = glob.glob(search_pattern)
    
    # Lọc bỏ file đầu ra nếu nó vô tình nằm trong thư mục đầu vào
    output_abs_path = os.path.abspath(args.output_file)
    dataset_files = [f for f in dataset_files if os.path.abspath(f) != output_abs_path]
        
    if len(dataset_files) > 0:
        print(f"Tìm thấy {len(dataset_files)} file dataset (.pt) trong thư mục '{args.input_dir}'. Bắt đầu quá trình lọc trùng lặp...")
        clean_and_merge_datasets(dataset_files, args.output_file)
    else:
        print(f"Không tìm thấy file dataset (.pt) nào trong thư mục '{args.input_dir}'.")
        print("Vui lòng kiểm tra lại đường dẫn thư mục (--input_dir).")
