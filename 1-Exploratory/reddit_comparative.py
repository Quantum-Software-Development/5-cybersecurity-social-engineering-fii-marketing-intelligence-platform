import pathlib
import pandas as pd

# Path to the Reddit parquet file generated earlier in the pipeline
REDDIT_PATH = pathlib.Path(
    '/Users/fabicampanari/Desktop/project-fii-marketing-intelligence-platform/__notebooks/data/silver/reddit_articles.parquet'
)

if REDDIT_PATH.is_file():
    df_reddit = pd.read_parquet(REDDIT_PATH)
    # Simple comparative metric: average sentiment scores for positive and negative posts
    if 'sentiment_score' in df_reddit.columns:
        pos_mean = df_reddit[df_reddit['sentiment_score'] > 0]['sentiment_score'].mean()
        neg_mean = df_reddit[df_reddit['sentiment_score'] < 0]['sentiment_score'].mean()
        reddit_comparative = f"Positivos ≈ {pos_mean:.2f} | Negativos ≈ {neg_mean:.2f}"
    else:
        reddit_comparative = "N/A (coluna sentiment_score ausente)"
else:
    reddit_comparative = "N/A (dados Reddit não encontrados)"

__all__ = ['reddit_comparative']
