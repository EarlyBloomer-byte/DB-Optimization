# models.py
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    full_name = Column(String, index=False)  # Intentionally NOT indexed yet
    email = Column(String, unique=True)
    bio = Column(Text) # Large text field to simulate data load

# Create the SQLite database file
engine = create_engine('sqlite:///production.db')
Base.metadata.create_all(engine)