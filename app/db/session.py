from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session, declarative_base
from app.core.config import settings

DATABASE_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"

engine = create_engine(DATABASE_URL,pool_pre_ping=True,)

sessionlocal = sessionmaker(bind=engine,class_=Session, autoflush=False, autocommit = False, expire_on_commit=False,)

# Base = declarative_base()

def get_db():
    
    db = sessionlocal()
    
    try:
        yield db

    finally:
        db.close()