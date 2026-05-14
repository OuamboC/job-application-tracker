from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import Field, Session, SQLModel, create_engine, select

from contextlib import asynccontextmanager

# Step 1 : Create the base ApplicationBase - the base class (It has all the fields that are shared by all the models) 
class ApplicationBase(SQLModel):
    status: str = Field(index = True)
    company_name: str = Field(index = True) # Field(index = True) tells SQLModel that it should create a SQL index for this column, that would allow faster lookups in the DB when reading data filtered by this column
    programme_name: str = Field(index = True) 
    opening_date: str | None = Field(default = None)               # int | None = Field(default = None) means "this field is optional, store nothing if not provided"
    interview_language: str                                        # No Field(index = True) because I will not filter by interview_language
    sponsor_visa: str                                              # No Field(index = True) because I will not filter by sponsor_visa
    currency: str                                                  # No Field(index = True) because I will not filter by currency
    salary: int | None = Field(default = None)
    cv: str                                                        # No Field(index = True) because I will not filter by cv
    cover_letter: str                                              # No Field(index = True) because I will not filter by cover_letter
    country: str = Field(index = True)
    city: str = Field(index = True)
    notes: str | None  = Field(default = None)                     # No Field because I will not filter by notes 

# Step 2 : Create Application - the table Model
# table = True tells SQLModel that this is a table model, it should represent a table in the SQL database.
# Because Application inherits from ApplicationBase, it also has the field declared in ApplicationBase, so all the field for Application: id + everything from ApplicationBase
class Application(ApplicationBase, table = True):
    # Field(primary_key = True) tells SQLModel that the id is the primary key in the SQL database
    # We use int | None for the primary key field so that in Python code we can create object without an id(id = None), assuming the DB will generate it when saving
    id: int | None = Field(default = None, primary_key = True)

# Step 3 : Create ApplicationPublic - the public data model(This is the one that will be returned to the clients of the API) 
# It has the same fields as ApplicationBase
# It also re-declared id: int. By doing this, we are making a contract with the API clients, so that they can always expect the id to there and to be an int (it will never be None)
# All the fields in ApplicationPublic are the same as in ApplicationBase, with id declared as int(not None)
class ApplicationPublic(ApplicationBase):
    id: int

# Step 4 : ApplicationCreate - the data model to create an application(This is the one that will validate the data from the clients) 
# It has the same fields as ApplicationBase
class ApplicationCreate(ApplicationBase):
    pass # no extra fields, inherits everything from ApplicationBase

# Step 5 : ApplicationUpdate - the data model to update an application
# This data model is somewhat special, it has all the same fields that would be needed to create a new application, but all fields are optional(they all have a default value)...
# This way, when we update an application, we can send just the fields that we want to update.
# Because all the fields actually change (the type now includes None and they now have a default value of None), we need to redeclare them
# We don't really need to inherit from ApplicationBase because we are re-declaring all the fields. We will leave it inheriting just for consistency, but this is not necessary...
# It's more a matter of personal taste.
# The fields of ApplicationUpdate are: everything in ApplicationBase
class ApplicationUpdate(ApplicationBase):
    status: str | None = None
    company_name: str | None = None 
    programme_name: str | None = None 
    opening_date: str | None = None               
    interview_language: str | None = None                                       
    sponsor_visa: str | None = None                                            
    currency: str | None = None                                                 
    salary: int | None =  None
    cv: str | None = None                                                        
    cover_letter: str | None = None                                              
    country: str | None = None
    city: str | None = None
    notes: str | None = None

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

# Step 9 : Handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI): 
    create_db_and_tables() # runs once when server starts
    yield                  # app runs here
                           # cleanup code goes here (runs on shutdown)

# Pass lifespan to app so FastAPI knows what to do on start/stop
app = FastAPI(lifespan = lifespan)

# Step 10 : Create with ApplicationCreate and return an ApplicationPublic
# We receive in the request an ApplicationCreate data model, and from it, we create an Application table model
# This new table model Application will have the fields sent by the client, and will also have an id generated by the DB
# Then we return the same table model Application as is from the function. 
# But as we declare the response_model with ApplicationPublic data model, FastAPI will use ApplicationPublic to validate and serialize the data

@app.post("/applications", response_model = ApplicationPublic)
def create_application(application: ApplicationCreate, session: SessionDep):
    db_application = Application.model_validate(application)
    session.add(db_application)                             # Stage application to be saved
    session.commit()                                        # Save to DB
    session.refresh(db_application)                         # Refresh with DB generated values(e.g: id)
    return db_application

# Step 11: Read Applications with ApplicationPublic
# We will use response_model = list[ApplicationPublic] to ensure that the data is validated and serialized correctly
# Extension : Filer by status

@app.get("/applications", response_model = list[ApplicationPublic])
def read_applications(
    session: SessionDep,                                           # Injected DB session
    offset: int = 0,                                               # Skip N applications (e.g: offset = 5 skips first 5)
    limit: Annotated[int, Query(le = 100)] = 100,                  # Max applications to return, capped at 100
    status: str | None = None,                                     # Optional filter by status
    ):
    query = select(Application)                                    # SELECT * FROM Application
    if status:                                                     # Check if status is provided
        query = query.where(Application.status == status)          # Filter by status
    applications = session.exec(                                   # Executes the query
        query                                                      # Filter by status
        .offset(offset)                                            # Skip N rows
        .limit(limit)                                              # Take only N rows
        ).all()                                                    # Return all results as a list
    return applications

# Step 12: Read One Application with HeroPublic
# We can read a single application

@app.get("/applications/{id}", response_model = ApplicationPublic)
def read_application(id: int, session: SessionDep):
    application = session.get(Application, id)
    if not application:                                                           # Check if application do not exist
        raise HTTPException(status_code = 404, detail = "Application not found")  # Raise the following message
    return application                                                            # Return single application

# Step 13: Update an Application with ApplicationUpdate
# We can update an application. For this, we will use an HTTP PATCH operation
# And in the code, we get a dict with all data sent by the client, *only the data sent by the client*, excluding any values that would be there just for being the default values.
# To do it, we will use exclude_unset = True. This is the main trick
# Then we will use application_db.sqlmodel_update(application_data) to update the application_db with the data from application_data
@app.patch("/applications/{id}", response_model = ApplicationPublic)
def update_application(id: int, application: ApplicationUpdate, session: SessionDep):
    application_db = session.get(Application, id)
    if not application_db:                                                          # Check if application_db do not exist
        raise HTTPException(status_code = 404, detail = "Application not found")    # Raise the following message
    application_data = application.model_dump(exclude_unset = True)
    application_db.sqlmodel_update(application_data)
    session.add(application_db)
    session.commit()
    session.refresh(application_db)
    return application_db

# Step 14: Delete an application

@app.delete("/applications/{id}")
def delete_application(id: int, session: SessionDep):
    application = session.get(Application, id)
    if not application:                                                             # Check if application do not exist
        raise HTTPException(status_code = 404, detail = "Application not found")    # Raise the following message
    session.delete(application)                                                     # Delete (stage) application
    session.commit()                                                                # Save to DB
    return {"ok": True}



