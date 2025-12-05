import os
import re
import requests
from bs4 import BeautifulSoup
import time
import random

# ==============================================================================
# 配置
# ==============================================================================
# 基础URL
BASE_URL = "https://yundouxueyuan.com"
# 比赛列表页面的URL模板
CONTEST_LIST_URL_TEMPLATE = "https://yundouxueyuan.com/d/NOIPC/contest?page={page_num}"
# 要爬取的页数
PAGES_TO_SCRAPE = 2
# 保存结果的目录
OUTPUT_DIR = "results"
# 下载间隔范围（秒），每次下载会随机选择一个延迟
MIN_DOWNLOAD_DELAY = 5
MAX_DOWNLOAD_DELAY = 10

# 重试配置
MAX_RETRIES = 40000000               # 最大重试次数
RETRY_BACKOFF_FACTOR = 8      # 重试等待时间的基数（秒）。第一次重试等待5s，第二次10s，第三次20s...
RETRY_JITTER = 10              # 重试等待时间的随机抖动范围（秒）

# 请求头
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    # 如果需要，请在此处替换为您的Cookie
    'Cookie': 'YOUR_COOKIE_HERE'
}
# ==============================================================================

def sanitize_filename(name):
    """
    清理字符串，使其成为一个有效的文件名。
    移除特殊字符，并将空格替换为下划线。
    """
    name = re.sub(r'【※ 官方数据】', '', name).strip()
    return re.sub(r'[\\/*?:"><|]', "", name).replace(' ', '_')

def scrape_contests():
    """
    主函数，用于爬取比赛数据。
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"创建目录: {OUTPUT_DIR}")

    for page_num in range(1, PAGES_TO_SCRAPE + 1):
        list_url = CONTEST_LIST_URL_TEMPLATE.format(page_num=page_num)
        print(f"\n正在爬取比赛列表第 {page_num} 页: {list_url}")

        try:
            response = requests.get(list_url, headers=HEADERS)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            contest_links = soup.select('h1.contest__title a[href*="/d/NOIPC/contest/"]')

            if not contest_links:
                print(f"在第 {page_num} 页没有找到比赛。")
                continue

            for link in contest_links:
                contest_name = link.text.strip()
                
                if "NOIP" in contest_name:
                    contest_path = link['href']
                    contest_id = contest_path.split('/')[-1]
                    print(f"  > 找到NOIP比赛: '{contest_name}' (ID: {contest_id})")

                    csv_download_url = f"{BASE_URL}{contest_path}/scoreboard/csv"
                    
                    # 添加下载前的随机延迟
                    delay = random.uniform(MIN_DOWNLOAD_DELAY, MAX_DOWNLOAD_DELAY)
                    print(f"    - 暂停 {delay:.2f} 秒...")
                    time.sleep(delay)

                    # --- 下载与重试逻辑 ---
                    for attempt in range(MAX_RETRIES):
                        try:
                            print(f"    - 正在下载 (尝试 {attempt + 1}/{MAX_RETRIES}): {csv_download_url}")
                            csv_response = requests.get(csv_download_url, headers=HEADERS)
                            csv_response.raise_for_status()
                            
                            filename = sanitize_filename(contest_name) + ".csv"
                            filepath = os.path.join(OUTPUT_DIR, filename)
                            
                            with open(filepath, 'wb') as f:
                                f.write(csv_response.content)
                            print(f"    - 成功保存到: {filepath}")
                            break # 下载成功，跳出重试循环

                        except requests.exceptions.RequestException as e:
                            print(f"    - 尝试 {attempt + 1} 失败: {e}")
                            if attempt < MAX_RETRIES - 1:
                                # 计算下一次重试的等待时间（指数退避 + 随机抖动）
                                backoff_time = RETRY_BACKOFF_FACTOR * (2 ** attempt)
                                retry_delay = backoff_time + random.uniform(0, RETRY_JITTER)
                                print(f"    - 等待 {retry_delay:.2f} 秒后重试...")
                                time.sleep(retry_delay)
                            else:
                                print(f"    - 所有重试均失败，放弃下载: {contest_name}")
                    # --- 重试逻辑结束 ---

        except requests.exceptions.RequestException as e:
            print(f"访问比赛列表第 {page_num} 页失败: {e}")

if __name__ == "__main__":
    scrape_contests()
