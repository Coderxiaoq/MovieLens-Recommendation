"""
项目配置文件
"""

import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 数据目录
DATA_DIR = PROJECT_ROOT / "data"
ML_LATEST_SMALL = DATA_DIR / "ml-latest-small"
ML_LATEST = DATA_DIR / "ml-latest"

# 数据文件
RATINGS_FILE = "ratings.csv"
MOVIES_FILE = "movies.csv"
TAGS_FILE = "tags.csv"
LINKS_FILE = "links.csv"
GENOME_SCORES_FILE = "genome-scores.csv"
GENOME_TAGS_FILE = "genome-tags.csv"

# 应用配置
APP_CONFIG = {
    "page_title": "电影推荐系统",
    "page_icon": "🎬",
    "layout": "wide",
}

# 推荐系统参数
RECOMMEND_CONFIG = {
    "min_ratings_default": 10,
    "top_n_default": 10,
    "min_ratings_range": (1, 50),
    "top_n_range": (1, 20),
}

# 分析参数
ANALYSIS_CONFIG = {
    "high_rating_threshold_default": 4.0,
    "min_support_default": 10,
    "high_rating_range": (2.0, 5.0),
    "min_support_range": (2, 50),
}

# 缓存配置
CACHE_CONFIG = {
    "ttl": 3600,  # 1小时
}
