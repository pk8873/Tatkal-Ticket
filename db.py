import os
from datetime import datetime
from sqlalchemy import create_engine, String, Integer, DateTime, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./tatkal_ticket.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

class Base(DeclarativeBase):
    pass

class Booking(Base):
    __tablename__ = "bookings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[str] = mapped_column(String(64), index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    source: Mapped[str] = mapped_column(String(120))
    destination: Mapped[str] = mapped_column(String(120))
    travel_date: Mapped[str] = mapped_column(String(20))
    quota: Mapped[str] = mapped_column(String(30))
    travel_class: Mapped[str] = mapped_column(String(20))
    train_no: Mapped[str | None] = mapped_column(String(20), nullable=True)
    boarding_station: Mapped[str | None] = mapped_column(String(120), nullable=True)
    passengers: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(40), default="READY_FOR_MANUAL_BOOKING")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(engine)
