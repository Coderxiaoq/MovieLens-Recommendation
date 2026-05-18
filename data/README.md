# 数据文件夹

此文件夹用于存放 MovieLens 数据集。

## 文件夹结构

```
data/
├── ml-latest-small/     # MovieLens 小数据集（推荐用于测试和开发）
│   ├── ratings.csv      # 用户评分数据 (userId, movieId, rating, timestamp)
│   ├── movies.csv       # 电影信息 (movieId, title, genres)
│   ├── tags.csv         # 用户标签 (userId, movieId, tag, timestamp)
│   ├── links.csv        # IMDB/TMDB 链接
│   └── README.txt       # 数据集说明
│
└── ml-latest/           # MovieLens 完整数据集
    ├── ratings.csv
    ├── movies.csv
    ├── tags.csv
    ├── links.csv
    ├── genome-scores.csv
    ├── genome-tags.csv
    └── README.txt
```

## 数据获取

### 方式一：从 MovieLens 官网下载
1. 访问 https://grouplens.org/datasets/movielens/
2. 下载所需的数据集版本：
   - **ml-latest-small** (~1MB) - 用于快速测试
   - **ml-latest** (~200MB) - 完整数据集
3. 解压到 `data/` 文件夹

### 方式二：使用 Python 脚本下载
```python
import urllib.request
import zipfile

# 下载小数据集
url = "https://files.grouplens.org/datasets/movielens/ml-latest-small.zip"
urllib.request.urlretrieve(url, "ml-latest-small.zip")

# 解压
with zipfile.ZipFile("ml-latest-small.zip", "r") as zip_ref:
    zip_ref.extractall("data/")
```

## 数据说明

### ratings.csv
- `userId`: 用户ID
- `movieId`: 电影ID
- `rating`: 评分（0.5-5.0，0.5为步长）
- `timestamp`: 时间戳

### movies.csv
- `movieId`: 电影ID
- `title`: 电影标题（年份）
- `genres`: 电影类型（用 | 分隔多个类型）

### tags.csv
- `userId`: 用户ID
- `movieId`: 电影ID
- `tag`: 用户标签
- `timestamp`: 时间戳

## 最小数据要求

应用至少需要以下文件运行：
- `ratings.csv` - 必需
- `movies.csv` - 必需
- `tags.csv` - 可选

## 数据大小参考

| 数据集 | 用户数 | 电影数 | 评分数 | 文件大小 |
|------|-------|-------|--------|---------|
| ml-latest-small | ~600 | ~9,000 | ~100K | ~1MB |
| ml-latest | ~280K | ~58K | ~27M | ~200MB |

## 注意事项

1. 确保文件编码为 UTF-8
2. CSV 文件应该有正确的列标题
3. 对于大数据集，首次加载可能需要几秒钟
4. 应用会自动缓存加载的数据以提高性能

## 许可证

MovieLens 数据集由 GroupLens Research 提供，详见：
https://grouplens.org/datasets/movielens/

## 隐私声明

MovieLens 数据已进行匿名处理，不包含真实用户信息。
