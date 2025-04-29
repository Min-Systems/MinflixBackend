import pickle
import joblib
from ..core.config import Settings
from pathlib import Path

# movies = pickle.load(open('./recommender/artifacts/movie_list.pkl', 'rb'))
# similarity = joblib.load('./recommender/artifacts/similarity.pkl')

settings = Settings()

if settings.recommender_file_directory == "":
    # get the base directory of the application
    base_dir = Path(__file__).parent.absolute()
    print(f"Base directory: {base_dir}")
    
    # Remove the doubled directory path - use only "artifacts" directly
    # movie_list_path = base_dir / "artifacts" / "movie_list.pkl"
    # similarity_path = base_dir / "artifacts" / "similarity.pkl"

    movie_list_path = "/app/recommender/artifacts/movie_list.pkl"
    similarity_path = "/app/recommender/artifacts/similarity.pkl"
    
    # Alternative approach - go up one directory if needed
    # movie_list_path = base_dir.parent / "artifacts" / "movie_list.pkl"
    # similarity_path = base_dir.parent / "artifacts" / "similarity.pkl"
    
    print(f"Looking for movie list at: {movie_list_path}")
    print(f"Looking for similarity at: {similarity_path}")

else:
   movie_list_path = Path(settings.recommender_file_directory) / "artifacts" / "movie_list.pkl" 
   similarity_path = Path(settings.recommender_file_directory) / "artifacts" /"similarity.pkl"

# open the files
movies = pickle.load(open(movie_list_path, 'rb'))
similarity = joblib.load(similarity_path)

movie_list = movies['title'].values

def recommend(movie):
    recommended_movies = []
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    # Recommend the top 3 movies (skipping the first result which is the same movie)
    for i in distances[1:4]:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies