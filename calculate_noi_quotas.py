import os
import glob
import math
import json
import pandas as pd
from collections import defaultdict

# ==============================================================================
# 核心假设与可配置参数 (根据 NOI2026 官方方案更新)
# ==============================================================================
S_TOTAL_B_QUOTAS = 150
K1_SEGMENTS = 5
K2_TOP_SCORES = 5
P_MAX_RATIO = 0.05
MAX_B_QUOTAS_PER_PROVINCE = 12
A_QUOTA_BASE = 5
# ==============================================================================

def load_province_mapping(filepath="province_mapping.json"):
    """从JSON文件加载省份名称到代码的映射，并返回一个代码到名称的反向映射。"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            name_to_code = json.load(f)
            # 创建并返回一个反向映射
            return {code: name for name, code in name_to_code.items()}
    except Exception as e:
        print(f"读取映射文件 '{filepath}' 出错: {e}")
        return {}

def load_province_participants(filepath="noip2025_participants.csv"):
    """
    从CSV加载各省NOIP参赛人数。
    假定CSV的第一列'省份代码'已包含正确的省份缩写。
    """
    participants = {}
    try:
        df = pd.read_csv(filepath)
        df = df[df['省份代码'] != 'TOTAL']
        # 假设 'B1' 列是参赛人数
        participants = df.set_index('省份代码')['B1'].to_dict()
    except Exception as e:
        print(f"读取参赛人数文件 '{filepath}' 出错: {e}")
    return participants

def load_all_scores(results_dir="results"):
    """
    加载 results/ 目录下所有省份的成绩，并从'用户'列解析省份代码。
    """
    all_scores = defaultdict(list)
    csv_files = glob.glob(os.path.join(results_dir, '*.csv'))
    
    if not csv_files:
        print(f"警告: 在 '{results_dir}' 目录中没有找到CSV成绩文件。")
        return {}
        
    all_dfs = [pd.read_csv(f) for f in csv_files]
    combined_df = pd.concat(all_dfs, ignore_index=True)

    if '用户' not in combined_df.columns:
        print("错误: 成绩文件中找不到 '用户' 列。" )
        return {}

    combined_df['province_code'] = combined_df['用户'].str.slice(0, 2)
    score_col = '总分数' if '总分数' in combined_df.columns else 'score'
    
    if score_col not in combined_df.columns:
        print(f"错误: 成绩文件中找不到 '{score_col}' 列。" )
        return {}

    grouped = combined_df[combined_df[score_col] > 0].groupby('province_code')
    for province_code, group in grouped:
        all_scores[province_code] = group[score_col].tolist()
        
    return all_scores

def calculate_quotas():
    """
    主计算函数。
    """
    print("--- 开始计算NOI2025省队名额 ---")
    
    # 1. 加载数据
    province_code_to_name = load_province_mapping()
    participants_data = load_province_participants()
    scores_data = load_all_scores()

    if not participants_data or not scores_data or not province_code_to_name:
        print("数据加载不完整，无法继续计算。" )
        return

    # 2. 计算全国总参赛人数
    national_total_participants = sum(participants_data.values())
    print(f"\n1. 全国总参赛人数 (来自participants文件): {national_total_participants}")

    # 3. 计算B类名额
    b1_quotas = {}
    b2_quotas = defaultdict(int)
    b3_quotas = defaultdict(int)
    
    # B1 计算
    print(f"\n2. 计算 B1 ...")
    for province_code, count in participants_data.items():
        b1_share = (count / national_total_participants) if national_total_participants else 0
        b1_quotas[province_code] = S_TOTAL_B_QUOTAS * 0.5 * b1_share

    # B2 计算
    print(f"3. 计算 B2 ...")
    all_representative_scores = [{'province_code': pc, 'score': sum(s[i:i+math.ceil(len(s)/K1_SEGMENTS)])/len(s[i:i+math.ceil(len(s)/K1_SEGMENTS)])} for pc, s in scores_data.items() for i in range(0,len(s),math.ceil(len(s)/K1_SEGMENTS)) if s]
    all_representative_scores.sort(key=lambda x: x['score'], reverse=True)
    b2_award_count = math.floor(S_TOTAL_B_QUOTAS * 0.3)
    for item in all_representative_scores[:b2_award_count]:
        b2_quotas[item['province_code']] += 1

    # B3 计算
    print(f"4. 计算 B3 ...")
    all_excellent_scores = [{'province_code': pc, 'score': score} for pc, s in scores_data.items() for score in sorted(s, reverse=True)[:K2_TOP_SCORES]]
    all_excellent_scores.sort(key=lambda x: x['score'], reverse=True)
    b3_award_count = math.floor(S_TOTAL_B_QUOTAS * 0.2)
    for item in all_excellent_scores[:b3_award_count]:
        b3_quotas[item['province_code']] += 1
        
    # 4. 汇总与约束
    print("\n5. 汇总与约束应用 ...")
    final_results = []
    # 以成绩数据中的省份为准进行计算和展示
    for province_code in sorted(scores_data.keys()):
        participant_count = participants_data.get(province_code, 0)
        if participant_count == 0:
            province_name = province_code_to_name.get(province_code, province_code)
            print(f"警告: 成绩文件中的省份 '{province_name} ({province_code})' 在参赛人数文件中未找到，跳过计算。" )
            continue

        b1 = b1_quotas.get(province_code, 0)
        b2 = b2_quotas.get(province_code, 0)
        b3 = b3_quotas.get(province_code, 0)
        
        total_b = round(b1 + b2 + b3)
        total_b = min(total_b, MAX_B_QUOTAS_PER_PROVINCE)
        
        final_results.append({
            '省份': province_code_to_name.get(province_code, province_code),
            'A类': A_QUOTA_BASE,
            'B1(计算)': f"{b1:.2f}",
            'B2(计算)': b2,
            'B3(计算)': b3,
            'B总名额(计算)': total_b,
            '总名额': A_QUOTA_BASE + total_b
        })
        
    # 5. 显示结果
    result_df = pd.DataFrame(final_results)
    print("\n--- NOI2025省队名额计算结果 ---")
    print(result_df.to_string())

    # 将结果保存到CSV文件
    try:
        output_filename = "noi2025_calculated_quotas.csv"
        result_df.to_csv(output_filename, index=False, encoding='utf-8-sig')
        print(f"\n计算结果已成功保存到: {output_filename}")
    except Exception as e:
        print(f"\n保存结果到CSV文件时出错: {e}")


if __name__ == "__main__":
    calculate_quotas()