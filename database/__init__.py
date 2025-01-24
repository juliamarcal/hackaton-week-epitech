from sqlalchemy_utils import database_exists, create_database
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os

# imports the elements of the database
from database.base import Base
from database.preProcessedData import PreProcessedData
from database.user import User

# from base import Base
# from preProcessedData import PreProcessedData
# from user import User

db_path = "database/db/"
# Verifies if the path doesn't exit
if not os.path.exists(db_path):
   # then create the directory
   os.makedirs(db_path)

# database access url (this is a url to access the local sqlite db)
db_url = 'sqlite:///%s/db.sqlite3' % db_path

# creates the engine that connects to the db
engine = create_engine(db_url, echo=False)

# Instanciate an session maker
Session = sessionmaker(bind=engine)

# create the db if it doesn't exist
if not database_exists(engine.url):
    create_database(engine.url) 

# create the tables if they don't exist
Base.metadata.create_all(engine)