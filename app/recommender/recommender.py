import pickle
import joblib
from ..core.config import Settings
from pathlib import Path

# movies = pickle.load(open('./recommender/artifacts/movie_list.pkl', 'rb'))
# similarity = joblib.load('./recommender/artifacts/similarity.pkl')

settings = Settings()

if settings.recommmender_file_directory == "":
    # get the base directory of the application
    base_dir = Path(__file__).parent.absolute()
    # make the paths
    movie_list_path = base_dir  / "recommender" / "artifacts" / "movie_list.pkl"
    similarity_path = base_dir  / "recommender" / "artifacts" / "similarity.pkl"
else:
   movie_list_path = settings.recommender_dir / "movie_list.pkl" 
   similarity_path = settings.recommender_dir / "similarity.pkl"

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