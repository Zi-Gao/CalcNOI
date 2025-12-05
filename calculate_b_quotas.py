import csv
import os
import math

def calculate_b_quotas_from_raw_data(filepath="noi2025_quotas.csv"):
    """
    读取 NOI2025 省队名额 CSV 文件 (其中B1为NOIP参赛人数)，
    推算 B1 名额，并与其他数据进行比较和展示。
    """
    if not os.path.exists(filepath):
        print(f"错误: 文件 '{filepath}' 未找到。请先运行 generate_csv_from_text.py。")
        return

    print(f"正在读取文件: {filepath} 并推算B类名额...")
    raw_data_rows = []
    national_noip_participants_total = 0
    errors = []

    try:
        with open(filepath, mode='r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                raw_data_rows.append(row)
                if row["省份"] != "总数":
                    try:
                        national_noip_participants_total += int(row["B1"])
                    except ValueError:
                        errors.append(f"省份 {row["省份"]}: B1(NOIP参赛人数)不是有效数字: {row["B1"]}")

    except Exception as e:
        print(f"读取或解析CSV文件时发生错误: {e}")
        return
    
    if errors:
        print("\n--- 原始数据读取错误 ---")
        for error in errors:
            print(error)
        return

    print(f"\n计算得出全国NOIP总参赛人数 (B1列总和): {national_noip_participants_total}")
    print("\n--- B类名额推算结果及数据验证 ---")
    
    calculated_results = []

    for row in raw_data_rows:
        province = row["省份"]
        if province == "总数":
            # 跳过总数行，或者可以进行总数验证
            continue

        try:
            a_quota_csv = int(row["A类名额"])
            noip_provincial_participants = int(row["B1"])
            b2_raw_input = int(row["B2"])
            b3_raw_input = int(row["B3"])
            a_plus_b_total_csv = int(row["A+B类总名额"])

            # 推导该省份的实际总B类名额 S (S = (A+B类总名额) - A类名额)
            # 这是假设 CSV 中 A+B类总名额 是最终名额，A类名额是已知的固定部分
            s_implied_total_b_quota = a_plus_b_total_csv - a_quota_csv

            # 计算 B1 名额 (根据公式: B1 = S × 50% × (NOIP各省人数 / 全国总人数))
            if national_noip_participants_total > 0:
                b1_calculated_float = s_implied_total_b_quota * 0.5 * \
                                      (noip_provincial_participants / national_noip_participants_total)
                b1_calculated_rounded = round(b1_calculated_float) # 按照规则四舍五入
            else:
                b1_calculated_float = 0.0
                b1_calculated_rounded = 0
            
            # 收集结果
            calculated_results.append({
                "省份": province,
                "A类名额(CSV)": a_quota_csv,
                "NOIP各省人数(B1)": noip_provincial_participants,
                "原始B2输入(B2)": b2_raw_input, # 无法直接计算，作为原始输入展示
                "原始B3输入(B3)": b3_raw_input, # 无法直接计算，作为原始输入展示
                "推导总B类名额(S)": s_implied_total_b_quota,
                "计算B1名额(浮点)": f"{b1_calculated_float:.2f}",
                "计算B1名额(四舍五入)": b1_calculated_rounded,
                "A+B类总名额(CSV)": a_plus_b_total_csv,
                "备注": "B2/B3名额计算需要更多参数和细节数据"
            })

        except ValueError as ve:
            errors.append(f"省份 {province}: 转换数值时出错 - {ve}. 原始行: {row}")
        except KeyError as ke:
            errors.append(f"省份 {province}: 缺少列 - {ke}. 原始行: {row}")
    
    for res in calculated_results:
        print(f"省份: {res['省份']} | A类(CSV): {res['A类名额(CSV)']} | NOIP人数(B1): {res['NOIP各省人数(B1)']} | 原始B2: {res['原始B2输入(B2)']} | 原始B3: {res['原始B3输入(B3)']} | 推导总B(S): {res['推导总B类名额(S)']} | 计算B1(四舍五入): {res['计算B1名额(四舍五入)']} (浮点: {res['计算B1名额(浮点)']}) | A+B总(CSV): {res['A+B类总名额(CSV)']}")

    if errors:
        print("\n--- 发现以下错误 ---")
        for error in errors:
            print(error)

if __name__ == "main":
    calculate_b_quotas_from_raw_data()