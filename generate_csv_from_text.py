import csv
import io

# 原始纯文本数据
raw_data_corrected = """
省份 A类名额 B1 B2 B3 A+B类总名额
广东 30 468 288 95 881
浙江 30 293 219 138 680
山东 30 334 119 60 543
北京 30 262 134 86 512
江苏 30 248 121 92 491
四川 30 203 135 102 470
福建 30 204 126 70 430
湖南 30 154 91 87 362
重庆 30 80 123 96 329
上海 30 136 103 58 327
安徽 30 161 50 30 271
河南 30 113 33 30 206
湖北 30 93 38 41 202
河北 30 104 36 29 199
陕西 30 87 29 28 174
江西 30 55 33 19 137
山西 30 77 7 23 137
广西 30 72 11 23 136
辽宁 30 63 18 22 133
天津 30 73 10 14 127
贵州 30 53 8 6 97
吉林 30 37 11 18 96
黑龙江 30 41 9 12 92
云南 30 50 4 6 90
新疆 30 48 5 3 86
海南 30 40 2 3 75
内蒙古 30 34 2 0 66
香港 30 5 11 19 65
甘肃 30 17 1 6 54
宁夏 30 15 0 0 45
澳门 30 4 4 3 41
青海 30 4 0 0 34
总数 960 3628 1781 1219 7588
"""

# 这是将原始文本转换为标准化CSV所必需的一次性映射。
# 此后的所有脚本将不再需要任何映射。
PROVINCE_NAME_TO_CODE_MAP = {
    '广东': 'GD', '浙江': 'ZJ', '山东': 'SD', '北京': 'BJ', '江苏': 'JS',
    '四川': 'SC', '福建': 'FJ', '湖南': 'HN', '重庆': 'CQ', '上海': 'SH',
    '安徽': 'AH', '河南': 'HA', '湖北': 'HB', '河北': 'HE', '陕西': 'SN',
    '江西': 'JX', '山西': 'SX', '广西': 'GX', '辽宁': 'LN', '天津': 'TJ',
    '贵州': 'GZ', '吉林': 'JL', '黑龙江': 'HL', '云南': 'YN', '新疆': 'XJ',
    '海南': 'HI', '内蒙古': 'NM', '香港': 'HK', '甘肃': 'GS', '宁夏': 'NX',
    '澳门': 'MO', '青海': 'QH', '总数': 'TOTAL'
}

def generate_csv(output_filename="noip2025_participants.csv"):
    """
    从内置的原始文本数据生成CSV文件，使用省份代码作为第一列。
    """
    data_file = io.StringIO(raw_data_corrected.strip())
    
    header_line = data_file.readline().strip().split()
    header_line[0] = '省份代码' # 修改表头
    
    try:
        with open(output_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(header_line)
            
            for line in data_file:
                if line.strip():
                    row_data = line.strip().split()
                    province_name = row_data[0]
                    province_code = PROVINCE_NAME_TO_CODE_MAP.get(province_name, province_name)
                    row_data[0] = province_code
                    writer.writerow(row_data)
        
        print(f"成功生成标准化CSV文件: '{output_filename}' (使用省份代码)")
        return True
    except IOError as e:
        print(f"写入文件时出错: {e}")
        return False

if __name__ == "__main__":
    generate_csv()
