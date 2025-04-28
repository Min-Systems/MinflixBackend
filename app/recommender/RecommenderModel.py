# import os
# import ast
# import pickle
# import nltk
# from nltk.stem import PorterStemmer
# import pandas as pd
# from sklearn.feature_extraction.text import CountVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# 
# # Create dataframe from movies.csv dataset
# movies_df = pd.read_csv('movies.csv')
# 
# # Convert movies_df tags columnb to lowercase
# movies_df['tags'] = movies_df['tags'].apply(lambda x:x.lower())
# 
# # We use this to make words like love and loved and loving to be just "lov"
# # This is to help romance movies with love in their description to be deemed "similar"
# ps = PorterStemmer()
# def stems(text):
#     list = []
#     for i in text.split():
#         list.append(ps.stem(i))
#     return " ".join(list)
# 
# # Apply stems function to movies_df tags column
# movies_df['tags'] = movies_df['tags'].apply(stems)
# 
# # Implement the counter vectorizer but also get rid of uselss words
# # like "in", "the", "a", etc...
# cv = CountVectorizer(max_features=1000, stop_words= 'english')
# 
# # Vectorize tags column
# vector = cv.fit_transform(movies_df['tags']).toarray()
# 
# # Use cosine similarity
# # Store results of running cosing similarity on tags vector
# similarity = cosine_similarity(vector)
# 
# # The actual recommend movie that recommends 3 other movies
# '''
# def recommend(movie):
#     index = movies_df[movies_df['title'] == movie].index[0]
#     distances = sorted(list(enumerate(similarity[index])), reverse=True, key = lambda x: x[1])
#     for i in distances[1:6]:
#         print(movies_df.iloc[i[0]].title)
# '''
# 
# # Dump the dataframe and model into an artifacts folder
# os.makedirs('artifacts',exist_ok=True)
# pickle.dump(movies_df, open('artifacts/movie_list.pkl', 'wb'))
# pickle.dump(similarity, open('artifacts/similarity.pkl', 'wb'))