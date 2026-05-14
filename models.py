from typing import Annotated
from sqlmodel import Field, SQLModel

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