import pickle
import pandas as pd
import streamlit as st
import requests



TMDB_API_KEY = "YOUR_API_KEY"


st.set_page_config(
    page_title="Movie Recommender",
    page_icon="🎬",
    layout="wide"
)

# ---------- GLOBAL STYLES (CSS) ----------
st.markdown("""
    <style>
    /* Overall background */
    .stApp {
        background: radial-gradient(circle at top left, #1d3557, #000000 60%);
        color: #f8fafc;
        font-family: "Segoe UI", system-ui, -apple-system, BlinkMacSystemFont;
    }

    /* Page title */
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #ff6b6b, #ffd166);
        -webkit-background-clip: text;
        color: transparent;
        margin-bottom: 0.2rem;
    }

    .subtitle {
        font-size: 0.95rem;
        color: #e2e8f0;
        margin-bottom: 1.5rem;
    }

    /* Movie cards */
    .movie-card {
        background: rgba(15, 23, 42, 0.85);
        border-radius: 18px;
        padding: 10px 10px 14px 10px;
        box-shadow: 0 18px 40px rgba(0, 0, 0, 0.45);
        backdrop-filter: blur(8px);
        text-align: center;
        transition: transform 0.18s ease, box-shadow 0.18s ease, border 0.18s ease;
        border: 1px solid rgba(148, 163, 184, 0.25);
    }

    .movie-card:hover {
        transform: translateY(-6px) scale(1.02);
        box-shadow: 0 26px 60px rgba(0, 0, 0, 0.65);
        border-color: #facc15;
    }

    .movie-title {
        font-size: 0.9rem;
        font-weight: 600;
        color: #f9fafb;
        margin-top: 0.4rem;
    }

    .movie-img {
        border-radius: 14px;
        height: 240px;
        width: 100%;
        object-fit: cover;
        margin-bottom: 0.3rem;
    }

    /* Make sidebar a bit darker */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #020617, #0b1120);
    }

    </style>
""", unsafe_allow_html=True)


# DATA LOADING
@st.cache_data(show_spinner=False)
def load_data():
    movies = pickle.load(open("movies.pkl", "rb"))
    similarity = pickle.load(open("similarity.pkl", "rb"))

    # if movies is dict, convert to DataFrame
    if isinstance(movies, dict):
        movies = pd.DataFrame(movies)
    return movies, similarity


movies, similarity = load_data()


#POSTER FETCHING
@st.cache_data(show_spinner=False)
def fetch_poster(movie_id: int):
    """Return TMDB poster URL given movie_id."""
    try:
        url = f"https://api.themoviedb.org/3/movie/{movie_id}"
        params = {
            "api_key": TMDB_API_KEY,
            "language": "en-US",
        }
        response = requests.get(url, params=params, timeout=5)
        data = response.json()
        poster_path = data.get("poster_path")
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
        return None
    except Exception:
        return None





#RECOMMEND FUNCTION
def recommend(movie_title: str, top_n: int = 5):
    """
    Return top_n recommended movies (names + poster URLs).
    Assumes columns: 'title' and 'movie_id'
    """
    try:
        movie_index = movies[movies["title"] == movie_title].index[0]
    except IndexError:
        return [], []

    distances = similarity[movie_index]
    movie_list = sorted(
        list(enumerate(distances)),
        key=lambda x: x[1],
        reverse=True
    )[1:top_n + 1]  # skip same movie

    names, posters = [], []
    for idx, score in movie_list:
        row = movies.iloc[idx]
        name = row["title"]
        movie_id = row["movie_id"]
        poster = fetch_poster(movie_id)
        names.append(name)
        posters.append(poster)

    return names, posters


#SIDEBAR (INTERACTIONS)
st.sidebar.title("⚙️ Controls")

top_n = st.sidebar.slider(
    "Number of recommendations",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
)

show_posters = st.sidebar.toggle("Show posters", value=True)
st.sidebar.markdown("---")
st.sidebar.info("Tip: Try different movies and see how similar the suggestions feel 😉")


#MAIN UI
st.markdown('<div class="main-title">🎬 Movie Recommender</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Pick a movie you like and I\'ll suggest similar ones for you.</div>',
    unsafe_allow_html=True
)

# Movie selector
movie_list = movies["title"].values
selected_movie = st.selectbox(
    "Search or select a movie:",
    movie_list,
    index=0,
    key="movie_select"
)

# Button
if st.button("✨ Show Recommendations", use_container_width=True):
    with st.spinner("Finding the best movies for you... 🍿"):
        names, posters = recommend(selected_movie, top_n=top_n)

    if not names:
        st.warning("No recommendations found. Try another movie.")
    else:
        st.success(f"Here are {len(names)} movies similar to **{selected_movie}**:")

        # Grid layout
        cols = st.columns(5)

        for i, (name, poster) in enumerate(zip(names, posters)):
            col = cols[i % 5]
            with col:
                # Custom HTML card
                if show_posters and poster:
                    card_html = f"""
                    <div class="movie-card">
                        <img src="{poster}" class="movie-img" alt="{name}">
                        <div class="movie-title">{name}</div>
                    </div>
                    """
                else:
                    card_html = f"""
                    <div class="movie-card">
                        <div class="movie-title" style="margin-top:8px;">{name}</div>
                    </div>
                    """
                st.markdown(card_html, unsafe_allow_html=True)

        st.balloons()
