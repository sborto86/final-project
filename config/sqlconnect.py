import streamlit as st
import sqlalchemy as alch
from sqlalchemy.exc import OperationalError

dbname = st.secrets["SQLDB"]
password= st.secrets["SQLPW"]
user = st.secrets["SQLUSER"]
port = int(st.secrets["SQLPORT"])
host = st.secrets["SQLHOST"]

connectionData = f"mysql+mysqlconnector://{user}:{password}@{host}:{port}/{dbname}"
engine = alch.create_engine(connectionData)

# Try to connect to the database
try:
    engine.connect()
except OperationalError:
    print(f"Database {dbname} doesn't exist")
except:
    print("Database connection error")

# Check if the tables exist if not, create tables

insp = alch.inspect(engine)
if not insp.has_table('gvolume'):
    with engine.connect() as con:
        with open("db/gvolume.sql") as file:
            query = alch.text(file.read())
            con.execute(query)
        with open("db/basedata.sql") as file:
            query = alch.text(file.read())
            con.execute(query)
if not insp.has_table('searchdata'):
    with engine.connect() as con:
        with open("db/searchdata.sql") as file:
            query = alch.text(file.read())
            con.execute(query)
if not insp.has_table('standardvolume'):
    with engine.connect() as con:
        with open("db/standardvolume.sql") as file:
            query = alch.text(file.read())
            con.execute(query)
if not insp.has_table('nytarchive'):
    with engine.connect() as con:
        with open("db/nytarchive.sql") as file:
            query = alch.text(file.read())
            con.execute(query)