import numpy as np
import pandas as pd
import pickle
import ast
import os

from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer
from db.engine import engine
# from memory_profiler import profile

ps = PorterStemmer()
new_df = None
similarity = None
current_directory = os.getcwd()

# movies_pkl_file = './model/movies_list.pkl'
# similarity_pkl_file = './model/similarity.pkl'

similarity_pkl_file = os.path.join(current_directory, 'data', 'cinego_similarity.pkl')
movies_pkl_file = os.path.join(current_directory, 'data', 'cinego_movies.pkl')

# Define various utility functions
def convert(obj):
    L = []
    for i in ast.literal_eval(obj):
        L.append(i['name'])
    return L

def convert3(obj):
    L = []
    counter = 0
    for i in ast.literal_eval(obj):
        if counter != 3:
            L.append(i['name'])
            counter +=1
        else:
            break
    return L

def fetch_director(obj):
    L = []
    for i in ast.literal_eval(obj):
        if i['job'] == 'Director':
            L.append(i['name'])
    return L

def stem(text):
    y = []
    for i in text.split():
        y.append(ps.stem(i))
    return " ".join(y)

# Main recommendation function
def generate_recommendation(movie: str, movies_df: DataFrame, similarity, count= 5):
    movie_index = movies_df[movies_df['title'].apply(lambda x:x.lower())==movie.lower()].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:count+1]
    
    recommended_movies = []
    for index, distance in movie_list:
        movie_data = movies_df.iloc[index].to_dict()
        movie_data['distance'] = distance
        recommended_movies.append(movie_data['id'])

    return recommended_movies

def generate_recommendation_by_id(movie_id: str, movies_df: DataFrame, similarity, count= 5):
    movie_index = movies_df[movies_df['id'] == movie_id].index[0]
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:count+1]
    
    recommended_movies = []
    for index, distance in movie_list:
        movie_data = movies_df.iloc[index].to_dict()
        movie_data['distance'] = distance
        recommended_movies.append(movie_data['id'])

    return recommended_movies

# Rest of the script to generate similarity and dataframe
# @profile
def run_recommendation_algorithm():
    global new_df
    global similarity
    current_directory = os.getcwd()
    
    # Load movies from database
    # movies_query =  "SELECT * FROM movies;"
    # movies_df = pd.read_sql_query(movies_query, engine)
    movies_file = os.path.join(current_directory, 'db', 'cinego-movies.csv')
    movies_df = pd.read_csv(movies_file)
    
    # Load genres from genre table 
    # genres_query =  "SELECT mg.movie_id, g.genre FROM movie_genre mg JOIN genre g ON mg.genre_id = g.id;"
    # genre_df = pd.read_sql_query(genres_query, engine)
    genres_file = os.path.join(current_directory, 'db', 'movie-genres.csv')
    genre_df = pd.read_csv(genres_file)
    
    # Group by movie_id and aggregate genres into a list and merge with movies
    grouped_genre_df = genre_df.groupby('movie_id')['genre'].agg(list).reset_index()
    grouped_genre_df['movie_id'] = grouped_genre_df['movie_id'].astype('int64')
    merged_movies = movies_df.merge(grouped_genre_df, left_on='id', right_on='movie_id', how='left')
    
    # sanitize and process data
    merged_movies['title'].dropna(inplace=True)
    merged_movies.fillna('', inplace=True)
    merged_movies['summary'] = merged_movies['summary'].apply(lambda x:x.split())
    merged_movies['summary'] = merged_movies['summary'].apply(lambda x:[i.replace(" ", "") for i in x])
    merged_movies['actors'] = merged_movies['actors'].apply(lambda x:x.split())
    merged_movies['actors'] = merged_movies['actors'].apply(lambda x:[i.replace(" ", "") for i in x])
    
    # Custom function to concatenate lists
    def concatenate_lists(row, columns=[]):
        concatenated = []
        for column in columns:
            concatenated.extend(row[column])
        return concatenated

    # Define the columns you want to concatenate
    columns_to_concat = ['genre', 'summary', 'actors']
    merged_movies['tags'] = merged_movies.apply(lambda x: concatenate_lists(x, columns_to_concat), axis=1)

    # Combine all the processed data into a single column - tags
    new_df = merged_movies[['id', 'title', 'tags', 'release_date', 'duration', 'parental_guide']]
    new_df['tags'] = new_df['tags'].apply(lambda x:' '.join(x))
    new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())

    # Matrix based on count vectorizer and tfidf vectorizer
    tfidf = TfidfVectorizer(max_features=5000, stop_words='english', use_idf=True, norm='l2')
    vectors = tfidf.fit_transform(new_df['tags']).toarray()

    # Apply stem function and generate similarity
    print("Applying word stemmer function...")
    new_df['tags'] = new_df['tags'].apply(stem)
    print("Creating similarity matrix...")
    similarity = cosine_similarity(vectors)
    
    # Clear large variables no longer needed to free up memory
    del vectors

    return None
    


def run_script():
    global new_df
    global similarity
    try:
        run_recommendation_algorithm()
    except Exception as e:
        print("Error running recommendation script: ", e)
    else:
        pickle.dump(new_df, open(movies_pkl_file, 'wb'))
        pickle.dump(similarity, open(similarity_pkl_file, 'wb'))

        print("Recommendation script run successfully")
        print('Pickle files generated...')
        print('\n\nDone! Have a safe working day🎉✨')
    return None