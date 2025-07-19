# models.py
from datetime import datetime
from enum import Enum
import os
from typing import List, Optional
from sqlalchemy import create_engine, Column, Integer, String, Boolean, Date, Enum as SQLEnum, \
    ForeignKey, ARRAY, Float, JSON, DateTime, func, CheckConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, validates
from sqlalchemy.dialects.postgresql import ARRAY as PG_ARRAY
import logging

logger = logging.getLogger(__name__)


DATABASE_URL = os.getenv("DATABASE_URL")

try:
    engine = create_engine(DATABASE_URL)
    if not engine:
        raise ValueError("Database URL is not set or invalid")
    # Test the connection immediately
    logger.info("✅ Database connection established successfully")
except Exception as e:
    logger.error(f"❌ Failed to connect to database: {e}")
    raise

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Enums
class RiskCapacity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class PlanType(str, Enum):
    TERM = "term"
    ENDOWMENT = "endowment"
    ULIP = "ulip"
    WHOLE_LIFE = "whole_life"
    MONEY_BACK = "money_back"

# User Model
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    date_of_birth = Column(Integer, nullable=False)
    month_of_birth = Column(Integer, nullable=False)
    year_of_birth = Column(Integer, nullable=False)
    email = Column(String(255), unique=True, nullable=False)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_ts = Column(DateTime, server_default=func.now())
    modified_ts = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    history = relationship("UserHistory", back_populates="user", cascade="all, delete")
    
    # Validations
    @validates('date_of_birth')
    def validate_date(self, key, date):
        if not 1 <= date <= 31:
            raise ValueError("Date must be between 1-31")
        return date
    
    @validates('month_of_birth')
    def validate_month(self, key, month):
        if not 1 <= month <= 12:
            raise ValueError("Month must be between 1-12")
        return month
    
    @validates('year_of_birth')
    def validate_year(self, key, year):
        current_year = datetime.now().year
        if not 1900 <= year <= current_year:
            raise ValueError(f"Year must be between 1900-{current_year}")
        return year
    
    __table_args__ = (
        CheckConstraint('date_of_birth BETWEEN 1 AND 31', name='check_date_range'),
        CheckConstraint('month_of_birth BETWEEN 1 AND 12', name='check_month_range'),
        CheckConstraint(f'year_of_birth BETWEEN 1900 AND {datetime.now().year}', name='check_year_range'),
    )

# User History Model
class UserHistory(Base):
    __tablename__ = "user_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete="CASCADE"))
    age = Column(Integer, nullable=False)
    occupation = Column(String(255), nullable=False)
    risk_capacity = Column(SQLEnum(RiskCapacity), nullable=False)
    created_ts = Column(DateTime, server_default=func.now())
    modified_ts = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationship
    user = relationship("User", back_populates="history")
    
    @validates('age')
    def validate_age(self, key, age):
        if not 18 <= age <= 100:
            raise ValueError("Age must be between 18-100")
        return age
    
    __table_args__ = (
        CheckConstraint('age BETWEEN 18 AND 100', name='check_age_range'),
    )

# LIC Plan Model
class LICPlan(Base):
    __tablename__ = "lic_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    plan_name = Column(String(255), nullable=False)
    plan_type = Column(SQLEnum(PlanType), nullable=False)
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    min_sum_assured = Column(Float, nullable=False)
    max_sum_assured = Column(Float, nullable=False)
    risk_capacity = Column(PG_ARRAY(String(10)), nullable=False)  # Array of RiskCapacity
    description = Column(String, nullable=True)
    features = Column(JSON, nullable=True)
    is_active = Column(Boolean, default=True)
    created_ts = Column(DateTime, server_default=func.now())
    modified_ts = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    @validates('min_age', 'max_age')
    def validate_age(self, key, age):
        if key == 'min_age' and age < 18:
            raise ValueError("Min age must be >= 18")
        if key == 'max_age' and age > 100:
            raise ValueError("Max age must be <= 100")
        return age
    
    @validates('risk_capacity')
    def validate_risk_capacity(self, key, risk_capacity):
        if not risk_capacity:
            raise ValueError("At least one risk capacity required")
        return risk_capacity
    
    __table_args__ = (
        CheckConstraint('min_age >= 18', name='check_min_age'),
        CheckConstraint('max_age <= 100', name='check_max_age'),
        CheckConstraint('max_age >= min_age', name='check_age_range'),
        CheckConstraint('max_sum_assured >= min_sum_assured', name='check_sum_assured'),
        CheckConstraint("array_length(risk_capacity, 1) > 0", name='check_risk_capacity_not_empty'),
    )

# Create all tables
def init_db():
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created/verified successfully")
    except Exception as e:
        logger.error(f"❌ Failed to create database tables: {e}")
        raise

# Database session dependency
def get_db():
    db = SessionLocal()
    try:
        logger.debug("ℹ️ Database session created")
        yield db
    except Exception as e:
        logger.error(f"⚠️ Database session error: {e}")
        db.rollback()
        raise
    finally:
        db.close()
        logger.debug("ℹ️ Database session closed")