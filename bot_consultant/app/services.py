import logging
from typing import Dict, Any, Optional, List

import httpx
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

from config import API_URL

async def _fetch_from_api(
    method: str,
    endpoint: str,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None
) -> Any:
    """Универсальная функция для запросов к API."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        try:
            response = await client.request(method, f"{API_URL}{endpoint}", params=params, json=json)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404 and method == "GET":
                return None if endpoint.startswith("/api/user/") or endpoint.startswith("/api/service_centers/") else []
            logger.error(f"API request failed: {method} {endpoint} - {e.response.status_code} - {e.response.text}")
            return None if method == "GET" else False
        except httpx.RequestError as e:
            logger.error(f"Network error during API request: {method} {endpoint} - {e}")
            return None if method == "GET" else False

async def get_regions() -> List[Dict[str, Any]]:
    return await _fetch_from_api("GET", "/api/regions") or []

async def fetch_cities(params) -> List[Dict[str, Any]]:
    return await _fetch_from_api("GET", "/api/cities", params=params) or []

async def get_user(telegram_id: int) -> Optional[Dict[str, Any]]:
    return await _fetch_from_api("GET", f"/api/user/{telegram_id}")

async def fetch_brands() -> List[Dict[str, Any]]:
    return await _fetch_from_api("GET", "/api/device_brands") or []

async def get_service_centers(skip: int, limit: int, city_id: int) -> List[Dict[str, Any]]:
    params = {"skip": skip, "limit": limit, "city_id": city_id}
    return await _fetch_from_api("GET", "/api/service_centers", params=params) or []

async def get_owned_service_centers(params) -> List[Dict[str, Any]]:
    return await _fetch_from_api("GET", "/api/owned", params=params) or []

async def fetch_reviews(skip: int, limit: int, service_center_id: int) -> List[Dict[str, Any]]:
    params = {"service_center_id": service_center_id, "skip": skip, "limit": limit}
    return await _fetch_from_api("GET", "/api/reviews", params=params) or []

async def search_service_centers(params) -> List[Dict[str, Any]]:
    return await _fetch_from_api("GET", "/api/service_centers/search", params=params) or []

async def fetch_service_center(service_center_id: int) -> Optional[Dict[str, Any]]:
    return await _fetch_from_api("GET", f"/api/service_centers/{service_center_id}")

async def update_user_city(telegram_id: int, city_id: int) -> bool:
    return await _fetch_from_api("PUT", "/api/user/city", json={"telegram_id": telegram_id, "city_id": city_id})

async def create_user(data: Dict[str, Any]) -> bool:
    return await _fetch_from_api("POST", "/api/user", json=data)

async def create_service_claim_request(data: Dict[str, Any]) -> bool:
    return await _fetch_from_api("POST", f"/api/service_centers/{data['service_center_id']}/claim", json=data)

async def notify_user(telegram_id: int, message: str, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Отправка уведомления пользователю через Telegram."""
    try:
        await context.bot.send_message(chat_id=telegram_id, text=message, parse_mode="HTML")
        return True
    except Exception as e:
        logger.error(f"Failed to notify user {telegram_id}: {e}")
        return False

async def approve_service_claim(claim_id: int) -> Optional[dict]:
    """Подтверждение заявки через API."""
    return await _fetch_from_api("PUT", f"/api/claims/{claim_id}/approve")

async def reject_service_claim(claim_id: int) -> Optional[dict]:
    """Отмена заявки через API."""
    return await _fetch_from_api("PUT", f"/api/claims/{claim_id}/reject")