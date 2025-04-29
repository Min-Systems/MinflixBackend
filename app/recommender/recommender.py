import pickle
import joblib
from ..core.config import Settings
from pathlib import Path

settings = Settings()

if settings.recommender_file_directory == "":
    movie_list_path = "/app/app/recommender/artifacts/movie_list.pkl"
    similarity_path = "/app/app/recommender/artifacts/similarity.pkl"

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