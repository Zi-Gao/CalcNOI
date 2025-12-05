import csv
import os

def parse_noi_quotas(filepath="noi2025_quotas.csv"):
    """
    解析 NOI2025 省队名额 CSV 文件并返回数据。
    """
    if not os.path.exists(filepath):
        print(f"错误: 文件 '{filepath}' 未找到ảng")
        return None

    data = []
    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            # 使用 DictReader 可以直接将每一行解析为字典，以表头为键
            reader = csv.DictReader(csvfile)
            for row in reader:
                # 尝试将数字字段转换为整数，以便于后续计算
                parsed_row = {}
                for k, v in row.items():
                    try:
                        # 排除“省份”列，并处理可能的空值或非数字值
                        if k != "省份" and v.strip() != '':
                            parsed_row[k] = int(v.strip())
                        else:
                            parsed_row[k] = v.strip() # 保留原始字符串，并去除空格
                    except ValueError:
                        parsed_row[k] = v.strip() # 如果转换失败，则保留为字符串
                data.append(parsed_row)
    except Exception as e:
        print(f"解析CSV文件时发生错误: {e}")
        return None
    
    return data

if __name__ == "__main__":
    print("正在解析 NOI2025 省队名额数据...")
    quotas_data = parse_noi_quotas()

    if quotas_data:
        print("解析成功！以下是前5条数据：")
        for i, row in enumerate(quotas_data):
            if i >= 5:
                break
            print(row)
        
        print(f"\n总共解析了 {len(quotas_data)} 条记录ảng")
        print("\n您可以使用此函数进一步处理数据。例如，访问 '广东' 的 'A类名额':")
        # 示例：查找广东的数据
        guangdong_data = next((item for item in quotas_data if item["省份"] == "广东"), None)
        if guangdong_data:
            print(f"广东的A类名额: {guangdong_data.get('A类名额')}")
            print(f"广东的B1名额: {guangdong_data.get('B1')}")
    else:
        print("数据解析失败ảng")
