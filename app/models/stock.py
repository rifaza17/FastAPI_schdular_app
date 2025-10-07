
from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from app.models.base import Base
from sqlalchemy.dialects.postgresql import JSONB

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    price = Column(Float)
    change = Column(Float)
    change_percent = Column(String)
    volume = Column(String)
    sector = Column(String)
    sub_category = Column(String)
    rsi = Column(Float, nullable=True)
    macd = Column(Float, nullable=True)
    obv = Column(Float, nullable=True)
    ema12 = Column(Float, nullable=True)
    ema26 = Column(Float, nullable=True)
    earning = Column(JSONB, nullable=True)
    dividend = Column(JSONB, nullable=True)
    news = Column(JSONB, nullable=True)
    # history = Column(ARRAY(Float), nullable=True)  # list of prices
    # history_labels = Column(ARRAY(String), nullable=True)  # list of timestamps
    updated_at = Column(DateTime, default=datetime.utcnow)
    forecast = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    aiFactor = Column(String, nullable=True)

    # store multiple timeframe histories
    history_1d = Column(JSON, nullable=True)
    history_1w = Column(JSON, nullable=True)
    history_1m = Column(JSON, nullable=True)
    history_3m = Column(JSON, nullable=True)
    history_1y = Column(JSON, nullable=True)
    history_5y = Column(JSON, nullable=True)

    updated_at = Column(DateTime, default=datetime.utcnow)
    forecast = Column(String, nullable=True)
    sentiment = Column(String, nullable=True)
    aiFactor = Column(String, nullable=True)

    insider_trading = Column(JSONB, nullable=True)