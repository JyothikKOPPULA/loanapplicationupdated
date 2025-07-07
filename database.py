from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
import urllib.parse

# Load environment variables
load_dotenv()

# Connection parameters
DB_USER = os.getenv('DB_USER', 'loan')
DB_PASSWORD = urllib.parse.quote_plus(os.getenv('DB_PASSWORD', 'Jyothika@01'))
DB_SERVER = os.getenv('DB_SERVER', 'loandtbsrvr.database.windows.net')
DB_NAME = os.getenv('DB_NAME', 'loandatavase')

# Create connection string using the exact format from Azure Portal
SQLALCHEMY_DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "encrypt=yes&"
    "trustservercertificate=no&"
    "connection+timeout=30"
)

# Create SQLAlchemy engine with optimized settings for Azure SQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Maximum number of permanent connections
    max_overflow=10,     # Allow up to 10 additional temporary connections
    pool_timeout=30,     # Connection timeout of 30 seconds
    fast_executemany=True  # Optimize batch operations
)

# Create session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create connection string using the exact format from Azure Portal
SQLALCHEMY_DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}?"
    "driver=ODBC+Driver+18+for+SQL+Server&"
    "encrypt=yes&"
    "trustservercertificate=no&"
    "connection+timeout=30"
)

# Create SQLAlchemy engine with optimized settings for Azure SQL
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_pre_ping=True,  # Verify connections before using
    pool_recycle=3600,   # Recycle connections after 1 hour
    pool_size=5,         # Maximum number of permanent connections
    max_overflow=10,     # Allow up to 10 additional temporary connections
    pool_timeout=30,     # Connection timeout of 30 seconds
    fast_executemany=True  # Optimize batch operations
)

# Create session
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Create Base class
Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
