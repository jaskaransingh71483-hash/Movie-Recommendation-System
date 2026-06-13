# 🎬 CineMatch - Intelligent Movie Discovery Engine

CineMatch is a premium content-based Movie Recommendation System designed to discover similar movies based on textual metadata profiles (genres, keywords, plot overviews, taglines, directors, and lead casts). Built using **Python**, **scikit-learn**, and **Streamlit**, it provides an interactive, glassmorphic cinema dashboard that loads movie details, reviews, and high-quality posters dynamically.

---

## ✨ Key Features

*   **🎬 Context-Rich Similarity Engine**: Recommends movies not just by plot overview, but by combining genres, plot, taglines, director, and lead actor profiles. Searching *Inception* will naturally surface other Leonardo DiCaprio films or Christopher Nolan projects.
*   **🎭 Live Genre-Based Filtering**: Narrow down recommendations to specific genres (e.g., finding *only* Sci-Fi movies similar to *Interstellar*).
*   **💎 Premium Glassmorphic UI**: Styled with a dark-slate cinema theme, custom layout rows, rating/runtime indicators, and custom CSS card animations.
*   **🔑 Dynamic OMDb API Integration**: Fetches high-quality posters and extended plot reviews live. Fallbacks gracefully to cached dataset details if an API key is not supplied.
*   **🎲 "Surprise Me" Button**: Automatically queries a random title from the database to discover new movies.
*   **📂 Modular Code Architecture**: Built with clear directory separations (`pipeline/`, `utils/`, `data/`, `config/`).

---

## 🛠️ Tech Stack & Libraries

*   **Front-End Dashboard**: [Streamlit](https://streamlit.io/)
*   **Data Processing**: [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
*   **Natural Language Processing**: [NLTK](https://www.nltk.org/) (Tokenization, Stopword removal)
*   **Machine Learning Model**: [Scikit-Learn](https://scikit-learn.org/) (`TfidfVectorizer`, `cosine_similarity`)
*   **Serialization**: [Joblib](https://joblib.readthedocs.io/)
*   **API Calls**: [Requests](https://requests.readthedocs.io/) (OMDb Poster API)

---

## 📐 How the Recommendation Engine Works

CineMatch utilizes standard Natural Language Processing (NLP) techniques:

1.  **Feature Extraction**: Merges `genres`, `keywords`, `overview`, `tagline`, `director`, and `cast` into a single, unified text corpus for each movie.
2.  **Text Cleaning**: Lowercases all tokens, removes numbers & special characters, and filters out English stopwords (e.g., "the", "and", "is").
3.  **TF-IDF Vectorization**: Transforms textual profiles into a high-dimensional sparse matrix representing the Term Frequency-Inverse Document Frequency (TF-IDF) scores for individual keywords.
4.  **Cosine Similarity**: Measures the cosine angle between movie vector representations. It scores similarity from `0.0` (unrelated) to `1.0` (identical content):
    $$\text{Similarity}(A, B) = \cos(\theta) = \frac{A \cdot B}{\|A\| \|B\|}$$

---

## 📂 Project Structure

```text
movie-recommendation-app-repo/
├── config/
│   └── config.json            # Stores OMDb API Key credentials
├── data/
│   ├── movies.csv             # Raw TMDb 5000 movies dataset
│   ├── metadata_store.joblib  # Preprocessed Pandas metadata store
│   └── similarity_model.joblib# Serialized cosine similarity matrix
├── pipeline/
│   ├── preprocess.py          # Data cleaning and model training pipeline
│   └── engine.py              # Query recommendations and handles filters
├── utils/
│   └── omdb.py                # Performs remote API requests to OMDb
├── app.py                     # Main Streamlit web application
├── requirements.txt           # Python dependency requirements
└── README.md                  # Project documentation
```

---

## 🚀 Getting Started

### 1. Installation & Environment Setup
Clone this repository to your local machine, open your terminal, and run:
```bash
# Create a virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Run the Preprocessing Pipeline
To clean the raw movie dataset and build the Cosine Similarity matrices, run:
```bash
python pipeline/preprocess.py
```
*This will create the serialized `.joblib` files inside the `data/` folder.*

### 3. Launch the Application
Run the Streamlit server locally:
```bash
streamlit run app.py
```
Open **[http://localhost:8501](http://localhost:8501)** in your web browser to use the app!

---

## 🔑 OMDb API Key Setup (Optional)
To display live movie posters and plot descriptions:
1. Register for a free API Key on [omdbapi.com](http://www.omdbapi.com/apikey.aspx).
2. Save your key in `config/config.json`:
   ```json
   {
     "OMDB_API_KEY": "YOUR_OMDB_KEY_HERE"
   }
   ```
3. Alternatively, you can input your key directly into the application's sidebar interface when running the app.
