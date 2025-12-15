from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.db.database import get_db
from app.models.city import City
from app.models.service import Service
from app.schemas.city import CityCreate, CityResponse, CityWithCount

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get("/", response_model=List[CityWithCount])
async def get_all_cities(db: Session = Depends(get_db)):
    """
    Получение списка всех городов с количеством услуг
    """
    cities = db.query(
        City,
        func.count(Service.id).label("services_count")
    ).outerjoin(Service).group_by(City.id).all()
    
    result = []
    for city, count in cities:
        city_dict = {
            "id": city.id,
            "name": city.name,
            "slug": city.slug,
            "services_count": count
        }
        result.append(city_dict)
    
    return result


@router.get("/{city_slug}", response_model=CityResponse)
async def get_city_by_slug(city_slug: str, db: Session = Depends(get_db)):
    """
    Получение города по slug
    """
    city = db.query(City).filter(City.slug == city_slug).first()
    
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Город не найден"
        )
    
    return city


@router.post("/", response_model=CityResponse, status_code=status.HTTP_201_CREATED)
async def create_city(city_data: CityCreate, db: Session = Depends(get_db)):
    """
    Создание нового города
    """
    existing = db.query(City).filter(
        (City.name == city_data.name) | (City.slug == city_data.slug)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Город с таким именем или slug уже существует"
        )
    
    city = City(**city_data.model_dump())
    db.add(city)
    db.commit()
    db.refresh(city)
    
    return city

