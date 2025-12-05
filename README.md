# NOI 省队名额计算器

本项目是一个用于计算和模拟NOI（全国青少年信息学奥林匹克竞赛）省队名额的工具。它严格遵循CCF官方发布的《NOI名额分配方案》，利用各省的NOIP（全国青少年信息学奥林匹克联赛）参赛人数和详细成绩数据，自动化地推算出A类和B类（B1, B2, B3）名额的分配情况。

## 项目特点

- **自动化计算**: 自动处理各省成绩，执行完整的B1（普及项）、B2（综合项）、B3（拔尖项）名额计算逻辑。
- **参数化模拟**: 核心计算参数（如全国B类总名额`S`、分段数`K1`、拔尖数`K2`等）均可在脚本中配置，方便进行不同场景的模拟和预测。
- **数据驱动**: 计算完全基于真实的NOIP参赛人数和成绩数据。
- **清晰的结果**: 输出详细的各省名额分配表，并保存为CSV文件，便于存档和分析。

## 项目结构

```
.
├── results/                     # 存放各省NOIP成绩CSV文件的目录
│   └── NOIP_2025_XX_批量测试.csv
├── .venv/                       # Python虚拟环境
├── calculate_noi_quotas.py      # 核心计算脚本
├── scraper.py                   # [工具] 用于从网站上爬取各省成绩的爬虫
├── generate_csv_from_text.py    # [工具] 用于从原始文本生成参赛人数CSV
├── noip2025_participants.csv    # [输入] 各省参赛人数数据 (由generate_csv脚本生成)
├── noi2025_calculated_quotas.csv # [输出] 最终计算出的省队名额分配结果
├── pyproject.toml               # 项目依赖定义 (使用uv管理)
├── requirements.txt             # 完整的依赖锁文件 (由uv生成)
└── README.md                    # 本文档
```

## 使用方法

### 1. 环境设置

本项目使用 [uv](https://github.com/astral-sh/uv) 进行快速的环境和依赖管理。

```bash
# 1. 创建虚拟环境
uv venv

# 2. 激活虚拟环境
# macOS / Linux
source .venv/bin/activate
# Windows
.venv\Scripts\activate

# 3. 安装所有依赖
uv pip sync requirements.txt
```

### 2. 数据准备

计算需要两类输入数据：

- **各省参赛人数**:
  运行 `generate_csv_from_text.py` 脚本，它会根据内置的原始文本数据，自动生成`noip2025_participants.csv`文件。该文件的省份列将使用标准的省份代码（如 'GD', 'SC'）。
  ```bash
  python generate_csv_from_text.py
  ```

- **各省NOIP成绩**:
  将所有省份的NOIP成绩CSV文件放入 `results/` 文件夹中。
  - **文件来源**: 您可以使用 `scraper.py` 爬虫脚本来下载这些文件。使用前请根据脚本内的提示配置好请求头（特别是Cookie，如果需要登录）。
  - **数据格式要求**: 成绩CSV文件必须包含`用户`和`总分数`两列。脚本会自动从`用户`列（如 'AH-0002'）中提取前两个字母作为省份代码。

### 3. 参数配置 (可选)

打开 `calculate_noi_quotas.py` 脚本，在文件顶部的配置区域，您可以根据需要调整核心计算参数，例如全国B类总名额 `S_TOTAL_B_QUOTAS` 等，以进行不同的测算。

```python
# ==============================================================================
# 核心假设与可配置参数 (根据 NOI2026 官方方案更新)
# ==============================================================================
S_TOTAL_B_QUOTAS = 150
K1_SEGMENTS = 5
K2_TOP_SCORES = 5
# ...
```

### 4. 执行计算

确保您的虚拟环境已激活，并且输入数据已准备就绪。

```bash
python calculate_noi_quotas.py
```

### 5. 查看结果

脚本执行后，会：
1.  在终端（控制台）中打印出详细的计算结果表格。
2.  将完整的计算结果保存到 `noi2025_calculated_quotas.csv` 文件中，供您查阅和使用。