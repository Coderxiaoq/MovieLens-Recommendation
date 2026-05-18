"""
工具函数模块
包含推荐、搜索、相似度计算等通用函数
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import streamlit as st


def search_movies(query: str, movies_df: pd.DataFrame) -> pd.DataFrame:
    """
    搜索电影（支持模糊匹配）
    """
    if not query:
        return pd.DataFrame()
        
    query = query.lower()
    # 增加 na=False 防止空值报错
    matches = movies_df[
        movies_df['title'].str.lower().str.contains(query, na=False)
    ]
    return matches


@st.cache_data
def compute_similarity(_sparse_matrix: csr_matrix, movie_mapping: dict) -> pd.DataFrame:
    """
    计算电影相似度矩阵（基于协同过滤）
    
    修改点：
    1. 接收稀疏矩阵 (csr_matrix) 而非 DataFrame
    2. 接收 movie_mapping 以还原索引
    """
    # cosine_similarity 支持稀疏矩阵输入，且效率很高
    # 注意：这里计算的是 Item-Item 相似度，所以直接传入矩阵即可（sklearn会自动处理行向量）
    # 如果想计算 User-User 相似度，需要传入 sparse_matrix.T
    similarity_matrix = cosine_similarity(_sparse_matrix.T) # 转置：行变为电影，列变为用户
    
    # 将 numpy 数组转换回 DataFrame，并使用原始 movieId 作为索引
    movie_ids = list(movie_mapping.keys())
    similarity_df = pd.DataFrame(
        similarity_matrix, 
        index=movie_ids, 
        columns=movie_ids
    )
    
    return similarity_df


def get_recommendations(
    movie_id: int,
    similarity_df: pd.DataFrame,
    movies_df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    获取推荐电影
    """
    if movie_id not in similarity_df.index:
        return pd.DataFrame()
    
    # 获取该电影与其他电影的相似度
    similar_scores = similarity_df.loc[movie_id]
    
    # 排序并排除自己 (iloc[1:])
    # 注意：sort_values 返回的是 Series，index 是 movieId
    similar_movies = similar_scores.sort_values(ascending=False).iloc[1:top_n+1]
    
    # 获取电影详情
    recommendations = movies_df[
        movies_df['movieId'].isin(similar_movies.index)
    ].copy()
    
    # 映射相似度分数
    recommendations['similarity_score'] = recommendations['movieId'].map(similar_scores)
    
    return recommendations.sort_values('similarity_score', ascending=False)


def parse_genres(movies_df: pd.DataFrame) -> dict:
    """
    解析电影类型
    """
    genre_count = {}
    
    for genres_str in movies_df['genres']:
        if pd.isna(genres_str) or genres_str == '(no genres listed)':
            continue
        
        # 确保是字符串
        if isinstance(genres_str, str):
            for genre in genres_str.split('|'):
                genre = genre.strip()
                if genre:
                    genre_count[genre] = genre_count.get(genre, 0) + 1
    
    return genre_count


def get_frequent_pairs(
    filtered_ratings: pd.DataFrame,
    high_rating_threshold: float = 4.0,
    min_support: int = 10
) -> pd.DataFrame:
    """
    挖掘频繁电影组合（基于矩阵乘法优化）
    
    修改点：
    使用矩阵乘法代替双重循环，速度提升 100 倍以上。
    """
    if filtered_ratings.empty:
        return pd.DataFrame()

    # 1. 二值化：只保留高评分记录
    high_ratings = filtered_ratings[filtered_ratings['rating'] >= high_rating_threshold].copy()
    
    if high_ratings.empty:
        return pd.DataFrame()

    # 2. 构建 用户-电影 二值矩阵 (1 表示高分，0 表示未高分)
    # 使用 pivot_table 创建稀疏形式的 DataFrame
    user_movie_matrix = high_ratings.pivot_table(
        index='userId', 
        columns='movieId', 
        values='rating', 
        fill_value=0
    )
    
    # 转为 0/1 矩阵
    binary_matrix = (user_movie_matrix > 0).astype(int)
    
    # 3. 矩阵乘法计算共现次数
    # Matrix (Movies x Users) * Matrix (Users x Movies) = Matrix (Movies x Movies)
    # 结果矩阵中的 [i, j] 元素即为电影 i 和 j 被同一用户打高分的次数
    co_occurrence_matrix = binary_matrix.T.dot(binary_matrix)
    
    # 4. 提取上三角矩阵（避免重复 A-B 和 B-A，且排除 A-A）
    # 将矩阵转换为长格式 DataFrame
    co_occurrence_df = co_occurrence_matrix.unstack().reset_index()
    co_occurrence_df.columns = ['movie1_id', 'movie2_id', 'common_users']
    
    # 过滤：只保留 movie1 < movie2 (上三角)，且 common_users >= min_support
    # 注意：这里假设 movieId 是可比较的整数
    frequent_pairs = co_occurrence_df[
        (co_occurrence_df['movie1_id'] < co_occurrence_df['movie2_id']) & 
        (co_occurrence_df['common_users'] >= min_support)
    ]
    
    return frequent_pairs.sort_values('common_users', ascending=False)


@st.cache_data
def compute_user_similarity(_user_movie_matrix, user_mapping: dict) -> pd.DataFrame:
    """
    计算用户相似度矩阵

    Args:
        _user_movie_matrix: 用户-电影评分矩阵 (csr_matrix)
        user_mapping: userId -> 矩阵行索引 的映射字典

    Returns:
        以 userId 为行列索引的相似度 DataFrame
    """
    user_similarity = cosine_similarity(_user_movie_matrix)
    user_ids = list(user_mapping.keys())
    similarity_df = pd.DataFrame(
        user_similarity,
        index=user_ids,
        columns=user_ids
    )
    return similarity_df


def get_user_based_recommendations(
    user_id: int,
    user_movie_matrix,          # csr_matrix
    user_similarity_df: pd.DataFrame,
    user_to_idx: dict,
    movie_to_idx: dict,
    movies_df: pd.DataFrame,
    top_n: int = 10
) -> pd.DataFrame:
    """
    基于用户的协同过滤推荐
    逻辑：找到最像的 K 个邻居 -> 加权计算他们喜欢的电影 -> 推荐给当前用户
    """
    if user_id not in user_similarity_df.index:
        return pd.DataFrame()

    # 1. 获取当前用户与其他所有用户的相似度
    sim_scores = user_similarity_df[user_id]

    # 2. 找出最相似的 Top K 个用户 (排除自己)
    k = min(50, len(sim_scores) - 1)
    similar_users = sim_scores.sort_values(ascending=False).iloc[1:k+1]

    # 3. 获取这些相似用户的矩阵行索引
    neighbor_rows = [user_to_idx[uid] for uid in similar_users.index]
    user_row = user_to_idx[user_id]

    # 4. 提取邻居评分并加权
    neighbor_ratings = user_movie_matrix[neighbor_rows, :]
    weights = similar_users.values.reshape(-1, 1)
    weighted_ratings = neighbor_ratings.multiply(weights)

    # 5. 汇总分数 (按列求和)
    total_scores = np.array(weighted_ratings.sum(axis=0)).flatten()

    # 6. 过滤掉当前用户已经看过的电影
    user_watched = np.array(user_movie_matrix[user_row, :].toarray()).flatten()
    unwatched_mask = (user_watched == 0)

    # 7. 构建 movieId -> score 映射，仅保留未看电影
    idx_to_movie = {i: mid for mid, i in movie_to_idx.items()}
    candidates = []
    for col_idx, score in enumerate(total_scores):
        if unwatched_mask[col_idx] and score > 0 and col_idx in idx_to_movie:
            candidates.append((idx_to_movie[col_idx], score))

    # 8. 排序取 Top N
    candidates.sort(key=lambda x: x[1], reverse=True)
    top_movie_ids = [m[0] for m in candidates[:top_n]]

    if not top_movie_ids:
        return pd.DataFrame()

    # 9. 获取电影详情
    recommendations = movies_df[movies_df['movieId'].isin(top_movie_ids)].copy()
    score_map = {m[0]: m[1] for m in candidates[:top_n]}
    recommendations['predicted_score'] = recommendations['movieId'].map(score_map)

    return recommendations.sort_values('predicted_score', ascending=False)