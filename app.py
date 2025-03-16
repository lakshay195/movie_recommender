import streamlit as st
import pickle
import requests
import random

# TMDB API Key (Replace with your own if needed)
API_KEY = "c7ec19ffdd3279641fb606d19ceb9bb1"

# Function to fetch movie posters and ratings
def fetch_movie_details(movie_id):
    url = f"https://api.themoviedb.org/3/movie/{movie_id}?api_key={API_KEY}&language=en-US"
    response = requests.get(url).json()
    poster = f"https://image.tmdb.org/t/p/w500{response['poster_path']}" if "poster_path" in response and response["poster_path"] else "https://via.placeholder.com/500x750?text=No+Image"
    rating = response.get("vote_average", "N/A")
    return poster, rating

# Load movie data and similarity matrix
movies = pickle.load(open("movies_list.pkl", 'rb'))
similarity = pickle.load(open("similarity.pkl", 'rb'))
genre_movies = pickle.load(open("genre_movies.pkl", 'rb'))  
movies_list = movies['title'].values
genres = genre_movies['genre'].unique()

# App Header
st.header("🎬 Movie Recommender System")
st.subheader("🎥 Trending Movies")

# List of movie IDs
movie_ids = [1632, 299536, 17455, 2830, 429422, 9722, 13972, 240, 155, 598, 914, 255709, 572154, 550, 157336, 27205, 603, 274, 680, 238, 278, 497, 424, 807, 185, 122, 769, 497698, 24428, 101, 8587, 111, 807, 372058, 603692, 335983, 496243, 597, 252, 914, 1124, 807, 299534, 862, 330457, 4232, 68718, 78, 103, 290, 1552, 36647, 9820, 961484, 671, 372058, 531219, 497698, 122, 954, 211672, 585, 807, 141, 120, 78, 1127, 238, 23835, 5915, 641, 599, 78, 112160, 322, 12599, 218, 567, 364, 920, 227, 184315, 8763, 260513]

# Select a random subset of movie IDs
random_ids = random.sample(movie_ids, 15)
imageUrls = [fetch_movie_details(movie_id) for movie_id in random_ids]

# Initialize session state for image index
if "image_index" not in st.session_state:
    st.session_state.image_index = 0

# Number of images per row
num_images_per_row = 5

# Add custom CSS for styling
st.markdown("""
<style>
    /* Background and Font */
    body {
        background-color: #121212;
        color: #ffffff;
        font-family: 'Poppins', sans-serif;
    }

    /* Slider Buttons */
    .slider-button {
        background: linear-gradient(135deg, #3b0094, #7f00ff, #ff0040);
        color: white;
        font-size: 20px;
        font-weight: bold;
        border: none;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
        text-align: center;
        box-shadow: 0px 4px 15px rgba(127, 0, 255, 0.5);
    }
    
    .slider-button:hover {
        background: linear-gradient(135deg, #7f00ff, #ff0040, #3b0094);
        transform: scale(1.2);
        box-shadow: 0px 6px 20px rgba(127, 0, 255, 0.8);
    }

    /* Movie Cards */
    .movie-card {
        background: linear-gradient(135deg, #1e1e1e, #292929);
        padding: 15px;
        border-radius: 15px;
        text-align: center;
        color: white;
        box-shadow: 0px 4px 20px rgba(127, 0, 255, 0.5);
        transition: transform 0.3s ease-in-out;
    }
    
    .movie-card:hover {
        transform: scale(1.1);
        box-shadow: 0px 6px 25px rgba(127, 0, 255, 0.8);
    }

    /* Dropdown Styling */
    select {
        background-color: #1e1e1e;
        color: #7f00ff;
        border: 2px solid #7f00ff;
        padding: 10px;
        font-size: 16px;
        border-radius: 8px;
        transition: 0.3s ease-in-out;
    }
    
    select:hover {
        border-color: #ff0040;
        box-shadow: 0px 0px 10px rgba(127, 0, 255, 0.8);
    }

    /* Streamlit Button Styling */
    div.stButton > button {
        background: linear-gradient(135deg, #3b0094, #7f00ff, #ff0040);
        color: white;
        font-size: 16px;
        font-weight: bold;
        border: none;
        border-radius: 12px;
        padding: 10px 20px;
        cursor: pointer;
        transition: all 0.3s ease-in-out;
        box-shadow: 0px 4px 10px rgba(127, 0, 255, 0.5);
    }

    div.stButton > button:hover {
        background: linear-gradient(135deg, #7f00ff, #ff0040, #3b0094);
        transform: scale(1.1);
        box-shadow: 0px 6px 20px rgba(127, 0, 255, 0.8);
    }

</style>

            """, unsafe_allow_html=True)

# Display images in a grid layout
start_idx = st.session_state.image_index
end_idx = min(start_idx + num_images_per_row, len(imageUrls))
row = st.columns(num_images_per_row)
for i, (img_url, rating) in enumerate(imageUrls[start_idx:end_idx]):
    with row[i]:
        st.image(img_url, width=300)

# Centered slider buttons
# Centered slider buttons with right button on extreme right
col1, col2, col3 = st.columns([1, 8, 1])  # Adjust column proportions for alignment

with col1:
    if st.button("◀", key="prev"):
        st.session_state.image_index = max(0, st.session_state.image_index - num_images_per_row)

with col3:
    if st.button("▶", key="next"):
        st.session_state.image_index = min(len(imageUrls) - num_images_per_row, st.session_state.image_index + num_images_per_row)


# Dropdown for genre selection
genre_query = st.selectbox("### **Select a Genre**", genres)
filtered_movies = genre_movies[genre_movies['genre'].str.contains(genre_query, case=False, na=False)]['title'].values
selectvalue = st.selectbox("### **Select a Movie**", filtered_movies) if filtered_movies.any() else ""

# Recommendation function
def recommend(movie):
    index = movies[movies['title'] == movie].index[0]
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    recommend_movie, recommend_poster, recommend_ratings = [], [], []
    for i in distance[1:41]:  
        movies_id = movies.iloc[i[0]].id
        poster, rating = fetch_movie_details(movies_id)
        recommend_movie.append(movies.iloc[i[0]].title)
        recommend_poster.append(poster)
        recommend_ratings.append(rating)
    return recommend_movie, recommend_poster, recommend_ratings

if st.button("Show Recommend") and selectvalue:
    movie_name, movie_poster, movie_ratings = recommend(selectvalue)
    st.markdown("<h3 style='text-align: center; color: #ff4b4b;'>🎥 Recommended Movies</h3>", unsafe_allow_html=True)
    cols = st.columns(5)
    for i in range(40):
        with cols[i % 5]:
            st.markdown(f"""
                <div class="movie-card">
                    <img src="{movie_poster[i]}" width="150" style="border-radius:5px;">
                    <p><strong>{movie_name[i]}</strong></p>
                    <p>⭐ Rating: {movie_ratings[i]}</p>
                </div>
            """, unsafe_allow_html=True)
# Display similar genre movies at the bottom
if genre_query:
    st.subheader(f"Movies in {genre_query} Genre")
    genre_movies_list = genre_movies[genre_movies['genre'].str.contains(genre_query, case=False, na=False)]['title'].values[:20]
    for movie in genre_movies_list:
        st.write(movie)
