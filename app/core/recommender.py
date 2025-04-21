import pickle
import json
import joblib

movies = pickle.load(open('../recommender/artifacts/movie_list.pkl', 'rb'))
similarity = joblib.load('../recommender/artifacts/similarity.pkl')

movie_list = movies['title'].values

def recommend(watched_movies):
    recommended_movies = {}
    for movie in watched_movies:
        try:
            index = movies[movies['title'] == movie].index[0]
        except IndexError:
            continue
        distances = list(enumerate(similarity[index]))
        for i, distance in distances:
            rec_movie = movies.iloc[i].title
            # skip if the movie was already watched
            if rec_movie in watched_movies:
                continue
            if rec_movie not in recommended_movies:
                recommended_movies[rec_movie] = 0
            recommended_movies[rec_movie] += distance
    sorted_recommendations = sorted(recommended_movies.items(), key=lambda x: x[1], reverse=True)
    final_recommendations = [rec[0] for rec in sorted_recommendations[:3]]
    return final_recommendations