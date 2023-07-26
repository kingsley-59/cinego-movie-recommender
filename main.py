import uvicorn
import os
import sys

from typing import Union, List
from fastapi import FastAPI
import pickle
from pandas import DataFrame
from movies import get_movie_by_id, get_movie_by_name

app = FastAPI()

movies_df: DataFrame = None
similarity = None

def load_pickle_file(file_path: str):
    if os.path.exists(file_path):
        return pickle.load(open(file_path, 'rb'))
    else:
        print(f"File {file_path} does not exist")
        return None

def load_data():
    global movies_df
    global similarity
    movies_df = load_pickle_file('./model/movies_list.pkl')
    similarity = load_pickle_file('./model/similarity.pkl')

def recommend(movie: str, movies_df: DataFrame, similarity, count= 5):
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
    
load_data()
if (movies_df is None or similarity is None): 
    print('Both paths to movies list and similarity must be valid')
    sys.exit(1)

@app.get('/')
def index():
    return {"message": "Hello there!"}

@app.get('/movies/{movie_id}')
async def get_movie(movie_id: int | str):
    csv_file_path = './model/movies.csv'
    movies = None
    try:
        if movie_id.isdigit():
            movies = get_movie_by_id(csv_file_path, movie_id)
        elif isinstance(movie_id, str):
            movies = get_movie_by_name(csv_file_path, movie_name=movie_id)
        else:
            return {'message': 'Invalid movie id'}
    except FileNotFoundError as e:
        print(f"New error: {e.filename} not found")
        return {"status": "error", "message": "CSV data file not found"}
    
    return {"message": "Successful", "data": movies}


@app.get('/recommend')
async def get_movie_recommendation(movie: Union[str, None] = None, count: int = 5):
    print(movie)
    if movie is None:
        return {
            "status": "error",
            "message": "movie is a required query param (/recommend?movie=[movie name])"
        }
    else: 
        result = recommend(movie, movies_df, similarity, count)
        return {
            "status": 'success',
            "message": "Successful request",
            "recommendation": result
        }


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)