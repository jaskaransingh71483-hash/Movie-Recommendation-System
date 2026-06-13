# pipeline/engine.py
import joblib
import logging
import pathlib

# Resolve paths dynamically
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DATA_DIR / "engine.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

movie_db = None
similarity_matrix = None

def load_engine():
    """Lazily load clean metadata database and similarity models."""
    global movie_db, similarity_matrix
    if movie_db is not None and similarity_matrix is not None:
        return True
        
    db_path = DATA_DIR / "metadata_store.joblib"
    model_path = DATA_DIR / "similarity_model.joblib"
    
    if not db_path.exists() or not model_path.exists():
        logging.warning("⚠️ Recommendation model files are missing from data/.")
        return False
        
    try:
        logging.info("🔁 Loading recommendation engines...")
        movie_db = joblib.load(db_path)
        similarity_matrix = joblib.load(model_path)
        logging.info("✅ Core systems loaded successfully.")
        return True
    except Exception as e:
        logging.error("❌ Failed to initialize recommendation engine: %s", str(e))
        return False

def get_movie_titles():
    """Fetch sorted list of unique movie titles."""
    global movie_db
    if not load_engine():
        return []
    return sorted(movie_db["title"].dropna().unique())

def get_movie_genres():
    """Fetch sorted list of unique genres present in dataset."""
    global movie_db
    if not load_engine():
        return []
    genres_set = set()
    for val in movie_db["genres"].dropna().unique():
        # Clean and split space-separated genres
        for genre in val.split():
            if genre:
                genres_set.add(genre)
    return sorted(list(genres_set))

def get_movie_metadata(movie_name):
    """Retrieve full metadata dictionary for a specific movie title."""
    global movie_db
    if not load_engine():
        return None
    idx = movie_db[movie_db['title'].str.lower() == movie_name.lower()].index
    if len(idx) == 0:
        return None
    return movie_db.iloc[idx[0]].to_dict()

def get_movie_recommendations(movie_name, top_n=5, genre_filter=None):
    """Recommend movies similar to the given title, optionally filtered by genre."""
    global movie_db, similarity_matrix
    if not load_engine():
        return None
        
    logging.info("🎬 Querying recommendations for: '%s' (Genre Filter: %s)", movie_name, genre_filter)
    
    # Locate movie index
    idx = movie_db[movie_db['title'].str.lower() == movie_name.lower()].index
    if len(idx) == 0:
        logging.warning("⚠️ Movie '%s' not found in database.", movie_name)
        return None
    idx = idx[0]
    
    # Compute similarity rankings
    sim_scores = list(enumerate(similarity_matrix[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
    
    recommended_indices = []
    for m_idx, score in sim_scores:
        if m_idx == idx:
            continue # Skip the query movie itself
            
        # Optional genre filtering
        if genre_filter:
            genres = movie_db.iloc[m_idx]["genres"].split()
            if genre_filter not in genres:
                continue
                
        recommended_indices.append(m_idx)
        if len(recommended_indices) == top_n:
            break
            
    logging.info("✅ Recommended %d movies.", len(recommended_indices))
    
    # Return DataFrame of recommended movies
    result_df = movie_db.iloc[recommended_indices].copy().reset_index(drop=True)
    result_df.index = result_df.index + 1
    result_df.index.name = "S.No."
    return result_df
