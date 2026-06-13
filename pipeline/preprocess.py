# pipeline/preprocess.py
import pandas as pd
import re
import nltk
import joblib
import logging
import pathlib
import ssl
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Resolve paths dynamically
BASE_DIR = pathlib.Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(DATA_DIR / "preprocess.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)

logging.info("🚀 Initializing data pipeline preprocessing...")

# Avoid NLTK SSL certificate verification issues on macOS
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

nltk.download('punkt')
nltk.download('punkt_tab')
nltk.download('stopwords')

stop_words = set(stopwords.words('english'))

# Clean text tokens helper
def clean_text_tokens(text):
    text = re.sub(r"[^a-zA-Z0-9\s]", "", str(text))
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in stop_words]
    return " ".join(tokens)

# Load dataset
try:
    df = pd.read_csv(DATA_DIR / "movies.csv")
    logging.info("✅ Raw dataset loaded. Total rows: %d", len(df))
except Exception as e:
    logging.error("❌ Failed to load movies.csv: %s", str(e))
    raise e

# Define features to retain for UI display and recommendation
metadata_columns = [
    "title", "genres", "keywords", "overview", "tagline",
    "release_date", "runtime", "vote_average", "popularity",
    "cast", "director"
]

# Keep only relevant columns
df = df[metadata_columns].copy()

# Fill missing values with empty strings/default values
df["genres"] = df["genres"].fillna("")
df["keywords"] = df["keywords"].fillna("")
df["overview"] = df["overview"].fillna("")
df["tagline"] = df["tagline"].fillna("")
df["cast"] = df["cast"].fillna("")
df["director"] = df["director"].fillna("")
df["runtime"] = df["runtime"].fillna(0)
df["vote_average"] = df["vote_average"].fillna(0.0)
df["release_date"] = df["release_date"].fillna("N/A")

# Combine textual features for TF-IDF vectorization (including director & cast to improve recommendations)
df["combined_features"] = (
    df["genres"] + " " +
    df["keywords"] + " " +
    df["overview"] + " " +
    df["tagline"] + " " +
    df["director"] + " " +
    df["cast"]
)

logging.info("🧹 Processing and cleaning textual features...")
df["cleaned_features"] = df["combined_features"].apply(clean_text_tokens)
logging.info("✅ Text features cleaned.")

# Vectorization using TF-IDF
logging.info("🔠 Vectorizing movie profiles using TF-IDF...")
vectorizer = TfidfVectorizer(max_features=5000)
tfidf_matrix = vectorizer.fit_transform(df["cleaned_features"])
logging.info("✅ Feature matrix shape: %s", tfidf_matrix.shape)

# Compute Cosine Similarity
logging.info("📐 Computing movie similarity space...")
similarity_matrix = cosine_similarity(tfidf_matrix, tfidf_matrix)
logging.info("✅ Cosine similarity matrix built successfully.")

# Serialize models and metadata to joblib files
logging.info("💾 Serializing processed artifacts...")
joblib.dump(df, DATA_DIR / "metadata_store.joblib")
joblib.dump(similarity_matrix, DATA_DIR / "similarity_model.joblib")
logging.info("💾 Artifacts saved successfully inside data/ folder.")

logging.info("🎉 Preprocessing pipeline finished successfully!")
