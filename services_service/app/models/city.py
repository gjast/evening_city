from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.db.database import Base


class City(Base):
    __tablename__ = "cities"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False, index=True)
    slug = Column(String(100), unique=True, nullable=False, index=True)
    
    services = relationship("Service", back_populates="city", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<City(id={self.id}, name={self.name})>"

