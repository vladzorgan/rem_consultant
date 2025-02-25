from fastapi import APIRouter

from app.api.api_v1.endpoints import devices, locations, repairs, prices, service_centers, auth, users

api_router = APIRouter()

# Регистрируем все маршруты API
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(devices.router, prefix="/devices", tags=["devices"])
api_router.include_router(locations.router, prefix="/locations", tags=["locations"])
api_router.include_router(repairs.router, prefix="/repairs", tags=["repairs"])
api_router.include_router(prices.router, prefix="/prices", tags=["prices"])
api_router.include_router(service_centers.router, prefix="/service-centers", tags=["service_centers"])