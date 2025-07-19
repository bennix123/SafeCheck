import logging
from sqlalchemy.orm import Session
from datetime import datetime
from utils.models import LICPlan, PlanType, RiskCapacity, Base, engine,SessionLocal

logger = logging.getLogger(__name__)

def seed_initial_plans(db: Session):
    """Seed initial LIC plans into the database"""
    try:
        # Check if plans already exist in the first stage
        existing_plans = db.query(LICPlan).count()
        if existing_plans > 0:
            logger.info("LIC plans already exist in database, skipping seeding")
            return

        plans_data = [
        {
            "plan_name": "LIC e-Term",
            "plan_type": PlanType.TERM,
            "min_age": 18,
            "max_age": 65,
            "min_sum_assured": 1000000,
            "max_sum_assured": 75000000,
            "risk_capacity": [RiskCapacity.LOW, RiskCapacity.MEDIUM],
            "description": "Pure online term plan with instant issuance",
            "features": {
                "instant_issuance": True,
                "medical_test_waiver": True,
                "premium_calculator": True
            }
        },
        {
            "plan_name": "LIC Anmol Jeevan II",
            "plan_type": PlanType.TERM,
            "min_age": 18,
            "max_age": 55,
            "min_sum_assured": 500000,
            "max_sum_assured": 2500000,
            "risk_capacity": [RiskCapacity.LOW],
            "description": "Affordable term insurance for rural/semi-urban customers",
            "features": {
                "simplified_underwriting": True,
                "low_premium": True
            }
        },
        {
            "plan_name": "LIC New Jeevan Anand",
            "plan_type": PlanType.ENDOWMENT,
            "min_age": 18,
            "max_age": 50,
            "min_sum_assured": 100000,
            "max_sum_assured": 10000000,
            "risk_capacity": [RiskCapacity.LOW, RiskCapacity.MEDIUM],
            "description": "Combines endowment assurance with whole life cover",
            "features": {
                "loyalty_additions": True,
                "accident_benefit": True,
                "premium_waiver": True
            }
        },
        {
            "plan_name": "LIC Jeevan Lakshya",
            "plan_type": PlanType.ENDOWMENT,
            "min_age": 18,
            "max_age": 50,
            "min_sum_assured": 100000,
            "max_sum_assured": 5000000,
            "risk_capacity": [RiskCapacity.LOW],
            "description": "Child education/marriage protection plan",
            "features": {
                "income_benefit": True,
                "premium_waiver": True,
                "maturity_benefit": True
            }
        },
        {
            "plan_name": "LIC Wealth Plus",
            "plan_type": PlanType.ULIP,
            "min_age": 18,
            "max_age": 60,
            "min_sum_assured": 500000,
            "max_sum_assured": 50000000,
            "risk_capacity": [RiskCapacity.MEDIUM, RiskCapacity.HIGH],
            "description": "Wealth creation with life cover",
            "features": {
                "fund_options": ["equity", "debt", "balanced", "index"],
                "topup_premium": True,
                "partial_withdrawal": True
            }
        },
        {
            "plan_name": "LIC New Endowment Plus",
            "plan_type": PlanType.ULIP,
            "min_age": 18,
            "max_age": 55,
            "min_sum_assured": 1000000,
            "max_sum_assured": 10000000,
            "risk_capacity": [RiskCapacity.MEDIUM],
            "description": "Combines protection with savings",
            "features": {
                "guaranteed_additions": True,
                "tax_benefits": True,
                "loyalty_additions": True
            }
        },
        {
            "plan_name": "LIC Jeevan Tarang",
            "plan_type": PlanType.WHOLE_LIFE,
            "min_age": 18,
            "max_age": 60,
            "min_sum_assured": 100000,
            "max_sum_assured": 10000000,
            "risk_capacity": [RiskCapacity.LOW, RiskCapacity.MEDIUM],
            "description": "Whole life plan with guaranteed income",
            "features": {
                "survival_benefit": True,
                "income_till_lifetime": True,
                "death_benefit": True
            }
        },
        {
            "plan_name": "LIC Bima Shree",
            "plan_type": PlanType.WHOLE_LIFE,
            "min_age": 18,
            "max_age": 55,
            "min_sum_assured": 500000,
            "max_sum_assured": 5000000,
            "risk_capacity": [RiskCapacity.MEDIUM],
            "description": "Limited premium whole life plan",
            "features": {
                "limited_premium_payment": True,
                "bonus": True,
                "loan_available": True
            }
        },
        {
            "plan_name": "LIC New Money Back Plan 25 Years",
            "plan_type": PlanType.MONEY_BACK,
            "min_age": 18,
            "max_age": 50,
            "min_sum_assured": 100000,
            "max_sum_assured": 5000000,
            "risk_capacity": [RiskCapacity.LOW, RiskCapacity.MEDIUM],
            "description": "Long-term money back policy with survival benefits",
            "features": {
                "survival_benefit_percentages": [15, 15, 15, 15, 40],
                "bonus": True,
                "accident_benefit": True
            }
        },
        {
            "plan_name": "LIC Jeevan Shiromani",
            "plan_type": PlanType.MONEY_BACK,
            "min_age": 18,
            "max_age": 55,
            "min_sum_assured": 1000000,
            "max_sum_assured": 10000000,
            "risk_capacity": [RiskCapacity.HIGH],
            "description": "High-value money back plan for HNIs",
            "features": {
                "flexible_premium_payment": True,
                "loyalty_addition": True,
                "premium_waiver": True
            }
        }
    ]

        for plan_data in plans_data:
            plan = LICPlan(**plan_data)
            db.add(plan)

        db.commit()
        logger.info(f"Successfully seeded {len(plans_data)} LIC plans")

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to seed LIC plans: {e}")
        raise

def init_seed_data():
    """Initialize seed data by creating database tables and seeding plans"""
    try:
        # Create all the tables first
        Base.metadata.create_all(bind=engine)     
        # Seeds lic plans into lic_plans_table
        db = SessionLocal()
        seed_initial_plans(db)
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        raise
    finally:
        db.close()

        