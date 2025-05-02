import numpy as np
from ..core.config import Settings

settings = Settings()

films = {
    # Action, Comedy, Drama, Sci-Fi
    "Assignment: Outer Space": [1, 0, 1, 0],
    "Brain From Planet Arous": [0, 1, 0, 1],
    "Creature from the Black Lagoon": [1, 1, 0, 0],
    "Evil Brain From Outer Space": [0, 0, 1, 1],
    "One Week": [1, 0, 0, 1],
    "The First 100 Years": [0, 1, 1, 0],
    "The Sinking of the Lusitania": [1, 1, 1, 0],
    "The Spirit of '43": [0, 0, 0, 1],
    "The Scarecrow": [1, 0, 1, 1],
    "Unknown World": [0, 1, 0, 0]
}


def cosine_similarity(vec_a, vec_b):
    """
        Calculate cosine similarity of two vectors

        Parameters
            vec_a (numpy vector): numpy vector
            vec_b (numpy vector): numpy vector

        Returns:
            float: 
    """
    dot_product = np.dot(vec_a, vec_b)
    magnitude_a = np.linalg.norm(vec_a)
    magnitude_b = np.linalg.norm(vec_b)
    return dot_product / (magnitude_a * magnitude_b)


# Convert the dataset to a matrix
film_names = list(films.keys())
film_vectors = np.array(list(films.values()))


# Calculate cosine similarity matrix
similarity_matrix = np.zeros((len(film_vectors), len(film_vectors)))
for i in range(len(film_vectors)):
    for j in range(len(film_vectors)):
        similarity_matrix[i][j] = cosine_similarity(
            film_vectors[i], film_vectors[j])


def recommend(film_name, top_n=2):
    """
        Recommend a film using the matrix and cosine similarity function
    """
    print(f"the film name {film_name}")
    film_index = film_names.index(film_name)
    print(f"{film_name} not in the database")
    similarity_scores = similarity_matrix[film_index]
    similar_films = sorted(zip(film_names, similarity_scores),
                           key=lambda x: x[1], reverse=True)
    result = [film for film, score in similar_films[1:top_n+1]]
    print(result)
    return result
