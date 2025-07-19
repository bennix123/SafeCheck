# dbHelper.py
from typing import Type, TypeVar, Any, Dict, List, Optional
from sqlalchemy import inspect, and_
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging

T = TypeVar('T')  # Generic type for SQLAlchemy models

class DBHelper:
    def __init__(self, db: Session):
        self.db = db
        self.logger = logging.getLogger(__name__)

    def _sanitize_input(self, data: Any) -> Any:
        """Basic input sanitization to prevent SQL injection"""
        if isinstance(data, str):
            return data.replace(";", "").replace("--", "")
        elif isinstance(data, dict):
            return {self._sanitize_input(k): self._sanitize_input(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._sanitize_input(item) for item in data]
        return data

    def _validate_model(self, model: Type[T]) -> None:
        """Validate the model is a SQLAlchemy model"""
        if not hasattr(model, '__table__'):
            raise ValueError(f"{model.__name__} is not a SQLAlchemy model")

    def create(self, model: Type[T], data: Dict[str, Any]) -> T:
        """Create a new record"""
        try:
            self._validate_model(model)
            sanitized_data = self._sanitize_input(data)
            
            instance = model(**sanitized_data)
            self.db.add(instance)
            self.db.commit()
            self.db.refresh(instance)
            self.logger.info(f"Created {model.__name__} with ID: {instance.id}")
            return instance
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error creating {model.__name__}: {e}")
            raise

    def get(self, model: Type[T], record_id: Any) -> Optional[T]:
        """Get a single record by ID"""
        try:
            self._validate_model(model)
            return self.db.query(model).filter(model.id == record_id).first()
        except Exception as e:
            self.logger.error(f"Error getting {model.__name__} with ID {record_id}: {e}")
            raise

    def get_all(self, model: Type[T], filters: Optional[Dict[str, Any]] = None) -> List[T]:
        """Get all records with optional filters"""
        try:
            self._validate_model(model)
            query = self.db.query(model)
            
            if filters:
                sanitized_filters = self._sanitize_input(filters)
                conditions = [getattr(model, k) == v for k, v in sanitized_filters.items()]
                query = query.filter(and_(*conditions))
                
            return query.all()
        except Exception as e:
            self.logger.error(f"Error getting all {model.__name__}: {e}")
            raise

    def update(self, model: Type[T], record_id: Any, update_data: Dict[str, Any]) -> Optional[T]:
        """Update a record"""
        try:
            self._validate_model(model)
            sanitized_data = self._sanitize_input(update_data)
            
            instance = self.db.query(model).filter(model.id == record_id).first()
            if not instance:
                return None
                
            for key, value in sanitized_data.items():
                setattr(instance, key, value)
                
            self.db.commit()
            self.db.refresh(instance)
            self.logger.info(f"Updated {model.__name__} with ID: {record_id}")
            return instance
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error updating {model.__name__} with ID {record_id}: {e}")
            raise

    def delete(self, model: Type[T], record_id: Any) -> bool:
        """Delete a record"""
        try:
            self._validate_model(model)
            instance = self.db.query(model).filter(model.id == record_id).first()
            if not instance:
                return False
                
            self.db.delete(instance)
            self.db.commit()
            self.logger.info(f"Deleted {model.__name__} with ID: {record_id}")
            return True
            
        except Exception as e:
            self.db.rollback()
            self.logger.error(f"Error deleting {model.__name__} with ID {record_id}: {e}")
            raise

    def get_by_field(self, model: Type[T], field: str, value: Any) -> Optional[T]:
        """Get a record by any field"""
        try:
            self._validate_model(model)
            sanitized_value = self._sanitize_input(value)
            return self.db.query(model).filter(getattr(model, field) == sanitized_value).first()
        except Exception as e:
            self.logger.error(f"Error getting {model.__name__} by {field}={value}: {e}")
            raise