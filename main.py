import uvicorn
import os
import sys
import pandas as pd
import signal

from typing import Union, List
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from pandas import DataFrame
# from memory_profiler import profile
from movies import get_movie_by_id, get_movie_by_name
from model.recommend import run_script, generate_recommendation

pd.options.mode.chained_assignment = None

app = FastAPI()

movies_df: DataFrame = None
similarity = None

def load_pickle_file(file_path: str):
    if os.path.exists(file_path):
        # return pickle.load(open(file_path, 'rb'))
        return pd.read_pickle(open(file_path, 'rb'))
    else:
        print(f"File {file_path} does not exist")
        return None

# @profile
def load_data():
    global movies_df
    global similarity
    movies_df = load_pickle_file('./model/movies_list.pkl')
    similarity = load_pickle_file('./model/similarity.pkl')
    print('Movies and similarity data loaded!')


@app.get('/')
def index():
    return {"message": "Hello there!"}

@app.get('/movies/{movie_id}')
async def get_movie(movie_id: Union[int, str]):
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
        if movies_df is None:
            load_data()
        if movie.lower() not in movies_df['title'].apply(lambda x:x.lower()).values:
            return {"status": "error", "message": f"Movie [{movie}] not found!"}
        result = generate_recommendation(movie, movies_df, similarity, count)
        return {
            "status": 'success',
            "message": "Successful request",
            "recommendation": result
        }

@app.get("/shutdown")
async def shutdown():
    os.kill(os.getpid(), signal.SIGINT)
    return PlainTextResponse("Server shutting down")

if __name__ == "__main__":
    print(os.path.exists('./model/movies_list.pkl') and os.path.exists('./model/similarity.pkl'))
    if os.path.exists('./model/movies_list.pkl') and os.path.exists('./model/similarity.pkl'):
        load_data()
        if (movies_df is None or similarity is None): 
            print('Both paths to movies list and similarity must be valid')
            sys.exit(1)
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
    else:
        print("Pkl files not found...!")
        run_script()
        load_data()
        if (movies_df is None or similarity is None): 
            print('App data error: Both paths to movies list and similarity must be valid')
            sys.exit(1)
        uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)