from sqlalchemy import create_engine

# Replace these values with your database configuration
db_user = 'root'
db_password = ''
db_host = 'localhost'
db_name = 'db_agency'

# Create a SQLAlchemy engine
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}')

