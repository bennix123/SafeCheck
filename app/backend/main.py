from typing import Optional
from utils.apiResponseHandler import APIResponseHandler
from utils.dbHelper import DBHelper
from fastapi import FastAPI, Depends,HTTPException,status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from datetime import datetime
from utils.models import init_db,engine, get_db,User,UserHistory,LICPlan
from pydantic import BaseModel, validator, EmailStr
import logging
import re
logger = logging.getLogger(__name__)

app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of allowed origins
    allow_credentials=True,  # Allow cookies
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


#OVERRIDE default exception handler for validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append({
            "field": field or "request_body",
            "message": error["msg"],
            "type": error["type"]
        })
    
    return APIResponseHandler.error_response(
        message="Validation failed",
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        error_details={
            "validation_errors": errors,
            "error_code": "invalid_request"
        }
    )


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
    return {"message": "✅ Server  running!"}

# Enhanced Pydantic Model with Complete Validation
# Request Model matching your exact JSON format
class UserCreateRequest(BaseModel):
    name: str
    email: EmailStr
    dateOfBirth: str  # Expects YYYY-MM-DD format

    @validator('name')
    def validate_name(cls, v):
        v = v.strip()
        if len(v) < 2:
            raise ValueError('Name must be at least 2 characters')
        if not re.match(r'^[a-zA-Z\s\-]+$', v):
            raise ValueError('Name can only contain letters, spaces and hyphens')
        return v

    @validator('dateOfBirth')
    def validate_date_of_birth(cls, v):
        try:
            birth_date = datetime.strptime(v, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('Invalid date format. Use YYYY-MM-DD')
        
        today = datetime.now().date()
        if birth_date > today:
            raise ValueError('Birth date cannot be in the future')
        
        age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        if age < 18:
            raise ValueError('User must be at least 18 years old')
        
        return v


# API Endpoint
@app.post("/signup/", status_code=status.HTTP_201_CREATED)
def create_user(user_request: UserCreateRequest, db: Session = Depends(get_db)):
    """
    Create user from {name, email, dateOfBirth} format
    
    Args:
        user_request: {
            "name": "Abhishek",
            "email": "abhishekkumar.doc007@gmail.com",
            "dateOfBirth": "2025-07-19" (YYYY-MM-DD)
        }
    """
    try:
        db_helper = DBHelper(db)
        
        # Check for existing email
        if db_helper.get_by_field(User, "email", user_request.email):
            raise ValueError("Email already registered")

        # Convert to database model format
        birth_date = datetime.strptime(user_request.dateOfBirth, '%Y-%m-%d')
        user_data = {
            "name": user_request.name,
            "email": user_request.email,
            "date_of_birth": birth_date.day,
            "month_of_birth": birth_date.month,
            "year_of_birth": birth_date.year,
            "is_active": True,
            "is_verified": False
        }

        # Create user
        created_user = db_helper.create(User, user_data)

        # Prepare response
        response_data = {
            "id": created_user.id,
            "name": created_user.name,
            "email": created_user.email,
            "dateOfBirth": user_request.dateOfBirth,
            "isActive": created_user.is_active,
            "createdAt": created_user.created_ts.isoformat()
        }

        return APIResponseHandler.success_response(
            data=response_data,
            message="User registered successfully"
        )

    except ValueError as e:
        return APIResponseHandler.error_response(
            message=str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error"
        )
    except Exception as e:
        return APIResponseHandler.handle_exception(
            exc=e,
            context="user registration"
        )