from typing import Annotated
from fastapi import Depends
from sqlmodel import Session, SQLModel, create_engine

# Step 6 : Create the engine (SQLModel engine is what holds the connections to the database)
sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# A thread is like a worker handling my request. Normally one request = one worker
# Using "check_same_thread": False allows FastAPI to use the same SQLite db in different threads. 
# This is necessary as one single request could use more than one thread
connect_args = {"check_same_thread": False}
# Engine holds the connection to the database
engine = create_engine(sqlite_url, connect_args = connect_args)

# Step 7 : Create the Tables
def create_db_and_tables():
    SQLModel.metadata.create_all(engine) # Create the tables for all the table models

# Step 8 : Create a Session Dependency (Provides a DB session per request)
def get_session():
    with Session(engine) as session: # open a DB session using the engine
        yield session                # hand the session to the route that needs it
                                     # when  the request is done, session closes automatically

# SessionDep is a reusable type hint that injects get_session into any route such as /applications/
SessionDep = Annotated[Session, Depends(get_session)]