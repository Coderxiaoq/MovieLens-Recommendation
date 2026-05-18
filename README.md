# 🎬 MovieLens 电影推荐系统

基于 MovieLens 数据集的完整电影推荐和数据分析系统，采用模块化设计，实现了协同过滤推荐和频繁模式挖掘。

## 📊 项目结构

```
.
├── data/                          # 数据文件夹（原始数据存放位置）
│   ├── ml-latest-small/          # 小数据集
│   └── ml-latest/                # 完整数据集
├── Matlab/                       # 利用MATLAB对数据进行分析

├── src/                           # 可视化源代码文件夹
│   ├── __init__.py
│   ├── app.py                    # 主应用入口
│   ├── config.py                 # 项目配置
│   │
│   └── modules/                  # 功能模块
│       ├── __init__.py
│       ├── data_loader.py        # 数据加载模块
│       ├── utils.py              # 工具函数（搜索、推荐、相似度计算）
│       ├── recommend.py          # 推荐模块
│       └── analysis.py           # 分析模块
│
├── notebooks/                     # Jupyter 笔记本
│
├── run.py                        # 应用启动脚本
├── requirements.txt              # 项目依赖
├── .gitignore                    # Git 忽略配置
└── README.md                     # 项目文档
```

## 🚀 快速开始

### 1. 环境配置

```bash
# 创建虚拟环境（如果还没有创建）
python -m venv .venv

# 激活虚拟环境
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 2. 数据准备

将 MovieLens 数据集放在 `data/` 文件夹中：
- `data/ml-latest-small/` - 小数据集（快速测试）
- `data/ml-latest/` - 完整数据集

每个数据集应包含以下文件：
- `ratings.csv` - 用户评分数据
- `movies.csv` - 电影信息
- `tags.csv` - 用户标签（可选）
- `links.csv` - IMDB/TMDB 链接（可选）

### 3. 运行应用

#### 方式一：使用启动脚本
```bash
python run.py
```

#### 方式二：直接运行 Streamlit
```bash
# 激活虚拟环境后
streamlit run src/app.py
```

然后在浏览器中打开 `http://localhost:8501`

## 📱 功能模块

### 1. 🔍 电影推荐
- 电影搜索（模糊匹配）
- 基于协同过滤的推荐
- 显示相似度评分
- 热门电影排行榜

### 2. 📊 评分分析
- 评分统计（平均值、中位数、标准差）
- 评分分布直方图
- 评分概率分布
- 详细的评分分布表

### 3. 🎭 类型偏好
- 电影类型分布（Top 15）
- 类型统计数据
- 可视化类型信息

### 4. 👥 用户行为
- 用户活跃度分布
- 用户评分风格分布
- 用户分类统计
  - 严格型用户（评分 < 3）
  - 中立型用户（评分 3-4）
  - 宽松型用户（评分 ≥ 4）

### 5. 🔗 频繁组合
- 基于 DHP 算法的频繁模式挖掘
- 找出常被一起高评分的电影对
- 可调节的参数（阈值、最小支持度）

## 🎯 推荐系统实现思路
- 数据加载与预处理：`modules/data_loader.py` 中使用 `load_data()` 读取 CSV，`preprocess_data()` 过滤低频电影和低活跃用户，构建 `scipy.sparse.csr_matrix` 的用户-电影评分矩阵。
- 电影搜索：`modules/utils.py` 中的 `search_movies()` 支持模糊匹配电影标题，用于推荐入口的选择。
- 基于物品的协同过滤：`modules/utils.py` 中 `compute_similarity()` 对电影-用户评分矩阵转置后计算余弦相似度，得到电影之间的相似度矩阵；`get_recommendations()` 根据选中电影查找相似电影并返回推荐列表。
- 基于用户的协同过滤：`get_user_based_recommendations()` 通过计算用户相似度、选择最相似邻居、加权邻居评分，预测当前用户可能喜欢但未看过的电影。
- 频繁模式挖掘：`get_frequent_pairs()` 对高评分记录二值化后构建用户-电影矩阵，使用矩阵乘法计算电影共现次数，筛选出共同高评分的电影组合。
- UI 集成：`src/modules/recommend.py` 在 Streamlit 页面中实现搜索、选择、推荐结果展示和热门电影展示，形成从输入到推荐输出的完整流程。

## 🛠️ 技术栈

- **Web 框架**: Streamlit
- **数据处理**: Pandas, NumPy
- **机器学习**: Scikit-learn（余弦相似度、协同过滤）
- **可视化**: Matplotlib
- **Python 版本**: 3.9+

## 📦 模块说明

### `config.py`
项目全局配置，包括：
- 数据路径配置
- 应用设置（页面标题、布局等）
- 推荐系统参数
- 分析参数范围

### `modules/data_loader.py`
数据加载和预处理：
- `load_data()` - 加载 CSV 数据
- `preprocess_data()` - 创建用户-电影评分矩阵
- `get_data_stats()` - 获取数据统计信息

### `modules/utils.py`
通用工具函数：
- `search_movies()` - 电影搜索
- `compute_similarity()` - 计算相似度矩阵
- `get_recommendations()` - 获取推荐
- `parse_genres()` - 解析电影类型
- `get_frequent_pairs()` - 挖掘频繁项集

### `modules/recommend.py`
推荐相关 UI：
- `recommend_module()` - 推荐模块界面

### `modules/analysis.py`
分析相关 UI：
- `rating_analysis_module()` - 评分分析
- `genre_analysis_module()` - 类型分析
- `user_behavior_module()` - 用户行为分析
- `frequent_pattern_module()` - 频繁模式分析

## 💡 使用示例

### 搜索电影并获取推荐
1. 选择 "🔍 电影推荐" 模块
2. 在搜索框输入电影名（如 "Toy Story"）
3. 从结果中选择电影
4. 查看推荐的相似电影

### 分析评分分布
1. 选择 "📊 评分分析" 模块
2. 查看评分的统计指标
3. 观察评分分布的直方图和概率分布

### 挖掘频繁电影组合
1. 选择 "🔗 频繁组合" 模块
2. 调节"高评分阈值"和"最小支持度"
3. 查看经常被一起高评分的电影对

## ⚙️ 参数调节

### 侧边栏设置
- **数据集选择**: 选择 `ml-latest-small`（快速）或 `ml-latest`（完整）
- **最小评分次数**: 过滤评分次数少于此值的电影
- **推荐数量**: 显示的推荐电影数

### 模块内参数
- **高评分阈值**: 定义什么是"高评分"
- **最小支持度**: 频繁模式的最小出现次数

## 📈 性能优化
- 使用 Streamlit 的 `@st.cache_data` 装饰器缓存数据和计算结果
- 余弦相似度计算采用向量化实现
- 频繁模式挖掘限制搜索空间（最多 50 部电影）






