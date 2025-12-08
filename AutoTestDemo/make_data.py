# 文件：AutoTestDemo/make_data.py
import csv
import random

def create_csv():
    # 1. 定义 100 个测试数据
    # 为了演示，我们生成类似：User_1_搜索词, User_2_搜索词...
    data = []
    header = ['user_id', 'search_word', 'expect_result']
    data.append(header)

    for i in range(1, 101): # 生成 100 条
        user_id = f"User_{i}"
        word = f"自动化测试_{i}" # 搜这个词
        expect = f"自动化测试_{i}" # 期望结果包含这个词
        data.append([user_id, word, expect])

    # 2. 写入 CSV 文件
    # newline='' 是为了防止 Excel 打开有空行
    with open('data/users.csv', 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerows(data)
    
    print(f"✅ 成功生成 {len(data)-1} 条测试数据，已保存到 data/users.csv")

if __name__ == '__main__':
    # 确保 data 文件夹存在
    import os
    if not os.path.exists('data'):
        os.makedirs('data')
    create_csv()