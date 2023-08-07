import mysql.connector.pooling
import pandas as pd

# Create a connection pool to the MySQL database
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "db_agency",
}

connection_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="my_pool", pool_size=5, **db_config)

def load_data_from_mysql():
    try:
        connection = connection_pool.get_connection()
        if connection.is_connected():
            # Execute SQL query to fetch movies
            query = "SELECT * FROM movies;"
            df = pd.read_sql_query(query, connection)
            return df
    except Exception as e:
        print("Error loading data from MySQL:", e)
    finally:
        # Release the connection back to the connection pool
        if connection and connection.is_connected():
            connection.close()
            
# Load data from MySQL into a Pandas DataFrame
movie_data = load_data_from_mysql()

for col in movie_data.columns:
    print(col)
    
print(movie_data.head())