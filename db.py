from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import cast, BigInteger, MetaData, create_engine, Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.sql import func
from config import DB_URI

Base = declarative_base()
engine = create_engine(DB_URI)
Session = sessionmaker(bind=engine)
meta_data = MetaData()
session = Session()