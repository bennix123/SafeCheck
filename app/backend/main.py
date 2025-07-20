from typing import Optional
from utils.apiResponseHandler import APIResponseHandler
from utils.dbHelper import DBHelper
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import FastAPI, Depends,HTTPException,status,Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from utils.emailHelper import EmailHelper
from sqlalchemy import inspect, text
from enum import Enum
from sqlalchemy.orm import Session
from datetime import datetime
from utils.models import init_db,engine, get_db,User,UserHistory,LICPlan
from utils.seeds_plans import init_seed_data
from pydantic import BaseModel, validator, EmailStr
import jwt
import logging
from typing import List
import re
logger = logging.getLogger(__name__)

app = FastAPI()

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
email_helper = EmailHelper()
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
    Save user history data to database
    
    Example Request:
    {
        "age": 23,
        "annual_income": 123456,
        "no_of_dependent": 2,
        "risk_capacity": "medium"
    }
    """
    try:
        db_helper = DBHelper(db)
        
        # Validate age range (though SQLAlchemy also checks this)
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
        
        created_history = db_helper.create(UserHistory, history_record)
        
        return APIResponseHandler.success_response(
            data={
                "id": created_history.id,
                "created_at": created_history.created_ts.isoformat()
            },
            message="User history saved successfully"
        )
        
    except ValueError as e:
        return APIResponseHandler.error_response(
            message=str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            error_code="validation_error"
        )
    except Exception as e:
        logger.error(f"Error saving user history: {str(e)}")
        return APIResponseHandler.error_response(
            message="Failed to save user history",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="database_error"
        )
    



class PlanRecommendationRequest(BaseModel):
    age: int
    dependents: int
    risk_tolerance: RiskCapacity

class PlanRecommendationResponse(BaseModel):
    plan_id: int
    plan_name: str
    plan_type: str
    sum_assured_range: str
    description: str
    match_score: float

@app.post("/recommend-plans/", response_model=List[PlanRecommendationResponse])
async def recommend_plans(
    request: PlanRecommendationRequest,
    db: Session = Depends(get_db)
):
    """
    Recommend LIC plans based on user's age, dependents and risk tolerance
    
    Example Request:
    {
        "age": 30,
        "dependents": 2,
        "risk_tolerance": "medium"
    }
    """
    try:
        # Validating age
        if not 18 <= request.age <= 100:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="Age must be between 18-100"
            )

        # Query suitable plans
        plans = db.query(LICPlan).filter(
            LICPlan.min_age <= request.age,
            LICPlan.max_age >= request.age,
            LICPlan.risk_capacity.any(request.risk_tolerance.value)
        ).all()

        if not plans:
            return APIResponseHandler.error_response(
            message="No matching plans found",
            status_code=status.HTTP_404_NOT_FOUND,
            error_code="No matching plans found"
        )

        recommended_plans = []
        for plan in plans:
            age_match = 1 - abs((request.age - (plan.min_age + plan.max_age)/2)/100)
            risk_match = 1.0 if request.risk_tolerance.value in plan.risk_capacity else 0.5
            dependents_factor = min(request.dependents/5, 1)
            
            score = (age_match * 0.4) + (risk_match * 0.4) + (dependents_factor * 0.2)
            
            recommended_plans.append({
                "plan_id": plan.id,
                "plan_name": plan.plan_name,
                "plan_type": plan.plan_type.value,
                "sum_assured_range": f"{plan.min_sum_assured:,} - {plan.max_sum_assured:,}",
                "description": plan.description,
                "match_score": round(score, 2)
            })

        recommended_plans.sort(key=lambda x: x["match_score"], reverse=True)

        return APIResponseHandler.success_response(
            data={
               recommended_plans
            },
            message="Plans Recommended Successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Plan recommendation error: {e}")
        return APIResponseHandler.error_response(
            message="Failed to save user history",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error_code="database_error"
        )
