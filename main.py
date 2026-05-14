from contextlib import asynccontextmanager
from fastapi import FastAPI
from database import create_db_and_tables
from routers import applications




# Step 9 : Handle startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI): 
    create_db_and_tables() # runs once when server starts
    yield                  # app runs here
                           # cleanup code goes here (runs on shutdown)

# Pass lifespan to app so FastAPI knows what to do on start/stop
app = FastAPI(lifespan = lifespan)

app.include_router(applications.router)