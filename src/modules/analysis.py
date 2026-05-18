"""
分析模块
处理数据分析相关的UI和可视化
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from .utils import parse_genres, get_frequent_pairs

# --- 全局字体配置 (解决中文乱码) ---
# 尝试设置中文字体，Windows通常是SimHei，Mac是Arial Unicode MS或Heiti TC
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS', 'Microsoft YaHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

def rating_analysis_module(filtered_ratings: pd.DataFrame):
    """评分分析模块"""
    st.header("📊 评分分布与统计分析")
    
    if filtered_ratings.empty:
        st.warning("当前没有评分数据可供分析。")
        return

    ratings_values = filtered_ratings['rating'].values
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("平均评分", f"{np.mean(ratings_values):.2f}⭐")
    with col2:
        st.metric("中位数", f"{np.median(ratings_values):.2f}")
    with col3:
        st.metric("标准差", f"{np.std(ratings_values):.2f}")
    with col4:
        high_pct = len(ratings_values[ratings_values >= 4]) / len(ratings_values) * 100
        st.metric("高评分占比", f"{high_pct:.1f}%")
    
    # 评分分布
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # 直方图
    axes[0].hist(ratings_values, bins=20, color='#1f77b4', edgecolor='black', alpha=0.7)
    axes[0].set_xlabel('评分', fontsize=11)
    axes[0].set_ylabel('频次', fontsize=11)
    axes[0].set_title('评分分布直方图', fontsize=12, fontweight='bold')
    axes[0].grid(True, alpha=0.3)
    
    # 概率分布
    rating_counts = pd.Series(ratings_values).value_counts().sort_index()
    axes[1].bar(
        rating_counts.index,
        rating_counts.values / len(ratings_values) * 100,
        color='#ff7f0e',
        edgecolor='black',
        alpha=0.7
    )
    axes[1].set_xlabel('评分', fontsize=11)
    axes[1].set_ylabel('概率 (%)', fontsize=11)
    axes[1].set_title('评分概率分布', fontsize=12, fontweight='bold')
    axes[1].grid(True, alpha=0.3, axis='y')
    
    st.pyplot(fig)
    
    # 详细分布表
    st.subheader("评分详细分布")
    distribution_data = []
    for rating in sorted(rating_counts.index):
        count = rating_counts[rating]
        percentage = count / len(ratings_values) * 100
        distribution_data.append({
            '评分': f"{rating}⭐",
            '数量': int(count),
            '占比': f"{percentage:.2f}%"
        })
    
    dist_df = pd.DataFrame(distribution_data)
    st.dataframe(dist_df, use_container_width=True)


def genre_analysis_module(movies: pd.DataFrame):
    """电影类型分析模块"""
    st.header("🎭 电影类型偏好分析")
    
    # 解析类型
    genre_count = parse_genres(movies)
    
    if not genre_count:
        st.warning("未找到类型信息或数据为空")
        return
    
    # 排序
    sorted_genres = sorted(genre_count.items(), key=lambda x: x[1], reverse=True)
    
    # 检查是否有数据
    if len(sorted_genres) == 0:
        st.warning("没有类型数据")
        return

    genres_list, counts_list = zip(*sorted_genres[:15])
    
    # 显示类型分布
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        st.subheader("类型分布（Top 15）")
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.barh(genres_list, counts_list, color='#2ca02c', edgecolor='black', alpha=0.8)
        ax.set_xlabel('电影数量', fontsize=11)
        ax.set_title('电影类型分布', fontsize=12, fontweight='bold')
        ax.invert_yaxis()
        ax.grid(True, alpha=0.3, axis='x')
        
        # 添加数值标签
        for i, (genre, count) in enumerate(zip(genres_list, counts_list)):
            ax.text(count, i, f' {count}', va='center', fontsize=9)
        
        st.pyplot(fig)
    
    with col2:
        st.subheader("类型统计")
        for i, (genre, count) in enumerate(sorted_genres[:10], 1):
            st.write(f"**{i}. {genre}**: {count} 部电影")


def user_behavior_module(filtered_ratings: pd.DataFrame):
    """用户行为分析模块"""
    st.header("👥 用户评分行为分析")
    
    if filtered_ratings.empty:
        st.warning("没有评分数据可供分析。")
        return

    # 计算用户统计
    user_stats = filtered_ratings.groupby('userId').agg({
        'rating': ['count', 'mean', 'std', 'min', 'max']
    }).round(2)
    user_stats.columns = ['rating_count', 'mean_rating', 'std_rating', 'min_rating', 'max_rating']
    user_stats = user_stats.reset_index()
    user_stats['rating_count'] = user_stats['rating_count'].astype(int)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("平均评分次数", f"{user_stats['rating_count'].mean():.0f}")
    with col2:
        st.metric("平均评分分数", f"{user_stats['mean_rating'].mean():.2f}⭐")
    with col3:
        st.metric("平均评分分散度", f"{user_stats['std_rating'].mean():.2f}")
    with col4:
        strict_pct = (user_stats['mean_rating'] < 3).sum() / len(user_stats) * 100
        st.metric("严格用户比例", f"{strict_pct:.1f}%")
    
    # 用户活跃度分布
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("用户活跃度分布")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(user_stats['rating_count'], bins=30, color='#d62728', edgecolor='black', alpha=0.7)
        ax.set_xlabel('评分数量', fontsize=11)
        ax.set_ylabel('用户数', fontsize=11)
        ax.set_title('用户活跃度分布', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        st.pyplot(fig)
    
    with col2:
        st.subheader("用户评分风格分布")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.hist(user_stats['mean_rating'], bins=20, color='#9467bd', edgecolor='black', alpha=0.7)
        ax.set_xlabel('平均评分', fontsize=11)
        ax.set_ylabel('用户数', fontsize=11)
        ax.set_title('用户平均评分分布（体现宽松/严格程度）', fontsize=12, fontweight='bold')
        ax.grid(True, alpha=0.3, axis='y')
        st.pyplot(fig)
    
    # 用户分类
    st.subheader("👥 用户分类统计")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        strict_users = (user_stats['mean_rating'] < 3).sum()
        st.metric("严格型用户", strict_users, f"({strict_users/len(user_stats)*100:.1f}%)")
        st.caption("倾向打低分（<3分）")
    
    with col2:
        moderate_users = ((user_stats['mean_rating'] >= 3) & (user_stats['mean_rating'] < 4)).sum()
        st.metric("中立型用户", moderate_users, f"({moderate_users/len(user_stats)*100:.1f}%)")
        st.caption("评分相对均衡")
    
    with col3:
        generous_users = (user_stats['mean_rating'] >= 4).sum()
        st.metric("宽松型用户", generous_users, f"({generous_users/len(user_stats)*100:.1f}%)")
        st.caption("倾向打高分（≥4分）")


def frequent_pattern_module(filtered_ratings: pd.DataFrame, movies: pd.DataFrame):
    """频繁模式挖掘模块"""
    st.header("🔗 高评分电影频繁组合（基于DHP思路）")
    
    st.info("📌 该模块基于 MATLAB 代码的 DHP 频繁模式挖掘方法，找出经常一起被高评分的电影组合")
    
    if filtered_ratings.empty:
        st.warning("没有评分数据可供分析。")
        return

    # 二值化评分
    high_rating_threshold = st.slider("高评分阈值", 2.0, 5.0, 4.0, 0.5)
    
    R_binary = (filtered_ratings['rating'] >= high_rating_threshold).astype(int)
    
    st.metric(
        "高评分占比",
        f"{R_binary.sum() / len(R_binary) * 100:.2f}%",
        f"(阈值: {high_rating_threshold}分)"
    )
    
    # 计算频繁2项集
    st.subheader("频繁电影组合（Top 20）")
    min_support = st.slider("最小支持度（用户数）", 2, 50, 10)
    
    try:
        frequent_df = get_frequent_pairs(
            filtered_ratings,
            high_rating_threshold,
            min_support
        )
        
        if not frequent_df.empty:
            frequent_df_display = frequent_df.head(20).copy()
            
            # 补充电影标题
            movie_dict = dict(zip(movies['movieId'], movies['title']))
            frequent_df_display['movie1_title'] = frequent_df_display['movie1_id'].map(movie_dict)
            frequent_df_display['movie2_title'] = frequent_df_display['movie2_id'].map(movie_dict)
            
            for idx, row in frequent_df_display.iterrows():
                st.write(f"**{row['movie1_title']}** ↔ **{row['movie2_title']}**")
                st.write(f"   共同高评分用户数: {row['common_users']} 人")
                st.divider()
        else:
            st.warning("未找到满足条件的频繁组合，请尝试降低最小支持度或调整阈值。")
    except Exception as e:
        st.error(f"频繁模式挖掘出错: {e}")