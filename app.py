# app.py
import json
import streamlit as st
import pathlib
import random
from pipeline.engine import load_engine, get_movie_titles, get_movie_genres, get_movie_metadata, get_movie_recommendations
from utils.omdb import fetch_omdb_metadata

# Resolve paths dynamically
BASE_DIR = pathlib.Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "config.json"

# Configure Page Layout & Icon
st.set_page_config(
    page_title="CineMatch - Premium Movie Discovery",
    page_icon="🎬",
    layout="centered"
)

# Custom Glassmorphic Dark-Cinema Theme Styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

    /* Global Typography overrides */
    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Primary Title Gradient styling */
    .hero-title {
        background: linear-gradient(135deg, #FF0844 0%, #FFB199 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: 800;
        text-align: center;
        margin-bottom: 0px;
    }
    
    .hero-subtitle {
        color: #94A3B8;
        font-size: 1.1rem;
        text-align: center;
        margin-top: 0px;
        margin-bottom: 30px;
    }

    /* Glassmorphic Movie Detail Card */
    .movie-detail-card {
        background: rgba(22, 28, 45, 0.45);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 25px;
        backdrop-filter: blur(10px);
        margin-bottom: 25px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
    }
    
    .detail-title {
        color: #FFFFFF;
        font-size: 1.8rem;
        font-weight: 700;
        margin-bottom: 4px;
    }
    
    .detail-tagline {
        color: #FFB199;
        font-style: italic;
        font-size: 1rem;
        margin-bottom: 15px;
    }

    /* Metadata pills */
    .meta-pills-container {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-bottom: 15px;
    }
    
    .meta-pill {
        background: rgba(255, 255, 255, 0.06);
        border: 1px solid rgba(255, 255, 255, 0.12);
        color: #CBD5E1;
        padding: 4px 12px;
        border-radius: 8px;
        font-size: 0.85rem;
        font-weight: 500;
    }

    /* Recommendations Cinema Grid Cards */
    .rec-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 20px;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .rec-card:hover {
        transform: translateY(-4px);
        border-color: rgba(255, 8, 68, 0.35);
        box-shadow: 0 10px 30px rgba(255, 8, 68, 0.12);
    }

    /* Genre tags */
    .genre-tag {
        background: rgba(255, 8, 68, 0.12);
        color: #FFB199;
        border: 1px solid rgba(255, 8, 68, 0.25);
        padding: 2px 10px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 6px;
    }
    
    .section-header {
        border-left: 4px solid #FF0844;
        padding-left: 10px;
        color: #FFFFFF;
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 30px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# Load configuration key
config = {"OMDB_API_KEY": "your_omdb_api_key"}
if CONFIG_PATH.exists():
    try:
        with open(CONFIG_PATH, "r") as f:
            config = json.load(f)
    except Exception:
        pass

# Render Header / Hero section
st.markdown('<div class="hero-title">🎬 CineMatch</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Premium Intelligent Movie Discovery Engine</div>', unsafe_allow_html=True)

# Verify recommendation system files
if not load_engine():
    st.error("⚠️ Recommendation assets not found in the data/ folder!")
    st.markdown("""
    To generate the engine files, run the preprocessing script inside your terminal:
    ```bash
    python pipeline/preprocess.py
    ```
    """)
else:
    # Retrieve movie metadata options
    titles = get_movie_titles()
    genres = get_movie_genres()

    # Session State tracking for surprise selection
    if "selected_movie" not in st.session_state:
        st.session_state["selected_movie"] = titles[0] if titles else "Avatar"

    # SIDEBAR: Configurations & Features
    st.sidebar.markdown("### ⚙️ Engine Configurations")
    
    # 🔑 OMDb API settings
    api_key = config.get("OMDB_API_KEY", "your_omdb_api_key")
    if api_key == "your_omdb_api_key" or not api_key:
        st.sidebar.warning("🔑 OMDb API Key not found in config.")
        api_key = st.sidebar.text_input("Enter OMDb API Key:", type="password", help="Sign up at http://www.omdbapi.com/")
    else:
        st.sidebar.success("🔑 OMDb API connection active.")

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🎬 Advanced Discovery")

    # 🎲 Surprise Me Button
    if st.sidebar.button("🎲 Surprise Me!", use_container_width=True):
        if titles:
            st.session_state["selected_movie"] = random.choice(titles)
            
    # 🔍 Recommendation Genre Filter
    selected_genre_filter = st.sidebar.selectbox(
        "🏷️ Restrict Recommendations to Genre:",
        ["All Genres"] + genres
    )
    
    genre_filter_val = None if selected_genre_filter == "All Genres" else selected_genre_filter

    # MAIN INTERFACE: Selector & Detail View
    selected_movie = st.selectbox(
        "🔍 Pick a movie to query similar options:",
        titles,
        index=titles.index(st.session_state["selected_movie"]) if st.session_state["selected_movie"] in titles else 0,
        key="selected_movie"
    )

    # Load local metadata for the selected movie
    meta = get_movie_metadata(selected_movie)
    
    if meta:
        # Fetch OMDb details (Plot / Poster)
        with st.spinner("Fetching latest metadata..."):
            omdb_plot, omdb_poster = fetch_omdb_metadata(selected_movie, api_key)
            
        # Fallback to local values if OMDb returns default values
        plot = omdb_plot if omdb_plot != "N/A" else meta.get("overview", "No plot available.")
        poster = omdb_poster if omdb_poster != "N/A" else None
        
        # Format year from release date
        release_date = meta.get("release_date", "N/A")
        year = release_date.split("-")[0] if "-" in str(release_date) else release_date
        
        # Render Movie detail card using custom HTML/CSS and Streamlit columns
        st.markdown('<div class="section-header">🎥 Current Movie Overview</div>', unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns([1, 2.2])
            
            with col1:
                if poster:
                    st.image(poster, use_container_width=True)
                else:
                    st.markdown("""
                    <div style="background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.1); border-radius:12px; height:220px; display:flex; align-items:center; justify-content:center; color:#64748B;">
                        ❌ No Poster
                    </div>
                    """, unsafe_allow_html=True)
                    
            with col2:
                st.markdown(f'<div class="detail-title">{selected_movie}</div>', unsafe_allow_html=True)
                if meta.get("tagline"):
                    st.markdown(f'<div class="detail-tagline">"{meta.get("tagline")}"</div>', unsafe_allow_html=True)
                
                # Render metadata pills
                rating_str = f"⭐ {meta.get('vote_average')}/10" if meta.get('vote_average') else "⭐ N/A"
                runtime_str = f"⏳ {int(meta.get('runtime'))} min" if meta.get('runtime') else "⏳ N/A"
                st.markdown(f"""
                <div class="meta-pills-container">
                    <span class="meta-pill">{rating_str}</span>
                    <span class="meta-pill">📅 {year}</span>
                    <span class="meta-pill">{runtime_str}</span>
                </div>
                """, unsafe_allow_html=True)
                
                # Render cast and director info
                st.markdown(f"**Director:** {meta.get('director')}")
                st.markdown(f"**Cast:** {meta.get('cast')}")
                
                # Render genre tags
                genres_html = "".join([f'<span class="genre-tag">{g}</span>' for g in meta.get("genres", "").split() if g])
                st.markdown(f'<div style="margin-top:10px; margin-bottom:15px;">{genres_html}</div>', unsafe_allow_html=True)
                
                st.write(plot)

        # RECOMMENDATION LOGIC
        st.markdown('<div class="section-header">🚀 AI recommendations</div>', unsafe_allow_html=True)
        
        if st.button("🔥 Generate Similar Movies", use_container_width=True):
            with st.spinner("Analyzing movie parameters & generating recommendations..."):
                recommendations = get_movie_recommendations(selected_movie, top_n=6, genre_filter=genre_filter_val)
                
                if recommendations is None or recommendations.empty:
                    st.warning("⚠️ No movies matched the criteria. Try changing the genre filter or selecting another movie.")
                else:
                    st.success(f"Here are the top matches based on content analysis:")
                    
                    # Display recommendations in list layout with details
                    for idx, row in recommendations.iterrows():
                        rec_title = row['title']
                        rec_year = row['release_date'].split("-")[0] if "-" in str(row['release_date']) else "N/A"
                        rec_rating = row['vote_average']
                        
                        rec_plot_omdb, rec_poster_omdb = fetch_omdb_metadata(rec_title, api_key)
                        
                        # Use local metadata fallback if OMDb fails
                        rec_plot = rec_plot_omdb if rec_plot_omdb != "N/A" else row.get("overview", "No plot overview.")
                        rec_poster = rec_poster_omdb if rec_poster_omdb != "N/A" else None
                        
                        st.markdown(f'<div class="rec-card">', unsafe_allow_html=True)
                        c1, c2 = st.columns([1, 4])
                        
                        with c1:
                            if rec_poster:
                                st.image(rec_poster, use_container_width=True)
                            else:
                                st.markdown("""
                                <div style="background:rgba(255,255,255,0.03); border:1px dashed rgba(255,255,255,0.1); border-radius:8px; height:120px; display:flex; align-items:center; justify-content:center; color:#64748B; font-size:0.8rem;">
                                    ❌ Poster
                                </div>
                                """, unsafe_allow_html=True)
                                
                        with c2:
                            st.markdown(f'<h4 style="margin:0 0 6px 0; color:#FFFFFF;">{rec_title} <span style="font-size:0.9rem; color:#94A3B8; font-weight:400;">({rec_year})</span></h4>', unsafe_allow_html=True)
                            
                            # Small inline stats
                            rec_rating_str = f"⭐ {rec_rating}/10" if rec_rating else "⭐ N/A"
                            st.markdown(f'<div style="font-size:0.8rem; color:#FFB199; margin-bottom:8px;">{rec_rating_str} | 🎬 Dir: {row.get("director", "N/A")}</div>', unsafe_allow_html=True)
                            
                            # Snippet overview
                            plot_snippet = rec_plot[:180] + "..." if len(rec_plot) > 180 else rec_plot
                            st.markdown(f'<p style="font-size:0.85rem; color:#CBD5E1; margin:0; line-height:1.4;">{plot_snippet}</p>', unsafe_allow_html=True)
                            
                        st.markdown('</div>', unsafe_allow_html=True)
