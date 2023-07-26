import numpy as np
import pandas as pd
import pickle
import ast
import os

from pandas import DataFrame
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.stem.porter import PorterStemmer

ps = PorterStemmer()
new_df = None
similarity = None

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
    print(movie_index)
    distances = similarity[movie_index]
    movie_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x:x[1])[1:count+1]
    
    recommended_movies = []
    for index, distance in movie_list:
        movie_data = movies_df.iloc[index].to_dict()
        movie_data['distance'] = distance
        recommended_movies.append(movie_data)

    return recommended_movies


# Rest of the script to generate similarity and dataframe
def run_recommendation_algorithm():
    global new_df
    global similarity
    current_directory = os.getcwd()

    # Construct the absolute paths for the CSV files
    credits_file = os.path.join(current_directory, 'model', 'credits.csv')
    movies_file = os.path.join(current_directory, 'model', 'movies.csv')
    credits_df = pd.read_csv(credits_file)
    movies_df = pd.read_csv(movies_file)


    # print(movies_df.shape)
    # print(movies_df.info())
    # print(credits_df.head())
    # print(movies_df.head()) # or .tail() to get the last few lines

    # Merge credits and movies dataframe where title is the same
    movies_df = movies_df.merge(credits_df, on='title')

    # Create a new dataframe, picking only the columns necessary
    movies = movies_df[['movie_id', 'title', 'overview', 'genres', 'keywords', 'cast', 'crew']]

    movies.dropna(inplace=True)
    print(movies.iloc[0])

    # Apply the utility functions to process data
    movies['genres'] = movies['genres'].apply(convert)
    movies['keywords'] = movies['keywords'].apply(convert)
    movies['cast'] = movies['cast'].apply(convert3)
    movies['crew'] = movies['crew'].apply(fetch_director)

    movies['overview'] = movies['overview'].apply(lambda x:x.split())
    movies['genres'] = movies['genres'].apply(lambda x:[i.replace(" ", "") for i in x])
    movies['keywords'] = movies['keywords'].apply(lambda x:[i.replace(" ", "") for i in x])
    movies['cast'] = movies['cast'].apply(lambda x:[i.replace(" ", "") for i in x] if x is not None else None)
    movies['crew'] = movies['crew'].apply(lambda x:[i.replace(" ", "") for i in x])

    # Combine all the processed data into a single column - tags
    movies['tags'] = movies['overview']+movies['genres']+movies['keywords']+movies['cast']+movies['crew']

    # Create new dataframe with the new data structure
    new_df = movies[['movie_id','title', 'tags']]
    new_df['tags'] = new_df['tags'].apply(lambda x:' '.join(x))
    new_df['tags'] = new_df['tags'].apply(lambda x:x.lower())

    # Matrix based on count vectorizer and tfidf vectorizer
    cv = CountVectorizer(max_features=5000, stop_words='english')
    tfidf = TfidfVectorizer(stop_words='english')

    # Create vectors with any of the vectorizers
    print(cv.fit_transform(new_df['tags']).toarray().shape)
    # vectors = cv.fit_transform(new_df['tags']).toarray()
    vectors = tfidf.fit_transform(new_df['tags']).toarray()
    print(len(cv.get_feature_names_out()))

    # Apply stem function and generate similarity
    new_df['tags'] = new_df['tags'].apply(stem)
    similarity = cosine_similarity(vectors)


    # print(generate_recommendation('Iron Man', new_df, similarity, 4))
    # print(generate_recommendation('Independence Day', new_df, similarity, 4))
    # print(generate_recommendation('Avatar', new_df, similarity, 4))
    return None


def run_script():
    global new_df
    global similarity
    try:
        run_recommendation_algorithm()
    except Exception as e:
        print("Error running recommendation script: ", e)
    else:
        current_directory = os.getcwd()
        similarity_pkl_file = os.path.join(current_directory, 'model', 'smilarity.pkl')
        movies_pkl_file = os.path.join(current_directory, 'model', 'movies_list.pkl')
        pickle.dump(new_df, open(movies_pkl_file, 'wb'))
        pickle.dump(similarity, open(similarity_pkl_file, 'wb'))

        print("Recommendation script run successfully")
        print('Pickle files generated...')
        print('\n\nDone! Have a safe working day🎉✨')
    return None
        
run_script()