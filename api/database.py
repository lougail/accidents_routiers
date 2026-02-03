import os
from datetime import datetime, timezone

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./predictions.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    input_data = Column(JSON)
    model_version = Column(String)
    probability = Column(Float)
    prediction = Column(Integer)
    grave = Column(String)


def init_db():
    Base.metadata.create_all(bind=engine)


def save_prediction(input_data: dict, model_version: str, probability: float, prediction: int, grave: bool):
    db = SessionLocal()
    try:
        db_prediction = Prediction(
            input_data=input_data,
            model_version=model_version,
            probability=probability,
            prediction=prediction,
            grave="oui" if grave else "non"
        )
        db.add(db_prediction)
        db.commit()
    finally:
        db.close()