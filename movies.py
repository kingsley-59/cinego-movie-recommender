import pandas as pd

def get_movie_by_id(csv_file_path, movie_id):
    df = pd.read_csv(csv_file_path)
    movie = df.loc[df['id'] == int(movie_id)]
    return movie.to_dict(orient='records')

def get_movie_by_name(csv_file_path, movie_name):
    df = pd.read_csv(csv_file_path)
    movie = df.loc[df['title'].str.lower() == movie_name.lower()]
    return movie.to_dict(orient='records')