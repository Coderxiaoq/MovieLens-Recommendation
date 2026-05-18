"""
数据加载模块
处理所有与数据加载相关的操作
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
from scipy.sparse import csr_matrix  # 导入稀疏矩阵库

from .config import DATA_DIR, RATINGS_FILE, MOVIES_FILE, TAGS_FILE


@st.cache_data
def load_data(dataset_name: str = "ml-latest"):
    """
    加载电影数据集
    
    Args:
        dataset_name: 数据集名称 ('ml-latest-small' 或 'ml-latest')
    
    Returns:
        movies, ratings, tags (DataFrame或None)
    """
    try:
        data_path = DATA_DIR / dataset_name
        
        if not data_path.exists():
            st.error(f"数据集路径不存在: {data_path}")
            return None, None, None
        
        # 1. 加载电影数据
        movies_file = data_path / MOVIES_FILE
        if not movies_file.exists():
            st.error(f"未找到 {MOVIES_FILE}")
            return None, None, None
        
        # 优化：直接指定数据类型，节省内存
        movies = pd.read_csv(movies_file)
        st.success("✅ 电影数据加载成功")
        
        # 2. 加载评分数据
        ratings_file = data_path / RATINGS_FILE
        if not ratings_file.exists():
            st.error(f"未找到 {RATINGS_FILE}")
            return None, None, None
        
        # 优化：rating 只有 0.5-5.0，使用 float32 足够，且比默认 float64 省一半内存
        ratings = pd.read_csv(ratings_file, dtype={'rating': 'float32'})
        st.success("✅ 评分数据加载成功")
        
        # 3. 加载标签数据（可选）
        tags = None
        tags_file = data_path / TAGS_FILE
        if tags_file.exists():
            tags = pd.read_csv(tags_file)
            st.success("✅ 标签数据加载成功")
        
        return movies, ratings, tags
    
    except Exception as e:
        st.error(f"数据加载失败: {str(e)}")
        return None, None, None


@st.cache_data
def preprocess_data(ratings: pd.DataFrame, movies: pd.DataFrame, min_ratings: int):
    """
    数据预处理：创建用户-电影评分稀疏矩阵
    
    核心修改：使用 scipy.sparse 替代 pivot_table 以避免内存溢出
    新增：同时过滤低频用户，进一步压缩矩阵规模
    
    Args:
        ratings: 评分数据
        movies: 电影数据
        min_ratings: 最小评分次数阈值（同时作用于电影和用户）
    
    Returns:
        user_movie_matrix (csr_matrix), filtered_ratings (DataFrame), user_mapping (dict), movie_mapping (dict)
    """
    # --- 1. 数据过滤 ---
    
    # 过滤冷门电影
    movie_counts = ratings.groupby('movieId').size()
    valid_movies = movie_counts[movie_counts >= min_ratings].index
    
    # 过滤不活跃用户 (防止矩阵行数过多)
    # 先基于有效电影过滤一次，再统计用户
    temp_ratings = ratings[ratings['movieId'].isin(valid_movies)]
    user_counts = temp_ratings.groupby('userId').size()
    valid_users = user_counts[user_counts >= min_ratings].index
    
    # 最终过滤
    filtered_ratings = temp_ratings[temp_ratings['userId'].isin(valid_users)].copy()
    
    st.info(f"过滤后数据规模: {len(filtered_ratings)} 条评分, {len(valid_users)} 用户, {len(valid_movies)} 电影")

    # --- 2. 构建稀疏矩阵映射 ---
    
    # 创建 ID 到 矩阵索引 的映射
    # 稀疏矩阵需要连续的整数索引 (0, 1, 2...)
    user_ids = sorted(valid_users)
    movie_ids = sorted(valid_movies)
    
    user_to_idx = {uid: i for i, uid in enumerate(user_ids)}
    movie_to_idx = {mid: i for i, mid in enumerate(movie_ids)}
    
    # 将原始 ID 转换为矩阵索引
    # 使用 .map() 向量化操作，速度极快
    row_indices = filtered_ratings['userId'].map(user_to_idx).values
    col_indices = filtered_ratings['movieId'].map(movie_to_idx).values
    rating_values = filtered_ratings['rating'].values
    
    # --- 3. 创建 CSR 稀疏矩阵 ---
    # CSR (Compressed Sparse Row) 格式非常适合推荐系统，因为它能快速进行矩阵切片和行操作
    user_movie_matrix = csr_matrix(
        (rating_values, (row_indices, col_indices)), 
        shape=(len(user_ids), len(movie_ids)),
        dtype=np.float32  # 显式指定数据类型
    )
    
    # 返回矩阵、过滤后的数据以及映射关系（后续推荐算法需要用到这些映射来还原ID）
    return user_movie_matrix, filtered_ratings, user_to_idx, movie_to_idx


def get_data_stats(ratings: pd.DataFrame, movies: pd.DataFrame) -> dict:
    """
    获取数据集统计信息
    
    Args:
        ratings: 评分数据
        movies: 电影数据
    
    Returns:
        包含统计信息的字典
    """
    return {
        "total_users": len(ratings['userId'].unique()),
        "total_movies": len(movies),
        "total_ratings": len(ratings),
        "avg_rating": float(ratings['rating'].mean()), # 转换为Python原生float以便JSON序列化
        "rating_std": float(ratings['rating'].std()),
    }