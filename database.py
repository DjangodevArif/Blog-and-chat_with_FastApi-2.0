from decouple import config
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DB_USERNAME = config('DB_USERNAME')
DB_PASSWORD = config('DB_PASSWORD')
# SQLALCHEMY_DATABASE_URL = "sqlite:///chat.db"
SQLALCHEMY_DATABASE_URL = f"postgresql://{DB_USERNAME}:{DB_PASSWORD}@localhost:5432/fastApiChatApp"
# SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin@localhost:5432/fastApiChatApp"

engine = create_engine(
    # SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
    SQLALCHEMY_DATABASE_URL
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
