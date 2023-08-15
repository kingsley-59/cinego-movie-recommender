import os
from sqlalchemy import create_engine
from dotenv import load_dotenv
load_dotenv()

db_user = 'root'
db_password = ''
db_host = 'localhost'
db_name = 'db_agency'

if os.getenv('ENVIRONMENT') == 'production':
    db_user = os.getenv('DB_USERNAME')
    db_password = os.getenv('DB_PASSWORD')
    db_host = 'localhost'
    db_name = 'db_agency'

print(db_user)
# Create a SQLAlchemy engine
engine = create_engine(f'mysql+mysqlconnector://{db_user}:{db_password}@{db_host}/{db_name}')

