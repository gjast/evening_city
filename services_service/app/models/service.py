from sqlalchemy import Column, Integer, String, Text, Numeric, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base
import enum


class ServiceType(enum.Enum):
    WORK = "work"
    ESTATE = "estate"
    NEWS = "news"
    AUTO = "auto"


class Service(Base):
    __tablename__ = "services"
    
    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False, index=True)
    
    service_type = Column(Enum(ServiceType), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Numeric(12, 2), nullable=True)
    image_url = Column(String(500), nullable=True)
    
    rating = Column(Numeric(2, 1), default=0)
    reviews_count = Column(Integer, default=0)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    city = relationship("City", back_populates="services")
    
    def __repr__(self):
        return f"<Service(id={self.id}, title={self.title}, type={self.service_type})>"

