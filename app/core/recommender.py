import pickle
import json
import joblib

movies = pickle.load(open('../recommender/artifacts/movie_list.pkl', 'rb'))
similarity = joblib.load('../recommender/artifacts/similarity.pkl')

movie_list = movies['title'].values

def recommend(movie):
    recommended_movies = []
    index = movies[movies['title'] == movie].index[0]
    distances = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda x: x[1])
    # Recommend the top 3 movies (skipping the first result which is the same movie)
    for i in distances[1:4]:
        recommended_movies.append(movies.iloc[i[0]].title)
    return recommended_movies