import pandas as pd

def get_movie_by_id(csv_file_path, movie_id):
    df = pd.read_csv(csv_file_path)
    # Check if movie_id is valid and convert to int
    try:
        movie_id = int(movie_id)
    except ValueError:
        return {"error": "Invalid movie_id"}

    # Filter the DataFrame by movie_id
    movie = df.loc[df['id'] == movie_id]

    # Check if the movie_id exists in the DataFrame
    if movie.empty:
        return {"error": "Movie not found"}
    movie = movie.fillna('')
    movie_dict = movie.to_dict(orient='records')
    return movie_dict

def get_movie_by_name(csv_file_path, movie_name):
    df = pd.read_csv(csv_file_path)
    # Check if movie_name is a non-empty string
    if not isinstance(movie_name, str) or not movie_name.strip():
        return {"error": "Invalid movie name"}

    # Filter the DataFrame by movie_name (case-insensitive)
    movie = df.loc[df['title'].str.lower() == movie_name.lower()]

    # Check if the movie name exists in the DataFrame
    if movie.empty:
        return {"error": "Movie not found"}

    # If multiple movies with the same name are found, return an error
    if len(movie) > 1:
        return {"error": "Multiple movies with the same name"}

    # Convert the filtered DataFrame to a dictionary and return the first record
    movie = movie.fillna('')
    movie_dict = movie.iloc[0].to_dict()
    return movie_dict