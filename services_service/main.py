from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import engine, Base
from app.routers import cities_router, services_router
from app.models.city import City
from app.models.service import Service, ServiceType

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    description="Микросервис услуг для городов",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(cities_router, prefix="/api/v1")
app.include_router(services_router, prefix="/api/v1")


@app.get("/", tags=["Health"])
async def root():
    """Проверка работоспособности сервиса"""
    return {
        "service": settings.APP_NAME,
        "status": "healthy",
        "version": "1.0.0"
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint для мониторинга"""
    return {"status": "ok"}


@app.on_event("startup")
async def seed_data():
    """Заполнение тестовыми данными при первом запуске"""
    from app.db.database import SessionLocal
    
    db = SessionLocal()
    
    try:
        # Проверяем, есть ли уже данные
        if db.query(City).count() > 0:
            return
        
        # 15 городов
        cities_data = [
            {"name": "Москва", "slug": "moscow"},
            {"name": "Санкт-Петербург", "slug": "spb"},
            {"name": "Екатеринбург", "slug": "ekaterinburg"},
            {"name": "Казань", "slug": "kazan"},
            {"name": "Новосибирск", "slug": "novosibirsk"},
            {"name": "Челябинск", "slug": "chelyabinsk"},
            {"name": "Краснодар", "slug": "krasnodar"},
            {"name": "Нижний Новгород", "slug": "nizhni_novgorod"},
            {"name": "Самара", "slug": "samara"},
            {"name": "Уфа", "slug": "ufa"},
            {"name": "Ростов-на-Дону", "slug": "rostov"},
            {"name": "Омск", "slug": "omsk"},
            {"name": "Красноярск", "slug": "krasnoyarsk"},
            {"name": "Воронеж", "slug": "voronezh"},
            {"name": "Пермь", "slug": "perm"},
        ]
        
        cities = []
        for city_data in cities_data:
            city = City(**city_data)
            db.add(city)
            cities.append(city)
        
        db.commit()
        
        # Тестовые услуги для каждого города
        services_templates = {
            ServiceType.WORK: [
                {"title": "Маникюр", "description": "Профессиональный маникюр и педикюр", "price": 1500},
                {"title": "Репетитор по математике", "description": "Подготовка к ЕГЭ и ОГЭ", "price": 2000},
                {"title": "Сантехник", "description": "Установка и ремонт сантехники", "price": 3000},
                {"title": "Электрик", "description": "Электромонтажные работы любой сложности", "price": 2500},
                {"title": "Уборка квартир", "description": "Генеральная и поддерживающая уборка", "price": 4000},
            ],
            ServiceType.ESTATE: [
                {"title": "2-к квартира, 65 м²", "description": "Евроремонт, мебель, техника", "price": 8500000},
                {"title": "1-к квартира, 42 м²", "description": "Новостройка, чистовая отделка", "price": 5200000},
                {"title": "Студия, 28 м²", "description": "Современный ремонт, центр города", "price": 3800000},
                {"title": "3-к квартира, 95 м²", "description": "Просторная планировка, парковка", "price": 12000000},
                {"title": "Таунхаус, 150 м²", "description": "Загородная жизнь рядом с городом", "price": 15000000},
            ],
            ServiceType.NEWS: [
                {"title": "Открытие нового ТЦ", "description": "В центре города открылся крупный торговый центр", "price": None},
                {"title": "Ремонт дорог завершен", "description": "Капитальный ремонт главной улицы закончен", "price": None},
                {"title": "Новая линия метро", "description": "Планируется строительство новой ветки метрополитена", "price": None},
                {"title": "Фестиваль еды", "description": "В эти выходные пройдет гастрономический фестиваль", "price": None},
                {"title": "День города", "description": "Программа мероприятий на День города", "price": None},
            ],
            ServiceType.AUTO: [
                {"title": "Toyota Camry 2020", "description": "Пробег 45000 км, один владелец", "price": 2500000},
                {"title": "BMW X5 2019", "description": "Полный привод, панорамная крыша", "price": 4500000},
                {"title": "Lada Vesta 2022", "description": "Новая, на гарантии", "price": 1200000},
                {"title": "Mercedes E-class 2021", "description": "AMG пакет, все опции", "price": 5800000},
                {"title": "Kia Rio 2023", "description": "Автомат, климат-контроль", "price": 1600000},
            ],
        }
        
        for city in cities:
            db.refresh(city)
            for service_type, templates in services_templates.items():
                for template in templates:
                    service = Service(
                        city_id=city.id,
                        service_type=service_type,
                        title=template["title"],
                        description=template["description"],
                        price=template["price"],
                        image_url="img/news01.webp",
                        rating=round(3 + (hash(template["title"]) % 20) / 10, 1),
                        reviews_count=abs(hash(template["title"])) % 500
                    )
                    db.add(service)
        
        db.commit()
        print("Тестовые данные успешно добавлены!")
        
    except Exception as e:
        print(f"Ошибка при добавлении тестовых данных: {e}")
        db.rollback()
    finally:
        db.close()

