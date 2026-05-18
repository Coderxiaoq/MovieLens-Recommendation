"""
电影推荐系统主应用
模块化设计，分离数据和逻辑
"""

import streamlit as st
import warnings
warnings.filterwarnings('ignore')

from modules import (
    load_data,
    preprocess_data,
    recommend_module,
    rating_analysis_module,
    genre_analysis_module,
    user_behavior_module,
    frequent_pattern_module,
)
from modules.config import APP_CONFIG, RECOMMEND_CONFIG

# 页面配置
st.set_page_config(**APP_CONFIG)

# 标题
st.title("🎬 MovieLens 电影推荐系统")
st.markdown("基于协同过滤的电影推荐 | 完整数据分析套件")

# 侧边栏
st.sidebar.header("⚙️ 设置")

# 数据集选择
data_folder = st.sidebar.selectbox(
    "选择数据集",
    ["ml-latest-small", "ml-latest"],
    index=0
)

# 参数配置
min_ratings = st.sidebar.slider(
    "最小评分次数",
    *RECOMMEND_CONFIG["min_ratings_range"],
    RECOMMEND_CONFIG["min_ratings_default"]
)

top_n = st.sidebar.slider(
    "推荐数量",
    *RECOMMEND_CONFIG["top_n_range"],
    RECOMMEND_CONFIG["top_n_default"]
)

# 分析模块选择
analysis_mode = st.sidebar.radio(
    "选择分析模块",
    [
        "🔍 电影推荐",
        "📊 评分分析",
        "🎭 类型偏好",
        "👥 用户行为",
        "🔗 频繁组合"
    ]
)

# ==================== 数据加载 ====================
st.sidebar.markdown("---")
st.sidebar.subheader("📂 数据加载")

with st.spinner("正在加载数据..."):
    movies, ratings, tags = load_data(data_folder)

if movies is None or ratings is None:
    st.stop()

# ==================== 数据预处理 ====================
with st.spinner("正在预处理数据..."):
    user_movie_matrix, filtered_ratings, user_to_idx, movie_to_idx = preprocess_data(ratings, movies, min_ratings)

st.sidebar.success("✅ 数据加载完成！")

# ==================== 主内容区域 ====================

# 电影推荐模块
if analysis_mode == "🔍 电影推荐":
    recommend_module(
        movies,
        ratings,
        filtered_ratings,
        user_movie_matrix,
        movie_to_idx,
        user_to_idx,
        top_n
    )

# 评分分析模块
elif analysis_mode == "📊 评分分析":
    rating_analysis_module(filtered_ratings)

# 类型偏好模块
elif analysis_mode == "🎭 类型偏好":
    genre_analysis_module(movies)

# 用户行为模块
elif analysis_mode == "👥 用户行为":
    user_behavior_module(filtered_ratings)

# 频繁模式挖掘模块
elif analysis_mode == "🔗 频繁组合":
    frequent_pattern_module(filtered_ratings, movies)

# ==================== 页脚 ====================
st.markdown("---")
st.markdown("""
<div style="text-align: center">
    <p style="color: #666;">🎬 MovieLens 电影推荐系统</p>
    <p style="color: #999; font-size: 12px;">技术栈: Python • Streamlit • Pandas • Scikit-learn • Matplotlib</p>
    <p style="color: #ccc; font-size: 11px;">项目结构: 数据分离 • 模块化设计 • 可扩展架构</p>
</div>
""", unsafe_allow_html=True)
