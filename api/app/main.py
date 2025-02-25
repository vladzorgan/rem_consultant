import time
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.api_v1.router import api_router
from app.core.config import settings
from app.db.session import get_async_db, engine
from app.models.logging import ApiLog

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API для сервиса поиска лучших цен на ремонт техники",
    version=settings.VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры API v1
app.include_router(api_router, prefix=settings.API_V1_STR)


# Промежуточное ПО для логирования
@app.middleware("http")
async def log_requests(request: Request, call_next):
    # Время начала обработки запроса
    start_time = time.time()

    # Получаем данные запроса
    method = request.method
    url = str(request.url)
    client_host = request.client.host if request.client else None

    try:
        # Обрабатываем запрос
        response = await call_next(request)

        # Вычисляем время обработки
        process_time = int((time.time() - start_time) * 1000)  # в миллисекундах

        # Логируем успешный запрос
        if not url.endswith(("/docs", "/redoc", "/openapi.json")):
            try:
                async for db in get_async_db():
                    api_log = ApiLog(
                        endpoint=url,
                        method=method,
                        ip_address=client_host,
                        response_time=process_time,
                        status_code=response.status_code
                    )
                    db.add(api_log)
                    await db.commit()
            except Exception as e:
                print(f"Ошибка при логировании запроса: {e}")

        return response
    except Exception as e:
        # Обрабатываем ошибку
        process_time = int((time.time() - start_time) * 1000)  # в миллисекундах

        # Логируем ошибочный запрос
        try:
            async for db in get_async_db():
                api_log = ApiLog(
                    endpoint=url,
                    method=method,
                    ip_address=client_host,
                    response_time=process_time,
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                db.add(api_log)
                await db.commit()
        except Exception as log_error:
            print(f"Ошибка при логировании запроса: {log_error}")

        # Возвращаем ошибку клиенту
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": str(e)}
        )


# Проверка здоровья API
@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "version": settings.VERSION,
        "debug": settings.DEBUG
    }