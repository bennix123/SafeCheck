# Standard library imports
from datetime import datetime
from enum import Enum
import logging
import re
from typing import Optional, List

# Third-party imports
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, EmailStr
from sqlalchemy import inspect
from sqlalchemy.orm import Session
import jwt

# Local application imports
from utils.apiResponseHandler import APIResponseHandler
from utils.dbHelper import DBHelper
from utils.emailHelper import EmailHelper
from utils.models import init_db, engine, get_db, User, UserHistory, LICPlan
from utils.seeds_plans import init_seed_data

# Initialize logging
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI()


#on app startup we created init_seed_data function to create all the table and seeds 10 lic plans into the licplans table
@app.on_event("startup")
async def startup():
    init_seed_data() 

origins = [
    "http://localhost:3000",#allowing the frontend to access the backend
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


security = HTTPBearer()
JWT_SECRET = "safeCheck"
JWT_ALGORITHM = "HS256"

#Helper function to get user_if from JWT token
#this is not used for now .It can be used in production 
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Dependency to get current user ID from JWT token"""
    try:
        token = credentials.credentials
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        user_id = payload.get("user_id")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: user_id missing"
            )
        return user_id
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not validate credentials: {str(e)}"
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



#api endpoint to fetch all the existing tables in db
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




#api end point to check weather backend server is running or not  
@app.get("/heath_check")
async def root():
    return {"message": "✅ Server  running!"}


#email Helper object to send otp to user registered email id and verify
email_helper = EmailHelper()





#api endpoint to send otp to user registered email
class SendOTPRequest(BaseModel):
    email: str
@app.post("/send-otp/", status_code=status.HTTP_200_OK)
async def send_otp(request:SendOTPRequest, db: Session = Depends(get_db)):
    logger.info(f"Request to send OTP: {request}")  
    """
    Send OTP to the provided email after checking if it exists in the database
    """
    try:
        db_helper = DBHelper(db)
        logger.info(f"Request to send OTP: {request}")  
        # Check if email exists in database
        user = db_helper.get_by_field(User, "email", request.email)
        if not user:
            return APIResponseHandler.error_response(
            message="Email not found in our system",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="Email not found in our system"
        )

        # Send OTP
        success = email_helper.send_otp(request.email)
        if not success:
            return APIResponseHandler.error_response(
            message="Failed to send OTP",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="Internal Server Error"
             )

        return APIResponseHandler.success_response(
            data={
                "email": request.email,
                "user_id": user.id,
                "name":user.name
            },
            message="OTP Sent Successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        return APIResponseHandler.error_response(
            message="Failed to send OTP",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=str(e)
             )






#api endpoint to verify-otp send to the user email-id
class VerifyOTPRequest(BaseModel):
    email: str
    otp: int
@app.post("/verify-otp/", status_code=status.HTTP_200_OK)
async def verify_otp(request:VerifyOTPRequest, db: Session = Depends(get_db)):
    """
    Verify the provided OTP against the stored OTP for the email
    """
    try:
        # Verify OTP

        db_helper = DBHelper(db)
        user = db_helper.get_by_field(User, "email", request.email)
        if not user:
            return APIResponseHandler.error_response(
                message="User not found",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="user_not_found"
            )
        

        is_valid = email_helper.verify_otp(request.email, request.otp)
        if not is_valid:
            return APIResponseHandler.error_response(
                message="Invalid OTP or OTP expired",
                status_code=status.HTTP_401_UNAUTHORIZED,
                error_code="Invalid OTP or OTP expired"
            )

        # token_data = {
        #     "user_id": user.id,
        #     "email": user.email
        # }
        # token = jwt.encode(token_data, JWT_SECRET, algorithm=JWT_ALGORITHM)

        return APIResponseHandler.success_response(
            data={
                # "access_token": token,
                "user_id": user.id,
                "email": user.email,
                "name":user.name
            },
            message="OTP verified successfully"
        )


    except HTTPException:
        raise
    except Exception as e:
       return APIResponseHandler.error_response(
            message="Failed to send OTP",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code=str(e)
             )





#api endpoint to signup into SafeCheck
# Enhanced Pydantic Model with Complete Validation
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
    



#api endpoint to save-user-history and recommend plans

class RiskCapacity(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class UserHistoryCreate(BaseModel):
    user_id: int
    age: int
    annual_income: int
    no_of_dependent: int
    risk_capacity: RiskCapacity

@app.post("/save-user-history/", status_code=status.HTTP_201_CREATED)
async def save_user_history(
    history_data: UserHistoryCreate,
    db: Session = Depends(get_db)
):
    """
    Save user history data to database and recommend plans
    
    Example Request:
    {
        "user_id": 1,
        "age": 23,
        "annual_income": 123456,
        "no_of_dependent": 2,
        "risk_capacity": "medium"
    }
    """
    try:
        db_helper = DBHelper(db)
        
        # Validate age range
        if not 18 <= history_data.age <= 100:
            return APIResponseHandler.error_response(
                message="Age must be between 18-100",
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                error_code="invalid_age_range"
            )
        
        # Create history record
        history_record = {
            "user_id": history_data.user_id,
            "age": history_data.age,
            "annual_income": history_data.annual_income,
            "no_of_dependent": history_data.no_of_dependent,
            "risk_capacity": history_data.risk_capacity
        }
        
        # Save user history
        created_history = db_helper.create(UserHistory, history_record)
        
        # Query suitable plans based on user's profile
        plans = db.query(LICPlan).filter(
            LICPlan.min_age <= history_data.age,
            LICPlan.max_age >= history_data.age,
            LICPlan.risk_capacity.any(history_data.risk_capacity)
        ).all()

        if not plans:
            return APIResponseHandler.error_response(
                message="No matching plans found",
                status_code=status.HTTP_404_NOT_FOUND,
                error_code="no_matching_plans"
            )

        # Calculate match scores for each plan
        recommended_plans = []
        for plan in plans:
            # Calculate age match score
            age_match = 1 - abs((history_data.age - (plan.min_age + plan.max_age)/2)/100)
            
            # Calculate risk match score
            risk_match = 1.0 if history_data.risk_capacity in plan.risk_capacity else 0.5
            
            # Calculate dependents factor
            dependents_factor = min(history_data.no_of_dependent/5, 1)
            
            # Calculate overall score
            score = (age_match * 0.4) + (risk_match * 0.4) + (dependents_factor * 0.2)
            
            recommended_plans.append({
                "plan_id": plan.id,
                "plan_name": plan.plan_name,
                "plan_type": plan.plan_type.value,
                "sum_assured_range": f"{plan.min_sum_assured:,} - {plan.max_sum_assured:,}",
                "description": plan.description,
                "match_score": round(score, 2)
            })

        # Sort plans by match score (highest first)
        recommended_plans.sort(key=lambda x: x["match_score"], reverse=True)
        
        return APIResponseHandler.success_response(
            data={
                "history": {
                    "id": created_history.id,
                    "created_at": created_history.created_ts.isoformat()
                },
                "recommended_plans": recommended_plans
            },
            message="User history saved successfully with plan recommendations"
        )
        
    except ValueError as e:
        return APIResponseHandler.error_response(
            message=str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error"
        )
    except Exception as e:
        logger.error(f"Error saving user history: {str(e)}", exc_info=True)
        return APIResponseHandler.error_response(
            message="Failed to save user history",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="database_error"
        )
