import os
from datetime import datetime, timezone

from sqlalchemy import JSON, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./predictions.db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc)
    )
    input_data: Mapped[dict] = mapped_column(JSON)
    model_version: Mapped[str]
    probability: Mapped[float]
    prediction: Mapped[int]
    grave: Mapped[str]


def init_db():
    Base.metadata.create_all(bind=engine)


def save_prediction(
    input_data: dict,
    model_version: str,
    probability: float,
    prediction: int,
    grave: bool,
):
    db = SessionLocal()
    try:
        db_prediction = Prediction(
            input_data=input_data,
            model_version=model_version,
            probability=probability,
            prediction=prediction,
            grave="oui" if grave else "non",
        )
        db.add(db_prediction)
        db.commit()
    finally:
        db.close()
