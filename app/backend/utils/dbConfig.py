# dbConfig.py
import os
import time
from typing import Optional, Dict, Any, List
import psycopg2
from psycopg2 import pool, sql, OperationalError, InterfaceError
from psycopg2.extras import RealDictCursor
import logging
from contextlib import contextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PostgreSQLDatabase:
    """
    PostgreSQL database connection manager with robust error handling
    """
    
    _connection_pool = None
    _is_connected = False
    _connection_retries = 3
    _retry_delay = 2
    
    @classmethod
    def get_connection_string(cls) -> str:
        """Get connection string from environment"""
        return os.getenv("DATABASE_URL")
    
    @classmethod
    def initialize_pool(cls, min_connections: int = 1, max_connections: int = 10) -> bool:
        """Initialize connection pool with retry logic"""
        if cls._connection_pool is not None:
            return cls._is_connected
            
        connection_string = cls.get_connection_string()
        if not connection_string:
            logger.error("DATABASE_URL environment variable not set")
            return False
            
        for attempt in range(1, cls._connection_retries + 1):
            try:
                logger.info(f"Attempting to connect to database (attempt {attempt}/{cls._connection_retries})...")
                cls._connection_pool = pool.ThreadedConnectionPool(
                    minconn=min_connections,
                    maxconn=max_connections,
                    dsn=connection_string,
                    cursor_factory=RealDictCursor
                )
                
                # Test the connection
                conn = cls._connection_pool.getconn()
                conn.close()
                
                cls._is_connected = True
                logger.info("✅ Database connected successfully")
                return True
                
            except (OperationalError, InterfaceError) as e:
                logger.error(f"Connection attempt {attempt} failed: {e}")
                if attempt < cls._connection_retries:
                    time.sleep(cls._retry_delay * attempt)  # Exponential backoff
                else:
                    cls._is_connected = False
                    logger.error("❌ All connection attempts failed")
                    return False
            except Exception as e:
                logger.error(f"Unexpected error during connection: {e}")
                cls._is_connected = False
                return False

    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected"""
        return cls._is_connected
    
    @classmethod
    @contextmanager
    def get_connection(self):
        """Get connection with automatic retry if pool is closed"""
        conn = None
        try:
            if self._connection_pool is None or self._connection_pool.closed:
                self.initialize_pool()
                
            conn = self._connection_pool.getconn()
            conn.autocommit = False
            yield conn
            conn.commit()
        except (OperationalError, InterfaceError) as e:
            logger.error(f"Database operation failed: {e}")
            if conn:
                conn.rollback()
            # Attempt to reconnect
            self._connection_pool = None
            self.initialize_pool()
            raise
        except Exception as e:
            logger.error(f"Unexpected database error: {e}")
            if conn:
                conn.rollback()
            raise
        finally:
            if conn and not conn.closed:
                try:
                    self._connection_pool.putconn(conn)
                except Exception as e:
                    logger.warning(f"Error returning connection: {e}")

# Initialize database connection when module loads
databaseObject = PostgreSQLDatabase()
if not databaseObject.initialize_pool():
    logger.warning("Proceeding without database connection")