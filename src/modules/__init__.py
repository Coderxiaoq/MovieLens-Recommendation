"""
模块包初始化文件
"""

from .data_loader import load_data, preprocess_data, get_data_stats
from .utils import search_movies, compute_similarity, get_recommendations, parse_genres, get_frequent_pairs
from .recommend import recommend_module
from .analysis import (
    rating_analysis_module,
    genre_analysis_module,
    user_behavior_module,
    frequent_pattern_module
)

__all__ = [
    # data_loader
    'load_data',
    'preprocess_data',
    'get_data_stats',
    
    # utils
    'search_movies',
    'compute_similarity',
    'get_recommendations',
    'parse_genres',
    'get_frequent_pairs',
    
    # recommend
    'recommend_module',
    
    # analysis
    'rating_analysis_module',
    'genre_analysis_module',
    'user_behavior_module',
    'frequent_pattern_module',
]
