from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# 1. 这里明确使用 SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./reader.db"

# 2. 【关键修复】 connect_args={"check_same_thread": False}
# 如果没有这一行，FastAPI 在不同线程读写时会报 ProgrammingError
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"check_same_thread": False} 
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Novel(Base):
    __tablename__ = "novels"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    content = Column(Text)