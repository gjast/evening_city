from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.city import City
from app.models.service import Service, ServiceType as ServiceTypeModel
from app.schemas.service import ServiceCreate, ServiceResponse, ServiceWithCity, ServiceType, ServiceUpdate

router = APIRouter(prefix="/services", tags=["Services"])


@router.get("/", response_model=List[ServiceWithCity])
async def get_services(
    city_slug: Optional[str] = Query(None, description="Фильтр по городу (slug)"),
    service_type: Optional[ServiceType] = Query(None, description="Тип услуги"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получение списка услуг с фильтрацией
    """
    query = db.query(Service).join(City)
    
    if city_slug:
        query = query.filter(City.slug == city_slug)
    
    if service_type:
        query = query.filter(Service.service_type == ServiceTypeModel[service_type.value.upper()])
    
    services = query.offset(skip).limit(limit).all()
    
    result = []
    for service in services:
        service_dict = {
            "id": service.id,
            "city_id": service.city_id,
            "service_type": service.service_type.value,
            "title": service.title,
            "description": service.description,
            "price": service.price,
            "image_url": service.image_url,
            "rating": service.rating,
            "reviews_count": service.reviews_count,
            "created_at": service.created_at,
            "updated_at": service.updated_at,
            "city_name": service.city.name,
            "city_slug": service.city.slug
        }
        result.append(service_dict)
    
    return result


@router.get("/by-type/{service_type}", response_model=List[ServiceWithCity])
async def get_services_by_type(
    service_type: ServiceType,
    city_slug: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    Получение услуг по типу (work, estate, news, auto)
    """
    query = db.query(Service).join(City).filter(
        Service.service_type == ServiceTypeModel[service_type.value.upper()]
    )
    
    if city_slug:
        query = query.filter(City.slug == city_slug)
    
    services = query.offset(skip).limit(limit).all()
    
    result = []
    for service in services:
        service_dict = {
            "id": service.id,
            "city_id": service.city_id,
            "service_type": service.service_type.value,
            "title": service.title,
            "description": service.description,
            "price": service.price,
            "image_url": service.image_url,
            "rating": service.rating,
            "reviews_count": service.reviews_count,
            "created_at": service.created_at,
            "updated_at": service.updated_at,
            "city_name": service.city.name,
            "city_slug": service.city.slug
        }
        result.append(service_dict)
    
    return result


@router.get("/{service_id}", response_model=ServiceWithCity)
async def get_service(service_id: int, db: Session = Depends(get_db)):
    """
    Получение услуги по ID
    """
    service = db.query(Service).filter(Service.id == service_id).first()
    
    if not service:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Услуга не найдена"
        )
    
    return {
        "id": service.id,
        "city_id": service.city_id,
        "service_type": service.service_type.value,
        "title": service.title,
        "description": service.description,
        "price": service.price,
        "image_url": service.image_url,
        "rating": service.rating,
        "reviews_count": service.reviews_count,
        "created_at": service.created_at,
        "updated_at": service.updated_at,
        "city_name": service.city.name,
        "city_slug": service.city.slug
    }


@router.post("/", response_model=ServiceResponse, status_code=status.HTTP_201_CREATED)
async def create_service(service_data: ServiceCreate, db: Session = Depends(get_db)):
    """
    Создание новой услуги
    """
    city = db.query(City).filter(City.id == service_data.city_id).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Город не найден"
        )
    
    service = Service(
        city_id=service_data.city_id,
        service_type=ServiceTypeModel[service_data.service_type.value.upper()],
        title=service_data.title,
        description=service_data.description,
        price=service_data.price,
        image_url=service_data.image_url
    )
    db.add(service)
    db.commit()
    db.refresh(service)
    
    return service


@router.get("/count/by-city/{city_slug}")
async def get_services_count_by_city(city_slug: str, db: Session = Depends(get_db)):
    """
    Получение количества услуг по городу
    """
    city = db.query(City).filter(City.slug == city_slug).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Город не найден"
        )
    
    counts = {}
    for st in ServiceTypeModel:
        count = db.query(Service).filter(
            Service.city_id == city.id,
            Service.service_type == st
        ).count()
        counts[st.value] = count
    
    return {
        "city": city.name,
        "city_slug": city.slug,
        "counts": counts,
        "total": sum(counts.values())
    }

