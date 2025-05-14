import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Đọc dữ liệu từ stats_full.csv
def load_data():
    data = pd.read_csv('stats_full.csv')
    data = data.dropna()
    numeric_cols = ['Path_Length', 'Completion_Time', 'Expanded_Nodes', 'Collected_Coins', 'Remaining_Blood']
    for col in numeric_cols:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    return data

# Tính trung bình theo thuật toán và bản đồ
def calculate_averages(data, column):
    return data.groupby(['Algorithm', 'Map'])[column].mean().unstack(level=0)

# Vẽ biểu đồ cột
def plot_bar_chart(data, title, ylabel, filename):
    plt.figure(figsize=(16, 8))  # Tăng kích thước cho 9 bản đồ
    maps = [f'Map {i}' for i in range(1, 10)]  # Map 1 đến Map 9
    algorithms = data.columns
    x = np.arange(len(maps))
    width = 0.15  # Độ rộng cột cho 5 thuật toán
    colors = ['skyblue', 'salmon', 'lightgreen', 'orange', 'purple']  # Màu cho mỗi thuật toán

    for i, algo in enumerate(algorithms):
        values = data[algo].reindex(maps).fillna(0)
        plt.bar(x + i * width, values, width, label=algo, color=colors[i % len(colors)])

    plt.xlabel('Map')
    plt.ylabel(ylabel)
    plt.title(title)
    plt.xticks(x + width * (len(algorithms) - 1) / 2, maps)
    plt.legend()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()

# Main
data = load_data()

# Tạo biểu đồ cho từng phương diện
plot_bar_chart(
    calculate_averages(data, 'Path_Length'),
    'Average Path Length by Map',
    'Path Length',
    'path_length.png'
)

plot_bar_chart(
    calculate_averages(data, 'Completion_Time'),
    'Average Completion Time by Map',
    'Completion Time (seconds)',
    'completion_time.png'
)

plot_bar_chart(
    calculate_averages(data, 'Expanded_Nodes'),
    'Average Expanded Nodes by Map',
    'Expanded Nodes',
    'expanded_nodes.png'
)

plot_bar_chart(
    calculate_averages(data, 'Collected_Coins'),
    'Average Collected Coins by Map',
    'Collected Coins',
    'collected_coins.png'
)

plot_bar_chart(
    calculate_averages(data, 'Remaining_Blood'),
    'Average Remaining Blood by Map',
    'Remaining Blood',
    'remaining_blood.png'
)