"""
推荐模块
处理电影推荐相关的UI和逻辑
"""

import streamlit as st
import pandas as pd
from modules.utils import (
    search_movies, get_recommendations,
    get_user_based_recommendations, compute_similarity,
    compute_user_similarity
)


def recommend_module(
    movies: pd.DataFrame,
    ratings: pd.DataFrame,
    filtered_ratings: pd.DataFrame,
    user_movie_matrix,      # 用户-电影矩阵 (csr_matrix)
    movie_to_idx: dict,     # 电影ID -> 矩阵列索引
    user_to_idx: dict,      # 用户ID -> 矩阵行索引
    top_n: int = 10
):
    """
    电影推荐模块
    """
    st.header("🎬 智能电影推荐系统")
    
    # 侧边栏：推荐模式选择
    st.sidebar.header("⚙️ 推荐设置")
    mode = st.sidebar.radio(
        "推荐模式",
        ["基于内容的推荐", "基于用户的协同过滤"],
        index=0
    )

    # 顶部统计信息（使用折叠面板）
    with st.expander("📊 查看数据集统计", expanded=False):
        col_a, col_b, col_c, col_d = st.columns(4)
        with col_a:
            st.metric("用户数", f"{len(ratings['userId'].unique()):,}")
        with col_b:
            st.metric("电影数", f"{len(movies):,}")
        with col_c:
            st.metric("总评分数", f"{len(filtered_ratings):,}")
        with col_d:
            st.metric("矩阵稀疏度", "99.x%")

    # --- 模式 1: 基于内容的推荐 ---
    if mode == "基于内容的推荐":

        similarity_df = compute_similarity(user_movie_matrix, movie_to_idx)

        st.subheader("🔍 找相似电影")
        st.markdown("输入一部你喜欢的电影，我们将为你推荐风格相似的其他影片。")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            movie_query = st.text_input(
                "搜索电影名称",
                placeholder="例如：Toy Story (1995)",
                label_visibility="collapsed"
            )
            
            if movie_query:
                search_results = search_movies(movie_query, movies)
                
                if not search_results.empty:
                    # 格式化显示选项
                    movie_options = search_results.apply(
                        lambda x: f"{x['title']} (ID:{x['movieId']})", axis=1
                    ).tolist()
                    
                    selected_movie_str = st.selectbox(
                        "选择电影",
                        movie_options,
                        key="select_movie_content"
                    )
                    
                    if selected_movie_str:
                        # 提取 movieId
                        selected_movie_id = int(selected_movie_str.split('(ID:')[-1].rstrip(')'))
                        
                        # 调用推荐逻辑
                        recommendations = get_recommendations(
                            selected_movie_id,
                            similarity_df,
                            movies,
                            top_n
                        )
                        
                        if not recommendations.empty:
                            st.success(f"基于 **{search_results[search_results['movieId']==selected_movie_id].iloc[0]['title']}** 的推荐结果：")
                            display_recommendations(recommendations)
                        else:
                            st.warning("未找到相似电影，可能是该电影数据较冷门。")
                else:
                    st.info("未找到匹配的电影，请尝试其他关键词。")
        
        with col2:
            st.markdown("### 💡 热门高分电影")
            display_popular_movies(filtered_ratings, movies, limit=5)

    # --- 模式 2: 基于用户的协同过滤 ---
    elif mode == "基于用户的协同过滤":
        st.subheader("👤 个性化推荐")
        st.markdown("输入用户ID，我们将根据该用户的评分历史，预测他可能喜欢的电影。")

        if user_movie_matrix is not None:
            # 计算用户相似度（缓存）
            user_similarity_df = compute_user_similarity(user_movie_matrix, user_to_idx)

            col1, col2 = st.columns([1, 2])

            with col1:
                # 展示输入区域内的有效用户 ID 范围
                valid_user_ids = sorted(user_to_idx.keys())
                sample_user = valid_user_ids[0]
                user_id = st.number_input(
                    "输入用户 ID",
                    min_value=min(valid_user_ids),
                    max_value=max(valid_user_ids),
                    value=int(sample_user),
                    step=1,
                    label_visibility="collapsed"
                )
                if st.button("生成推荐", type="primary"):
                    try:
                        user_recs = get_user_based_recommendations(
                            user_id,
                            user_movie_matrix,
                            user_similarity_df,
                            user_to_idx,
                            movie_to_idx,
                            movies,
                            top_n
                        )

                        if not user_recs.empty:
                            st.success(f"为 **用户 {user_id}** 生成的个性化推荐：")
                            display_recommendations(user_recs)
                        else:
                            st.warning("未找到足够的相似用户或推荐结果。")

                    except Exception as e:
                        st.error(f"推荐计算出错: {e}")

            with col2:
                # 展示该用户的历史评分
                st.markdown(f"#### 用户 {user_id} 的历史评分")
                user_history = filtered_ratings[filtered_ratings['userId'] == user_id]
                if not user_history.empty:
                    user_history = user_history.merge(movies[['movieId', 'title']], on='movieId')
                    st.dataframe(
                        user_history[['title', 'rating']].sort_values('rating', ascending=False),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.warning("该用户无评分记录")
        else:
            st.warning("系统未加载用户评分矩阵，无法进行协同过滤推荐。")


def display_recommendations(df: pd.DataFrame):
    """美化推荐结果展示"""
    score_col = 'similarity_score' if 'similarity_score' in df.columns else 'predicted_score'
    label = "相似度" if score_col == 'similarity_score' else "预测分"
    for i, (_, row) in enumerate(df.iterrows(), 1):
        with st.container():
            col_title, col_score = st.columns([4, 1])
            with col_title:
                st.write(f"**{i}. {row['title']}**")
            with col_score:
                st.metric(label, f"{row[score_col]:.2f}")
            st.divider()


def display_popular_movies(data: pd.DataFrame, movies: pd.DataFrame, limit: int = 10):
    """展示热门电影"""
    movie_stats = data.groupby('movieId').agg({
        'rating': ['count', 'mean']
    }).round(2)
    movie_stats.columns = ['count', 'mean_rating']
    movie_stats = movie_stats.reset_index()
    
    popular = movie_stats.merge(movies[['movieId', 'title']], on='movieId')
    popular = popular[popular['count'] >= 10] # 至少10人评分
    popular = popular.sort_values('count', ascending=False).head(limit)
    
    for i, (_, m) in enumerate(popular.iterrows(), 1):
        st.write(
            f"**{i}. {m['title']}** \n\n 评分: **{m['mean_rating']:.2f}⭐** ({int(m['count'])}人)"
        )