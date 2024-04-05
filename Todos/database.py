from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
# import pyodbc
from sqlalchemy.engine import URL
import pymssql

# server = '172.17.0.3:1433' # to specify an alternate port
# database = 'todosapp' 
# username = 'SA' 
# password = 'Dhruv-0646'

## SQLALCHEMY_DATABASE_URL = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC Driver 18 for SQL+Server' #'sqlite:///./todosapp.db'
# con_string = f'DRIVER={driver};SERVER={server};PORT={port};DATABASE={database};UID={username};PWD={password};TrustServerCertificate=Yes' 

# SQLALCHEMY_DATABASE_URL = URL.create('mssql+pyodbc', query={"odbc_connect": con_string})


server = '172.17.0.3' # to specify an alternate port
port = '1433'
database = 'todosapp' 
username = 'SA' 
password = 'Dhruv-0646'
driver = 'ODBC Driver 18 for SQL Server'
SQLALCHEMY_DATABASE_URL = URL.create(drivername='mssql+pymssql', username=username, password=password, database=database, host=server, port=port)

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush=False, bind=engine)

Base = declarative_base()