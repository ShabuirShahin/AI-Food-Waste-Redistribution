from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class NGO(Base):
    __tablename__ = "ngos"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    is_verified = Column(Boolean, default=False)
    reliability_score = Column(Float, default=0.5)
    response_count = Column(Integer, default=0)
    accept_count = Column(Integer, default=0)
    avg_response_time = Column(Float, default=0.0)

    foods = relationship("FoodPost", back_populates="ngo")


class FoodPost(Base):
    __tablename__ = "food_posts"

    id = Column(Integer, primary_key=True, index=True)
    quantity = Column(Integer, nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    expiry_hours = Column(Integer, nullable=False)
    status = Column(String, default="available")

    ngo_id = Column(Integer, ForeignKey("ngos.id"), nullable=True)
    ngo = relationship("NGO", back_populates="foods")


class Feedback(Base):
    __tablename__ = "feedback"

    id = Column(Integer, primary_key=True, index=True)
    food_id = Column(Integer)
    ngo_id = Column(Integer)
    success = Column(Boolean)
