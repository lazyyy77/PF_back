import re
import sys
import argparse

def parse_log_file(log_file_path):
    """
    从日志文件中解析所有的 LORA 和 TPGPU 值。

    Args:
        log_file_path (str): 日志文件的路径。
    
    Returns:
        tuple: 包含三个列表 (lora_values_1, lora_values_2, tpgpu_values)。
    """
    lora_values_1 = []
    lora_values_2 = []
    tpgpu_values = []

    lora_pattern = re.compile(r"\[LORA \(([^,]+), ([^)]+)\)\]")
    tpgpu_pattern = re.compile(r"\[TP GPU ([\d.]+)\]")

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            for line in f:
                lora_match = lora_pattern.search(line)
                if lora_match:
                    try:
                        val1 = float(lora_match.group(1))
                        val2 = float(lora_match.group(2))
                        lora_values_1.append(val1)
                        lora_values_2.append(val2)
                    except (ValueError, IndexError):
                        pass
                
                tpgpu_match = tpgpu_pattern.search(line)
                if tpgpu_match:
                    try:
                        tpgpu_values.append(float(tpgpu_match.group(1)))
                    except (ValueError, IndexError):
                        pass
    except FileNotFoundError:
        print(f"错误: 文件未找到 '{log_file_path}'", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"读取文件时发生错误: {e}", file=sys.stderr)
        sys.exit(1)
    print(lora_values_1)
    print("yeah")
    print(lora_values_2)
    print(tpgpu_values)
        
    return lora_values_1, lora_values_2, tpgpu_values

def analyze_and_print(lora_values_1, lora_values_2, tpgpu_values):
    """
    分析数据并打印结果。
    """
    # 计算并打印 LORA 结果
    print("\n--- LORA 值分析 ---")
    if lora_values_1:
        lora1_sum = sum(lora_values_1)
        lora1_avg = lora1_sum / len(lora_values_1)
        lora2_sum = sum(lora_values_2)
        lora2_avg = lora2_sum / len(lora_values_2)
        print(f"分析了 {len(lora_values_1)} 个 LORA 条目。")
        print(f"第一个值的总和: {lora1_sum}, 平均值: {lora1_avg}")
        print(f"第二个值的总和: {lora2_sum}, 平均值: {lora2_avg}")
    else:
        print("在指定范围内未找到 LORA 值。")

    # 计算并打印 TPGPU 结果
    print("\n--- TPGPU 值分析 ---")
    if tpgpu_values:
        tpgpu_sum = sum(tpgpu_values)
        tpgpu_avg = tpgpu_sum / len(tpgpu_values)
        print(f"分析了 {len(tpgpu_values)} 个 TPGPU 条目。")
        print(f"总和: {tpgpu_sum / 1000}")
        print(f"平均值: {tpgpu_avg / 1000}")
    else:
        print("在指定范围内未找到 TPGPU 值。")

    # 计算并打印比率
    print("\n--- 比率分析 ---")
    if tpgpu_values and lora_values_1 and tpgpu_sum != 0:
        ratio1 = lora1_sum / (tpgpu_sum / 1000)
        ratio2 = lora2_sum / (tpgpu_sum / 1000)
        print(f"LORA 第一个值总和 / TPGPU 总和: {ratio1}")
        print(f"LORA 第二个值总和 / TPGPU 总和: {ratio2}")
    else:
        print("无法计算比率（数据不足或 TPGPU 总和为零）。")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从日志文件中解析 LORA 和 TPGPU 值。")
    parser.add_argument("log_file", help="要解析的日志文件的路径。")
    args = parser.parse_args()
    
    # 1. 解析整个文件
    all_lora1, all_lora2, all_tpgpu = parse_log_file(args.log_file)
    
    total_points = len(all_lora1)
    print(f"总共找到 {total_points} 个数据点。")
    
    # 2. 获取用户输入的范围
    while True:
        try:
            range_input = input(f"请输入数据点范围 (例如, '10-30')，或直接按回车使用所有 {total_points} 个数据: ")
            if not range_input.strip():
                start, end = 1, total_points
                print(f"使用所有数据点 (1-{total_points})。")
                break

            parts = range_input.split('-')
            if len(parts) != 2:
                raise ValueError("格式错误，请使用 'start-end' 格式。")
            
            start_str, end_str = parts
            start = int(start_str) if start_str.strip() else 1
            end = int(end_str) if end_str.strip() else total_points

            if start < 1 or end > total_points or start > end:
                raise ValueError(f"范围无效。请确保 1 <= start <= end <= {total_points}。")
            
            print(f"使用数据点范围: {start}-{end}")
            break
        except ValueError as e:
            print(f"输入错误: {e}")

    # 3. 根据范围切片数据
    start_idx = start - 1
    end_idx = end
    
    selected_lora1 = all_lora1[start_idx:end_idx]
    selected_lora2 = all_lora2[start_idx:end_idx]
    selected_tpgpu = all_tpgpu[start_idx:end_idx]
    
    # 4. 分析并打印结果
    analyze_and_print(selected_lora1, selected_lora2, selected_tpgpu)
