from sqlalchemy.ext.declarative import declarative_base
from tornado_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

dbuser = os.environ.get('POSTGRES_USER')
dbpass = os.environ.get('POSTGRES_PASSWORD')
dbserv = os.environ.get('POSTGRES_HOST')
database = os.environ.get('POSTGRES_DB')
port = os.environ.get('POSTGRES_PORT')
database_uri = 'postgresql://{}:{}@{}/{}'.format(dbuser, dbpass, dbserv, database)

Base = declarative_base()

db = SQLAlchemy(database_uri)
db_engine = create_engine(database_uri)
db_session = sessionmaker()
