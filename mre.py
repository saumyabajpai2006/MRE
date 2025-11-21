import pandas as pd
from joblib import load
import os

# Get the absolute path to the models directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, 'recommender', 'models')

# Module-level caches to avoid reloading large files on every request
_DF = None
_SIM = None

def _load_models(mmap_mode='r'):
    """Lazy-loads and caches models. Attempts to memory-map the similarity array
    to avoid loading the entire matrix into RAM when possible.

    mmap_mode: passed to joblib.load; if it fails, falls back to default load.
    """
    global _DF, _SIM
    if _DF is None:
        df_path = os.path.join(MODELS_DIR, 'clean_movies.parquet')
        if not os.path.exists(df_path):
            raise FileNotFoundError(f"Missing {df_path}")
        _DF = pd.read_parquet(df_path)

    if _SIM is None:
        sim_path = os.path.join(MODELS_DIR, 'similarity.joblib')
        if not os.path.exists(sim_path):
            raise FileNotFoundError(f"Missing {sim_path}")
        try:
            # Try to memory-map large numpy arrays inside the joblib file.
            _SIM = load(sim_path, mmap_mode=mmap_mode)
        except TypeError:
            # Older joblib versions or incompatible contents may raise; fall back
            _SIM = load(sim_path)

    return _DF, _SIM

def get_id_from_movie(movie_name, df):
    try:
        return df[df['names'].str.lower() == movie_name.lower()].index.tolist()[0]
    except Exception:
        return -1

def get_random_movie_from_keyword(keyword, df):
    try:
        return df[df['overview'].str.lower().str.contains(keyword.lower())].sample(1).index.tolist()[0]
    except Exception:
        return -1

def get_recommendation(query='', by='name', count=10):
    df, sim = _load_models()
    print(f'query: {query}, by: {by}, count: {count}')
    match by:
        case 'name':
            movie_id = get_id_from_movie(query, df)
            if movie_id == -1:
                return 'Movie not found'
            else:
                # If sim[row] returns a numpy array or sparse row, handle both
                row = sim[movie_id]
                try:
                    scores = list(enumerate(row))
                except Exception:
                    # sparse matrix row (e.g., csr_matrix)
                    scores = list(enumerate(row.toarray().ravel()))
                scores = sorted(scores, key=lambda x: x[1], reverse=True)
                # Exclude the queried movie itself, return top `count`
                movie_indices = [i[0] for i in scores if i[0] != movie_id][:count]
                return df['names'].iloc[movie_indices].head(count).tolist()
        case 'word':
            movie_ids = get_random_movie_from_keyword(query, df)
            if movie_ids == -1:
                return 'Movie not found'
            else:
                row = sim[movie_ids]
                try:
                    scores = list(enumerate(row))
                except Exception:
                    scores = list(enumerate(row.toarray().ravel()))
                scores = sorted(scores, key=lambda x: x[1], reverse=True)
                movie_indices = [i[0] for i in scores if i[0] != movie_ids][:count]
                return df['names'].iloc[movie_indices].head(count).tolist()


if __name__ == '__main__':
    print(get_recommendation('inception', by='name', count=10))