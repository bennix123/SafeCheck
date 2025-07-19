from fastapi import FastAPI, Depends,HTTPException
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from utils.models import init_db,engine, get_db, Base
import logging
logger = logging.getLogger(__name__)

app = FastAPI()


@app.on_event("startup")
async def startup():
    init_db() 

@app.get("/tables")
async def get_all_tables(db: Session = Depends(get_db)):
    try:
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"Tables in the database: {tables}")
        return tables
        
    except Exception as e:
        logger.error(f"Error fetching tables: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    
@app.get("/heath_check")
async def root():
    return {"message": "✅ Server is running!"}