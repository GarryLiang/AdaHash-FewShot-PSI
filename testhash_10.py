import os
import random
import subprocess
import time
import re
import pandas as pd

def generate_data_with_intersection(size_p0, size_p1, intersection_size, min_val=1, max_val=20000):
    """生成带有指定交集大小的两组不重复随机整数"""
    total_required = size_p0 + size_p1 - intersection_size
    if total_required > (max_val - min_val + 1):
        raise ValueError(f"无法在范围 [{min_val}, {max_val}] 内生成所需的不重复整数（总需求: {total_required}）。请扩大数值范围或减小数据量。")
    
    # 1. 先生成指定数量的交集元素
    intersection_elements = set()
    while len(intersection_elements) < intersection_size:
        intersection_elements.add(random.randint(min_val, max_val))
    
    # 2. 生成 P0 独有的元素
    p0_unique = set()
    while len(p0_unique) < (size_p0 - intersection_size):
        num = random.randint(min_val, max_val)
        if num not in intersection_elements:
            p0_unique.add(num)
    
    # 3. 生成 P1 独有的元素
    p1_unique = set()
    while len(p1_unique) < (size_p1 - intersection_size):
        num = random.randint(min_val, max_val)
        if num not in intersection_elements and num not in p0_unique:
            p1_unique.add(num)
            
    # 4. 合并并转为列表
    p0_data = list(intersection_elements | p0_unique)
    p1_data = list(intersection_elements | p1_unique)
    
    return p0_data, p1_data

def create_input_files(size_p0, size_p1, intersection_size):
    """创建 MP-SPDZ 输入文件"""
    os.makedirs("Player-Data", exist_ok=True)
    
    p0_data, p1_data = generate_data_with_intersection(size_p0, size_p1, intersection_size)

    # 写入 P0 数据
    with open("Player-Data/Input-P0-0", "w") as f:
        f.write(f"{size_p0}\n")
        for num in p0_data:
            f.write(f"{num}\n")

    # 写入 P1 数据
    with open("Player-Data/Input-P1-0", "w") as f:
        f.write(f"{size_p1}\n")
        for num in p1_data:
            f.write(f"{num}\n")

    print(f"✅ 数据生成完毕 | P0总量: {size_p0}, P1总量: {size_p1}, 预设交集: {intersection_size}")
    return intersection_size

def run_experiment_and_parse_logs(expected_intersection, run_times=10):
    """运行实验并解析日志"""
    print(f"\n开始进行 {run_times} 次实验...")
    os.makedirs("Logs", exist_ok=True)

    results = []
    for i in range(1, run_times + 1):
        print(f"正在进行第 {i} 次实验...")
        
        # 1. 清理上一次的日志和残留进程
        subprocess.run("killall -9 semi2k-party.x", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        log_files = ["Logs/p0_test.log", "Logs/p1_test.log"]
        for log_file in log_files:
            if os.path.exists(log_file):
                os.remove(log_file)

        # 2. 启动两个进程
        cmd_p0 = "./semi2k-party.x -N 2 -p 0 hashpsi-1000 -h localhost > Logs/p0_test.log 2>&1"
        cmd_p1 = "./semi2k-party.x -N 2 -p 1 hashpsi-1000 -h localhost > Logs/p1_test.log 2>&1"

        process_0 = subprocess.Popen(cmd_p0, shell=True)
        process_1 = subprocess.Popen(cmd_p1, shell=True)

        # 3. 等待两个进程结束
        process_0.wait()
        process_1.wait()
        time.sleep(0.5) # 确保日志完全写入

        # 4. 解析日志
        try:
            with open("Logs/p0_test.log", "r") as f:
                log_content = f.read()

            # 提取各项指标
            exact_match = re.search(r'Exact intersection: (-?\d+)', log_content)
            noisy_match = re.search(r'Noisy intersection: (-?\d+)', log_content)
            output_match = re.search(r'Final Output: (-?\d+)', log_content)
            time_match = re.search(r'Time = ([\d.]+) seconds', log_content)
            data_match = re.search(r'Data sent = ([\d.]+) MB', log_content)
            rounds_match = re.search(r'in ~([\d,]+) rounds', log_content)

            exact_intersection = int(exact_match.group(1)) if exact_match else None
            noisy_intersection = int(noisy_match.group(1)) if noisy_match else None
            final_output = int(output_match.group(1)) if output_match else None
            
            time_taken = float(time_match.group(1)) if time_match else None
            data_sent_mb = float(data_match.group(1)) if data_match else None
            rounds = int(rounds_match.group(1).replace(',', '')) if rounds_match else None

            results.append({
                "Run": i,
                "Expected Intersection": expected_intersection,
                "Exact Intersection (MPC)": exact_intersection,
                "Noisy Intersection": noisy_intersection,
                "Final Output": final_output,
                "Time (s)": time_taken,
                "Data (MB)": data_sent_mb,
                "Rounds": rounds
            })
            print(f"第 {i} 次完成 | 真实/预设交集: {expected_intersection}, MPC精确交集: {exact_intersection}, Final Output: {final_output}")
        except Exception as e:
            print(f"❌ 第 {i} 次实验解析日志失败: {e}")
            results.append({
                "Run": i, "Expected Intersection": expected_intersection, "Exact Intersection (MPC)": None,
                "Noisy Intersection": None, "Final Output": None, "Time (s)": None, "Data (MB)": None, "Rounds": None
            })

    return results

def main():
    try:
        print("请输入实验参数：")
        size_p0 = int(input("P0 数据总量 (例如 150): "))
        size_p1 = int(input("P1 数据总量 (例如 150): "))
        intersection_size = int(input("预设交集大小 (例如 50): "))
        
        if size_p0 <= 0 or size_p1 <= 0 or intersection_size < 0:
            raise ValueError("数据量和交集大小必须为非负数，且数据总量需大于0。")
        if intersection_size > min(size_p0, size_p1):
            raise ValueError("交集大小不能超过 P0 或 P1 的数据总量。")
            
    except ValueError as e:
        print(f"输入错误: {e}")
        return

    # 1. 创建输入文件并获取预设交集
    expected_intersection = create_input_files(size_p0, size_p1, intersection_size)

    # 2. 运行实验 (默认跑 10 次)
    results = run_experiment_and_parse_logs(expected_intersection, run_times=10)

    # 3. 创建并打印汇总表格
    df = pd.DataFrame(results)
    print("\n--- 10次实验结果汇总 ---")
    print(df.to_string(index=False))

    # 4. 打印平均值
    if not df['Time (s)'].isna().all():
        avg_time = df['Time (s)'].mean()
        avg_data = df['Data (MB)'].mean()
        avg_rounds = df['Rounds'].mean()
        print("\n--- 10次实验平均值 ---")
        print(f"平均运行时间: {avg_time:.3f} 秒")
        print(f"平均通信量: {avg_data:.3f} MB")
        print(f"平均通信轮次: {avg_rounds:.0f}")

if __name__ == "__main__":
    main()
